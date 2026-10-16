#!/usr/bin/env python3
"""
make-holiday-sales-2026-chart.py  [outdir]

The 10/16/26 daily's Economy chart. Harv attached the newsletter's "Holiday
Sales Set to Speed Up" graphic: forecast growth in 2026 U.S. holiday retail
sales vs. 2025, Mastercard 5.5%, Deloitte 4.0 to 4.8%, Bain 4.5%, NRF 4.2%,
and a single "2025 actual 3.1%" bar. Emits BOTH:

  holiday-sales-101626.png      plain HB monogram    -> RE email + Agent Hub
  holiday-sales-101626-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 10/16/26 (every number read at the forecaster's own release)
=============================================================================
* NRF, press release Oct. 15, 2026: Nov. and Dec. sales "will grow 4.2% over
  2025 ... $1.013 trillion"; "last year's holiday sales rose 3.1% over 2024
  totaling $972 billion". Excludes autos, gas stations and restaurants.
* Deloitte, press release Sept. 10, 2026: Nov. 2026 through Jan. 2027,
  $1.70 to $1.71 trillion, up 4.0% to 4.8%; "In 2025, holiday sales
  increased by 4.1% in the same period."
* Bain & Company, press release Sept. 3, 2026: Nov. and Dec. sales to grow
  4.5% YoY (nominal), topping $1 trillion; the 2025 season rose 3.5%.
  "Inflation will account for more than half of the nominal rise."
* Mastercard Economics Institute, holiday report Sept. 23, 2026: retail sales
  excluding gas and autos, Nov. 1 to Dec. 24, up 5.5%; "2.8pp of the 5.5%
  growth rate reflects inflation". Its 2025 season: SpendingPulse release
  Dec. 23, 2025, retail ex autos up 3.9% Nov. 1 to Dec. 21 (preliminary).

THE FIX: the supplied graphic's lone "2025 actual 3.1%" is NRF's yardstick
only. Each forecaster measures a different window and basket, and their own
2025 figures run 3.1% to 4.1%. So each forecast is drawn next to its OWN 2025
result. Read that way, three of four do speed up, and Deloitte's range sits
about where its 2025 landed (4.1%).

matplotlib; build with python3.13 on Mac.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "101626"

CREAM = "#fdf6e8"
INK = "#1f2933"
BLUE = "#2b6cb0"
LIGHT = "#9fbbd9"
GREY = "#b9ad93"
GRID = "#d8cdb8"
MUTED = "#8a8172"
CORAL = "#c0503a"

# (name, 2025 own result, 2026 forecast low, 2026 forecast high)
ROWS = [
    ("Mastercard", 3.9, 5.5, 5.5),
    ("Bain", 3.5, 4.5, 4.5),
    ("Deloitte", 4.1, 4.0, 4.8),
    ("NRF", 3.1, 4.2, 4.2),
]


def build():
    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.15, 0.16, 0.78, 0.64])
    ax.set_facecolor(CREAM)

    H = 0.34
    for i, (name, y25, lo, hi) in enumerate(ROWS):
        yc = len(ROWS) - 1 - i
        y26, y25b = yc + H / 2 + 0.02, yc - H / 2 - 0.02
        # 2026 forecast
        ax.barh(y26, lo, height=H, color=BLUE, zorder=3)
        if hi > lo:
            ax.add_patch(Rectangle((lo, y26 - H / 2), hi - lo, H, facecolor=LIGHT,
                                   edgecolor=BLUE, hatch="///", lw=0, zorder=3))
            lab = f"{lo:.1f}% to {hi:.1f}%"
        else:
            lab = f"{hi:.1f}%"
        ax.text(hi + 0.08, y26, lab, va="center", ha="left", fontsize=16,
                fontweight="bold", color=BLUE)
        # its own 2025 result
        ax.barh(y25b, y25, height=H, color=GREY, zorder=3)
        ax.text(y25 + 0.08, y25b, f"{y25:.1f}% in 2025", va="center", ha="left",
                fontsize=13, color=MUTED)
        ax.text(-0.12, yc, name, va="center", ha="right", fontsize=18,
                fontweight="bold", color=INK)

    ax.text(6.35, 0.0, "About half of the gain\nis higher prices, say\nMastercard and Bain.",
            ha="right", va="center", fontsize=13, color=CORAL, fontstyle="italic",
            linespacing=1.35)

    ax.set_xlim(0, 6.4)
    ax.set_ylim(-0.6, len(ROWS) - 0.4)
    ax.set_xticks([0, 1, 2, 3, 4, 5, 6])
    ax.set_xticklabels(["0%", "1%", "2%", "3%", "4%", "5%", "6%"], fontsize=12, color=MUTED)
    ax.set_yticks([])
    ax.tick_params(axis="x", length=0, pad=8)
    ax.grid(axis="x", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # legend chips, top left of the plot
    lx, ly = 0.15, 0.835
    fig.patches.append(Rectangle((lx, ly), 0.018, 0.022, transform=fig.transFigure,
                                 facecolor=BLUE, edgecolor="none"))
    fig.text(lx + 0.024, ly + 0.011, "2026 forecast", fontsize=13, color=INK, va="center")
    fig.patches.append(Rectangle((lx + 0.15, ly), 0.018, 0.022, transform=fig.transFigure,
                                 facecolor=GREY, edgecolor="none"))
    fig.text(lx + 0.174, ly + 0.011, "Same forecaster's 2025 result", fontsize=13,
             color=INK, va="center")

    fig.text(0.035, 0.955, "Holiday Sales Set to Speed Up", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895, "Forecast growth in 2026 U.S. holiday retail sales, next to "
             "each forecaster's own 2025 result.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.055, "Source: NRF (Oct. 15, 2026), Deloitte (Sept. 10), Bain & Company "
             "(Sept. 3), Mastercard Economics Institute (Sept. 23); Mastercard SpendingPulse "
             "(Dec. 23, 2025).", fontsize=10.2, color=MUTED, ha="left", va="bottom")
    fig.text(0.035, 0.025, "Windows differ: NRF and Bain Nov. to Dec., Deloitte Nov. to Jan., "
             "Mastercard Nov. 1 to Dec. 24 (its 2025 figure is Nov. 1 to Dec. 21, preliminary).",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"holiday-sales-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
