"""Plotly-Figuren: Brett-Darstellung, Tiefe-vs-Wert-Konvergenz,
Zugübereinstimmung (alle Achsen fest, autorange statt expliziter range)."""

from __future__ import annotations

import plotly.graph_objects as go

from ev_constants import EMPTY, EMPTY_COLOUR, PLAYER_COLOURS
from ev_game import winning_line


def board_figure(board, last_move, winner: int | None, best_column: int | None = None) -> go.Figure:
    rows, cols = len(board), len(board[0])
    fig = go.Figure()

    win_cells = set()
    if winner is not None and last_move is not None:
        line = winning_line(board, last_move, winner)
        if line:
            win_cells = set(line)

    xs, ys, colours, line_widths, line_colours = [], [], [], [], []
    for r in range(rows):
        for c in range(cols):
            value = board[r][c]
            xs.append(c)
            ys.append(rows - 1 - r)
            colours.append(EMPTY_COLOUR if value == EMPTY else PLAYER_COLOURS[value])
            if (r, c) in win_cells:
                line_widths.append(4)
                line_colours.append("#1a1a1a")
            else:
                line_widths.append(1)
                line_colours.append("#9a9a9a")

    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="markers",
            marker=dict(size=32, color=colours, line=dict(width=line_widths, color=line_colours)),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    if best_column is not None:
        fig.add_trace(
            go.Scatter(
                x=[best_column],
                y=[rows + 0.35],
                mode="markers",
                marker=dict(size=14, color="#2ca02c", symbol="triangle-down"),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    fig.add_trace(
        go.Scatter(
            x=[-0.7, cols - 0.3],
            y=[-0.7, rows + 0.9],
            mode="markers",
            marker=dict(size=1, color="rgba(0,0,0,0)"),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig.update_xaxes(autorange=True, showgrid=False, zeroline=False, showticklabels=False, fixedrange=True)
    fig.update_yaxes(
        autorange=True,
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        fixedrange=True,
        scaleanchor="x",
        scaleratio=1,
    )
    fig.update_layout(height=min(70 * rows + 140, 620), margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="#f7f7f7")
    return fig


def agreement_figure(measured: dict) -> go.Figure:
    labels = [f"{'im Training' if 'in_distribution' in k[0] else 'ungesehen'}, Tiefe {k[1]}" for k in measured]
    hand = [v["hand"] * 100 for v in measured.values()]
    fitted = [v["fitted"] * 100 for v in measured.values()]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Handgewichtet", x=labels, y=hand, marker_color="#1f77b4"))
    fig.add_trace(go.Bar(name="Gefittet", x=labels, y=fitted, marker_color="#ff7f0e"))
    fig.update_yaxes(title="Zugübereinstimmung mit exaktem Optimalzug (%)", range=[90, 101], fixedrange=True)
    fig.update_xaxes(fixedrange=True)
    fig.update_layout(barmode="group", height=420, margin=dict(l=10, r=10, t=30, b=10))
    return fig
