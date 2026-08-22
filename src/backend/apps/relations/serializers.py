from apps.relations.models import FriendRequest
from rest_framework import serializers
from django.contrib.auth import get_user_model
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from apps.users.models import User
else:
    User = get_user_model()


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = [
            "id",
            "sender",
            "receiver",
        ]


class FriendRequestSendSerializer(serializers.Serializer):
    receiver = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
    )

    def validate(self, attrs):
        sender: User = self.context["request"].user
        receiver: User = attrs["receiver"]

        if receiver == sender:
            raise serializers.ValidationError({
                "receiver": "Cannot invite yourself"
            })

        if sender.is_blocked_by(receiver):
            raise serializers.ValidationError({
                "receiver": f"user: {receiver.username} is blocking you"
            })

        if sender.is_blocking(receiver):
            raise serializers.ValidationError({
                "receiver": f"you have blocked user: {receiver.username}"
            })

        if sender.is_friend(receiver):
            raise serializers.ValidationError({
                "receiver": f"user: {receiver.username} is already your friend"
            })

        if FriendRequest.already_exists(sender, receiver):
            raise serializers.ValidationError({
                "receiver": f"friend request to {receiver.username} is already pending"
            })

        return attrs
