from django.db import models
from django.contrib.auth import get_user_model
import uuid
from typing import TYPE_CHECKING

User = get_user_model()

if TYPE_CHECKING:
    from django.db.models.fields.related_descriptors import RelatedManager


class ChatRoom(models.Model):
    class RoomType(models.TextChoices):
        PRIVATE = "PRIVATE", "Private"
        GROUP = "GROUP", "Group"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    room_type = models.CharField(
        max_length=20,
        choices=RoomType,
        default=RoomType.PRIVATE,
    )
    members = models.ManyToManyField(
        to=User,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    if TYPE_CHECKING:
        messages: RelatedManager["Message"]

    class Meta:
        default_related_name = "chat_rooms"
        ordering = ["-last_message_at"]

    def __str__(self):
        return self.name or str(self.id)


class Message(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    sender = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
    )
    content = models.TextField()
    chat_room = models.ForeignKey(
        to=ChatRoom,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        default_related_name = "messages"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.sender}: {self.content[:20]}"
