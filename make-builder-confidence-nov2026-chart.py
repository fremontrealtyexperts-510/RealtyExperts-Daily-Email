#!/usr/bin/env python3
"""
make-builder-confidence-nov2026-chart.py  XLS_DIR  MLS_CSV  [outdir]

The 11/18/26 daily's Real Estate chart: our recreation of the supplied graphic
"Builder Confidence Hits 14-Year Low" (NAHB/Wells Fargo Housing Market Index,
Nov. 2025 to Nov. 2026, latest 25), plus a LOCAL band from today's MLS export.

Emits BOTH:
  builder-confidence-111826.png      plain HB monogram    -> RE email + Agent Hub
  builder-confidence-111826-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

SOURCE AND VERIFICATION
XLS_DIR holds NAHB's own November 2026 tables from nahb.org/hmi
(Last-Modified Tue, 17 Nov 2026 14:48 GMT):
  t1-nahb-wells-fargo-national-and-regional-hmi-202611.xls  national + regional
  t2-national-hmi-history-202611.xls                        national since 1985
Every plotted value is read from those files. All 13 points on the supplied
graphic (38 39 37 37 38 34 37 36 34 35 32 29 25) are asserted against both
tables. The headline is tested on its own: 25 is the lowest reading since
April 2012 (24); every month from May 2012 through October 2026 is above 25.
ADDED: the West region (includes California) as NAHB's 3 month average,
23 in November, the lowest of the four regions and the lowest since Jan 2012.

LOCAL BAND: MLS_CSV is today's dated export (dump-mls-csv.js). Same basis as
the 10/20/26 chart: new = YrBlt 2025 or 2026; for sale = ACTV NEW CS BOMK PCH;
in contract = PEND. The Oct. 20 comparison (19 of 52 in the five cities) is
from that day's export, recorded in session-2026-10-20 memory.

matplotlib only; build with python3.13 on Mac.
"""
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
import xlrd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

XLS, CSV = sys.argv[1], sys.argv[2]
OUTDIR = sys.argv[3] if len(sys.argv) > 3 else "."
STAMP = "111826"

