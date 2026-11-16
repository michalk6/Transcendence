from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import generics
from rest_framework.exceptions import NotAuthenticated, ValidationError
from rest_framework.permissions import AllowAny
from apps.games.tic_tac_toe.serializers import MatchSerializer, RankingSerializer
from apps.games.tic_tac_toe.models import Match
from apps.games.tic_tac_toe.services import create_match, broadcast_matches_updated, has_open_match
from asgiref.sync import async_to_sync

User = get_user_model()


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                name="mine",
                type=OpenApiTypes.BOOL,
                description="`true` shows waiting and in progress matches of the logged user "
                            "(use it to come back to a match). Login is required.",
            ),
        ],
    ),
)
class MatchListCreateView(generics.ListCreateAPIView):
    serializer_class = MatchSerializer
    queryset = Match.objects.filter(status=Match.GameStatus.WAITING)

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = Match.objects.select_related("player_x", "player_o").order_by("id")
        if self.request.query_params.get("mine") != "true":
            return queryset.filter(status=Match.GameStatus.WAITING)

        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()
        return queryset.filter(
            Q(player_x=user) | Q(player_o=user),
            status__in=[Match.GameStatus.WAITING, Match.GameStatus.IN_PROGRESS],
        )

    def perform_create(self, serializer):
        if has_open_match(self.request.user):
            raise ValidationError({"detail": "You already have an open match."})
        match = serializer.save(player_x=self.request.user)
        create_match(match.pk)
        async_to_sync(broadcast_matches_updated)()


class RankingListView(generics.ListAPIView):
    serializer_class = RankingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        finished_wins = Q(games_won__status=Match.GameStatus.FINISHED)
        queryset = User.objects.annotate(wins=Count("games_won", filter=finished_wins))
        return queryset.filter(wins__gt=0).order_by("-wins", "username")
