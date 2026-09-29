"""Rauchtests der Streamlit-Oberfläche per AppTest."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

import ev_constants as C
from ev_presets import depth_key

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app.py"


def _run(setup=None):
    at = AppTest.from_file(str(APP), default_timeout=90)
    if setup is not None:
        setup(at)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def test_default_renders_without_exception():
    at = _run()
    assert any("Stellung" in h.value for h in at.subheader)


def test_every_board_option_renders():
    for index in range(len(C.BOARD_OPTIONS)):

        def setup(at, index=index):
            at.session_state["board_index_select"] = index
            at.session_state["moves"] = []

        _run(setup)


def test_both_eval_choices_render():
    for choice in (C.EVAL_HAND, C.EVAL_FITTED):

        def setup(at, choice=choice):
            at.session_state["eval_choice_select"] = choice

        _run(setup)


def test_each_board_keeps_its_own_depth_independently():
    # Echter Fund beim Bau: st.slider setzt den Wert still auf das Minimum
    # zurueck, sobald sich max_value fuer DENSELBEN Schluessel aendert (siehe
    # ev_presets.py-Moduldoku) - Fix: ein eigener Schluessel je Brettgroesse,
    # dessen max_value sich nie aendert.
    def setup(at):
        at.session_state["board_index_select"] = 0
        at.session_state[depth_key(0)] = 8

    at = _run(setup)
    at.radio(key="board_index_select").set_value(2)  # 6x7, max_depth=6
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state[depth_key(2)] <= 6
    assert at.session_state[depth_key(0)] == 8  # unveraendert, eigener Schluessel

    at.radio(key="board_index_select").set_value(0)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state[depth_key(0)] == 8  # beim Zurueckwechseln erhalten


def test_clicking_a_column_button_plays_a_move():
    at = _run()
    drop_buttons = [b for b in at.button if b.key and b.key.startswith("drop_")]
    assert drop_buttons
    drop_buttons[0].click()
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert len(at.session_state["moves"]) == 1


def test_switching_board_size_resets_moves():
    def setup(at):
        at.session_state["board_index_select"] = 0
        at.session_state["moves"] = [0]

    at = _run(setup)
    at.radio(key="board_index_select").set_value(1)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["moves"] == []


def test_permalink_restores_everything():
    at = AppTest.from_file(str(APP), default_timeout=90)
    at.query_params["board"] = "1"
    at.query_params["eval"] = C.EVAL_FITTED
    at.query_params["depth"] = "3"
    at.query_params["moves"] = "0,1"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["board_index_select"] == 1
    assert at.session_state["eval_choice_select"] == C.EVAL_FITTED
    assert at.session_state[depth_key(1)] == 3
    assert at.session_state["moves"] == [0, 1]


def test_permalink_does_not_get_clobbered_by_later_rerun():
    at = AppTest.from_file(str(APP), default_timeout=90)
    at.query_params["board"] = "0"
    at.run()
    drop_buttons = [b for b in at.button if b.key and b.key.startswith("drop_")]
    drop_buttons[0].click()
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["moves"] == [0]
