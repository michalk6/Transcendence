from apps.games.tic_tac_toe.game import Game
from redis import asyncio, Redis
from django.conf import settings
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from apps.games.tic_tac_toe.models import Match
from django.contrib.auth import get_user_model
import json

User = get_user_model()


GAME_LOBBY_GROUP = "tic_tac_toe_lobby"

redis_client = Redis.from_url(settings.REDIS_URL)
async_redis_client = asyncio.from_url(settings.REDIS_URL)
channel_layer = get_channel_layer()


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
        result = game.make_move(sign, target_board, target_cell)

        if result in ("winner_X", "winner_O", "draw"):
            await set_game_result(result, match_id)
            await delete_match_state(match_id)
        else:
            await save_match_state(match_id, game)

        if channel_layer is not None:
            await channel_layer.group_send(
                f"match_{match_id}",
                {
                    "type": "move.result",
                    "result": result,
                    "board_state": game.to_dict(),
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
