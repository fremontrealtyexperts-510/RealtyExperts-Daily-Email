#!/usr/bin/env python3
"""
make-ko-ytd-2026-chart.py  DATA_DIR  [outdir]

The 10/26/26 daily's stock chart. Harv attached the newsletter's "Coca-Cola (KO)"
graphic: daily line with area fill, "$69.91" start label, "$92.71" end pill,
"Up 32.6% in 2026", source Google Finance, Oct. 23, 2026 close. Emits BOTH:

  ko-ytd-102626.png      plain HB monogram    -> RE email + Agent Hub
  ko-ytd-102626-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

No Coca-Cola logo: the graphic carried the trademark script, ours does not.

DATA_DIR holds three Yahoo chart API pulls (query1.finance.yahoo.com/v8/finance/
chart, fetched Oct. 26, 2026 about 9:10 AM PT, during Monday's session; Monday's
partial bar is ignored):
  ko-yahoo.json          KO, interval 1d, Dec. 1, 2025 onward
  ko-max-monthly.json    KO, interval 1mo, Jan. 1985 to Dec. 2025 (the record test)
  gspc-yahoo.json        ^GSPC, interval 1d, Dec. 30, 2025 onward

=============================================================================
VERIFICATION 10/26/26
=============================================================================
* Dec. 31, 2025 close $69.91 and Oct. 23, 2026 close $92.71 both match the
  graphic. 92.71 / 69.91 = up 32.61%, so its 32.6% holds. Its "$69.91" sits
  under a "Jan" tick, but it is the Dec. 31 close (Jan. 2 was $69.12).
* 2026 high close $95.34 on Oct. 22 (up 2.87% that day), then down 2.76% on
  Oct. 23. Highest monthly HIGH from 1985 through Dec. 2025 was $74.38 (Apr.
  2025), so every 2026 close above that is a record and Oct. 22 is the record.
* 2026 low close $67.54 on Jan. 7.
* S&P 500 (^GSPC) Dec. 31, 2025 close 6,845.50, Oct. 23 close 7,623.68: up 11.37%.
* Earnings: The Coca-Cola Company release of Sept. 29, 2026 (investors site,
  press release 1173): third quarter results "Oct. 27 before the New York Stock
  Exchange opens", call 8:30 a.m. ET. Market Briefs' "reports earnings this
  week" holds.

matplotlib; build with python3.13 on Mac.
"""
import json
import os
import sys
from datetime import date, datetime, timezone
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
STAMP = "102626"

CREAM = "#fdf6e8"
INK = "#1f2933"
GREEN = "#2f7d4f"
DEEP = "#1f5c39"
FILL = "#d9eadb"
GRID = "#d8cdb8"
MUTED = "#8a8172"
CORAL = "#d9643a"

START, END = date(2025, 12, 31), date(2026, 10, 23)


def pct(a, b, places="0.01"):
    # round ONCE from the raw ratio; formatting a 2 place value to 1 place
    # double rounds (29.549 -> 29.55 -> "29.6")
    return float(((Decimal(str(a)) / Decimal(str(b)) - 1) * 100).quantize(
        Decimal(places), rounding=ROUND_HALF_UP))


def daily(fname):
    r = json.load(open(os.path.join(DATA, fname)))["chart"]["result"][0]
    et = ZoneInfo("America/New_York")
    s = {}
    for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]):
        if c is not None:
            s[datetime.fromtimestamp(t, et).date()] = round(c, 2)
    return s


def load():
    s = daily("ko-yahoo.json")
    start, fri = s[START], s[END]
    assert (start, fri) == (69.91, 92.71), (start, fri)
    assert s[date(2026, 1, 2)] == 69.12, s[date(2026, 1, 2)]
    assert pct(fri, start) == 32.61, pct(fri, start)
    ser = sorted((k, v) for k, v in s.items() if START <= k <= END)
    y26 = [(k, v) for k, v in ser if k.year == 2026]
    hi = max(y26, key=lambda t: t[1])
    lo = min(y26, key=lambda t: t[1])
    assert hi == (date(2026, 10, 22), 95.34), hi
    assert lo == (date(2026, 1, 7), 67.54), lo
    assert pct(95.34, s[date(2026, 10, 21)]) == 2.87
    assert pct(fri, 95.34) == -2.76

    # record test: every monthly HIGH through Dec. 2025 sits below the 2026 high
    m = json.load(open(os.path.join(DATA, "ko-max-monthly.json")))["chart"]["result"][0]
    highs = [(datetime.fromtimestamp(t, timezone.utc).date(), h)
             for t, h in zip(m["timestamp"], m["indicators"]["quote"][0]["high"]) if h]
    assert highs[0][0] <= date(1985, 1, 1) and highs[-1][0] >= date(2025, 12, 1), (highs[0], highs[-1])
    prior = max(highs, key=lambda t: t[1])
    assert round(prior[1], 2) == 74.38 and prior[0] == date(2025, 4, 1), prior

    g = daily("gspc-yahoo.json")
    spx = pct(g[END], g[START])
    assert (g[START], g[END], spx) == (6845.5, 7623.68, 11.37), (g[START], g[END], spx)
    return ser, start, fri, hi, lo, spx


