# Authentication API

## Overview

This document describes authentication endpoints provided by the backend.

Authentication is based on JWT (JSON Web Token).

The API uses:

* Access Token — used to authenticate requests
* Refresh Token — used to obtain a new Access Token

All authentication endpoints are available under:

```http
/api/auth/
```

---

## JWT Authorization

Protected endpoints require an access token.

The token must be sent in the `Authorization` header:

```http
Authorization: Bearer <access_token>
```

Example:

```http
GET /api/users/me/
Authorization: Bearer eyJhbGciOiJIUzI1Ni...
```

---

# Register

Creates a new user account and automatically authenticates the user.

---

## Endpoint

```http
POST /api/auth/register/
```

---

## Request

Content-Type:

```http
Content-Type: application/json
```

Body:

```json
{
    "username": "john",
    "email": "john@example.com",
    "password": "strong_password123",
    "repeat_password": "strong_password123"
}
```

---

## Fields

| Field             | Type   | Required | Description                                   |
| ----------------- | ------ | -------- | --------------------------------------------- |
| `username`        | string | yes      | Unique username                               |
| `email`           | string | yes      | User email address                            |
| `password`        | string | yes      | User password                                 |
| `repeat_password` | string | yes      | Password confirmation                         |

---

## Response

Status:

```http
201 Created
```

Body:

```json
{
    "user": {
        "id": 1,
        "username": "john",
        "email": "john@example.com"
    },
    "refresh": "eyJhbGciOiJIUzI1Ni...",
    "access": "eyJhbGciOiJIUzI1Ni..."
}
```

---

## Errors

### Validation Error

Status:

```http
400 Bad Request
```

Example:

```json
{
    "username": [
        "A user with that username already exists."
    ]
}
```

Validation errors depend on the provided data.

---

## Notes

The user is automatically authenticated after successful registration.

Both `password` and `repeat_password` fields are write-only and are not returned in the response.

---

# Login

Authenticates an existing user.

---

## Endpoint

```http
POST /api/auth/login/
```

---

## Request

Content-Type:

```http
Content-Type: application/json
```

Body:

```json
{
    "username": "john",
    "password": "strong_password123"
}
```

The `username` field accepts:

- user's username
- user's email address

Email addresses are matched case-sensitively.

Examples:

Login using username:

```json
{
    "username": "john",
    "password": "strong_password123"
}
```

Login using email:

```json
{
    "username": "john@example.com",
    "password": "strong_password123"
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
    "refresh": "eyJhbGciOiJIUzI1Ni...",
    "access": "eyJhbGciOiJIUzI1Ni..."
}
```

---

## Errors

### Invalid Credentials

Status:

```http
401 Unauthorized
```

Example:

```json
{
    "detail": "No active account found with the given credentials"
}
```

---

## Notes

The returned access token should be used to authenticate protected endpoints.

---

# Refresh Access Token

Generates a new access token using a valid refresh token.

---

## Endpoint

```http
POST /api/auth/refresh/
```

---

## Request

Body:

```json
{
    "refresh": "eyJhbGciOiJIUzI1Ni..."
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
    "access": "eyJhbGciOiJIUzI1Ni...",
    "refresh": "eyJhbGciOiJIUzI1Ni..."
}
```

---

## Errors

### Invalid or Expired Refresh Token

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

# Verify Token

Checks whether a token is valid.

This endpoint does not require authentication.

---

## Endpoint

```http
POST /api/auth/verify/
```

---

## Request

Body:

```json
{
    "token": "eyJhbGciOiJIUzI1Ni..."
}
```

---

## Response

Valid token:

```http
200 OK
```

---

## Errors

### Invalid Token

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

# Logout

Invalidates a refresh token.

---

## Endpoint

```http
POST /api/auth/logout/
```

---

## Request

Body:

```json
{
    "refresh": "eyJhbGciOiJIUzI1Ni..."
}
```

---

## Response

Status:

```http
200 OK
```

---

## Errors

### Invalid or Blacklisted Refresh Token

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

Only the provided refresh token is invalidated.

Other active sessions remain unaffected.

---

# Logout All Sessions

Logs out the currently authenticated user from all active sessions.

This endpoint invalidates all refresh tokens issued for the user.

Previously issued access tokens remain valid until expiration.

The user is identified automatically from the JWT access token.

---

## Endpoint

```http
POST /api/auth/logout-all/
```

---

## Authentication

This endpoint requires a valid access token.

Header:

```http
Authorization: Bearer <access_token>
```

Example:

```http
POST /api/auth/logout-all/
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
    "message": "Logged out from all sessions successfully"
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

## Notes

After successful execution:

- all refresh tokens associated with the user become unusable,
- previously issued access tokens remain valid until expiration,
- the user must authenticate again to obtain a new token pair.

This endpoint affects all active sessions of the user, including sessions on other devices.

---

# Token Lifetime

Current configuration:

| Token         | Lifetime   |
| ------------- | ---------- |
| Access Token  | 15 minutes |
| Refresh Token | 7 days     |

Refresh tokens are rotated after usage.

Old refresh tokens are blacklisted after rotation.