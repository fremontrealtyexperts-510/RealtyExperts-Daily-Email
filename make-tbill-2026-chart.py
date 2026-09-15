#!/usr/bin/env python3
"""
make-tbill-2026-chart.py  [outdir]

Recreates the CNBC "U.S. 3 Month Treasury" YTD screenshot shown in the
ClearValue Tax video for the 09/15/26 edition. Emits BOTH variants:

  tbill-2026-091526.png      plain monogram    -> RE email + Agent Hub
  tbill-2026-091526-hb.png   + wordmark        -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/15/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

Supplied: CNBC US3M 4.022% (+0.007), a YTD line from about 3.6 to 4.015.
The video's claim: bills now refinance at about 4.0%, up from 3.7% for most of
the year.

Treasury daily par yield curve, 3 Mo (constant maturity, bond equivalent):
  Jan 2 3.65; Jan through May range 3.62 to 3.74 (so "3.7 for most of the
  year" holds for the first five months); June 3.77 to 3.87; Aug 31 3.91;
  Sep 10 4.00; Sep 11 4.07; Sep 14 4.11.
CNBC's live US3M quote is a market yield at a moment in time, so 4.022% in the
video and Treasury's 4.11% Monday close are different measures, not a
conflict. (Yahoo ^IRX, a DISCOUNT rate, shows 3.955; not used.)

FRAMING added: the Fed's target range, 3.50% to 3.75% (FRED DFEDTARL/U).
Three month bills now yield more than the top of the range: the market has
already priced the quarter point hike the Fed decides Wednesday.

matplotlib only; build with python3.13 on Mac.
"""
import os
import sys
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "091526"

CREAM = "#fdf6e8"
INK = "#1f2933"
TEAL = "#2f7d6d"
CORAL = "#e2574c"
SLATE = "#8a9aa8"
DEEP = "#b8433a"
GRID = "#e6dcc8"
MUTED = "#8a8172"

# Treasury daily par yield curve, 3 Mo close, 2026 (date, 3mo)
TSY = [("2026-01-02",3.65),("2026-01-05",3.64),("2026-01-06",3.63),("2026-01-07",3.62),("2026-01-08",3.62),("2026-01-09",3.62),("2026-01-12",3.67),("2026-01-13",3.67),("2026-01-14",3.67),("2026-01-15",3.68),("2026-01-16",3.67),("2026-01-20",3.7),("2026-01-21",3.7),("2026-01-22",3.71),("2026-01-23",3.7),("2026-01-26",3.67),("2026-01-27",3.67),("2026-01-28",3.68),("2026-01-29",3.67),("2026-01-30",3.67),("2026-02-02",3.69),("2026-02-03",3.69),("2026-02-04",3.69),("2026-02-05",3.67),("2026-02-06",3.68),("2026-02-09",3.69),("2026-02-10",3.69),("2026-02-11",3.7),("2026-02-12",3.7),("2026-02-13",3.68),("2026-02-17",3.69),("2026-02-18",3.7),("2026-02-19",3.69),("2026-02-20",3.69),("2026-02-23",3.69),("2026-02-24",3.69),("2026-02-25",3.69),("2026-02-26",3.68),("2026-02-27",3.67),("2026-03-02",3.72),("2026-03-03",3.71),("2026-03-04",3.71),("2026-03-05",3.7),("2026-03-06",3.69),("2026-03-09",3.71),("2026-03-10",3.71),("2026-03-11",3.71),("2026-03-12",3.72),("2026-03-13",3.72),("2026-03-16",3.72),("2026-03-17",3.72),("2026-03-18",3.73),("2026-03-19",3.73),("2026-03-20",3.74),("2026-03-23",3.74),("2026-03-24",3.74),("2026-03-25",3.73),("2026-03-26",3.73),("2026-03-27",3.73),("2026-03-30",3.71),("2026-03-31",3.7),("2026-04-01",3.7),("2026-04-02",3.7),("2026-04-03",3.71),("2026-04-06",3.72),("2026-04-07",3.71),("2026-04-08",3.69),("2026-04-09",3.68),("2026-04-10",3.69),("2026-04-13",3.71),("2026-04-14",3.71),("2026-04-15",3.71),("2026-04-16",3.7),("2026-04-17",3.7),("2026-04-20",3.71),("2026-04-21",3.69),("2026-04-22",3.69),("2026-04-23",3.69),("2026-04-24",3.69),("2026-04-27",3.68),("2026-04-28",3.68),("2026-04-29",3.68),("2026-04-30",3.68),("2026-05-01",3.68),("2026-05-04",3.7),("2026-05-05",3.69),("2026-05-06",3.69),("2026-05-07",3.69),("2026-05-08",3.69),("2026-05-11",3.7),("2026-05-12",3.7),("2026-05-13",3.69),("2026-05-14",3.69),("2026-05-15",3.69),("2026-05-18",3.68),("2026-05-19",3.67),("2026-05-20",3.65),("2026-05-21",3.68),("2026-05-22",3.68),("2026-05-26",3.68),("2026-05-27",3.68),("2026-05-28",3.69),("2026-05-29",3.69),("2026-06-01",3.78),("2026-06-02",3.77),("2026-06-03",3.78),("2026-06-04",3.78),("2026-06-05",3.78),("2026-06-08",3.8),("2026-06-09",3.79),("2026-06-10",3.79),("2026-06-11",3.78),("2026-06-12",3.78),("2026-06-15",3.79),("2026-06-16",3.79),("2026-06-17",3.83),("2026-06-18",3.83),("2026-06-22",3.85),("2026-06-23",3.85),("2026-06-24",3.85),("2026-06-25",3.84),("2026-06-26",3.83),("2026-06-29",3.87),("2026-06-30",3.87),("2026-07-01",3.85),("2026-07-02",3.82),("2026-07-06",3.87),("2026-07-07",3.86),("2026-07-08",3.87),("2026-07-09",3.83),("2026-07-10",3.85),("2026-07-13",3.89),("2026-07-14",3.84),("2026-07-15",3.83),("2026-07-16",3.84),("2026-07-17",3.85),("2026-07-20",3.86),("2026-07-21",3.87),("2026-07-22",3.89),("2026-07-23",3.95),("2026-07-24",3.96),("2026-07-27",3.96),("2026-07-28",3.9),("2026-07-29",3.83),("2026-07-30",3.82),("2026-07-31",3.83),("2026-08-03",3.91),("2026-08-04",3.89),("2026-08-05",3.89),("2026-08-06",3.9),("2026-08-07",3.87),("2026-08-10",3.89),("2026-08-11",3.89),("2026-08-12",3.87),("2026-08-13",3.87),("2026-08-14",3.86),("2026-08-17",3.87),("2026-08-18",3.86),("2026-08-19",3.86),("2026-08-20",3.87),("2026-08-21",3.88),("2026-08-24",3.87),("2026-08-25",3.86),("2026-08-26",3.85),("2026-08-27",3.84),("2026-08-28",3.9),("2026-08-31",3.91),("2026-09-01",3.92),("2026-09-02",3.92),("2026-09-03",3.89),("2026-09-04",3.91),("2026-09-08",3.94),("2026-09-09",3.95),("2026-09-10",4.0),("2026-09-11",4.07),("2026-09-14",4.11)]


