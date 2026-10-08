#!/usr/bin/env python3
"""
make-manheim-2026-chart.py  DATA_DIR  [outdir]

The 10/08/26 daily's used car chart (Economy section). Harv attached the
newsletter graphic "Used Car Prices Are Cooling" (Manheim Used Vehicle Value
Index, 2026, Jan to Sep; "Peak: 215.3" in March, 205.9 in September,
"down 4.4% since March"; "Source: Cox Automotive / Manheim, Oct. 2026").
Emits BOTH:

  manheim-100826.png      plain HB monogram    -> RE email + Agent Hub
  manheim-100826-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds muvvi-sept-2026.xlsx, Cox Automotive's own data file linked
from "Manheim Used Vehicle Value Index: September 2026 Trends" (Oct. 7, 2026):
  coxautoinc.com/wp-content/uploads/2026/10/Sept-2026-Manheim-Used-Vehicle-Value-Index.xlsx
Sheet DATA, column B "Index (1/97 = 100)", mix, mileage and seasonally adjusted.

=============================================================================
VERIFICATION 10/08/26
=============================================================================
Cox release, verbatim: "The Manheim Used Vehicle Value Index (MUVVI) in
September was 205.9, reflecting a 0.6% decrease ... compared to September
2025. The index is down 1.1% month over month." The xlsx gives Sep 205.88,
Sep 2025 207.03 (-0.55%), Aug 208.18 (-1.10%). Every labeled point on the
supplied graphic matches the file to one decimal: Feb 212.3, Mar 215.3 (peak),
Apr 211.9, May 212.6, Jun 212.9, Jul 210.0, Aug 208.2, Sep 205.9. January is
210.48, so 210.5 (the graphic's line sits near 210.6; unlabeled there).
"Down 4.4% since March": 205.88 / 215.28 = -4.36%. September is the first
negative year over year reading of 2026 (Jan +2.4% ... Aug +0.4%, Sep -0.6%).
Q3 press release: Cox "now expects the Manheim Used Vehicle Value Index to end
2026 up approximately 0.2% year over year, down from the 2% increase forecast
in July"; "last year's increase of 0.4%" equals the Dec 2025 y/y in the file
(+0.38%), so the forecast is a December y/y: 205.54 x 1.002 = about 206.0.

matplotlib + openpyxl; build with python3.13 on Mac.
"""
import os
import sys
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "100826"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e05a47"
DEEP = "#b8432f"
SLATE = "#9a9081"
GREEN = "#2f855a"
GRID = "#d8cdb8"
MUTED = "#8a8172"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def r1(x):
    return Decimal(str(x)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def load():
    wb = openpyxl.load_workbook(os.path.join(DATA, "muvvi-sept-2026.xlsx"), data_only=True)
    ws = wb["DATA"]
    idx = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if isinstance(row[0], datetime) and row[1] is not None:
            idx[(row[0].year, row[0].month)] = Decimal(str(row[1]))
    y26 = [idx[(2026, m)] for m in range(1, 10)]
    y25 = [idx[(2025, m)] for m in range(1, 13)]
    assert (2026, 10) not in idx, "file has October; this chart is the September release"
    # every label on the supplied graphic
    want = {2: "212.3", 3: "215.3", 4: "211.9", 5: "212.6", 6: "212.9", 7: "210.0", 8: "208.2", 9: "205.9"}
    for m, v in want.items():
        assert r1(y26[m - 1]) == Decimal(v), (m, y26[m - 1])
    assert max(y26) == y26[2]                                            # March is the peak
    since_mar = (y26[8] / y26[2] - 1) * 100
    assert r1(since_mar) == Decimal("-4.4"), since_mar
    yoy_sep = (y26[8] / y25[8] - 1) * 100
    assert r1(yoy_sep) == Decimal("-0.6"), yoy_sep                       # Cox: down 0.6% y/y
    assert all(y26[i] > y25[i] for i in range(8)) and y26[8] < y25[8]    # first y/y drop of 2026
    dec_yoy_25 = (y25[11] / idx[(2024, 12)] - 1) * 100
    assert r1(dec_yoy_25) == Decimal("0.4"), dec_yoy_25                  # "last year's increase of 0.4%"
    forecast_dec = y25[11] * Decimal("1.002")
    return y26, y25, forecast_dec


def build():
    y26, y25, fdec = load()
    x26 = list(range(1, 10))
    x25 = list(range(1, 13))
    v26 = [float(v) for v in y26]
    v25 = [float(v) for v in y25]

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.06, 0.15, 0.89, 0.64])
    ax.set_facecolor(CREAM)

    # 2025 for reference
    ax.plot(x25, v25, color=SLATE, lw=2.0, ls=(0, (4, 3)), zorder=2)
    ax.text(10, v25[9] - 0.45, "2025", fontsize=12.5, color=SLATE, ha="center", va="top", fontweight="bold")

    # 2026
    ax.fill_between(x26, v26, 200, color=CORAL, alpha=0.10, lw=0, zorder=1)
    ax.plot(x26, v26, color=CORAL, lw=3.4, solid_joinstyle="round", zorder=4)
    ax.scatter(x26, v26, s=26, color=CORAL, zorder=5)

    # Cox's year end forecast, dotted from September
    ax.plot([9, 12], [v26[8], float(fdec)], color=CORAL, lw=2.0, ls=(0, (1, 2.5)), zorder=3)
    ax.scatter([12], [float(fdec)], s=90, color=CREAM, edgecolor=CORAL, linewidth=2.2, zorder=5)
    ax.annotate("Cox forecast for\nDecember: about 206,\nup just 0.2% on the year",
                xy=(12, float(fdec)), xytext=(4, 16), textcoords="offset points",
                fontsize=11.5, color=DEEP, ha="right", va="bottom", linespacing=1.25, zorder=6)

    # March peak
    ax.annotate(f"Peak: {r1(y26[2])}", xy=(3, v26[2]), xytext=(0, 16), textcoords="offset points",
                fontsize=15, fontweight="bold", color=INK, ha="center", va="bottom", zorder=7,
                bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=GRID))
    ax.scatter([3], [v26[2]], s=110, color=CREAM, edgecolor=CORAL, linewidth=2.6, zorder=6)

    # September
    ax.scatter([9], [v26[8]], s=140, color=CORAL, edgecolor=CREAM, linewidth=2, zorder=7)
    ax.annotate(f"September {r1(y26[8])}", xy=(9, v26[8]), xytext=(-16, -8), textcoords="offset points",
                fontsize=16, fontweight="bold", color="white", ha="right", va="top", zorder=8,
                bbox=dict(boxstyle="round,pad=0.35", facecolor=CORAL, edgecolor="none"))

    since_mar = abs(r1((y26[8] / y26[2] - 1) * 100))
    yoy = abs(r1((y26[8] / y25[8] - 1) * 100))
    ax.text(5.05, 217.6, f"Down {since_mar}% since March", fontsize=17, fontweight="bold",
            color=DEEP, ha="left", va="top")
    ax.text(5.05, 216.25, f"and {yoy}% below September 2025, the first\nyear over year drop of 2026",
            fontsize=12.5, color=INK, ha="left", va="top", linespacing=1.3)
    ax.text(1.0, v26[0] - 0.75, "2026", fontsize=13, color=CORAL, fontweight="bold", ha="left", va="top")

    ax.set_xlim(0.6, 12.75)
    ax.set_ylim(200, 218)
    ax.set_xticks(x25)
    ax.set_xticklabels(MONTHS, fontsize=12, color=MUTED)
    ax.set_yticks([200, 204, 208, 212, 216])
    ax.set_yticklabels(["200", "204", "208", "212", "216"], fontsize=11, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.035, 0.955, "Used Car Prices Are Cooling", fontsize=26, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.895,
             "Manheim Used Vehicle Value Index, wholesale prices adjusted for mix, mileage and season "
             "(January 1997 = 100)",
             fontsize=13.2, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.030,
             "Source: Cox Automotive, Manheim Used Vehicle Value Index data file and Q3 2026 press release, "
             "Oct. 7, 2026.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"manheim-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
