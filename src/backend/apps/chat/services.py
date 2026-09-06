from typing import TYPE_CHECKING
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.chat.models import ChatRoom

if TYPE_CHECKING:
    from apps.users.models import User
else:
    User = get_user_model()


def create_private_chat_room(member1: User, member2: User) -> ChatRoom:
    with transaction.atomic():
        list(
            User.objects
            .filter(pk__in=[member1.pk, member2.pk])
            .order_by("pk")
            .select_for_update()
        )
        existing_room: ChatRoom | None = (
            ChatRoom.objects
            .filter(room_type=ChatRoom.RoomType.PRIVATE)
            .filter(members=member1)
            .filter(members=member2)
            .first()
        )
        if existing_room:
            return existing_room

        chat_room = ChatRoom.objects.create(
            room_type=ChatRoom.RoomType.PRIVATE
        )
        chat_room.members.set([member1, member2])
    return chat_room
