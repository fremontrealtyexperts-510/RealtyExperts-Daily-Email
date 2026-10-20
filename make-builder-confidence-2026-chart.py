#!/usr/bin/env python3
"""
make-builder-confidence-2026-chart.py  XLS_DIR  [outdir]

The 10/20/26 daily's Real Estate chart: our recreation of the supplied graphic
"Builder Confidence Hits 14-Year Low" (NAHB Housing Market Index, 2026,
"Lowest since June 2012", source NAHB/Wells Fargo, Oct. 19, 2026).

Emits BOTH:
  builder-confidence-102026.png      plain HB monogram    -> RE email + Agent Hub
  builder-confidence-102026-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

=============================================================================
SOURCE AND VERIFICATION
=============================================================================
XLS_DIR holds NAHB's own October 2026 tables from nahb.org/hmi
(Last-Modified Mon, 19 Oct 2026 13:59 GMT):
  t1-nahb-wells-fargo-national-and-regional-hmi-202610.xls  national + regional
  t2-national-hmi-history-202610.xls                        national since 1985

Every plotted value is read from those files, never typed. The supplied
graphic's ten points (Jan 37, Feb 37, Mar 38, Apr 34, May 37, Jun 36, Jul 34,
Aug 35, Sep 32, Oct 29) are asserted against the file: all ten match.

The headline is a separate claim and is tested on its own (rule of 08/19/26):
June 2012 read 29, and every month from July 2012 through September 2026 is
above 29. The closest was April 2020 at 30, the pandemic shock, so the chart
draws that level as the thing October is being compared against.

ADDED (same publisher, same survey): the West region, which includes
California, as NAHB's three month moving average. NAHB reports regions only
as 3 month averages because the regional samples are small, so the West line
is labeled that way and is not compared point for point with the national
monthly reading in the copy. West Oct 2026 = 26, the lowest of the four
regions (Northeast 38, Midwest 40, South 30).

matplotlib only; build with python3.13 on Mac.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import xlrd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

XLS = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "102026"

CREAM = "#fdf6e8"
INK = "#1f2933"
GRID = "#e4d9c4"
MUTED = "#8a8172"
CORAL = "#e2574c"
SLATE = "#4f6d8a"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"]
SUPPLIED = [37, 37, 38, 34, 37, 36, 34, 35, 32, 29]


def t1_series(sheet, row, yr_row, mo_row):
    """Return {(year, 'Mon'): value} for one row of Table 1."""
    out, yr = {}, None
    for c in range(3, sheet.ncols):
        y = sheet.cell_value(yr_row, c)
        if isinstance(y, float) and y > 1900:
            yr = int(y)
        m = str(sheet.cell_value(mo_row, c)).strip().rstrip(".")
        v = sheet.cell_value(row, c)
        if m and v != "" and yr:
            out[(yr, m[:3])] = float(v)
    return out


def load():
    b1 = xlrd.open_workbook(os.path.join(XLS, "t1-nahb-wells-fargo-national-and-regional-hmi-202610.xls"))
    s1 = b1.sheet_by_index(0)
    assert str(s1.cell_value(6, 0)).strip() == "Housing Market Index"
    assert str(s1.cell_value(37, 0)).strip() == "West"
    assert "3 MONTH" in str(s1.cell_value(27, 0)).upper()
    nat = t1_series(s1, 6, 2, 3)
    west3 = t1_series(s1, 37, 28, 29)
    ne3, mw3, s3 = (t1_series(s1, r, 28, 29) for r in (31, 33, 35))

    b2 = xlrd.open_workbook(os.path.join(XLS, "t2-national-hmi-history-202610.xls"))
    s2 = b2.sheet_by_index(0)
    hist = {}
    for r in range(3, s2.nrows):
        y = s2.cell_value(r, 0)
        if not isinstance(y, float):
            continue
        for c, m in enumerate(MONTHS + ["Nov", "Dec"], start=1):
            v = s2.cell_value(r, c)
            if v != "":
                hist[(int(y), m)] = float(v)

    national = [nat[(2026, m)] for m in MONTHS]
    west = [west3[(2026, m)] for m in MONTHS]
    # the two NAHB tables agree with each other and with the supplied graphic
    assert national == [hist[(2026, m)] for m in MONTHS]
    assert [int(v) for v in national] == SUPPLIED, national
    # regional ranking quoted in the copy
    assert (ne3[(2026, "Oct")], mw3[(2026, "Oct")], s3[(2026, "Oct")], west[-1]) == (38, 40, 30, 26)
    # the headline: lowest since June 2012
    order = MONTHS + ["Nov", "Dec"]
    keys = sorted(hist, key=lambda k: (k[0], order.index(k[1])))
    jun12 = keys.index((2012, "Jun"))
    between = [hist[k] for k in keys[jun12 + 1:keys.index((2026, "Oct"))]]
    assert hist[(2012, "Jun")] == 29 and min(between) == 30, (hist[(2012, "Jun")], min(between))
    assert hist[(2020, "Apr")] == 30
    return national, west


def build():
    national, west = load()
    x = list(range(len(MONTHS)))

    fig = plt.figure(figsize=(14.0, 8.4), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.06, 0.15, 0.90, 0.64])
    ax.set_facecolor(CREAM)

    # what October is compared against: the April 2020 pandemic low of 30
    ax.axhline(30, color=MUTED, lw=1.3, ls=(0, (2, 3)), zorder=2)
    ax.text(4.25, 30.3, "30 = April 2020 pandemic low, the floor until now",
            fontsize=12, color=MUTED, ha="left", va="bottom", zorder=3,
            bbox=dict(boxstyle="square,pad=0.1", facecolor=CREAM, edgecolor="none"))

    # West region, NAHB's 3 month average
    ax.plot(x, west, color=SLATE, lw=2.4, ls=(0, (6, 3)), marker="o", ms=5.5,
            zorder=4, alpha=0.9)
    ax.text(x[-1], west[-1] - 0.9, f"West {west[-1]:.0f}", fontsize=13.5,
            color=SLATE, fontweight="bold", ha="center", va="top")

    # the national index, as on the supplied graphic
    ax.plot(x, national, color=CORAL, lw=3.6, marker="o", ms=9, zorder=5,
            solid_capstyle="round")
    for i, v in enumerate(national[:-1]):
        ax.text(x[i], v + 0.65, f"{v:.0f}", fontsize=15, fontweight="bold",
                color=INK, ha="center", va="bottom", zorder=6)
    box_y = national[-1] + 7.0
    ax.annotate(f"{national[-1]:.0f}", xy=(x[-1], national[-1]),
                xytext=(x[-1], box_y), fontsize=30,
                fontweight="bold", color="white", ha="center", va="center", zorder=7,
                bbox=dict(boxstyle="round,pad=0.32", facecolor=CORAL, edgecolor="none"),
                arrowprops=dict(arrowstyle="-", color=CORAL, lw=2.2, shrinkA=0, shrinkB=6))
    ax.text(x[-1] - 0.42, box_y, "Lowest since\nJune 2012",
            fontsize=13, fontweight="bold", color=CORAL, ha="right", va="center")

    ax.set_xlim(-0.35, len(MONTHS) - 0.2)
    ax.set_ylim(22, 42)
    ax.set_xticks(x)
    ax.set_xticklabels(MONTHS, fontsize=14, fontweight="bold", color=INK)
    ax.set_yticks([24, 28, 32, 36, 40])
    ax.tick_params(axis="y", labelsize=12, colors=MUTED, length=0)
    ax.tick_params(axis="x", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=1.0, zorder=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.035, 0.955, "Builder Confidence Hits 14-Year Low", fontsize=27,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.893,
             "NAHB/Wells Fargo Housing Market Index, 2026. October fell 3 points to 29. "
             "Above 50 means more builders call conditions good than poor.",
             fontsize=13.2, color=MUTED, ha="left", va="top")
    # legend row: real line samples, not text glyphs
    from matplotlib.lines import Line2D
    fig.add_artist(Line2D([0.060, 0.076, 0.092], [0.835, 0.835, 0.835], color=CORAL, lw=3.6,
                          marker="o", ms=8, markevery=[1], transform=fig.transFigure))
    fig.text(0.100, 0.835, "U.S. index, monthly", color=INK, fontsize=13.5,
             ha="left", va="center")
    fig.add_artist(Line2D([0.262, 0.278, 0.294], [0.835, 0.835, 0.835], color=SLATE, lw=2.4,
                          ls=(0, (4, 2)), marker="o", ms=5.5, markevery=[1],
                          transform=fig.transFigure))
    fig.text(0.302, 0.835, "West region, which includes California (NAHB 3 month average)",
             color=INK, fontsize=13.5, ha="left", va="center")
    fig.text(0.035, 0.035,
             "Source: NAHB/Wells Fargo Housing Market Index, seasonally adjusted, released Oct. 19, 2026 "
             "(national monthly; regional figures are NAHB's\nthree month moving averages). "
             "June 2012 read 29; every month since was 30 or higher until October.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.45)
    return fig, national, west


if __name__ == "__main__":
    fig, national, west = build()
    out = os.path.join(OUTDIR, f"builder-confidence-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    print("national", [int(v) for v in national])
    print("west 3mo", [int(v) for v in west])
