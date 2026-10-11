#!/usr/bin/env python3
"""
make-fed-vs-mortgage-2026-chart.py  DATA_DIR  [outdir]

The 10/11/26 Sunday daily's Economy chart. No supplied graphic: Market Briefs'
Sunday edition ("Dealing debt", Ray Dalio, the Fed's Sept. hike, mortgage math)
gave the theme and Harv asked for helpful pictures of our own. The point: the
30-year mortgage rate does not move one for one with the Fed. Emits BOTH:

  fed-vs-mortgage-101126.png      plain HB monogram    -> RE email + Agent Hub
  fed-vs-mortgage-101126-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds the FRED downloads (fetched Oct. 11, 2026 10:37 AM PT):
  DFEDTARU.csv, DFEDTARL.csv  federal funds target range, upper and lower, daily
  MORTGAGE30US.csv            Freddie Mac PMMS 30-year fixed, weekly (Thursdays)

=============================================================================
VERIFICATION 10/11/26
=============================================================================
Target range changes since 2015 (DFEDTARU): 0.50 Dec. 16, 2015 ... 2.50 Dec.
20, 2018; cuts 2019 to March 16, 2020 (0.25); hikes March 17, 2022 to July 27,
2023 (5.50); cuts Sept. 19, 2024 to Dec. 11, 2025 (3.75); then 4.00 on Sept. 17,
2026, the first hike since July 2023 (Market Briefs: "first time since 2023",
"3.75% to 4%": both right).
Freddie 30-year: 2026 low 5.98% (Feb. 26), latest 7.40% (Oct. 8), up 1.42
points while the Fed's upper bound moved 0.25 (3.75 to 4.00).

matplotlib; build with python3.13 on Mac.
"""
import csv
import os
import sys
from datetime import date, datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "101126"
START = date(2015, 1, 1)

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e05a47"
DEEP = "#b8432f"
BLUE = "#2b6cb0"
BLUE_D = "#1e4e8c"
BAND = "#c9daee"
GRID = "#d8cdb8"
MUTED = "#8a8172"


def series(name):
    out = []
    with open(os.path.join(DATA, f"{name}.csv")) as f:
        for row in list(csv.reader(f))[1:]:
            if row[1] in ("", "."):
                continue
            d = datetime.strptime(row[0], "%Y-%m-%d").date()
            if d >= START:
                out.append((d, float(row[1])))
    return out


def build():
    up = series("DFEDTARU")
    lo = dict(series("DFEDTARL"))
    mort = series("MORTGAGE30US")

    assert up[-1][1] == 4.00 and lo[up[-1][0]] == 3.75, up[-1]
    hike = next(d for d, v in up if d >= date(2026, 1, 1) and v == 4.00)
    assert hike == date(2026, 9, 17), hike
    y26 = [p for p in mort if p[0].year == 2026]
    low26 = min(y26, key=lambda p: p[1])
    last = mort[-1]
    assert low26 == (date(2026, 2, 26), 5.98), low26
    assert last == (date(2026, 10, 8), 7.40), last
    rise = round(last[1] - low26[1], 2)
    assert rise == 1.42

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.065, 0.16, 0.80, 0.63])
    ax.set_facecolor(CREAM)

    ud = [d for d, _ in up]
    ax.fill_between(ud, [lo[d] for d in ud], [v for _, v in up], step="post",
                    color=BAND, lw=0, zorder=2)
    ax.step(ud, [v for _, v in up], where="post", color=BLUE, lw=2.0, zorder=3)
    ax.plot([d for d, _ in mort], [v for _, v in mort], color=CORAL, lw=2.6,
            solid_joinstyle="round", zorder=4)

    # direct labels instead of a legend
    ax.text(date(2015, 3, 1), 5.15, "30-year fixed mortgage rate", fontsize=15,
            fontweight="bold", color=DEEP, ha="left", va="bottom")
    ax.text(date(2015, 2, 1), 1.3, "Fed's target range", fontsize=14,
            fontweight="bold", color=BLUE_D, ha="left", va="bottom")

    # the Sept. 2026 hike
    ax.scatter([hike], [4.00], s=90, color=BLUE, edgecolor=CREAM, linewidth=1.8, zorder=6)
    ax.annotate("Sept. 17, 2026: first hike\nsince 2023, to 3.75% to 4%",
                xy=(hike, 4.0), xytext=(date(2024, 9, 1), 2.35), fontsize=12.5, color=BLUE_D,
                ha="left", va="top", linespacing=1.3, zorder=7,
                arrowprops=dict(arrowstyle="-", color=BLUE_D, lw=1.1))

    # 2026 low and latest
    ax.scatter([low26[0]], [low26[1]], s=70, color=CREAM, edgecolor=CORAL, linewidth=2.2, zorder=6)
    ax.annotate(f"{low26[1]:.2f}%\nFeb. 26", xy=low26, xytext=(0, -14), textcoords="offset points",
                fontsize=12, color=DEEP, ha="center", va="top", linespacing=1.2, zorder=7)
    ax.scatter([last[0]], [last[1]], s=130, color=CORAL, edgecolor=CREAM, linewidth=2, zorder=7)
    ax.annotate(f"{last[1]:.2f}%", xy=last, xytext=(12, 0), textcoords="offset points",
                fontsize=20, fontweight="bold", color="white", ha="left", va="center", zorder=8,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=CORAL, edgecolor="none"))

    # takeaway
    ax.text(date(2015, 3, 1), 7.95, f"Since Feb. 26, the 30-year is up {rise:.2f} points.",
            fontsize=19, fontweight="bold", color=INK, ha="left", va="top")
    ax.text(date(2015, 3, 1), 7.35, "The Fed moved 0.25. Mortgage rates track the bond market,\n"
            "where the 10-Year Treasury closed Friday at 5.24%.",
            fontsize=13, color=INK, ha="left", va="top", linespacing=1.3)

    ax.set_xlim(START, date(2027, 4, 1))
    ax.set_ylim(0, 8.4)
    ax.set_yticks([0, 2, 4, 6, 8])
    ax.set_yticklabels(["0%", "2%", "4%", "6%", "8%"], fontsize=11.5, color=MUTED)
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    for t in ax.get_xticklabels():
        t.set_fontsize(12)
        t.set_color(MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.035, 0.955, "The Fed Hiked Once. Mortgage Rates Rose All Year.", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895, "Federal funds target range and the weekly 30-year fixed mortgage rate, "
             "Jan. 2015 to Oct. 8, 2026", fontsize=13.2, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.065, "Sources: Federal Reserve target range and Freddie Mac Primary Mortgage "
             "Market Survey, via FRED; U.S. Treasury daily yield curve.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"fed-vs-mortgage-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
