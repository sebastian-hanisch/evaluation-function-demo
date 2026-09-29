"""Bewertungsfunktionen: statt bis zum Spielende zu suchen, wird die Suche
nach wenigen Halbzügen abgebrochen und die Stellung geschätzt - macht auch
das echte Standard-Vier-Gewinnt-Brett (6×7) durchsuchbar.

Kind-Stück von minimax-demo (Wurzel-Ast B der Adversarische-Suche-Linie).
"""

from __future__ import annotations

import streamlit as st

import ev_constants as C
from ev_evaluation import format_de_number, to_move_verdict, weights_for
from ev_exact import exact_value
from ev_game import apply_move, check_win_at, is_full, legal_columns, other_player, replay, undo_move
from ev_pdf_export import build_pdf
from ev_presets import (
    PRESET_HELP,
    PRESETS,
    apply_preset,
    depth_key,
    init_session_state_defaults,
    load_permalink_settings,
    sync_query_params,
)
from ev_search import search
from ev_visualization import agreement_figure, board_figure

_de = format_de_number

st.set_page_config(page_title="Bewertungsfunktion – Sebastian Hanisch", layout="wide")

st.title("📐 Bewertungsfunktionen: schätzen statt bis zum Ende suchen")
st.markdown(
    """
    Bisher hat diese Linie immer bis zum **Spielende** durchgesucht – bewiesen exakt, aber auf großen
    Brettern unbezahlbar. Eine **Bewertungsfunktion** bricht die Suche nach wenigen Zügen ab und schätzt
    die Stellung stattdessen anhand von Merkmalen (hier: offene Linien je Bedrohungsstufe). Diese Demo
    vergleicht zwei Gewichtungen dieser Merkmale – **handgewählt** und **per kleinste Quadrate an
    bekannten Werten angepasst** – und zeigt, was das für die Zugwahl wirklich bedeutet. Am Ende der
    Seite: die 📐 Mathematische Formulierung.
    """
)

st.caption("🎯 Schnellstart")
preset_cols = st.columns(len(PRESETS))
for col, name in zip(preset_cols, PRESETS):
    col.button(name, use_container_width=True, on_click=apply_preset, args=(name,), help=PRESET_HELP[name])
st.caption("🔗 Die URL merkt sich Brettgröße, Bewertung, Suchtiefe und Zugfolge (Permalink).")

load_permalink_settings()
init_session_state_defaults()


def _reset_moves() -> None:
    st.session_state["moves"] = []


def _on_board_change() -> None:
    st.session_state["moves"] = []


with st.sidebar:
    st.header("⚙️ Einstellungen")
    eval_choice = st.radio(
        "Bewertungsfunktion",
        options=[C.EVAL_HAND, C.EVAL_FITTED],
        format_func=lambda o: C.EVAL_LABELS[o],
        key="eval_choice_select",
        on_change=_reset_moves,
    )
    board_index = st.radio(
        "Brettgröße",
        options=range(len(C.BOARD_OPTIONS)),
        format_func=lambda i: C.BOARD_OPTIONS[i]["label"],
        key="board_index_select",
        on_change=_on_board_change,
    )
    max_depth = C.BOARD_OPTIONS[board_index]["max_depth"]
    this_depth_key = depth_key(board_index)
    if this_depth_key not in st.session_state:
        st.session_state[this_depth_key] = min(C.DEFAULT_DEPTH, max_depth)
    depth = st.slider(
        "Suchtiefe (Halbzüge)",
        min_value=1,
        max_value=max_depth,
        key=this_depth_key,
        on_change=_reset_moves,
        help="Bei kleinen Brettern bis zur maximalen Tiefe = exakte Suche (keine Schätzung mehr nötig).",
    )
    if st.button("↺ Neues Spiel", use_container_width=True):
        st.session_state["moves"] = []
        st.rerun()

board_spec = C.BOARD_OPTIONS[board_index]
rows, cols = board_spec["rows"], board_spec["cols"]
moves: list[int] = [m for m in st.session_state["moves"] if 0 <= m < cols]
sync_query_params(board_index, eval_choice, depth, moves)

weights = weights_for(eval_choice)


