from django.contrib.auth import get_user_model
from rest_framework import serializers
from apps.games.tic_tac_toe.models import Match

User = get_user_model()


class MatchSerializer(serializers.ModelSerializer):
    player_x_username = serializers.CharField(
        source="player_x.username", read_only=True, allow_null=True,
    )
    player_o_username = serializers.CharField(
        source="player_o.username", read_only=True, allow_null=True,
    )

    class Meta:
        model = Match
        fields = [
            "id", "player_x", "player_x_username",
            "player_o", "player_o_username", "winner", "status",
        ]
        read_only_fields = fields


class RankingSerializer(serializers.ModelSerializer):
    wins = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "wins"]
