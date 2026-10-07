#!/usr/bin/env python3
"""
make-trade-gap-2026-chart.py  DATA_DIR  [outdir]

The 10/07/26 daily's trade deficit chart (Economy section). Harv attached the
newsletter graphic "Trade Gap Back Above $100B" (monthly U.S. goods and services
trade deficit, Jan. 2025 to Aug. 2026; Mar '25 $133.0B, Oct '25 low $37.4B,
Aug '26 $105.6B; "Source: U.S. Census Bureau & BEA, Oct. 6, 2026"). Emits BOTH:

  trade-gap-100726.png      plain HB monogram    -> RE email + Agent Hub
  trade-gap-100726-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds bopgstb.csv, pulled 10/07/26 from
  fred.stlouisfed.org/graph/fredgraph.csv?id=BOPGSTB&cosd=2024-10-01
(Trade Balance: Goods and Services, Balance of Payments Basis, millions of
dollars, seasonally adjusted; the vintage that carries the Oct. 6 release).

=============================================================================
VERIFICATION 10/07/26
=============================================================================
BEA/Census release "U.S. International Trade in Goods and Services, August
2026" (Oct. 6, 2026, BEA 26-44, CB 26-160), verbatim: "the goods and services
deficit was $105.6 billion in August, up $12.7 billion from $92.8 billion in
July, revised" and "+13.7%". FRED: Aug -105,572, Jul -92,826 (105,572 / 92,826
= +13.73%). All three labeled points on the supplied graphic match FRED exactly:
Mar 2025 -132,983 ($133.0B), Oct 2025 -37,376 ($37.4B), Aug 2026 -105,572.
August is the widest gap since March 2025 (no month from Apr 2025 to Jul 2026
exceeds $92.8B). Release also: year to date the deficit is DOWN $138.2B, or
19.9%, from the same period of 2025 (the early 2025 pre tariff import rush);
August goods imports rose $17.4B on a Census basis, capital goods +$6.2B,
semiconductors +$2.4B; the goods deficit with Taiwan was $18.3B, third after
Mexico ($27.7B) and Vietnam ($24.0B).

matplotlib only; build with python3.13 on Mac.
"""
import csv
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
STAMP = "100726"

CREAM = "#fdf6e8"
INK = "#1f2933"
ORANGE = "#dd6b20"
DEEP = "#b7521a"
GRID = "#d8cdb8"
MUTED = "#8a8172"


def b1(millions):
    return (Decimal(millions) / 1000).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def load():
    rows = []
    for r in csv.DictReader(open(os.path.join(DATA, "bopgstb.csv"))):
        d = datetime.strptime(r["observation_date"], "%Y-%m-%d")
        if d >= datetime(2025, 1, 1):
            rows.append((d, -Decimal(r["BOPGSTB"])))          # deficit as a positive number
    by = dict(rows)
    assert rows[-1][0] == datetime(2026, 8, 1), rows[-1]
    assert b1(by[datetime(2026, 8, 1)]) == Decimal("105.6")
    assert b1(by[datetime(2026, 7, 1)]) == Decimal("92.8")
    assert (by[datetime(2026, 8, 1)] / by[datetime(2026, 7, 1)] - 1) * 100 > Decimal("13.65")
    assert b1(by[datetime(2025, 3, 1)]) == Decimal("133.0")
    assert b1(by[datetime(2025, 10, 1)]) == Decimal("37.4")
    peak = max(rows, key=lambda t: t[1])
    low = min(rows, key=lambda t: t[1])
    assert peak[0] == datetime(2025, 3, 1) and low[0] == datetime(2025, 10, 1)
    between = [v for d, v in rows if datetime(2025, 4, 1) <= d <= datetime(2026, 7, 1)]
    assert max(between) < by[datetime(2026, 8, 1)]                # widest since March 2025
    return rows


def build():
    rows = load()
    xs = [d for d, _ in rows]
    ys = [float(v) / 1000 for _, v in rows]

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.13, 0.84, 0.66])
    ax.set_facecolor(CREAM)

    ax.fill_between(xs, ys, 0, color=ORANGE, alpha=0.12, lw=0, zorder=1)
    ax.plot(xs, ys, color=ORANGE, lw=3.0, solid_joinstyle="round", zorder=3)

    # the three points the story turns on
    pk = (datetime(2025, 3, 1), 133.0)
    lo = (datetime(2025, 10, 1), 37.4)
    nw = (datetime(2026, 8, 1), 105.6)
    ax.scatter([pk[0], lo[0]], [pk[1], lo[1]], s=80, color=CREAM, edgecolor=DEEP, linewidth=2.2, zorder=5)
    ax.annotate("March 2025: $133.0B\nimports rushed in ahead of tariffs", xy=pk, xytext=(20, 4),
                textcoords="offset points", fontsize=12, color=INK, ha="left", va="center",
                linespacing=1.25, zorder=6)
    ax.annotate("October 2025: $37.4B, the low", xy=lo, xytext=(0, -22), textcoords="offset points",
                fontsize=12, color=INK, ha="center", va="top", zorder=6)
    ax.scatter([nw[0]], [nw[1]], s=120, color=ORANGE, edgecolor=CREAM, linewidth=2, zorder=6)
    ax.annotate("$105.6B", xy=nw, xytext=(-20, 6), textcoords="offset points", fontsize=19,
                fontweight="bold", color="white", ha="right", va="center", zorder=7,
                bbox=dict(boxstyle="round,pad=0.35", facecolor=ORANGE, edgecolor="none"))
    ax.text(datetime(2026, 8, 10), 141, "August 2026, up 13.7%\nfrom July, the widest\ngap since March 2025",
            fontsize=11.5, color=DEEP, ha="right", va="top", linespacing=1.25, zorder=6)

    ax.set_ylim(0, 150)
    ax.set_xlim(datetime(2024, 12, 10), datetime(2026, 9, 25))
    ax.set_yticks([0, 30, 60, 90, 120, 150])
    ax.set_yticklabels(["$0", "$30B", "$60B", "$90B", "$120B", "$150B"], fontsize=11, color=MUTED)
    ticks = [datetime(2025, 1, 1), datetime(2025, 4, 1), datetime(2025, 7, 1), datetime(2025, 10, 1),
             datetime(2026, 1, 1), datetime(2026, 4, 1), datetime(2026, 8, 1)]
    ax.set_xticks(ticks)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax.get_xticklabels(), fontsize=12, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.035, 0.955, "The Trade Gap Is Back Above $100 Billion", fontsize=25, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.900, "Monthly U.S. trade deficit in goods and services, seasonally adjusted",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.030,
             "Source: U.S. Census Bureau and Bureau of Economic Analysis, released Oct. 6, 2026 "
             "(balance of payments basis, via FRED).",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"trade-gap-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