def build():
    ser, start, fri, hi, lo, spx = load()
    ytd = pct(fri, start, "0.1")
    assert ytd == 32.6, ytd
    spx1 = pct(7623.68, 6845.5, "0.1")
    assert spx1 == 11.4, spx1
    xs = [datetime(k.year, k.month, k.day) for k, _ in ser]
    ys = [v for _, v in ser]

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.065, 0.12, 0.76, 0.69])
    ax.set_facecolor(CREAM)

    FLOOR = 62
    ax.fill_between(xs, FLOOR, ys, color=FILL, lw=0, zorder=1, alpha=0.9)
    ax.plot(xs, ys, color=GREEN, lw=2.6, solid_joinstyle="round", zorder=4)

    # where the year started, so the gain reads at a glance
    ax.axhline(start, color="#b9ad93", lw=1.3, ls=(0, (4, 4)), zorder=2)

    ax.scatter([xs[0]], [start], s=70, color=CREAM, edgecolor=GREEN, linewidth=2.2, zorder=5)
    # label sits BELOW the January dip (low $67.54 on Jan. 7) so the line stays clear
    ax.annotate(f"Dec. 31: ${start:.2f}", xy=(xs[0], start), xytext=(6, -44),
                textcoords="offset points", fontsize=13, fontweight="bold", color=INK,
                ha="left", va="top")

    # record close, the day before Friday's pullback
    hx = datetime(hi[0].year, hi[0].month, hi[0].day)
    ax.scatter([hx], [hi[1]], s=60, color=CORAL, edgecolor=CREAM, linewidth=1.5, zorder=6)
    ax.annotate(f"Record close: ${hi[1]:.2f}\n(Oct. 22)", xy=(hx, hi[1]), xytext=(-14, 6),
                textcoords="offset points", fontsize=12, color=CORAL, fontweight="bold",
                ha="right", va="bottom")

    # Friday close pill, well BELOW the line with a leader: the Sept. to Oct. line
    # never closes under $85.65, and a pill closer in hid that stretch (first render)
    fx = xs[-1]
    ax.scatter([fx], [fri], s=130, color=DEEP, edgecolor=CREAM, linewidth=2, zorder=7)
    ax.annotate(f"Oct. 23: ${fri:.2f}", xy=(fx, fri), xytext=(-10, -150), textcoords="offset points",
                fontsize=17, fontweight="bold", color="white", ha="right", va="top",
                zorder=8, annotation_clip=False,
                arrowprops=dict(arrowstyle="-", color=DEEP, lw=1.3, shrinkA=0, shrinkB=6),
                bbox=dict(boxstyle="round,pad=0.38", facecolor=DEEP, edgecolor="none"))

    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b."))
    ax.set_xlim(datetime(2025, 12, 22), datetime(2026, 10, 31))
    ax.set_ylim(FLOOR, 101)
    ax.set_yticks([65, 70, 75, 80, 85, 90, 95, 100])
    ax.set_yticklabels([f"${v}" for v in [65, 70, 75, 80, 85, 90, 95, 100]], fontsize=12.5, color=MUTED)
    ax.tick_params(axis="x", labelsize=12.5, colors=MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # right hand stat column
    fig.text(0.862, 0.70, "Coca-Cola this year", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(0.862, 0.665, f"+{ytd:.1f}%", fontsize=27, fontweight="bold", color=GREEN,
             ha="left", va="top")
    fig.text(0.862, 0.55, "S&P 500 this year", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(0.862, 0.515, f"+{spx1:.1f}%", fontsize=27, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.862, 0.40, "Q3 results", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(0.862, 0.365, "Oct. 27", fontsize=27, fontweight="bold", color=CORAL,
             ha="left", va="top")
    fig.text(0.862, 0.295, "before the opening bell", fontsize=11.5, color=MUTED,
             ha="left", va="top")

    fig.text(0.035, 0.955, f"Coca-Cola Is Up {ytd:.1f}% in 2026", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895,
             "Coca-Cola (KO) daily closing price, 2026, through Friday, Oct. 23.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035,
             "Source: Yahoo Finance daily closes, Dec. 31, 2025 through Oct. 23, 2026. Results date: The Coca-Cola Company, Sept. 29, 2026.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"ko-ytd-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
