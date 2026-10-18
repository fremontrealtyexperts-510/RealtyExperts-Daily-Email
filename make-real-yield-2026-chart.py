#!/usr/bin/env python3
"""
make-real-yield-2026-chart.py  DATA_DIR  [outdir]

The 10/18/26 Sunday daily's Economy chart. No supplied graphic: Market Briefs'
Sunday edition ("Inflation nation": can inflation shrink the $40T debt, the
1940s playbook, the "hidden tax" on lenders) gave the theme. The point: in the
1940s, 1970s and 2021 to 2023, the 10-year paid LESS than inflation (the hidden
tax the essay describes). Since June 2023 it has paid more. Emits BOTH:

  real-yield-101826.png      plain HB monogram    -> RE email + Agent Hub
  real-yield-101826-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds the FRED downloads (fetched Oct. 18, 2026 about 11:25 AM PT):
  fred-GS10.csv      10-year Treasury constant maturity, monthly avg, Apr. 1953 on
  fred-LTGOVTBD.csv  long-term U.S. government bonds (10+ years), monthly, 1925 to 2000
  fred-CPIAUCNS.csv  CPI-U all items, not seasonally adjusted, monthly

Real yield = that month's yield minus CPI inflation over the prior 12 months
(ex post). LTGOVTBD is used through Mar. 1953, GS10 from Apr. 1953 (its first
month); the footer says so.

=============================================================================
VERIFICATION 10/18/26
=============================================================================
Mar. 1947: yield 2.19, CPI y/y 19.67, real -17.48 (series low).
Mar. 1951 (Treasury-Fed Accord): real -6.85. Dec. 1974: -4.91.
Jun. 1984: +9.34 (series high). Mar. 2022: -6.41 (low since 2015).
Last negative month May 2023; positive every month since June 2023.
Sept. 2026: GS10 4.99, CPI y/y 3.74, real +1.25.
Market Briefs: "10-year was 5.24% that day [Oct. 1], up from 4.13% a year
earlier": Treasury daily curve 10/01/2026 5.24 (right), 10/01/2025 4.12
(4.13 was 10/03/2025; close enough).

matplotlib; build with python3.13 on Mac.
"""
import csv
import os
import sys
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "101826"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e05a47"
DEEP = "#b8432f"
GREEN = "#2f855a"
GREEN_D = "#22643f"
GRID = "#d8cdb8"
MUTED = "#8a8172"


def monthly(name):
    out = {}
    with open(os.path.join(DATA, f"fred-{name}.csv")) as f:
        for row in list(csv.reader(f))[1:]:
            if row[1] in ("", "."):
                continue
            out[row[0][:7]] = float(row[1])
    return out


def real_series():
    lt, g10, cpi = monthly("LTGOVTBD"), monthly("GS10"), monthly("CPIAUCNS")
    pts = []
    for ym in sorted(cpi):
        y, m = int(ym[:4]), int(ym[5:])
        prev = f"{y - 1}-{m:02d}"
        if y < 1942 or prev not in cpi:
            continue
        nom = g10.get(ym) if ym >= "1953-04" else lt.get(ym)
        if nom is None:
            continue
        infl = (cpi[ym] / cpi[prev] - 1) * 100
        pts.append((date(y, m, 15), nom, infl, nom - infl))
    return pts


def build():
    pts = real_series()
    by = {(d.year, d.month): p for p in pts for d in [p[0]]}
    low = min(pts, key=lambda p: p[3])
    last = pts[-1]
    assert (low[0].year, low[0].month) == (1947, 3) and round(low[3], 2) == -17.48, low
    assert (last[0].year, last[0].month) == (2026, 9), last
    assert round(last[1], 2) == 4.99 and round(last[2], 2) == 3.74 and round(last[3], 2) == 1.25, last
    p22 = by[(2022, 3)]
    assert round(p22[3], 2) == -6.41, p22
    neg = [p for p in pts if p[3] < 0]
    assert (neg[-1][0].year, neg[-1][0].month) == (2023, 5), neg[-1]
    p74 = by[(1974, 12)]

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.065, 0.15, 0.86, 0.60])
    ax.set_facecolor(CREAM)

    xs = [p[0] for p in pts]
    ys = [p[3] for p in pts]
    ax.fill_between(xs, ys, 0, where=[v < 0 for v in ys], interpolate=True,
                    color=CORAL, alpha=0.30, lw=0, zorder=2)
    ax.fill_between(xs, ys, 0, where=[v >= 0 for v in ys], interpolate=True,
                    color=GREEN, alpha=0.22, lw=0, zorder=2)
    ax.plot(xs, ys, color=INK, lw=1.3, zorder=3)
    ax.axhline(0, color=INK, lw=1.1, zorder=3)

    # zone labels
    ax.text(date(1987, 1, 1), 7.6, "Lenders ahead of inflation", fontsize=14, fontweight="bold",
            color=GREEN_D, ha="left", va="bottom")
    ax.text(date(1987, 1, 1), -9.5, "Lenders behind inflation:\nthe \"hidden tax\"", fontsize=14,
            fontweight="bold", color=DEEP, ha="left", va="top", linespacing=1.25)

    # callouts
    ax.annotate("1947: 2.2% yield,\n19.7% inflation", xy=(low[0], low[3]),
                xytext=(date(1953, 6, 1), -15.2), fontsize=12, color=DEEP, ha="left", va="center",
                linespacing=1.25, arrowprops=dict(arrowstyle="-", color=DEEP, lw=1.0))
    ax.annotate("1951: Fed freed\nto raise rates", xy=(date(1951, 3, 15), by[(1951, 3)][3]),
                xytext=(date(1957, 6, 1), -8.6), fontsize=12, color=INK, ha="left", va="center",
                linespacing=1.25, arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.0))
    ax.text(date(1977, 6, 1), -6.0, "1970s", fontsize=12, color=DEEP, ha="center", va="top")
    ax.annotate("2022", xy=(p22[0], p22[3]), xytext=(0, -10), textcoords="offset points",
                fontsize=12, color=DEEP, ha="center", va="top")

    ax.scatter([last[0]], [last[3]], s=120, color=GREEN, edgecolor=CREAM, linewidth=2, zorder=6)
    ax.annotate(f"+{last[3]:.1f}", xy=(last[0], last[3]), xytext=(10, 22), textcoords="offset points",
                fontsize=19, fontweight="bold", color="white", ha="left", va="bottom", zorder=7,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=GREEN, edgecolor="none"))

    ax.set_xlim(date(1941, 6, 1), date(2029, 6, 1))
    ax.set_ylim(-19, 11)
    ticks = [-15, -10, -5, 0, 5, 10]
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"{t:+d}" if t else "0" for t in ticks], fontsize=11.5, color=MUTED)
    ax.xaxis.set_major_locator(mdates.YearLocator(10, month=1, day=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    for t in ax.get_xticklabels():
        t.set_fontsize(12)
        t.set_color(MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.035, 0.955, "Bonds Pay More Than Inflation Again", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895, "10-year Treasury yield minus inflation over the past 12 months, "
             "in percentage points, 1942 to Sept. 2026", fontsize=13.2, color=MUTED,
             ha="left", va="top")
    fig.text(0.035, 0.845, f"September 2026: the 10-Year averaged {last[1]:.2f}% while prices rose "
             f"{last[2]:.2f}%. Positive every month since June 2023.",
             fontsize=14, color=INK, ha="left", va="top")
    fig.text(0.035, 0.055, "Sources: Federal Reserve 10-year constant maturity yield (long-term "
             "government bond yield before Apr. 1953) and BLS CPI-U, via FRED.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"real-yield-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
