from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from rest_framework import generics, status
from rest_framework.response import Response
from typing import cast
from apps.relations.serializers import FriendRequestSendSerializer, FriendRequestSerializer
from apps.relations.models import FriendRequest
from apps.relations.services import accept_request


User = get_user_model()


class ReceivedFriendRequestListView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(
            receiver=self.request.user,
        )


class SentFriendRequestListView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(
            sender=self.request.user,
        )


class SendFriendRequestView(generics.GenericAPIView):
    serializer_class = FriendRequestSendSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sender: User = cast(User, request.user)
        receiver: User = serializer.validated_data["receiver"]

        friend_request: FriendRequest = FriendRequest(sender=sender, receiver=receiver)

        reverse_request: FriendRequest | None = friend_request.get_reverse()
        if reverse_request:
            accept_request(reverse_request)
            return Response(
                {"message": "Friend added"},
                status.HTTP_200_OK,
            )

        friend_request.save()

        return Response(
            {"message": "Friend request sent successfully"},
            status.HTTP_201_CREATED,
        )


class AcceptFriendRequestView(generics.GenericAPIView):
    queryset = FriendRequest.objects.all()

    def post(self, request, *args, **kwargs):
        friend_request: FriendRequest = self.get_object()

        if request.user != friend_request.receiver:
            raise PermissionDenied()

        accept_request(friend_request)
        return Response(
            {"message": "Friend request accepted"},
            status.HTTP_200_OK,
        )


class RejectFriendRequestView(generics.GenericAPIView):
    queryset = FriendRequest.objects.all()

    def post(self, request, *args, **kwargs):
        friend_request: FriendRequest = self.get_object()

        if request.user != friend_request.receiver:
            raise PermissionDenied()

        friend_request.delete()
        return Response(
            {"message": "Friend request rejected"},
            status.HTTP_200_OK,
        )
