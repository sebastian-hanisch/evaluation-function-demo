"""Gewichte per NICHT-NEGATIVEN kleinsten Quadraten an bekannte exakte
Spielwerte anpassen - der Gegenpart zur handgewählten Gewichtung in
`ev_constants.HAND_WEIGHTS`.

Nicht-Negativität ist Absicht (nicht nur ein Optimierungsdetail): ein
zusätzliches offenes eigenes Fenster kann die eigene Stellung per Definition
nie verschlechtern - ein unbeschränkter Fit (`numpy.linalg.lstsq`) lieferte in
einem ersten Versuch NEGATIVE Gewichte für Stufe 1/2 (Artefakt der
Zufallspartien-Trainingsverteilung, nicht plausibel), die hier per
Domänenwissen ausgeschlossen werden.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import nnls

from ev_features import feature_vector


def fit_weights(dataset: list[tuple[tuple, int, int]]) -> list[float]:
    """`dataset`: Liste (board_key, player_to_move, exact_value). Löst
    min_{w >= 0} ||X w - y||^2 (kein Bias-Term - das Merkmal ist bereits
    symmetrisch um 0, eine leere Stellung hat Merkmalsvektor 0 und Wert 0,
    ein Bias-Term wäre hier nicht sinnvoll interpretierbar)."""
    X = []
    y = []
    for board_key, _player, value in dataset:
        board = [list(row) for row in board_key]
        X.append(feature_vector(board))
        y.append(value)
    X = np.array(X, dtype=float)
    y = np.array(y, dtype=float)
    weights, _residual = nnls(X, y)
    return weights.tolist()
