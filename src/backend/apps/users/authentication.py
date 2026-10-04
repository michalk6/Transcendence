from typing import TypeVar

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import Token
from django.contrib.auth.models import AbstractBaseUser
from rest_framework_simplejwt.models import TokenUser
from django.conf import settings

AuthUser = TypeVar("AuthUser", AbstractBaseUser, TokenUser)

User = get_user_model()


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            user = User.objects.get(email=username)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            User().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

        return None


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request: Request) -> tuple[AuthUser, Token] | None:
        raw_token = request.COOKIES.get(
            settings.SIMPLE_JWT.get("AUTH_COOKIE", "access_token")
        )

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token.encode("utf-8"))

        return self.get_user(validated_token), validated_token
