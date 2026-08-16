from django.urls import path
from apps.users.views import user_views


urlpatterns = [
    path("me/", user_views.CurrentUserView.as_view()),
    path("me/password/", user_views.PasswordChangeView.as_view()),
    path("profile/<str:username>/", user_views.PublicUserView.as_view()),
    path("profile/<str:username>/friends/", user_views.FriendListView.as_view()),
    path("search/", user_views.SearchUserView.as_view()),
]
