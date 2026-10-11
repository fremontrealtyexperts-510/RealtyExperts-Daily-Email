#!/usr/bin/env python3
"""
make-mortgage-3pct-local-chart.py  LIVE_INVENTORY_JSON  [outdir]

The 10/11/26 Sunday daily's Real Estate chart. Market Briefs' "Mortgage Math"
said a $400,000 mortgage "now costs about $975 more a month than it did at 3%,
because the average 30-year fixed rate is over 7.50%". Our version runs the
same math on the five city median home. Emits BOTH:

  mortgage-3pct-local-101126.png      plain HB monogram    -> RE email + Agent Hub
  mortgage-3pct-local-101126-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 10/11/26
=============================================================================
Newsletter check, $400,000 loan, 30-year, principal and interest: 3% = $1,686;
7.50% = $2,797 (+$1,111); MND's 7.48% (Oct. 9) = $2,791 (+$1,105). Their $975
is the gap at 7.00% (solved: 7.001%), so the newsletter understated it.
Local: median list price of the 611 homes on the market in Fremont, Hayward,
Milpitas, Newark and Union City, Oct. 11 MLS export (live-inventory.json
all.market.medianPrice) = $1,074,950. 20% down, loan $859,960, under the
$1,249,125 Alameda high balance conforming limit, so MND's 30-year applies.
3% $3,626; 4% $4,106; 5% $4,616; 6% $5,156; 7.48% $6,001. +$2,375 vs 3% (differences of the rounded payments).

matplotlib; build with python3.13 on Mac.
"""
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP, getcontext

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

getcontext().prec = 40

LIVE = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "101126"
TODAY = Decimal("7.48")          # MND 30-year fixed, Oct. 9, 2026 (latest posted)
DOWN = Decimal("0.20")

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e05a47"
DEEP = "#b8432f"
BLUE = "#2b6cb0"
BLUE_D = "#1e4e8c"
GRID = "#d8cdb8"
MUTED = "#8a8172"


def pmt(loan, rate):
    r = rate / Decimal(1200)
    return (loan * r / (1 - (1 + r) ** -360)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def build():
    d = json.load(open(LIVE))
    assert d["date"] == "10/11/26", d["date"]
    med = Decimal(str(d["all"]["market"]["medianPrice"]))
    assert med == Decimal("1074950") and d["all"]["market"]["count"] == 611
    loan = med * (1 - DOWN)
    assert loan < Decimal("1249125")

    # the newsletter's own example
    assert pmt(Decimal(400000), Decimal(3)) == 1686
    assert pmt(Decimal(400000), Decimal("7.50")) - pmt(Decimal(400000), Decimal(3)) == 1111
    assert pmt(Decimal(400000), TODAY) - pmt(Decimal(400000), Decimal(3)) == 1105

    rates = [Decimal(3), Decimal(4), Decimal(5), Decimal(6), TODAY]
    pays = [pmt(loan, r) for r in rates]
    assert [int(p) for p in pays] == [3626, 4106, 4616, 5156, 6001], pays
    gap = pays[-1] - pays[0]
    assert gap == 2375

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.065, 0.17, 0.62, 0.60])
    ax.set_facecolor(CREAM)

    x = list(range(len(rates)))
    cols = ["#9fbfe0", "#86acd6", "#6b98cb", "#4f83bf", CORAL]
    ax.bar(x, [float(p) for p in pays], width=0.62, color=cols, zorder=3)
    for i, p in enumerate(pays):
        last = i == len(pays) - 1
        ax.text(i, float(p) + 110, f"${p:,}", ha="center", va="bottom",
                fontsize=19 if last else 16, fontweight="bold", color=DEEP if last else BLUE_D)
    ax.set_xticks(x)
    ax.set_xticklabels(["3%", "4%", "5%", "6%", f"{TODAY}%\ntoday"], fontsize=15, color=INK)
    for t in ax.get_xticklabels()[-1:]:
        t.set_fontweight("bold")
        t.set_color(DEEP)

    # bracket from the 3% bar to today
    y = float(pays[-1]) + 820
    ax.plot([0, 0, 4, 4], [float(pays[0]) + 600, y, y, float(pays[-1]) + 620],
            color=MUTED, lw=1.2, zorder=2)
    ax.text(2, y + 90, f"+${gap:,} a month", ha="center", va="bottom", fontsize=22,
            fontweight="bold", color=DEEP)

    ax.set_ylim(0, 8200)
    ax.set_yticks([0, 2000, 4000, 6000, 8000])
    ax.set_yticklabels(["$0", "$2,000", "$4,000", "$6,000", "$8,000"], fontsize=11.5, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # side panel: what it means
    yr = gap * 12
    fig.text(0.725, 0.72, "Same home, same\ndown payment", fontsize=19, fontweight="bold",
             color=INK, ha="left", va="top", linespacing=1.2)
    fig.text(0.725, 0.60,
             f"At 3%, the median home\ncost \\${pays[0]:,} a month.\n\n"
             f"At today's {TODAY}%, it is\n\\${pays[-1]:,}: about \\${yr:,}\nmore a year.\n\n"
             f"Even at 6%, the payment\nwould be \\${pays[-1] - pays[3]:,} lower\nthan today.",
             fontsize=14.5, color=INK, ha="left", va="top", linespacing=1.35)

    fig.text(0.035, 0.955, "The 3% Mortgage vs. Today, on a Local Home", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895, f"Monthly principal and interest on ${med:,}, the median list price "
             "in Fremont, Hayward, Milpitas, Newark and Union City, with 20% down",
             fontsize=13.2, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.065, f"30-year fixed, loan ${loan:,.0f}. Median of the {d['all']['market']['count']} "
             "homes on the market in our Oct. 11, 2026 MLS export.\nToday's rate: Mortgage News Daily "
             "30-year fixed index, Oct. 9, 2026. Taxes, insurance and HOA dues not included.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.4)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"mortgage-3pct-local-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
