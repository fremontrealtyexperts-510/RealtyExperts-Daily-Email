#!/usr/bin/env python3
"""
make-older-owners-local-chart.py  B25007_JSON  [outdir]

The 11/24/26 daily's local companion to the Fed generation chart (Harv's "Who
Owns America's Real Estate?" graphic; the Market Briefs "Silver Tsunami" story).
KEEP IT LOCAL: the Fed's DFA has no city detail, so this asks the local question
with the Census Bureau instead: of the owner-occupied homes in each city, what
share have a householder 55 to 64, and 65 or older?

It counts HOMES (households), not dollars, so it is a different measure from the
Fed chart and the copy must say so.

Data: ACS 5-year 2020-2024 (ACSDT5Y2024), table B25007 Tenure by Age of
Householder, owner-occupied lines _002 (total), _007/_008 (55-59, 60-64),
_009/_010/_011 (65-74, 75-84, 85+), via the keyless data.census.gov table API.
Newark has no 1-year estimate and the widest margin of error (65+ owners
2,418 +/- about 300 of 10,584), noted on the chart.

Emits BOTH:
  older-owners-local-112426.png      plain HB monogram    -> RE email + Agent Hub
  older-owners-local-112426-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app
"""
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

SRC = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "112426"

CREAM = "#fdf6e8"
INK = "#1f2933"
GRID = "#e6dcc8"
MUTED = "#8a8172"
CORAL = "#e2574c"
PEACH = "#f4b59f"
SAND = "#b8a98a"
SANDL = "#e2d7bf"

CITIES = ["Union City", "Hayward", "Milpitas", "Fremont", "Newark"]
REFS = [("Alameda County", "Alameda County"), ("California", "California"), ("US", "United States")]
# (65+, 55-64, 55+) at printed precision
EXPECT = {"Union City": ("31.6", "25.0", "56.6"), "Hayward": ("30.3", "22.8", "53.1"),
          "Milpitas": ("26.5", "21.5", "48.0"), "Fremont": ("25.9", "22.4", "48.3"),
          "Newark": ("22.8", "25.9", "48.8"), "Alameda County": ("30.5", "21.4", "51.9"),
          "California": ("33.8", "22.4", "56.1"), "US": ("33.0", "21.6", "54.7")}
EXPECT_FIVE = (31671, 58195)   # five city owner homes with a householder 65+, and 55+


def r1(x):
    return Decimal(str(x)).quantize(Decimal("0.1"), ROUND_HALF_UP)


def bands(v):
    o = v["own"]
    s65 = (v["65_74"] + v["75_84"] + v["85p"]) / o * 100
    s55 = (v["55_59"] + v["60_64"]) / o * 100
    return s65, s55


def build():
    d = json.load(open(SRC))["ACSDT5Y2024"]
    for k, (a, b, c) in EXPECT.items():
        s65, s55 = bands(d[k])
        assert (str(r1(s65)), str(r1(s55)), str(r1(s65 + s55))) == (a, b, c), (k, s65, s55)
    n65 = sum(d[c]["65_74"] + d[c]["75_84"] + d[c]["85p"] for c in CITIES)
    n55 = n65 + sum(d[c]["55_59"] + d[c]["60_64"] for c in CITIES)
    own = sum(d[c]["own"] for c in CITIES)
    assert (int(n65), int(n55)) == EXPECT_FIVE, (n65, n55)

    rows = [(c, *bands(d[c]), True) for c in CITIES] + [(lab, *bands(d[k]), False) for k, lab in REFS]

    fig = plt.figure(figsize=(14.0, 7.9), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.17, 0.15, 0.56, 0.66])
    ax.set_facecolor(CREAM)
    n = len(rows)
    ys = []
    for i, (name, s65, s55, local) in enumerate(rows):
        y = n - 1 - i - (0.55 if not local else 0)
        ys.append(y)
        c1, c2 = (CORAL, PEACH) if local else (SAND, SANDL)
        ax.barh(y, s65, height=0.62, color=c1, zorder=3)
        ax.barh(y, s55, left=s65, height=0.62, color=c2, zorder=3)
        ax.text(s65 - 0.8, y, f"{r1(s65)}%", va="center", ha="right", fontsize=13.5, fontweight="bold",
                color=CREAM if local else INK)
        ax.text(s65 + s55 + 0.9, y, f"{r1(s65 + s55)}%", va="center", ha="left", fontsize=15, fontweight="bold",
                color=INK if local else MUTED)
        ax.text(-1.0, y, name, va="center", ha="right", fontsize=15, fontweight="bold" if local else "normal",
                color=INK if local else MUTED)
    ax.set_xlim(0, 66)
    ax.set_ylim(min(ys) - 0.6, max(ys) + 0.6)
    ax.set_yticks([])
    ax.set_xticks([0, 10, 20, 30, 40, 50, 60])
    ax.set_xticklabels(["0", "10%", "20%", "30%", "40%", "50%", "60%"], fontsize=12, color=MUTED)
    ax.tick_params(length=0, pad=8)
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.legend(handles=[Patch(color=CORAL, label="Householder 65 or older"), Patch(color=PEACH, label="55 to 64"),
                       Patch(color=CREAM, label="Right: 55 or older, total")],
              loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=3, frameon=False, fontsize=12.5,
              handlelength=1.4, columnspacing=1.6)

    fig.text(0.765, 0.70, f"{int(round(n65, -2)):,}", fontsize=40, fontweight="bold", color=CORAL, ha="left",
             va="center")
    fig.text(0.77, 0.625, "owner-occupied homes in the\nfive cities have a householder\n65 or older",
             fontsize=13.5, color=INK, ha="left", va="top", linespacing=1.4)
    fig.text(0.77, 0.44, f"About {int(round(n55, -3)):,} of the {int(round(own, -3)):,}\nhave one 55 or older",
             fontsize=13.5, color=MUTED, ha="left", va="top", linespacing=1.4)

    fig.text(0.035, 0.955, "Who Owns the Homes Here", fontsize=26, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.897, "Share of owner-occupied homes by age of the householder, 2020 to 2024 average",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.022, "Census Bureau, American Community Survey 5-year estimates, table B25007. Counts homes, "
             "not dollars. Newark's estimate has the widest margin of error.\nSource: U.S. Census Bureau.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.45)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"older-owners-local-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    print("wrote", out)
