from rest_framework import serializers
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

    def get_name(self, object):
        if not object.name and object.room_type == ChatRoom.RoomType.PRIVATE:
            member = object.members.exclude(
                pk=self.context["request"].user.pk
            ).first()
            if member:
                name = member.username
                if member.first_name or member.last_name:
                    name = f"{name} ({f'{member.first_name} {member.last_name}'.strip()})"
                return name

        return object.name

    def get_last_message(self, object):
        if not object.last_message:
            return None
        sender = object.last_message.sender
        if not sender:
            sender_name = "Unknown"
        elif sender == self.context["request"].user:
            sender_name = "Me"
        else:
            sender_name = sender.username
        return f"{sender_name}: {object.last_message.content[:20]}"


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            "content",
            "created_at",
        ]


class ChatRoomCreateSerializer(serializers.Serializer):
    pass


class MessageSendSerializer(serializers.Serializer):
    pass
