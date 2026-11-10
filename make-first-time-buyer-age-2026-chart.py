"""
make-first-time-buyer-age-2026-chart.py  DATA_DIR  [outdir]

The 11/10/26 daily's Real Estate chart. Harv supplied a newsletter graphic ("First-Time
Homebuyers Hit 40": bars for 1991 28, 2020 33, 2022 36, 2024 38, 2026 40; source NAR
Profile of Home Buyers and Sellers). Recreated as OUR chart from NAR's own series.

Emits BOTH:
  first-time-buyer-age-111026.png      plain HB monogram    -> RE email + Agent Hub
  first-time-buyer-age-111026-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR/data.json["nar_first_time_buyer_median_age"] is the full 1981 to 2026 series read
from the data behind NAR's own chart ("Median Age of First-Time Home Buyers, 1981-2026",
the Flourish story embedded in "Top 10 Takeaways from NAR's 2026 Profile of Home Buyers
and Sellers"), 11/10/26.

=============================================================================
VERIFICATION 11/10/26
=============================================================================
* Every bar in the supplied graphic matches NAR: 1991 28, 2020 33, 2022 36, 2024 38, 2026 40.
* FRAMING FIX: the graphic's "Hit 40" in 2026 skips 2025, which was ALSO 40. NAR's text:
  the median "remained at the all-time high seen in last year's report of 40 years old".
  So this chart shows the whole series, and the headline says "for a second year".
* NAR: "Since 2010, the age of first-time buyers has been incrementally climbing from 30."
  2010 = 30 in the series (asserted). 1991 = 28 is the series low (asserted).
* Survey years are uneven before 2003 (1981, 1985, 1987, 1989, 1991, ... 2000, 2002); the
  line connects the surveys NAR published, plotted on a true year axis.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "111026"

CREAM = "#fdf6e8"
INK = "#1f2933"
GREEN = "#2e8b57"
SAND = "#b89a63"
GRID = "#e6dcc8"
MUTED = "#8a8172"
ORANGE = "#ea580c"


def load():
    s = json.load(open(os.path.join(DATA, "data.json")))["nar_first_time_buyer_median_age"]["series"]
    pts = sorted((int(y), int(v)) for y, v in s.items())
    d = dict(pts)
    assert (d[1991], d[2020], d[2022], d[2024], d[2026]) == (28, 33, 36, 38, 40), d
    assert d[2025] == 40 and d[1981] == 29 and d[2010] == 30, d
    assert min(d.values()) == 28 and max(d.values()) == 40, d
    assert len(pts) == 34, len(pts)
    return pts


def build():
    pts = load()
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.07, 0.15, 0.86, 0.62])
    ax.set_facecolor(CREAM)

    ax.fill_between(xs, 20, ys, color=SAND, alpha=0.18, zorder=1, lw=0)
    ax.plot(xs, ys, color=SAND, lw=3.2, zorder=3, solid_joinstyle="round")
    ax.plot([2024, 2025, 2026], [38, 40, 40], color=GREEN, lw=4.2, zorder=4, solid_capstyle="round")

    marks = {1981: (29, "29", "first survey", 0), 1991: (28, "28", "the low", 0),
             2010: (30, "30", "", 0), 2020: (33, "33", "", 0), 2022: (36, "36", "", 0),
             2024: (38, "38", "", 0), 2025: (40, "40", "", 0), 2026: (40, "40", "", 0)}
    for x, (y, lab, note, _) in marks.items():
        recent = x >= 2024
        ax.scatter([x], [y], s=70 if recent else 48, color=GREEN if recent else INK, zorder=5,
                   edgecolor=CREAM, linewidth=1.5)
        dy = 1.0 if x not in (1991,) else -1.25
        va = "bottom" if dy > 0 else "top"
        if x == 2025:
            continue
        if x == 2024:
            ax.text(x - 0.5, y + 0.2, "38", ha="right", va="center", fontsize=18, fontweight="bold", color=GREEN, zorder=6)
            continue
        txt = lab if x != 2026 else "40"
        ax.text(x, y + dy, txt, ha="center", va=va, fontsize=18 if recent else 14,
                fontweight="bold", color=GREEN if recent else INK, zorder=6)
        if note:
            ax.text(x, y + dy + (1.25 if dy > 0 else -1.4), note, ha="center", va=va, fontsize=11.5,
                    color=MUTED)
    ax.text(2025.5, 42.6, "40 in 2025\nand 2026", ha="center", va="bottom", fontsize=13,
            color=GREEN, fontweight="bold", linespacing=1.15)

    for yv in (25, 30, 35, 40):
        ax.axhline(yv, color=GRID, lw=1, zorder=0)
        ax.text(1979.2, yv, str(yv), ha="right", va="center", fontsize=12, color=MUTED)
    for xv in (1981, 1990, 2000, 2010, 2020, 2026):
        ax.text(xv, 23.3, str(xv), ha="center", va="top", fontsize=13, color=INK,
                fontweight="bold" if xv == 2026 else "normal")
    ax.set_xlim(1979.5, 2028)
    ax.set_ylim(23.5, 46)
    ax.axis("off")

    fig.text(0.035, 0.955, "First-Time Buyers Are 40 For A Second Straight Year", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.897, "Median age of first-time U.S. home buyers, 1981 to 2026 (record high, unchanged from 2025)",
             fontsize=14, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.03, "Source: National Association of REALTORS, 2026 Profile of Home Buyers and Sellers "
             "(median age of first-time home buyers, 1981 to 2026). Surveys were not annual before 2002.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"first-time-buyer-age-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
