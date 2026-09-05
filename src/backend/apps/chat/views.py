from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics
from apps.chat.serializers import (
    ChatRoomSerializer, MessageSerializer,
    ChatRoomCreateSerializer, MessageCreateSerializer
)
from typing import cast, TYPE_CHECKING

if TYPE_CHECKING:
    from apps.users.models import User
else:
    User = get_user_model()


class ChatRoomListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == "POST":
            return ChatRoomCreateSerializer
        return ChatRoomSerializer

    def get_queryset(self):
        user = cast(User, self.request.user)
        return (
            user.chat_rooms
            .prefetch_related("members")
            .select_related("last_message__sender")
        )


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        user = cast(User, self.request.user)
        chat_room = get_object_or_404(
            user.chat_rooms.all(),
            pk=self.kwargs["pk"],
        )
        return chat_room.messages.all()

class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageCreateSerializer
