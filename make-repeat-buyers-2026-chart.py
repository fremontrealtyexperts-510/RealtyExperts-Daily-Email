"""
make-repeat-buyers-2026-chart.py  NAR_RELEASE_HTML  LIVE_INVENTORY_JSON  [outdir]

The 11/16/26 daily's Real Estate chart. Harv supplied "Repeat Buyers Dominate
Housing" (NAR 2026 Profile: 78% repeat buyers, median age 62; 22% first-time,
median age 40). Rebuilt as OUR chart and KEPT LOCAL: NAR's median down payments
for each group (9% first-time, 19% repeat) applied to the five city median list
price on our board, with the monthly principal and interest at MND's 30-year.

Emits BOTH:
  repeat-buyers-111626.png      plain HB monogram    -> RE email + Agent Hub
  repeat-buyers-111626-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

NAR_RELEASE_HTML    = nar.realtor/newsroom/first-time-home-buyer-share-inches-up-to-22-median-age-remains-at-record-high-of-40
LIVE_INVENTORY_JSON = live-inventory.json from generate-live-inventory.js (11/16/26 MLS export)

=============================================================================
VERIFICATION 11/16/26
=============================================================================
* Every NAR figure is asserted against the release's own sentences (Nov. 5,
  2026; survey covers July 2025 to June 2026): first-time share 22% (record
  low 21% a year earlier), median age 40 (ties the all-time high), 9% median
  down payment; repeat buyers 78% of purchases, median age 62 (ties the
  all-time high), 19% median down payment. The supplied graphic's four numbers
  all match. All buyers' median age 58 (from 59) is in the copy, not the chart.
* Five city median list price of homes on the market (ACTV + NEW, PCH as
  ACTV) = $999,988, read from live-inventory.json dated 11/16/26.
* Rate 7.50% = MND 30-year fixed, last updated Friday 11/13/26 (no Monday
  row by 8:10 AM PT). Loans of $909,989 and $809,990 are under Alameda's
  $1,249,125 high-balance conforming limit, so MND's conforming 30-year applies.
* Payments computed in Decimal and cross-checked in float; dollars and
  down payments rounded half up.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import html
import json
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

NAR, LIVE = sys.argv[1], sys.argv[2]
OUTDIR = sys.argv[3] if len(sys.argv) > 3 else "."
STAMP = "111626"
RATE = Decimal("7.50")

CREAM = "#fdf6e8"
INK = "#1f2933"
MUTED = "#8a8172"
REPEAT = "#e3a35b"
REPEAT_TXT = "#bf6f1c"
FIRST = "#2f7d4f"
LOCAL = "#efe3c8"
GOLD = "#a8792a"
TILE = "#f9f1e1"

PHRASES = [
    "rose slightly to 22% from last year’s record low of 21%",
    "typical age of first-time buyers remained at an all-time high of 40",
    "covers transactions between July 2025 and June 2026",
    "Median age: 40 years old—matching the all-time high",
    "9% median down payment",
    "Repeat buyers accounted for 78% of all home purchases",
    "Median age: 62 years old—matching the all-time high",
    "19% median down payment",
    "Median age: 58 years old Down from 59 last year",
]


def dollars(x):
    return x.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def payment(loan):
    r = RATE / Decimal(1200)
    f = (1 + r) ** 360
    p = dollars(loan * r * f / (f - 1))
    rf = float(RATE) / 1200
    pf = float(loan) * rf / (1 - (1 + rf) ** -360)
    assert abs(float(p) - pf) < 0.51, (p, pf)
    return p


def load():
    t = open(NAR, encoding="utf-8", errors="ignore").read()
    t = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style).*?</\1>", " ", t)))
    t = re.sub(r"\s+", " ", t)
    for p in PHRASES:
        assert p in t, p
    live = json.load(open(LIVE))
    assert live["date"] == "11/16/26", live["date"]
    med = Decimal(live["all"]["market"]["medianPrice"])
    assert med == Decimal("999988"), med
    rows = []
    for name, pct in (("First-time buyers", 9), ("Repeat buyers", 19)):
        down = med * pct / 100
        loan = med - down
        assert loan < Decimal("1249125")
        rows.append((name, pct, (down / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * 100, payment(loan)))
    assert [(r[2], r[3]) for r in rows] == [(Decimal("90000"), Decimal("6363")), (Decimal("190000"), Decimal("5664"))], rows
    return med, rows


def build():
    med, rows = load()
    fig = plt.figure(figsize=(14.0, 8.6), dpi=100)
    fig.patch.set_facecolor(CREAM)
    fig.text(0.035, 0.955, "Repeat Buyers Dominate Housing", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.900, "Share of U.S. home purchases, July 2025 to June 2026", fontsize=13.5, color=MUTED,
             ha="left", va="top")

    ax = fig.add_axes([0.06, 0.37, 0.30, 0.48])
    ax.set_facecolor(CREAM)
    ax.pie([22, 78], colors=[FIRST, REPEAT], startangle=90, counterclock=False,
           wedgeprops=dict(width=0.36, edgecolor=CREAM, linewidth=3))
    ax.set_aspect("equal")
    ax.text(0, 0.06, "78%", fontsize=30, fontweight="bold", color=INK, ha="center", va="center")
    ax.text(0, -0.2, "are repeat buyers", fontsize=12.5, color=MUTED, ha="center", va="center")

    def block(y, color, pct, label, line2):
        fig.patches.append(FancyBboxPatch((0.43, y - 0.012), 0.022, 0.03, boxstyle="round,pad=0.003",
                                          transform=fig.transFigure, facecolor=color, edgecolor="none"))
        fig.text(0.47, y + 0.004, pct, fontsize=34, fontweight="bold", color=color, ha="left", va="center")
        fig.text(0.575, y + 0.002, label, fontsize=22, fontweight="bold", color=INK, ha="left", va="center")
        fig.text(0.47, y - 0.058, line2, fontsize=15, color=INK, ha="left", va="center")

    block(0.735, REPEAT_TXT, "78%", "Repeat buyers", "Median age 62, and a 19% median down payment")
    block(0.555, FIRST, "22%", "First-time buyers", "Median age 40 (ties the record), 9% median down payment")

    fig.patches.append(Rectangle((0.035, 0.095), 0.93, 0.235, transform=fig.transFigure, facecolor=LOCAL,
                                 edgecolor="none"))
    fig.text(0.055, 0.302, "HERE: THOSE DOWN PAYMENTS ON OUR FIVE CITY MEDIAN LIST PRICE OF \\$%s"
             % format(int(med), ","), fontsize=13.5, fontweight="bold", color=GOLD, ha="left", va="center")
    x0, w, gap = 0.055, 0.435, 0.02
    for i, (name, pct, down, pay) in enumerate(rows):
        x = x0 + i * (w + gap)
        color = FIRST if i == 0 else REPEAT
        tcolor = FIRST if i == 0 else REPEAT_TXT
        fig.patches.append(Rectangle((x, 0.125), w, 0.15, transform=fig.transFigure, facecolor=TILE,
                                     edgecolor="none"))
        fig.patches.append(Rectangle((x, 0.125), 0.006, 0.15, transform=fig.transFigure, facecolor=color,
                                     edgecolor="none"))
        fig.text(x + 0.02, 0.252, "%s, %d%% down" % (name, pct), fontsize=13.5, fontweight="bold", color=INK,
                 ha="left", va="center")
        fig.text(x + 0.02, 0.185, "\\$%s down" % format(int(down), ","), fontsize=23, fontweight="bold",
                 color=tcolor, ha="left", va="center")
        fig.text(x + 0.255, 0.185, "\\$%s" % format(int(pay), ","), fontsize=24, fontweight="bold", color=INK,
                 ha="left", va="center")
        fig.text(x + 0.255, 0.145, "a month, principal and interest", fontsize=11, color=MUTED, ha="left",
                 va="center")
    fig.text(0.035, 0.062, "Payments at 7.50%, 30-year fixed (Mortgage News Daily, Nov. 13), before taxes and insurance. "
             "Five cities: Fremont, Hayward, Milpitas, Newark, Union City.", fontsize=10.2, color=MUTED, ha="left", va="bottom")
    fig.text(0.035, 0.026, "Source: National Association of REALTORS®, 2026 Profile of Home Buyers and Sellers; "
             "MLS listing export, Nov. 16, 2026.", fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"repeat-buyers-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
