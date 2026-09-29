# Bewertungsfunktionen: schätzen statt bis zum Ende suchen

Kind-Stück von **[minimax-demo](https://github.com/sebastian-hanisch/minimax-demo)** (Wurzel der
Adversarische-Suche-Linie, Wurzel des zweiten Astes "Suchtiefe begrenzen statt mehr durchsuchen"). Vehikel:
dasselbe Mini-Vier-Gewinnt, dasselbe Brettmodell.

## Warum dieses Problem

Bisher hat diese Linie immer bis zum **Spielende** durchgesucht – bewiesen exakt, aber auf großen Brettern
unbezahlbar (selbst mit Alpha-Beta und Transpositionstabelle brauchte 5×5 in transposition-table-demo noch
27,9 Sekunden). Eine **Bewertungsfunktion** bricht die Suche nach wenigen Zügen ab und schätzt die Stellung
stattdessen anhand von Merkmalen – der Preis: die Suche liefert keine bewiesen exakten Werte mehr.

## Modell

Merkmale: für jedes der Länge-4-Fenster (horizontal, vertikal, beide Diagonalen) wird geprüft, ob es noch
von einer Seite gewinnbar ist; die Zahl der eigenen Steine darin (1, 2 oder 3) zählt als "Bedrohungsstufe".
Merkmal je Stufe = (offene Rot-Fenster dieser Stufe) − (offene Gelb-Fenster dieser Stufe). Die
Bewertungsfunktion ist eine lineare Kombination dieser drei Merkmale, mit zwei verschiedenen Gewichtungen:

- **Handgewichtet** (1, 8, 40): stärkere Betonung höherer Bedrohungsstufen, eine übliche, aber nicht an
  Daten geeichte Designentscheidung.
- **Gefittet**: nicht-negative kleinste Quadrate (`scipy.optimize.nnls`) an 4.655 exakt gelösten Stellungen
  aus 5.000 Zufallspartien auf 4×3 (Grundwahrheit über den Alpha-Beta+Tabelle-Löser aus
  transposition-table-demo). Nicht-Negativität ist Absicht: ein zusätzliches offenes eigenes Fenster kann
  die eigene Stellung nie verschlechtern – ein unbeschränkter Fit lieferte in einem ersten Versuch
  unplausible NEGATIVE Gewichte (Artefakt der Zufallspartien-Verteilung).

## Befunde (gemessen, keine Behauptungen)

- **Das echte Standard-Vier-Gewinnt-Brett (6×7) wird spielbar**: Tiefe 6 braucht nur 16.393 Knoten und
  0,25 Sekunden (naive Reihenfolge, kein Move-Ordering, keine Tabelle) – ein Brett, das mit exakter Suche
  praktisch nie fertig würde.
- **Gefittete Gewichte**: `[0.0, 0.0, 0.288]` – die Anpassung verwirft Stufe 1 und 2 komplett und verlässt
  sich nur noch auf Stufe 3.

## Befunde und Korrekturen gegenüber dem Plan

**Ehrlicher, unerwarteter Befund**: erwartet war, dass die gefittete Gewichtung die handgewählte schlägt
("zeigt, dass Handabstimmung suboptimal ist" – ursprüngliche DAG-Scoping-Notiz). Gemessen (Zugübereinstimmung
mit dem exakten Optimalzug, 500 Testpositionen je Zeile):

| Testbrett | Tiefe | Handgewichtet | Gefittet |
|---|---|---|---|
| 4×3 (Trainingsbrett, eigener Testsplit) | 2 | 100,0 % | 100,0 % |
| 4×3 (Trainingsbrett, eigener Testsplit) | 4 | 100,0 % | 100,0 % |
| 3×4 (ungesehen) | 2 | 99,4 % | 97,6 % |
| 3×4 (ungesehen) | 4 | 100,0 % | 97,8 % |

