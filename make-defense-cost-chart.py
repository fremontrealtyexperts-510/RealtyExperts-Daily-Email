#!/usr/bin/env python3
"""
make-defense-cost-chart.py  [outdir]

Recreates the Market Briefs graphic "The $38 Billion War Tab" for the
09/16/26 edition, neutral wording, all seven CBO categories. Emits BOTH variants:

  defense-cost-091626.png      plain monogram    -> RE email + Agent Hub
  defense-cost-091626-hb.png   + wordmark        -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/16/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

Primary source: CBO letter of September 15, 2026, cbo.gov/publication/62756,
PDF 62756-Iran.pdf, Table 1 ("CBO's Estimate of DoD's Costs ... Through
August 1, 2026, by Category"), total 38.1.

All five supplied bars match CBO exactly (13.1, 10.4, 7.3, 2.7, 1.9). Fixed here:
  * SCOPE. The graphic said "What the U.S. spent". CBO's figure is the added
    cost to the Defense Department only, and munitions and equipment are
    REPLACEMENT costs, not money already spent.
  * MISSING BARS. The five bars sum to 35.4. CBO's other two pieces are
    other operations costs 1.5 and other munitions 1.2; all seven sum to 38.1.
  * PERIOD. Operations began February 28, 2026; the estimate runs to Aug. 1.
  * FUEL. The 2.7 is a fiscal 2026 figure that runs through September 2026.
  * EQUIPMENT. 1.9 is CBO's base case; its alternative is 3.3.
  * Base repair costs: CBO could not estimate them (N.A.).
Munitions parts sum to 21.6 (CBO states 21.7, rounding), 57% of 38.1;
operations and equipment sum to 16.5.

NEUTRAL per Harv 09/16/26: budget facts only, no commentary.

matplotlib only; build with python3.13 on Mac.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "091626"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
SLATE = "#6f8597"
GRID = "#d8cdb8"
MUTED = "#8a8172"
DEEP = "#b8433a"

M, O = "munitions", "operations"
BARS = [  # (label, $ billions, kind)
    ("Missile defense interceptors", 13.1, M),
    ("Increased flying hours", 10.4, O),
    ("Land-attack cruise missiles", 7.3, M),
    ("Increased fuel costs*", 2.7, O),
    ("Equipment lost**", 1.9, O),
    ("Other operations costs", 1.5, O),
    ("Other munitions", 1.2, M),
]
TOTAL = 38.1
MUNITIONS = 21.6  # sum of the three parts; CBO states 21.7 (rounding)


def build():
    assert round(sum(v for _, v, _ in BARS), 1) == TOTAL

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    n = len(BARS)
    for i, (label, v, kind) in enumerate(BARS):
        y = n - 1 - i
        col = CORAL if kind == M else SLATE
        ax.barh(y, v, height=0.62, color=col, zorder=2)
        ax.text(v + 0.18, y, f"\\${v:.1f}B", va="center", ha="left",
                fontsize=17, fontweight="bold", color=INK)
        ax.text(-0.3, y, label, va="center", ha="right", fontsize=14, color=INK)

    ax.set_xlim(0, 16.2)
    ax.set_ylim(-0.6, n - 0.4)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)

    ax.legend(handles=[
        Patch(color=CORAL, label=f"Replacing munitions: \\${MUNITIONS:.1f}B (57%)"),
        Patch(color=SLATE, label="Operations and equipment: \\$16.5B"),
    ], loc="lower right", frameon=True, facecolor="#f6e7cf", edgecolor=GRID,
        fontsize=13, borderpad=0.8)

    fig.text(0.045, 0.945, "CBO Puts Iran Conflict Cost At \\$38.1 Billion",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888,
             "Estimated added cost to the Defense Department, Feb. 28 to Aug. 1, 2026, by category",
             fontsize=14, color=MUTED, ha="left", va="top")

    fig.text(0.045, 0.118,
             "*Fuel covers fiscal year 2026 through September.   **CBO base case; its higher estimate is \\$3.3B.   "
             "Base repair costs were not estimated.",
             fontsize=11, color=DEEP, ha="left", va="bottom")
    fig.text(0.045, 0.030,
             "Source: Congressional Budget Office, letter dated September 15, 2026, Table 1. Munitions and equipment are replacement costs.\n"
             "Covers Defense Department costs above its regular budget only; CBO rounds its munitions total to \\$21.7B.",
             fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5)

    fig.subplots_adjust(left=0.265, right=0.975, top=0.83, bottom=0.2)
    return fig


if __name__ == "__main__":
    fig = build()
    save_pair(fig, os.path.join(OUTDIR, f"defense-cost-{STAMP}.png"),
              logo=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hb-logo-mark.png"))
