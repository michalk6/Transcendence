from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from apps.users.serializers.auth_serializers import RegisterSerializer
from apps.users.services.token_services import invalidate_all_refresh_tokens
from apps.users.utils.cookie_utils import set_auth_cookies, delete_auth_cookies
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from apps.users.schemas import logout_all_docs, register_doc, login_doc, token_refresh_doc, logout_doc


@register_doc
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_user = serializer.save()
        user_data = serializer.data

        refresh = RefreshToken.for_user(new_user)

        response_data = {
            "user": user_data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        headers = self.get_success_headers(serializer.data)
        response = Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
        response = set_auth_cookies(request, response)
        response.data["detail"] = "Successfully registered."
        return response


@login_doc
class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            response = set_auth_cookies(request, response)
            response.data["detail"] = "Successfully logged in."

        return response


@token_refresh_doc
@method_decorator(csrf_protect, name='dispatch')
class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(
            settings.SIMPLE_JWT.get("AUTH_COOKIE_REFRESH", "refresh_token")
        )
        if not refresh_token:
            return Response(
                {"detail": "Refresh token cookie is missing."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e

        response = Response(serializer.validated_data, status=status.HTTP_200_OK)

        response = set_auth_cookies(request, response)
        response.data["detail"] = "Tokens successfully refreshed."

        return response


@logout_doc
@method_decorator(csrf_protect, name='dispatch')
class CookieTokenBlacklistView(TokenBlacklistView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(
            settings.SIMPLE_JWT.get("AUTH_COOKIE_REFRESH", "refresh_token")
        )
        if not refresh_token:
            return Response(
                {"detail": "Refresh token cookie is missing."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e
        response = Response(serializer.validated_data, status=status.HTTP_200_OK)

        response = delete_auth_cookies(response)
        response.data["detail"] = "Successfully logged out."

        return response


@logout_all_docs
@method_decorator(csrf_protect, name='dispatch')
class LogoutAllView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        invalidate_all_refresh_tokens(request.user)

        response = Response(
            {
                "detail": "Logged out from all sessions successfully",
            },
            status=status.HTTP_200_OK,
        )

        return delete_auth_cookies(response)
