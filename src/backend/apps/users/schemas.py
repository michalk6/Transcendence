from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    inline_serializer,
    OpenApiResponse, OpenApiParameter,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers, status
from apps.users.serializers.auth_serializers import RegisterSerializer


logout_all_docs = extend_schema_view(
    post=extend_schema(
        request=None,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=inline_serializer(
                    name="LogoutAllResponse",
                    fields={"message": serializers.CharField()},
                ),
            ),
        },
    ),
)


register_doc = extend_schema_view(
    post=extend_schema(
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=inline_serializer(
                    name="RegisterResponse",
                    fields={
                        "user": RegisterSerializer(),
                        "refresh": serializers.CharField(),
                        "access": serializers.CharField(),
                    },
                ),
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Invalid input data.",
            ),
        },
    ),
)


search_user_doc = extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                name="q",
                type=OpenApiTypes.STR,
                description="Search users by `username`, `first_name` or `last_name`.  \n"
                            "Search terms are split by whitespace and must all match.  \n"
                            "Returns an empty list when the parameter is omitted.",
            ),
        ],
    ),
)


friend_list_doc = extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                name="mutuality",
                type=OpenApiTypes.STR,
                description="Enables filtering friends based on mutuality:  \n"
                            "- `mutual` - shows mutual friends,\n"
                            "- `not_mutual` - shows friends which authenticated user doesn't know.\n\n"
                            "Filtering is applied only when user is logged in.",
                enum=["mutual", "not_mutual"],
            ),
        ],
    ),
)


password_change_doc = extend_schema_view(
    patch=extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=inline_serializer(
                    name="PasswordChangeResponse",
                    fields={
                        "message": serializers.CharField(),
                        "refresh": serializers.CharField(),
                        "access": serializers.CharField(),
                    },
                ),
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Invalid input data.",
            ),
        },
    ),
)
