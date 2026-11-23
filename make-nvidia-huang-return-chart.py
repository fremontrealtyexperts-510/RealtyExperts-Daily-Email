#!/usr/bin/env python3
"""
make-nvidia-huang-return-chart.py  YAHOO_NVDA_JSON  NASDAQ_NVDA_JSON  TODAY_CLOSE  [outdir]

The 11/23/26 daily's Stocks chart. Harv: "Jensen Huang returned, so speak on
that." No graphic supplied; this is OUR chart of Nvidia's daily closes.

Events, from Nvidia's own SEC filings (CIK 1045810):
  * 8-K acc. 0001045810-26-000082 (filed Nov. 12): the board accepted Jensen
    Huang's resignation as President, CEO and director on Nov. 11, effective
    immediately; CFO Colette Kress interim CEO.
  * 8-K acc. 0001045810-26-000090 (filed Nov. 23): on Nov. 22 the board
    reinstated Huang as President, CEO and director, effective immediately
    (unanimous vote per the Ex. 99.1 press release); Kress stays CFO.
  * Nov. 20: reports (Reuters, unnamed sources) that SEC staff are examining
    Nvidia's accounting; neither the SEC nor Nvidia confirmed. NVDA -14.01%.

Closes: Yahoo chart API (period1=0, interval=1d) and the Nasdaq API
(10 years, back to 11/21/2016) must agree to the cent on every day both
carry from Sept. 1; TODAY_CLOSE is Monday's official close from CNBC's quote
service, and the Yahoo bar for 11/23 must equal it.
  Record close $239.24 on Oct. 6, 2026. Nov. 20 close $125.53 (-47.5%).

Emits BOTH:
  nvidia-huang-return-112326.png      plain HB monogram    -> RE email + Agent Hub
  nvidia-huang-return-112326-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

matplotlib only; build with python3.13 on Mac, run from the workspace.
"""
import json
import os
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

YJ, NJ, TODAY_CLOSE = sys.argv[1], sys.argv[2], Decimal(sys.argv[3])
OUTDIR = sys.argv[4] if len(sys.argv) > 4 else "."
STAMP = "112326"
ET = ZoneInfo("America/New_York")

CREAM = "#fdf6e8"
INK = "#1f2933"
GRID = "#e6dcc8"
MUTED = "#8a8172"
GREEN = "#3c8d3f"
CORAL = "#e2574c"
SHADE = "#f3e3cf"
START = date(2026, 9, 1)
TODAY = date(2026, 11, 23)


def money(x):
    return Decimal(str(x)).quantize(Decimal("0.01"), ROUND_HALF_UP)


def pct(x):
    return Decimal(str(x)).quantize(Decimal("0.1"), ROUND_HALF_UP)


def load():
    d = json.load(open(YJ))["chart"]["result"][0]
    y = [(datetime.fromtimestamp(t, ET).date(), c) for t, c in zip(d["timestamp"], d["indicators"]["quote"][0]["close"]) if c]
    rows = json.load(open(NJ))["data"]["tradesTable"]["rows"]
    n = {datetime.strptime(r["date"], "%m/%d/%Y").date(): Decimal(r["close"].replace("$", "").replace(",", "")) for r in rows}
    for d0, c in y:
        if START <= d0 < TODAY:
            assert money(c) == n[d0], (d0, c, n[d0])
    assert y[-1][0] == TODAY and money(y[-1][1]) == TODAY_CLOSE, (y[-1], TODAY_CLOSE)
    return y, n


