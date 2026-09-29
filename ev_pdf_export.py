"""PDF-Export der aktuellen Positions-Analyse (fpdf2).

`multi_cell(w=0, ...)` lässt den Cursor per Default am RECHTEN statt am linken
Rand stehen - ohne `new_x=LMARGIN` würde ein zweiter `multi_cell`-Aufruf direkt
danach abstürzen (bekannter Bug aus minimax-demo, hier von Anfang an korrekt).
Keine Sonderzeichen wie „…" in PDF-gebundenen Strings (bekannter Bug aus
alpha-beta-demo: fpdf2s Helvetica-Kernschrift crasht daran).
"""

from __future__ import annotations

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from ev_constants import EVAL_LABELS, PLAYER_NAMES
from ev_evaluation import format_de_number, to_move_verdict

_NEXT_LINE = dict(new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def build_pdf(
    rows: int,
    cols: int,
    moves: list[int],
    eval_choice: str,
    depth: int,
    player_to_move: int,
    value: float,
    node_count: int,
    best_column: int,
) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "Bewertungsfunktion - Analyse der aktuellen Stellung", **_NEXT_LINE)

    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Brett: {rows} Zeilen x {cols} Spalten", **_NEXT_LINE)
    move_text = ", ".join(str(m) for m in moves) if moves else "keine (Startstellung)"
    pdf.cell(0, 8, f"Bisherige Züge (Spalten): {move_text}", **_NEXT_LINE)
    pdf.cell(0, 8, f"Bewertungsfunktion: {EVAL_LABELS[eval_choice]}", **_NEXT_LINE)
    pdf.cell(0, 8, f"Suchtiefe: {depth}", **_NEXT_LINE)
    pdf.cell(0, 8, f"Am Zug: {PLAYER_NAMES[player_to_move]}", **_NEXT_LINE)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Ergebnis der Suche", **_NEXT_LINE)
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(0, 8, to_move_verdict(value, player_to_move), **_NEXT_LINE)
    pdf.cell(0, 8, f"Geschätzter Wert: {format_de_number(value, 2)}", **_NEXT_LINE)
    pdf.cell(0, 8, f"Durchsuchte Knoten: {format_de_number(node_count)}", **_NEXT_LINE)
    pdf.cell(0, 8, f"Gewählte Spalte: {best_column}", **_NEXT_LINE)

    return bytes(pdf.output())
