from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password"]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data) -> User:
        new_user = User.objects.create_user(  # type: ignore
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return new_user
