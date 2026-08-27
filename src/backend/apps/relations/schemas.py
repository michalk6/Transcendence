from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    inline_serializer, OpenApiResponse,
)
from rest_framework import serializers, status


send_friend_request_response = OpenApiResponse(
    response=inline_serializer(
        name="SendFriendRequestResponse",
        fields={"message": serializers.CharField()},
    ),
)


send_friend_request_doc = extend_schema_view(
    post=extend_schema(
        responses={
            status.HTTP_200_OK: send_friend_request_response,
            status.HTTP_201_CREATED: send_friend_request_response,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Invalid input data.",
            ),
        },
    ),
)


accept_reject_friend_request_doc = extend_schema_view(
    post=extend_schema(
        request=None,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=inline_serializer(
                    name="AcceptRejectFriendRequestResponse",
                    fields={
                        "message": serializers.CharField(),
                    },
                ),
            ),
        },
    ),
)


delete_friend_request_doc = extend_schema_view(
    delete=extend_schema(
        request=None,
        responses=None,
    ),
)


remove_friend_doc = extend_schema_view(
    post=extend_schema(
        request=None,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=inline_serializer(
                    name="RemoveFriendResponse",
                    fields={
                        "message": serializers.CharField(),
                    },
                ),
            ),
        },
    ),
)


block_user_doc = extend_schema_view(
    post=extend_schema(
        request=None,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=inline_serializer(
                    name="BlockUserResponse",
                    fields={
                        "message": serializers.CharField(),
                    },
                ),
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Authenticated user cannot block themselves.",
            ),
            status.HTTP_409_CONFLICT: OpenApiResponse(
                description="Authenticated user cannot block their friend.",
            ),
        },
    ),
)


unblock_user_doc = extend_schema_view(
    post=extend_schema(
        request=None,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=inline_serializer(
                    name="UnblockUserResponse",
                    fields={
                        "message": serializers.CharField(),
                    },
                ),
            ),
        },
    ),
)
