#!/usr/bin/env python3
"""
make-fed-hike-2026-chart.py  [outdir]

The Fed's September 16, 2026 hike, the lead of the 09/16/26 edition (Harv asked
for it to be the highlight, with a callback to the odds we reported). Emits BOTH:

  fed-hike-091626.png      plain monogram    -> RE email + Agent Hub
  fed-hike-091626-hb.png   + wordmark        -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/16/26
=============================================================================

Decision: federalreserve.gov press release monetary20260916a, 2:00 PM EDT
(11:00 AM PT): "raise the target range for the federal funds rate by 1/4
percentage point to 3-3/4 to 4 percent", vote 12 to 0. Implementation note
(monetary20260916a1): effective September 17, 2026.

History: FRED DFEDTARU / DFEDTARL, every change since December 2021, copied
below. The last increase before today took effect July 27, 2023 (5.25% to
5.50%), so this is the first increase since July 2023. Cuts ran September 2024
to December 2025, from 5.50% down to 3.75% at the top of the range.

Odds we printed (CME FedWatch): 85.6% in the 09/11 edition, 92.3% in the 09/15
edition, 92.7% Wednesday morning (Yahoo Finance live blog, 1:17 PM UTC). The
09/14 edition quoted Kalshi and Polymarket (84.5%), a different source, so it is
not plotted with the CME figures.

matplotlib only; build with python3.13 on Mac.
"""
import os
import sys
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "091626"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
BAND = "#e8a33d"
GRID = "#d8cdb8"
MUTED = "#8a8172"
DEEP = "#b8433a"
BOX = "#f6e7cf"

# (effective date, lower %, upper %) from FRED, plus today's decision.
STEPS = [
    (date(2022, 1, 1), 0.00, 0.25),
    (date(2022, 3, 17), 0.25, 0.50),
    (date(2022, 5, 5), 0.75, 1.00),
    (date(2022, 6, 16), 1.50, 1.75),
    (date(2022, 7, 28), 2.25, 2.50),
    (date(2022, 9, 22), 3.00, 3.25),
    (date(2022, 11, 3), 3.75, 4.00),
    (date(2022, 12, 15), 4.25, 4.50),
    (date(2023, 2, 2), 4.50, 4.75),
    (date(2023, 3, 23), 4.75, 5.00),
    (date(2023, 5, 4), 5.00, 5.25),
    (date(2023, 7, 27), 5.25, 5.50),
    (date(2024, 9, 19), 4.75, 5.00),
    (date(2024, 11, 8), 4.50, 4.75),
    (date(2024, 12, 19), 4.25, 4.50),
    (date(2025, 9, 18), 4.00, 4.25),
    (date(2025, 10, 30), 3.75, 4.00),
    (date(2025, 12, 11), 3.50, 3.75),
    (date(2026, 9, 17), 3.75, 4.00),   # today's decision, effective tomorrow
]
END = date(2026, 12, 31)


def build():
    xs, lo, hi = [], [], []
    for i, (d, l, u) in enumerate(STEPS):
        nxt = STEPS[i + 1][0] if i + 1 < len(STEPS) else END
        xs += [d, nxt]
        lo += [l, l]
        hi += [u, u]

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    ax.fill_between(xs, lo, hi, color=BAND, alpha=0.35, lw=0, zorder=2)
    ax.plot(xs, hi, color=INK, lw=2.2, zorder=3)

    # today's step, highlighted
    hx = [STEPS[-1][0], END]
    ax.fill_between(hx, [3.75, 3.75], [4.00, 4.00], color=CORAL, lw=0, zorder=4)
    ax.plot([STEPS[-1][0]] * 2, [3.50, 4.00], color=CORAL, lw=3, zorder=4)
    ax.annotate("Sept. 16, 2026: up 0.25\nto 3.75% to 4.00%\nFirst increase since July 2023",
                xy=(date(2026, 9, 30), 4.02), xytext=(date(2025, 11, 20), 5.55),
                fontsize=13.5, fontweight="bold", color=DEEP, ha="center", va="bottom",
                linespacing=1.35,
                arrowprops=dict(arrowstyle="->", color=DEEP, lw=1.6))

    ax.text(date(2023, 12, 1), 5.62, "Last hike: July 2023, to 5.25% to 5.50%",
            fontsize=12, color=INK, ha="center", va="bottom")
    ax.text(date(2025, 3, 1), 3.35, "Cuts from Sept. 2024\nto Dec. 2025",
            fontsize=12, color=MUTED, ha="center", va="top", linespacing=1.3)

    ax.text(date(2023, 10, 1), 2.3,
            "Hike odds we reported (CME FedWatch)\n"
            "Sept. 11 edition:   85.6%\n"
            "Sept. 15 edition:   92.3%\n"
            "Sept. 16 morning:  92.7%\n"
            "Result: a quarter point hike, 12 to 0",
            fontsize=12.5, color=INK, ha="left", va="top", linespacing=1.6,
            bbox=dict(boxstyle="round,pad=0.7", fc=BOX, ec=GRID))

    ax.set_ylim(0, 6.6)
    ax.set_xlim(date(2022, 1, 1), END)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.tick_params(colors=MUTED, labelsize=12, length=0)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)

    fig.text(0.045, 0.945, "Fed Raises Rates, First Hike Since 2023",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888,
             "Federal funds target range, 2022 to 2026 (shaded band; line is the top of the range)",
             fontsize=14, color=MUTED, ha="left", va="top")
    fig.text(0.045, 0.030,
             "Source: Federal Reserve FOMC statement, September 16, 2026, effective September 17; history from the Federal Reserve via FRED.\n"
             "Odds are CME FedWatch readings as printed in our September 11 and 15 editions and reported the morning of September 16.",
             fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5)

    fig.subplots_adjust(left=0.07, right=0.975, top=0.84, bottom=0.16)
    return fig


if __name__ == "__main__":
    fig = build()
    save_pair(fig, os.path.join(OUTDIR, f"fed-hike-{STAMP}.png"),
              logo=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hb-logo-mark.png"))
