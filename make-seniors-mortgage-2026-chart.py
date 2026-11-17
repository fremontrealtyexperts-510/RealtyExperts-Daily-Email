"""
make-seniors-mortgage-2026-chart.py  ACS_DIR  [outdir]

The 11/17/26 daily's Real Estate chart. Harv supplied "More Seniors Still Have
a Mortgage" (share of U.S. homeowners 75 and older still paying a mortgage:
20.3%, 1.79M in 2010; 28.7%, 3.93M in 2025; "2.2x as many"; credited to a
Realtor.com analysis of Census ACS data). Rebuilt as OUR chart straight from
the Census table, and KEPT LOCAL with Alameda County from the same table.

Emits BOTH:
  seniors-mortgage-111726.png      plain HB monogram    -> RE email + Agent Hub
  seniors-mortgage-111726-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

ACS_DIR holds b25027-<year>-<geo>.json from the data.census.gov table API
(api.census.gov now 302s to missing_key without a key; this endpoint does not):
  https://data.census.gov/api/access/data/table?id=ACSDT1Y<year>.B25027&g=<geo>
  geo 010XX00US (U.S.), 0400000US06 (California), 0500000US06001 (Alameda County)
B25027 = Mortgage status by age of householder (owner-occupied units).
  _009E with a mortgage, householder 75+; _017E without a mortgage, householder 75+.

=============================================================================
VERIFICATION 11/17/26
=============================================================================
* National, exactly the graphic: 2010 1,794,234 of 8,828,866 = 20.32%;
  2025 3,928,935 of 13,680,563 = 28.72%; 3,928,935 / 1,794,234 = 2.19x.
* Alameda County: 2010 8,194 of 29,989 = 27.32%; 2025 19,562 of 47,160 =
  41.48% (90% margin about 3.5 points); 2.39x. Not a one-year blip: 2019 34.8%,
  2023 39.1%, 2024 37.1%. California 2025: 39.1%.
* The Realtor.com write-up itself was not found; the chart credits the Census
  table it is built from.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import json
import math
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

ACS = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "111726"

CREAM = "#fdf6e8"
INK = "#1f2933"
MUTED = "#8a8172"
RING = "#eadfc9"
OLD = "#7fa7c9"
OLD_TXT = "#3f6f98"
NEW = "#e3a35b"
NEW_TXT = "#bf6f1c"
LOCAL = "#efe3c8"
GOLD = "#a8792a"
TILE = "#f9f1e1"
GREEN = "#2f7d4f"


def read(year, geo):
    d = json.load(open(os.path.join(ACS, f"b25027-{year}-{geo}.json")))["response"]["data"]
    v = dict(zip(d[0], d[1]))
    w, wo = int(v["B25027_009E"]), int(v["B25027_017E"])
    mw, mwo = int(v["B25027_009M"]), int(v["B25027_017M"])
    t = w + wo
    p = w / t
    moe = math.sqrt(max(mw ** 2 - p ** 2 * (mw ** 2 + mwo ** 2), 0)) / t   # ACS proportion formula
    return {"name": v["NAME"], "with": w, "total": t, "pct": Decimal(w * 100) / Decimal(t), "moe": moe * 100}


def r1(x):
    return Decimal(x).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def load():
    us10, us25 = read(2010, "010XX00US"), read(2025, "010XX00US")
    al10, al25 = read(2010, "0500000US06001"), read(2025, "0500000US06001")
    ca25 = read(2025, "0400000US06")
    assert (us10["with"], us10["total"], us25["with"], us25["total"]) == (1794234, 8828866, 3928935, 13680563)
    assert (str(r1(us10["pct"])), str(r1(us25["pct"]))) == ("20.3", "28.7")
    assert str(r1(Decimal(us25["with"]) / us10["with"])) == "2.2"
    assert str(r1(Decimal(us25["total"]) / us10["total"])) == "1.5"   # "all homeowners 75+ rose 1.5x"
    assert (al10["with"], al10["total"], al25["with"], al25["total"]) == (8194, 29989, 19562, 47160)
    assert (str(r1(al10["pct"])), str(r1(al25["pct"]))) == ("27.3", "41.5")
    assert str(r1(Decimal(al25["with"]) / al10["with"])) == "2.4"
    assert 3.3 < al25["moe"] < 3.6, al25["moe"]
    assert str(r1(ca25["pct"])) == "39.1"
    assert al10["name"].startswith("Alameda County")
    return us10, us25, al10, al25, ca25


def donut(fig, rect, pct, color, txt_color):
    ax = fig.add_axes(rect)
    ax.set_facecolor(CREAM)
    p = float(pct)
    ax.pie([p, 100 - p], colors=[color, RING], startangle=90, counterclock=False,
           wedgeprops=dict(width=0.30, edgecolor=CREAM, linewidth=2))
    ax.set_aspect("equal")
    ax.text(0, 0, f"{r1(pct)}%", fontsize=34, fontweight="bold", color=txt_color, ha="center", va="center")


def build():
    us10, us25, al10, al25, ca25 = load()
    fig = plt.figure(figsize=(14.0, 8.8), dpi=100)
    fig.patch.set_facecolor(CREAM)
    fig.text(0.035, 0.955, "More Seniors Still Have a Mortgage", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.900, "Share of homeowners age 75 and older still paying off a mortgage", fontsize=13.5,
             color=MUTED, ha="left", va="top")

    # national: 2010 and 2025 donuts, an arrow and the multiple between them
    fig.text(0.205, 0.835, "U.S. 2010", fontsize=20, fontweight="bold", color=INK, ha="center", va="center")
    fig.text(0.795, 0.835, "U.S. 2025", fontsize=20, fontweight="bold", color=INK, ha="center", va="center")
    donut(fig, [0.085, 0.43, 0.24, 0.37], us10["pct"], OLD, OLD_TXT)
    donut(fig, [0.675, 0.43, 0.24, 0.37], us25["pct"], NEW, NEW_TXT)
    fig.text(0.205, 0.395, "1.79 million homeowners", fontsize=16, color=INK, ha="center", va="center")
    fig.text(0.795, 0.395, "3.93 million homeowners", fontsize=16, color=INK, ha="center", va="center")
    fig.patches.append(FancyArrowPatch((0.37, 0.62), (0.63, 0.62), transform=fig.transFigure,
                                       arrowstyle="-|>,head_length=12,head_width=8", lw=3, color=OLD,
                                       mutation_scale=1))
    fig.text(0.5, 0.68, "2.2x as many", fontsize=24, fontweight="bold", color=NEW_TXT, ha="center",
             va="center")
    fig.text(0.5, 0.56, "while all homeowners 75+\nrose 1.5x", fontsize=13, color=MUTED, ha="center",
             va="center", linespacing=1.2)

    # local band
    fig.patches.append(Rectangle((0.035, 0.105), 0.93, 0.24, transform=fig.transFigure, facecolor=LOCAL,
                                 edgecolor="none"))
    fig.text(0.055, 0.317, "HERE: ALAMEDA COUNTY HOMEOWNERS 75 AND OLDER", fontsize=13.5, fontweight="bold",
             color=GOLD, ha="left", va="center")
    tiles = (
        ("2010", al10, OLD, OLD_TXT, "about %s homeowners" % format(round(al10["with"], -2), ",")),
        ("2025", al25, NEW, NEW_TXT, "about %s homeowners" % format(round(al25["with"], -2), ",")),
    )
    x0, w, gap = 0.055, 0.285, 0.02
    for i, (yr, d, color, tcolor, line2) in enumerate(tiles):
        x = x0 + i * (w + gap)
        fig.patches.append(Rectangle((x, 0.13), w, 0.155, transform=fig.transFigure, facecolor=TILE,
                                     edgecolor="none"))
        fig.patches.append(Rectangle((x, 0.13), 0.006, 0.155, transform=fig.transFigure, facecolor=color,
                                     edgecolor="none"))
        fig.text(x + 0.022, 0.255, yr, fontsize=14, fontweight="bold", color=INK, ha="left", va="center")
        fig.text(x + 0.022, 0.196, f"{r1(d['pct'])}%", fontsize=30, fontweight="bold", color=tcolor,
                 ha="left", va="center")
        fig.text(x + 0.022, 0.148, line2, fontsize=12.5, color=INK, ha="left", va="center")
    x = x0 + 2 * (w + gap)
    fig.patches.append(Rectangle((x, 0.13), 0.93 - (x - 0.035) - 0.02, 0.155, transform=fig.transFigure,
                                 facecolor=TILE, edgecolor="none"))
    fig.text(x + 0.022, 0.255, "2.4x as many here", fontsize=14, fontweight="bold", color=INK, ha="left",
             va="center")
    fig.text(x + 0.022, 0.196, "About 4 in 10", fontsize=24, fontweight="bold", color=NEW_TXT, ha="left",
             va="center")
    fig.text(x + 0.022, 0.148, f"California {r1(ca25['pct'])}%, U.S. {r1(us25['pct'])}%", fontsize=12.5,
             color=INK, ha="left", va="center")

    fig.text(0.035, 0.062, "Owner-occupied homes. Alameda County figures carry a margin of error of about "
             "3.5 points (90% confidence).", fontsize=10.2, color=MUTED, ha="left", va="bottom")
    fig.text(0.035, 0.026, "Source: U.S. Census Bureau, American Community Survey 1-year estimates, table "
             "B25027 (mortgage status by age of householder), 2010 and 2025.", fontsize=10.2, color=MUTED,
             ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"seniors-mortgage-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
