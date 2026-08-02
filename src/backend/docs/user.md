# User API

## Overview

This document describes user management endpoints provided by the backend.

These endpoints allow authenticated users to:
- retrieve their own profile information
- update their profile data
- change their password

All user endpoints operate on the currently authenticated user identified by the JWT access token.

The API does not require sending a user ID in requests. The backend determines the user automatically from the provided access token.

---

# Get Current User

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

The `id` field is read-only and cannot be modified.

The user is identified automatically from the JWT access token.

---

# Change Current User Password

Changes the password of the currently authenticated user.

The user must provide the current password and a new password.

The new password must pass Django password validation rules.

---

## Endpoint

```http
PATCH /api/users/me/password/
```

## Authentication

This endpoint requires a valid access token.

Header:

```http
Authorization: Bearer <access_token>
```

Example:

```http
PATCH /api/users/me/password/
Authorization: Bearer eyJhbGciOiJIUzI1Ni...
```

---

## Request

The request body must contain the following fields:

| Field              | Type   | Required | Description                      |
|--------------------|--------|----------|----------------------------------|
| `current_password` | string | Yes      | Current user password            |
| `new_password`     | string | Yes      | New password                     |
| `repeat_password`  | string | Yes      | Confirmation of new password     |

Example:

```json
{
    "current_password": "OldPassword123!",
    "new_password": "NewPassword123!",
    "repeat_password": "NewPassword123!"
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
    "message": "Password changed successfully",
    "refresh": "eyJhbGciOiJIUzI1Ni...",
    "access": "eyJhbGciOiJIUzI1Ni..."
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

### Incorrect Current Password

Status:

```http
400 Bad Request
```

Example:

```json
{
    "current_password": [
        "Current password is incorrect."
    ]
}
```

---

### Password Confirmation Does Not Match

Status:

```http
400 Bad Request
```

Example:

```json
{
    "password": [
        "password field didn't match"
    ]
}
```

---

### New Password Validation Error

Status:

```http
400 Bad Request
```

Example:

```json
{
    "new_password": [
        "This password is too short. It must contain at least 8 characters.",
        "This password is too common."
    ]
}
```

Validation rules are provided by Django's configured password validators.

---

## Notes

The endpoint does not require or accept a user ID.

The user is identified automatically from the JWT access token.

After changing the password, the user receives a new access and refresh token pair for the current session.

All previously issued refresh tokens are invalidated.

Previously issued access tokens remain valid until expiration.

# Get Public User Profile

Returns public information about a user.

This endpoint allows retrieving a user's public profile by username.

The endpoint does not require authentication.

---

## Endpoint

```http
GET /api/users/profile/<username>/
```

Example:

```http
GET /api/users/profile/john/
```

---

## Authentication

This endpoint is public and does not require an access token.

No `Authorization` header is required.

---

## Request

No request body is required.

The username is provided as a URL parameter.

---

## URL Parameters

| Parameter  | Type   | Required | Description                    |
| ---------- | ------ | -------- | ------------------------------ |
| `username` | string | Yes      | Username of the requested user |

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
    "first_name": "John",
    "last_name": "Smith"
}
```

---

## Response Fields

| Field        | Type    | Description            |
| ------------ | ------- | ---------------------- |
| `id`         | integer | Unique user identifier |
| `username`   | string  | User's username        |
| `first_name` | string  | User's first name      |
| `last_name`  | string  | User's last name       |

---

## Errors

### User Not Found

Status:

```http
404 Not Found
```

Example:

```json
{
    "detail": "No User matches the given query."
}
```

---

## Notes

This endpoint returns only public user information.

Private data such as email address and authentication-related information are not included in the response.

The user is identified by the `username` parameter provided in the URL.

The endpoint is intended for displaying public user profiles.
