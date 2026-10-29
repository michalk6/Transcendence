from django.apps import AppConfig


class TicTacToeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.games.tic_tac_toe'
    label = 'tic_tac_toe'
