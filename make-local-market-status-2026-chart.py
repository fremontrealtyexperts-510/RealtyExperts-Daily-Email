#!/usr/bin/env python3
"""
make-local-market-status-2026-chart.py  HIST_DIR  [outdir]

The 11/19/26 daily's Real Estate chart. Harv asked for "a status of the market
for the local market" on the day NAR reported October pending home sales down
4.7% on the month and 16.7% on the year (West down 20.3%), a second straight
record low. This asks the local question with OUR OWN data: how many homes are
for sale, how many are in contract, and how does that compare with the same day
a year ago? Same method as make-incontract-yoy-chart.py (10/15/26), plus a
"homes for sale per home in contract" column as the one number status read.

Emits BOTH:
  local-market-status-111926.png      plain HB monogram    -> RE email + Agent Hub
  local-market-status-111926-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

=============================================================================
SOURCE AND BASIS
=============================================================================
HIST_DIR holds 111925.csv and 111926.csv, verbatim dumps of the dated
MLS_Defined_Spread_Sheet_4 exports for Nov. 19, 2025 ("111925 - 950am.xlsx", a
real .xlsx on Drive, converted cell for cell with openpyxl) and Nov. 19, 2026
(today's sheet via dump-mls-csv.js). Same calendar day, so no seasonal skew.
The listing level CSVs are never committed; only the counts below.

  For sale     = ACTV, NEW, CS, BOMK, PCH (the five city ledger's live basis),
                 all property types.
  In contract  = PEND.
  Board        = the 14 cities present in BOTH exports. Milpitas joined the
                 export in January 2026, so it is left out of every bar.

Counts generated from the files on 11/19/26 (asserted below):
                 for sale         in contract     for sale per contract
  14 cities     1,696 -> 1,755    803 -> 570      2.1 -> 3.1
  Fremont         173 ->   197     89 ->  56      1.9 -> 3.5
  Hayward         194 ->   170     97 ->  59      2.0 -> 2.9
  Newark           45 ->    72     35 ->  24      1.3 -> 3.0
  Union City       44 ->    56     18 ->  16      2.4 -> 3.5

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
STAMP = "111926"

CREAM = "#fdf6e8"
INK = "#1f2933"
GRID = "#d8cdb8"
MUTED = "#8a8172"
BLUE = "#2f6f9f"     # for sale
CORAL = "#e2574c"    # in contract
LIVE = {"ACTV", "NEW", "CS", "BOMK", "PCH"}
HEADER = ("MLS No,Status,DOM,Address,Unit,City,Area,LP,SP,BT,SqFt,BR,Bth,PB,"
          "Gar,GarSp,YrBlt,Acres,Lot SqFt,HOA Fee,Freq").split(",")
ROWS = [("BOARD", "Board wide"), ("FREMONT", "Fremont"),
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


def ratio(fs, pc):
    return (Decimal(fs) / Decimal(pc)).quantize(Decimal("0.1"), ROUND_HALF_UP)


def build():
    then = counts(os.path.join(HIST, "111925.csv"))
    now = counts(os.path.join(HIST, "111926.csv"))
    assert then == {"BOARD": (1696, 803), "FREMONT": (173, 89), "HAYWARD": (194, 97),
                    "NEWARK": (45, 35), "UNION CITY": (44, 18)}, then
    assert now == {"BOARD": (1755, 570), "FREMONT": (197, 56), "HAYWARD": (170, 59),
                   "NEWARK": (72, 24), "UNION CITY": (56, 16)}, now

    fig = plt.figure(figsize=(14.0, 8.4), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.20, 0.14, 0.555, 0.64])
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
            off = 1.6
            ax.text(p + off if p >= 0 else p - off, y + dy, txt, va="center",
                    ha="left" if p >= 0 else "right", fontsize=13,
                    fontweight="bold", color=color, zorder=5,
                    bbox=dict(boxstyle="square,pad=0.12", facecolor=CREAM, edgecolor="none"))
        ax.text(-0.035, y, label, transform=ax.get_yaxis_transform(), ha="right",
                va="center", fontsize=15, fontweight="bold", color=INK)
        # status column: homes for sale per home in contract
        r0, r1 = ratio(*then[key]), ratio(*now[key])
        ax.text(1.06, y, f"{r0}", transform=ax.get_yaxis_transform(), ha="center", va="center",
                fontsize=15, color=MUTED)
        ax.text(1.14, y, "→", transform=ax.get_yaxis_transform(), ha="center", va="center",
                fontsize=15, color=MUTED)
        ax.text(1.22, y, f"{r1}", transform=ax.get_yaxis_transform(), ha="center", va="center",
                fontsize=17, fontweight="bold", color=INK)
        if i == 0:
            ax.axhline(y - 0.62, color=GRID, lw=1.2, zorder=1)

    ax.text(1.14, n - 0.25, "For sale per\nhome in contract", transform=ax.get_yaxis_transform(),
            ha="center", va="bottom", fontsize=12.5, color=INK, fontweight="bold", linespacing=1.25)
    ax.text(1.06, n - 0.42, "2025", transform=ax.get_yaxis_transform(), ha="center", va="bottom",
            fontsize=10.5, color=MUTED)
    ax.text(1.22, n - 0.42, "2026", transform=ax.get_yaxis_transform(), ha="center", va="bottom",
            fontsize=10.5, color=MUTED)

    ax.set_xlim(-80, 108)
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

    fig.text(0.20, 0.835, "■", color=BLUE, fontsize=18, ha="left", va="center")
    fig.text(0.22, 0.835, "Homes for sale", color=INK, fontsize=14, ha="left", va="center")
    fig.text(0.38, 0.835, "■", color=CORAL, fontsize=18, ha="left", va="center")
    fig.text(0.40, 0.835, "Homes in contract (pending)", color=INK, fontsize=14,
             ha="left", va="center")

    fig.text(0.035, 0.955, "Local Contracts Are Down 29% From a Year Ago", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.897, "Nov. 19, 2025 to Nov. 19, 2026, the same day a year apart. Board wide, "
             "supply is up 3%; signed contracts are down 29%.", fontsize=13.2,
             color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035,
             "Source: our daily Bay East MLS export, Nov. 19, 2025 and Nov. 19, 2026, all property types. "
             "For sale = active, new, coming soon, back on market\nand price change. "
             "Board wide = the 14 cities in both exports (Milpitas joined the export in January 2026 "
             "and is not included).", fontsize=10.2, color=MUTED, ha="left", va="bottom",
             linespacing=1.45)
    return fig, then, now


if __name__ == "__main__":
    fig, then, now = build()
    out = os.path.join(OUTDIR, f"local-market-status-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    for key, label in ROWS:
        (a1, a2), (b1, b2) = then[key], now[key]
        print(f"{label:24s} for sale {a1:,} -> {b1:,} ({pct(a1, b1):+d}%)   "
              f"in contract {a2:,} -> {b2:,} ({pct(a2, b2):+d}%)   "
              f"per contract {ratio(a1, a2)} -> {ratio(b1, b2)}")
    print("wrote", out)
