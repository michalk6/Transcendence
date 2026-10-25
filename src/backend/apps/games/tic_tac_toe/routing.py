from django.urls import path
from apps.games.tic_tac_toe.consumers import GameConsumer


websocket_urlpatterns = [
    path("ws/games/tictactoe/<int:match_id>/", GameConsumer.as_asgi())  # type: ignore
]
