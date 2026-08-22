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
                description="Invalid input data."
            ),
        },
    ),
)