def build():
    d = [datetime.strptime(a, "%Y-%m-%d") for a, _ in TSY]
    y = [b for _, b in TSY]
    jan_may = [v for dt, v in zip(d, y) if dt.month <= 5]
    assert (min(jan_may), max(jan_may)) == (3.62, 3.74) and y[-1] == 4.11

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    x0, x1 = datetime(2025, 12, 26), datetime(2026, 9, 24)
    ax.axhspan(3.50, 3.75, color=SLATE, alpha=0.20, linewidth=0, zorder=1)
    ax.axhspan(3.75, 4.00, facecolor="none", edgecolor=CORAL, hatch="///",
               alpha=0.35, linewidth=0, zorder=1)
    ax.text(datetime(2026, 1, 3), 3.515, "Fed target range today: 3.50% to 3.75%",
            fontsize=12, color="#5b6875", fontweight="bold", ha="left", va="bottom")
    ax.text(datetime(2026, 1, 3), 3.985, "Range after a quarter point hike: 3.75% to 4.00%",
            fontsize=12, color=CORAL, fontweight="bold", ha="left", va="top")

    ax.plot(d, y, color=TEAL, linewidth=2.8, zorder=3)
    ax.scatter([d[-1]], [y[-1]], s=80, color=TEAL, zorder=4)
    ax.text(d[-1], 4.14, "4.11%\nSep 14", fontsize=14, color=TEAL, fontweight="bold",
            ha="center", va="bottom", linespacing=1.2)
    # Inside the current range band, under the line (it first sat in the hike band).
    ax.text(datetime(2026, 4, 22), 3.585, "January to May: 3.62% to 3.74%",
            fontsize=12.5, color=INK, ha="center", va="center", fontweight="bold")

    ax.set_xlim(x0, x1)
    ax.set_ylim(3.45, 4.28)
    ax.set_yticks([3.5, 3.75, 4.0, 4.25])
    ax.set_yticklabels(["3.50%", "3.75%", "4.00%", "4.25%"], fontsize=12, color=MUTED)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.tick_params(length=0, labelsize=12.5, colors=MUTED)
    ax.yaxis.grid(True, color=GRID, linewidth=1, zorder=0)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)

    fig.text(0.045, 0.945, "T-Bills Have Already Priced In The Hike",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888, "3-month Treasury yield, daily closes, 2026, against the Fed's target range",
             fontsize=14, color=MUTED, ha="left", va="top")

    fig.text(0.045, 0.100,
             "Bills the Treasury rolls over now cost about 4.1%, up from about 3.7% in the first five months of the year.",
             fontsize=11.5, color=DEEP, ha="left", va="bottom")
    fig.text(0.045, 0.030,
             "Source: U.S. Treasury daily par yield curve (3 month constant maturity), closes through September 14, 2026; target range from\n"
             "the Federal Reserve via FRED. CNBC's live US3M quote (4.022% in the video) is an intraday market yield, a different measure.",
             fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5)

    fig.subplots_adjust(left=0.075, right=0.975, top=0.83, bottom=0.21)
    return fig


if __name__ == "__main__":
    fig = build()
    save_pair(fig, os.path.join(OUTDIR, f"tbill-2026-{STAMP}.png"),
              logo=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hb-logo-mark.png"))
