from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from apps.games.tic_tac_toe.models import Match
from channels.db import database_sync_to_async
from apps.games.tic_tac_toe.services import GAME_LOBBY_GROUP, broadcast_matches_updated, get_turn_deadline, \
    join_match, perform_make_move, read_match_state, abort_match, perform_forfeit
from apps.games.tic_tac_toe.game import InvalidMove
from redis.exceptions import LockError

User = get_user_model()


def match_group(match_id):
    return f"match_{match_id}"


class GameConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self) -> None:
        await self.accept()

        match_id = self.scope["url_route"]["kwargs"]["match_id"]  # type: ignore
        self.match_id = match_id
        match = await self.get_match(match_id)
        if match is None:
            await self.close(code=4404)
            return

        self.match_group = match_group(match_id)

        await self.channel_layer.group_add(self.match_group, self.channel_name)

        try:
            game = await read_match_state(self.match_id)
        except ValueError:
            await abort_match(match_id)
            await broadcast_matches_updated()
            await self.close(code=4500)
            return

        await self.send_json({
            "type": "game_state",
            "board_state": game.to_dict(),
            "turn_deadline": await get_turn_deadline(match_id),
        })

    async def disconnect(self, code: int) -> None:
        if hasattr(self, "match_group"):
            await self.channel_layer.group_discard(self.match_group, self.channel_name)

    async def receive_json(self, content, **kwargs) -> None:
        if not isinstance(content, dict):
            await self.send_json({
                "type": "error",
                "detail": "Invalid JSON format.",
            })
            return

        action = content.get("action")
        if action == "join":
            await self.handle_join_match()
        elif action == "make_move":
            target_board = content.get("next_board")
            target_cell = content.get("next_cell")
            if type(target_board) is not int or type(target_cell) is not int:
                return
            await self.handle_make_move(target_board, target_cell)
        elif action == "forfeit":
            await self.handle_forfeit()
        else:
            await self.send_json({
                "type": "error",
                "detail": "Unknown action.",
            })

    async def handle_join_match(self):
        user: User | None = self.scope.get("user")
        if user is None or not user.is_authenticated:
            return
        if not await join_match(self.match_id, user):
            await self.send_json({
                "type": "error",
                "detail": "Cannot join this match.",
            })
            return
        await self.channel_layer.group_send(
            self.match_group,
            {
                "type": "user.joined",
                "user_id": user.pk,
            }
        )
        await broadcast_matches_updated()

    async def user_joined(self, event):
        await self.send_json({
            "type": "player_joined",
            "user_id": event.get("user_id"),
        })

    async def handle_make_move(self, target_board, target_cell):
        user: User | None = self.scope.get("user")
        if user is None or not user.is_authenticated:
            return
        try:
            await perform_make_move(self.match_id, user, target_board, target_cell)
        except InvalidMove as err:
            await self.send_json({
                "type": "error",
                "detail": f"Invalid Move {err}",
            })
            return
        except LockError:
            await self.send_json({
                "type": "error",
                "detail": "Could not process move. Try again.",
            })
            return
        except ValueError as err:
            await abort_match(self.match_id)
            await broadcast_matches_updated()
            await self.send_json({
                "type": "error",
                "detail": str(err)
            })
            return

    async def handle_forfeit(self):
        user = self.scope.get("user")
        if user is None or not user.is_authenticated:
            return
        try:
            await perform_forfeit(self.match_id, user)
        except LockError:
            await self.send_json({
                "type": "error",
                "detail": "Could not forfeit match. Try again.",
            })
            return

    async def user_forfeit(self, event):
        await self.send_json({
            "type": "user_forfeit",
            "user_id": event["user_id"],
        })
        await self.close(code=1000)

    async def move_result(self, event):
        await self.send_json({
            "type": "move_result",
            "detail": event["result"],
            "board_state": event["board_state"],
            "turn_deadline": event["turn_deadline"],
        })

        if event["result"] in ("winner_X", "winner_O", "draw"):
            await self.close(code=1000)

    @database_sync_to_async
    def get_match(self, match_id: int) -> Match | None:
        return Match.objects.filter(
            pk=match_id,
            status__in=[
                Match.GameStatus.IN_PROGRESS,
                Match.GameStatus.WAITING,
            ],
        ).first()


class LobbyConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self) -> None:
        await self.channel_layer.group_add(GAME_LOBBY_GROUP, self.channel_name)

        await self.accept()

    async def matches_updated(self, event):
        await self.send_json({
            "type": "matches_updated",
        })

    async def disconnect(self, code: int) -> None:
        await self.channel_layer.group_discard(GAME_LOBBY_GROUP, self.channel_name)
