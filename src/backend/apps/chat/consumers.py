from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from apps.chat.serializers import MessageCreateSerializer
from rest_framework.exceptions import ValidationError
from apps.chat.presence import (
    add_connection, remove_connection, is_online, get_online_user_ids, refresh_presence, PRESENCE_TTL
)
from django.contrib.auth import get_user_model
from apps.users.queries import annotate_and_sort_by_friendship_status
from apps.users.serializers.user_serializers import PublicUserSerializer
import asyncio
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from apps.users.models import User
else:
    User = get_user_model()


ONLINE_USERS_GROUP = "online_users"


def user_group(user_pk):
    return f"user_{user_pk}"


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self) -> None:
        user = self.scope.get("user")

        if user is None or not user.is_authenticated:
            await self.close(code=4401)
            return

        self.user_group = user_group(user.pk)
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.channel_layer.group_add(ONLINE_USERS_GROUP, self.channel_name)

        await add_connection(user.pk, self.channel_name)
        await self.accept()
        await self.handle_go_online()
        self.heartbeat_task = asyncio.create_task(self.presence_heartbeat(user.pk))

    async def handle_go_online(self):
        await self.broadcast_status("online")

    async def disconnect(self, code: int) -> None:
        if hasattr(self, "heartbeat_task"):
            self.heartbeat_task.cancel()
        user = self.scope.get("user")
        if user is None or not user.is_authenticated:
            return

        await remove_connection(user.pk, self.channel_name)

        if hasattr(self, "user_group"):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
        await self.channel_layer.group_discard(ONLINE_USERS_GROUP, self.channel_name)

        await self.handle_go_offline()

    async def handle_go_offline(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            return
        if await is_online(user.pk):
            return
        await self.broadcast_status("offline")

    async def broadcast_status(self, status):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            return
        await self.channel_layer.group_send(
            ONLINE_USERS_GROUP,
            {
                "type": "send.status",
                "user_id": user.pk,
                "status": status,
            }
        )

    async def send_status(self, event):
        await self.send_json({
            "user_id": event.get("user_id"),
            "status": event.get("status"),
        })

    async def receive_json(self, content, **kwargs) -> None:
        if not isinstance(content, dict):
            await self.send_json({"action": "error", "detail": "Invalid JSON format."})
            return

        action = content.get("action")
        if action == "get_online_users":
            await self.handle_get_online_users()
        elif action == "send_message":
            message = content.get("message")
            if not isinstance(message, dict):
                await self.send_json({
                    "action": "error",
                    "detail": "Message must be a JSON object.",
                })
                return
            await self.handle_send_message(message)
        else:
            await self.send_json({"action": "error", "detail": "Unknown action."})

    async def handle_get_online_users(self):
        online_user_ids = await get_online_user_ids()
        online_users = await self.retrieve_users_from_db(online_user_ids)
        await self.send_json({
            "online_users": online_users,
        })

    async def handle_send_message(self, message):
        try:
            message_dict = await self.create_message(message)
            member_ids = message_dict.pop("member_ids", [])
        except ValidationError as err:
            await self.send_json({
                "action": "error",
                "detail": str(err.detail),
            })
            return

        for member_id in member_ids:
            member_group = user_group(member_id)
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

    async def presence_heartbeat(self, user_id):
        while True:
            await asyncio.sleep(PRESENCE_TTL // 3)
            await refresh_presence(user_id)

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

    @database_sync_to_async
    def retrieve_users_from_db(self, user_ids):
        user = cast(User, self.scope.get("user"))
        queryset = User.objects.filter(id__in=user_ids)
        queryset = annotate_and_sort_by_friendship_status(queryset, user)
        serializer = PublicUserSerializer(instance=queryset, many=True)
        return serializer.data
