#!/usr/bin/env python3
"""
make-cola-2027-chart.py  [outdir]

The 10/14/26 daily's Social Security chart. Harv attached the newsletter graphic
"Retirees' Biggest Raise Since 2023" (COLA by year: 2022 5.9%, 2023 8.7%, 2024
3.2%, 2025 2.5%, 2026 2.8%, and a hatched "2027 est. ~3.5%" from The Senior
Citizens League, "official figure due Oct. 14"). Emits BOTH:

  cola-2027-101426.png      plain HB monogram    -> RE email + Agent Hub
  cola-2027-101426-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 10/14/26
=============================================================================
* The official figure is out, so the estimate bar is replaced. SSA, Oct. 14,
  2026 (ssa.gov/cola): "Social Security and Supplemental Security Income (SSI)
  benefits for 76 million Americans will increase 3.6 percent in 2027." Not the
  newsletter's ~3.5%.
* Cross-check from BLS CPI-W (CWUR0000SA0), released the same morning:
  Q3 2026 average (327.104 + 328.481 + 330.654) / 3 = 328.746 over Q3 2025
  (316.349 + 317.306 + 318.139) / 3 = 317.265 = 3.62%, rounds to 3.6.
* History, SSA's own table (ssa.gov/oact/cola/colaseries.html) lists each COLA
  under the December it takes effect: 2021 5.9, 2022 8.7, 2023 3.2, 2024 2.5,
  2025 2.8, 2026 3.6. Benefits rise with the January payment, so by the year it
  is PAID (the newsletter's and SSA fact sheets' convention, "the 2027 COLA")
  that is 2022 5.9 ... 2027 3.6. All five historical bars match.
* "Biggest since 2023" holds: 3.6 beats 2024's 3.2, 2025's 2.5, 2026's 2.8.
* Dollars, SSA 2027 COLA fact sheet: average for all retired workers $2,095
  before the COLA, $2,170 after (+$75). The newsletter's "$68 to about $2,008"
  was an outdated estimate.

matplotlib; build with python3.13 on Mac.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "101426"

# SSA colaseries, keyed by December effective -> shifted to the year paid
SSA_BY_DECEMBER = {2021: 5.9, 2022: 8.7, 2023: 3.2, 2024: 2.5, 2025: 2.8, 2026: 3.6}
PAID = {y + 1: v for y, v in SSA_BY_DECEMBER.items()}
BEFORE, AFTER = 2095, 2170           # SSA fact sheet, all retired workers

CREAM = "#fdf6e8"
INK = "#1f2933"
BLUE = "#2b6cb0"
GREEN = "#2f7d4f"
GREEN_BG = "#e3efe4"
GRID = "#d8cdb8"
MUTED = "#8a8172"


def build():
    years = sorted(PAID)
    vals = [PAID[y] for y in years]
    assert years == [2022, 2023, 2024, 2025, 2026, 2027]
    assert vals == [5.9, 8.7, 3.2, 2.5, 2.8, 3.6], vals
    assert vals[-1] > max(vals[2:5]) and vals[-1] < vals[1]   # biggest since 2023
    assert AFTER - BEFORE == 75

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.05, 0.13, 0.62, 0.66])
    ax.set_facecolor(CREAM)

    x = list(range(len(years)))
    colors = [BLUE] * 5 + [GREEN]
    ax.bar(x, vals, width=0.66, color=colors, zorder=3)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.18, f"{v:.1f}%", ha="center", va="bottom", fontsize=19,
                fontweight="bold", color=colors[i])
    ax.text(5, vals[-1] + 1.05, "official", ha="center", va="bottom", fontsize=12.5,
            color=GREEN, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in years], fontsize=15, fontweight="bold", color=INK)
    ax.get_xticklabels()[-1].set_color(GREEN)
    ax.set_ylim(0, 10)
    ax.set_yticks([])
    ax.tick_params(axis="x", length=0, pad=8)
    ax.axhline(0, color=INK, lw=1.6, zorder=4)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # right panel: what it means in dollars
    px = 0.71
    fig.text(px, 0.72, "Average retired worker, per month", fontsize=13.5, color=MUTED,
             ha="left", va="top")
    fig.text(px, 0.665, f"${BEFORE:,}", fontsize=30, fontweight="bold", color=BLUE,
             ha="left", va="top")
    fig.text(px + 0.115, 0.655, "to", fontsize=16, color=MUTED, ha="left", va="top")
    fig.text(px + 0.15, 0.665, f"${AFTER:,}", fontsize=30, fontweight="bold", color=GREEN,
             ha="left", va="top")
    fig.text(px, 0.565, f"+\\${AFTER - BEFORE} a month starting in January",
             fontsize=14, fontweight="bold", color=INK, ha="left", va="top",
             bbox=dict(boxstyle="round,pad=0.45", facecolor=GREEN_BG, edgecolor="none"))
    fig.text(px, 0.44, "Also changing in 2027:", fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(px, 0.40, r"Taxable maximum \$184,500 to \$192,300", fontsize=13.5, color=INK,
             ha="left", va="top")
    fig.text(px, 0.36, "Earnings limit under full retirement", fontsize=13.5, color=INK,
             ha="left", va="top")
    fig.text(px, 0.325, r"age \$24,480 to \$25,560 a year", fontsize=13.5, color=INK,
             ha="left", va="top")

    fig.text(0.035, 0.955, "Retirees Get Their Biggest Raise Since 2023", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895, "Social Security cost of living adjustment (COLA), by the year it is "
             "paid. The 2027 figure was announced Oct. 14.", fontsize=13.2, color=MUTED,
             ha="left", va="top")
    fig.text(0.035, 0.035, "Source: Social Security Administration COLA history and 2027 COLA "
             "fact sheet (Oct. 14, 2026).", fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"cola-2027-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
