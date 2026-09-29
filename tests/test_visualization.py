"""Regressionstest gegen den in minimax-demo gefundenen scaleanchor+range-Bug."""

from ev_constants import MEASURED_AGREEMENT
from ev_game import empty_board
from ev_visualization import agreement_figure, board_figure


def test_board_figure_uses_autorange_not_explicit_range():
    board = empty_board(4, 3)
    fig = board_figure(board, None, None, 1)
    assert fig.layout.xaxis.autorange is True
    assert fig.layout.xaxis.range is None
    assert fig.layout.yaxis.autorange is True
    assert fig.layout.yaxis.range is None


def test_board_figure_cell_count_matches_board_size():
    board = empty_board(6, 7)
    fig = board_figure(board, None, None, None)
    assert len(fig.data[0].x) == 6 * 7


def test_agreement_figure_has_two_traces():
    fig = agreement_figure(MEASURED_AGREEMENT)
    assert len(fig.data) == 2
    assert len(fig.data[0].x) == len(MEASURED_AGREEMENT)
