"""
make-nvidia-ytd-2026-chart.py  YAHOO_JSON  NASDAQ_JSON  [outdir]

The 11/13/26 daily's Stocks chart. Harv supplied "Nvidia Erases Its 2026 Gains"
(NVDA share price year to date, -10.9%, Nov. 12 close $166.19). Rebuilt as OUR
chart from two independent daily close histories that must agree to the cent.

Emits BOTH:
  nvidia-ytd-111326.png      plain HB monogram    -> RE email + Agent Hub
  nvidia-ytd-111326-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

YAHOO_JSON  = query1.finance.yahoo.com/v8/finance/chart/NVDA?interval=1d (Dec 20, 2025 on)
NASDAQ_JSON = api.nasdaq.com/api/quote/NVDA/historical?assetclass=stocks&fromdate=2025-12-30&todate=2026-11-12

=============================================================================
VERIFICATION 11/13/26
=============================================================================
* 220 sessions, Dec. 30, 2025 to Nov. 12, 2026: every Yahoo close equals the
  Nasdaq close to the cent, no session missing from either side.
* Dec. 31, 2025 close $186.50; Nov. 12, 2026 close $166.19 = -10.89%, the
  supplied graphic's -10.9%.
* 2026 high close $239.24 on Oct. 6; Nov. 12 is down 30.5% from it. The only
  lower 2026 close is $165.17 on March 30, so Nov. 12 is the lowest close
  since then.
* Nvidia's 8-K (filed Nov. 12): the board accepted Jensen Huang's resignation
  as CEO on Nov. 11, effective immediately; the marker sits on that session.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import json
import os
import sys
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

YSRC, NSRC = sys.argv[1], sys.argv[2]
OUTDIR = sys.argv[3] if len(sys.argv) > 3 else "."
STAMP = "111326"
ET = ZoneInfo("America/New_York")
END = "2026-11-12"

CREAM = "#fdf6e8"
INK = "#1f2933"
RED = "#c8102e"
GRID = "#e6dcc8"
MUTED = "#8a8172"
SAND = "#b9a888"


def load():
    y = json.load(open(YSRC))["chart"]["result"][0]
    yd = {datetime.fromtimestamp(t, ET).strftime("%Y-%m-%d"): c
          for t, c in zip(y["timestamp"], y["indicators"]["quote"][0]["close"]) if c is not None}
    n = json.load(open(NSRC))["data"]["tradesTable"]["rows"]
    nd = {datetime.strptime(r["date"], "%m/%d/%Y").strftime("%Y-%m-%d"):
          Decimal(r["close"].replace("$", "").replace(",", "")) for r in n}
    keys = sorted(k for k in nd if "2025-12-31" <= k <= END)
    ykeys = sorted(k for k in yd if "2025-12-31" <= k <= END)
    assert keys == ykeys, (set(keys) ^ set(ykeys))
    for k in keys:   # two independent histories, to the cent
        assert Decimal(str(yd[k])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) == nd[k], (k, yd[k], nd[k])
    base = nd["2025-12-31"]
    last = nd[END]
    assert (base, last) == (Decimal("186.50"), Decimal("166.19")), (base, last)
    ytd = (last / base - 1) * 100
    assert ytd.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP) == Decimal("-10.9"), ytd
    s26 = [k for k in keys if k >= "2026-01-01"]
    hi = max(s26, key=lambda k: nd[k])
    assert (hi, nd[hi]) == ("2026-10-06", Decimal("239.24")), (hi, nd[hi])
    lower = [k for k in s26 if nd[k] < last]
    assert lower == ["2026-03-30"], lower
    return [(date.fromisoformat(k), float(nd[k])) for k in keys], base, last, ytd, hi, nd[hi]


def build():
    pts, base, last, ytd, hi, hiv = load()
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    fig = plt.figure(figsize=(14.0, 7.8), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.13, 0.80, 0.64])
    ax.set_facecolor(CREAM)

    ax.fill_between(xs, 150, ys, color=RED, alpha=0.07, lw=0, zorder=2)
    ax.plot(xs, ys, color=RED, lw=2.6, zorder=4)
    ax.axhline(float(base), color=INK, lw=1.3, ls=(0, (5, 4)), zorder=3, alpha=0.7)
    ax.text(date(2026, 11, 20), float(base) + 1.4, f"Dec. 31, 2025\nclose \\${base}", fontsize=12.5, color=INK,
            ha="left", va="bottom", linespacing=1.15)

    hd = date.fromisoformat(hi)
    ax.plot([hd], [float(hiv)], marker="o", ms=9, color=INK, zorder=5)
    ax.text(hd, float(hiv) + 2.4, f"2026 high \\${hiv}\nOct. 6", fontsize=12.5, color=INK, ha="center",
            va="bottom", linespacing=1.2)

    rd = date(2026, 11, 11)
    rv = [p[1] for p in pts if p[0] == rd][0]
    ax.annotate("Nov. 11: CEO resignation", xy=(rd, rv), xytext=(date(2026, 9, 2), 172.5), fontsize=12,
                color=MUTED, ha="center", va="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.1))

    ld = xs[-1]
    ax.plot([ld], [ys[-1]], marker="o", ms=12, color=RED, zorder=6)
    ax.text(date(2026, 11, 20), ys[-1] + 0.2, f"\\${last}", fontsize=24, fontweight="bold", color=RED,
            ha="left", va="center")
    ax.text(date(2026, 11, 20), ys[-1] - 6.0, "Nov. 12 close", fontsize=12.5, color=INK, ha="left", va="center")

    for g in (160, 180, 200, 220, 240):
        ax.axhline(g, color=GRID, lw=1, zorder=1, ls=(0, (4, 4)))
        ax.text(date(2025, 12, 24), g, f"\\${g}", ha="right", va="center", fontsize=12, color=MUTED)
    ax.set_xlim(date(2025, 12, 26), date(2027, 1, 18))
    ax.set_ylim(150, 252)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_xticks([date(2026, m, 1) for m in (1, 3, 5, 7, 9, 11)])
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.tick_params(axis="x", length=0, labelsize=13, pad=8)
    for t in ax.get_xticklabels():
        t.set_color(INK)

    fig.text(0.035, 0.955, "Nvidia Erases Its 2026 Gains", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.897, "NVDA daily closing price, Dec. 31, 2025 to Nov. 12, 2026", fontsize=13.5,
             color=MUTED, ha="left", va="top")
    pct = str(ytd.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)).replace("-", "\u2212")
    ax.text(date(2026, 1, 6), 247, f"{pct}%", fontsize=30, fontweight="bold", color=RED, ha="left", va="top")
    ax.text(date(2026, 1, 6), 236.5, "year to date", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.03, "Source: Nasdaq and Yahoo Finance daily closes (identical for all 220 sessions); "
             "Nvidia 8-K filed Nov. 12, 2026.", fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"nvidia-ytd-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
