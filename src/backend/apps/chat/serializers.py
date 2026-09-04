from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.chat.models import ChatRoom, Message


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


class MessageSendSerializer(serializers.Serializer):
    pass
