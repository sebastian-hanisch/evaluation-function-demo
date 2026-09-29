"""Mini-Vier-Gewinnt: Brettmechanik (Fallen lassen, Sieg-/Remis-Prüfung).

Wortgleiche Kopie von `tt_game.py`/`ab_game.py`/`mm_game.py` (Vorgänger dieser
Linie) - dasselbe Vehikel, nicht neu erfunden.
"""

from __future__ import annotations

from dataclasses import dataclass

from ev_constants import EMPTY, PLAYER_ONE, PLAYER_TWO, WIN_LENGTH

_DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))


@dataclass(frozen=True)
class Move:
    column: int
    row: int


def empty_board(rows: int, cols: int) -> list[list[int]]:
    return [[EMPTY] * cols for _ in range(rows)]


def other_player(player: int) -> int:
    return PLAYER_TWO if player == PLAYER_ONE else PLAYER_ONE


def legal_columns(board: list[list[int]]) -> list[int]:
    return [c for c in range(len(board[0])) if board[0][c] == EMPTY]


def is_full(board: list[list[int]]) -> bool:
    return len(legal_columns(board)) == 0


def apply_move(board: list[list[int]], col: int, player: int) -> Move:
    rows = len(board)
    for row in range(rows - 1, -1, -1):
        if board[row][col] == EMPTY:
            board[row][col] = player
            return Move(column=col, row=row)
    raise ValueError(f"Spalte {col} ist voll")


def undo_move(board: list[list[int]], move: Move) -> None:
    board[move.row][move.column] = EMPTY


def check_win_at(board: list[list[int]], move: Move, player: int) -> bool:
    rows, cols = len(board), len(board[0])
    for dr, dc in _DIRECTIONS:
        count = 1
        r, c = move.row + dr, move.column + dc
        while 0 <= r < rows and 0 <= c < cols and board[r][c] == player:
            count += 1
            r += dr
            c += dc
        r, c = move.row - dr, move.column - dc
        while 0 <= r < rows and 0 <= c < cols and board[r][c] == player:
            count += 1
            r -= dr
            c -= dc
        if count >= WIN_LENGTH:
            return True
    return False


@dataclass(frozen=True)
class Replay:
    board: list[list[int]]
    player_to_move: int
    last_move: Move | None
    winner: int | None
    is_terminal: bool


def replay(rows: int, cols: int, moves: list[int]) -> Replay:
    board = empty_board(rows, cols)
    player = PLAYER_ONE
    last_move: Move | None = None
    winner: int | None = None
    is_terminal = False
    for col in moves:
        if is_terminal or not (0 <= col < cols) or board[0][col] != EMPTY:
            break
        last_move = apply_move(board, col, player)
        if check_win_at(board, last_move, player):
            winner = player
            is_terminal = True
        elif is_full(board):
            is_terminal = True
        else:
            player = other_player(player)
    return Replay(board=board, player_to_move=player, last_move=last_move, winner=winner, is_terminal=is_terminal)


def winning_line(board: list[list[int]], move: Move, player: int) -> list[tuple[int, int]] | None:
    rows, cols = len(board), len(board[0])
    for dr, dc in _DIRECTIONS:
        cells = [(move.row, move.column)]
        r, c = move.row + dr, move.column + dc
        while 0 <= r < rows and 0 <= c < cols and board[r][c] == player:
            cells.append((r, c))
            r += dr
            c += dc
        r, c = move.row - dr, move.column - dc
        while 0 <= r < rows and 0 <= c < cols and board[r][c] == player:
            cells.append((r, c))
            r -= dr
            c -= dc
        if len(cells) >= WIN_LENGTH:
            return cells
    return None


def all_windows(rows: int, cols: int) -> list[list[tuple[int, int]]]:
    """Alle Länge-4-Fenster (horizontal, vertikal, beide Diagonalen)."""
    windows = []
    for r in range(rows):
        for c in range(cols):
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                cells = [(r + i * dr, c + i * dc) for i in range(WIN_LENGTH)]
                if all(0 <= rr < rows and 0 <= cc < cols for rr, cc in cells):
                    windows.append(cells)
    return windows
