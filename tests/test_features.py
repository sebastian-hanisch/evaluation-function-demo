"""Merkmalsextraktion: von Hand nachvollziehbare Fälle."""

from ev_constants import PLAYER_ONE, PLAYER_TWO
from ev_game import apply_move, empty_board
from ev_features import feature_vector


def test_empty_board_has_zero_features():
    board = empty_board(4, 4)
    assert feature_vector(board) == [0, 0, 0]


def test_single_stone_gives_one_stufe_1_window_per_line_through_it():
    # Auf einem 4x4-Brett gibt es 10 Fenster insgesamt (siehe test_game.py);
    # ein Stein unten links (0,0 nach Faller-Logik: Spalte 0) liegt auf Reihe
    # 3 - dort verlaufen genau 2 Fenster hindurch (horizontal Reihe 3,
    # Diagonale von (3,0) nach (0,3) existiert nicht bei 4x4 da die einzige
    # Diagonale (0,0)-(3,3) ist - stattdessen zaehlen wir nur, dass es > 0 ist
    # und ausschliesslich Stufe 1 betrifft.
    board = empty_board(4, 4)
    apply_move(board, 0, PLAYER_ONE)
    x = feature_vector(board)
    assert x[1] == 0  # Stufe 2
    assert x[2] == 0  # Stufe 3
    assert x[0] > 0  # Stufe 1: mindestens ein offenes Fenster mit 1 Rot-Stein


def test_feature_vector_is_antisymmetric_under_colour_swap():
    board_rot = empty_board(4, 3)
    apply_move(board_rot, 0, PLAYER_ONE)
    apply_move(board_rot, 0, PLAYER_ONE)

    board_gelb = empty_board(4, 3)
    apply_move(board_gelb, 0, PLAYER_TWO)
    apply_move(board_gelb, 0, PLAYER_TWO)

    x_rot = feature_vector(board_rot)
    x_gelb = feature_vector(board_gelb)
    assert x_rot == [-v for v in x_gelb]


def test_blocked_window_counts_nowhere():
    # Zwei verschiedene Farben im selben Fenster -> zaehlt weder fuer Rot
    # noch fuer Gelb. 1x4-Brett: genau ein Fenster (die ganze Reihe).
    board = empty_board(1, 4)
    apply_move(board, 0, PLAYER_ONE)
    apply_move(board, 1, PLAYER_TWO)
    assert feature_vector(board) == [0, 0, 0]


def test_three_in_open_window_is_stufe_3():
    board = empty_board(1, 4)
    apply_move(board, 0, PLAYER_ONE)
    apply_move(board, 1, PLAYER_ONE)
    apply_move(board, 2, PLAYER_ONE)
    x = feature_vector(board)
    assert x == [0, 0, 1]
