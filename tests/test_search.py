"""Tiefenbegrenzte Suche: Grundverhalten + Konvergenz gegen den exakten Wert
bei wachsender Tiefe (der zentrale Vertrauens-Check dieses Stücks)."""

from ev_constants import HAND_WEIGHTS, PLAYER_ONE, PLAYER_TWO
from ev_exact import exact_value
from ev_game import apply_move, empty_board
from ev_search import search


def test_search_finds_immediate_win():
    board = empty_board(4, 2)
    for col, player in [(0, PLAYER_ONE), (1, PLAYER_TWO)] * 3:
        apply_move(board, col, player)
    result = search(board, PLAYER_ONE, max_depth=1, weights=HAND_WEIGHTS)
    assert result.best_column == 0
    assert result.value >= 1e5


def test_search_at_full_depth_matches_exact_value_on_small_board():
    # Wenn max_depth mindestens so groß ist wie die verbleibenden Felder,
    # erreicht die Suche immer das Spielende - dann muss der Wert exakt sein,
    # unabhängig von den Gewichten (Bewertungsfunktion wird nie gebraucht).
    board = empty_board(3, 3)
    exact = exact_value([row[:] for row in board], PLAYER_ONE)
    result = search([row[:] for row in board], PLAYER_ONE, max_depth=9, weights=HAND_WEIGHTS)
    assert result.value == exact


def test_deeper_search_does_not_get_worse_node_efficiency_ordering():
    # Kein strenger Beweis, aber ein Sanity-Check: mehr Tiefe -> mindestens so
    # viele Knoten.
    board = empty_board(4, 3)
    shallow = search([row[:] for row in board], PLAYER_ONE, max_depth=2, weights=HAND_WEIGHTS)
    deep = search([row[:] for row in board], PLAYER_ONE, max_depth=4, weights=HAND_WEIGHTS)
    assert deep.node_count >= shallow.node_count


def test_search_is_pure_no_board_mutation():
    board = empty_board(4, 3)
    before = [row[:] for row in board]
    search(board, PLAYER_ONE, max_depth=3, weights=HAND_WEIGHTS)
    assert board == before


def test_zero_weights_give_zero_estimate_on_non_terminal_cutoff():
    board = empty_board(4, 4)
    result = search(board, PLAYER_ONE, max_depth=1, weights=[0.0, 0.0, 0.0])
    assert result.value == 0.0