CREAM = "#fdf6e8"
INK = "#1f2933"
GRID = "#e4d9c4"
MUTED = "#8a8172"
CORAL = "#e2574c"
SLATE = "#4f6d8a"
GREEN = "#2f7d4f"
LOCAL = "#efe3c8"
ORDER = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
KEYS = [(2025, "Nov"), (2025, "Dec")] + [(2026, m) for m in ORDER[:11]]
LABELS = ["Nov\n'25", "Dec", "Jan\n'26", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov\n'26"]
SUPPLIED = [38, 39, 37, 37, 38, 34, 37, 36, 34, 35, 32, 29, 25]
FIVE = {"FREMONT", "HAYWARD", "MILPITAS", "NEWARK", "UNION CITY"}
FOR_SALE = {"ACTV", "NEW", "CS", "BOMK", "PCH"}


def t1_series(sheet, row, yr_row, mo_row):
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


def load_nahb():
    s1 = xlrd.open_workbook(os.path.join(XLS, "t1-nahb-wells-fargo-national-and-regional-hmi-202611.xls")).sheet_by_index(0)
    assert str(s1.cell_value(6, 0)).strip() == "Housing Market Index"
    assert str(s1.cell_value(37, 0)).strip() == "West" and "3 MONTH" in str(s1.cell_value(27, 0)).upper()
    nat = t1_series(s1, 6, 2, 3)
    w3 = t1_series(s1, 37, 28, 29)
    ne3, mw3, so3 = (t1_series(s1, r, 28, 29) for r in (31, 33, 35))
    s2 = xlrd.open_workbook(os.path.join(XLS, "t2-national-hmi-history-202611.xls")).sheet_by_index(0)
    hist = {}
    for r in range(3, s2.nrows):
        y = s2.cell_value(r, 0)
        if isinstance(y, float):
            for c, m in enumerate(ORDER, start=1):
                v = s2.cell_value(r, c)
                if v != "":
                    hist[(int(y), m)] = float(v)
    national = [nat[k] for k in KEYS]
    west = [w3[k] for k in KEYS]
    assert national == [hist[k] for k in KEYS]
    assert [int(v) for v in national] == SUPPLIED, national
    # regional ranking in the copy: NE 34, MW 35, South 27, West 23
    assert (ne3[(2026, "Nov")], mw3[(2026, "Nov")], so3[(2026, "Nov")], west[-1]) == (34, 35, 27, 23)
    # headline: lowest since April 2012
    keys = sorted(hist, key=lambda k: (k[0], ORDER.index(k[1])))
    i = keys.index((2012, "Apr"))
    assert hist[(2012, "Apr")] == 24 and min(hist[k] for k in keys[i + 1:keys.index((2026, "Nov"))]) > 25
    # West 3 month: last at or below 23 was January 2012
    wk = sorted(w3, key=lambda k: (k[0], ORDER.index(k[1])))
    lower = [k for k in wk[:-1] if w3[k] <= 23]
    assert lower[-1] == (2012, "Jan"), lower[-3:]
    return national, west


def load_local():
    rows = list(csv.DictReader(open(CSV)))
    def count(sel, new):
        rs = [r for r in sel if (r["YrBlt"] in ("2025", "2026")) == new]
        return sum(r["Status"] in FOR_SALE for r in rs), sum(r["Status"] == "PEND" for r in rs)
    five = [r for r in rows if r["City"] in FIVE]
    loc = {"five_new": count(five, True), "five_resale": count(five, False),
           "board_new": count(rows, True), "board_resale": count(rows, False)}
    assert loc == {"five_new": (32, 10), "five_resale": (562, 178),
                   "board_new": (115, 21), "board_resale": (1748, 598)}, loc
    return loc


def pct(fs_ic):
    fs, ic = fs_ic
    return round(100 * ic / (fs + ic))


def build():
    national, west = load_nahb()
    loc = load_local()
    x = list(range(len(KEYS)))

    fig = plt.figure(figsize=(14.0, 9.4), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.06, 0.315, 0.90, 0.475])
    ax.set_facecolor(CREAM)

    ax.plot(x, west, color=SLATE, lw=2.4, ls=(0, (6, 3)), marker="o", ms=5.5, zorder=4, alpha=0.9)
    ax.text(x[-1] + 0.05, west[-1] - 1.1, f"West {west[-1]:.0f}", fontsize=13.5,
            color=SLATE, fontweight="bold", ha="center", va="top")
    ax.plot(x, national, color=CORAL, lw=3.6, marker="o", ms=9, zorder=5, solid_capstyle="round")
    for i, v in enumerate(national[:-1]):
        ax.text(x[i], v + 0.75, f"{v:.0f}", fontsize=15, fontweight="bold", color=INK,
                ha="center", va="bottom", zorder=6)
    box_y = national[-1] + 12.5
    ax.annotate(f"{national[-1]:.0f}", xy=(x[-1], national[-1]), xytext=(x[-1], box_y), fontsize=30,
                fontweight="bold", color="white", ha="center", va="center", zorder=7,
                bbox=dict(boxstyle="round,pad=0.32", facecolor=CORAL, edgecolor="none"),
                arrowprops=dict(arrowstyle="-", color=CORAL, lw=2.2, shrinkA=0, shrinkB=6))
    ax.text(x[-1] - 0.5, box_y, "Lowest since\nApril 2012", fontsize=13, fontweight="bold",
            color=CORAL, ha="right", va="center")

    ax.set_xlim(-0.4, len(KEYS) - 0.45)
    ax.set_ylim(18, 44)
    ax.set_xticks(x)
    ax.set_xticklabels(LABELS, fontsize=13, fontweight="bold", color=INK)
    ax.set_yticks([20, 25, 30, 35, 40])
    ax.tick_params(axis="y", labelsize=12, colors=MUTED, length=0)
    ax.tick_params(axis="x", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=1.0, zorder=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.035, 0.962, "Builder Confidence Hits 14-Year Low", fontsize=27, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.905, "NAHB/Wells Fargo Housing Market Index. November fell 4 points to 25. "
             "Above 50 means more builders call conditions good than poor.",
             fontsize=13.2, color=MUTED, ha="left", va="top")
    fig.add_artist(Line2D([0.060, 0.076, 0.092], [0.853, 0.853, 0.853], color=CORAL, lw=3.6,
                          marker="o", ms=8, markevery=[1], transform=fig.transFigure))
    fig.text(0.100, 0.853, "U.S. index, monthly", color=INK, fontsize=13.5, ha="left", va="center")
    fig.add_artist(Line2D([0.262, 0.278, 0.294], [0.853, 0.853, 0.853], color=SLATE, lw=2.4,
                          ls=(0, (4, 2)), marker="o", ms=5.5, markevery=[1], transform=fig.transFigure))
    fig.text(0.302, 0.853, "West region, which includes California (NAHB 3 month average)",
             color=INK, fontsize=13.5, ha="left", va="center")

    # LOCAL band
    fig.add_artist(FancyBboxPatch((0.035, 0.075), 0.93, 0.155, boxstyle="round,pad=0.004,rounding_size=0.012",
                                  transform=fig.transFigure, facecolor=LOCAL, edgecolor="none", zorder=0))
    fig.text(0.05, 0.212, "HERE, TODAY: BRAND NEW HOMES (BUILT 2025 OR 2026) VS RESALE, SHARE IN CONTRACT",
             fontsize=12.5, fontweight="bold", color=GREEN, ha="left", va="top")
    fn, fr, bn, br = loc["five_new"], loc["five_resale"], loc["board_new"], loc["board_resale"]
    cols = [
        (0.05, "Our five cities", f"New {fn[1]} of {sum(fn)} in contract ({pct(fn)}%)",
         f"Resale {pct(fr)}%. On Oct. 20 it was new 19 of 52 (37%)"),
        (0.52, "Bay East board", f"New {bn[1]} of {sum(bn)} in contract ({pct(bn)}%)",
         f"Resale {pct(br)}%. New homes lag resale"),
    ]
    for x0, head, big, small in cols:
        fig.text(x0, 0.172, head, fontsize=12.5, color=INK, ha="left", va="top")
        fig.text(x0, 0.140, big, fontsize=17, fontweight="bold", color=INK, ha="left", va="top")
        fig.text(x0, 0.100, small, fontsize=12, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.028,
             "Source: NAHB/Wells Fargo Housing Market Index, seasonally adjusted, released Nov. 17, 2026 (regional = NAHB 3 month "
             "averages). Local: Bay East MLS export of\nNov. 18, 2026; for sale = active, new, coming soon, back on market, price change; "
             "in contract = pending. Five cities = Fremont, Hayward, Milpitas, Newark, Union City.",
             fontsize=9.6, color=MUTED, ha="left", va="bottom", linespacing=1.45)
    return fig, national, west, loc


if __name__ == "__main__":
    fig, national, west, loc = build()
    out = os.path.join(OUTDIR, f"builder-confidence-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    print("national", [int(v) for v in national])
    print("west 3mo", [int(v) for v in west])
    print("local", loc)
