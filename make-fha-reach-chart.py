#!/usr/bin/env python3
"""
make-fha-reach-chart.py  [outdir]

THE LOCAL ANSWER to the 09/23/26 national FHA story. A ranking of LGI Homes
against Toll Brothers is trivia to a Fremont agent; "how far does an FHA loan
actually reach on our street" is a conversation they can have with a buyer this
afternoon. So we compute it ourselves.

QUESTION: of the homes on the market right now in the five cities we track,
how many are even within an FHA loan's reach?

METHOD, one geography, one vintage, stated on the chart:
  * Universe  every live listing in today's MLS export, 09/23/26. Live means
              Active, New, Coming Soon and Back on Market, the same definition
              generate-live-inventory.js uses for the daily ledger, so this
              chart and the ledger cannot disagree.
  * Ceiling   \\$1,249,125, the 2026 FHA limit for a one unit home in Alameda
              County. Milpitas sits in Santa Clara County, which carries the
              same high cost ceiling, so one line covers all five cities.
  * Counted   list price at or below that ceiling. This is the CONSERVATIVE
              read: it uses the loan limit as if it were a price cap and
              ignores the buyer's down payment. Allowing the FHA minimum of
              3.5% down lifts the reachable price to about \\$1,294,000 and
              nudges every city up a point or two. The footnote says so.

Numbers are generated from the CSV at run time, never hand typed.

matplotlib only; build with python3.13 on Mac.
"""
import csv
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
CSV_PATH = sys.argv[2] if len(sys.argv) > 2 else "/tmp/mls-today.csv"
STAMP = "092326"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
RUST = "#c8692f"
SLATE = "#8a9aa8"
MUTED = "#8a8172"

LIVE = {"ACTV", "NEW", "CS", "BOMK"}
CITIES = ["HAYWARD", "NEWARK", "MILPITAS", "FREMONT", "UNION CITY"]
PRETTY = {"UNION CITY": "Union City"}
FHA_LIMIT = Decimal("1249125")


def pct(n, d):
    return (Decimal(n) * 100 / Decimal(d)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def load():
    rows = list(csv.DictReader(open(CSV_PATH)))
    out = {}
    for c in CITIES:
        prices = []
        for r in rows:
            if r["Status"].strip().upper() not in LIVE:
                continue
            if r["City"].strip().upper() != c:
                continue
            try:
                prices.append(Decimal(str(r["LP"]).replace(",", "").replace("$", "")))
            except Exception:
                pass
        within = sum(1 for p in prices if p <= FHA_LIMIT)
        out[c] = (len(prices), within, pct(within, len(prices)))
    return out


def build(data):
    order = sorted(CITIES, key=lambda c: data[c][2], reverse=True)

    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)

    fig.text(0.062, 0.925, "How Far An FHA Loan Reaches Here",
             fontsize=30, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.062, 0.858,
             "Share of homes on the market today priced within the "
             "$1,249,125 FHA limit",
             fontsize=14.5, color=MUTED, ha="left", va="top")

    ax = fig.add_axes((0.185, 0.245, 0.60, 0.545))
    ax.set_facecolor(CREAM)

    ys = list(range(len(order)))[::-1]
    for y, city in zip(ys, order):
        total, within, share = data[city]
        col = CORAL if city == "FREMONT" else (RUST if share >= 60 else SLATE)
        ax.barh(y, float(share), height=0.58, color=col, zorder=3)
        ax.text(float(share) + 1.4, y, f"{share}%", ha="left", va="center",
                fontsize=20, fontweight="bold",
                color=col if col != SLATE else INK, zorder=5)
        ax.text(float(share) - 1.6, y, f"{within} of {total}", ha="right",
                va="center", fontsize=12, fontweight="bold", color="white",
                zorder=5)

    ax.set_yticks(ys)
    ax.set_yticklabels([PRETTY.get(c, c.title()) for c in order],
                       fontsize=15, fontweight="bold")
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.6, len(order) - 0.4)
    ax.set_xticks([])
    ax.tick_params(axis="y", length=0)
    for s in ("top", "right", "bottom", "left"):
        ax.spines[s].set_visible(False)

    tot = sum(data[c][0] for c in CITIES)
    win = sum(data[c][1] for c in CITIES)
    fig.text(0.062, 0.185,
             f"Across the five cities, {win} of {tot} live listings "
             f"({pct(win, tot)}%) sit within FHA's reach.",
             fontsize=14, fontweight="bold", color=DEEP, ha="left", va="top")
    fig.text(0.062, 0.118,
             "Conservative count: the loan limit is used as a price cap. At "
             "FHA's 3.5% minimum down, about $1,294,000 is reachable.",
             fontsize=11.5, color=MUTED, ha="left", va="top")
    fig.text(0.062, 0.045,
             "Source: Bay East MLS live listings, September 23, 2026, and the "
             "2026 FHA one unit limit for Alameda and Santa Clara counties.",
             fontsize=10.5, color=MUTED, ha="left", va="bottom")

    return fig


if __name__ == "__main__":
    data = load()
    for c in CITIES:
        t, w, s = data[c]
        print(f"  {c:11} live={t:4d} withinFHA={w:4d} {s}%")
    fig = build(data)
    out = os.path.join(OUTDIR, f"fha-reach-tricity-{STAMP}.png")
    plain, branded = save_pair(fig, out, facecolor=CREAM)
    print("wrote", plain)
    print("wrote", branded)
