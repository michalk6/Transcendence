from rest_framework import serializers


class AvatarUploadSerializer(serializers.Serializer):
    avatar = serializers.ImageField(write_only=True)
