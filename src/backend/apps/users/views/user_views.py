from rest_framework import generics
from apps.users.serializers.user_serializers import UserSerializer


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
