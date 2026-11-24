#!/usr/bin/env python3
"""
make-nvidia-rollercoaster-2026-chart.py  YAHOO_NVDA_JSON  NASDAQ_NVDA_JSON  CLOSE_DAY  CLOSE  STAMP  [outdir]
       [--midday PRICE "LABEL"]

The 11/24/26 daily's Stocks chart. Harv supplied "Nvidia's 2026 Rollercoaster"
(daily closes YTD through Nov. 23: -11.5% YTD, record high $239.24, "scandal low"
$125.53, $165.05 and +31% Monday). A supplied graphic is a design brief, not a
data source. Checked against Yahoo and the Nasdaq API:
  * Dec. 31, 2025 close $186.50; Nov. 23 close $165.05 = -11.5% YTD. Correct.
  * Record close $239.24 on Oct. 6. Correct. The May peak is $235.74 (May 14).
  * $125.53 is the Nov. 20 close and the 2026 low. Correct. Relabeled neutrally
    ("Nov. 20 low"); the report copy stays non-political.
Closes run through CLOSE_DAY (the latest official close); YTD is computed on
CLOSE. Every Yahoo close from Dec. 31, 2025 through CLOSE_DAY must equal the
Nasdaq API close to the cent, except CLOSE_DAY itself when Nasdaq has not posted
it yet (it lags hours; its quote endpoint shows the AFTER-HOURS price as the close,
154.02 vs the official 155.38 on 11/24): CLOSE, taken from CNBC, must then equal
Yahoo's close and the footer says so. --midday adds a hollow, dotted last point for a
live price (the 11/24 report shipped at midday on Harv's call) and says so.

Emits BOTH:
  nvidia-rollercoaster-MMDDYY.png      plain HB monogram    -> RE email + Agent Hub
  nvidia-rollercoaster-MMDDYY-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app
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

ARGS = sys.argv[1:]
MID = None
if "--midday" in ARGS:
    i = ARGS.index("--midday")
    MID = (Decimal(ARGS[i + 1]), ARGS[i + 2])
    ARGS = ARGS[:i] + ARGS[i + 3:]
YJ, NJ = ARGS[0], ARGS[1]
TODAY = date.fromisoformat(ARGS[2])
TODAY_CLOSE = Decimal(ARGS[3])
STAMP = ARGS[4]
OUTDIR = ARGS[5] if len(ARGS) > 5 else "."
ET = ZoneInfo("America/New_York")
LATE = False

CREAM = "#fdf6e8"
INK = "#1f2933"
GRID = "#e6dcc8"
MUTED = "#8a8172"
GREEN = "#3c8d3f"
FILL = "#e3ecd7"
CORAL = "#e2574c"
BASE_DAY, BASE = date(2025, 12, 31), Decimal("186.50")
REC_DAY, REC = date(2026, 10, 6), Decimal("239.24")
LOW_DAY, LOW = date(2026, 11, 20), Decimal("125.53")
MON = (date(2026, 11, 23), Decimal("165.05"))


def money(x):
    return Decimal(str(x)).quantize(Decimal("0.01"), ROUND_HALF_UP)


def pct(x):
    return Decimal(str(x)).quantize(Decimal("0.1"), ROUND_HALF_UP)


def mdy(d0):
    m = d0.strftime("%b.").replace("May.", "May").replace("Sep.", "Sept.").replace("Jun.", "June").replace("Jul.", "July")
    return f"{m} {d0.day}"


def load():
    d = json.load(open(YJ))["chart"]["result"][0]
    y = [(datetime.fromtimestamp(t, ET).date(), money(c)) for t, c in zip(d["timestamp"], d["indicators"]["quote"][0]["close"]) if c]
    rows = json.load(open(NJ))["data"]["tradesTable"]["rows"]
    n = {datetime.strptime(r["date"], "%m/%d/%Y").date(): Decimal(r["close"].replace("$", "").replace(",", "")) for r in rows}
    global LATE
    checked = 0
    for d0, c in y:
        if BASE_DAY <= d0 <= TODAY:
            if d0 == TODAY and d0 not in n:
                LATE = True          # Nasdaq history posts the day's close hours later; CLOSE (from CNBC) is checked below
                continue
            assert c == n[d0], (d0, c, n[d0])
            checked += 1
    assert dict(y)[TODAY] == TODAY_CLOSE, (dict(y)[TODAY], TODAY, TODAY_CLOSE)
    pts = [(d0, c) for d0, c in y if BASE_DAY <= d0 <= TODAY]
    return pts, checked


def build():
    pts, checked = load()
    px = dict(pts)
    assert px[BASE_DAY] == BASE and px[REC_DAY] == REC and px[LOW_DAY] == LOW and px[MON[0]] == MON[1], "anchor"
    yr = [(d0, c) for d0, c in pts if d0 >= date(2026, 1, 1)]
    assert max(yr, key=lambda r: r[1]) == (REC_DAY, REC) and min(yr, key=lambda r: r[1]) == (LOW_DAY, LOW)
    assert pct((MON[1] / BASE - 1) * 100) == Decimal("-11.5")          # the graphic's figure, at its date
    ytd = (TODAY_CLOSE / BASE - 1) * 100
    prev = pts[-2][1]
    day = (TODAY_CLOSE / prev - 1) * 100
    print(f"checked {checked} closes vs Nasdaq; YTD {pct(ytd)}%; today {pct(day)}% vs {pts[-2][0]} {prev}")

    fig = plt.figure(figsize=(14.0, 7.9), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.15, 0.64, 0.66])
    ax.set_facecolor(CREAM)
    xs = [datetime(d0.year, d0.month, d0.day) for d0, _ in pts]
    ys = [float(c) for _, c in pts]
    ax.fill_between(xs, ys, 100, color=FILL, zorder=1)
    ax.plot(xs, ys, color=GREEN, lw=2.4, zorder=3)
    ax.axhline(float(BASE), color=INK, lw=1.0, ls=(0, (4, 3)), zorder=2)
    ax.text(datetime(2026, 8, 8), float(BASE) - 2.5, f"2025 close ${BASE}", fontsize=11.5, color=INK,
            ha="left", va="top")

    rx = datetime(REC_DAY.year, REC_DAY.month, REC_DAY.day)
    ax.scatter([rx], [float(REC)], color=GREEN, s=60, zorder=4, edgecolor=CREAM, linewidth=1.5)
    ax.text(rx, float(REC) + 4, f"Record close ${REC}\n{mdy(REC_DAY)}", ha="center", va="bottom", fontsize=12,
            color=INK, linespacing=1.3)
    lx = datetime(LOW_DAY.year, LOW_DAY.month, LOW_DAY.day)
    ax.scatter([lx], [float(LOW)], color=CORAL, s=70, zorder=5, edgecolor=CREAM, linewidth=1.5)
    ax.text(lx - timedelta(days=3), float(LOW) - 1, f"2026 low ${LOW}\n{mdy(LOW_DAY)}", ha="right", va="center",
            fontsize=12, color=INK, linespacing=1.3)
    tx = xs[-1]
    ax.scatter([tx], [float(TODAY_CLOSE)], color=GREEN, s=90, zorder=5, edgecolor=CREAM, linewidth=1.6)
    if MID is None:
        ax.text(tx + timedelta(days=4), float(TODAY_CLOSE), f"${TODAY_CLOSE}\n{mdy(TODAY)}", ha="left", va="center",
                fontsize=13.5, fontweight="bold", color=INK, linespacing=1.3)
    else:
        mx = tx + timedelta(days=1)
        ax.plot([tx, mx], [float(TODAY_CLOSE), float(MID[0])], color=GREEN, lw=2.2, ls=(0, (1.5, 1.2)), zorder=3)
        ax.scatter([mx], [float(MID[0])], s=80, zorder=6, facecolor=CREAM, edgecolor=GREEN, linewidth=2)
        ax.text(tx + timedelta(days=5), float(TODAY_CLOSE) + 6, f"${TODAY_CLOSE}\n{mdy(TODAY)} close", ha="left",
                va="center", fontsize=12.5, fontweight="bold", color=INK, linespacing=1.3)
        ax.text(tx + timedelta(days=5), float(MID[0]) - 9, f"${MID[0]}\n{MID[1]}", ha="left", va="center",
                fontsize=12.5, color=MUTED, linespacing=1.3)

    ax.set_ylim(100, 262)
    ax.set_xlim(datetime(2025, 12, 24), datetime(2026, 12, 15))
    ax.set_yticks([100, 125, 150, 175, 200, 225, 250])
    ax.set_yticklabels([f"${v}" for v in [100, 125, 150, 175, 200, 225, 250]], fontsize=12, color=MUTED)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda v, _: mdates.num2date(v).strftime("%b").replace("Sep", "Sept") if mdates.num2date(v).month < 12 else ""))
    ax.tick_params(axis="x", labelsize=12, colors=MUTED, length=0, pad=8)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    col = CORAL if ytd < 0 else GREEN
    sign = "+" if ytd > 0 else ("−" if ytd < 0 else "")
    fig.text(0.795, 0.70, f"{sign}{abs(pct(ytd))}%", fontsize=44, fontweight="bold", color=col, ha="left", va="center")
    fig.text(0.80, 0.615, "year to date" if MID is None else f"year to date at the\n{mdy(TODAY)} close", fontsize=17 if MID is None else 14.5,
             color=INK, ha="left", va="center", linespacing=1.3)
    fig.text(0.80, 0.52, f"Down {abs(pct((TODAY_CLOSE / REC - 1) * 100))}% from the\nOct. 6 record", fontsize=13.5,
             color=INK, ha="left", va="top", linespacing=1.45)
    fig.text(0.80, 0.40, f"Up {pct((TODAY_CLOSE / LOW - 1) * 100)}% from the\nNov. 20 low", fontsize=13.5,
             color=MUTED, ha="left", va="top", linespacing=1.45)

    fig.text(0.035, 0.955, "Nvidia's 2026 Rollercoaster", fontsize=26, fontweight="bold", color=INK, ha="left", va="top")
    sub = f"Daily closing price, Dec. 31, 2025 to {mdy(TODAY)}, 2026" + ("" if MID is None else f", plus {MID[1]}")
    fig.text(0.035, 0.897, sub, fontsize=13.5, color=MUTED, ha="left", va="top")
    chk = "Closes checked against the Nasdaq to the cent" + (f"; the {mdy(TODAY)} close against CNBC" if LATE else "")
    fig.text(0.035, 0.022, chk + ("." if MID is None else f"; {MID[1]} is a live price, not a close.") + "\n"
             "Source: Nasdaq via Yahoo Finance.", fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.45)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"nvidia-rollercoaster-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    print("wrote", out)
