from rest_framework import generics
from apps.games.tic_tac_toe.serializers import MatchSerializer
from apps.games.tic_tac_toe.models import Match


class MatchListCreateView(generics.ListCreateAPIView):
    serializer_class = MatchSerializer
    queryset = Match.objects.filter(status=Match.GameStatus.WAITING)

    def perform_create(self, serializer):
        serializer.save(player_x=self.request.user)
