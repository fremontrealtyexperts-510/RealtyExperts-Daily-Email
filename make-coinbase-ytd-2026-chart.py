#!/usr/bin/env python3
"""
make-coinbase-ytd-2026-chart.py  DATA_DIR  [outdir]

The 10/30/26 daily's crypto chart. Harv attached the newsletter's "Coinbase Stock
Is Down 28% in 2026" graphic: COIN month-end closes from a $226 start to $162.
Emits BOTH:

  coinbase-ytd-103026.png      plain HB monogram    -> RE email + Agent Hub
  coinbase-ytd-103026-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

No company logo: the graphic carried a trademark, ours does not.

DATA_DIR holds COIN-yahoo.json: Yahoo chart API, interval 1d, Dec. 2025 onward,
fetched Oct. 30, 2026 after the 4 PM ET close.

=============================================================================
VERIFICATION 10/30/26
=============================================================================
* The graphic was right when cut and stale by the time this ran. Its $226 is the
  Dec. 31, 2025 close ($226.14, the correct YTD base), its nine month-end points
  match Yahoo, and its $162 is the Oct. 28 close ($162.32), down 28.2%.
* Since then: Thursday $160.59, Friday $143.54 after Q3 results and the Binance
  hack. Oct. 30 is October's last trading day, so the last point here IS the real
  month-end close, down 36.5%, and the title moves to 37%.
* Results (8-K Exhibit 99.1, Oct. 29): revenue $1,215.6M, down 35% y/y, flat q/q;
  net income $718.7M, adjusted net income $77.7M (the adjustment removes $715.0M
  of gains on crypto held for investment).

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import json
import os
import sys
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "103026"

CREAM = "#fdf6e8"
INK = "#1f2933"
BLUE = "#2563eb"
CORAL = "#d9643a"
GRID = "#d8cdb8"
MUTED = "#8a8172"
MINUS = "−"

BASE, END = date(2025, 12, 31), date(2026, 10, 30)


def pct(a, b, places="0.1"):
    # round ONCE from the raw ratio
    return float(((Decimal(str(a)) / Decimal(str(b)) - 1) * 100).quantize(
        Decimal(places), rounding=ROUND_HALF_UP))


def load():
    r = json.load(open(os.path.join(DATA, "COIN-yahoo.json")))["chart"]["result"][0]
    et = ZoneInfo("America/New_York")
    closes = {}
    for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]):
        if c is not None:
            closes[datetime.fromtimestamp(t, et).date()] = round(c, 2)
    month_end = {}
    for d in sorted(closes):
        month_end[(d.year, d.month)] = (d, closes[d])
    pts = [month_end[k] for k in sorted(month_end) if k >= (2025, 12)]
    assert pts[0] == (BASE, 226.14), pts[0]
    assert pts[-1] == (END, 143.54), pts[-1]
    assert len(pts) == 11, len(pts)
    # the graphic's frame: right through Wednesday, so only the endpoint moved
    assert (closes[date(2026, 10, 28)], pct(closes[date(2026, 10, 28)], 226.14)) == (162.32, -28.2)
    assert closes[date(2026, 10, 29)] == 160.59
    assert pct(143.54, 160.59) == -10.6
    assert pct(143.54, 226.14) == -36.5
    assert [round(v) for _, v in pts[1:-1]] == [195, 176, 175, 188, 189, 146, 146, 188, 186]
    return pts


def build():
    pts = load()
    vals = [v for _, v in pts]
    labels = ["Start"] + [d.strftime("%b") for d, _ in pts[1:]]
    xs = list(range(len(vals)))

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.07, 0.115, 0.735, 0.70])
    ax.set_facecolor(CREAM)

    ax.plot(xs, vals, color=BLUE, lw=3.0, solid_joinstyle="round", zorder=4)
    ax.scatter(xs[1:-1], vals[1:-1], s=34, color=BLUE, zorder=5)
    ax.scatter([xs[0]], [vals[0]], s=120, color=INK, edgecolor=CREAM, linewidth=2, zorder=6)
    ax.scatter([xs[-1]], [vals[-1]], s=130, color=CORAL, edgecolor=CREAM, linewidth=2, zorder=6)

    ax.annotate(f"\\${vals[0]:.2f}", xy=(xs[0], vals[0]), xytext=(26, 4), textcoords="offset points",
                fontsize=16, fontweight="bold", color=INK, ha="left", va="center")
    ax.annotate("Dec. 31 close", xy=(xs[0], vals[0]), xytext=(26, -15), textcoords="offset points",
                fontsize=11.5, color=MUTED, ha="left", va="center")

    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=13.5, color=INK)
    ax.set_xlim(-0.25, len(xs) - 0.75)
    ax.set_ylim(120, 240)
    ticks = [140, 160, 180, 200, 220, 240]
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"\\${v}" for v in ticks], fontsize=12.5, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=9)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    X = 0.825
    fig.text(X, 0.72, "Year to date", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(X, 0.685, f"{MINUS}{abs(round(pct(vals[-1], vals[0], '1')))}%", fontsize=40, fontweight="bold",
             color=CORAL, ha="left", va="top")
    fig.text(X, 0.565, "Oct. 30 close", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(X, 0.53, f"\\${vals[-1]:.2f}", fontsize=24, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(X, 0.445, "That day", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(X, 0.41, f"{MINUS}10.6%", fontsize=24, fontweight="bold", color=CORAL, ha="left", va="top")

    fig.text(0.035, 0.955, "Coinbase Stock Is Down 37% in 2026", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.895, "COIN month-end closing price, Dec. 31, 2025 to Oct. 30, 2026.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035, "Source: Yahoo Finance daily closes (COIN), Dec. 31, 2025 to Oct. 30, 2026.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"coinbase-ytd-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
