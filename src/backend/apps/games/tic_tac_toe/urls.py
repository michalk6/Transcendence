from django.urls import path
from apps.games.tic_tac_toe import views


urlpatterns = [
    path("matches/", views.MatchListCreateView.as_view()),
    path("ranking/", views.RankingListView.as_view()),
]
