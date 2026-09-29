"""Merkmale für die Bewertungsfunktion: offene Linien je Bedrohungsstufe.

Für jedes der Länge-4-Fenster (horizontal, vertikal, beide Diagonalen) wird
geprüft, ob es noch von EINER Seite gewonnen werden kann (die andere Farbe
kommt darin nicht vor). Ist es das, zählt die Zahl der eigenen Steine darin
als "Bedrohungsstufe" (1, 2 oder 3 - bei 4 wäre die Stellung schon terminal
und würde nie hier ankommen). Das Merkmal je Stufe ist die Differenz
Rot-Fenster minus Gelb-Fenster auf dieser Stufe - symmetrisch zum Spielwert
(Farbtausch dreht das Vorzeichen um), was beide Bewertungen (Hand+Fit) teilen.
"""

from __future__ import annotations

from ev_constants import EMPTY, PLAYER_ONE, PLAYER_TWO
from ev_game import all_windows

N_FEATURES = 3  # Stufe 1, 2, 3

_WINDOW_CACHE: dict[tuple[int, int], list[list[tuple[int, int]]]] = {}


def _windows_for(rows: int, cols: int) -> list[list[tuple[int, int]]]:
    key = (rows, cols)
    if key not in _WINDOW_CACHE:
        _WINDOW_CACHE[key] = all_windows(rows, cols)
    return _WINDOW_CACHE[key]


def feature_vector(board: list[list[int]]) -> list[int]:
    rows, cols = len(board), len(board[0])
    rot_counts = [0, 0, 0, 0]  # Index = Stufe (0 ungenutzt)
    gelb_counts = [0, 0, 0, 0]
    for window in _windows_for(rows, cols):
        values = [board[r][c] for r, c in window]
        has_rot = PLAYER_ONE in values
        has_gelb = PLAYER_TWO in values
        if has_rot and not has_gelb:
            rot_counts[values.count(PLAYER_ONE)] += 1
        elif has_gelb and not has_rot:
            gelb_counts[values.count(PLAYER_TWO)] += 1
        # beide Farben vertreten (blockiert) oder ganz leer -> zählt nirgends
    return [rot_counts[k] - gelb_counts[k] for k in (1, 2, 3)]
