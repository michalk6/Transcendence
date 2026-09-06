from django.urls import path
from apps.chat import views


urlpatterns = [
    path("chat-rooms/", views.ChatRoomListCreateView.as_view()),
    path("chat-rooms/<uuid:pk>/messages/", views.MessageListView.as_view()),
    path("message/", views.MessageCreateView.as_view()),
    path("message/<uuid:pk>/", views.MessageUpdateDeleteView.as_view()),
]
