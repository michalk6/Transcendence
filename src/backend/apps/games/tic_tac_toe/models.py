from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Match(models.Model):
    class GameStatus(models.TextChoices):
        FINISHED = "finished", "Finished"
        IN_PROGRESS = "in_progress", "In progress"
        WAITING = "waiting", "Waiting for opponent"

    player_x = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="games_as_x",
    )
    player_o = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="games_as_o",
    )
    winner = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="games_won",
    )
    status = models.CharField(
        max_length=20,
        choices=GameStatus,
        default=GameStatus.WAITING,
    )
