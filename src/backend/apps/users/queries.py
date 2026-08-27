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
    if not user.is_authenticated:
        return queryset
    user = cast(User, user)
    return queryset.annotate(
        friendship_status=Case(
            When(
                condition=Exists(user.friends.filter(pk=OuterRef("pk"))),
                then=Value(FriendshipStatus.FRIENDS),
            ),
            When(
                condition=Exists(user.blocklist.filter(pk=OuterRef("pk"))),
                then=Value(FriendshipStatus.BLOCKED),
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


def annotate_and_sort_by_friendship_status(
    queryset: QuerySet[User],
    user: User | AnonymousUser,
) -> QuerySet[User]:
    if not user.is_authenticated:
        return queryset
    user = cast(User, user)
    return annotate_friendship_status(queryset, user).annotate(
        friendship_order=Case(
            When(
                condition=Q(friendship_status=FriendshipStatus.FRIENDS),
                then=Value(0),
            ),
            When(
                condition=Q(friendship_status=FriendshipStatus.BLOCKED),
                then=Value(2),
            ),
            default=Value(1)
        ),
    ).order_by('friendship_order')


def annotate_mutual_friend_count(
    queryset: QuerySet[User],
    user: User | AnonymousUser,
) -> QuerySet[User]:
    if not user.is_authenticated:
        return queryset
    user = cast(User, user)
    return queryset.annotate(
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


def filter_mutual_friends(
    queryset: QuerySet[User],
    user: User | AnonymousUser,
) -> QuerySet[User]:
    if not user.is_authenticated:
        return queryset
    user = cast(User, user)
    return queryset.filter(
        pk__in=user.friends.all(),
    )


def filter_not_mutual_friends(
    queryset: QuerySet[User],
    user: User | AnonymousUser,
) -> QuerySet[User]:
    if not user.is_authenticated:
        return queryset
    user = cast(User, user)
    return queryset.exclude(pk=user.pk).exclude(
        pk__in=user.friends.all(),
    )


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
