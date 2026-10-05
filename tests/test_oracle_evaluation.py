"""Unabhängiges Orakel für exakten Löser, Merkmale, tiefenbegrenzte Suche und Gewichtsfit.

Anderer Rechenweg als die Demo-Module: Stellung als Spalten-Tupel, Siegprüfung und Merkmale
durch Aufzählen aller Viererlinien, exakte Werte per memoisiertem Minimax (ohne Pruning/Tabelle),
tiefenbegrenzte Suche als reines Minimax (ohne Alpha-Beta), nicht-negative kleinste Quadrate durch
Enumeration aller Stützmengen mit `numpy.linalg.lstsq` (statt `scipy.optimize.nnls`).
"""

import itertools
import random
from functools import lru_cache

import numpy as np
import pytest

from ev_data import generate_dataset
from ev_exact import exact_value
from ev_features import feature_vector
from ev_fit import fit_weights
from ev_game import apply_move, check_win_at, empty_board, legal_columns
from ev_search import search


class _Oracle:
    def __init__(self, rows, cols):
        self.rows, self.cols = rows, cols
        self.lines = []
        for r in range(rows):
            for c in range(cols):
                for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                    cells = [(r + i * dr, c + i * dc) for i in range(4)]
                    if all(0 <= a < rows and 0 <= b < cols for a, b in cells):
                        self.lines.append(cells)
        self.value = lru_cache(maxsize=None)(self._value)

    def cell(self, st, r, c):
        h = self.rows - 1 - r
        return st[c][h] if h < len(st[c]) else 0

    def won(self, st, p):
        return any(all(self.cell(st, r, c) == p for r, c in line) for line in self.lines)

    def moves(self, st):
        return [c for c in range(self.cols) if len(st[c]) < self.rows]

    def play(self, st, c, p):
        return st[:c] + (st[c] + (p,),) + st[c + 1 :]

    def _value(self, st, p):
        vals = []
        for c in self.moves(st):
            ns = self.play(st, c, p)
            if self.won(ns, p):
                vals.append(1 if p == 1 else -1)
            elif not self.moves(ns):
                vals.append(0)
            else:
                vals.append(self.value(ns, 3 - p))
        return max(vals) if p == 1 else min(vals)

    def features(self, st):
        f = [0, 0, 0]
        for line in self.lines:
            vals = [self.cell(st, r, c) for r, c in line]
            owners = set(vals) - {0}
            if len(owners) == 1:
                f[vals.count(next(iter(owners))) - 1] += 1 if 1 in owners else -1
        return f

    def plain(self, st, p, depth, w):
        if depth == 0:
            return sum(a * b for a, b in zip(w, self.features(st)))
        vals = list(self.child_values(st, p, depth, w).values())
        return max(vals) if p == 1 else min(vals)

    def child_values(self, st, p, depth, w):
        out = {}
        for c in self.moves(st):
            ns = self.play(st, c, p)
            if self.won(ns, p):
                out[c] = 1e6 if p == 1 else -1e6
            elif not self.moves(ns):
                out[c] = 0.0
            else:
                out[c] = self.plain(ns, 3 - p, depth - 1, w)
        return out


def _to_state(board):
    rows, cols = len(board), len(board[0])
    out = []
    for c in range(cols):
        col = []
        for r in range(rows - 1, -1, -1):
            if board[r][c] == 0:
                break
            col.append(board[r][c])
        out.append(tuple(col))
    return tuple(out)


def _random_position(rng, rows, cols, max_free, min_free=0):
    board, p = empty_board(rows, cols), 1
    for _ in range(rng.randint(max(0, rows * cols - max_free), rows * cols - min_free)):
        free = legal_columns(board)
        if not free:
            return None
        mv = apply_move(board, rng.choice(free), p)
        if check_win_at(board, mv, p) or not legal_columns(board):
            return None
        p = 3 - p
    return (board, p) if legal_columns(board) else None


def test_exact_value_and_features_match_oracle():
    rng = random.Random(1)
    done = 0
    while done < 120:
        rows, cols = rng.randint(1, 5), rng.randint(1, 5)
        pos = _random_position(rng, rows, cols, 9)
        if pos is None:
            continue
        board, p = pos
        o, st = _Oracle(rows, cols), _to_state(board)
        assert exact_value([r[:] for r in board], p) == o.value(st, p)
        assert feature_vector(board) == o.features(st)
        swapped = [[(3 - v if v else 0) for v in row] for row in board]
        assert feature_vector(swapped) == [-x for x in feature_vector(board)]
        done += 1


@pytest.mark.parametrize("rows,cols", [(3, 3), (4, 3), (3, 4)])
def test_empty_board_is_a_draw(rows, cols):
    assert exact_value(empty_board(rows, cols), 1) == 0 == _Oracle(rows, cols).value(tuple(() for _ in range(cols)), 1)


def test_depth_limited_search_equals_plain_minimax():
    rng = random.Random(2)
    weight_sets = [[1.0, 8.0, 40.0], [0.0, 0.0, 0.2882882882882883], [0.3, 1.7, 2.2], [0.0, 0.0, 0.0]]
    done = 0
    while done < 60:
        rows, cols = rng.randint(2, 4), rng.randint(2, 4)
        pos = _random_position(rng, rows, cols, rows * cols, min_free=1)
        if pos is None:
            continue
        board, p = pos
        o, st = _Oracle(rows, cols), _to_state(board)
        depth, w = rng.randint(1, 3), rng.choice(weight_sets)
        vals = o.child_values(st, p, depth, w)
        best = max(vals.values()) if p == 1 else min(vals.values())
        first = [c for c in o.moves(st) if vals[c] == best][0]
        res = search([r[:] for r in board], p, depth, w)
        assert res.value == pytest.approx(best)
        assert res.best_column == first
        done += 1


def _oracle_nnls(X, y):
    best = None
    for k in range(4):
        for support in itertools.combinations(range(3), k):
            w = np.zeros(3)
            if support:
                sol = np.linalg.lstsq(X[:, list(support)], y, rcond=None)[0]
                if (sol < 0).any():
                    continue
                w[list(support)] = sol
            rss = float(((X @ w - y) ** 2).sum())
            if best is None or rss < best[0] - 1e-12:
                best = (rss, w)
    return best[1]


def test_fit_matches_support_enumeration_and_labels_match_oracle():
    data = generate_dataset(4, 3, 300, seed=5)
    o = _Oracle(4, 3)
    X = np.array([o.features(_to_state([list(r) for r in key])) for key, _p, _v in data], dtype=float)
    y = np.array([v for _k, _p, v in data], dtype=float)
    for key, p, v in data[:80]:
        assert o.value(_to_state([list(r) for r in key]), p) == v
    assert fit_weights(data) == pytest.approx(list(_oracle_nnls(X, y)), abs=1e-9)
