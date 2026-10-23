# WebSocket API

WebSocket is used for chat messages and user online status.

## Connection

```text
ws://localhost:8000/ws/chat/
```

The user must be logged in. Authentication uses JWT tokens stored in cookies.
If the user is not authenticated, the connection is rejected (code `4401`).

After connecting, the client can send JSON messages with an `action` field.

## Get online users

Send:

```json
{
  "action": "get_online_users"
}
```

Response:

```json
{
  "online_users": [
    {
      "id": 536,
      "username": "alice",
      "first_name": "Alice",
      "last_name": "Smith",
      "friendship_status": "friends",
      "mutual_friends": null
    }
  ]
}
```

The list contains online users. Friendship status is calculated for the logged-in user. Friends are listed first, blocked users last.

## Send a message

Send:

```json
{
  "action": "send_message",
  "message": {
    "chat_room": "room-uuid",
    "content": "Hello!"
  }
}
```

The backend validates and saves the message. It then sends the saved message to all members of the chat room.

Received message:

```json
{
  "id": "message-uuid",
  "sender": 536,
  "content": "Hello!",
  "chat_room": "room-uuid",
  "created_at": "2026-10-23T18:00:00+00:00"
}
```

## Online and offline status

When a user connects or disconnects, the backend sends a status update:

```json
{
  "user_id": 536,
  "status": "online"
}
```

The status can be `online` or `offline`.

Only the user ID is sent. If the frontend needs more user data, it can get the profile from the REST API.

A user can have more than one connection. The `offline` status is sent only when the user has no connections left.

## Errors

For an unknown action or invalid data, the backend can send:

```json
{
  "action": "error",
  "detail": "Unknown action."
}
```

Other errors include `Invalid JSON format.` and `Message must be a JSON object.`. Message validation errors are also returned with `action: "error"`.

## Presence

Redis stores active WebSocket connections for each user. A heartbeat refreshes the user's presence every 20 seconds. The Redis key expires after 60 seconds without a refresh.

If the server crashes, the user may still appear online for a short time. Expiring the Redis key does not automatically send an `offline` event.

## Other chat operations

Chat rooms, message history, and message editing or deleting use the REST API. These endpoints are documented in Swagger.