@st.cache_data(show_spinner="Suche mit Bewertungsfunktion ...")
def _replay_and_search(rows: int, cols: int, moves: tuple[int, ...], depth: int, weights: tuple[float, ...]):
    state = replay(rows, cols, list(moves))
    if state.is_terminal:
        return state, None
    result = search([row[:] for row in state.board], state.player_to_move, depth, list(weights))
    return state, result


@st.cache_data(show_spinner="Löse exakt zum Vergleich ...")
def _exact_for(rows: int, cols: int, moves: tuple[int, ...]):
    state = replay(rows, cols, list(moves))
    if state.is_terminal:
        return None, None
    board = [row[:] for row in state.board]
    values = {}
    for col in legal_columns(board):
        move = apply_move(board, col, state.player_to_move)
        if check_win_at(board, move, state.player_to_move):
            v = 1 if state.player_to_move == C.PLAYER_ONE else -1
        elif is_full(board):
            v = 0
        else:
            v = exact_value(board, other_player(state.player_to_move))
        undo_move(board, move)
        values[col] = v
    best = max(values.values()) if state.player_to_move == C.PLAYER_ONE else min(values.values())
    best_cols = [c for c, v in values.items() if v == best]
    return best, best_cols


state, result = _replay_and_search(rows, cols, tuple(moves), depth, tuple(weights))

st.subheader("Stellung")
board_col, info_col = st.columns([2, 1])

with board_col:
    best_col = result.best_column if result is not None else None
    fig = board_figure(state.board, state.last_move, state.winner, best_col)
    st.plotly_chart(fig, use_container_width=True, key="board_chart")

    if not state.is_terminal:
        click_cols = st.columns(cols)
        for c, click_col in enumerate(click_cols):
            full_column = state.board[0][c] != C.EMPTY
            label = f"⬇{c}" + (" ★" if c == best_col else "")
            if click_col.button(label, key=f"drop_{c}", disabled=full_column, use_container_width=True):
                st.session_state["moves"] = moves + [c]
                st.rerun()

with info_col:
    if state.is_terminal:
        if state.winner is not None:
            st.success(f"Spiel beendet: {C.PLAYER_NAMES[state.winner]} hat gewonnen.")
        else:
            st.info("Spiel beendet: Remis (Brett voll).")
    else:
        st.metric("Am Zug", C.PLAYER_NAMES[state.player_to_move])
        st.metric("Geschätzter Wert", f"{result.value:.2f}" if abs(result.value) < 1000 else ("Sieg" if result.value > 0 else "Niederlage"))
        st.metric("Durchsuchte Knoten", _de(result.node_count))
        verdict = to_move_verdict(result.value, state.player_to_move)
        st.info(verdict)
        st.caption("★ = von der Suche gewählte Spalte (Schätzung, siehe 📐 unten).")

        pdf_bytes = build_pdf(rows, cols, moves, eval_choice, depth, state.player_to_move, result.value, result.node_count, best_col)
        st.download_button("📄 Analyse als PDF", data=pdf_bytes, file_name="bewertungsfunktion_analyse.pdf", mime="application/pdf")

st.markdown("---")
st.subheader("🔬 Wie gut ist die Schätzung wirklich?")
if state.is_terminal:
    st.info("Spiel bereits beendet - kein weiterer Vergleich möglich.")
elif not board_spec["exact_ok"]:
    st.info(
        "Auf dem echten Vier-Gewinnt-Brett (6×7) gibt es keinen exakten Vergleichswert - selbst mit "
        "Alpha-Beta und Transpositionstabelle (siehe transposition-table-demo) unerreichbar langsam. "
        "Der Vergleich unten läuft deshalb nur auf den beiden kleinen Brettern."
    )
else:
    exact_best, exact_best_cols = _exact_for(rows, cols, tuple(moves))
    if best_col in exact_best_cols:
        st.success(
            f"Bei Suchtiefe {depth} wählt die Suche Spalte {best_col} - das ist (mit-)optimal laut "
            f"exakter Lösung (optimale Spalten: {', '.join(map(str, exact_best_cols))})."
        )
    else:
        st.warning(
            f"Bei Suchtiefe {depth} wählt die Suche Spalte {best_col} - das ist NICHT optimal laut "
            f"exakter Lösung (optimale Spalten: {', '.join(map(str, exact_best_cols))})."
        )
    st.caption(f"Exakter Spielwert dieser Stellung: {exact_best:+d}.")

