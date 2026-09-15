#!/usr/bin/env python3
"""
make-ai-power-chart.py  [outdir]

Recreates the newsletter graphic "AI's $110 Billion Power Bill" (Market
Briefs, 09/15/26; source Moody's Ratings via Bloomberg, Sept 14, 2026) for the
09/15/26 edition. Emits BOTH variants:

  ai-power-091526.png      plain monogram    -> RE email + Agent Hub
  ai-power-091526-hb.png   + wordmark        -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/15/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

Supplied: 45 GW to be built; natural gas 30+ GW (67%); solar + storage ~13 GW
(29%); nuclear restarts <2 GW (<5%).

Moody's as reported (SBS, verbatim; Bloomberg Sept 14 paywalled, Advisor
Perspectives and FA-Mag 403): "45 gigawatts (GW) of new power plants by 2030,
costing 110 billion dollars"; "over 30 GW is expected to come from natural gas
power, with the rest primarily coming from solar energy and energy storage";
"The share of restarted nuclear power plants is projected to not exceed 5%."
Costs: "electricity costs will increase by 25 billion to 30 billion dollars
annually"; data centers "directly shoulder up to 15 billion dollars", "about
30% of the total power plant construction cost". IEA: 426 TWh in 2030, 10% of
U.S. electricity, double the 2025 share.

NOT SOURCEABLE: the graphic's "~13 GW, 29%" for solar and storage. Moody's
gives no figure for it; 13 is 45 minus 30 minus 2, the designer's arithmetic.
Dropped: the rebuild draws gas (over 30 GW) and "the rest" (under 15 GW),
and states the nuclear ceiling in words.

matplotlib only; build with python3.13 on Mac. Every "$" is escaped.
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
ORANGE = "#d9822b"
SUN = "#e9b44c"
DEEP = "#b8433a"
GRID = "#d8cdb8"
MUTED = "#8a8172"

TOTAL_GW = 45
GAS_GW = 30  # "over 30 GW"


def build():
    rest = TOTAL_GW - GAS_GW
    assert rest == 15 and round(GAS_GW / TOTAL_GW * 100) == 67

    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)

    ax = fig.add_axes([0.03, 0.17, 0.42, 0.66])
    ax.set_facecolor(CREAM)
    ax.pie([GAS_GW, rest], colors=[ORANGE, SUN], startangle=90, counterclock=False,
           wedgeprops=dict(width=0.34, edgecolor=CREAM, linewidth=3))
    ax.text(0, 0.10, "45 GW", fontsize=34, fontweight="bold", color=INK, ha="center", va="center")
    ax.text(0, -0.17, "new generation\nby 2030", fontsize=13, color=MUTED, ha="center",
            va="center", linespacing=1.3)
    ax.set_aspect("equal")

    x = 0.50
    rows = [
        (ORANGE, "Natural gas", "More than 30 GW, about two thirds of the build"),
        (SUN, "Everything else", "Under 15 GW, mostly solar and battery storage.\n"
                                 "Nuclear restarts: no more than 5% of the total."),
    ]
    y = 0.76
    for col, head, body in rows:
        fig.patches.append(plt.Rectangle((x, y - 0.012), 0.022, 0.04, color=col,
                                         transform=fig.transFigure, figure=fig))
        fig.text(x + 0.035, y + 0.008, head, fontsize=17, fontweight="bold", color=INK,
                 ha="left", va="center")
        fig.text(x + 0.035, y - 0.045, body, fontsize=13, color=INK, ha="left", va="top",
                 linespacing=1.45)
        y -= 0.20

    fig.text(x, 0.38, "Who pays", fontsize=15, fontweight="bold", color=DEEP, ha="left", va="top")
    fig.text(x, 0.335,
             "\\$110 billion to build. Moody's says it could add \\$25 to \\$30 billion\n"
             "a year to U.S. electricity costs; data centers pay up to \\$15 billion\n"
             "of the build directly, about 30%.",
             fontsize=12.5, color=INK, ha="left", va="top", linespacing=1.5)

    fig.text(0.045, 0.945, "AI's \\$110 Billion Power Bill",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888,
             "New U.S. power generation Moody's says data centers need through 2030",
             fontsize=14, color=MUTED, ha="left", va="top")

    fig.text(0.045, 0.030,
             "Source: Moody's Ratings, September 14, 2026, as reported by Bloomberg and SBS. Demand basis: the IEA's forecast of 426 TWh for U.S.\n"
             "data centers in 2030, 10% of U.S. electricity. Moody's gives no separate gigawatt figure for solar and storage, so none is drawn.",
             fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5)
    return fig


if __name__ == "__main__":
    fig = build()
    save_pair(fig, os.path.join(OUTDIR, f"ai-power-{STAMP}.png"),
              logo=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hb-logo-mark.png"))
