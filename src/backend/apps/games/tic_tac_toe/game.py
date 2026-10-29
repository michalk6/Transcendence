from typing import Self


class InvalidMove(Exception):
    pass


class InnerBoard:
    def __init__(self) -> None:
        self.cells: list[str | None] = [None] * 9
        self.winner: str | None = None

    def make_move(self, sign: str, target: int) -> str | None:
        if self.winner is not None:
            raise InvalidMove("Board is already finished")
        if sign not in ("X", "O"):
            raise InvalidMove("Incorrect sign")
        if target < 0 or 8 < target:
            raise InvalidMove("Cell index out of range")
        if self.cells[target] is not None:
            raise InvalidMove("Cell is not empty")
        self.cells[target] = sign
        return self.check_winner()

    def check_rows(self) -> str | None:
        if self.cells[0] == self.cells[1] == self.cells[2] is not None:
            return self.cells[0]
        if self.cells[3] == self.cells[4] == self.cells[5] is not None:
            return self.cells[3]
        if self.cells[6] == self.cells[7] == self.cells[8] is not None:
            return self.cells[6]

    def check_columns(self) -> str | None:
        if self.cells[0] == self.cells[3] == self.cells[6] is not None:
            return self.cells[0]
        if self.cells[1] == self.cells[4] == self.cells[7] is not None:
            return self.cells[1]
        if self.cells[2] == self.cells[5] == self.cells[8] is not None:
            return self.cells[2]

    def check_diagonals(self) -> str | None:
        if self.cells[0] == self.cells[4] == self.cells[8] is not None:
            return self.cells[0]
        if self.cells[2] == self.cells[4] == self.cells[6] is not None:
            return self.cells[2]

    def is_board_full(self) -> bool:
        for cell in self.cells:
            if cell is None:
                return False
        return True

    def check_winner(self) -> str | None:
        if self.winner is not None:
            return self.winner
        self.winner = (
            self.check_rows() or self.check_columns() or self.check_diagonals()
        )
        if self.winner is None and self.is_board_full():
            self.winner = "draw"
        return self.winner

    def to_dict(self) -> dict:
        return {
            "cells": self.cells,
            "winner": self.winner,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        inner_board = cls()
        inner_board.cells = data["cells"]
        inner_board.winner = data["winner"]
        return inner_board


class Game:
    def __init__(self) -> None:
        self.board: list[InnerBoard] = [InnerBoard() for _ in range(9)]
        self.current_player: str = "X"
        self.next_board: int | None = None
        self.winner: str | None = None

    def switch_turn(self) -> None:
        self.current_player = "X" if self.current_player == "O" else "O"

    def make_move(self, sign: str, target_board: int, target_cell: int) -> str | None:
        if self.winner is not None:
            raise InvalidMove("Game is already finished")
        if self.next_board is not None and self.next_board != target_board:
            raise InvalidMove("Target board must be selected according to opponent's previous move")
        if target_board < 0 or 8 < target_board:
            raise InvalidMove("Board index out of range")
        if sign != self.current_player:
            raise InvalidMove("Not your turn")

        self.board[target_board].make_move(sign, target_cell)
        self.switch_turn()
        self.next_board = target_cell if self.board[target_cell].winner is None else None
        winner = self.check_winner()
        if winner is None:
            return f"next_{self.current_player}"
        if winner == "draw":
            return winner
        return f"winner_{winner}"

    def check_rows(self) -> str | None:
        if self.board[0].winner == self.board[1].winner == self.board[2].winner \
                and self.board[0].winner in ("X", "O"):
            return self.board[0].winner
        if self.board[3].winner == self.board[4].winner == self.board[5].winner \
                and self.board[3].winner in ("X", "O"):
            return self.board[3].winner
        if self.board[6].winner == self.board[7].winner == self.board[8].winner \
                and self.board[6].winner in ("X", "O"):
            return self.board[6].winner

    def check_columns(self) -> str | None:
        if self.board[0].winner == self.board[3].winner == self.board[6].winner \
                and self.board[0].winner in ("X", "O"):
            return self.board[0].winner
        if self.board[1].winner == self.board[4].winner == self.board[7].winner \
                and self.board[1].winner in ("X", "O"):
            return self.board[1].winner
        if self.board[2].winner == self.board[5].winner == self.board[8].winner \
                and self.board[2].winner in ("X", "O"):
            return self.board[2].winner

    def check_diagonals(self) -> str | None:
        if self.board[0].winner == self.board[4].winner == self.board[8].winner \
                and self.board[0].winner in ("X", "O"):
            return self.board[0].winner
        if self.board[2].winner == self.board[4].winner == self.board[6].winner \
                and self.board[2].winner in ("X", "O"):
            return self.board[2].winner

    def is_board_full(self) -> bool:
        for cell in self.board:
            if cell.winner is None:
                return False
        return True

    def check_winner(self) -> str | None:
        if self.winner is not None:
            return self.winner
        self.winner = (
            self.check_rows() or self.check_columns() or self.check_diagonals()
        )
        if self.winner is None and self.is_board_full():
            self.winner = "draw"
        return self.winner

    def to_dict(self) -> dict:
        return {
            "board": [inner.to_dict() for inner in self.board],
            "current_player": self.current_player,
            "next_board": self.next_board,
            "winner": self.winner,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        game = cls()
        game.board = [InnerBoard.from_dict(inner) for inner in data["board"]]
        game.current_player = data["current_player"]
        game.next_board = data["next_board"]
        game.winner = data["winner"]
        return game
