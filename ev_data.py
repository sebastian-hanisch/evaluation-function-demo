"""Trainings-/Testdaten für die Bewertungsfunktionen: zufällige Partien auf
einem kleinen, vollständig lösbaren Brett, jede besuchte Stellung mit ihrem
exakten Spielwert (aus ev_exact) - die Grundwahrheit, an der beide
Bewertungen (Hand+Fit) gemessen werden.
"""

from __future__ import annotations

import random

from ev_constants import PLAYER_ONE
from ev_exact import exact_value
from ev_game import apply_move, check_win_at, empty_board, is_full, legal_columns, other_player


def generate_dataset(rows: int, cols: int, n_games: int, seed: int) -> list[tuple[tuple, int, int]]:
    """Gibt eine Liste (board_key, player_to_move, exact_value) zurück, ohne
    Duplikate (dieselbe Stellung kann über verschiedene Partien mehrfach
    erreicht werden - dann nur einmal gezählt, wie ein Trainingsdatensatz es
    verlangt)."""
    rng = random.Random(seed)
    seen: dict[tuple, tuple[tuple, int, int]] = {}
    for _ in range(n_games):
        board = empty_board(rows, cols)
        player = PLAYER_ONE
        while True:
            cols_left = legal_columns(board)
            if not cols_left:
                break
            key = (tuple(tuple(row) for row in board), player)
            if key not in seen:
                value = exact_value([row[:] for row in board], player)
                seen[key] = (key[0], player, value)
            move = apply_move(board, rng.choice(cols_left), player)
            if check_win_at(board, move, player):
                break
            if is_full(board):
                break
            player = other_player(player)
    return list(seen.values())
