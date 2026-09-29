"""Exakter Löser (Alpha-Beta + Transpositionstabelle, wortgleiche Portierung
aus transposition-table-demo) - dient hier NICHT als Live-Suche der App,
sondern als Grundwahrheit zum Erzeugen von Trainings-/Testdaten für die
Bewertungsfunktionen (kleine Bretter, wo die exakte Lösung noch schnell ist).
"""

from __future__ import annotations

import random

from ev_constants import PLAYER_ONE
from ev_game import apply_move, check_win_at, is_full, legal_columns, other_player, undo_move

_NEG_INF, _POS_INF = -2, 2
EXACT, LOWER, UPPER = "exact", "lower", "upper"

_MAX_ROWS = 8
_MAX_COLS = 8
_rng = random.Random(20260929)
_ZOBRIST = [[{1: _rng.getrandbits(64), 2: _rng.getrandbits(64)} for _ in range(_MAX_COLS)] for _ in range(_MAX_ROWS)]


def _board_hash(board) -> int:
    h = 0
    for r, row in enumerate(board):
        for c, value in enumerate(row):
            if value:
                h ^= _ZOBRIST[r][c][value]
    return h


def _toggle(h: int, r: int, c: int, player: int) -> int:
    return h ^ _ZOBRIST[r][c][player]


def _terminal_value(board, move, player) -> int | None:
    if check_win_at(board, move, player):
        return 1 if player == PLAYER_ONE else -1
    if is_full(board):
        return 0
    return None


def _recurse(board, player, alpha, beta, h, table) -> int:
    original_alpha = alpha
    key = (h, player)
    if key in table:
        value, flag = table[key]
        if flag == EXACT:
            return value
        if flag == LOWER:
            alpha = max(alpha, value)
        elif flag == UPPER:
            beta = min(beta, value)
        if alpha >= beta:
            return value

    best = None
    for col in legal_columns(board):
        move = apply_move(board, col, player)
        h2 = _toggle(h, move.row, move.column, player)
        terminal = _terminal_value(board, move, player)
        value = terminal if terminal is not None else _recurse(board, other_player(player), alpha, beta, h2, table)
        undo_move(board, move)
        if player == PLAYER_ONE:
            if best is None or value > best:
                best = value
            alpha = max(alpha, best)
        else:
            if best is None or value < best:
                best = value
            beta = min(beta, best)
        if alpha >= beta:
            break

    if best <= original_alpha:
        flag = UPPER
    elif best >= beta:
        flag = LOWER
    else:
        flag = EXACT
    table[key] = (best, flag)
    return best


def exact_value(board, player: int) -> int:
    """Exakter Spielwert der Stellung (aus Sicht Rot: +1/-1/0)."""
    table: dict = {}
    h = _board_hash(board)
    return _recurse(board, player, _NEG_INF, _POS_INF, h, table)
