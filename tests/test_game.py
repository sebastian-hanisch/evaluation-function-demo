"""Brettmechanik - wortgleiche Kopie der Tests aus den Vorgängerstücken."""

import pytest

from ev_constants import EMPTY, PLAYER_ONE, PLAYER_TWO
from ev_game import (
    all_windows,
    apply_move,
    check_win_at,
    empty_board,
    is_full,
    legal_columns,
    other_player,
    replay,
    undo_move,
    winning_line,
)


def test_empty_board_shape():
    board = empty_board(3, 4)
    assert len(board) == 3
    assert all(len(row) == 4 for row in board)
    assert all(cell == EMPTY for row in board for cell in row)


def test_other_player():
    assert other_player(PLAYER_ONE) == PLAYER_TWO
    assert other_player(PLAYER_TWO) == PLAYER_ONE


def test_drop_lands_on_lowest_free_row():
    board = empty_board(3, 3)
    move = apply_move(board, 1, PLAYER_ONE)
    assert move.row == 2


def test_full_column_raises():
    board = empty_board(2, 1)
    apply_move(board, 0, PLAYER_ONE)
    apply_move(board, 0, PLAYER_TWO)
    with pytest.raises(ValueError):
        apply_move(board, 0, PLAYER_ONE)


def test_legal_columns_excludes_full_ones():
    board = empty_board(2, 2)
    apply_move(board, 0, PLAYER_ONE)
    apply_move(board, 0, PLAYER_TWO)
    assert legal_columns(board) == [1]


def test_undo_move_restores_empty_cell():
    board = empty_board(3, 3)
    move = apply_move(board, 0, PLAYER_ONE)
    undo_move(board, move)
    assert board[move.row][move.column] == EMPTY


def test_horizontal_win_detected():
    board = empty_board(1, 4)
    move = None
    for col in range(4):
        move = apply_move(board, col, PLAYER_ONE)
    assert check_win_at(board, move, PLAYER_ONE)


def test_three_in_a_row_is_not_a_win():
    board = empty_board(1, 3)
    move = None
    for col in range(3):
        move = apply_move(board, col, PLAYER_ONE)
    assert not check_win_at(board, move, PLAYER_ONE)


def test_replay_stops_at_win():
    state = replay(4, 4, [0, 1, 0, 1, 0, 1, 0])
    assert state.is_terminal
    assert state.winner == PLAYER_ONE


def test_winning_line_returns_four_cells():
    board = empty_board(1, 4)
    move = None
    for col in range(4):
        move = apply_move(board, col, PLAYER_ONE)
    line = winning_line(board, move, PLAYER_ONE)
    assert line is not None
    assert len(line) == 4


def test_is_full_true_only_when_no_columns_left():
    board = empty_board(1, 2)
    assert not is_full(board)
    apply_move(board, 0, PLAYER_ONE)
    assert not is_full(board)
    apply_move(board, 1, PLAYER_TWO)
    assert is_full(board)


def test_all_windows_count_for_3x3():
    # 3x3: nur die beiden Diagonalen sind Länge-4-fähig? Nein - 3x3 hat KEIN
    # Länge-4-Fenster ueberhaupt (Sieglaenge 4 > jede Dimension).
    assert all_windows(3, 3) == []


def test_all_windows_count_for_4x4():
    # 4x4: 4 horizontal (1 je Zeile) + 4 vertikal (1 je Spalte) + 1 Diagonale
    # je Richtung = 10.
    windows = all_windows(4, 4)
    assert len(windows) == 10
    assert all(len(w) == 4 for w in windows)


def test_all_windows_count_for_standard_board():
    # 6x7 (Standard-Vier-Gewinnt): bekannter Wert = 69 Fenster.
    assert len(all_windows(6, 7)) == 69
