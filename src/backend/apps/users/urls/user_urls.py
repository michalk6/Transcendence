from django.urls import path
from apps.users.views import user_views


urlpatterns = [
    path("me/", user_views.MeView.as_view())
]
