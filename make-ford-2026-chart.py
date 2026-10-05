#!/usr/bin/env python3
"""
make-ford-2026-chart.py  DATA_DIR  [outdir]

The 10/05/26 daily's Ford chart (Stocks section). Harv attached the newsletter
graphic "Ford Stalls Out" (Ford share price, Jan. 2 to Oct. 2, 2026, -7.77% year
to date, $12.10). Rebuilt from primary data, not traced. Emits BOTH variants:

  ford-ytd-100526.png      plain HB monogram    -> RE email + Agent Hub
  ford-ytd-100526-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds three files pulled on 10/05/26 (Yahoo 429'd all morning):
  F-nasdaq.json    api.nasdaq.com/api/quote/F/historical?assetclass=stocks
                   &fromdate=2025-12-20&todate=2026-10-05&limit=400
  GM-nasdaq.json   same endpoint, GM
  SPX-cnbc.json    ts-api.cnbc.com/harmony/app/bars/.SPX/1D/20251229000000/
                   20260106000000/adjusted/EST5EDT.json (the Dec 31 close only;
                   the Oct 2 close 7,722.72 is CNBC's previous_day_closing,
                   the same figure on the 10/02 to 10/04 cards)

=============================================================================
VERIFICATION 10/05/26
=============================================================================
Year to date is measured from the Dec 31, 2025 close ($13.12), which is how the
newsletter's -7.77% was computed: 12.10 / 13.12 - 1 = -7.774%. (From the Jan 2
close of $13.34 it would be -9.3%, so the supplied subtitle "Jan. 2" is loose;
ours states Dec. 31.) Prices are NOT adjusted for dividends, same as the
supplied chart ("share price").

2026 closing high $17.44 on May 29; low $11.21 on Mar 30. The May run: $11.99
(May 12) to $17.44 (May 29), +45.5% in 12 sessions. May 13 was +13.18% on a
Morgan Stanley call about Ford Energy's battery storage business (Bloomberg,
05/13/26); Ford and EDF announced a framework for up to 20 GWh of storage on
May 18 (Ford's own release, q4cdn 2026/May/18). The supplied graphic draws the
peak under its "Jun" tick; it was the last session of May.

September: NHTSA recall 26V578 (2023 to 2027 F-150 fuel tank straps, report
received 09/09/26; 223,472 trucks per the notice coverage). Ford's Q3 U.S.
sales release (SEC 8-K exhibit 99, 10/02/26): 509,764 vehicles, down 6.6%,
"reflecting the planned portfolio changes" (Escape and Corsair phase-out), and
an end of September F-150 supplier issue "containable" within the $10.0B to
$11.0B adjusted EBIT guidance.

Benchmarks, same Dec 31 base: S&P 500 6,845.50 -> 7,722.72 = +12.81%;
GM $81.32 -> $78.27 = -3.75%. Off the May 29 high Ford is -30.6%.

matplotlib only; build with python3.13 on Mac.
"""
import json
import os
import sys
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "100526"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
SLATE = "#6f8296"
GRID = "#d8cdb8"
MUTED = "#8a8172"
SPAN = "#f1e2c8"
MINUS = "−"                       # a hyphen minus can vanish at small sizes


def pct(a, b):
    return (Decimal(str(a)) / Decimal(str(b)) - 1) * 100


def r1(d):
    return d.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def signed(d, places="0.1"):
    q = d.quantize(Decimal(places), rounding=ROUND_HALF_UP)
    return f"+{q}%" if q > 0 else f"{MINUS}{abs(q)}%"


def nasdaq(name):
    rows = json.load(open(os.path.join(DATA, name)))["data"]["tradesTable"]["rows"]
    out = [(datetime.strptime(r["date"], "%m/%d/%Y"), float(r["close"].replace("$", "").replace(",", "")))
           for r in rows]
    return sorted(out)


def close_on(series, mdy):
    want = datetime.strptime(mdy, "%m/%d/%Y")
    return [c for d, c in series if d == want][0]


def load():
    f = nasdaq("F-nasdaq.json")
    gm = nasdaq("GM-nasdaq.json")
    bars = json.load(open(os.path.join(DATA, "SPX-cnbc.json")))["barData"]["priceBars"]
    spx_dec31 = float([b for b in bars if b["tradeTime"].startswith("20251231")][0]["close"])
    spx_oct2 = 7722.72

    base = close_on(f, "12/31/2025")
    last_d, last = f[-1]
    assert (base, last, last_d.strftime("%m/%d/%Y")) == (13.12, 12.10, "10/02/2026"), (base, last, last_d)
    ytd = pct(last, base)
    assert ytd.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) == Decimal("-7.77"), ytd

    y26 = [(d, c) for d, c in f if d.year == 2026 or d == datetime(2025, 12, 31)]
    hi = max(y26, key=lambda t: t[1])
    lo = min(y26, key=lambda t: t[1])
    assert hi == (datetime(2026, 5, 29), 17.44), hi
    assert lo == (datetime(2026, 3, 30), 11.21), lo
    run = pct(17.44, close_on(f, "05/12/2026"))
    assert r1(run) == Decimal("45.5"), run
    sessions = [d for d, _ in f if datetime(2026, 5, 12) < d <= datetime(2026, 5, 29)]
    assert len(sessions) == 12, len(sessions)
    off_hi = pct(last, 17.44)
    assert r1(off_hi) == Decimal("-30.6"), off_hi

    spx = pct(spx_oct2, spx_dec31)
    assert spx_dec31 == 6845.50 and r1(spx) == Decimal("12.8"), (spx_dec31, spx)
    gmy = pct(close_on(gm, "10/02/2026"), close_on(gm, "12/31/2025"))
    assert r1(gmy) == Decimal("-3.8"), gmy
    return y26, base, ytd, spx, gmy, off_hi


