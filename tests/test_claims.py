"""Jede Zahl aus dem README wird hier gegen den tatsächlichen Code nachgerechnet."""

import random
import time

import pytest

from ev_constants import HAND_WEIGHTS, PLAYER_ONE, TRAIN_COLS, TRAIN_GAMES, TRAIN_ROWS, TRAIN_SEED
from ev_data import generate_dataset
from ev_exact import exact_value
from ev_fit import fit_weights
from ev_game import apply_move, check_win_at, empty_board, is_full, legal_columns, other_player, undo_move
from ev_search import search


def test_readme_fitted_weights():
    data = generate_dataset(TRAIN_ROWS, TRAIN_COLS, TRAIN_GAMES, TRAIN_SEED)
    w = fit_weights(data)
    assert w == pytest.approx([0.0, 0.0, 0.2882882882882883])
    assert len(data) == 4655


def test_readme_standard_board_node_count_and_speed():
    board = empty_board(6, 7)
    t0 = time.perf_counter()
    result = search(board, PLAYER_ONE, max_depth=6, weights=HAND_WEIGHTS)
    dt = time.perf_counter() - t0
    assert result.node_count == 16_393
    assert dt < 5.0  # großzügige Marge - CI-Runner sind langsamer als lokal


def _true_best_columns(board, player):
    values = {}
    for col in legal_columns(board):
        move = apply_move(board, col, player)
        if check_win_at(board, move, player):
            v = 1 if player == PLAYER_ONE else -1
        elif is_full(board):
            v = 0
        else:
            v = exact_value([row[:] for row in board], other_player(player))
        undo_move(board, move)
        values[col] = v
    best = max(values.values()) if player == PLAYER_ONE else min(values.values())
    return [c for c, v in values.items() if v == best]


def test_readme_agreement_in_distribution_4x3():
    train = generate_dataset(TRAIN_ROWS, TRAIN_COLS, TRAIN_GAMES, TRAIN_SEED)
    w_fit = fit_weights(train)

    data = generate_dataset(TRAIN_ROWS, TRAIN_COLS, TRAIN_GAMES, TRAIN_SEED)
    random.Random(42).shuffle(data)
    split = int(len(data) * 0.8)
    test = data[split:]
    random.Random(11).shuffle(test)

    for max_depth, expect_n in ((2, 553), (4, 197)):
        agree_fit = agree_hand = total = 0
        for board_key, player, _value in test:
            board = [list(row) for row in board_key]
            if sum(row.count(0) for row in board) <= max_depth:
                continue
            total += 1
            best_cols = _true_best_columns(board, player)
            r_fit = search([row[:] for row in board], player, max_depth, w_fit)
            r_hand = search([row[:] for row in board], player, max_depth, HAND_WEIGHTS)
            agree_fit += r_fit.best_column in best_cols
            agree_hand += r_hand.best_column in best_cols
        assert total == expect_n
        assert agree_fit == total
        assert agree_hand == total


def test_readme_agreement_out_of_distribution_3x4():
    # Der eigentliche, unerwartete Befund: auf einem UNGESEHENEN Brett (3x4,
    # das Training war auf 4x3) schneidet die Handgewichtung besser ab.
    train = generate_dataset(TRAIN_ROWS, TRAIN_COLS, TRAIN_GAMES, TRAIN_SEED)
    w_fit = fit_weights(train)

    test_data = generate_dataset(3, 4, 3000, seed=99)
    random.Random(7).shuffle(test_data)

    expected = {2: (0.994, 0.976), 4: (1.0, 0.978)}
    for max_depth, (expect_hand, expect_fit) in expected.items():
        agree_fit = agree_hand = total = 0
        for board_key, player, _value in test_data:
            board = [list(row) for row in board_key]
            if sum(row.count(0) for row in board) <= max_depth:
                continue
            total += 1
            best_cols = _true_best_columns(board, player)
            r_fit = search([row[:] for row in board], player, max_depth, w_fit)
            r_hand = search([row[:] for row in board], player, max_depth, HAND_WEIGHTS)
            agree_fit += r_fit.best_column in best_cols
            agree_hand += r_hand.best_column in best_cols
            if total >= 500:
                break
        assert agree_hand / total == pytest.approx(expect_hand, abs=0.01)
        assert agree_fit / total == pytest.approx(expect_fit, abs=0.01)
        assert agree_hand >= agree_fit  # der Kernbefund: Hand schlägt Fit hier
