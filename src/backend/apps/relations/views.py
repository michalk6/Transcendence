from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from typing import cast
from apps.relations.serializers import FriendRequestSendSerializer, FriendRequestSerializer
from apps.relations.models import FriendRequest


User = get_user_model()


class SendFriendRequest(generics.GenericAPIView):
    serializer_class = FriendRequestSendSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sender: User = cast(User, request.user)
        receiver: User = serializer.validated_data["receiver"]

        FriendRequest.objects.create(sender=sender, receiver=receiver)

        return Response(
            {"request": "Friend request sent successfully"},
            status.HTTP_201_CREATED,
        )
