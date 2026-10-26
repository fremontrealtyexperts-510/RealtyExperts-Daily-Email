#!/usr/bin/env python3
"""
make-datacenter-pushback-2026-chart.py  DATA_DIR  [outdir]

The 10/26/26 daily's Real Estate chart. Harv attached the newsletter's "Data
Centers Hit a Wall" graphic: a donut of 146 U.S. projects delayed or canceled,
"~3/4 Local opposition" and "~1/4 Other factors", source "S&P Global Ratings via
Bloomberg (Oct. 2026)". Emits BOTH:

  datacenter-pushback-102626.png      plain HB monogram    -> RE email + Agent Hub
  datacenter-pushback-102626-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

(make-datacenter-chart.py is an OLDER, different chart. Do not confuse the two.)

DATA_DIR holds ij-890280.txt: the text of Bloomberg's Oct. 23, 2026 story "Data
Centers Face Downgrade Risk Amid Local Pushback, S&P Says" as republished by
Insurance Journal on Oct. 26, 2026 (insurancejournal.com/news/national/2026/10/26/
890280.htm; bloomberg.com is bot gated). The script asserts each sentence it
draws from is present in that text.

=============================================================================
VERIFICATION 10/26/26
=============================================================================
* "tracked 146 delayed or canceled projects in the US. About three-quarters of
  them were tied to local pushback." S&P Global Ratings, report dated Oct. 23,
  analysts including Chris Mooney. The graphic's 146 and ~3/4 both hold.
* "About three-quarters" is approximate. The ring is DRAWN at 75% and the
  chart says so; it prints no derived project count (no "about 110").
* Extra facts from the same story: local governments "across 40 states" have
  imposed bans; concerns "include energy costs, water scarcity, air pollution
  and noise pollution"; the impact on credit grades "has so far been minimal".

matplotlib; build with python3.13 on Mac.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "102626"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#d6363c"
SAND = "#e3d6bb"
SANDINK = "#8a7a5c"
MUTED = "#8a8172"

SOURCE_SENTENCES = [
    "tracked 146 delayed or canceled projects in the US.",
    "About three-quarters of them were tied to local pushback.",
    "prompting local governments across 40 states to impose bans, according to the report.",
    "Frequently cited concerns include energy costs, water scarcity, air pollution and noise pollution.",
    "analysts including Chris Mooney wrote in a Oct. 23 report.",
]


def check_source():
    t = open(os.path.join(DATA, "ij-890280.txt"), encoding="utf-8").read()
    for s in SOURCE_SENTENCES:
        assert s in t, f"not in source text: {s}"
    return 146, 0.75, 40


def build():
    projects, local_share, states = check_source()

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)

    # donut, left half
    ax = fig.add_axes([0.05, 0.13, 0.42, 0.68])
    ax.set_facecolor(CREAM)
    ax.pie([local_share, 1 - local_share], colors=[CORAL, SAND], startangle=90,
           counterclock=False, wedgeprops=dict(width=0.30, edgecolor=CREAM, linewidth=3))
    ax.set_aspect("equal")
    ax.text(0, 0.10, f"{projects}", ha="center", va="center", fontsize=60,
            fontweight="bold", color=INK)
    ax.text(0, -0.24, "projects delayed\nor canceled", ha="center", va="center",
            fontsize=15, color=MUTED, linespacing=1.25)

    # right hand legend and stats
    def swatch(y, color):
        fig.patches.append(Rectangle((0.535, y), 0.022, 0.038, transform=fig.transFigure,
                                     facecolor=color, edgecolor="none"))

    swatch(0.665, CORAL)
    fig.text(0.572, 0.705, "About 3/4", fontsize=34, fontweight="bold", color=CORAL,
             ha="left", va="top")
    fig.text(0.572, 0.625, "tied to local pushback", fontsize=17, color=INK,
             ha="left", va="top")

    swatch(0.495, SAND)
    fig.text(0.572, 0.535, "About 1/4", fontsize=34, fontweight="bold", color=SANDINK,
             ha="left", va="top")
    fig.text(0.572, 0.455, "other causes", fontsize=17, color=INK, ha="left", va="top")

    fig.lines.append(plt.Line2D([0.535, 0.93], [0.395, 0.395], transform=fig.transFigure,
                                color="#d8cdb8", lw=1.2))

    fig.text(0.535, 0.365, f"{states} states", fontsize=30, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.535, 0.29, "where local governments have imposed bans", fontsize=15,
             color=MUTED, ha="left", va="top")
    fig.text(0.535, 0.235, "Top concerns: energy costs, water, air pollution, noise",
             fontsize=15, color=MUTED, ha="left", va="top")

    fig.text(0.035, 0.955, "Neighbors Are Stalling Data Centers", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895,
             "U.S. data center projects delayed or canceled, by cause, as tracked by S&P Global Ratings.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.068,
             "S&P puts the local pushback share at about three quarters; the ring is drawn at 75%.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    fig.text(0.035, 0.035,
             "Source: S&P Global Ratings report, Oct. 23, 2026, as reported by Bloomberg.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"datacenter-pushback-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