Auf dem eigenen Trainingsbrett sind beide gleich gut – der Unterschied zeigt sich erst auf einem
**ungesehenen** Brett, und dort schneidet die einfache Handgewichtung **besser** ab. Mechanismus: die
kleinste-Quadrate-Anpassung optimiert den quadratischen Fehler beim Vorhersagen des exakten Werts – das ist
NICHT dieselbe Zielgröße wie "den richtigen Zug wählen" (nur die relative Reihenfolge der Kandidaten zählt
dafür). Auf den Zufallspartien-Trainingsdaten reicht Stufe 3 allein aus, um den Wert gut vorherzusagen; die
Handgewichtung nutzt dagegen alle drei Stufen und verallgemeinert dadurch robuster auf eine andere
Brettform. Ein Lehrbuchfall dafür, dass das Optimieren einer Proxy-Metrik nicht automatisch die Metrik
verbessert, die eigentlich zählt.

## Ehrliche Grenzen

- **Die Schätzung ist beweisbar NICHT exakt** – anders als in jedem bisherigen Stück dieser Linie keine
  Garantie mehr auf den optimalen Zug.
- **Nur 3 Merkmale, nur linear.** Echte Engines (z. B. NNUE in modernen Schach-Engines) nutzen tausende
  Merkmale und nichtlineare Netze.
- **Die Trainingsdaten stammen aus Zufallspartien**, nicht aus echtem/starkem Spiel – wahrscheinlich der
  Hauptgrund für den Generalisierungs-Befund oben (nicht gesondert nachgewiesen).

## Tests

47 Tests (`pytest tests/ -v`): Brettmechanik, Merkmalsextraktion (von Hand nachvollziehbar, antisymmetrisch
unter Farbtausch), exakter Löser (Kreuzprobe gegen die Vorgängerstücke), Gewichtsanpassung (reproduzierbar,
nicht-negativ), tiefenbegrenzte Suche (Konvergenz gegen den exakten Wert bei voller Tiefe), PDF-Export,
Visualisierung, Streamlit-Rauchtests. Ein echter, unerwarteter Streamlit-Bug beim Bau gefunden+gefixt:
`st.slider(..., max_value=..., key=...)` setzt den Wert still auf das Minimum zurück, sobald sich
`max_value` zwischen zwei Läufen ändert – SELBST wenn der bisherige Wert innerhalb der neuen Grenzen liegt
(reproduziert mit einem Zwei-Zeilen-Repro-Skript, kein Anwendungsfehler, echtes Streamlit-Verhalten). Fix:
ein eigener Suchtiefe-Schlüssel je Brettgröße statt eines gemeinsamen, dessen `max_value` sich nie ändert.

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Einstiegspunkt |
| `ev_constants.py` | Brettgrößen, Gewichte, gemessene Referenzwerte |
| `ev_game.py` | Brettmechanik (Kopie der Vorgängerstücke) |
| `ev_features.py` | Merkmalsextraktion (offene Linien je Bedrohungsstufe) |
| `ev_exact.py` | Exakter Löser (Alpha-Beta+Tabelle) - Grundwahrheit für Trainings-/Testdaten |
| `ev_data.py` | Trainings-/Testdaten aus Zufallspartien |
| `ev_fit.py` | Gewichtsanpassung (nicht-negative kleinste Quadrate) |
| `ev_search.py` | Tiefenbegrenzte Alpha-Beta-Suche mit Bewertungsfunktion |
| `ev_evaluation.py` | Verdikt-Texte, Gewichts-Auswahl |
| `ev_visualization.py` | Plotly-Brett und Vergleichsdiagramme |
| `ev_presets.py` | Presets, Permalink, Session-Defaults |
| `ev_pdf_export.py` | PDF-Export |

## Bewusst nicht umgesetzt

- Training auf Partien der Suche selbst statt Zufallspartien (naheliegender nächster Schritt für den
  Generalisierungs-Befund, hier nicht verfolgt).
- Move-Ordering/Transpositionstabelle in der tiefenbegrenzten Suche (Gegenstand der bereits gebauten
  Geschwisterstücke dieser Linie, hier bewusst nicht kombiniert, um den Fokus auf die Bewertungsfunktion
  zu halten).
- Nichtlineare/größere Bewertungsfunktionen (NNUE-artig) – als SOTA-Verweis erwähnt, nicht gebaut.

## Lokal ausführen

```bash
pip install -r requirements-dev.txt
streamlit run app.py
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und fpdf2.
