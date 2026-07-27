from rest_framework import generics, status
from rest_framework.response import Response
from apps.users.serializers.user_serializers import (
    UserSerializer,
    PasswordChangeSerializer,
)
from apps.users.services.token_services import reset_refresh_tokens


class CurrentUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class PasswordChangeView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        refresh_token = reset_refresh_tokens(request.user)
        return Response(
            {
                "message": "Password changed successfully",
                "refresh": str(refresh_token),
                "access": str(refresh_token.access_token),
            },
            status=status.HTTP_200_OK,
        )
