from django.contrib.auth import get_user_model
from django.core.exceptions import BadRequest
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from typing import cast
from apps.relations.serializers import FriendRequestSendSerializer, FriendRequestSerializer
from apps.relations.models import FriendRequest
from apps.relations.services import accept_request
from apps.relations.schemas import (
    send_friend_request_doc, accept_reject_friend_request_doc, delete_friend_request_doc,
    remove_friend_doc, block_user_doc, unblock_user_doc,
)
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from apps.users.models import User
else:
    User = get_user_model()


class ReceivedFriendRequestListView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        user: User = cast(User, self.request.user)
        return user.received_friend_requests.all()


class SentFriendRequestListView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        user: User = cast(User, self.request.user)
        return user.sent_friend_requests.all()


@send_friend_request_doc
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
                status=status.HTTP_200_OK,
            )

        friend_request.save()

        return Response(
            {"message": "Friend request sent successfully"},
            status=status.HTTP_201_CREATED,
        )


@accept_reject_friend_request_doc
class AcceptFriendRequestView(generics.GenericAPIView):
    def get_queryset(self):
        user = cast(User, self.request.user)
        return user.received_friend_requests.all()

    def post(self, request, *args, **kwargs):
        friend_request: FriendRequest = self.get_object()

        accept_request(friend_request)
        return Response(
            {"message": "Friend request accepted"},
            status=status.HTTP_200_OK,
        )


@accept_reject_friend_request_doc
class RejectFriendRequestView(generics.GenericAPIView):
    def get_queryset(self):
        user = cast(User, self.request.user)
        return user.received_friend_requests.all()

    def post(self, request, *args, **kwargs):
        friend_request: FriendRequest = self.get_object()

        friend_request.delete()
        return Response(
            {"message": "Friend request rejected"},
            status=status.HTTP_200_OK,
        )


@delete_friend_request_doc
class DeleteFriendRequestView(generics.DestroyAPIView):
    def get_queryset(self):
        user: User = cast(User, self.request.user)
        return FriendRequest.objects.filter(
            sender=user,
        )


@remove_friend_doc
class RemoveFriendView(generics.GenericAPIView):
    def get_queryset(self):
        user: User = cast(User, self.request.user)
        return user.friends.all()

    def post(self, request, *args, **kwargs):
        user = cast(User, request.user)
        to_remove: User = self.get_object()
        user.remove_friend(to_remove)
        return Response(
            {"message": f"User {to_remove} removed from your friend list"},
            status=status.HTTP_200_OK,
        )


@block_user_doc
class BlockUserView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        user: User = request.user
        to_block: User = get_object_or_404(User, pk=self.kwargs["pk"])

        if user == to_block:
            raise BadRequest()

        if user.is_friend(to_block):
            return Response(
                {
                    "detail":
                    f"User {to_block} is your friend. "
                    "Remove them from friend list first",
                },
                status=status.HTTP_409_CONFLICT,
            )

        user.block_user(to_block)
        return Response(
            {"message": f"User {to_block} blocked"},
            status=status.HTTP_200_OK,
        )


@unblock_user_doc
class UnblockUserView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        user: User = request.user
        to_unblock = get_object_or_404(User, pk=self.kwargs["pk"])

        user.unblock_user(to_unblock)
        return Response(
            {"message": f"User {to_unblock} unblocked"},
            status=status.HTTP_200_OK,
        )
