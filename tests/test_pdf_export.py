"""Regressionstest: aufeinanderfolgende multi_cell-Aufrufe dürfen nicht
crashen, keine fpdf2-Crash-Zeichen in PDF-gebundenen Strings."""

from ev_constants import EVAL_HAND, HAND_WEIGHTS, PLAYER_ONE
from ev_game import empty_board
from ev_pdf_export import build_pdf
from ev_search import search


def test_build_pdf_does_not_crash():
    board = empty_board(4, 3)
    result = search(board, PLAYER_ONE, max_depth=3, weights=HAND_WEIGHTS)
    pdf_bytes = build_pdf(4, 3, [], EVAL_HAND, 3, PLAYER_ONE, result.value, result.node_count, result.best_column)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 500
