from django.db import models
from django.db.models import F, Q
from django.contrib.auth import get_user_model


User = get_user_model()


class FriendRequest(models.Model):
    sender = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="sent_friend_requests",
    )
    receiver = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="received_friend_requests",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sender", "receiver"],
                name="unique_friend_request",
            ),
            models.CheckConstraint(
                condition=~Q(sender=F("receiver")),
                name="sender_not_receiver",
            ),
        ]

    @classmethod
    def already_exists(cls, sender: User, receiver: User) -> bool:
        return cls.objects.filter(
            sender=sender,
            receiver=receiver,
        ).exists()
