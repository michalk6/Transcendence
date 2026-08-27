from __future__ import annotations
from django.db import models
from django.contrib.auth.models import AbstractUser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.fields.related_descriptors import RelatedManager
    from apps.relations.models import FriendRequest


class User(AbstractUser):
    email = models.EmailField(unique=True)

    friends = models.ManyToManyField(
        to="self",
        symmetrical=True,
        blank=True,
    )
    blocklist = models.ManyToManyField(
        to="self",
        symmetrical=False,
        blank=True,
    )

    if TYPE_CHECKING:
        sent_friend_requests: RelatedManager[FriendRequest]
        received_friend_requests: RelatedManager[FriendRequest]

    def is_friend(self, other: User) -> bool:
        return self.friends.contains(other)

    def is_blocking(self, other: User) -> bool:
        return self.blocklist.contains(other)

    def is_blocked_by(self, other: User) -> bool:
        return other.is_blocking(self)

    def add_friend(self, other: User) -> None:
        if self.pk == other.pk:
            return
        self.unblock_user(other)
        other.unblock_user(self)
        self.friends.add(other)

    def remove_friend(self, other: User) -> None:
        self.friends.remove(other)

    def block_user(self, other: User) -> None:
        if self.pk == other.pk:
            return
        self.remove_friend(other)
        self.blocklist.add(other)

    def unblock_user(self, other: User) -> None:
        self.blocklist.remove(other)

    def __str__(self):
        return self.username
