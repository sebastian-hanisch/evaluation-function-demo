"""Kennzahlen, Gewichts-Auswahl und Formatierung."""

from __future__ import annotations

import streamlit as st

from ev_constants import EVAL_HAND, HAND_WEIGHTS, PLAYER_NAMES, PLAYER_ONE, TRAIN_COLS, TRAIN_GAMES, TRAIN_ROWS, TRAIN_SEED
from ev_data import generate_dataset
from ev_fit import fit_weights


@st.cache_data(show_spinner="Passe Gewichte an Trainingsdaten an ...")
def fitted_weights() -> list[float]:
    data = generate_dataset(TRAIN_ROWS, TRAIN_COLS, TRAIN_GAMES, TRAIN_SEED)
    return fit_weights(data)


def weights_for(choice: str) -> list[float]:
    return HAND_WEIGHTS if choice == EVAL_HAND else fitted_weights()


def to_move_verdict(value: float, player_to_move: int) -> str:
    name = PLAYER_NAMES[player_to_move]
    outcome_for_mover = value if player_to_move == PLAYER_ONE else -value
    if abs(outcome_for_mover) < 1:
        return f"{name} steht laut Schätzung etwa ausgeglichen."
    if outcome_for_mover >= 1e5:
        return f"{name} hat gerade eben gewonnen."
    if outcome_for_mover <= -1e5:
        return f"{name} hat gerade eben verloren."
    if outcome_for_mover > 0:
        return f"{name} steht laut Schätzung im Vorteil."
    return f"{name} steht laut Schätzung im Nachteil."


def format_de_number(value: float, decimals: int = 0) -> str:
    return f"{value:,.{decimals}f}".replace(",", ".")
