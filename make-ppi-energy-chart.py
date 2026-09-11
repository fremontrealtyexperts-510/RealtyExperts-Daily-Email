#!/usr/bin/env python3
"""
make-ppi-energy-chart.py  [outdir]

Recreates the newsletter graphic "Energy Did The Heavy Lifting" for the
09/11/26 edition. (make-ppi-chart.py is an older, different chart; this is a
new file on purpose so neither clobbers the other.) Emits BOTH variants:

  ppi-energy-091126.png      plain monogram    -> RE email + Agent Hub
  ppi-energy-091126-hb.png   + wordmark        -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/11/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

The supplied graphic: producer prices, 12 month change through August 2026,
Energy 24.4%, All wholesale prices 5.4%, Core (ex. food, energy, trade) 4.7%,
Fed's inflation target 2.0%. Source BLS, August 2026 PPI, released Sept 10.

ALL THREE PPI VALUES ARE RIGHT. BLS API, unadjusted index levels, Aug 2026
over Aug 2025:
  WPUFD412   final demand energy                         +24.38%  -> 24.4
  WPUFD4     final demand                                 +5.44%  ->  5.4
  WPUFD49116 final demand less foods, energy and trade    +4.66%  ->  4.7
  WPUFD42    final demand services (added here)           +4.48%  ->  4.5
The release (USDL 26-1495, 8:30 a.m. ET Thursday, September 10, 2026) prints
5.4 and 4.7 verbatim.

FRAMING. "Heavy lifting" is BLS's own story for the MONTH: final demand goods
+1.1% in August, "Over three-fourths of the broad-based rise can be attributed
to prices for final demand energy, which moved up 4.2 percent", and diesel
"jumped 24.1 percent" (seasonally adjusted). It is not the story of the
12 month bars the graphic draws: with food, energy and trade stripped out,
producer prices are still up 4.7%, and services 4.5%. So the rebuild keeps
the four bars, adds services, and says both halves. The Fed's 2% goal is for
consumer prices (PCE), not producer prices, so it is labeled as a yardstick.

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
STAMP = "091126"

CREAM = "#fdf6e8"
INK = "#1f2933"
ORANGE = "#d9822b"
DEEP = "#b8433a"
CORAL = "#e2574c"
SOFT = "#e9b27a"
SLATE = "#8a9aa8"
GRID = "#d8cdb8"
MUTED = "#8a8172"

# (label, 12 month % change through Aug 2026, unadjusted, BLS API to 2 dp, colour)
BARS = [
    ("Energy", "24.38", ORANGE),
    ("All producer prices\n(final demand)", "5.44", CORAL),
    ("Core\n(excluding food, energy, trade)", "4.66", DEEP),
    ("Services", "4.48", DEEP),
    ("Fed's 2% goal\n(for consumer prices)", "2.00", SLATE),
]


def pct(s):
    return Decimal(s).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def build():
    assert [str(pct(v)) for _, v, _ in BARS] == ["24.4", "5.4", "4.7", "4.5", "2.0"]

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    ys = list(range(len(BARS)))[::-1]
    for y, (label, v, col) in zip(ys, BARS):
        val = float(v)
        ax.barh(y, val, height=0.62, color=col, alpha=0.55 if col == SLATE else 1.0, zorder=2)
        ax.text(val + 0.35, y, f"{pct(v)}%", va="center", ha="left",
                fontsize=20, fontweight="bold", color=SLATE if col == SLATE else INK)
        ax.text(-0.5, y, label, va="center", ha="right", fontsize=13.5,
                color=MUTED if col == SLATE else INK, linespacing=1.25)

    ax.axvline(2.0, color=SLATE, linewidth=1.1, linestyle=(0, (5, 4)), zorder=1)
    ax.set_xlim(0, 28.5)
    ax.set_ylim(-0.6, len(BARS) - 0.4)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)

    # The monthly story, which is where "heavy lifting" actually lives.
    ax.text(9.0, 2.15,
            "August alone (seasonally adjusted)\n"
            "Final demand +0.4%   Energy +4.2%   Diesel +24.1%\n"
            "BLS: energy drove over three fourths of\nthe month's rise in goods prices.",
            fontsize=12.5, color=INK, ha="left", va="center", linespacing=1.55,
            bbox=dict(boxstyle="round,pad=0.7", fc="#f6e7cf", ec=GRID))

    fig.text(0.045, 0.945, "Energy Led August. It Is Not the Whole Story.",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888,
             "Producer prices, 12 month change through August 2026",
             fontsize=14, color=MUTED, ha="left", va="top")

    fig.text(
        0.045, 0.118,
        "Energy is up 24.4% in a year, but strip out food, energy and trade and producer prices are still up 4.7%,\n"
        "more than twice the Fed's 2% goal, and the Fed meets next week.",
        fontsize=11.5, color=DEEP, ha="left", va="bottom", linespacing=1.55,
    )
    fig.text(
        0.045, 0.040,
        "Source: U.S. Bureau of Labor Statistics, Producer Price Index for August 2026, released September 10, 2026. 12 month changes\n"
        "are unadjusted. The Fed's 2% target applies to consumer prices (PCE) and is shown for scale.",
        fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5,
    )

    fig.subplots_adjust(left=0.265, right=0.975, top=0.83, bottom=0.21)
    return fig


if __name__ == "__main__":
    fig = build()
    save_pair(fig, os.path.join(OUTDIR, f"ppi-energy-{STAMP}.png"),
              logo=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hb-logo-mark.png"))
