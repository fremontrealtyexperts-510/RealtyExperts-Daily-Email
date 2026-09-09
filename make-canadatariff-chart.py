#!/usr/bin/env python3
"""
make-canadatariff-chart.py  [outdir]

Recreates the Market Briefs graphic "Canada Taxes U.S. Goods" for the 09/09/26
edition. Emits BOTH brand variants:

  canadatariff-090926.png      plain monogram    -> RE email + Agent Hub
  canadatariff-090926-hb.png   + wordmark        -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/09/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

All THREE rates verified against the Department of Finance Canada schedule
effective September 8, 2026 at 12:01 a.m., cross checked against Blakes'
summary of the same order in council:

  15%  "Fork-lift trucks and industrial handling equipment", "Parts for
       harvesting and agricultural machinery", "Air conditioners"
  25%  "Household articles of steel and aluminum (cookware, sanitary ware,
       kitchenware)", "Washing machines, dryers and dishwasher parts"
  50%  "Steel and aluminum products (ingots, bars, rods, wire, tubes, pipes)"

So the graphic's three category-to-rate pairs are RIGHT.

WHAT THE SUPPLIED GRAPHIC OVERSIMPLIFIES, and how this version fixes it
------------------------------------------------------------------
These are not three tidy categories each carrying one rate. Canada assigned
rates **product by product, to mirror the matching U.S. rate on the same good**,
so a single everyday category straddles tiers. The cleanest proof is inside
"appliances" itself: **air conditioners are taxed at 15% while washing machines,
dryers and dishwasher parts are taxed at 25%.** Steel is mostly 50% but some
steel derivative lines land at 25%.

Reading the original as "appliances = 25%" will mislead anyone pricing a real
purchase. The bars are kept (they are the correct headline tiers) and a footnote
carries the product-by-product rule plus the air-conditioner counterexample.

⚠️ CURRENCY. The order covers **C$27.6 billion**, Canadian dollars. Market
Briefs wrote "$27.6B of U.S. products" with no currency marker, which a U.S.
reader takes as USD. At CAD/USD 0.7242 that is **US$20.0 billion**, so the
unmarked figure overstates the scope by about 38%. The subtitle states the
currency explicitly. Same discipline as the Brent futures-versus-spot lock:
never let two units share a label.

Not charted, kept in the report copy: the local angle. Steel, aluminum and
appliances are remodel and new-construction inputs, which is where a Bay Area
reader actually meets this policy.

matplotlib only; build with python3.13 on Mac.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "090926"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
SLATE = "#8a9aa8"
MID = "#6b8299"
GRID = "#d8cdb8"
MUTED = "#8a8172"

CATS = ["Machinery parts,\nfork-lifts, A/C", "Appliances\n(washers, dryers)", "Steel & aluminum\n(bars, tubes, pipe)"]
RATES = [15, 25, 50]


def build():
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    colors = [SLATE, MID, CORAL]
    for i, (v, col) in enumerate(zip(RATES, colors)):
        top = i == len(RATES) - 1
        ax.bar(i, v, width=0.58, color=col,
               edgecolor=DEEP if top else "none", linewidth=1.5 if top else 0, zorder=3)
        ax.text(i, v + 1.0, f"{v}%", ha="center", va="bottom",
                fontsize=22 if top else 19, fontweight="bold",
                color=DEEP if top else INK, zorder=5)

    ax.set_xticks(range(len(CATS)))
    ax.set_xticklabels(CATS, fontsize=13.5, fontweight="bold")
    ax.set_xlim(-0.62, len(CATS) - 0.38)
    ax.set_ylim(0, 60)
    ax.set_yticks([0, 10, 20, 30, 40, 50])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.grid(axis="y", color=GRID, linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="both", length=0, labelsize=13, colors=SLATE)
    for lbl in ax.get_xticklabels():   # after tick_params, which resets colours
        lbl.set_color(INK)

    fig.text(0.045, 0.945, "Canada's Counter Tariffs on U.S. Goods",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888,
             "Rates effective September 8, 2026, covering C\\$27.6 billion of U.S. imports (about US\\$20 billion)",
             fontsize=14, color=MUTED, ha="left", va="top")

    fig.text(
        0.045, 0.126,
        "These are rate TIERS, not category rates. Canada set each product's rate to mirror the matching U.S. tariff on the same good, so one\n"
        "everyday category can straddle tiers: air conditioners are taxed at 15% while washing machines and dryers are taxed at 25%.",
        fontsize=11.5, color=DEEP, ha="left", va="bottom", linespacing=1.55,
    )
    fig.text(
        0.045, 0.045,
        "Source: Department of Finance Canada, list of U.S. products subject to counter-tariffs effective September 8, 2026, in force 12:01 a.m.\n"
        "Currency is Canadian dollars; the U.S. dollar figure uses CAD/USD 0.7242 on September 9, 2026.",
        fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5,
    )

    fig.subplots_adjust(left=0.075, right=0.965, top=0.815, bottom=0.265)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"canadatariff-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
