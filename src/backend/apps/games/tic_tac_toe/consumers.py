from channels.generic.websocket import AsyncJsonWebsocketConsumer


class GameConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self) -> None:
        user = self.scope.get("user")

        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return

        match_id = self.scope["url_route"]["kwargs"]["match_id"]  # type: ignore

        await self.accept()