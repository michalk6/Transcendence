from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.users.serializers.user_serializers import (
    PrivateUserSerializer,
    PasswordChangeSerializer,
    PublicUserSerializer,
)
from apps.users.services.token_services import reset_refresh_tokens
from apps.users.pagination import UserListPagination
from apps.users.queries import (
    annotate_friendship_status,
    annotate_and_sort_by_friendship_status,
    annotate_mutual_friend_count,
    filter_users_by_naming_fields,
    filter_mutual_friends,
    filter_not_mutual_friends,
)
from apps.users.schemas import search_user_doc, friend_list_doc, block_list_doc, password_change_doc
from typing import TYPE_CHECKING, cast


if TYPE_CHECKING:
    from apps.users.models import User
else:
    User = get_user_model()


class CurrentUserView(generics.RetrieveUpdateAPIView):
    serializer_class = PrivateUserSerializer

    def get_object(self):
        return self.request.user


class PublicUserView(generics.RetrieveAPIView):
    serializer_class = PublicUserSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    lookup_field = "username"

    def get_queryset(self):
        user = cast(User | AnonymousUser, self.request.user)
        queryset = super().get_queryset()
        queryset = annotate_friendship_status(queryset, user)
        queryset = annotate_mutual_friend_count(queryset, user)
        return queryset


@search_user_doc
class SearchUsersView(generics.ListAPIView):
    serializer_class = PublicUserSerializer
    permission_classes = [AllowAny]
    pagination_class = UserListPagination

    def get_queryset(self):
        queryset = User.objects.all()
        q = self.request.query_params.get("q")
        if not q:
            return User.objects.none()
        queryset = filter_users_by_naming_fields(queryset, q)
        user = cast(User | AnonymousUser, self.request.user)
        queryset = annotate_and_sort_by_friendship_status(queryset, user)
        queryset = annotate_mutual_friend_count(queryset, user)

        return queryset


@friend_list_doc
class FriendListView(generics.ListAPIView):
    serializer_class = PublicUserSerializer
    permission_classes = [AllowAny]
    pagination_class = UserListPagination

    def get_queryset(self):
        username = self.kwargs["username"]
        inspected_user: User = get_object_or_404(User, username=username)
        user = cast(User | AnonymousUser, self.request.user)

        queryset = inspected_user.friends.all()

        mutuality = self.request.query_params.get("mutuality")
        if mutuality == "mutual":
            queryset = filter_mutual_friends(queryset, user)
        elif mutuality == "not_mutual":
            queryset = filter_not_mutual_friends(queryset, user)

        search_term = self.request.query_params.get("search")
        if search_term:
            queryset = filter_users_by_naming_fields(queryset, search_term)

        queryset = annotate_and_sort_by_friendship_status(queryset, user)
        queryset = annotate_mutual_friend_count(queryset, user)

        return queryset


@block_list_doc
class BlocklistListView(generics.ListAPIView):
    serializer_class = PublicUserSerializer
    pagination_class = UserListPagination

    def get_queryset(self):
        user: User = cast(User, self.request.user)
        queryset = user.blocklist.all()

        search_term = self.request.query_params.get("search")
        if search_term:
            queryset = filter_users_by_naming_fields(queryset, search_term)

        return queryset


@password_change_doc
class PasswordChangeView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        refresh_token = reset_refresh_tokens(request.user)
        return Response(
            {
                "message": "Password changed successfully",
                "refresh": str(refresh_token),
                "access": str(refresh_token.access_token),
            },
            status=status.HTTP_200_OK,
        )
