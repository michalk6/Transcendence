# Authentication API

## Overview

This document describes authentication endpoints provided by the backend.

Authentication is based on JWT (JSON Web Token).

The API uses:

* Access Token — used to authenticate requests
* Refresh Token — used to obtain a new Access Token

---

# JWT Authorization

Protected endpoints require an access token.

The token must be sent in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Example:

```
GET /api/users/me/

Authorization: Bearer eyJhbGciOiJIUzI1Ni...
```

---

# Register

Creates a new user account and automatically authenticates the user.

## Endpoint

```
POST /api/auth/register/
```

## Request

Content-Type:

```
application/json
```

Body:

```json
{
    "username": "john",
    "email": "john@example.com",
    "password": "strong_password123"
}
```

## Fields

| Field    | Type   | Required | Description        |
| -------- | ------ | -------- | ------------------ |
| username | string | yes      | Unique username    |
| email    | string | yes      | User email address |
| password | string | yes      | User password      |

## Response

Status:

```
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

## Notes

After successful registration, the user is already authenticated and can use the returned access token.

---

# Login

Authenticates an existing user.

## Endpoint

```
POST /api/auth/login/
```

## Request

Content-Type:

```
application/json
```

Body:

```json
{
    "username": "john",
    "password": "strong_password123"
}
```

## Response

Status:

```
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

# Refresh Access Token

Generates a new access token using a valid refresh token.

## Endpoint

```
POST /api/auth/refresh/
```

## Request

Body:

```json
{
    "refresh": "eyJhbGciOiJIUzI1Ni..."
}
```

## Response

Status:

```
200 OK
```

Body:

```json
{
    "access": "eyJhbGciOiJIUzI1Ni..."
}
```

---

# Verify Token

Checks whether a token is valid.

## Endpoint

```
POST /api/auth/verify/
```

## Request

Body:

```json
{
    "token": "eyJhbGciOiJIUzI1Ni..."
}
```

## Response

Valid token:

Status:

```
200 OK
```

Invalid token:

Status:

```
401 Unauthorized
```

---

# Logout

Invalidates the refresh token.

## Endpoint

```
POST /api/auth/logout/
```

## Request

Body:

```json
{
    "refresh": "eyJhbGciOiJIUzI1Ni..."
}
```

## Response

Status:

```
200 OK
```

---

# Token Lifetime

Current configuration:

| Token         | Lifetime   |
| ------------- | ---------- |
| Access Token  | 15 minutes |
| Refresh Token | 7 days     |

Refresh tokens are rotated after usage.

Old refresh tokens are blacklisted after rotation.

---

# Error Responses

## Validation Error

Status:

```
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

---

## Invalid Credentials

Status:

```
401 Unauthorized
```

Example:

```json
{
    "detail": "No active account found with the given credentials"
}
```

---

## Missing Authentication

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
