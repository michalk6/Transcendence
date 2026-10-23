from apps.chat.routing import websocket_urlpatterns as chat_ws_urlpatterns


websocket_urlpatterns = [
    *chat_ws_urlpatterns,
]
