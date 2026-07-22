"""
charts.py
---------
Builds matplotlib Figure objects for the Dashboard and Recommendation
screens. Figures are returned (not shown) so the GUI layer can embed them
with FigureCanvasTkAgg.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # safe default; GUI embeds the canvas explicitly
import matplotlib.pyplot as plt

DARK_BG = "#1a1a1a"
LIGHT_BG = "#ffffff"
ACCENT = "#2fa572"
ACCENT2 = "#e6a23c"


def _style_axes(ax, dark: bool) -> None:
    bg = DARK_BG if dark else LIGHT_BG
    fg = "#eaeaea" if dark else "#222222"
    ax.set_facecolor(bg)
    ax.figure.set_facecolor(bg)
    ax.tick_params(colors=fg, labelsize=8)
    ax.xaxis.label.set_color(fg)
    ax.yaxis.label.set_color(fg)
    ax.title.set_color(fg)
    for spine in ax.spines.values():
        spine.set_color(fg)


def bar_chart(labels: list[str], values: list[float], title: str,
              ylabel: str = "", dark: bool = True):
    fig, ax = plt.subplots(figsize=(4.6, 3.2), dpi=100)
    colors = [ACCENT, ACCENT2, "#5b8def", "#d9534f", "#9b59b6"][:len(labels)]
    if len(labels) > 5:
        colors = (colors * (len(labels) // 5 + 1))[:len(labels)]
    ax.bar(labels, values, color=colors)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    _style_axes(ax, dark)
    fig.tight_layout()
    plt.xticks(rotation=20, ha="right")
    return fig


def pie_chart(labels: list[str], values: list[float], title: str, dark: bool = True):
    fig, ax = plt.subplots(figsize=(4.2, 3.2), dpi=100)
    values = [max(v, 0.0001) for v in values]
    colors = [ACCENT, ACCENT2, "#5b8def", "#d9534f", "#9b59b6", "#8bc34a"][:len(labels)]
    ax.pie(values, labels=labels, autopct="%1.0f%%", colors=colors,
           textprops={"fontsize": 8, "color": "#eaeaea" if dark else "#222222"})
    ax.set_title(title, color="#eaeaea" if dark else "#222222")
    fig.patch.set_facecolor(DARK_BG if dark else LIGHT_BG)
    fig.tight_layout()
    return fig


def line_chart(x_labels: list[str], series: dict[str, list[float]], title: str,
                ylabel: str = "", dark: bool = True):
    fig, ax = plt.subplots(figsize=(5.2, 3.2), dpi=100)
    colors = [ACCENT, ACCENT2, "#5b8def", "#d9534f"]
    for i, (name, values) in enumerate(series.items()):
        ax.plot(x_labels, values, marker="o", label=name, color=colors[i % len(colors)])
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=7, facecolor=DARK_BG if dark else LIGHT_BG,
              labelcolor="#eaeaea" if dark else "#222222")
    _style_axes(ax, dark)
    fig.tight_layout()
    plt.xticks(rotation=20, ha="right")
    return fig
