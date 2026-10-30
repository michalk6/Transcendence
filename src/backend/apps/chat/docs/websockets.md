# WebSocket API

WebSocket is used for chat messages and user online status.

## Private Chat

### Connection

```text
ws://localhost:8000/ws/chat/
```

The user must be logged in. Authentication uses JWT tokens stored in cookies.
If the user is not authenticated, the connection is rejected (code `4401`).

The client sends JSON messages with an `action` field. Messages from the backend use a `type` field.

### Get online users

Send:

```json
{
  "action": "get_online_users"
}
```

Response:

```json
{
  "type": "online_users",
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

### Send a message

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
  "type": "message_created",
  "message": {
    "id": "message-uuid",
    "sender": 536,
    "content": "Hello!",
    "chat_room": "room-uuid",
    "created_at": "2026-10-23T18:00:00+00:00"
  }
}
```

### Online and offline status

When a user connects, the backend sends an online status update. When the user's last connection closes, it sends an offline status update.

```json
{
  "type": "user_status",
  "user_id": 536,
  "status": "online"
}
```

The status can be `online` or `offline`.

Only the user ID is sent. If the frontend needs more user data, it can get the profile from the REST API.

A user can have more than one connection. The `offline` status is sent only when the user has no connections left.

### Errors

For an unknown action or invalid data, the backend can send:

```json
{
  "type": "error",
  "detail": "Unknown action."
}
```

Other errors include `Invalid JSON format.` and `Message must be a JSON object.`. Message validation errors are also returned with `type: "error"`.

### Presence

Redis stores active WebSocket connections for each user. A heartbeat refreshes the user's presence every 20 seconds. The Redis key expires after 60 seconds without a refresh.

If the server crashes, the user may still appear online for a short time. Expiring the Redis key does not automatically send an `offline` event.

### Other chat operations

Chat rooms, message history, and message editing or deleting use the REST API. These endpoints are documented in Swagger.

## General Chat

### Connection

General chat uses a separate WebSocket connection:

```text
ws://localhost:8000/ws/chat/general/
```

The user must be logged in. Authentication uses JWT cookies. Unauthenticated connections are rejected with code `4401`.

### Message history

After connecting, the backend automatically sends the last 100 messages stored in Redis.

```json
{
  "type": "general_message_list",
  "message_list": [
    {
      "sender": {
        "id": 536,
        "username": "alice"
      },
      "content": "Hello!",
      "created_at": "2026-10-30T20:00:00+00:00"
    }
  ]
}
```

### Send a message

Send:

```json
{
  "action": "send_message",
  "content": "Hello everyone!"
}
```

The backend adds the sender and creation time, saves the message in Redis, and sends it to all users connected to general chat.

Received message:

```json
{
  "type": "general_message",
  "message": {
    "sender": {
      "id": 536,
      "username": "alice"
    },
    "content": "Hello everyone!",
    "created_at": "2026-10-30T20:00:00+00:00"
  }
}
```

Messages cannot be empty or longer than 2000 characters.

### Errors

For invalid message content or an unknown action, the backend sends:

```json
{
  "type": "error",
  "detail": "Invalid message content."
}
```

Other errors include `Invalid JSON format.` and `Unknown action.`

### Message storage

General chat messages are stored only in Redis. Only the last 100 messages are kept. Older messages are removed automatically.

General chat messages are not stored in the database.