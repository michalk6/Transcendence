from rest_framework.response import Response
from django.conf import settings


def get_cookie_options(**additional) -> dict:
    return {
        "path": settings.SIMPLE_JWT.get("AUTH_COOKIE_PATH", "/"),
        "domain": settings.SIMPLE_JWT.get("AUTH_COOKIE_DOMAIN", None),
        "samesite": settings.SIMPLE_JWT.get("AUTH_COOKIE_SAMESITE", "Lax"),
        **additional,
    }


def set_auth_cookies(response: Response) -> Response:
    if response.status_code not in (200, 201) or not isinstance(response.data, dict):
        return response

    cookie_options = get_cookie_options(
        secure = settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", True),
        httponly = settings.SIMPLE_JWT.get("AUTH_COOKIE_HTTP_ONLY", True),
    )

    access_token = response.data.pop("access", None)
    refresh_token = response.data.pop("refresh", None)

    if access_token:
        response.set_cookie(
            key=settings.SIMPLE_JWT.get("AUTH_COOKIE", "access_token"),
            value=access_token,
            max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
            **cookie_options,
        )

    if refresh_token:
        response.set_cookie(
            key=settings.SIMPLE_JWT.get("AUTH_COOKIE_REFRESH", "refresh_token"),
            value=refresh_token,
            max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
            **cookie_options,
        )

    return response


def delete_auth_cookies(response: Response) -> Response:
    cookie_options = get_cookie_options()

    response.delete_cookie(
        key=settings.SIMPLE_JWT.get("AUTH_COOKIE", "access_token"),
        **cookie_options,
    )

    response.delete_cookie(
        key=settings.SIMPLE_JWT.get("AUTH_COOKIE_REFRESH", "refresh_token"),
        **cookie_options,
    )

    return response
