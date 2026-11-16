from apps.games.tic_tac_toe.game import Game, InvalidMove
from redis import Redis, asyncio as asyncio_redis
from django.conf import settings
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from apps.games.tic_tac_toe.models import Match
from django.contrib.auth import get_user_model
from django.db.models import Q
import json
import random
import time
import asyncio as asyncio_lib

User = get_user_model()


GAME_LOBBY_GROUP = "tic_tac_toe_lobby"
TURN_TIME_LIMIT = 60
MAX_OPEN_MATCHES = 1

redis_client = Redis.from_url(settings.REDIS_URL)
async_redis_client = asyncio_redis.from_url(settings.REDIS_URL)
channel_layer = get_channel_layer()


def turn_deadline_key(match_id: int) -> str:
    return f"tic_tac:toe:match:{match_id}:turn_deadline"


async def set_turn_deadline(match_id: int) -> float:
    deadline = time.time() + TURN_TIME_LIMIT
    await async_redis_client.set(
        turn_deadline_key(match_id),
        deadline,
    )
    return deadline


async def get_turn_deadline(match_id: int) -> float | None:
    deadline = await async_redis_client.get(
        turn_deadline_key(match_id)
    )
    if deadline is None:
        return None
    return float(deadline)


async def delete_turn_deadline(match_id: int) -> None:
    await async_redis_client.delete(
        turn_deadline_key(match_id)
    )


async def start_deadline_countdown(match_id: int, deadline):
    await asyncio_lib.sleep(deadline - time.time())

    lock = async_redis_client.lock(
        match_lock_key(match_id),
        timeout=10,
        blocking_timeout=5,
    )

    async with lock:
        current_deadline = await get_turn_deadline(match_id)
        if current_deadline == deadline:
            game = await read_match_state(match_id)
            sign = game.current_player
            user = await get_current_player(sign, match_id)
            if not await set_forfeit_result(match_id, user):
                return
            await delete_match_state(match_id)
            await delete_turn_deadline(match_id)
            if channel_layer is not None:
                await channel_layer.group_send(
                    f"match_{match_id}",
                    {
                        "type": "user.forfeit",
                        "user_id": user.pk,
                    },
                )
            await broadcast_matches_updated()


def match_key(match_id):
    return f"tic_tac:toe:match:{match_id}"


def match_lock_key(match_id: int) -> str:
    return f"tic_tac:toe:match:{match_id}:lock"


def create_match(match_id: int) -> None:
    game = Game()
    redis_client.set(match_key(match_id), json.dumps(game.to_dict()))


async def save_match_state(match_id: int, game: Game) -> None:
    await async_redis_client.set(match_key(match_id), json.dumps(game.to_dict()))


async def delete_match_state(match_id: int) -> None:
    await async_redis_client.delete(match_key(match_id))


async def read_match_state(match_id) -> Game:
    game_json = await async_redis_client.get(match_key(match_id))
    if game_json is None:
        raise ValueError("Cannot find match with given id")
    game_data = json.loads(game_json)
    return Game.from_dict(game_data)


async def broadcast_matches_updated():
    if channel_layer is None:
        return
    await channel_layer.group_send(
        GAME_LOBBY_GROUP,
        {"type": "matches.updated"},
    )


async def perform_make_move(
    match_id: int, user: User, target_board: int, target_cell: int
) -> None:
    lock = async_redis_client.lock(
        match_lock_key(match_id),
        timeout=10,
        blocking_timeout=5,
    )

    async with lock:
        sign = await get_sign(user, match_id)
        if sign is None:
            return

        game = await read_match_state(match_id)
        deadline = await get_turn_deadline(match_id)

        if (
            game.current_player == sign
            and deadline is not None and time.time() > deadline
        ):
            if not await set_forfeit_result(match_id, user):
                return
            await delete_match_state(match_id)
            await delete_turn_deadline(match_id)

            if channel_layer is not None:
                await channel_layer.group_send(
                    f"match_{match_id}",
                    {
                        "type": "user.forfeit",
                        "user_id": user.pk,
                    },
                )
                await broadcast_matches_updated()

            return

        result = game.make_move(sign, target_board, target_cell)

        if result in ("winner_X", "winner_O", "draw"):
            await set_game_result(result, match_id)
            await delete_match_state(match_id)
            await delete_turn_deadline(match_id)
            new_deadline = None
        else:
            await save_match_state(match_id, game)
            new_deadline = await set_turn_deadline(match_id)
            asyncio_lib.create_task(
                start_deadline_countdown(match_id, new_deadline)
            )

        if channel_layer is not None:
            await channel_layer.group_send(
                f"match_{match_id}",
                {
                    "type": "move.result",
                    "result": result,
                    "board_state": game.to_dict(),
                    "turn_deadline": new_deadline,
                }
            )

            if result in ("winner_X", "winner_O", "draw"):
                await broadcast_matches_updated()


