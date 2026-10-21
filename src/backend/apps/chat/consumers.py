from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from apps.chat.serializers import MessageCreateSerializer


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self) -> None:
        user = self.scope.get("user")

        if user is None or not user.is_authenticated:
            await self.close(code=4401)
            return

        self.user_group = f"user_{user.pk}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)

        await self.accept()

    async def disconnect(self, code: int) -> None:
        if hasattr(self, "user_group"):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)

    async def receive_json(self, content, **kwargs) -> None:
        if content["action"] == "send_message":
            await self.handle_send_message(content["message"])

    async def handle_send_message(self, message):
        message_dict = await self.create_message(message)
        member_ids = message_dict.pop("member_ids", [])
        for member_id in member_ids:
            member_group = f"user_{member_id}"
            await self.channel_layer.group_send(
                member_group,
                {
                    "type": "message.created",
                    "message": message_dict,
                },
            )

    async def message_created(self, event):
        message = event.get("message", {})
        await self.send_json(message, close=False)

    @database_sync_to_async
    def create_message(self, message):
        serializer = MessageCreateSerializer(
            data=message,
            context={"user": self.scope.get("user")},
        )
        serializer.is_valid(raise_exception=True)
        saved_message = serializer.save()
        member_ids = list(
            saved_message.chat_room.members.values_list("id", flat=True)
        )

        return {
            "id": str(saved_message.id),
            "sender": saved_message.sender_id,
            "content": saved_message.content,
            "chat_room": str(saved_message.chat_room_id),
            "created_at": saved_message.created_at.isoformat(),
            "member_ids": member_ids,
        }
