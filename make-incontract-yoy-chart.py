#!/usr/bin/env python3
"""
make-incontract-yoy-chart.py  HIST_DIR  [outdir]

The 10/15/26 daily's Real Estate chart. No newsletter graphic was supplied;
the day's lead was the MBA weekly survey (30-year contract rate 7.50%, the
highest since November 2023; purchase applications down 4% on the week and
16% below the same week a year ago). This asks the local question with OUR
OWN data: are fewer Bay East buyers signing contracts than a year ago?

Emits BOTH:
  incontract-yoy-101526.png      plain HB monogram    -> RE email + Agent Hub
  incontract-yoy-101526-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

=============================================================================
SOURCE AND BASIS
=============================================================================
HIST_DIR holds 101525.csv and 101526.csv, verbatim dumps of the dated
MLS_Defined_Spread_Sheet_4 exports for Oct. 15, 2025 (a real .xlsx on Drive,
converted cell for cell with openpyxl) and Oct. 15, 2026 (today's sheet via
dump-mls-csv.js). Same calendar day, so no seasonal skew. The listing level
CSVs are never committed; only the counts below.

  For sale     = ACTV, NEW, CS, BOMK, PCH (the five city ledger's live basis,
                 PCH folded in since 10/06/26), all property types.
  In contract  = PEND.
  Board        = the 14 cities present in BOTH exports. Milpitas joined the
                 export in January 2026, so it is left out of every bar.

Counts generated from the files on 10/15/26 (asserted below):
                 for sale         in contract
  14 cities     2,072 -> 1,979    858 -> 686
  Fremont         222 ->   239     94 ->  85
  Hayward         230 ->   189     89 ->  84
  Newark           66 ->    90     35 ->  20
  Union City       41 ->    64     30 ->  23

matplotlib only; build with python3.13 on Mac.
"""
import csv
import os
import sys
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

HIST = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "101526"

CREAM = "#fdf6e8"
INK = "#1f2933"
GRID = "#d8cdb8"
MUTED = "#8a8172"
BLUE = "#2f6f9f"     # for sale
CORAL = "#e2574c"    # in contract
LIVE = {"ACTV", "NEW", "CS", "BOMK", "PCH"}
HEADER = ("MLS No,Status,DOM,Address,Unit,City,Area,LP,SP,BT,SqFt,BR,Bth,PB,"
          "Gar,GarSp,YrBlt,Acres,Lot SqFt,HOA Fee,Freq").split(",")
ROWS = [("BOARD", "14 cities, board wide"), ("FREMONT", "Fremont"),
        ("HAYWARD", "Hayward"), ("NEWARK", "Newark"), ("UNION CITY", "Union City")]


def counts(path):
    with open(path, newline="") as f:
        r = csv.reader(f)
        head = next(r)
        assert head == HEADER, (path, head)
        rows = [dict(zip(HEADER, x)) for x in r]
    rows = [x for x in rows if x["City"] != "MILPITAS"]
    out = {}
    for key, _ in ROWS:
        sel = rows if key == "BOARD" else [x for x in rows if x["City"] == key]
        c = Counter(x["Status"] for x in sel)
        out[key] = (sum(c[s] for s in LIVE), c["PEND"])
    return out


def pct(a, b):
    return int((Decimal(b - a) / Decimal(a) * 100).quantize(Decimal("1"), ROUND_HALF_UP))


def build():
    then = counts(os.path.join(HIST, "101525.csv"))
    now = counts(os.path.join(HIST, "101526.csv"))
    assert then["BOARD"] == (2072, 858) and now["BOARD"] == (1979, 686), (then, now)
    assert then["NEWARK"] == (66, 35) and now["NEWARK"] == (90, 20)

    fig = plt.figure(figsize=(14.0, 8.4), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.22, 0.14, 0.72, 0.66])
    ax.set_facecolor(CREAM)

    h = 0.36
    n = len(ROWS)
    for i, (key, label) in enumerate(ROWS):
        y = n - 1 - i
        for dy, idx, color in [(h / 2 + 0.02, 0, BLUE), (-h / 2 - 0.02, 1, CORAL)]:
            a, b = then[key][idx], now[key][idx]
            p = pct(a, b)
            ax.barh(y + dy, p, height=h, color=color, zorder=3)
            sign = "+" if p > 0 else ("−" if p < 0 else "")
            txt = f"{sign}{abs(p)}%   {a:,} to {b:,}"
            off = 1.4
            ax.text(p + off if p >= 0 else p - off, y + dy, txt, va="center",
                    ha="left" if p >= 0 else "right", fontsize=13.5,
                    fontweight="bold", color=color, zorder=5,
                    bbox=dict(boxstyle="square,pad=0.12", facecolor=CREAM, edgecolor="none"))
        ax.text(-0.035, y, label, transform=ax.get_yaxis_transform(), ha="right",
                va="center", fontsize=15.5, fontweight="bold", color=INK)
        if i == 0:
            ax.axhline(y - 0.62, color=GRID, lw=1.2, zorder=1)

    ax.set_xlim(-78, 92)
    ax.set_ylim(-0.6, n - 0.4)
    ax.axvline(0, color=INK, lw=1.6, zorder=4)
    ax.set_yticks([])
    ax.set_xticks([-50, -25, 0, 25, 50, 75])
    ax.set_xticklabels(["−50%", "−25%", "0", "+25%", "+50%", "+75%"],
                       fontsize=12, color=MUTED)
    ax.tick_params(axis="x", length=0, pad=6)
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # legend chips
    fig.text(0.22, 0.835, "■", color=BLUE, fontsize=18, ha="left", va="center")
    fig.text(0.24, 0.835, "Homes for sale", color=INK, fontsize=14, ha="left", va="center")
    fig.text(0.40, 0.835, "■", color=CORAL, fontsize=18, ha="left", va="center")
    fig.text(0.42, 0.835, "Homes in contract (pending)", color=INK, fontsize=14,
             ha="left", va="center")

    fig.text(0.035, 0.955, "Fewer Homes in Contract Than a Year Ago", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.897, "Change from Oct. 15, 2025 to Oct. 15, 2026, the same day a year apart. "
             "Board wide, supply is down 4%; signed contracts are down 20%.", fontsize=13.2,
             color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035,
             "Source: our daily Bay East MLS export, Oct. 15, 2025 and Oct. 15, 2026, all property types. "
             "For sale = active, new, coming soon, back on market\nand price change. "
             "Board wide = the 14 cities in both exports (Milpitas joined the export in January 2026 "
             "and is not included).", fontsize=10.2, color=MUTED, ha="left", va="bottom",
             linespacing=1.45)
    return fig, then, now


if __name__ == "__main__":
    fig, then, now = build()
    out = os.path.join(OUTDIR, f"incontract-yoy-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    for key, label in ROWS:
        (a1, a2), (b1, b2) = then[key], now[key]
        print(f"{label:24s} for sale {a1:,} -> {b1:,} ({pct(a1, b1):+d}%)   "
              f"in contract {a2:,} -> {b2:,} ({pct(a2, b2):+d}%)")
    print("wrote", out)
