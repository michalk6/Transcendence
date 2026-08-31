from django.contrib.auth import get_user_model
from rest_framework import generics
from apps.chat.serializers import (
    ChatRoomSerializer,
)
from typing import cast, TYPE_CHECKING

if TYPE_CHECKING:
    from apps.users.models import User
else:
    User = get_user_model()


class ChatRoomListView(generics.ListAPIView):
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        user = cast(User, self.request.user)
        return (
            user.chat_rooms
            .prefetch_related("members")
            .select_related("last_message__sender")
        )
