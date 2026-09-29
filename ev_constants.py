"""Regler-Grenzen, feste Annahmen, Farben."""

WIN_LENGTH = 4
EMPTY = 0
PLAYER_ONE = 1  # beginnt immer, entspricht "Rot"
PLAYER_TWO = 2  # "Gelb"

PLAYER_NAMES = {PLAYER_ONE: "Rot", PLAYER_TWO: "Gelb"}
PLAYER_COLOURS = {PLAYER_ONE: "#d62728", PLAYER_TWO: "#f2c744"}
EMPTY_COLOUR = "#e5e5e5"

# Handgewichtung: Stufe-3-Drohungen (ein Feld vor Vollendung) deutlich
# staerker gewichtet als Stufe 1/2 - eine uebliche, aber NICHT an Daten
# geeichte Designentscheidung.
HAND_WEIGHTS = [1.0, 8.0, 40.0]

# Trainingsdaten fuer die gefittete Gewichtung: 5000 Zufallspartien auf 4x3,
# fester Seed (Reproduzierbarkeit), nicht-negative kleinste Quadrate (siehe
# ev_fit.py - die Nicht-Negativitaet ist Absicht: ein eigenes offenes Feld
# kann die eigene Stellung nie verschlechtern, per Domänenwissen erzwungen).
TRAIN_ROWS, TRAIN_COLS = 4, 3
TRAIN_GAMES = 5000
TRAIN_SEED = 1

EVAL_HAND = "hand"
EVAL_FITTED = "fitted"
EVAL_LABELS = {
    EVAL_HAND: "Handgewichtet (1, 8, 40)",
    EVAL_FITTED: "Gefittet (kleinste Quadrate an 4×3-Trainingsdaten)",
}

# Live wählbare Bretter: die zwei kleinen (mit Vergleich zum exakten Wert)
# und das ECHTE Standard-Vier-Gewinnt-Brett (6x7) - mit exakter Suche
# (siehe transposition-table-demo) praktisch nie fertig lösbar, mit
# tiefenbegrenzter Suche + Bewertungsfunktion hier in Sekundenbruchteilen.
BOARD_OPTIONS = [
    {"rows": 4, "cols": 3, "label": "4 Zeilen × 3 Spalten (klein, exakt vergleichbar)", "exact_ok": True, "max_depth": 12},
    {"rows": 3, "cols": 4, "label": "3 Zeilen × 4 Spalten (klein, exakt vergleichbar)", "exact_ok": True, "max_depth": 12},
    {"rows": 6, "cols": 7, "label": "6 × 7 (echtes Standard-Vier-Gewinnt)", "exact_ok": False, "max_depth": 6},
]
DEFAULT_BOARD_INDEX = 0
DEFAULT_DEPTH = 4

# Gemessene Zugübereinstimmungsrate (tools/measure_agreement.py-Äquivalent,
# siehe tests/test_claims.py): tiefenbegrenzte Suche mit HAND_WEIGHTS bzw.
# der gefitteten Gewichtung, verglichen mit dem exakten Optimalzug, auf 500
# zufälligen Testpositionen mit genug freien Feldern für die jeweilige Tiefe.
# EHRLICHER, NICHT erwarteter Befund: auf dem TRAININGSbrett (4x3) sind beide
# gleich gut (100 %) - erst auf dem UNGESEHENEN Brett (3x4) zeigt sich ein
# Unterschied, und dort schneidet die Handgewichtung BESSER ab als die
# gefittete (siehe README "Befunde und Korrekturen gegenüber dem Plan").
MEASURED_AGREEMENT = {
    # (board, depth): {"hand": rate, "fitted": rate, "n": Anzahl Testpositionen}
    ("in_distribution_4x3", 2): {"hand": 1.0, "fitted": 1.0, "n": 553},
    ("in_distribution_4x3", 4): {"hand": 1.0, "fitted": 1.0, "n": 197},
    ("out_of_distribution_3x4", 2): {"hand": 0.994, "fitted": 0.976, "n": 500},
    ("out_of_distribution_3x4", 4): {"hand": 1.0, "fitted": 0.978, "n": 500},
}
