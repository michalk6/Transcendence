# User API

## Get Current User

Returns information about the currently authenticated user.

This endpoint uses the user identified by the JWT access token.

---

## Endpoint

```http
GET /api/users/me/
```

## Authentication

This endpoint requires a valid access token.

Header:

```http
Authorization: Bearer <access_token>
```

Example:

```http
GET /api/users/me/
Authorization: Bearer eyJhbGciOiJIUzI1Ni...
```

---

## Request

No request body is required.

---

## Response

Status:

```http
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
|--------------|---------|------------------------|
| `id`         | integer | Unique user identifier |
| `username`   | string  | User's username        |
| `email`      | string  | User's email address   |
| `first_name` | string  | User's first name      |
| `last_name`  | string  | User's last name       |

---

## Errors

### Missing Authentication

Status:

```http
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

```http
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

---

# Update Current User

Updates the profile of the currently authenticated user.

Only the fields provided in the request body are updated.

---

## Endpoint

```http
PATCH /api/users/me/
```

## Authentication

This endpoint requires a valid access token.

Header:

```http
Authorization: Bearer <access_token>
```

Example:

```http
PATCH /api/users/me/
Authorization: Bearer eyJhbGciOiJIUzI1Ni...
```

---

## Request

Request body may contain one or more of the following fields:

| Field        | Type   | Required | Description              |
|--------------|--------|----------|--------------------------|
| `username`   | string | No       | New username             |
| `email`      | string | No       | New email address        |
| `first_name` | string | No       | New first name           |
| `last_name`  | string | No       | New last name            |

Example:

```json
{
    "first_name": "John",
    "last_name": "Smith"
}
```

---

## Response

Status:

```http
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

## Errors

### Missing Authentication

Status:

```http
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

```http
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

### Validation Error

Status:

```http
400 Bad Request
```

Example:

```json
{
    "email": [
        "Enter a valid email address."
    ]
}
```

Validation errors depend on the field being updated.

---

## Notes

This endpoint performs a partial update (`PATCH`).

Only the fields included in the request body are modified. All omitted fields remain unchanged.

The user is identified automatically from the JWT access token.