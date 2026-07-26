from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()


def invalidate_all_refresh_tokens(user: User) -> None:
    tokens = (
        OutstandingToken
        .objects
        .filter(
            user=user,
            blacklistedtoken__isnull=True,
        )
    )

    for token in tokens:
        try:
            RefreshToken(token.token).blacklist()
        except TokenError:
            # Ignore tokens invalidated by another process (e.g. race condition).
            pass


def reset_refresh_tokens(user: User) -> RefreshToken:
    invalidate_all_refresh_tokens(user)
    return RefreshToken.for_user(user=user)
