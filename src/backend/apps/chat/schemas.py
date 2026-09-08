from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiResponse
)
from rest_framework import status
from apps.chat.serializers import (
    ChatRoomAddMembersSerializer, ChatRoomChangeNameSerializer, ChatRoomSerializer,
)


chat_room_leave_doc = extend_schema_view(
    post=extend_schema(
        request=None,
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Cannot leave a private chat room."
            )
        }
    )
)


message_create_doc = extend_schema_view(
    post=extend_schema(
        description="Provide `chat_room` or `receiver`.  \n"
                    "Both may be provided if the receiver belongs to the chat room."
    )
)


chat_room_add_members_doc = extend_schema_view(
    post=extend_schema(
        responses={
            status.HTTP_200_OK: ChatRoomAddMembersSerializer(),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Cannot add members to private room."
            ),
        }
    )
)


chat_room_retrieve_by_user_id_doc = extend_schema_view(
    get=extend_schema(
        description=(
            "Returns an existing private chat room with the specified user.  \n"
            "A chat room is not created if it does not exist."
        ),
        responses={
            status.HTTP_200_OK: ChatRoomSerializer(),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Cannot message yourself."
            ),
        },
    )
)


chat_room_change_name_doc = extend_schema_view(
    patch=extend_schema(
        responses={
            status.HTTP_200_OK: ChatRoomChangeNameSerializer(),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="New name cannot be blank."
            ),
        },
    ),
    put=extend_schema(
        description="Method \"PUT\" not allowed.",
    )
)
