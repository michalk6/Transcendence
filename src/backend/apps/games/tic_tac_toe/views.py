from rest_framework import generics
from rest_framework.permissions import AllowAny
from apps.games.tic_tac_toe.serializers import MatchSerializer
from apps.games.tic_tac_toe.models import Match
from apps.games.tic_tac_toe.services import create_match, broadcast_matches_updated
from asgiref.sync import async_to_sync


class MatchListCreateView(generics.ListCreateAPIView):
    serializer_class = MatchSerializer
    queryset = Match.objects.filter(status=Match.GameStatus.WAITING)

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        match = serializer.save(player_x=self.request.user)
        create_match(match.pk)
        async_to_sync(broadcast_matches_updated)()
