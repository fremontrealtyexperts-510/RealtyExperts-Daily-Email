#!/usr/bin/env python3
"""
make-nvidia-ramp-2026-chart.py  [outdir]

Recreation of the "Nvidia's Revenue Ramp" graphic Harv supplied for the 09/18/26
edition. Emits BOTH variants:

  nvidia-ramp-091826.png      plain monogram   -> RE email + Agent Hub
  nvidia-ramp-091826-hb.png   + wordmark       -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/18/26
=============================================================================

REPORTED BARS: all three match the supplied graphic exactly. Pulled from SEC
EDGAR companyconcept us-gaap:Revenues for CIK 0001045810 (NVIDIA), 10-K values:

  fiscal year (ends)          graphic      SEC filing        verdict
  FY2024  (2024-01-28)        $60.9B       $60,922M          match
  FY2025  (2025-01-26)        $130.5B      $130,497M         match
  FY2026  (2026-01-25)        $215.9B      $215,900M         match

FY2026 growth works out to 65%, which agrees with the Motley Fool's "Nvidia's
revenue increased by 65% in its fiscal 2026" (09/04/26).

★ THE TWO FORECAST BARS ARE NOT THE SAME KIND OF NUMBER, and the supplied
graphic's legend ("Forecast") flattened that difference:

  FY2027 $396B is an ANALYST CONSENSUS, not company guidance. Fortune
  (08/26/26) reported the Visible Alpha consensus at "roughly $570 billion, or
  44% growth from fiscal 2027" for FY2028, which puts the FY2027 base at
  570 / 1.44 = $395.8B, i.e. about $396B. Drawn dashed and labelled consensus.

  FY2028 $673B is DERIVED, not issued. What Nvidia gave on 08/26/26 with its
  Q2 FY2027 results was a GROWTH RATE: about 70% revenue growth in fiscal 2028
  (Fortune: "a projection that its revenue would skyrocket by 70% next fiscal
  year"). $673B is that 70% applied to the $396B consensus. Fortune applied it
  to a higher base and reported "fiscal 2028 revenue in the range of $690
  billion to $700 billion". Both are published; neither is a company dollar
  figure. So this bar is drawn as a RANGE, $673B to $700B, with the hatched
  segment carrying the spread, and the footnote says the guidance is a rate.

  The supplied graphic's own footnote, "FY28 company guidance (+70%)", is the
  half that is right; the $673B printed above the bar as if Nvidia had said it
  is the half that is not.

Market context checked but NOT plotted: NVDA closed $219.34 on 09/17/26 (+2.54%,
Yahoo), and 24.1B shares outstanding (10-Q filed 2026-08-21) puts the market cap
near $5.3T, so Market Briefs' "$5.2T" is close but stale on price.

matplotlib only; build with python3.13 on Mac.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "091826"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
GREEN = "#4f8a5b"
GRID = "#d8cdb8"
MUTED = "#8a8172"

# (label, value $B, kind)
REPORTED = [("FY2024", 60.9), ("FY2025", 130.5), ("FY2026", 215.9)]
CONSENSUS = ("FY2027", 396.0)
GUIDED_LOW, GUIDED_HIGH = 673.0, 700.0

fig, ax = plt.subplots(figsize=(11.2, 6.3), dpi=115)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

xs = list(range(5))
labels = [r[0] for r in REPORTED] + [CONSENSUS[0], "FY2028"]

for x, (_, v) in zip(xs[:3], REPORTED):
    ax.bar(x, v, width=0.58, color=CORAL, zorder=3)
    ax.text(x, v + 14, f"\\${v:,.1f}B", ha="center", va="bottom",
            fontsize=15, fontweight="bold", color=INK)

# FY2027: analyst consensus
ax.bar(xs[3], CONSENSUS[1], width=0.58, facecolor="#f6d9cf", edgecolor=DEEP,
       linewidth=1.8, linestyle=(0, (5, 3)), zorder=3)
ax.text(xs[3], CONSENSUS[1] + 14, f"\\${CONSENSUS[1]:,.0f}B", ha="center",
        va="bottom", fontsize=15, fontweight="bold", color=INK)
ax.text(xs[3], CONSENSUS[1] / 2, "analyst\nconsensus", ha="center", va="center",
        fontsize=11, color=DEEP, fontweight="bold")

# FY2028: 70% guidance applied to the consensus, drawn as a range
ax.bar(xs[4], GUIDED_LOW, width=0.58, facecolor="#dceadf", edgecolor=GREEN,
       linewidth=1.8, linestyle=(0, (5, 3)), zorder=3)
ax.bar(xs[4], GUIDED_HIGH - GUIDED_LOW, width=0.58, bottom=GUIDED_LOW,
       facecolor="none", edgecolor=GREEN, hatch="///", linewidth=1.4,
       linestyle=(0, (2, 2)), zorder=3, alpha=0.75)
ax.text(xs[4], GUIDED_HIGH + 14, f"\\${GUIDED_LOW:,.0f}B to \\${GUIDED_HIGH:,.0f}B",
        ha="center", va="bottom", fontsize=15, fontweight="bold", color=INK)
ax.text(xs[4], GUIDED_LOW / 2, "about 70%\ngrowth, as\nguided", ha="center",
        va="center", fontsize=11, color="#2f5c3a", fontweight="bold")

ax.set_xticks(xs)
ax.set_xticklabels(labels, fontsize=13.5, fontweight="bold", color=INK)
ax.tick_params(axis="x", length=0, pad=8)
ax.tick_params(axis="y", colors=MUTED, labelsize=11)
ax.set_yticks([0, 200, 400, 600, 800])
ax.set_yticklabels(["0", "\\$200B", "\\$400B", "\\$600B", "\\$800B"],
                   fontsize=11, color=MUTED)
ax.set_ylim(0, 830)
ax.set_xlim(-0.62, 4.62)
ax.grid(axis="y", color=GRID, linewidth=0.9, alpha=0.7, zorder=0)
ax.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(GRID)

ax.set_title("Nvidia's Revenue Ramp", fontsize=25, fontweight="bold",
             color=INK, pad=32, loc="left", x=0)
ax.text(0, 1.045, "Total annual revenue, fiscal years ending late January",
        transform=ax.transAxes, fontsize=13, color=MUTED)

ax.legend(handles=[
    Patch(facecolor=CORAL, label="Reported (SEC filings)"),
    Patch(facecolor="#f6d9cf", edgecolor=DEEP, linestyle=(0, (5, 3)),
          label="Analyst consensus"),
    Patch(facecolor="#dceadf", edgecolor=GREEN, linestyle=(0, (5, 3)),
          label="Nvidia's growth guidance, applied"),
], loc="upper left", frameon=False, fontsize=11.5, ncol=1,
    bbox_to_anchor=(0.005, 0.965))

fig.text(0.008, 0.028,
         "Source: Nvidia revenue from SEC filings (FY2024 to FY2026). FY2027 is the analyst consensus of about \\$396 billion.\n"
         "Nvidia guided to about 70% growth in FY2028, a rate and not a dollar figure: that is \\$673 billion on the consensus\n"
         "base and about \\$700 billion on higher estimates.",
         fontsize=9.2, color=MUTED, ha="left", va="bottom", linespacing=1.5)

fig.subplots_adjust(left=0.075, right=0.985, top=0.845, bottom=0.185)

out = os.path.join(OUTDIR, f"nvidia-ramp-{STAMP}.png")
plain, branded = save_pair(fig, out, facecolor=CREAM)
print("wrote", plain)
print("wrote", branded)
