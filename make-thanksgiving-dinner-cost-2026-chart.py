#!/usr/bin/env python3
"""
make-thanksgiving-dinner-cost-2026-chart.py  AFBF_PAGE_HTML  [outdir]

Thanksgiving 2026 greeting email (11/26/26, no market update that day): a light,
festive chart of what a classic Thanksgiving dinner for 10 costs, by region, from
the American Farm Bureau Federation's 41st annual survey. The West (us) is
highlighted. Figures are parsed from AFBF's Market Intel page saved with curl:
  https://www.fb.org/intel/markets/thanksgiving-dinner-cost-ticks-upward-in-2026
and asserted: U.S. $58.63 (up 6% from 2025, $5.86 a person, more than 8% below the
2022 record), Northeast $61.57, West $58.74, Midwest $56.89, South $54.33, the
16 pound turkey $23.68.

Emits BOTH:
  thanksgiving-dinner-cost-112626.png      plain HB monogram    -> RE email + Agent Hub
  thanksgiving-dinner-cost-112626-hb.png   monogram + wordmark  -> Harv's sites
"""
import html
import os
import re
import sys
from decimal import Decimal

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

SRC = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "112626"
CREAM = "#fdf6e8"
INK = "#1f2933"
MUTED = "#8a8172"
GRID = "#e6dcc8"
ORANGE = "#d9822b"
CRAN = "#a3333d"
SAND = "#d8c7a3"


def text():
    s = open(SRC, encoding="utf-8", errors="ignore").read()
    s = re.sub(r"(?is)<(script|style).*?</\1>", "", s)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s)))


def build():
    t = text()
    for frag in ["Thanksgiving dinner for 10 people averages $58.63, up 6% from a year ago",
                 "$5.86 per person", "more than 8% lower than the record high experienced in 2022",
                 "$61.57", "In 2018, AFBF added ham, frozen green beans and russet potatoes", "at $58.74 and $56.89, respectively", "The South's average dinner cost is $54.33"]:
        assert frag in t, frag
    rows = [("Northeast", Decimal("61.57")), ("West", Decimal("58.74")), ("U.S. average", Decimal("58.63")),
            ("Midwest", Decimal("56.89")), ("South", Decimal("54.33"))]

    fig = plt.figure(figsize=(14.0, 7.9), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.20, 0.17, 0.52, 0.61])
    ax.set_facecolor(CREAM)
    n = len(rows)
    for i, (name, v) in enumerate(rows):
        y = n - 1 - i
        col = CRAN if name == "West" else (INK if name == "U.S. average" else ORANGE)
        ax.barh(y, float(v), height=0.62, color=col, zorder=3)
        ax.text(float(v) + 0.6, y, f"${v}", va="center", ha="left", fontsize=19, fontweight="bold",
                color=CRAN if name == "West" else INK)
        lab = "West (that's us)" if name == "West" else name
        ax.text(-1.2, y, lab, va="center", ha="right", fontsize=17,
                fontweight="bold" if name in ("West", "U.S. average") else "normal",
                color=CRAN if name == "West" else INK)
    ax.set_xlim(0, 72)
    ax.set_ylim(-0.6, n - 0.4)
    ax.set_yticks([])
    ax.set_xticks([0, 20, 40, 60])
    ax.set_xticklabels(["$0", "$20", "$40", "$60"], fontsize=12, color=MUTED)
    ax.tick_params(length=0, pad=8)
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.765, 0.70, "$5.86", fontsize=50, fontweight="bold", color=CRAN, ha="left", va="center")
    fig.text(0.77, 0.615, "a person, for a classic\ndinner for 10", fontsize=15, color=INK, ha="left", va="top",
             linespacing=1.4)
    fig.text(0.77, 0.47, "Up 6% from 2025, still\nmore than 8% below\nthe 2022 record", fontsize=13.5, color=INK,
             ha="left", va="top", linespacing=1.45)
    fig.text(0.77, 0.32, "The 16 pound turkey:\n$23.68", fontsize=13.5, color=MUTED, ha="left", va="top",
             linespacing=1.45)

    fig.text(0.035, 0.955, "What Thanksgiving Dinner Costs This Year", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.897, "Classic Thanksgiving dinner for 10 people, 2026, by region", fontsize=14, color=MUTED,
             ha="left", va="top")
    fig.text(0.035, 0.03, "AFBF's 41st annual survey of grocery prices for a classic Thanksgiving dinner for 10, "
             "built around a 16 pound turkey.\nSource: American Farm Bureau Federation.",
             fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.45)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"thanksgiving-dinner-cost-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    print("wrote", out)
