# User API

## Get Current User

Returns information about the currently authenticated user.

This endpoint uses the user identified by the JWT access token.

---

## Endpoint

```
GET /api/users/me/
```

## Authentication

This endpoint requires a valid access token.

Header:

```
Authorization: Bearer <access_token>
```

Example:

```
GET /api/users/me/

Authorization: Bearer eyJhbGciOiJIUzI1Ni...
```

---

## Request

No request body is required.

---

## Response

Status:

```
200 OK
```

Body:

```json
{
    "id": 1,
    "username": "john",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Smith"
}
```

---

## Response Fields

| Field        | Type    | Description            |
| ----------   | ------- | ---------------------- |
| `id`         | integer | Unique user identifier |
| `username`   | string  | User's username        |
| `email`      | string  | User's email address   |
| `first_name` | string  | User's first name      |
| `last_name`  | string  | User's last name       |

---

## Errors

### Missing Authentication

Status:

```
401 Unauthorized
```

Example:

```json
{
    "detail": "Authentication credentials were not provided."
}
```

---

### Invalid or Expired Token

Status:

```
401 Unauthorized
```

Example:

```json
{
    "detail": "Given token not valid for any token type",
    "code": "token_not_valid"
}
```

---

## Notes

The user returned by this endpoint is determined from the JWT access token.

The frontend should not send a user ID or username in the request. The backend identifies the user automatically based on the provided access token.