async def perform_forfeit(match_id: int, user: User) -> None:
    lock = async_redis_client.lock(
        match_lock_key(match_id),
        timeout=10,
        blocking_timeout=5,
    )

    async with lock:
        if await set_forfeit_result(match_id, user):
            await delete_match_state(match_id)
            await delete_turn_deadline(match_id)
            if channel_layer is None:
                return
            await channel_layer.group_send(
                f"match_{match_id}",
                {
                    "type": "user.forfeit",
                    "user_id": user.pk,
                },
            )
            await broadcast_matches_updated()


@database_sync_to_async
def set_forfeit_result(match_id: int, user: User) -> bool:
    match = Match.objects.get(pk=match_id)

    if match.status != Match.GameStatus.IN_PROGRESS:
        return False

    if user.pk == match.player_o_id:  # type: ignore
        match.winner = match.player_x
    elif user.pk == match.player_x_id:  # type: ignore
        match.winner = match.player_o
    else:
        return False

    match.status = Match.GameStatus.FINISHED
    match.save()
    return True


@database_sync_to_async
def get_sign(user, match_id) -> str | None:
    match: Match = Match.objects.get(pk=match_id)

    if match.status != Match.GameStatus.IN_PROGRESS:
        return None

    if user.pk == match.player_x_id:  # type: ignore
        return "X"
    if user.pk == match.player_o_id:  # type: ignore
        return "O"
    return None


@database_sync_to_async
def set_game_result(game_result, match_id) -> None:
    match = Match.objects.get(pk=match_id)

    if game_result == "winner_X":
        match.winner = match.player_x
    if game_result == "winner_O":
        match.winner = match.player_o

    match.status = Match.GameStatus.FINISHED
    match.save()


def user_to_dict(user: User | None) -> dict | None:
    if user is None:
        return None
    return {"id": user.pk, "username": user.username}


# match must be loaded with select_related("player_x", "player_o"), so no query is made here
def players_to_dict(match: Match) -> dict:
    return {
        "X": user_to_dict(match.player_x),
        "O": user_to_dict(match.player_o),
    }


@database_sync_to_async
def get_players(match_id: int) -> dict:
    match = Match.objects.select_related("player_x", "player_o").get(pk=match_id)
    return players_to_dict(match)


def has_open_match(user: User) -> bool:
    open_matches = Match.objects.filter(
        Q(player_x=user) | Q(player_o=user),
        status__in=[Match.GameStatus.WAITING, Match.GameStatus.IN_PROGRESS],
    )
    return open_matches.count() >= MAX_OPEN_MATCHES


@database_sync_to_async
def check_open_match(user: User) -> bool:
    return has_open_match(user)


# unlike get_sign it works for a waiting match too, so the creator can be recognized
@database_sync_to_async
def find_player_sign(user: User, match_id: int) -> str | None:
    match = Match.objects.get(pk=match_id)
    if user.pk == match.player_x_id:  # type: ignore
        return "X"
    if user.pk == match.player_o_id:  # type: ignore
        return "O"
    return None


async def perform_join(match_id: int, user: User) -> tuple[Game, float] | None:
    lock = async_redis_client.lock(
        match_lock_key(match_id),
        timeout=10,
        blocking_timeout=5,
    )

    async with lock:
        if not await join_match(match_id, user):
            return None

        # coin flip, X is always the creator but any of the players can start
        game = await read_match_state(match_id)
        game.current_player = random.choice(["X", "O"])
        await save_match_state(match_id, game)

        deadline = await set_turn_deadline(match_id)
        asyncio_lib.create_task(start_deadline_countdown(match_id, deadline))
        return game, deadline


@database_sync_to_async
def join_match(match_id: int, user: User) -> bool:
    return bool(Match.objects.filter(
        pk=match_id,
        player_o__isnull=True,
        status=Match.GameStatus.WAITING,
    ).exclude(
        player_x=user,
    ).update(
        player_o=user,
        status=Match.GameStatus.IN_PROGRESS,
    ))


@database_sync_to_async
def abort_match(match_id: int) -> None:
    Match.objects.filter(
        pk=match_id,
        status__in=[
            Match.GameStatus.IN_PROGRESS,
            Match.GameStatus.WAITING,
        ]
    ).update(status=Match.GameStatus.ABORTED)


@database_sync_to_async
def get_current_player(sign: str, match_id: int) -> User:
    match = Match.objects.get(id=match_id)
    if sign == "X":
        return match.player_x
    else:
        return match.player_o
