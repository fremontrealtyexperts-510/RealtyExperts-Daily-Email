#!/usr/bin/env python3
"""
make-market-drawdown-nov2026-chart.py  DATA_DIR  [outdir]

The 11/21/26 (Saturday) daily's Stocks chart. Harv: "say something about the
market yesterday, especially the stock. It was horrible how it went down." No
graphic supplied; this is OUR chart from index closes.

Shows how far each index closed below its own record close, every trading day
from Sept. 1 to Nov. 20, 2026, with the 10% "correction" and 20% "bear market"
lines.

Emits BOTH:
  market-drawdown-112126.png      plain HB monogram    -> RE email + Agent Hub
  market-drawdown-112126-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds Yahoo chart API JSON (range=2y, interval=1d) saved on 11/21/26:
  %5EGSPC.json  %5EIXIC.json  %5EDJI.json
Record closes (checked against 10 years of daily closes on 11/21/26, and the
Nov. 20 closes against CNBC's quote service):
  S&P 500   record 7,818.93 on Oct. 6, 2026;  Nov. 20 close 6,910.39  (-11.6%)
  Nasdaq    record 27,599.79 on Oct. 6, 2026; Nov. 20 close 22,617.73 (-18.1%)
  Dow       record 54,349.12 on Aug. 5, 2026; Nov. 20 close 48,147.33 (-11.4%)
Week (Nov. 13 to Nov. 20 closes): S&P -8.61% (worst since the week ended
Apr. 4, 2025), Nasdaq -10.02% and Dow -8.02% (both worst since March 2020).

matplotlib only; build with python3.13 on Mac, run from the workspace.
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
STAMP = "112126"
ET = ZoneInfo("America/New_York")

CREAM = "#fdf6e8"
INK = "#1f2933"
GRID = "#e6dcc8"
MUTED = "#8a8172"
CORAL = "#e2574c"   # Nasdaq
BLUE = "#2f6f9f"    # S&P 500
GOLD = "#b7862a"    # Dow
START = date(2026, 9, 1)
END = date(2026, 11, 20)


def load(fname):
    d = json.load(open(os.path.join(DATA, fname)))["chart"]["result"][0]
    closes = d["indicators"]["quote"][0]["close"]
    return [(datetime.fromtimestamp(t, ET).date(), c) for t, c in zip(d["timestamp"], closes) if c]


def pct(x):
    return float(Decimal(str(x)).quantize(Decimal("0.1"), ROUND_HALF_UP))


SERIES = [("%5EGSPC.json", "S&P 500", BLUE, (date(2026, 10, 6), 7818.93), 6910.39),
          ("%5EIXIC.json", "Nasdaq", CORAL, (date(2026, 10, 6), 27599.79), 22617.73),
          ("%5EDJI.json", "Dow", GOLD, (date(2026, 8, 5), 54349.12), 48147.33)]


def build():
    fig = plt.figure(figsize=(14.0, 7.9), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.15, 0.76, 0.62])
    ax.set_facecolor(CREAM)
    ends = []
    for fname, name, color, (rec_d, rec_v), fri in SERIES:
        s = [x for x in load(fname) if x[0] <= END]
        hi = max(s, key=lambda x: x[1])
        assert (hi[0], round(hi[1], 2)) == (rec_d, rec_v), (name, hi)
        assert s[-1][0] == END and round(s[-1][1], 2) == fri, (name, s[-1])
        dd, run = [], 0.0
        for d0, c in s:
            run = max(run, c)
            if d0 >= START:
                dd.append((d0, (c / run - 1) * 100))
        xs = [datetime(d0.year, d0.month, d0.day) for d0, _ in dd]
        ys = [v for _, v in dd]
        ax.plot(xs, ys, color=color, lw=2.8, zorder=4)
        ax.scatter([xs[-1]], [ys[-1]], color=color, s=46, zorder=5)
        ends.append((name, color, ys[-1], xs[-1]))
    # end labels, nudged apart
    ends.sort(key=lambda e: e[2])
    placed = []
    for name, color, v, x in ends:
        y = v
        for p in placed:
            if abs(y - p) < 1.6:
                y = p + 1.6
        placed.append(y)
        sign = "−" if v < 0 else "+"
        ax.text(x + (datetime(2026, 11, 22) - datetime(2026, 11, 20)), y, f"{name}  {sign}{abs(pct(v)):.1f}%",
                color=color, fontsize=15, fontweight="bold", va="center", ha="left")
    for lvl, lab in [(-10, "Correction: 10% below the record"), (-20, "Bear market: 20% below")]:
        ax.axhline(lvl, color=INK if lvl == -10 else MUTED, lw=1.2, ls=(0, (5, 4)), zorder=2)
        ax.text(datetime(2026, 9, 2), lvl + 0.45, lab, fontsize=11.5, color=INK if lvl == -10 else MUTED, va="bottom")
    ax.axhline(0, color=INK, lw=1.4, zorder=3)
    ax.text(datetime(2026, 9, 2), 0.45, "Record close", fontsize=11.5, color=INK, va="bottom")
    ax.set_ylim(-22.5, 2.2)
    ax.set_xlim(datetime(2026, 9, 1), datetime(2026, 11, 21))
    ax.set_yticks([-20, -15, -10, -5, 0])
    ax.set_yticklabels(["−20%", "−15%", "−10%", "−5%", "0"], fontsize=12, color=MUTED)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b. 1"))
    ax.tick_params(axis="x", labelsize=12, colors=MUTED, length=0, pad=8)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", which="minor", length=0)
    for lab in ax.get_xticklabels():
        lab.set_color(MUTED)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    ax.axvspan(datetime(2026, 11, 16), datetime(2026, 11, 20, 23), color="#f3e3cf", zorder=0)
    ax.text(datetime(2026, 11, 18, 12), 1.2, "this week", ha="center", fontsize=11, color=MUTED)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.035, 0.955, "Stocks Slide Into a Correction", fontsize=26, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.897, "How far each index closed below its record, every trading day since Sept. 1, 2026",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.862, "This week the Nasdaq fell 10.0% and the Dow 8.0%, their worst weeks since March 2020; "
             "the S&P 500 fell 8.6%", fontsize=13.5, color=INK, ha="left", va="top")
    fig.text(0.035, 0.022, "Records: S&P 500 and Nasdaq on Oct. 6, 2026; Dow on Aug. 5, 2026. Daily closes through "
             "Friday, Nov. 20.\nSource: S&P Dow Jones Indices and Nasdaq via Yahoo Finance; closes checked against CNBC.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.45)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"market-drawdown-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    print("wrote", out)
