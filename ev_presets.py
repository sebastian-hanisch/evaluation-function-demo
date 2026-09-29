"""PRESETS, Permalink (Begrenzen/Einrasten), Session-Defaults.

Die Suchtiefe wird NICHT in einem einzigen `depth_select`-Schlüssel gehalten,
sondern PRO BRETTGRÖSSE in einem eigenen Schlüssel (`depth_key`). Echter Fund
beim Bau: `st.slider(..., max_value=..., key="depth_select")` setzt den Wert
still auf das Minimum zurück, sobald sich `max_value` zwischen zwei Läufen
ändert - SELBST wenn der bisherige Wert innerhalb der neuen Grenzen liegt
(reproduziert mit einem Zwei-Zeilen-Repro-Skript, kein Anwendungsfehler,
echtes Streamlit-Verhalten). Ein Schlüssel pro Brett hat dagegen über seine
ganze Lebensdauer IMMER dasselbe `max_value` - der Reset-Fall tritt nie ein.
"""

from __future__ import annotations

import streamlit as st

from ev_constants import BOARD_OPTIONS, DEFAULT_BOARD_INDEX, DEFAULT_DEPTH, EVAL_FITTED, EVAL_HAND

PRESETS = {
    "Handgewichtet (4×3)": {"board_index": 0, "eval_choice": EVAL_HAND, "depth": DEFAULT_DEPTH, "moves": []},
    "Gefittet (4×3)": {"board_index": 0, "eval_choice": EVAL_FITTED, "depth": DEFAULT_DEPTH, "moves": []},
    "Echtes Vier-Gewinnt (6×7)": {"board_index": 2, "eval_choice": EVAL_HAND, "depth": 6, "moves": []},
}
PRESET_HELP = {
    "Handgewichtet (4×3)": "Kleines, exakt vergleichbares Brett mit der handgewählten Gewichtung.",
    "Gefittet (4×3)": "Dieselbe Größe, Gewichte per kleinste Quadrate an Trainingsdaten angepasst.",
    "Echtes Vier-Gewinnt (6×7)": "Der Standardgröße, die exakte Suche praktisch nie löst - hier in Sekundenbruchteilen.",
}

_DEFAULTS = {"board_index": DEFAULT_BOARD_INDEX, "eval_choice": EVAL_HAND, "depth": DEFAULT_DEPTH, "moves": []}


def depth_key(board_index: int) -> str:
    return f"depth_select_{board_index}"


def _default_depth_for(board_index: int) -> int:
    return min(DEFAULT_DEPTH, BOARD_OPTIONS[board_index]["max_depth"])


def apply_preset(name: str) -> None:
    preset = PRESETS[name]
    st.session_state["board_index_select"] = preset["board_index"]
    st.session_state["eval_choice_select"] = preset["eval_choice"]
    st.session_state[depth_key(preset["board_index"])] = preset["depth"]
    st.session_state["moves"] = list(preset["moves"])


def init_session_state_defaults() -> None:
    if "board_index_select" not in st.session_state:
        st.session_state["board_index_select"] = _DEFAULTS["board_index"]
    if "eval_choice_select" not in st.session_state:
        st.session_state["eval_choice_select"] = _DEFAULTS["eval_choice"]
    board_index = st.session_state["board_index_select"]
    key = depth_key(board_index)
    if key not in st.session_state:
        st.session_state[key] = _default_depth_for(board_index)
    if "moves" not in st.session_state:
        st.session_state["moves"] = list(_DEFAULTS["moves"])


def _parse_moves(raw: str) -> list[int]:
    if not raw:
        return []
    try:
        return [int(x) for x in raw.split(",") if x != ""]
    except ValueError:
        return []


def load_permalink_settings() -> None:
    """Lädt Einstellungen aus der URL - NUR beim allerersten Lauf dieser
    Session (sonst würde jeder Klick sofort wieder rückgängig gemacht - echter,
    bereits einmal gefundener Bug in minimax-demo, siehe dortige Moduldoku)."""
    if "board_index_select" in st.session_state:
        return
    params = st.query_params
    if not any(k in params for k in ("board", "moves", "eval", "depth")):
        return

    board_index = _DEFAULTS["board_index"]
    if "board" in params:
        try:
            candidate = int(params["board"])
        except ValueError:
            candidate = board_index
        if 0 <= candidate < len(BOARD_OPTIONS):
            board_index = candidate

    eval_choice = params.get("eval", _DEFAULTS["eval_choice"])
    if eval_choice not in {EVAL_HAND, EVAL_FITTED}:
        eval_choice = _DEFAULTS["eval_choice"]

    max_depth = BOARD_OPTIONS[board_index]["max_depth"]
    depth = _default_depth_for(board_index)
    if "depth" in params:
        try:
            depth = int(params["depth"])
        except ValueError:
            pass
    depth = max(1, min(depth, max_depth))

    moves = _parse_moves(params.get("moves", ""))

    st.session_state["board_index_select"] = board_index
    st.session_state["eval_choice_select"] = eval_choice
    st.session_state[depth_key(board_index)] = depth
    st.session_state["moves"] = moves


def sync_query_params(board_index: int, eval_choice: str, depth: int, moves: list[int]) -> None:
    st.query_params["board"] = str(board_index)
    st.query_params["eval"] = eval_choice
    st.query_params["depth"] = str(depth)
    st.query_params["moves"] = ",".join(str(m) for m in moves)
