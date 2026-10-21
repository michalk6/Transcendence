from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from http.cookies import Morsel, SimpleCookie
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed, TokenError
from django.conf import settings

User = get_user_model()


@database_sync_to_async
def get_user(access_token: Morsel[str] | None) -> User | AnonymousUser:
    if access_token is None:
        return AnonymousUser()

    authenticator = JWTAuthentication()
    try:
        validated_token = authenticator.get_validated_token(
            access_token.value.encode("utf-8")
        )
        return authenticator.get_user(validated_token)
    except (InvalidToken, TokenError, AuthenticationFailed):
        return AnonymousUser()


class CookieJWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        scope["user"] = AnonymousUser()

        if scope["type"] == "websocket":
            headers = dict(scope.get("headers", []))
            cookie_header = headers.get(b"cookie", b"").decode("latin1")

            cookies = SimpleCookie(cookie_header)
            access_token = cookies.get(
                settings.SIMPLE_JWT.get("AUTH_COOKIE", "access_token")
            )
            scope["user"] = await get_user(access_token)

        return await self.app(scope, receive, send)
