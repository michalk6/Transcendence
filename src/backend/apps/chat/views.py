from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.request import Request
from apps.chat.serializers import (
    ChatRoomSerializer, MessageSerializer,
    ChatRoomCreateSerializer, MessageCreateSerializer,
    MessageUpdateSerializer,
    ChatRoomAddMembersSerializer,
)
from apps.chat.models import Message, ChatRoom
from apps.chat.schemas import (
    chat_room_leave_doc, message_create_doc,
    chat_room_add_members_doc, chat_room_retrieve_by_user_id_doc,
)
from rest_framework.exceptions import ValidationError, NotFound
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


@chat_room_retrieve_by_user_id_doc
class ChatRoomRetrieveByUserIdView(generics.RetrieveAPIView):
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        user = cast(User, self.request.user)
        return user.chat_rooms.filter(room_type=ChatRoom.RoomType.PRIVATE)

    def get_object(self):
        user = cast(User, self.request.user)
        target_user_id = self.kwargs["user_id"]

        if target_user_id == user.pk:
            raise ValidationError({"detail": "Cannot message yourself."})

        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.filter(members=target_user_id).first()

        if not obj:
            raise NotFound("No ChatRoom matches the given query.")
        self.check_object_permissions(self.request, obj)
        return obj


@message_create_doc
class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageCreateSerializer


class MessageUpdateDeleteView(generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = MessageUpdateSerializer

    def get_queryset(self):
        user = cast(User, self.request.user)
        return user.messages.all()

    def perform_destroy(self, instance: Message):
        with transaction.atomic():
            chat_room = (
                ChatRoom.objects
                .filter(last_message=instance)
                .select_for_update()
                .first()
            )
            instance.delete()
            if chat_room:
                chat_room.last_message = chat_room.messages.all().first()
                if chat_room.last_message:
                    chat_room.last_message_at = chat_room.last_message.created_at
                    chat_room.save(update_fields=["last_message", "last_message_at"])
                elif chat_room.room_type == ChatRoom.RoomType.PRIVATE:
                    chat_room.delete()


@chat_room_leave_doc
class ChatRoomLeaveView(generics.GenericAPIView):
    def get_queryset(self):
        user = cast(User, self.request.user)
        return user.chat_rooms.all()

    def post(self, request, *args, **kwargs):
        user: User = cast(User, request.user)
        chat_room: ChatRoom = self.get_object()

        if chat_room.room_type == ChatRoom.RoomType.PRIVATE:
            return Response(
                {"detail": "Cannot leave a private chat room."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        with transaction.atomic():
            chat_room.members.remove(user)
            if not chat_room.members.exists():
                chat_room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@chat_room_add_members_doc
class ChatRoomAddMembersView(generics.GenericAPIView):
    serializer_class = ChatRoomAddMembersSerializer

    def get_queryset(self):
        user: User = cast(User, self.request.user)
        return user.chat_rooms.all()

    def post(self, request: Request, *args, **kwargs):
        chat_room: ChatRoom = self.get_object()
        if chat_room.room_type == ChatRoom.RoomType.PRIVATE:
            return Response(
                {"detail": "Cannot add members to private room."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = cast(
            ChatRoomAddMembersSerializer, self.get_serializer(
                instance=chat_room, data=request.data,
            )
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
