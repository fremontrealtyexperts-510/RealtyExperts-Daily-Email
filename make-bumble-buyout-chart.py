#!/usr/bin/env python3
"""
make-bumble-buyout-chart.py  DATA_DIR  [outdir]

The 10/14/26 daily's stock chart. Harv attached the newsletter's "guess the
stock chart" graphic: "$5.95 +66.67% (+2.38) YTD", a 2026 line that drifts
from about $3.60 to $2.50 and then spikes in the last two sessions, "Source:
Google Finance, Close as of Oct. 13, 2026". Market Briefs' answer: Bumble.
Emits BOTH:

  bumble-buyout-101426.png      plain HB monogram    -> RE email + Agent Hub
  bumble-buyout-101426-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds bmbl-nasdaq.json, the Nasdaq historical API pull
(api.nasdaq.com/api/quote/BMBL/historical, Dec. 1, 2025 to Oct. 14, 2026,
fetched Oct. 14, 2026 about 8:10 AM PT; Yahoo's chart API was answering 429).

=============================================================================
VERIFICATION 10/14/26
=============================================================================
* Headline holds: Dec. 31, 2025 close $3.57, Oct. 13, 2026 close $5.95,
  up $2.38 = 66.67%. CNBC's quote service also shows the $5.95 prior close.
* The deal, from Bumble's own release (8-K Exhibit 99.1, Oct. 13, 2026,
  8:24 AM ET): Ithaca Holdings, all cash, "valuing the Company at $1.3 billion",
  "$6.05 per share", "approximately 138% premium to the unaffected closing
  share price on October 9, 2026". Oct. 9 close $2.54; 6.05 / 2.54 = 2.38x.
* Monday Oct. 12 closed $3.80 on 42.3 million shares after reports of
  advanced talks at about a $1 billion valuation; Tuesday $5.95 on 118 million.
* The newsletter's YTD frame is right but hides the shape: the stock had
  slid to $2.50 (Oct. 7, the 2026 low) from a $4.47 April high, so the
  move that matters is Friday to Tuesday, up 134%.

matplotlib; build with python3.13 on Mac.
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
STAMP = "101426"
DEAL = 6.05

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e05a47"
DEEP = "#b8432f"
BLUE = "#2b6cb0"
GREEN = "#2f7d4f"
GRID = "#d8cdb8"
MUTED = "#8a8172"
ORANGE = "#d9822b"


def pct(a, b):
    return float(((Decimal(str(a)) / Decimal(str(b)) - 1) * 100).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP))


def load():
    d = json.load(open(os.path.join(DATA, "bmbl-nasdaq.json")))
    rows = d["data"]["tradesTable"]["rows"]
    s = {datetime.strptime(r["date"], "%m/%d/%Y"): float(r["close"].strip("$").replace(",", ""))
         for r in rows}
    start = s[datetime(2025, 12, 31)]
    fri, mon, tue = s[datetime(2026, 10, 9)], s[datetime(2026, 10, 12)], s[datetime(2026, 10, 13)]
    assert (start, fri, mon, tue) == (3.57, 2.54, 3.80, 5.95), (start, fri, mon, tue)
    assert pct(tue, start) == 66.67, pct(tue, start)
    ser = sorted((k, v) for k, v in s.items() if datetime(2025, 12, 31) <= k <= datetime(2026, 10, 13))
    pre = [(k, v) for k, v in ser if datetime(2026, 1, 1) <= k < datetime(2026, 10, 12)]
    hi = max(pre, key=lambda t: t[1])
    lo = min(pre, key=lambda t: t[1])
    assert hi == (datetime(2026, 4, 21), 4.47) and lo == (datetime(2026, 10, 7), 2.50), (hi, lo)
    return ser, start, fri, mon, tue, hi, lo


def build():
    ser, start, fri, mon, tue, hi, lo = load()
    xs = [k for k, _ in ser]
    ys = [v for _, v in ser]

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.065, 0.12, 0.765, 0.69])
    ax.set_facecolor(CREAM)

    ax.fill_between(xs, 2.0, ys, color="#dbe6f3", lw=0, zorder=1)
    ax.plot(xs, ys, color=BLUE, lw=2.6, solid_joinstyle="round", zorder=4)

    # deal price
    ax.axhline(DEAL, color=GREEN, lw=1.8, ls=(0, (5, 3)), zorder=3)
    ax.text(datetime(2026, 1, 6), DEAL + 0.08, "Buyout price: $6.05 a share in cash",
            fontsize=13, fontweight="bold", color=GREEN, ha="left", va="bottom")

    # start of year
    ax.scatter([xs[0]], [start], s=60, color=BLUE, edgecolor=CREAM, linewidth=1.5, zorder=5)
    ax.annotate(f"Dec. 31: ${start:.2f}", xy=(xs[0], start), xytext=(4, 40),
                textcoords="offset points", fontsize=12.5, color=INK, ha="left", va="bottom",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.9, shrinkA=0, shrinkB=5))

    # April high
    ax.scatter([hi[0]], [hi[1]], s=50, color=BLUE, edgecolor=CREAM, linewidth=1.5, zorder=5)
    ax.annotate(f"2026 high ${hi[1]:.2f}\n(April 21)", xy=hi, xytext=(0, 12),
                textcoords="offset points", fontsize=12, color=INK, ha="center", va="bottom")

    # Friday, unaffected
    ax.scatter([datetime(2026, 10, 9)], [fri], s=80, color=CORAL, edgecolor=CREAM,
               linewidth=1.8, zorder=6)
    ax.annotate(f"Fri. Oct. 9: ${fri:.2f}\nbefore the news", xy=(datetime(2026, 10, 9), fri),
                xytext=(-16, -6), textcoords="offset points", fontsize=12.5, color=DEEP,
                fontweight="bold", ha="right", va="top")

    # Monday, talks reported
    ax.scatter([datetime(2026, 10, 12)], [mon], s=70, color=ORANGE, edgecolor=CREAM,
               linewidth=1.8, zorder=6)
    ax.annotate(f"Mon.: ${mon:.2f}\ntalks reported", xy=(datetime(2026, 10, 12), mon),
                xytext=(-16, 0), textcoords="offset points", fontsize=12.5, color=ORANGE,
                fontweight="bold", ha="right", va="center")

    # Tuesday close
    ax.scatter([datetime(2026, 10, 13)], [tue], s=150, color=DEEP, edgecolor=CREAM,
               linewidth=2, zorder=7)
    ax.annotate(f"Tue.: ${tue:.2f}", xy=(datetime(2026, 10, 13), tue), xytext=(-16, -2),
                textcoords="offset points", fontsize=15, fontweight="bold", color="white",
                ha="right", va="top", zorder=8,
                bbox=dict(boxstyle="round,pad=0.35", facecolor=DEEP, edgecolor="none"))

    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b."))
    ax.set_xlim(datetime(2025, 12, 24), datetime(2026, 10, 20))
    ax.set_ylim(2.0, 6.45)
    ax.set_yticks([2, 3, 4, 5, 6])
    ax.set_yticklabels(["$2", "$3", "$4", "$5", "$6"], fontsize=12, color=MUTED)
    ax.tick_params(axis="x", labelsize=12.5, colors=MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    for lab in ax.get_xticklabels():
        lab.set_color(MUTED)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # right hand stat column
    fig.text(0.855, 0.74, "Since Friday", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(0.855, 0.705, f"+{pct(tue, fri):.0f}%", fontsize=28, fontweight="bold",
             color=DEEP, ha="left", va="top")
    fig.text(0.855, 0.58, "This year", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(0.855, 0.545, f"+{pct(tue, start):.1f}%", fontsize=28, fontweight="bold",
             color=BLUE, ha="left", va="top")
    fig.text(0.855, 0.42, "Deal value", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(0.855, 0.385, "$1.3B", fontsize=28, fontweight="bold", color=GREEN,
             ha="left", va="top")

    fig.text(0.035, 0.955, "Bumble Jumps On A $6.05 Buyout", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895, "Bumble (BMBL) daily closing price, 2026. Ithaca Holdings agreed "
             "Oct. 13 to take the dating app private.", fontsize=13.2, color=MUTED,
             ha="left", va="top")
    fig.text(0.035, 0.035, "Source: Nasdaq daily closes through Oct. 13, 2026; deal terms from "
             "Bumble's Oct. 13, 2026 announcement (SEC Form 8-K).", fontsize=10.2,
             color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"bumble-buyout-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
