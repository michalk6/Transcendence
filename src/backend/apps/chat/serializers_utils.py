from django.contrib.auth import get_user_model
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from apps.users.models import User
else:
    User = get_user_model()


def build_warnings(
    blocking: list[User], blocked_by: list[User],
) -> dict[str, Any]:
    warnings = {}
    w_blocking = [
        {"user_id": m.pk, "username": m.username}
        for m in blocking
    ]

    w_blocked_by = [
        {"user_id": m.pk, "username": m.username}
        for m in blocked_by
    ]

    if w_blocking:
        warnings["blocking"] = {
            "message": "Some users cannot be added because you have blocked them.",
            "users": w_blocking,
        }
    if w_blocked_by:
        warnings["blocked_by"] = {
            "message": "Some users cannot be added because they have blocked you.",
            "users": w_blocked_by,
        }
    return warnings
