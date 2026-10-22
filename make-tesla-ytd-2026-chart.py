#!/usr/bin/env python3
"""
make-tesla-ytd-2026-chart.py  DATA_DIR  [outdir]

The 10/22/26 daily's stock chart. Harv attached the newsletter's "Tesla Stock in
2026" graphic: daily line, "$446" start label, "$386" end pill, "down 14.1% YTD",
"heading into Q3 earnings", source Google Finance, Oct. 21, 2026 close. Emits BOTH:

  tesla-ytd-102226.png      plain HB monogram    -> RE email + Agent Hub
  tesla-ytd-102226-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds tsla-yahoo.json, the Yahoo chart API pull
(query1.finance.yahoo.com/v8/finance/chart/TSLA, interval 1d, Dec. 24, 2025 to
Oct. 22, 2026, fetched Oct. 22, 2026 about 11:10 AM PT, during Thursday's session;
Thursday's partial bar is ignored).

=============================================================================
VERIFICATION 10/22/26
=============================================================================
* Oct. 21 close $386.47 matches the graphic's $386 and CNBC's prior close.
* Dec. 31, 2025 close $449.72. 386.47 / 449.72 = down 14.06%, so the graphic's
  14.1% headline holds. Its "$446" start label matches NO close (Dec. 31 was
  $449.72, Jan. 2 was $438.07), so the chart labels the real Dec. 31 close.
* 2026 low close $298.32 on July 29; Oct. 21 is 29.55% above it.
* "Heading into Q3 earnings" is stale for us: Tesla reported after the bell on
  Oct. 21 (8-K 0001628280-26-066738). Deck: revenue $28.046B (flat), non-GAAP
  EPS $0.48 vs $0.50, deliveries 486,532 (down 2%), capex $4.73B (up 110%),
  active FSD subscriptions 1.74M (upfront buyers AND monthly subscribers).

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
STAMP = "102226"

CREAM = "#fdf6e8"
INK = "#1f2933"
RED = "#d6363c"
DEEP = "#a8232a"
FILL = "#f6d9cf"
GRID = "#d8cdb8"
MUTED = "#8a8172"
GREEN = "#2f7d4f"


def pct(a, b, places="0.01"):
    # round ONCE from the raw ratio; formatting a 2 place value to 1 place
    # double rounds (29.549 -> 29.55 -> "29.6")
    return float(((Decimal(str(a)) / Decimal(str(b)) - 1) * 100).quantize(
        Decimal(places), rounding=ROUND_HALF_UP))


def load():
    r = json.load(open(os.path.join(DATA, "tsla-yahoo.json")))["chart"]["result"][0]
    et = ZoneInfo("America/New_York")
    s = {}
    for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]):
        if c is not None:
            s[datetime.fromtimestamp(t, et).date()] = round(c, 2)
    start, wed = s[date(2025, 12, 31)], s[date(2026, 10, 21)]
    assert (start, wed) == (449.72, 386.47), (start, wed)
    assert pct(wed, start) == -14.06, pct(wed, start)
    ser = sorted((k, v) for k, v in s.items() if date(2025, 12, 31) <= k <= date(2026, 10, 21))
    y26 = [(k, v) for k, v in ser if k.year == 2026]
    lo = min(y26, key=lambda t: t[1])
    assert lo == (date(2026, 7, 29), 298.32), lo
    return ser, start, wed, lo


def build():
    ser, start, wed, lo = load()
    ytd = pct(wed, start)
    off_low = pct(wed, lo[1], "0.1")
    assert off_low == 29.5, off_low
    assert pct(wed, start, "0.1") == -14.1
    xs = [datetime(k.year, k.month, k.day) for k, _ in ser]
    ys = [v for _, v in ser]

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.065, 0.12, 0.76, 0.69])
    ax.set_facecolor(CREAM)

    FLOOR = 275
    ax.fill_between(xs, FLOOR, ys, color=FILL, lw=0, zorder=1, alpha=0.85)
    ax.plot(xs, ys, color=RED, lw=2.6, solid_joinstyle="round", zorder=4)

    # where the year started, so the loss reads at a glance
    ax.axhline(start, color="#b9ad93", lw=1.3, ls=(0, (4, 4)), zorder=2)

    ax.scatter([xs[0]], [start], s=70, color=CREAM, edgecolor=RED, linewidth=2.2, zorder=5)
    ax.annotate(f"Dec. 31: ${start:.2f}", xy=(xs[0], start), xytext=(6, 14),
                textcoords="offset points", fontsize=13, fontweight="bold", color=INK,
                ha="left", va="bottom")

    lx = datetime(lo[0].year, lo[0].month, lo[0].day)
    ax.scatter([lx], [lo[1]], s=55, color=DEEP, edgecolor=CREAM, linewidth=1.5, zorder=5)
    ax.annotate(f"2026 low: ${lo[1]:.2f}\n(July 29)", xy=(lx, lo[1]), xytext=(14, 2),
                textcoords="offset points", fontsize=12, color=DEEP, ha="left", va="center")

    # Wednesday close pill, the day Tesla reported
    fx = xs[-1]
    ax.scatter([fx], [wed], s=130, color=DEEP, edgecolor=CREAM, linewidth=2, zorder=7)
    # pill sits up and to the LEFT of the point: to the right it ran into the stat column
    ax.annotate(f"Oct. 21: ${wed:.2f}", xy=(fx, wed), xytext=(-8, 30), textcoords="offset points",
                fontsize=17, fontweight="bold", color="white", ha="right", va="bottom",
                zorder=8, annotation_clip=False,
                bbox=dict(boxstyle="round,pad=0.38", facecolor=DEEP, edgecolor="none"))

    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b."))
    ax.set_xlim(datetime(2025, 12, 22), datetime(2026, 10, 29))
    ax.set_ylim(FLOOR, 478)
    ax.set_yticks([300, 350, 400, 450])
    ax.set_yticklabels(["$300", "$350", "$400", "$450"], fontsize=12.5, color=MUTED)
    ax.tick_params(axis="x", labelsize=12.5, colors=MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # right hand stat column
    fig.text(0.862, 0.70, "This year", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(0.862, 0.665, f"{pct(wed, start, '0.1'):.1f}%".replace("-", "−"), fontsize=27,
             fontweight="bold", color=DEEP, ha="left", va="top")
    fig.text(0.862, 0.55, "From the July low", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(0.862, 0.515, f"+{off_low:.1f}%", fontsize=27,
             fontweight="bold", color=GREEN, ha="left", va="top")
    fig.text(0.862, 0.40, "Q3 deliveries", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(0.862, 0.365, "−2%", fontsize=27, fontweight="bold", color=DEEP,
             ha="left", va="top")
    fig.text(0.862, 0.295, "486,532 vs. 497,099", fontsize=11.5, color=MUTED,
             ha="left", va="top")

    fig.text(0.035, 0.955, f"Tesla Is Down {abs(pct(wed, start, '0.1')):.1f}% in 2026", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895,
             "Tesla (TSLA) daily closing price, 2026, through Oct. 21, the day it reported third quarter results.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035,
             "Source: Yahoo Finance daily closes, Dec. 31, 2025 through Oct. 21, 2026. Deliveries: Tesla Q3 2026 update, Oct. 21, 2026.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"tesla-ytd-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
