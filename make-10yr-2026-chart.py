#!/usr/bin/env python3
"""
make-10yr-2026-chart.py  [outdir]

Recreates the newsletter graphic "The 10-Year Just Hit 5%" (Market Briefs,
09/15/26) for the 09/15/26 edition. Emits BOTH variants:

  tenyr-2026-091526.png      plain monogram    -> RE email + Agent Hub
  tenyr-2026-091526-hb.png   + wordmark        -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/15/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

Supplied points: Jan 4.26, Feb 3.97 ("2026 low"), Mar 4.30, Apr 4.40,
May 4.45, Jun 4.44, Jul 4.75, Aug 4.75, Sep 14 5.00% (intraday).

Treasury daily par yield curve, 10 Yr: every monthly point is the MONTH END
close, exact: Jan 30 4.26, Feb 27 3.97, Mar 31 4.30, Apr 30 4.40, May 29 4.45,
Jun 30 4.44, Jul 31 4.75, Aug 31 4.75. 3.97 on Feb 27 is also the 2026 low.

ENDPOINT MIXES MEASURES: the last point is an intraday tick (Yahoo ^TNX high
5.012 on Sept 14) while the rest are closes. Treasury's Sept 14 close is
4.97%, up 0.01. (Market Briefs printed 4.99%.) 4.97 is the highest close since
Oct 19, 2023 (4.98), FRED DGS10; the 2024 to 2025 high was 4.79 (Jan 13, 2025).

The rebuild draws every daily close, keeps the month end dots, ends on the
4.97% close and marks the intraday 5.01% separately.

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
ORANGE = "#d9822b"
CORAL = "#e2574c"
DEEP = "#b8433a"
GRID = "#e6dcc8"
MUTED = "#8a8172"

# Treasury daily par yield curve, 10 Yr close, 2026 (date, 10y)
TSY = [("2026-01-02",4.19),("2026-01-05",4.17),("2026-01-06",4.18),("2026-01-07",4.15),("2026-01-08",4.19),("2026-01-09",4.18),("2026-01-12",4.19),("2026-01-13",4.18),("2026-01-14",4.15),("2026-01-15",4.17),("2026-01-16",4.24),("2026-01-20",4.3),("2026-01-21",4.26),("2026-01-22",4.26),("2026-01-23",4.24),("2026-01-26",4.22),("2026-01-27",4.24),("2026-01-28",4.26),("2026-01-29",4.24),("2026-01-30",4.26),("2026-02-02",4.29),("2026-02-03",4.28),("2026-02-04",4.29),("2026-02-05",4.21),("2026-02-06",4.22),("2026-02-09",4.22),("2026-02-10",4.16),("2026-02-11",4.18),("2026-02-12",4.09),("2026-02-13",4.04),("2026-02-17",4.05),("2026-02-18",4.09),("2026-02-19",4.08),("2026-02-20",4.08),("2026-02-23",4.03),("2026-02-24",4.04),("2026-02-25",4.05),("2026-02-26",4.02),("2026-02-27",3.97),("2026-03-02",4.05),("2026-03-03",4.06),("2026-03-04",4.09),("2026-03-05",4.13),("2026-03-06",4.15),("2026-03-09",4.12),("2026-03-10",4.15),("2026-03-11",4.21),("2026-03-12",4.27),("2026-03-13",4.28),("2026-03-16",4.23),("2026-03-17",4.2),("2026-03-18",4.26),("2026-03-19",4.25),("2026-03-20",4.39),("2026-03-23",4.34),("2026-03-24",4.39),("2026-03-25",4.33),("2026-03-26",4.42),("2026-03-27",4.44),("2026-03-30",4.35),("2026-03-31",4.3),("2026-04-01",4.33),("2026-04-02",4.31),("2026-04-03",4.35),("2026-04-06",4.34),("2026-04-07",4.33),("2026-04-08",4.29),("2026-04-09",4.29),("2026-04-10",4.31),("2026-04-13",4.3),("2026-04-14",4.26),("2026-04-15",4.29),("2026-04-16",4.32),("2026-04-17",4.26),("2026-04-20",4.26),("2026-04-21",4.3),("2026-04-22",4.3),("2026-04-23",4.34),("2026-04-24",4.31),("2026-04-27",4.35),("2026-04-28",4.36),("2026-04-29",4.42),("2026-04-30",4.4),("2026-05-01",4.39),("2026-05-04",4.45),("2026-05-05",4.43),("2026-05-06",4.36),("2026-05-07",4.41),("2026-05-08",4.38),("2026-05-11",4.42),("2026-05-12",4.46),("2026-05-13",4.46),("2026-05-14",4.47),("2026-05-15",4.59),("2026-05-18",4.61),("2026-05-19",4.67),("2026-05-20",4.57),("2026-05-21",4.57),("2026-05-22",4.56),("2026-05-26",4.5),("2026-05-27",4.48),("2026-05-28",4.45),("2026-05-29",4.45),("2026-06-01",4.47),("2026-06-02",4.46),("2026-06-03",4.49),("2026-06-04",4.47),("2026-06-05",4.55),("2026-06-08",4.56),("2026-06-09",4.53),("2026-06-10",4.55),("2026-06-11",4.45),("2026-06-12",4.48),("2026-06-15",4.47),("2026-06-16",4.43),("2026-06-17",4.49),("2026-06-18",4.46),("2026-06-22",4.51),("2026-06-23",4.5),("2026-06-24",4.41),("2026-06-25",4.4),("2026-06-26",4.38),("2026-06-29",4.38),("2026-06-30",4.44),("2026-07-01",4.48),("2026-07-02",4.49),("2026-07-06",4.48),("2026-07-07",4.55),("2026-07-08",4.56),("2026-07-09",4.54),("2026-07-10",4.56),("2026-07-13",4.62),("2026-07-14",4.58),("2026-07-15",4.55),("2026-07-16",4.57),("2026-07-17",4.55),("2026-07-20",4.6),("2026-07-21",4.63),("2026-07-22",4.67),("2026-07-23",4.71),("2026-07-24",4.69),("2026-07-27",4.65),("2026-07-28",4.61),("2026-07-29",4.67),("2026-07-30",4.68),("2026-07-31",4.75),("2026-08-03",4.7),("2026-08-04",4.63),("2026-08-05",4.63),("2026-08-06",4.69),("2026-08-07",4.65),("2026-08-10",4.72),("2026-08-11",4.7),("2026-08-12",4.68),("2026-08-13",4.63),("2026-08-14",4.68),("2026-08-17",4.72),("2026-08-18",4.71),("2026-08-19",4.65),("2026-08-20",4.69),("2026-08-21",4.74),("2026-08-24",4.7),("2026-08-25",4.64),("2026-08-26",4.66),("2026-08-27",4.67),("2026-08-28",4.73),("2026-08-31",4.75),("2026-09-01",4.79),("2026-09-02",4.79),("2026-09-03",4.77),("2026-09-04",4.78),("2026-09-08",4.8),("2026-09-09",4.83),("2026-09-10",4.95),("2026-09-11",4.96),("2026-09-14",4.97)]
INTRADAY_HIGH_SEP14 = 5.01  # Yahoo ^TNX 30 minute bars, high 5.012


def build():
    d = [datetime.strptime(a, "%Y-%m-%d") for a, _ in TSY]
    y = [b for _, b in TSY]
    # Month end closes must equal the supplied graphic's points.
    ends = {}
    for dt, v in zip(d, y):
        ends[(dt.year, dt.month)] = (dt, v)
    me = [ends[(2026, m)] for m in range(1, 9)]
    assert [v for _, v in me] == [4.26, 3.97, 4.30, 4.40, 4.45, 4.44, 4.75, 4.75]
    assert min(y) == 3.97 and y[-1] == 4.97

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    ax.fill_between(d, y, 3.8, color=ORANGE, alpha=0.12, linewidth=0, zorder=1)
    ax.plot(d, y, color=ORANGE, linewidth=2.6, zorder=3)
    ax.scatter([a for a, _ in me], [v for _, v in me], s=36, facecolor=CREAM,
               edgecolor=ORANGE, linewidth=2, zorder=4)
    ax.axhline(5.0, color=CORAL, linewidth=1.2, linestyle=(0, (6, 5)), zorder=2)
    ax.text(d[0], 5.015, "5.00%", color=CORAL, fontsize=11.5, fontweight="bold",
            ha="left", va="bottom")

    # 2026 low
    low_i = y.index(3.97)
    # One line, left of and below the dot: a two line label here sat on the "Mar" tick.
    ax.text(datetime(2026, 1, 24), 3.895, "2026 low: 3.97% on Feb 27",
            ha="left", va="center", fontsize=12, color=INK, fontweight="bold")
    assert d[low_i] == datetime(2026, 2, 27)
    # Monday close + intraday touch
    ax.scatter([d[-1]], [4.97], s=90, color=DEEP, zorder=5)
    ax.scatter([d[-1]], [INTRADAY_HIGH_SEP14], s=70, facecolor=CREAM, edgecolor=CORAL,
               linewidth=2, zorder=5)
    ax.text(d[-1], 5.075, "Intraday Sep 14: 5.01%", fontsize=11, color=CORAL,
            ha="right", va="bottom")
    ax.annotate("Close Sep 14: 4.97%\nhighest close since\nOct 19, 2023",
                xy=(d[-1], 4.97), xytext=(datetime(2026, 7, 25), 4.28),
                fontsize=12.5, color=DEEP, fontweight="bold", ha="center", va="center",
                linespacing=1.4, arrowprops=dict(arrowstyle="-", color=DEEP, lw=1.1))

    ax.set_ylim(3.8, 5.15)
    ax.set_xlim(datetime(2025, 12, 26), datetime(2026, 9, 24))
    ax.set_yticks([4.0, 4.25, 4.5, 4.75, 5.0])
    ax.set_yticklabels(["4.00%", "4.25%", "4.50%", "4.75%", "5.00%"], fontsize=12, color=MUTED)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.tick_params(length=0, labelsize=12.5, colors=MUTED)
    ax.yaxis.grid(True, color=GRID, linewidth=1, zorder=0)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)

    fig.text(0.045, 0.945, "The 10-Year Touched 5%. It Closed At 4.97%.",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888, "U.S. 10-year Treasury yield, daily closes, 2026 (dots mark each month end)",
             fontsize=14, color=MUTED, ha="left", va="top")

    fig.text(0.045, 0.100,
             "Mortgage rates follow the 10-Year: Mortgage News Daily's 30-year hit 7.17% Monday, its highest reading in a year.",
             fontsize=11.5, color=DEEP, ha="left", va="bottom")
    fig.text(0.045, 0.030,
             "Source: U.S. Treasury daily par yield curve, closes through September 14, 2026; intraday high from Yahoo Finance (^TNX).\n"
             "Highest close since October 19, 2023 (4.98%), per Federal Reserve data via FRED.",
             fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5)

    fig.subplots_adjust(left=0.075, right=0.975, top=0.83, bottom=0.21)
    return fig


if __name__ == "__main__":
    fig = build()
    save_pair(fig, os.path.join(OUTDIR, f"tenyr-2026-{STAMP}.png"),
              logo=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hb-logo-mark.png"))
