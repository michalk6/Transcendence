from django.urls import path
from apps.relations import views


urlpatterns = [
    path("friend-requests/", views.SendFriendRequestView.as_view()),
    path("friend-requests/received/", views.ReceivedFriendRequestListView.as_view()),
    path("friend-requests/sent/", views.SentFriendRequestListView.as_view()),
    path("friend-requests/<int:pk>/accept/", views.AcceptFriendRequestView.as_view()),
    path("friend-requests/<int:pk>/reject/", views.RejectFriendRequestView.as_view()),
    path("friend-requests/<int:pk>/", views.DeleteFriendRequestView.as_view()),
    path("friends/<int:pk>/remove/", views.RemoveFriendView.as_view()),
    path("blocklist/<int:pk>/add/", views.BlockUserView.as_view()),
    path("blocklist/<int:pk>/remove/", views.UnblockUserView.as_view()),
]