st.subheader("🔬 Handgewicht oder gefittet – was funktioniert besser?")
st.markdown(
    """
    Erwartet war: eine an bekannten exakten Werten angepasste Gewichtung sollte eine handgewählte
    schlagen. **Gemessen** (Zugübereinstimmung mit dem exakten Optimalzug, 500 Testpositionen je Balken):
    """
)
st.plotly_chart(agreement_figure(C.MEASURED_AGREEMENT), use_container_width=True, key="agreement_chart")
st.warning(
    "**Ehrlicher, unerwarteter Befund:** auf dem Trainingsbrett (4×3) sind beide gleich gut (100 %) – "
    "aber auf einem UNGESEHENEN Brett (3×4) schneidet die simple Handgewichtung BESSER ab als die "
    "gefittete (99,4–100 % vs. 97,6–97,8 %). Die kleinste-Quadrate-Anpassung verwirft dabei Stufe 1 und "
    "2 komplett (beide Gewichte fallen auf 0) und verlässt sich nur noch auf Stufe 3 – das passt gut zu "
    "den Trainingsdaten (Zufallspartien auf 4×3), verallgemeinert aber schlechter als die Handgewichtung, "
    "die alle drei Stufen nutzt. Ein Lehrbuchfall dafür, dass eine Metrik zu optimieren (hier: quadratischer "
    "Fehler beim Vorhersagen des Werts) nicht automatisch die Metrik verbessert, die eigentlich zählt "
    "(hier: den richtigen Zug zu wählen)."
)

st.subheader("🔬 Jetzt spielbar: echtes Vier-Gewinnt")
st.markdown(
    """
    Auf dem Standardbrett (6 Zeilen × 7 Spalten) braucht die tiefenbegrenzte Suche mit Bewertungsfunktion
    bei Tiefe 6 nur rund 16.000 Knoten und **0,25 Sekunden** (gemessen, `tests/test_claims.py`) – ein
    Brett, auf dem selbst Alpha-Beta mit Transpositionstabelle (siehe transposition-table-demo, dort schon
    bei 5×5 27,9 Sekunden) nicht mehr exakt durchkäme.
    """
)

st.markdown("---")
st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
    - **Die Schätzung ist beweisbar NICHT exakt** – anders als in jedem bisherigen Stück dieser Linie gibt
      es keine Garantie mehr, dass der gewählte Zug wirklich optimal ist (siehe Experiment oben).
    - **Nur 3 Merkmale, nur linear.** Echte Engines (z. B. NNUE in modernen Schach-Engines) nutzen tausende
      Merkmale und nichtlineare Netze - hier bewusst klein und nachvollziehbar gehalten.
    - **Die Trainingsdaten stammen aus Zufallspartien**, nicht aus echtem Spiel - das ist wahrscheinlich
      der Hauptgrund für den Generalisierungs-Befund oben, hier aber nicht gesondert geprüft (eigener,
      hier nicht gebauter nächster Schritt wäre Training auf Partien der Suche selbst).
    """
)

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
        Statt bis zum Spielende zu rekursieren, bricht die Suche bei Tiefe $d=0$ ab und bewertet die
        Stellung $s$ direkt über eine lineare Bewertungsfunktion:

        $$
        \text{eval}(s) = \sum_{k=1}^{3} w_k \cdot \big(x_k^{\text{Rot}}(s) - x_k^{\text{Gelb}}(s)\big)
        $$

        wobei $x_k^{\text{Farbe}}(s)$ die Zahl der noch offenen Vierer-Fenster mit genau $k$ Steinen dieser
        Farbe zählt. Die Gewichte $w = (w_1, w_2, w_3)$ sind entweder handgewählt oder per kleinste
        Quadrate an bekannten exakten Werten $y_i$ auf einem kleinen, vollständig gelösten Brett
        angepasst: $\min_w \sum_i (w^\top x_i - y_i)^2$, mit $w \geq 0$ (ein offenes eigenes Fenster kann
        die eigene Stellung nie verschlechtern - erzwungen per Domänenwissen, siehe `ev_fit.py`).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning. Interesse an einer maßgeschneiderten Lösung für "
    "Ihr Unternehmen? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html)"
)