def build():
    s, base, ytd, spx, gmy, off_hi = load()
    print(f"Ford YTD {ytd:.3f}%  S&P {spx:.2f}%  GM {gmy:.2f}%  off high {off_hi:.1f}%")
    xs = [d for d, _ in s]
    ys = [c for _, c in s]

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.175, 0.80, 0.625])
    ax.set_facecolor(CREAM)

    ymin, ymax = 10.2, 19.0
    may13, may29 = datetime(2026, 5, 12, 12), datetime(2026, 5, 29, 12)
    ax.axvspan(may13, may29, ymin=0, ymax=1, color=SPAN, lw=0, zorder=0)

    ax.fill_between(xs, ys, ymin, color=CORAL, alpha=0.10, lw=0, zorder=1)
    ax.plot(xs, ys, color=CORAL, lw=2.4, solid_joinstyle="round", zorder=3)

    # the year's starting line
    ax.axhline(base, color=MUTED, lw=1.4, ls=(0, (6, 4)), zorder=2)
    ax.text(datetime(2026, 3, 9), base + 0.17, "Started 2026 at $13.12", fontsize=11.5,
            color=MUTED, ha="left", va="bottom", zorder=6)

    # the rally band
    ax.text(datetime(2026, 5, 21), 18.55, "Battery storage rally", fontsize=12, fontweight="bold",
            color=INK, ha="center", va="center", zorder=6)
    ax.text(datetime(2026, 5, 21), 18.12, "+45% in 12 sessions", fontsize=11, color=INK,
            ha="center", va="center", zorder=6)

    # high, low, last
    ax.scatter([datetime(2026, 5, 29)], [17.44], s=58, color=DEEP, zorder=5)
    ax.text(datetime(2026, 6, 4), 17.44, "$17.44 on May 29,\nthe year's high", fontsize=11.5,
            color=INK, ha="left", va="center", linespacing=1.2, zorder=6)
    ax.scatter([datetime(2026, 3, 30)], [11.21], s=58, color=DEEP, zorder=5)
    ax.text(datetime(2026, 3, 30), 10.93, "$11.21, Mar. 30 low", fontsize=11.5, color=INK,
            ha="center", va="top", zorder=6)

    end = datetime(2026, 10, 2)
    ax.scatter([end], [12.10], s=95, color=CORAL, edgecolor=CREAM, linewidth=2, zorder=6)
    ax.annotate("$12.10", xy=(end, 12.10), xytext=(16, 0), textcoords="offset points",
                fontsize=19, fontweight="bold", color="white", ha="left", va="center", zorder=7,
                bbox=dict(boxstyle="round,pad=0.35", facecolor=CORAL, edgecolor="none"))
    ax.text(datetime(2026, 10, 9), 11.42, f"{MINUS}31% from\nthe May high", fontsize=10.8,
            color=DEEP, ha="left", va="top", linespacing=1.15, zorder=6)

    # September's news, under the line where the chart is empty
    ax.text(datetime(2026, 9, 27), 10.42,
            "September: an F-150 recall, a supplier problem\nthat hit F-150 output, Q3 sales down 6.6%",
            fontsize=10.6, color=MUTED, ha="right", va="bottom", linespacing=1.25, zorder=6)

    # the year to date block, top right inside the plot where the line never goes
    ax.text(datetime(2026, 10, 1), 18.62, signed(ytd, "0.1"), fontsize=34, fontweight="bold",
            color=CORAL, ha="right", va="center", zorder=6)
    ax.text(datetime(2026, 10, 1), 17.86, "year to date", fontsize=12.5, color=INK,
            ha="right", va="center", zorder=6)
    ax.text(datetime(2026, 10, 1), 17.38, f"S&P 500 {signed(spx)}   GM {signed(gmy)}",
            fontsize=11.5, color=MUTED, ha="right", va="center", zorder=6)

    ax.set_ylim(ymin, ymax)
    ax.set_xlim(datetime(2025, 12, 24), datetime(2026, 10, 30))
    ax.set_yticks([12, 14, 16, 18])
    ax.set_yticklabels(["$12", "$14", "$16", "$18"], fontsize=11, color=MUTED)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.set_xticks([datetime(2026, m, 1) for m in range(1, 11)])
    plt.setp(ax.get_xticklabels(), fontsize=12, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.035, 0.955, "Ford Gave Back Its Battery Rally, and Then Some",
             fontsize=24, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.905, "Ford Motor Co. closing share price, Dec. 31, 2025 to Oct. 2, 2026",
             fontsize=13.5, color=MUTED, ha="left", va="top")

    fig.text(0.035, 0.030,
             "Sources: Nasdaq closing prices (Ford, GM), CNBC (S&P 500), Ford's Q3 2026 U.S. sales "
             "release, NHTSA recall 26V578. Prices are not adjusted for dividends.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"ford-ytd-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
