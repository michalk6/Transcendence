from django.db import models
from django.db.models import F, Q
from django.contrib.auth import get_user_model
from typing import Self


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

    def get_reverse(self) -> Self | None:
        return type(self).objects.filter(
            sender=self.receiver,
            receiver=self.sender,
        ).first()

    @classmethod
    def already_exists(cls, sender: User, receiver: User) -> bool:
        return cls.objects.filter(
            sender=sender,
            receiver=receiver,
        ).exists()

    @classmethod
    def get_request(cls, sender: User, receiver: User) -> Self | None:
        return cls.objects.filter(
            sender=sender,
            receiver=receiver,
        ).first()
