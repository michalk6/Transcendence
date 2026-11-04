from pathlib import Path
from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.avatars.models import Avatar, avatar_storage
from apps.avatars.serializers import AvatarUploadSerializer
from apps.avatars.services import save_avatar, delete_avatar


User = get_user_model()
DEFAULT_AVATAR = Path(__file__).resolve().parent / "static_default" / "default_avatar.svg"


def send_default_avatar():
    return FileResponse(open(DEFAULT_AVATAR, "rb"), content_type="image/svg+xml")


class MyAvatarView(generics.GenericAPIView):
    serializer_class = AvatarUploadSerializer
    parser_classes = [MultiPartParser]

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        save_avatar(request.user, serializer.validated_data["avatar"])
        return Response(
            {"message": "Avatar updated", "url": f"/api/avatars/{request.user.username}/"},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        delete_avatar(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AvatarDetailView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = None

    def get(self, request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        avatar = Avatar.objects.filter(user=user).first()
        if avatar is None:
            return send_default_avatar()
        if not avatar_storage.exists(avatar.file_name):
            return send_default_avatar()
        response = FileResponse(avatar_storage.open(avatar.file_name), content_type="image/png")
        response["Cache-Control"] = "no-cache"
        return response
