from django.urls import path
from apps.chat import views


urlpatterns = [
    path("chat-rooms/", views.ChatRoomListCreateView.as_view()),
    path("chat-rooms/<uuid:pk>/leave/", views.ChatRoomLeaveView.as_view()),
    path("chat-rooms/<uuid:pk>/rename/", views.ChatRoomChangeNameView.as_view()),
    path("chat-rooms/<uuid:pk>/members/", views.ChatRoomAddMembersView.as_view()),
    path("chat-rooms/<uuid:pk>/messages/", views.MessageListView.as_view()),
    path("chat-rooms/user/<int:user_id>/", views.ChatRoomRetrieveByUserIdView.as_view()),
    path("message/", views.MessageCreateView.as_view()),
    path("message/<uuid:pk>/", views.MessageUpdateDeleteView.as_view()),
]
