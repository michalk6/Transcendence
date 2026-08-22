from enum import StrEnum


class FriendshipStatus(StrEnum):
    FRIENDS = "friends"
    REQUEST_SENT = "request_sent"
    REQUEST_RECEIVED = "request_received"
    NONE = "none"
    SELF = "self"
