#!/usr/bin/env python3
"""
make-10yr-19yrhigh-chart.py  [outdir] [treasury_rows.csv]

REALTY EXPERTS recreation of the "Treasury Yields Hit a 19-Year High" graphic
for the 09/24/26 daily email. OUR OWN branded chart, not the source image.

(Named to avoid clobbering the older make-10yr-2026-chart.py.)

VERIFIED against the U.S. Treasury daily par yield curve, 10 Yr column:

  * Month ends January to August match the supplied graphic exactly:
    4.26, 3.97, 4.30, 4.40, 4.45, 4.44, 4.75, 4.75.
  * The last point did NOT. The graphic shows 5.10% for September 23; the
    Treasury curve close is 5.11%. Treasury wins on the 10-Year, so the rise
    from February's 3.97% low is 114 basis points, not 113.
  * "19-year high" holds. The last close at or above 5.11% was July 13, 2007.
    The highest close between August 2007 and this month was 4.98% on
    October 19, 2023, drawn here as a dashed reference so the claim is visible.

Input rows are "month,MM/DD/YYYY,yield" as written by the Treasury month
queries; duplicates are dropped and every plotted value is read from the file.

matplotlib only; build with python3.13 on Mac.
"""
import csv
import os
import sys
from collections import OrderedDict
from datetime import datetime
from decimal import Decimal

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
SRC = sys.argv[2] if len(sys.argv) > 2 else "/tmp/t10_2026.csv"
STAMP = "092426"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
SLATE = "#8a9aa8"
MUTED = "#8a8172"
GRID = "#d8cdb8"

PEAK_2023 = Decimal("4.98")   # 10/19/2023, Treasury curve, verified 09/24/26


def load():
    seen = {}
    for r in csv.reader(open(SRC)):
        if len(r) != 3 or not r[2]:
            continue
        try:
            d = datetime.strptime(r[1], "%m/%d/%Y")
        except ValueError:
            continue
        if d.year == 2026:
            seen[d] = Decimal(r[2])
    me = OrderedDict()
    for d in sorted(seen):
        me[d.month] = (d, seen[d])
    return list(me.values())


def build(points):
    labels = [d.strftime("%b") for d, _ in points]
    labels[-1] = points[-1][0].strftime("%b %-d")
    ys = [float(y) for _, y in points]
    lo_i = min(range(len(ys)), key=lambda i: ys[i])
    last = points[-1][1]
    low = points[lo_i][1]
    bp = int((last - low) * 100)

    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    fig.text(0.062, 0.925, "Treasury Yields Hit a 19-Year High",
             fontsize=30, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.062, 0.858,
             f"U.S. 10-year Treasury yield at each month end of 2026, up {bp} "
             f"basis points from February's low",
             fontsize=14.5, color=MUTED, ha="left", va="top")

    ax = fig.add_axes((0.105, 0.2, 0.83, 0.555))
    ax.set_facecolor(CREAM)
    xs = list(range(len(ys)))
    ax.fill_between(xs, ys, 3.7, color=CORAL, alpha=0.10, zorder=1)
    ax.plot(xs, ys, color=CORAL, linewidth=3.2, zorder=3)
    ax.scatter(xs, ys, s=70, color=CREAM, edgecolor=CORAL, linewidth=2.6, zorder=4)

    ax.axhline(float(PEAK_2023), color=SLATE, linestyle=(0, (5, 4)), linewidth=1.6,
               zorder=2)
    ax.text(0.15, float(PEAK_2023) + 0.03, f"October 2023 peak, {PEAK_2023}%",
            fontsize=12, fontweight="bold", color=SLATE, ha="left", va="bottom")

    ax.annotate(f"{low}%", (lo_i, ys[lo_i]), xytext=(16, -4),
                textcoords="offset points", ha="left", va="center", fontsize=16,
                fontweight="bold", color="white",
                bbox=dict(boxstyle="round,pad=0.4", fc=SLATE, ec="none"))
    ax.annotate(f"{last}%", (xs[-1], ys[-1]), xytext=(-8, 20),
                textcoords="offset points", ha="right", va="bottom", fontsize=20,
                fontweight="bold", color="white",
                bbox=dict(boxstyle="round,pad=0.4", fc=DEEP, ec="none"))

    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=14, fontweight="bold", color=INK)
    ax.set_ylim(3.7, 5.45)
    ax.set_yticks([4.0, 4.5])
    ax.set_yticklabels(["4.00%", "4.50%"], fontsize=12.5, color=MUTED)
    ax.set_xlim(-0.4, len(xs) - 0.6)
    ax.grid(axis="y", color=GRID, linewidth=1, zorder=0)
    ax.tick_params(length=0, pad=8)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)

    fig.text(0.062, 0.1,
             "The highest close since July 13, 2007, the last time the 10-year "
             "finished at 5.11% or more. September is the latest close, not a month end.",
             fontsize=11.5, color=MUTED, ha="left", va="top")
    fig.text(0.062, 0.035,
             "Source: U.S. Treasury Daily Par Yield Curve Rates, 10 year, through "
             "September 23, 2026.",
             fontsize=10.5, color=MUTED, ha="left", va="bottom")
    return fig, bp


if __name__ == "__main__":
    pts = load()
    for d, y in pts:
        print(f"  {d:%m/%d/%Y} {y}%")
    fig, bp = build(pts)
    print(f"  rise from low: {bp} bp")
    save_pair(fig, os.path.join(OUTDIR, f"treasury-10yr-high-{STAMP}.png"),
              facecolor=CREAM)