def build():
    y, n = load()
    hist = [(d0, money(c)) for d0, c in y]
    rec = max(hist[:-1], key=lambda x: x[1])
    assert rec == (date(2026, 10, 6), Decimal("239.24")), rec
    fri = dict(hist)[date(2026, 11, 20)]
    assert fri == Decimal("125.53")
    day = (TODAY_CLOSE / fri - 1) * 100
    # best day check: Nasdaq history (10 years) and Yahoo's longer history
    ns = sorted(n.items())
    best_n = max(((ns[i][1] / ns[i - 1][1] - 1) * 100 for i in range(1, len(ns))))
    assert day > best_n, (day, best_n)          # beats every day in Nasdaq's 10 years
    pts = [(d0, c) for d0, c in hist if d0 >= START]

    fig = plt.figure(figsize=(14.0, 7.9), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.15, 0.66, 0.66])
    ax.set_facecolor(CREAM)
    xs = [datetime(d0.year, d0.month, d0.day) for d0, _ in pts]
    ys = [float(c) for _, c in pts]
    ax.axvspan(datetime(2026, 11, 11, 12), datetime(2026, 11, 22), color=SHADE, zorder=0)
    ax.text(datetime(2026, 11, 16, 18), 246, "Huang out", ha="center", va="center", fontsize=12, color=MUTED)
    ax.plot(xs[:-1], ys[:-1], color=GREEN, lw=2.8, zorder=3)
    ax.plot(xs[-2:], ys[-2:], color=GREEN, lw=2.8, ls=(0, (1.5, 1.2)), zorder=3)
    # record
    rx = datetime(2026, 10, 6)
    ax.scatter([rx], [239.24], color=GREEN, s=60, zorder=4, edgecolor=CREAM, linewidth=1.5)
    ax.text(rx, 243.5, "Record close $239.24\nOct. 6", ha="center", va="bottom", fontsize=12, color=INK, linespacing=1.3)
    # Friday low
    fx = datetime(2026, 11, 20)
    ax.scatter([fx], [125.53], color=CORAL, s=70, zorder=5, edgecolor=CREAM, linewidth=1.5)
    ax.text(fx - timedelta(days=1), 121, f"$125.53 Friday, Nov. 20\ndown {abs(pct((fri / rec[1] - 1) * 100))}% from the record",
            ha="right", va="top", fontsize=12, color=INK, linespacing=1.3)
    # Monday
    mx = datetime(2026, 11, 23)
    ax.scatter([mx], [float(TODAY_CLOSE)], color=GREEN, s=90, zorder=5, edgecolor=CREAM, linewidth=1.6)
    ax.text(mx + timedelta(days=1), float(TODAY_CLOSE), f"${TODAY_CLOSE}\nMonday", ha="left", va="center",
            fontsize=13.5, fontweight="bold", color=INK, linespacing=1.3)
    # event ticks
    for d0, lab in [(datetime(2026, 11, 11, 12), "Nov. 11\nHuang steps down"),
                    (datetime(2026, 11, 22), "Nov. 22\nboard reinstates him")]:
        ax.axvline(d0, color=INK, lw=1.1, ls=(0, (4, 3)), zorder=2)
    ax.text(datetime(2026, 11, 11), 98, "Nov. 11: Huang steps down", ha="right", va="bottom", fontsize=11.5, color=INK)
    ax.text(datetime(2026, 11, 22, 12), 98, "Nov. 22:\nreinstated", ha="left", va="bottom", fontsize=11.5, color=INK,
            linespacing=1.25)
    ax.set_ylim(95, 262)
    ax.set_xlim(datetime(2026, 8, 31), datetime(2026, 11, 30))
    ax.set_yticks([100, 150, 200, 250])
    ax.set_yticklabels(["$100", "$150", "$200", "$250"], fontsize=12, color=MUTED)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: mdates.num2date(v).strftime("%b. 1").replace("Sep.", "Sept.")))
    ax.tick_params(axis="x", labelsize=12, colors=MUTED, length=0, pad=8)
    ax.tick_params(axis="y", length=0)
    for lab in ax.get_xticklabels():
        lab.set_color(MUTED)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.765, 0.66, f"+{pct(day)}%", fontsize=44, fontweight="bold", color=GREEN, ha="left", va="center")
    fig.text(0.773, 0.565, "on Monday", fontsize=17, color=INK, ha="left", va="center")
    fig.text(0.773, 0.47, "Nvidia's biggest one day gain\nin more than ten years", fontsize=13.5, color=INK,
             ha="left", va="top", linespacing=1.45)
    fig.text(0.773, 0.355, f"Still {abs(pct((TODAY_CLOSE / rec[1] - 1) * 100))}% below\nthe Oct. 6 record",
             fontsize=13.5, color=MUTED, ha="left", va="top", linespacing=1.45)

    fig.text(0.035, 0.955, "Nvidia: Huang Out, Huang Back", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.897, "Daily closing price, Sept. 1 to Nov. 23, 2026", fontsize=13.5, color=MUTED,
             ha="left", va="top")
    fig.text(0.035, 0.022, "Events: Nvidia Form 8-K filings of Nov. 12 and Nov. 23, 2026. Closes checked against the "
             "Nasdaq; Monday's close from CNBC.\nSource: Nasdaq via Yahoo Finance; NVIDIA Corp. SEC filings.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.45)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"nvidia-huang-return-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    print("wrote", out)
