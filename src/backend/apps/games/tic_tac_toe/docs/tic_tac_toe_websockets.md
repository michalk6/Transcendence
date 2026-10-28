# Ultimate Tic Tac Toe WebSocket API

WebSockets are used to play Ultimate Tic Tac Toe, watch matches, and receive lobby updates.

Anyone can connect to the game and lobby WebSockets. Login is required to join a match, make moves, or forfeit.

## Connections

### Game

```text
ws://localhost:8000/ws/games/tictactoe/<match_id>/
```

Replace `<match_id>` with the match ID.

The connection is available for matches with status `waiting` or `in_progress`.

After connecting, the server sends the current game state. Anyone connected to the match receives game updates, including spectators.

The server accepts the connection first, then checks the match:

- `4404` — the match does not exist or is not available (`finished` or `aborted`).
- `4500` — the match exists but its game state is missing from Redis. The match is marked as `aborted`.

### Lobby

```text
ws://localhost:8000/ws/games/tictactoe/lobby/
```

The lobby WebSocket is public. It sends a notification when the match list changes.

## Message format

Client messages use an `action` field. Server messages use a `type` field.

All messages are JSON.

## Game messages

### Initial game state

Sent by the server after connecting to an available match.

```json
{
  "type": "game_state",
  "board_state": {
    "board": [
      {"cells": [null, null, null, null, null, null, null, null, null], "winner": null},
      {"cells": [null, null, null, null, null, null, null, null, null], "winner": null},
      {"cells": [null, null, null, null, null, null, null, null, null], "winner": null},
      {"cells": [null, null, null, null, null, null, null, null, null], "winner": null},
      {"cells": [null, null, null, null, null, null, null, null, null], "winner": null},
      {"cells": [null, null, null, null, null, null, null, null, null], "winner": null},
      {"cells": [null, null, null, null, null, null, null, null, null], "winner": null},
      {"cells": [null, null, null, null, null, null, null, null, null], "winner": null},
      {"cells": [null, null, null, null, null, null, null, null, null], "winner": null}
    ],
    "current_player": "X",
    "next_board": null,
    "winner": null
  }
}
```

`board_state` fields:

| Field | Description |
| --- | --- |
| `board` | Array of 9 small boards. |
| `board[i].cells` | Array of 9 cells: `"X"`, `"O"`, or `null`. |
| `board[i].winner` | `"X"`, `"O"`, `"draw"`, or `null`. |
| `current_player` | Player whose turn is next: `"X"` or `"O"`. |
| `next_board` | Index of the required small board (`0`–`8`), or `null` if the player can choose an available board. |
| `winner` | Overall game result: `"X"`, `"O"`, `"draw"`, or `null`. |

Board and cell indices start at `0` and end at `8`.

### Join a match

Only a logged-in user can join. The match must be waiting for a second player. The creator cannot join their own match as the second player.

Send:

```json
{
  "action": "join"
}
```

When joining succeeds, everyone connected to the match receives:

```json
{
  "type": "player_joined",
  "user_id": 536
}
```

The lobby also receives `matches_updated`.

If joining is not possible, the sender receives:

```json
{
  "type": "error",
  "detail": "Cannot join this match."
}
```

### Make a move

Only a logged-in player in an `in_progress` match can make a move. The game checks the player's turn, board, and cell.

Send:

```json
{
  "action": "make_move",
  "next_board": 0,
  "next_cell": 4
}
```

Both values must be integers from `0` to `8`. `next_board` is the small board to play on; `next_cell` is the cell inside that board.

When the move succeeds, everyone connected to the match receives:

```json
{
  "type": "move_result",
  "detail": "next_O",
  "board_state": {
    "board": [
      {"cells": [null, null, null, null, "X", null, null, null, null], "winner": null},
      {"cells": [null, null, null, null, null, null, null, null, null], "winner": null},
      {"cells": [null, null, null, null, null, null, null, null, null], "winner": null},
      {"cells": [null, null, null, null, null, null, null, null, null], "winner": null},
      {"cells": [null, null, null, null, null, null, null, null, null], "winner": null},
      {"cells": [null, null, null, null, null, null, null, null, null], "winner": null},
      {"cells": [null, null, null, null, null, null, null, null, null], "winner": null},
      {"cells": [null, null, null, null, null, null, null, null, null], "winner": null},
      {"cells": [null, null, null, null, null, null, null, null, null], "winner": null}
    ],
    "current_player": "O",
    "next_board": 4,
    "winner": null
  }
}
```

Possible `detail` values:

| Value | Meaning |
| --- | --- |
| `next_X` | Move accepted; X plays next. |
| `next_O` | Move accepted; O plays next. |
| `winner_X` | X won the game. |
| `winner_O` | O won the game. |
| `draw` | The game ended in a draw. |

The `board_state` always contains the updated game state. When the game ends, the server sends this final message and closes the game WebSocket with code `1000`.

Invalid moves return an error to the sender, for example:

```json
{
  "type": "error",
  "detail": "Invalid Move Not this player turn"
}
```

If the server cannot acquire the move lock, it sends:

```json
{
  "type": "error",
  "detail": "Could not process move. Try again."
}
```

### Forfeit a match

A logged-in player can give up an `in_progress` match. The other player wins.

Send:

```json
{
  "action": "forfeit"
}
```

Everyone connected to the match receives:

```json
{
  "type": "user_forfeit",
  "user_id": 536
}
```

`user_id` is the ID of the player who forfeited.

After this message, the server closes all game WebSocket connections with code `1000`.

If the server cannot acquire the lock, the sender receives:

```json
{
  "type": "error",
  "detail": "Could not forfeit match. Try again."
}
```

### Other errors

Unknown action:

```json
{
  "type": "error",
  "detail": "Unknown action."
}
```

Invalid JSON structure (for example, a JSON array instead of an object):

```json
{
  "type": "error",
  "detail": "Invalid JSON format."
}
```

Some invalid or unauthorized actions are ignored without an error response. For example, `make_move` with non-integer indices is ignored, and anonymous users cannot join, move, or forfeit.

If game state is missing during a move, the match is marked as `aborted` and the sender receives an error.

## Lobby messages

The lobby WebSocket does not require any client actions.

When a match is created, a player joins, or a match finishes, the server sends:

```json
{
  "type": "matches_updated"
}
```

This notification does not contain the match list. The frontend should request the updated list using the REST API:

```text
GET /api/games/tic_tac_toe_ultimate/matches/
```

This GET endpoint is public. Creating a match with POST requires login.

## Match lifecycle

| Status | Meaning |
| --- | --- |
| `waiting` | Match created, waiting for another player. |
| `in_progress` | Both players joined and can play. |
| `finished` | Match ended by a win, draw, or forfeit. |
| `aborted` | Active match lost its game state. |

The board is stored in Redis while the match is active. After a win, draw, or forfeit, the result is saved in the database and the board is deleted from Redis. Finished and aborted matches cannot be opened again through the game WebSocket.

## Notes

- All users connected to the same match, including spectators, receive `player_joined`, `move_result`, and `user_forfeit`.
- A normal WebSocket disconnect does not forfeit the match. A player must explicitly send `{"action": "forfeit"}`.
- The game WebSocket sends a full board state on connect and after every successful move.
- The lobby only sends change notifications. It does not send full match data.
