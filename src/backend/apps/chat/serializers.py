from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.chat.models import ChatRoom, Message
from django.contrib.auth import get_user_model
from typing import TYPE_CHECKING, cast
from apps.chat.services import create_private_chat_room

if TYPE_CHECKING:
    from apps.users.models import User
else:
    User = get_user_model()


class ChatRoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "name",
            "room_type",
            "members",
            "created_at",
            "last_message",
            "last_message_at",
        ]

    name = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    def get_name(self, instance):
        if not instance.name and instance.room_type == ChatRoom.RoomType.PRIVATE:
            member = instance.members.exclude(
                pk=self.context["request"].user.pk
            ).first()
            if member:
                name = member.username
                if member.first_name or member.last_name:
                    name = f"{name} ({f'{member.first_name} {member.last_name}'.strip()})"
                return name

        return instance.name

    def get_last_message(self, instance):
        if not instance.last_message:
            return None
        sender = instance.last_message.sender
        if not sender:
            sender_name = "Unknown"
        elif sender == self.context["request"].user:
            sender_name = "Me"
        else:
            sender_name = sender.username
        return f"{sender_name}: {instance.last_message.content[:20]}"


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            "content",
            "created_at",
        ]


class ChatRoomCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "name",
            "members",
            "warnings",
        ]

    warnings = serializers.SerializerMethodField(read_only=True)

    def validate_members(self, value):
        distinct = []
        encountered = set()
        for member in value:
            if member not in encountered:
                distinct.append(member)
                encountered.add(member)
        return distinct

    def build_warnings(self, blocking, blocked_by):
        warnings = {}
        blocking = [
            {"user_id": m.pk, "username": m.username}
            for m in blocking
        ]

        blocked_by = [
            {"user_id": m.pk, "username": m.username}
            for m in blocked_by
        ]

        if blocking:
            warnings["blocking"] = {
                "message": "Some users cannot be added because you have blocked them.",
                "users": blocking,
            }
        if blocked_by:
            warnings["blocked_by"] = {
                "message": "Some users cannot be added because they have blocked you.",
                "users": blocked_by,
            }
        return warnings

    def get_warnings(self, instance):
        return self.build_warnings(
            getattr(instance, "_blocking", []),
            getattr(instance, "_blocked_by", []),
        )

    def filter_blocklisted_members(self, members):
        user = self.context["request"].user
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

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data_members = list(validated_data.get("members", []))
        accepted_members, blocking, blocked_by = (
            self.filter_blocklisted_members(
                validated_data_members
            )
        )

        if user not in accepted_members:
            accepted_members.append(user)

        if len(accepted_members) < 2:
            raise ValidationError({
                "members": ["This list must contain at least one valid member."],
                "warnings": self.build_warnings(blocking, blocked_by),
            })

        if not validated_data.get("name"):
            validated_data["name"] = " ".join(
                [m.username for m in accepted_members]
            )[:100]

        validated_data["members"] = accepted_members
        validated_data["room_type"] = ChatRoom.RoomType.GROUP

        room = super().create(validated_data)
        room._blocking = blocking
        room._blocked_by = blocked_by
        return room


class MessageCreateSerializer(serializers.Serializer):
    chat_room = serializers.PrimaryKeyRelatedField(
        queryset=ChatRoom.objects.all(),
        required=False,
    )
    receiver = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        write_only=True,
    )
    content = serializers.CharField()

    def validate(self, attrs):
        user: User = cast(User, self.context["request"].user)
        chat_room: ChatRoom | None = attrs.get("chat_room", None)
        receiver: User | None = attrs.get("receiver", None)

        if not chat_room and not receiver:
            raise ValidationError("You must provide chat room or receiver.")

        if chat_room and not chat_room.members.filter(pk=user.pk).exists():
            raise ValidationError(f'Invalid pk "{chat_room.pk}" - object does not exist.')

        if chat_room and receiver:
            if not chat_room.members.filter(pk=receiver.pk).exists():
                raise ValidationError("Receiver is not member of given chat room.")

        if receiver and receiver == user:
            raise ValidationError({"receiver": "You cannot send a message to yourself."})

        if chat_room and chat_room.room_type == ChatRoom.RoomType.PRIVATE:
            if not receiver:
                receiver = chat_room.members.exclude(pk=user.pk).first()
        if receiver and user.is_blocked_by(receiver):
            raise ValidationError({"receiver": f"{receiver.username} is blocking you."})
        if receiver and user.is_blocking(receiver):
            raise ValidationError({"receiver": f"You are blocking {receiver.username}."})

        return attrs

    def create(self, validated_data):
        user: User = self.context["request"].user
        chat_room: ChatRoom | None = validated_data.get("chat_room", None)
        receiver: User | None = validated_data.pop("receiver", None)
        with transaction.atomic():
            if not chat_room:
                assert receiver is not None
                chat_room = create_private_chat_room(user, receiver)
            message = Message.objects.create(
                sender=user,
                content=validated_data["content"],
                chat_room=chat_room,
            )
            chat_room.last_message = message
            chat_room.last_message_at = message.created_at
            chat_room.save(update_fields=["last_message", "last_message_at"])
        return message


class MessageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["content"]
