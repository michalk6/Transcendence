from django.urls import path
from apps.chat.consumers import ChatConsumer, GeneralChatConsumer


websocket_urlpatterns = [
    path("ws/chat/", ChatConsumer.as_asgi()),  # type: ignore
    path("ws/chat/general/", GeneralChatConsumer.as_asgi()),  # type: ignore
]
