#!/usr/bin/env python3
"""
make-fed-uturn-2026-chart.py  DATA_DIR  [outdir]

The 10/29/26 daily's Fed chart. Harv attached the newsletter's "The Fed's Rate
U-Turn" graphic: fed funds target, upper bound, Jan. 2025 to Oct. 2026, "3 cuts
in late 2025", "5 straight holds", "Sept. hike", pill "OCT HOLD 4.00%", source
Federal Reserve FOMC statements. Emits BOTH:

  fed-uturn-102926.png      plain HB monogram    -> RE email + Agent Hub
  fed-uturn-102926-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR/dfedtaru.csv: FRED DFEDTARU (federal funds target range, upper limit),
daily, Dec. 15, 2024 to Oct. 29, 2026, fetched Oct. 29, 2026 about 11:05 AM PT.

=============================================================================
VERIFICATION 10/29/26
=============================================================================
* FRED changes in the window: 4.50 from Dec. 19, 2024; 4.25 from Sept. 18,
  2025; 4.00 from Oct. 30, 2025; 3.75 from Dec. 11, 2025; 4.00 from Sept. 17,
  2026. So three cuts in late 2025 and one hike in September 2026, as drawn.
* Holds between the Dec. 2025 cut and the Sept. 2026 hike: the Jan., Mar.,
  Apr., Jun. and Jul. 2026 meetings, five, as the graphic says.
* Oct. 28, 2026 statement (federalreserve.gov monetary20261028a): "decided to
  maintain the target range for the federal funds rate at 3-3/4 to 4 percent";
  Lisa D. Cook and Beth M. Hammack dissented, preferring a 1/4 point hike. The
  statement names no "voting for" list, so the copy says two dissents, not
  Market Briefs' "10-2".

matplotlib; build with python3.13 on Mac.
"""
import csv
import os
import sys
from datetime import date, datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "102926"

CREAM = "#fdf6e8"
INK = "#1f2933"
GREEN = "#2f7d4f"
FILL = "#d9eadb"
CORAL = "#d9643a"
GRID = "#d8cdb8"
MUTED = "#8a8172"

START, END = date(2025, 1, 1), date(2026, 10, 29)


def load():
    rows = list(csv.reader(open(os.path.join(DATA, "dfedtaru.csv"))))[1:]
    s = {date.fromisoformat(d): float(v) for d, v in rows if v not in ("", ".")}
    ser = sorted((k, v) for k, v in s.items() if START <= k <= END)
    changes = [(k, v) for (k, v), (_, pv) in zip(ser[1:], ser[:-1]) if v != pv]
    assert ser[0] == (START, 4.50), ser[0]
    assert ser[-1] == (END, 4.00), ser[-1]
    assert changes == [(date(2025, 9, 18), 4.25), (date(2025, 10, 30), 4.00),
                       (date(2025, 12, 11), 3.75), (date(2026, 9, 17), 4.00)], changes
    return ser


def build():
    ser = load()
    xs = [datetime(k.year, k.month, k.day) for k, _ in ser]
    ys = [v for _, v in ser]
    hike = datetime(2026, 9, 17)
    hi = next(i for i, x in enumerate(xs) if x == hike)

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.07, 0.12, 0.74, 0.69])
    ax.set_facecolor(CREAM)

    FLOOR = 3.5
    ax.fill_between(xs, FLOOR, ys, step="post", color=FILL, lw=0, zorder=1, alpha=0.9)
    ax.step(xs[:hi + 1], ys[:hi + 1], where="post", color=GREEN, lw=3.0, zorder=4)
    ax.step(xs[hi - 1:], ys[hi - 1:], where="post", color=CORAL, lw=3.0, zorder=5)

    ax.text(datetime(2025, 3, 15), 4.36, "Holds through summer 2025", fontsize=13, color=MUTED,
            ha="left", va="center")
    ax.text(datetime(2025, 9, 1), 4.53, "3 cuts in late 2025", fontsize=14.5, fontweight="bold",
            color=INK, ha="left", va="bottom")
    ax.text(datetime(2026, 4, 15), 3.68, "5 straight holds", fontsize=14.5, fontweight="bold",
            color=GREEN, ha="center", va="center")
    ax.text(datetime(2026, 9, 10), 4.07, "Sept. hike", fontsize=14.5, fontweight="bold",
            color=CORAL, ha="right", va="bottom")

    ex = xs[-1]
    ax.scatter([ex], [ys[-1]], s=110, color=CORAL, edgecolor=CREAM, linewidth=2, zorder=7)
    ax.annotate("Oct. hold\n4.00%", xy=(ex, ys[-1]), xytext=(18, 0), textcoords="offset points",
                fontsize=17, fontweight="bold", color="white", ha="left", va="center",
                zorder=8, annotation_clip=False,
                bbox=dict(boxstyle="round,pad=0.45", facecolor=CORAL, edgecolor="none"))

    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
    ax.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda v, _: (lambda d: d.strftime("%b") + ("" if d.month == 5 else ".") + d.strftime(" '%y"))(
            mdates.num2date(v))))
    ax.set_xlim(datetime(2024, 12, 20), datetime(2026, 11, 10))
    ax.set_ylim(FLOOR, 4.75)
    ticks = [3.50, 3.75, 4.00, 4.25, 4.50, 4.75]
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"{v:.2f}%" for v in ticks], fontsize=12.5, color=MUTED)
    ax.tick_params(axis="x", labelsize=12.5, colors=MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.035, 0.955, "The Fed's Rate U-Turn", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.895,
             "Fed funds target rate (upper bound), Jan. 2025 to Oct. 29, 2026. Two officials dissented Oct. 28, wanting another hike.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035,
             "Source: Federal Reserve FOMC statements; FRED series DFEDTARU (Federal Reserve Bank of St. Louis).",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"fed-uturn-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
