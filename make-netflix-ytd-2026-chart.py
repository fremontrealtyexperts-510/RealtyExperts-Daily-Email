#!/usr/bin/env python3
"""
make-netflix-ytd-2026-chart.py  DATA_DIR  [outdir]

The 10/16/26 daily's stock chart. Harv attached the newsletter's "Netflix Stock
Is Down 22.6% in 2026" graphic: daily closes year to date, $93.76 start, a
"2026 high: $107.79" in April, $72.61 "as of Oct. 15, 2026 close", source Google
Finance. Emits BOTH:

  netflix-ytd-101626.png      plain HB monogram    -> RE email + Agent Hub
  netflix-ytd-101626-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds nflx-yahoo.json, the Yahoo chart API pull
(query1.finance.yahoo.com/v8/finance/chart/NFLX, interval 1d, Dec. 31, 2024 to
Oct. 16, 2026, fetched Oct. 16, 2026 about 2:00 PM PT, after the close).

=============================================================================
VERIFICATION 10/16/26
=============================================================================
* Every labeled point on the supplied graphic matches the daily closes:
  Dec. 31, 2025 $93.76; 2026 high $107.79 on April 16; Oct. 15 $72.61.
  72.61 / 93.76 = down 22.56%, so the 22.6% headline holds for Thursday.
* We run after Friday's close, so the line runs one session further:
  Oct. 16 close $70.53 (down 2.86% on the day; CNBC quote service agrees),
  down 24.78% for 2026. The 2026 low is $67.06 on Oct. 2.
* 199 sessions in 2026, no degenerate (high == low) bars.
* Story (Market Briefs 10/16 plus AP 10/14): Netflix is cutting about 1,000
  jobs, roughly 6% of staff, and reports third quarter results Tuesday,
  Oct. 20. The newsletter's "content chief is stepping down" item could not
  be confirmed at any primary source, so it stays out of the copy.

matplotlib; build with python3.13 on Mac.
"""
import json
import os
import sys
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "101626"

CREAM = "#fdf6e8"
INK = "#1f2933"
RED = "#d6363c"
DEEP = "#a8232a"
FILL = "#f6d9cf"
GRID = "#d8cdb8"
MUTED = "#8a8172"


def pct(a, b):
    return float(((Decimal(str(a)) / Decimal(str(b)) - 1) * 100).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP))


def load():
    r = json.load(open(os.path.join(DATA, "nflx-yahoo.json")))["chart"]["result"][0]
    et = ZoneInfo("America/New_York")
    s = {}
    for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]):
        if c is not None:
            s[datetime.fromtimestamp(t, et).date()] = round(c, 2)
    start = s[date(2025, 12, 31)]
    thu, fri = s[date(2026, 10, 15)], s[date(2026, 10, 16)]
    assert (start, thu, fri) == (93.76, 72.61, 70.53), (start, thu, fri)
    assert pct(thu, start) == -22.56, pct(thu, start)
    ser = sorted((k, v) for k, v in s.items() if date(2025, 12, 31) <= k <= date(2026, 10, 16))
    y26 = [(k, v) for k, v in ser if k.year == 2026]
    assert len(y26) == 199, len(y26)
    hi = max(y26, key=lambda t: t[1])
    lo = min(y26, key=lambda t: t[1])
    assert hi == (date(2026, 4, 16), 107.79) and lo == (date(2026, 10, 2), 67.06), (hi, lo)
    return ser, start, thu, fri, hi, lo


def build():
    ser, start, thu, fri, hi, lo = load()
    ytd = pct(fri, start)
    assert ytd == -24.78, ytd
    xs = [datetime(k.year, k.month, k.day) for k, _ in ser]
    ys = [v for _, v in ser]

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.065, 0.12, 0.76, 0.69])
    ax.set_facecolor(CREAM)

    FLOOR = 60
    ax.fill_between(xs, FLOOR, ys, color=FILL, lw=0, zorder=1, alpha=0.85)
    ax.plot(xs, ys, color=RED, lw=2.6, solid_joinstyle="round", zorder=4)

    # where the year started, so the loss reads at a glance
    ax.axhline(start, color="#b9ad93", lw=1.3, ls=(0, (4, 4)), zorder=2)

    # start of year
    ax.scatter([xs[0]], [start], s=70, color=CREAM, edgecolor=RED, linewidth=2.2, zorder=5)
    ax.annotate(f"Dec. 31: ${start:.2f}", xy=(xs[0], start), xytext=(6, 14),
                textcoords="offset points", fontsize=13, fontweight="bold", color=INK,
                ha="left", va="bottom")

    # 2026 high
    hx = datetime(hi[0].year, hi[0].month, hi[0].day)
    ax.scatter([hx], [hi[1]], s=70, color=CREAM, edgecolor=RED, linewidth=2.2, zorder=5)
    ax.annotate(f"2026 high: ${hi[1]:.2f} (April 16)", xy=(hx, hi[1]), xytext=(12, -2),
                textcoords="offset points", fontsize=13, fontweight="bold", color=INK,
                ha="left", va="center")

    # 2026 low
    lx = datetime(lo[0].year, lo[0].month, lo[0].day)
    ax.scatter([lx], [lo[1]], s=55, color=DEEP, edgecolor=CREAM, linewidth=1.5, zorder=5)
    ax.annotate(f"2026 low: ${lo[1]:.2f}\n(Oct. 2)", xy=(lx, lo[1]), xytext=(-10, -4),
                textcoords="offset points", fontsize=12, color=DEEP, ha="right", va="top")

    # Friday close pill
    fx = xs[-1]
    ax.scatter([fx], [fri], s=130, color=DEEP, edgecolor=CREAM, linewidth=2, zorder=7)
    ax.annotate(f"${fri:.2f}", xy=(fx, fri), xytext=(16, 0), textcoords="offset points",
                fontsize=17, fontweight="bold", color="white", ha="left", va="center",
                zorder=8, annotation_clip=False,
                bbox=dict(boxstyle="round,pad=0.38", facecolor=DEEP, edgecolor="none"))

    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b."))
    ax.set_xlim(datetime(2025, 12, 22), datetime(2026, 10, 24))
    ax.set_ylim(FLOOR, 114)
    ax.set_yticks([60, 70, 80, 90, 100, 110])
    ax.set_yticklabels(["$60", "$70", "$80", "$90", "$100", "$110"], fontsize=12.5, color=MUTED)
    ax.tick_params(axis="x", labelsize=12.5, colors=MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # right hand stat column
    fig.text(0.862, 0.70, "This year", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(0.862, 0.665, f"{ytd:.1f}%".replace("-", "−"), fontsize=27,
             fontweight="bold", color=DEEP, ha="left", va="top")
    fig.text(0.862, 0.55, "From the high", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(0.862, 0.515, f"{pct(fri, hi[1]):.1f}%".replace("-", "−"), fontsize=27,
             fontweight="bold", color=DEEP, ha="left", va="top")
    fig.text(0.862, 0.40, "Earnings", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(0.862, 0.365, "Tue. Oct. 20", fontsize=19, fontweight="bold", color=INK,
             ha="left", va="top")

    fig.text(0.035, 0.955, f"Netflix Is Down {abs(ytd):.1f}% in 2026", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895, "Netflix (NFLX) daily closing price, 2026, through the Oct. 16 close.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035, "Source: Yahoo Finance daily closes, Dec. 31, 2025 through Oct. 16, 2026.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"netflix-ytd-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
