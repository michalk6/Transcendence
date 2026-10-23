from django.urls import path
from apps.users.views import auth_views


urlpatterns = [
    path('register/', auth_views.RegisterView.as_view(), name='register'),
    path('login/', auth_views.CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', auth_views.CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', auth_views.CookieTokenBlacklistView.as_view(), name='token_blacklist'),
    path('logout-all/', auth_views.LogoutAllView.as_view(), name='logout_all_sessions'),
]
