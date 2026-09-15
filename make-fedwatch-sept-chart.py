#!/usr/bin/env python3
"""
make-fedwatch-sept-chart.py  [outdir]

Recreates the CME FedWatch screenshot shown in the ClearValue Tax video
"A Major Interest Rate Decision is Coming Wednesday" for the 09/15/26 edition.
Emits BOTH variants:

  fedwatch-091526.png      plain monogram    -> RE email + Agent Hub
  fedwatch-091526-hb.png   + wordmark        -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/15/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

The supplied screenshot: 16 Sep 2026 meeting, current target 350-375,
no change 7.7%, hike to 375-400 92.3%.

  92.3% hike: matches CME FedWatch as reported by Stocktwits, Sept 15, 2026,
              3:31 AM EDT. (Yahoo carried 90.7% on Sept 14; the odds move
              intraday, so the figure is pinned to its date.)
  Target range 3.50% to 3.75%: FRED DFEDTARL / DFEDTARU, Sept 15, 2026.
  Path added here: 48.4% on Aug 11 and 85.6% on Sept 11 (24/7 Wall St.,
  Sept 11, the figure our 09/11 edition used).

The video's "59.4% before the CPI report" could NOT be matched to any source
(CBS put the pre-CPI Thursday reading near 70%), so it is not drawn.

FRAMING. FedWatch is a market price from fed funds futures, not a forecast by
the Fed, and the footer says so.

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
STAMP = "091526"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
SLATE = "#8a9aa8"
DEEP = "#b8433a"
GRID = "#d8cdb8"
MUTED = "#8a8172"

BARS = [  # (label, probability %, colour)
    ("Quarter point hike\nto 3.75% to 4.00%", 92.3, CORAL),
    ("No change\nstays 3.50% to 3.75%", 7.7, SLATE),
]
PATH = [("Aug 11", 48.4), ("Sep 11", 85.6), ("Sep 15", 92.3)]


def build():
    assert round(sum(v for _, v, _ in BARS), 1) == 100.0

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    for y, (label, v, col) in zip([1, 0], BARS):
        ax.barh(y, v, height=0.56, color=col, zorder=2)
        ax.text(v + 1.2, y, f"{v:.1f}%", va="center", ha="left", fontsize=30,
                fontweight="bold", color=INK if col == CORAL else MUTED)
        ax.text(-1.5, y, label, va="center", ha="right", fontsize=15,
                color=INK, linespacing=1.35, fontweight="bold" if col == CORAL else "normal")

    ax.set_xlim(0, 112)
    ax.set_ylim(-0.6, 1.6)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)

    path = "      ".join(f"{d}: {v:.1f}%" for d, v in PATH)
    ax.text(24, 0.0, "How the hike odds moved\n" + path,
            fontsize=13, color=INK, ha="left", va="center", linespacing=1.7,
            bbox=dict(boxstyle="round,pad=0.7", fc="#f6e7cf", ec=GRID))

    fig.text(0.045, 0.945, "Markets Put A Fed Hike At 92%",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888,
             "CME FedWatch probabilities for the Fed's September 16, 2026 decision",
             fontsize=14, color=MUTED, ha="left", va="top")

    fig.text(0.045, 0.100,
             "The Fed's target range is 3.50% to 3.75% today. A hike would lift it to 3.75% to 4.00%.",
             fontsize=11.5, color=DEEP, ha="left", va="bottom")
    fig.text(0.045, 0.030,
             "Source: CME FedWatch as reported September 15, 2026 (Stocktwits); August 11 and September 11 readings via 24/7 Wall St.;\n"
             "target range from the Federal Reserve via FRED. Probabilities are priced from fed funds futures, not a forecast by the Fed.",
             fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5)

    fig.subplots_adjust(left=0.25, right=0.975, top=0.82, bottom=0.22)
    return fig


if __name__ == "__main__":
    fig = build()
    save_pair(fig, os.path.join(OUTDIR, f"fedwatch-{STAMP}.png"),
              logo=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hb-logo-mark.png"))
