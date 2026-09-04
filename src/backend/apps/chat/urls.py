from django.urls import path
from apps.chat import views


urlpatterns = [
    path("chat-rooms/", views.ChatRoomListCreateView.as_view()),
    path("chat-rooms/<uuid:pk>/messages/", views.MessageListView.as_view()),
]
