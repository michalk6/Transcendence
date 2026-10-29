from apps.chat.routing import websocket_urlpatterns as chat_ws_urlpatterns
from apps.games.routing import websocket_urlpatterns as games_ws_urlpatterns


websocket_urlpatterns = [
    *chat_ws_urlpatterns,
    *games_ws_urlpatterns,
]
