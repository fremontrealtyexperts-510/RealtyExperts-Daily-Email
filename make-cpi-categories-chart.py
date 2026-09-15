#!/usr/bin/env python3
"""
make-cpi-categories-chart.py  [outdir]

Recreates the "Compared to a year ago... Here's how key categories in the CPI
moved" graphic from the ClearValue Tax video for the 09/15/26 edition. Emits:

  cpi-categories-091526.png      plain monogram    -> RE email + Agent Hub
  cpi-categories-091526-hb.png   + wordmark        -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/15/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

Supplied: Energy 16.3, Gasoline 27.4, Diesel fuel 52.0, Shelter 3.0,
Clothing 3.6, Food 2.7, Transportation 2.4, New vehicles 0.6.

BLS API, unadjusted, Aug 2026 over Aug 2025:
  CUUR0000SA0E    energy                    16.277  -> 16.3  right
  CUUR0000SETB01  gasoline (all types)      27.405  -> 27.4  right
  CUUR0000SEHE01  FUEL OIL                  52.039  -> 52.0  value right, LABEL WRONG
  CUUR0000SETB02  other motor fuel (diesel) 43.964  -> 44.0  (the real diesel line)
  CUUR0000SAH1    shelter                    3.041  ->  3.0  right
  CUUR0000SAA     apparel                    3.609  ->  3.6  right
  CUUR0000SAF1    food                       2.673  ->  2.7  right
  CUUR0000SAS4    TRANSPORTATION SERVICES    2.367  ->  2.4  value right, LABEL narrow
  CUUR0000SAT     transportation (all)       6.158  ->  6.2
  CUUR0000SETA01  new vehicles               0.569  ->  0.6  right
  CUUR0000SA0     all items                  3.397  ->  3.4
The graphic's "Diesel fuel 52.0%" is fuel oil, the home heating oil index;
diesel sits in "other motor fuel", up 44.0%. Its "Transportation 2.4%" is
transportation SERVICES; transportation overall, gasoline included, is 6.2%.
Both are relabeled here and the two real lines are added.

matplotlib only; build with python3.13 on Mac.
"""
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "091526"

CREAM = "#fdf6e8"
INK = "#1f2933"
ORANGE = "#d9822b"
CORAL = "#e2574c"
TEAL = "#2f7d6d"
SLATE = "#8a9aa8"
DEEP = "#b8433a"
GRID = "#d8cdb8"
MUTED = "#8a8172"

# (label, exact 12 month %, colour, note)
ROWS = [
    ("Fuel oil (home heating)", "52.039", CORAL, "the original labels this diesel"),
    ("Other motor fuel, incl. diesel", "43.964", CORAL, "added: the actual diesel line"),
    ("Gasoline", "27.405", CORAL, ""),
    ("Energy index", "16.277", ORANGE, ""),
    ("Transportation, all", "6.158", TEAL, "added: includes gasoline"),
    ("Apparel (clothing)", "3.609", TEAL, ""),
    ("Shelter", "3.041", TEAL, ""),
    ("Food", "2.673", TEAL, ""),
    ("Transportation services", "2.367", TEAL, "the original's \"transportation\""),
    ("New vehicles", "0.569", TEAL, ""),
]


def pct(s):
    return Decimal(s).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def build():
    assert [str(pct(v)) for _, v, _, _ in ROWS] == \
        ["52.0", "44.0", "27.4", "16.3", "6.2", "3.6", "3.0", "2.7", "2.4", "0.6"]

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    ys = list(range(len(ROWS)))[::-1]
    for y, (label, v, col, note) in zip(ys, ROWS):
        val = float(v)
        ax.barh(y, val, height=0.66, color=col, zorder=2)
        ax.text(val + 0.6, y, f"{pct(v)}%", va="center", ha="left", zorder=5,
                fontsize=14, fontweight="bold", color=INK,
                bbox=dict(boxstyle="square,pad=0.1", fc=CREAM, ec="none"))
        ax.text(-0.8, y, label, va="center", ha="right", fontsize=13, color=INK)
        if note and val > 30:
            # Long bars: the note goes inside the bar (outside it ran off the page).
            ax.text(4.5, y, note, va="center", ha="left", fontsize=11.5,
                    color="white", style="italic", zorder=5)
        elif note:
            ax.text(val + 7.0, y, note, va="center", ha="left", fontsize=11,
                    color=MUTED, style="italic")

    ax.axvline(3.397, color=INK, linewidth=1.1, linestyle=(0, (5, 4)), zorder=3)
    ax.text(3.9, len(ROWS) - 0.35, "All items 3.4%", fontsize=11, color=INK,
            ha="left", va="bottom", fontweight="bold")

    ax.set_xlim(0, 66)
    ax.set_ylim(-0.6, len(ROWS) + 0.1)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)

    fig.text(0.045, 0.945, "Energy Is The Outlier In A 3.4% Year",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888, "U.S. consumer prices by category, 12 month % change, August 2026",
             fontsize=14, color=MUTED, ha="left", va="top")

    fig.text(0.045, 0.030,
             "Source: U.S. Bureau of Labor Statistics, Consumer Price Index for August 2026, released September 11, 2026, unadjusted. The 52.0% is\n"
             "fuel oil, not diesel; diesel sits in other motor fuel, up 44.0%. The 2.4% is transportation services; transportation overall is up 6.2%.",
             fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5)

    fig.subplots_adjust(left=0.235, right=0.975, top=0.84, bottom=0.14)
    return fig


if __name__ == "__main__":
    fig = build()
    save_pair(fig, os.path.join(OUTDIR, f"cpi-categories-{STAMP}.png"),
              logo=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hb-logo-mark.png"))
