from django.urls import path
from apps.relations import views


urlpatterns = [
    path("friend-requests/", views.SendFriendRequestView.as_view()),
    path("friend-requests/<int:pk>/accept/", views.AcceptFriendRequestView.as_view()),
    path("friend-requests/<int:pk>/reject/", views.RejectFriendRequestView.as_view()),
]
