from django.urls import path
from apps.relations import views


urlpatterns = [
    path("friend-requests/", views.SendFriendRequest.as_view()),
]
