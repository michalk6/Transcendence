from rest_framework import serializers
from apps.games.tic_tac_toe.models import Match


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ["id", "player_x", "player_o", "winner", "status"]
        read_only_fields = fields
