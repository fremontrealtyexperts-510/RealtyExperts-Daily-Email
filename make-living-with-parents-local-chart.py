#!/usr/bin/env python3
"""
make-living-with-parents-local-chart.py  B09021_JSON  [outdir]

The 11/23/26 daily's Real Estate chart. realtor.com's Nov. 23 Weekly Housing
Outlook led with "The Geography of the Crowded Nest" (18 to 34 year olds
living with their parents; Northeast 36.9%, the highest region, other regions
just below the national rate). National and regional only, so per the KEEP IT
LOCAL rule we chart our five cities from the Census Bureau's own table.

Measure: ACS table B09021 (Living Arrangements of Adults 18 Years and Over by
Age), 18 to 34 years, "Child of householder" divided by all 18 to 34 year
olds. That is: young adults who live in a household headed by a parent. It is
NOT realtor.com's exact series (their Northeast 36.9% vs this table's 37.3%
for 2020 to 2024 and 38.0% for 2025), so their figures are quoted in text only.

Vintage: ACS 5-year 2020 to 2024 (the only release that covers Newark, under
65,000 people), with the 2015 to 2019 5-year as the earlier marker.
B09021_JSON = census_fetch.py output (data.census.gov table API, keyless),
saved 11/23/26.

Emits BOTH:
  living-with-parents-112326.png      plain HB monogram    -> RE email + Agent Hub
  living-with-parents-112326-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

matplotlib only; build with python3.13 on Mac, run from the workspace.
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

SRC = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "112326"

CREAM = "#fdf6e8"
INK = "#1f2933"
GRID = "#e6dcc8"
MUTED = "#8a8172"
CORAL = "#e2574c"
TEAL = "#2a8c82"
SAND = "#cdbf9f"

CITIES = ["Union City", "Hayward", "Newark", "Fremont", "Milpitas"]
REFS = [("California", "California"), ("Alameda County", "Alameda County"), ("US", "United States")]
EXPECT = {"Union City": "48.0", "Hayward": "40.9", "Newark": "38.9", "Fremont": "36.4", "Milpitas": "33.0",
          "California": "39.3", "Alameda County": "33.6", "US": "32.8"}


def r1(x):
    return Decimal(str(x)).quantize(Decimal("0.1"), ROUND_HALF_UP)


def share(row):
    return row["child_of_hh"] / row["age18_34"] * 100


def build():
    d = json.load(open(SRC))
    now, then = d["ACSDT5Y2024"], d["ACSDT5Y2019"]
    for k, v in EXPECT.items():
        assert str(r1(share(now[k]))) == v, (k, share(now[k]))
    rows = [(c, share(now[c]), share(then[c]), CORAL if c == "Fremont" else TEAL) for c in CITIES]
    rows.sort(key=lambda r: -r[1])
    rows += [(lab, share(now[k]), share(then[k]), SAND) for k, lab in REFS]

    fig = plt.figure(figsize=(14.0, 7.9), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.17, 0.15, 0.70, 0.66])
    ax.set_facecolor(CREAM)
    n = len(rows)
    ys = []
    for i, (name, v, old, col) in enumerate(rows):
        y = n - 1 - i - (0.55 if i >= len(CITIES) else 0)   # a small gap before the reference bars
        ys.append(y)
        ax.barh(y, v, height=0.62, color=col, zorder=3)
        ax.plot([old, old], [y - 0.36, y + 0.36], color=INK, lw=2.2, zorder=4)
        ax.text(max(v, old) + 0.8, y, f"{r1(v)}%", va="center", ha="left", fontsize=15, fontweight="bold",
                color=INK if col != SAND else MUTED)
        ax.text(-1.0, y, name, va="center", ha="right", fontsize=15,
                fontweight="bold" if col != SAND else "normal", color=INK if col != SAND else MUTED)
    ax.set_xlim(0, 56)
    ax.set_ylim(min(ys) - 0.6, max(ys) + 0.6)
    ax.set_yticks([])
    ax.set_xticks([0, 10, 20, 30, 40, 50])
    ax.set_xticklabels(["0", "10%", "20%", "30%", "40%", "50%"], fontsize=12, color=MUTED)
    ax.tick_params(length=0, pad=8)
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # legend for the tick marks
    fig.text(0.17, 0.835, "Bar: 2020 to 2024 average", fontsize=12.5, color=INK, ha="left", va="center")
    fig.add_artist(plt.Line2D([0.345, 0.345], [0.822, 0.848], color=INK, lw=2.2, transform=fig.transFigure))
    fig.text(0.352, 0.835, "2015 to 2019 average", fontsize=12.5, color=INK, ha="left", va="center")

    fig.text(0.035, 0.955, "Young Adults Living With a Parent", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.897, "Share of 18 to 34 year olds who live in a household headed by a parent",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.022, "Census Bureau, American Community Survey 5-year estimates, table B09021 "
             "(18 to 34 year olds who are the child of the householder).\nSource: U.S. Census Bureau.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.45)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"living-with-parents-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    print("wrote", out)
