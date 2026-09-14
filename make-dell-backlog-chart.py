#!/usr/bin/env python3
"""
make-dell-backlog-chart.py  [outdir]

Recreates the newsletter graphic "Dell's AI Backlog Nearly Doubled In One
Quarter" for the 09/14/26 edition. Emits BOTH variants:

  dell-backlog-091426.png      plain monogram    -> RE email + Agent Hub
  dell-backlog-091426-hb.png   + wordmark        -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/14/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

The supplied graphic: AI-optimized server backlog $43B (Q4 FY26, Jan 2026),
$51.3B (Q1 FY27, May 2026), $95B (Q2 FY27, Jul 2026). Source Dell Q2 FY27
results, reported Sept. 1, 2026.

ALL THREE VALUES ARE RIGHT, and the quarterly flow ties out:
  Q4 FY26 (reported Feb 26, 2026): entered FY27 with a record $43B backlog;
          Q4 AI orders $34.1B, AI servers shipped $9.5B.
  Q1 FY27 (reported May 28, 2026): orders $24.4B, AI server revenue $16.1B,
          backlog $51.3B.  43.0 + 24.4 - 16.1 = 51.3, exact.
  Q2 FY27 (reported Sept 1, 2026): orders $60.9B, AI server revenue $16.4B,
          backlog $95.0B.  51.3 + 60.9 - 16.4 = 95.8; Dell reports 95.0.
Quarter ends (Friday nearest month end): Jan 30, May 1, Jul 31, 2026, so the
three bars are evenly spaced 13 week quarters.

FRAMING. "Nearly doubled" is 1.85x (95.0 / 51.3 = +85.2%). The rebuild says
85%, and adds what the original leaves out: WHY it grew. Orders jumped 2.5x
quarter over quarter while shipments held near $16B, so the backlog swelled.
Q2 orders ($60.9B) exceeded Dell's entire quarterly revenue ($47.0B).

matplotlib only; build with python3.13 on Mac.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "091426"

CREAM = "#fdf6e8"
INK = "#1f2933"
GREEN = "#2f8f5b"
DEEPGREEN = "#1f6b43"
DEEP = "#b8433a"
GRID = "#d8cdb8"
MUTED = "#8a8172"

# (quarter, quarter end, backlog $B, orders $B, shipped $B)
QUARTERS = [
    ("Q4 FY26", "Jan 2026", 43.0, 34.1, 9.5),
    ("Q1 FY27", "May 2026", 51.3, 24.4, 16.1),
    ("Q2 FY27", "Jul 2026", 95.0, 60.9, 16.4),
]


def money(v):
    return f"${v:.1f}B"


def build():
    # Flow check: prior backlog + orders - shipped
    assert round(QUARTERS[0][2] + QUARTERS[1][3] - QUARTERS[1][4], 1) == QUARTERS[1][2]
    assert round(QUARTERS[2][2] / QUARTERS[1][2] - 1, 3) == 0.852

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    xs = range(len(QUARTERS))
    for x, (q, end, backlog, orders, shipped) in zip(xs, QUARTERS):
        col = DEEPGREEN if x == len(QUARTERS) - 1 else GREEN
        ax.bar(x, backlog, width=0.56, color=col, zorder=2)
        ax.text(x, backlog + 3.0, money(backlog).replace(".0B", "B"),
                ha="center", va="bottom", fontsize=30, fontweight="bold", color=INK)
        ax.text(x, 3.2, f"Booked {money(orders)}\nShipped {money(shipped)}",
                ha="center", va="bottom", fontsize=12.5, color="white",
                linespacing=1.45, fontweight="bold")
        ax.text(x, -5.5, q, ha="center", va="top", fontsize=16,
                fontweight="bold", color=INK)
        ax.text(x, -12.5, end, ha="center", va="top", fontsize=13, color=MUTED)

    ax.axhline(0, color=GRID, linewidth=2, zorder=3)
    ax.set_xlim(-0.55, 2.55)
    ax.set_ylim(0, 116)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)

    # Every "$" in figure text is escaped: two unescaped dollar signs in one
    # string turn the span between them into mathtext (hit on the first render).
    ax.text(-0.42, 101,
            "Q2 orders: \\$60.9B, more than Dell's entire \\$47.0B\n"
            "of quarterly revenue. Shipments: \\$16.4B, about the\n"
            "same as Q1. Orders outran shipping, so the backlog grew.",
            fontsize=12.5, color=INK, ha="left", va="top", linespacing=1.55,
            bbox=dict(boxstyle="round,pad=0.7", fc="#f6e7cf", ec=GRID))

    fig.text(0.045, 0.945, "Dell's AI Backlog Jumped 85% In One Quarter",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888,
             "AI-optimized server backlog at fiscal quarter end: orders booked but not yet shipped",
             fontsize=14, color=MUTED, ha="left", va="top")

    fig.text(
        0.045, 0.100,
        "Dell now expects \\$74 billion of AI server revenue this fiscal year, up from \\$60 billion three months ago.",
        fontsize=11.5, color=DEEP, ha="left", va="bottom",
    )
    fig.text(
        0.045, 0.040,
        "Source: Dell Technologies results for fiscal Q4 2026 (reported Feb. 26, 2026), Q1 2027 (May 28, 2026) and Q2 2027 (Sept. 1, 2026).",
        fontsize=10.5, color=MUTED, ha="left", va="bottom",
    )

    fig.subplots_adjust(left=0.05, right=0.975, top=0.83, bottom=0.235)
    return fig


if __name__ == "__main__":
    fig = build()
    save_pair(fig, os.path.join(OUTDIR, f"dell-backlog-{STAMP}.png"),
              logo=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hb-logo-mark.png"))
