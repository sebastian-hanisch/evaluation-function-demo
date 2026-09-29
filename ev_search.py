"""Tiefenbegrenzte Alpha-Beta-Suche: statt bis zum Spielende durchzusuchen,
bricht die Suche nach `max_depth` Halbzügen ab und schätzt die Stellung über
eine lineare Bewertungsfunktion (Gewichte × Merkmale) statt sie exakt zu
lösen. Das macht Bretter durchsuchbar, auf denen selbst Alpha-Beta+Tabelle
nicht mehr bis zum Ende kommt - der Preis: das Ergebnis ist eine SCHÄTZUNG,
kein bewiesener Wert.
"""

from __future__ import annotations

from dataclasses import dataclass

from ev_constants import PLAYER_ONE
from ev_features import feature_vector
from ev_game import apply_move, check_win_at, is_full, legal_columns, other_player, undo_move

_NEG_INF, _POS_INF = -1e9, 1e9


@dataclass
class NodeCounter:
    count: int = 0


@dataclass
class SearchResult:
    value: float
    best_column: int
    node_count: int


def evaluate(board: list[list[int]], weights: list[float]) -> float:
    x = feature_vector(board)
    return sum(w * xi for w, xi in zip(weights, x))


def _terminal_value(board, move, player) -> float | None:
    if check_win_at(board, move, player):
        return 1e6 if player == PLAYER_ONE else -1e6
    if is_full(board):
        return 0.0
    return None


def _recurse(board, player, depth, alpha, beta, weights, counter: NodeCounter) -> float:
    counter.count += 1
    if depth == 0:
        return evaluate(board, weights)

    best = None
    for col in legal_columns(board):
        move = apply_move(board, col, player)
        terminal = _terminal_value(board, move, player)
        value = terminal if terminal is not None else _recurse(board, other_player(player), depth - 1, alpha, beta, weights, counter)
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
    return best


def search(board: list[list[int]], player: int, max_depth: int, weights: list[float]) -> SearchResult:
    counter = NodeCounter()
    alpha, beta = _NEG_INF, _POS_INF
    best_value = None
    best_col = None
    for col in legal_columns(board):
        move = apply_move(board, col, player)
        terminal = _terminal_value(board, move, player)
        value = terminal if terminal is not None else _recurse(board, other_player(player), max_depth - 1, alpha, beta, weights, counter)
        undo_move(board, move)
        if player == PLAYER_ONE:
            if best_value is None or value > best_value:
                best_value, best_col = value, col
            alpha = max(alpha, best_value)
        else:
            if best_value is None or value < best_value:
                best_value, best_col = value, col
            beta = min(beta, best_value)
        if alpha >= beta:
            break
    return SearchResult(value=best_value, best_column=best_col, node_count=counter.count)
