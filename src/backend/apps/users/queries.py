from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet, Case, When, Exists, Value, OuterRef, Q, Count
from apps.users.models import User
from apps.users.enums import FriendshipStatus
from apps.relations.models import FriendRequest
from typing import cast


def annotate_friendship_status(
    queryset: QuerySet[User],
    user: User | AnonymousUser,
) -> QuerySet[User]:
    if user.is_authenticated:
        user = cast(User, user)
        queryset = queryset.annotate(
            friendship_status=Case(
                When(
                    condition=Exists(user.friends.filter(pk=OuterRef("pk"))),
                    then=Value(FriendshipStatus.FRIENDS),
                ),
                When(
                    condition=Exists(FriendRequest.objects.filter(sender=user, receiver=OuterRef("pk"))),
                    then=Value(FriendshipStatus.REQUEST_SENT),
                ),
                When(
                    condition=Exists(FriendRequest.objects.filter(sender=OuterRef("pk"), receiver=user)),
                    then=Value(FriendshipStatus.REQUEST_RECEIVED),
                ),
                When(
                    condition=Q(pk=user.pk),
                    then=Value(FriendshipStatus.SELF),
                ),
                default=Value(FriendshipStatus.NONE),
            )
        )

    return queryset


def annotate_mutual_friend_count(
    queryset: QuerySet[User],
    user: User | AnonymousUser,
):
    if user.is_authenticated:
        user = cast(User, user)
        queryset = queryset.annotate(
            mutual_friends=Case(
                When(
                    condition=Q(pk=user.pk),
                    then=Value(None),
                ),
                default=Count(
                    "friends",
                    filter=Q(friends__in=user.friends.all()),
                ),
            ),
        )
    return queryset


def filter_mutual_friends(
    queryset: QuerySet[User],
    user: User | AnonymousUser,
) -> QuerySet[User]:
    user = cast(User, user)
    queryset = queryset.filter(
        pk__in=user.friends.all(),
    )
    return queryset


def filter_not_mutual_friends(
    queryset: QuerySet[User],
    user: User | AnonymousUser,
) -> QuerySet[User]:
    user = cast(User, user)
    queryset = queryset.exclude(pk=user.pk).exclude(
        pk__in=user.friends.all(),
    )
    return queryset


def filter_users_by_naming_fields(
    queryset: QuerySet[User],
    search_term: str,
) -> QuerySet[User]:
    terms = search_term.split()
    result = queryset
    for term in terms:
        result = result & queryset.filter(
            Q(username__icontains=term)
            | Q(first_name__icontains=term)
            | Q(last_name__icontains=term)
        )
    return result
