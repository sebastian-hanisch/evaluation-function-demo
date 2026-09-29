"""Kreuzprobe: der exakte Löser (Grundwahrheit für Trainings-/Testdaten) muss
dieselben Werte liefern wie in minimax-demo/alpha-beta-demo/
transposition-table-demo gemessen."""

import pytest

from ev_constants import PLAYER_ONE
from ev_exact import exact_value
from ev_game import empty_board


@pytest.mark.parametrize("rows,cols", [(3, 3), (4, 3), (3, 4), (4, 4)])
def test_value_matches_previous_pieces(rows, cols):
    board = empty_board(rows, cols)
    assert exact_value(board, PLAYER_ONE) == 0
