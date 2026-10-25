from django.urls import path, include

urlpatterns = [
    path('tic_tac_toe_ultimate/', include('apps.games.tic_tac_toe.urls')),
]
