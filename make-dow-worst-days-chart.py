#!/usr/bin/env python3
"""
make-dow-worst-days-chart.py  [outdir]

Recreation of "The Dow's 5 Worst Days Ever" graphic Harv supplied for the
10/19/26 daily (Black Monday, Oct. 19, 1987, was 39 years ago that day). Goes
in the Stocks section. Emits BOTH:

  dow-worst-days-101926.png      plain HB monogram    -> RE email + Agent Hub
  dow-worst-days-101926-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 10/19/26 (every percent recomputed from the two closes below)
=============================================================================
  date          prior close   close       change      graphic
  1987-10-19     2,246.74    1,738.74    -508.00     -22.61%   matches
  2020-03-16    23,185.62   20,188.52  -2,997.10     -12.93%   matches
  1929-10-28       298.97      260.64     -38.33     -12.82%   matches
  1929-10-29       260.64      230.07     -30.57     -11.73%   matches
  2020-03-12    23,553.22   21,200.62  -2,352.60      -9.99%   matches

2020 closes: Yahoo ^DJI daily (1992 on); it also shows no other day since 1992
worse than -9.99% (next: 2008-10-15, -7.87%). 1929 and 1987 closes: the
published all-time list (WSJ market data center and Dow Jones' Highlights/
Lowlights file, as tabled on Wikipedia's list of largest daily changes).
Sixth place is Nov. 6, 1929 (-9.92%), so the top five is stable.
EXCLUDED, like the graphic: Dec. 12, 1914 (-24.39% in Dow Jones' own file) is a
discontinuity from a 1916 index revision; the Dow actually rose 4.4% that day.
Stooq's full history sits behind a bot check and was NOT used.
Perspective line: Monday 10/19/26 Dow close 51,966.03 (CNBC) x 22.61% =
11,749.5, "about 11,750 points".

matplotlib; build with python3.13 on Mac, from this workspace (logo path).
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
STAMP = "101926"
TODAY_CLOSE = Decimal("51966.03")

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e05a47"
DEEP = "#b8432f"
SOFT = "#eda393"
MUTED = "#8a8172"

# (label, year, prior close, close)
DAYS = [
    ("Oct. 19", "1987", "2246.74", "1738.74"),
    ("Mar. 16", "2020", "23185.62", "20188.52"),
    ("Oct. 28", "1929", "298.97", "260.64"),
    ("Oct. 29", "1929", "260.64", "230.07"),
    ("Mar. 12", "2020", "23553.22", "21200.62"),
]
EXPECT = ["-22.61", "-12.93", "-12.82", "-11.73", "-9.99"]


def pct(prev, close):
    p = (Decimal(close) / Decimal(prev) - 1) * 100
    return p.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def fmt(v):
    return f"{Decimal(v):,.2f}"


def build():
    rows = [(lab, yr, prev, close, pct(prev, close)) for lab, yr, prev, close in DAYS]
    assert [str(r[4]) for r in rows] == EXPECT, [r[4] for r in rows]
    pts = (TODAY_CLOSE * Decimal("0.2261")).quantize(Decimal("1"))
    assert pts == 11750, pts

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.20, 0.17, 0.62, 0.58])
    ax.set_facecolor(CREAM)

    n = len(rows)
    ys = list(range(n))[::-1]
    for y, (lab, yr, prev, close, p) in zip(ys, rows):
        top = y == n - 1
        ax.barh(y, float(-p), height=0.66, color=CORAL if top else SOFT, zorder=3)
        ax.text(float(-p) + 0.35, y + 0.07, f"{p}%".replace("-", "−"), fontsize=24 if top else 20,
                fontweight="bold", color=DEEP if top else INK, ha="left", va="center")
        ax.text(float(-p) + 0.35, y - 0.25, f"{fmt(prev)} to {fmt(close)}", fontsize=11.5,
                color=MUTED, ha="left", va="center")
        ax.text(-0.5, y + 0.02, yr, fontsize=24, fontweight="bold", color=INK, ha="right", va="center")
        ax.text(-4.3, y + 0.02, lab, fontsize=14, fontweight="bold", color=MUTED, ha="right", va="center")

    ax.set_xlim(0, 30.5)
    ax.set_ylim(-0.6, n - 0.4)
    ax.axis("off")

    fig.text(0.035, 0.955, "The Dow's Five Worst Days", fontsize=28, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.888, "Largest one-day percentage drops, close to close. Black Monday was "
             "39 years ago today.", fontsize=14, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.838, f"At Monday's close of {TODAY_CLOSE:,.2f}, a 22.61% day would erase "
             f"about {pts:,} points.", fontsize=14.5, color=INK, ha="left", va="top")
    fig.text(0.035, 0.085, "Excludes Dec. 12, 1914, a break from a 1916 index revision (the Dow "
             "actually rose that day). Next worst: Nov. 6, 1929, −9.92%.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    fig.text(0.035, 0.050, "Sources: S&P Dow Jones Indices daily closes (Dow Jones Highlights/Lowlights, "
             "WSJ market data); Yahoo Finance for 2020.", fontsize=10.2, color=MUTED,
             ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"dow-worst-days-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
