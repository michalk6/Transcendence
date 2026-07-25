from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
        ]


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True, required=True,
    )
    new_password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True, required=True,
    )
    repeat_password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True, required=True,
    )

    def validate(self, attrs):
        user: User = self.context["request"].user
        if not user.check_password(attrs["current_password"]):
            raise serializers.ValidationError(
                {
                    "current_password": [
                        "Current password is incorrect.",
                    ],
                },
            )

        if attrs["new_password"] != attrs["repeat_password"]:
            raise serializers.ValidationError(
                {"password": "password field didn't match"}
            )

        return attrs

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def save(self, **kwargs):
        user: User = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
