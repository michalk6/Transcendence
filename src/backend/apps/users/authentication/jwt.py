from typing import TypeVar

from django.contrib.auth import get_user_model
from rest_framework.request import Request
from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import Token
from django.contrib.auth.models import AbstractBaseUser
from rest_framework_simplejwt.models import TokenUser
from django.conf import settings

AuthUser = TypeVar("AuthUser", AbstractBaseUser, TokenUser)

User = get_user_model()


class CookieJWTAuthentication(JWTAuthentication):
    def enforce_csrf(self, request):
        """
        Enforce CSRF validation same as in SessionAuthentication.
        """
        def dummy_get_response(request):  # pragma: no cover
            return None

        check = CSRFCheck(dummy_get_response)  # type: ignore
        # populates request.META['CSRF_COOKIE'], which is used in process_view()
        check.process_request(request)
        reason = check.process_view(request, None, (), {})  # type: ignore
        if reason:
            # CSRF failed, bail with explicit error message
            raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)

    def authenticate(self, request: Request) -> tuple[AuthUser, Token] | None:
        raw_token = request.COOKIES.get(
            settings.SIMPLE_JWT.get("AUTH_COOKIE", "access_token")
        )

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token.encode("utf-8"))

        self.enforce_csrf(request)

        return self.get_user(validated_token), validated_token
