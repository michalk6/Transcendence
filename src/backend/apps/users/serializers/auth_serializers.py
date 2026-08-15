from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth import get_user_model
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from apps.users.models import User
else:
    User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    repeat_password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True, required=True
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "repeat_password"]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["repeat_password"]:
            raise serializers.ValidationError({"password": "password field didn't match"})
        return attrs

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data) -> User:
        new_user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return new_user
