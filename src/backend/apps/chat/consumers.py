from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        user = self.scope["user"]  # type: ignore
        if not user.is_authenticated:  # type: ignore
            await self.close(code=4401)
            return

        await self.accept()
