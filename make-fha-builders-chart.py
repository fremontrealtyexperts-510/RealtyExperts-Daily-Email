#!/usr/bin/env python3
"""
make-fha-builders-chart.py  [outdir]

REALTY EXPERTS recreation of the Market Briefs / ResiClub "Some Builders Run On
FHA Loans" graphic for the 09/23/26 daily email. OUR OWN branded chart, not the
source image.

WHAT CHANGED FROM THE SUPPLIED GRAPHIC, and why (a supplied graphic is a design
brief, never a data source):

  KEPT  LGI Homes 53%      verbatim, "53% at LGI Homes"
  KEPT  Toll Brothers 3%   verbatim, "just 3% of Toll Brothers' homebuyers
                           used FHA financing"
  DROPPED  Ashton Woods 39%  The supplied image is the ONLY place this number
                           appears. It could not be found in the ResiClub write
                           up, the Market Briefs news article, AEI's published
                           indicators, or any secondary coverage. Per the
                           standing rule we drop a bar we cannot source rather
                           than repeat it.

ADDED, and verified at the same source, the average selling price for each
builder. That is the whole explanation of the spread, and it turns a two bar
chart into an argument: FHA reliance tracks price point, not company strategy.

  LGI Homes      ASP \\$367,407
  Toll Brothers  ASP \\$996,400

National context in the footnote, deliberately NOT drawn on the share axis
because it is a different denominator: the New York Fed puts FHA at roughly 12%
of the \\$12.94 trillion U.S. mortgage BALANCE, which is a share of debt
outstanding, not a share of one builder's buyers.

Source: ResiClub analysis of AEI Housing Center data, September 2026.

matplotlib only; build with python3.13 on Mac.
"""
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "092326"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
SLATE = "#8a9aa8"
DEEP = "#b8433a"
MUTED = "#8a8172"

# builder, FHA share of 2025 buyers (%), average selling price (\$), colour
BUILDERS = [
    ("LGI Homes", Decimal("53"), Decimal("367407"), CORAL),
    ("Toll Brothers", Decimal("3"), Decimal("996400"), SLATE),
]


def dollars(x):
    return f"{Decimal(x).quantize(Decimal('1'), rounding=ROUND_HALF_UP):,}"


def build():
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)

    fig.text(0.062, 0.915, "Some Builders Run On FHA Loans",
             fontsize=30, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.062, 0.845,
             "Share of 2025 homebuyers who financed with an FHA loan, and what the "
             "average home cost",
             fontsize=14.5, color=MUTED, ha="left", va="top")

    ys = [1, 0]

    # ---- left panel: FHA share of buyers
    axl = fig.add_axes((0.175, 0.315, 0.315, 0.40))
    axl.set_facecolor(CREAM)
    for y, (name, share, _asp, col) in zip(ys, BUILDERS):
        axl.barh(y, float(share), height=0.52, color=col, zorder=3)
        axl.text(float(share) + 1.6, y, f"{share}%", ha="left", va="center",
                 fontsize=26, fontweight="bold", color=col if col != SLATE else INK,
                 zorder=5)
    axl.set_yticks(ys)
    axl.set_yticklabels([b[0] for b in BUILDERS], fontsize=15, fontweight="bold")
    axl.set_xlim(0, 68)
    axl.set_ylim(-0.55, 1.55)
    axl.set_xticks([])
    axl.tick_params(axis="y", length=0)
    for s in ("top", "right", "bottom", "left"):
        axl.spines[s].set_visible(False)
    axl.set_title("Bought with an FHA loan", fontsize=13.5, fontweight="bold",
                  color=INK, pad=16, loc="left")

    # ---- right panel: average selling price
    axr = fig.add_axes((0.585, 0.315, 0.315, 0.40))
    axr.set_facecolor(CREAM)
    for y, (name, _share, asp, col) in zip(ys, BUILDERS):
        axr.barh(y, float(asp), height=0.52, color=col, alpha=0.42, zorder=3)
        axr.text(float(asp) + 26000, y, f"${dollars(asp)}", ha="left", va="center",
                 fontsize=19, fontweight="bold", color=INK, zorder=5)
    axr.set_yticks(ys)
    axr.set_yticklabels([])
    axr.set_xlim(0, 1420000)
    axr.set_ylim(-0.55, 1.55)
    axr.set_xticks([])
    axr.tick_params(axis="y", length=0)
    for s in ("top", "right", "bottom", "left"):
        axr.spines[s].set_visible(False)
    axr.set_title("Average selling price", fontsize=13.5, fontweight="bold",
                  color=INK, pad=16, loc="left")

    fig.text(0.062, 0.185,
             "The entry level builder leans on FHA. The luxury builder barely "
             "touches it.",
             fontsize=14, fontweight="bold", color=DEEP, ha="left", va="top")
    fig.text(0.062, 0.128,
             "For scale, the New York Fed puts FHA at roughly 12% of the "
             "$12.94 trillion U.S. mortgage balance. That is a share of debt "
             "outstanding, a different\nmeasure from the buyer shares above.",
             fontsize=11.5, color=MUTED, ha="left", va="top", linespacing=1.5)
    fig.text(0.062, 0.043,
             "Source: ResiClub analysis of AEI Housing Center data, September 2026. "
             "FHA counted as a share of all sales, including all cash.",
             fontsize=10.5, color=MUTED, ha="left", va="bottom")

    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"fha-builders-{STAMP}.png")
    plain, branded = save_pair(fig, out, facecolor=CREAM)
    print("wrote", plain)
    print("wrote", branded)
