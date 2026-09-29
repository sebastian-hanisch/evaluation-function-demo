"""Gewichtsanpassung: reproduzierbar (fester Seed) und mit Domänenwissen
konsistent (nicht-negativ)."""

from ev_constants import TRAIN_COLS, TRAIN_GAMES, TRAIN_ROWS, TRAIN_SEED
from ev_data import generate_dataset
from ev_fit import fit_weights


def test_fit_is_deterministic_for_fixed_seed():
    data = generate_dataset(TRAIN_ROWS, TRAIN_COLS, TRAIN_GAMES, TRAIN_SEED)
    w1 = fit_weights(data)
    w2 = fit_weights(data)
    assert w1 == w2


def test_fitted_weights_are_non_negative():
    data = generate_dataset(TRAIN_ROWS, TRAIN_COLS, 500, seed=3)
    w = fit_weights(data)
    assert all(wi >= 0 for wi in w)


def test_fit_reproduces_measured_readme_weights():
    # Siehe ev_constants.py / README - die tatsächlich für die App verwendeten
    # Trainingsparameter müssen dieselben Gewichte liefern wie gemessen.
    data = generate_dataset(TRAIN_ROWS, TRAIN_COLS, TRAIN_GAMES, TRAIN_SEED)
    w = fit_weights(data)
    assert w[0] == 0.0
    assert w[1] == 0.0
    assert w[2] > 0.28 and w[2] < 0.29
