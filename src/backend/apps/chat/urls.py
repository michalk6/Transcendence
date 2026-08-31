from django.urls import path
from apps.chat import views


urlpatterns = [
    path("chat-rooms/", views.ChatRoomListView.as_view())
]
