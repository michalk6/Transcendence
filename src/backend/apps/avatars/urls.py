from django.urls import path
from apps.avatars import views


urlpatterns = [
    path("me/", views.MyAvatarView.as_view()),
    path("<str:username>/", views.AvatarDetailView.as_view()),
]
