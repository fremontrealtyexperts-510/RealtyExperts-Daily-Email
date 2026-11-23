#!/usr/bin/env python3
"""
make-btc-seven-week-slide-chart.py  YAHOO_BTC_JSON  [outdir]

The 11/23/26 daily's Crypto chart. Harv supplied a newsletter graphic,
"Bitcoin's 7-Week Slide" (weekly closes Oct. 4 to Nov. 21, $86.57K to
$60.09K, -30.58%, credited to Cointelegraph, Look Into Bitcoin, CoinDesk).
A design brief, not a data source. Re-pulled and diffed on 11/23/26:

  * Its Oct. 4 to Nov. 15 points match the Sunday (UTC) daily closes within
    about $100, EXCEPT Oct. 11, which it drew near $82.5K; every source has
    about $83.7K (Yahoo 83,679, CoinGecko 83,691, Coin Metrics 83,637).
  * Its last point, Nov. 21, is a SATURDAY ($60,094 on Yahoo). The week was
    not over. We end on the completed weekly close, Sunday Nov. 22, $61,162.
  * So our figure is -29.3% (86,480 to 61,162), not -30.58%.
  * Seven straight weekly losses (Oct. 11 to Nov. 22), the longest run
    since the nine weeks that ended May 29, 2022 (checked over 10 years of
    Sunday closes in the same file).

Emits BOTH:
  btc-seven-week-slide-112326.png      plain HB monogram    -> RE email + Agent Hub
  btc-seven-week-slide-112326-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

YAHOO_BTC_JSON = Yahoo chart API BTC-USD, range=10y, interval=1d, saved 11/23/26.

matplotlib only; build with python3.13 on Mac, run from the workspace.
"""
import json
import os
import sys
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

SRC = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "112326"

CREAM = "#fdf6e8"
INK = "#1f2933"
GRID = "#e6dcc8"
MUTED = "#8a8172"
ORANGE = "#e8892b"
CORAL = "#e2574c"
FIRST = date(2026, 10, 4)
LAST = date(2026, 11, 22)


def sundays():
    d = json.load(open(SRC))["chart"]["result"][0]
    closes = d["indicators"]["quote"][0]["close"]
    rows = [(datetime.fromtimestamp(t, timezone.utc).date(), c) for t, c in zip(d["timestamp"], closes) if c]
    return [(d0, c) for d0, c in rows if d0.weekday() == 6]


def pct(x, q="0.1"):
    return Decimal(str(x)).quantize(Decimal(q), ROUND_HALF_UP)


def build():
    sun = sundays()
    pts = [(d0, c) for d0, c in sun if FIRST <= d0 <= LAST]
    assert len(pts) == 8 and pts[0][0] == FIRST and pts[-1][0] == LAST, pts
    # seven straight weekly losses, and the week before Oct. 4 was a gain
    assert all(pts[i][1] < pts[i - 1][1] for i in range(1, 8))
    before = [c for d0, c in sun if d0 < FIRST][-1]
    assert pts[0][1] > before
    # longest run of weekly losses since the one that ended May 29, 2022
    run, best_since_2022 = 0, 0
    for i in range(1, len(sun)):
        run = run + 1 if sun[i][1] < sun[i - 1][1] else 0
        if sun[i][0] > date(2022, 5, 29) and sun[i][0] < FIRST:
            best_since_2022 = max(best_since_2022, run)
    assert best_since_2022 < 7, best_since_2022
    chg = (pts[-1][1] / pts[0][1] - 1) * 100
    assert str(pct(chg)) == "-29.3", chg
    assert round(pts[0][1]) == 86480 and round(pts[-1][1]) == 61162

    fig = plt.figure(figsize=(14.0, 7.9), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.15, 0.62, 0.67])
    ax.set_facecolor(CREAM)
    xs = list(range(len(pts)))
    ys = [c / 1000 for _, c in pts]
    ax.fill_between(xs, ys, 55, color=ORANGE, alpha=0.13, zorder=1)
    ax.plot(xs, ys, color=ORANGE, lw=3.2, zorder=3)
    ax.scatter(xs, ys, color=ORANGE, s=70, zorder=4, edgecolor=CREAM, linewidth=1.6)
    # value labels on every point
    for i, (x, y) in enumerate(zip(xs, ys)):
        lab = f"${pts[i][1]:,.0f}"
        bold = i in (0, len(xs) - 1)
        if i == 6:   # Nov. 15: the line rises steeply into this point, so label it below and left
            ax.text(x - 0.12, y - 1.0, lab, ha="right", va="top", fontsize=11.5, color=MUTED)
            continue
        ax.text(x, y + 1.35, lab, ha="center", va="bottom", fontsize=13.5 if bold else 11.5,
                fontweight="bold" if bold else "normal", color=INK if bold else MUTED)
    ax.set_ylim(55, 92)
    ax.set_xlim(-0.45, len(xs) - 0.55)
    ax.set_yticks([60, 70, 80, 90])
    ax.set_yticklabels(["$60K", "$70K", "$80K", "$90K"], fontsize=12, color=MUTED)
    ax.set_xticks(xs)
    ax.set_xticklabels([d0.strftime("%b. %-d").replace("Sep.", "Sept.") for d0, _ in pts], fontsize=12, color=MUTED)
    ax.tick_params(length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # right-hand callout
    fig.text(0.735, 0.66, f"−{abs(pct(chg))}%", fontsize=50, fontweight="bold", color=CORAL, ha="left", va="center")
    fig.text(0.738, 0.565, "in seven weeks", fontsize=17, color=INK, ha="left", va="center")
    fig.text(0.738, 0.47, "Seven straight weekly losses,\nthe longest run since the nine\nweeks that ended May 2022",
             fontsize=13.5, color=INK, ha="left", va="top", linespacing=1.45)
    fig.text(0.738, 0.30, "Monday afternoon: about $61,200", fontsize=12.5, color=MUTED, ha="left", va="top")

    fig.text(0.035, 0.955, "Bitcoin's Seven Week Slide", fontsize=26, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.897, "Weekly closing price (Sunday, UTC), Oct. 4 to Nov. 22, 2026",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.022, "Weekly close = the Sunday daily close in UTC. Nov. 22 is the latest completed week.\n"
             "Source: CoinMarketCap via Yahoo Finance; closes checked against CoinGecko and Coin Metrics.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.45)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"btc-seven-week-slide-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    print("wrote", out)
