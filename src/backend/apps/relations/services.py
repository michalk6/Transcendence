from django.contrib.auth import get_user_model
from django.db import transaction
from apps.relations.models import FriendRequest
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from apps.users.models import User
else:
    User = get_user_model()


@transaction.atomic
def accept_request(friend_request: FriendRequest) -> None:
    sender: User = friend_request.sender
    receiver: User = friend_request.receiver

    receiver.add_friend(sender)
    friend_request.delete()
