"""
make-tech-workers-nyc-bayarea-2026-chart.py  DATA_DIR  [outdir]

The 11/10/26 daily's Economy chart. Harv supplied a newsletter graphic ("NYC Passes the
Bay Area in Tech": Bay Area 399.6K -> 375.7K (-6.0%), New York 363.7K -> 394.3K (+8.4%),
2022 vs 2025, source CBRE Scoring Tech Talent 2026). Recreated as OUR chart from CBRE's
own text.

Emits BOTH:
  tech-workers-nyc-bayarea-111026.png      plain HB monogram    -> RE email + Agent Hub
  tech-workers-nyc-bayarea-111026-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR/data.json["cbre_tech_talent"] holds CBRE's sentence from the Scoring Tech Talent
2026 overview (Aug 18, 2026): "The tech talent workforce grew by 30,640 to 394,300 in the
New York Metro and contracted by 23,900 to 375,730 in the San Francisco Bay Area between
2022 and 2025." The press release repeats 394,300 and 375,730.

=============================================================================
VERIFICATION 11/10/26
=============================================================================
* 2022 = 2025 minus the change: New York 363,660, Bay Area 399,630 (asserted). These match
  the graphic's 363.7K and 399.6K, and its +8.4% / -6.0% (asserted).
* Market Briefs printed "Bay Area: 375,730" and "New York: 394,300", same as CBRE.
* CBRE counts tech talent by OCCUPATION across all industries (CBRE: nearly two thirds of
  New York's tech workers are at non-tech employers such as banks and media firms, per MB).

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "111026"

CREAM = "#fdf6e8"
INK = "#1f2933"
GREEN = "#2e8b57"
ORANGE = "#ea580c"
GRID = "#e6dcc8"
MUTED = "#8a8172"


def load():
    c = json.load(open(os.path.join(DATA, "data.json")))["cbre_tech_talent"]
    ny25, bay25 = c["ny_2025"], c["bay_2025"]
    ny22, bay22 = ny25 - c["ny_change"], bay25 - c["bay_change"]
    assert (ny25, bay25, ny22, bay22) == (394300, 375730, 363660, 399630), (ny25, bay25, ny22, bay22)
    nyp, bayp = (ny25 / ny22 - 1) * 100, (bay25 / bay22 - 1) * 100
    assert round(nyp, 1) == 8.4 and round(bayp, 1) == -6.0, (nyp, bayp)
    return ny22, ny25, nyp, bay22, bay25, bayp


def k(v):
    return f"{v / 1000:,.1f}K"


def build():
    ny22, ny25, nyp, bay22, bay25, bayp = load()
    raw = dict(ny22=ny22, ny25=ny25, bay22=bay22, bay25=bay25)
    ny22, ny25, bay22, bay25 = ny22 / 1000, ny25 / 1000, bay22 / 1000, bay25 / 1000   # plot in thousands
    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.05, 0.14, 0.90, 0.64])
    ax.set_facecolor(CREAM)
    X0, X1 = 0.0, 1.0
    for x in (X0, X1):
        ax.plot([x, x], [352, 410], color=GRID, lw=1.5, ls=(0, (4, 4)), zorder=1)
    ax.plot([X0, X1], [bay22, bay25], color=ORANGE, lw=5, zorder=3, solid_capstyle="round")
    ax.plot([X0, X1], [ny22, ny25], color=GREEN, lw=5, zorder=3, solid_capstyle="round")
    for x, y, c in ((X0, bay22, ORANGE), (X1, bay25, ORANGE), (X0, ny22, GREEN), (X1, ny25, GREEN)):
        ax.scatter([x], [y], s=170, color=c, zorder=4, edgecolor=CREAM, linewidth=2)

    # left labels
    ax.text(X0 - 0.04, bay22 + 2.2, "SF Bay Area", ha="right", va="bottom", fontsize=15, color=ORANGE, fontweight="bold")
    ax.text(X0 - 0.04, bay22 + 1.6, k(raw["bay22"]), ha="right", va="top", fontsize=24, color=INK, fontweight="bold")
    ax.text(X0 - 0.04, ny22 + 2.2, "New York Metro", ha="right", va="bottom", fontsize=15, color=GREEN, fontweight="bold")
    ax.text(X0 - 0.04, ny22 + 1.6, k(raw["ny22"]), ha="right", va="top", fontsize=24, color=INK, fontweight="bold")
    # right labels
    ax.text(X1 + 0.04, ny25 + 2.2, "New York Metro", ha="left", va="bottom", fontsize=15, color=GREEN, fontweight="bold")
    ax.text(X1 + 0.04, ny25 + 1.6, f"{k(raw["ny25"])}  (+{nyp:.1f}%)", ha="left", va="top", fontsize=24, color=INK, fontweight="bold")
    ax.text(X1 + 0.04, bay25 + 2.2, "SF Bay Area", ha="left", va="bottom", fontsize=15, color=ORANGE, fontweight="bold")
    ax.text(X1 + 0.04, bay25 + 1.6, f"{k(raw["bay25"])}  ({bayp:.1f}%)", ha="left", va="top", fontsize=24, color=INK, fontweight="bold")
    for x, lab in ((X0, "2022"), (X1, "2025")):
        ax.text(x, 350, lab, ha="center", va="top", fontsize=18, color=INK, fontweight="bold")
    ax.set_xlim(-0.75, 1.85)
    ax.set_ylim(344, 412)
    ax.axis("off")

    fig.text(0.035, 0.955, "New York Passed The Bay Area In Tech Workers", fontsize=26, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.897, "Tech talent jobs by metro, 2022 and 2025: New York added 30,640 while the Bay Area lost 23,900",
             fontsize=14, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.03, "Source: CBRE Research, Scoring Tech Talent 2026 (August 2026). Tech talent counts tech occupations "
             "in every industry, not only tech companies.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"tech-workers-nyc-bayarea-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
