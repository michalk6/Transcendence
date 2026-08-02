from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.users.serializers.user_serializers import (
    PrivateUserSerializer,
    PasswordChangeSerializer,
    PublicUserSerializer,
)
from apps.users.services.token_services import reset_refresh_tokens


User = get_user_model()


class CurrentUserView(generics.RetrieveUpdateAPIView):
    serializer_class = PrivateUserSerializer

    def get_object(self):
        return self.request.user


class PublicUserView(generics.RetrieveAPIView):
    serializer_class = PublicUserSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    lookup_field = "username"


class SearchUserView(generics.ListAPIView):
    serializer_class = PublicUserSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = User.objects.all()
        q = self.request.query_params.get("q")
        if not q:
            return User.objects.none()
        queryset = queryset.filter(
            Q(username__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
        )
        return queryset


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
