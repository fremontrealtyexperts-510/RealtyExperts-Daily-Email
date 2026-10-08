#!/usr/bin/env python3
"""
make-rent-100k-2026-chart.py  DATA_DIR  [outdir]

The 10/08/26 daily's rent chart (Real Estate section). Harv attached the
newsletter graphic "What $100K Rents Across America" (median square footage on
a $2,500/month budget: Memphis 2,119, Oklahoma City 2,000, Raleigh 1,885,
Houston 1,848, U.S. 1,152, New York 801, San Francisco 729, San Jose 650;
"Source: Zillow Research, Oct. 2026"). Emits BOTH:

  rent-100k-100826.png      plain HB monogram    -> RE email + Agent Hub
  rent-100k-100826-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds zillow-100k-rents-100726.csv, parsed 10/08/26 from the table in
Zillow's release "What $100K rents: A house in Memphis, a one-bedroom apartment
in San Jose" (PR Newswire, Seattle, Oct. 7, 2026): United States plus the 50
largest metros, with median listed rent (Jan. to Aug. 2026) and, for listings
"at the top of a $100,000 household income budget, $2,333-$2,500/month", the
median square footage, median bedrooms, single family share and 1 bedroom or
smaller share.

=============================================================================
VERIFICATION 10/08/26
=============================================================================
All eight bars on the supplied graphic match the release table exactly.
The graphic is a SELECTION, not a ranking: it skips San Antonio (1,874, which
outranks Houston) and San Diego (726), Los Angeles (750) and Boston (758),
which are all tighter than New York (801). This chart ranks honestly: the five
roomiest and five tightest of the 50 metros, plus the U.S. line. Release text,
verbatim: "a household with a combined income of $100,000 has a maximum monthly
budget of about $2,500, compared to roughly $1,450 for the typical renter
household earning $58,000"; San Jose "median list rent is $3,539 ... The
typical affordable unit is just 650 square feet, one bedroom, one bath, with
95% of options being apartments or condos." Fremont, Hayward, Newark and Union
City sit in Zillow's San Francisco metro; Milpitas in San Jose's.

matplotlib only; build with python3.13 on Mac.
"""
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "100826"

CREAM = "#fdf6e8"
INK = "#1f2933"
GREEN = "#2f855a"
BLUE = "#2b6cb0"
CORAL = "#e05a47"
GRID = "#d8cdb8"
MUTED = "#8a8172"

BAY = {"San Francisco", "San Jose"}


def load():
    rows = list(csv.DictReader(open(os.path.join(DATA, "zillow-100k-rents-100726.csv"))))
    assert len(rows) == 51, len(rows)
    us = [r for r in rows if r["metro"] == "United States"][0]
    metros = [r for r in rows if r["metro"] != "United States"]
    by = {r["metro"].split(",")[0]: int(r["median_sqft"]) for r in rows}
    want = {"Memphis": 2119, "Oklahoma City": 2000, "Raleigh": 1885, "Houston": 1848,
            "United States": 1152, "New York": 801, "San Francisco": 729, "San Jose": 650}
    for k, v in want.items():
        assert by[k] == v, (k, by[k])
    metros.sort(key=lambda r: -int(r["median_sqft"]))
    top, bottom = metros[:5], metros[-5:]
    assert [r["metro"].split(",")[0] for r in top] == ["Memphis", "Oklahoma City", "Raleigh", "San Antonio", "Houston"]
    assert bottom[-1]["metro"].startswith("San Jose")
    return top, us, bottom


def label(r):
    beds = int(r["median_bedrooms"])
    return f"{int(r['median_sqft']):,} sq ft, {beds} bed{'s' if beds > 1 else ''}"


def build():
    top, us, bottom = load()
    order = top + [us] + bottom
    names, vals, colors, texts = [], [], [], []
    for r in order:
        n = r["metro"].split(",")[0]
        names.append("U.S. overall" if n == "United States" else n)
        vals.append(int(r["median_sqft"]))
        colors.append(BLUE if r is us else (GREEN if r in top else CORAL))
        texts.append(label(r))

    fig = plt.figure(figsize=(14.0, 8.6), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.205, 0.15, 0.70, 0.66])
    ax.set_facecolor(CREAM)

    ys = []
    y = 0.0
    for i in range(len(order)):
        ys.append(y)
        y -= 1.0
        if i in (4, 5):
            y -= 0.35                                   # breathing room around the U.S. bar
    ax.barh(ys, vals, height=0.72, color=colors, zorder=3)
    for yy, v, c, t in zip(ys, vals, colors, texts):
        ax.text(v + 28, yy, t, fontsize=13, fontweight="bold", color=c, ha="left", va="center", zorder=4)
    ax.set_yticks(ys)
    ax.set_yticklabels(names, fontsize=14, color=INK)
    for tl, n in zip(ax.get_yticklabels(), names):
        if n in BAY or n == "U.S. overall":
            tl.set_fontweight("bold")
    ax.set_xlim(0, 2650)
    ax.set_ylim(ys[-1] - 0.7, ys[0] + 0.7)
    ax.set_xticks([])
    ax.tick_params(axis="y", length=0, pad=10)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # the local read, beside the tight block
    low_y = [yy for yy, c in zip(ys, colors) if c == CORAL]
    ax.text(1360, sum(low_y) / len(low_y), "San Francisco and San Jose:\nonly 5% of these rentals are houses,\nthe rest apartments and condos",
            fontsize=12.5, color=CORAL, ha="left", va="center", linespacing=1.3, zorder=4)

    fig.text(0.035, 0.955, "What a $100K Income Rents", fontsize=26, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.895,
             "Median size of rentals listed at $2,333 to $2,500 a month, the top of a $100,000 household's "
             "budget, 2026",
             fontsize=13.2, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.052,
             "The five roomiest and five tightest of the 50 largest metros. Fremont, Hayward, Newark and Union City "
             "are in Zillow's San Francisco metro; Milpitas is in San Jose's.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    fig.text(0.035, 0.022, "Source: Zillow, \"What $100K rents,\" Oct. 7, 2026 (Zillow rental listings).",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"rent-100k-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
