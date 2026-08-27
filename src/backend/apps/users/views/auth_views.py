from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.serializers.auth_serializers import RegisterSerializer
from apps.users.services.token_services import invalidate_all_refresh_tokens
from apps.users.schemas import logout_all_docs, register_doc


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
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


@logout_all_docs
class LogoutAllView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        invalidate_all_refresh_tokens(request.user)

        return Response(
            {
                "message": "Logged out from all sessions successfully",
            },
            status=status.HTTP_200_OK,
        )
