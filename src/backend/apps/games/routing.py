from apps.games.tic_tac_toe.routing import websocket_urlpatterns as tic_tac_toe_ws_urlpatterns


websocket_urlpatterns = [
    *tic_tac_toe_ws_urlpatterns,
]
