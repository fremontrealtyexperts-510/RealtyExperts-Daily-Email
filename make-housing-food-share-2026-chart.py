#!/usr/bin/env python3
"""
make-housing-food-share-2026-chart.py  DATA_DIR  [outdir]

The 11/02/26 daily's Real Estate chart. Harv attached the newsletter's "Housing +
Food Eat Nearly Half of Spending" donut: BLS Consumer Expenditures 2025, shares of
the average household budget, "highest in 15 years". Emits BOTH:

  housing-food-share-110226.png      plain HB monogram    -> RE email + Agent Hub
  housing-food-share-110226-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds bls-cx-all-units.json: BLS public API v1, series CXUHOUSINGLB0101M,
CXUFOODTOTLLB0101M and CXUTOTALEXPLB0101M, 2006 to 2025, fetched Nov. 2, 2026.

=============================================================================
VERIFICATION 11/02/26
=============================================================================
* BLS news release, Oct. 29, 2026: $81,905 total, up 4.3%; housing $27,790, 33.9%.
  All of the graphic's dollars and shares reproduce from the series.
* "Highest in 15 years" holds, and the script tests it rather than trusting it:
  46.91% beats every year from 2011 to 2024. The nearest are 2020 (46.84%, the
  pandemic year) and 2011 (46.80%). 2010 was higher at 47.16%. The small line
  draws that comparison so a reader can see it.
* Market Briefs called groceries the biggest driver, "where spending rose 4.6%".
  4.6% is ALL food. Food at home rose 4.3%. Housing rose 5.8% and shelter 8.0%,
  and housing added $1,524 a year to food's $464, so the copy says housing.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "110226"

CREAM = "#fdf6e8"
INK = "#1f2933"
ORANGE = "#ea580c"
BLUE = "#2563eb"
TAN = "#d8cdb8"
GRID = "#d8cdb8"
MUTED = "#8a8172"


def share(a, b):
    # round ONCE from the raw ratio
    return float((Decimal(a) * 100 / Decimal(b)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def load():
    d = json.load(open(os.path.join(DATA, "bls-cx-all-units.json")))
    hsg, food, tot = (d[k] for k in ("CXUHOUSINGLB0101M", "CXUFOODTOTLLB0101M", "CXUTOTALEXPLB0101M"))
    assert (hsg["2025"], food["2025"], tot["2025"]) == (27790, 10633, 81905)
    assert (share(27790, 81905), share(10633, 81905)) == (33.9, 13.0)
    combo = {int(y): (hsg[y] + food[y]) / tot[y] * 100 for y in tot}
    assert round(combo[2025], 2) == 46.91
    assert all(combo[y] < combo[2025] for y in range(2011, 2025)), "the 15 year claim failed"
    assert combo[2010] > combo[2025]
    return combo


def build():
    combo = load()
    h, f, t = 27790, 10633, 81905
    rest = t - h - f
    assert (share(h + f, t), share(rest, t)) == (46.9, 53.1)

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)

    ax = fig.add_axes([0.035, 0.105, 0.42, 0.72])
    ax.set_aspect("equal")
    ax.pie([h, f, rest], colors=[ORANGE, BLUE, TAN], startangle=90, counterclock=False,
           wedgeprops=dict(width=0.34, edgecolor=CREAM, linewidth=3))
    ax.text(0, 0.07, "46.9%", ha="center", va="center", fontsize=46, fontweight="bold", color=INK)
    ax.text(0, -0.17, "housing + food", ha="center", va="center", fontsize=15, color=MUTED)

    rows = [(ORANGE, "Housing", "$27,790 a year", "33.9%", ORANGE, 0.775),
            (BLUE, "Food", "$10,633 a year", "13.0%", BLUE, 0.655),
            (TAN, "Everything else", "Transportation, health and more", "53.1%", MUTED, 0.535)]
    for col, name, sub, val, vcol, y in rows:
        fig.add_artist(plt.Rectangle((0.495, y - 0.034), 0.022, 0.0376, transform=fig.transFigure,
                                     facecolor=col, edgecolor="none"))
        fig.text(0.53, y + 0.012, name, fontsize=19, fontweight="bold", color=INK, ha="left", va="center")
        fig.text(0.53, y - 0.03, sub.replace("$", "\\$"), fontsize=12.5, color=MUTED, ha="left", va="center")
        fig.text(0.965, y - 0.008, val, fontsize=29, fontweight="bold", color=vcol, ha="right", va="center")

    # draw what "highest in 15 years" is compared against
    yrs = list(range(2010, 2026))
    vals = [combo[y] for y in yrs]
    fig.text(0.495, 0.445, "Housing + food share of spending, 2010 to 2025", fontsize=12.5, color=MUTED,
             ha="left", va="top")
    a2 = fig.add_axes([0.505, 0.125, 0.455, 0.27])
    a2.set_facecolor(CREAM)
    a2.plot(yrs, vals, color=ORANGE, lw=2.6, solid_joinstyle="round", zorder=4)
    a2.scatter([2010, 2020], [combo[2010], combo[2020]], s=48, color=ORANGE, edgecolor=CREAM, linewidth=1.2, zorder=5)
    a2.scatter([2025], [combo[2025]], s=120, color=ORANGE, edgecolor=CREAM, linewidth=1.8, zorder=6)
    for yr, ha, dx, dy in ((2010, "left", 9, 8), (2020, "right", -8, 2), (2025, "right", -12, 10)):
        a2.annotate(f"{yr}: {combo[yr]:.1f}%", xy=(yr, combo[yr]), xytext=(dx, dy), textcoords="offset points",
                    fontsize=12.5, fontweight="bold", color=INK, ha=ha, va="bottom")
    a2.set_xlim(2009.6, 2025.6)
    a2.set_ylim(44.9, 47.9)
    a2.set_xticks([2010, 2015, 2020, 2025])
    a2.set_xticklabels(["2010", "2015", "2020", "2025"], fontsize=11.5, color=MUTED)
    a2.set_yticks([45, 46, 47])
    a2.set_yticklabels(["45%", "46%", "47%"], fontsize=11, color=MUTED)
    a2.tick_params(axis="both", length=0, pad=6)
    a2.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    a2.set_axisbelow(True)
    for sp in a2.spines.values():
        sp.set_visible(False)

    fig.text(0.035, 0.955, "Housing + Food Eat Nearly Half of Spending", fontsize=26, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.895, "Share of the average U.S. household budget in 2025. Highest in 15 years.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035, "Source: U.S. Bureau of Labor Statistics, Consumer Expenditures 2025 (Oct. 29, 2026). "
                           "Average annual spending, all consumer units.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"housing-food-share-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
