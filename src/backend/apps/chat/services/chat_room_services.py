from typing import TYPE_CHECKING, Iterable
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.chat.models import ChatRoom

if TYPE_CHECKING:
    from apps.users.models import User
else:
    User = get_user_model()


def filter_blocklisted_members(
    user: User, members: Iterable[User],
) -> tuple[list[User], list[User], list[User]]:
    accepted_members, blocking, blocked_by = [], [], []

    members_pks = [m.pk for m in members]
    blocklist = set(user.blocklist.filter(pk__in=members_pks))
    blocklisted = set(user.blocklisted.filter(pk__in=members_pks))

    for member in members:
        if member in blocklist:
            blocking.append(member)
        elif member in blocklisted:
            blocked_by.append(member)
        else:
            accepted_members.append(member)
    return accepted_members, blocking, blocked_by


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
