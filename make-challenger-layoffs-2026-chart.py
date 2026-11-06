"""
make-challenger-layoffs-2026-chart.py  DATA_DIR  [outdir]

The 11/06/26 daily's Economy chart. Harv supplied a Market Briefs style graphic,
"Layoffs Cool Off" (Challenger, Gray & Christmas, U.S. job cuts announced each
month, 153K in October 2025 to 44K in October 2026, -71% Y/Y). Recreated as OUR
chart from Challenger's own report, with California's October figure called
out (the state led all states; Challenger has no metro breakdown).

Emits BOTH:
  challenger-layoffs-110626.png      plain HB monogram    -> RE email + Agent Hub
  challenger-layoffs-110626-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR/report.txt is `pdftotext -layout` of
https://www.challengergray.com/wp-content/uploads/2026/11/Challenger-Report-October-2026.pdf
(released 5:30 AM ET Thursday, November 5, 2026). Table 1 "MONTH BY MONTH TOTALS".

=============================================================================
VERIFICATION 11/06/26
=============================================================================
* All 13 points of the supplied graphic match Table 1 (153,074 ... 43,994).
* Table 1 columns sum EXACTLY to its printed TOTAL row: 2026 Jan to Oct
  617,189; 2025 full year 1,206,374 (asserted below).
* -71%: 43,994 / 153,074 - 1 = -71.26%; the release says "down 71%".
* California, from the release text: 10,032 in October 2026, down 29% from
  14,206 in October 2025; 124,850 year to date, 20% of all cuts.
* No reuse restriction found in the release or the PDF (unlike ISM, S&P Global,
  MBA and ADP); the page carries only a copyright line. Attributed on the chart.
* These are ANNOUNCED cuts, which can be spread over months or never happen;
  the footer says so.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "110626"

CREAM = "#fdf6e8"
INK = "#1f2933"
RED = "#d1495b"
GREEN = "#2e8b57"
SAND = "#c9b48f"
GRID = "#e6dcc8"
MUTED = "#8a8172"
AXIS = "#8a7f6a"
ORANGE = "#ea580c"

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
ABBR = {m: m[:3] for m in MONTHS}

SUPPLIED = [153, 71, 35, 108, 48, 60, 83, 97, 46, 33, 53, 43, 44]   # thousands, as read off the graphic


def load():
    t = open(os.path.join(DATA, "report.txt"), encoding="utf-8").read()
    i = t.index("MONTH BY MONTH TOTALS")
    block = t[i:t.index("LAYOFF LOCATION", i)]
    y26, y25 = {}, {}
    for m in MONTHS:
        g = re.search(r"^\s*%s\s+([\d,]+)(?:\s+([\d,]+))?\s*$" % m, block, flags=re.M)
        assert g, m
        a, b = g.group(1), g.group(2)
        if b is None:                       # Nov/Dec: only the 2025 column is filled
            y25[m] = int(a.replace(",", ""))
        else:
            y26[m] = int(a.replace(",", ""))
            y25[m] = int(b.replace(",", ""))
    tot = re.search(r"^\s*TOTAL\s+([\d,]+)\s+([\d,]+)\s*$", block, flags=re.M)
    assert sum(y26.values()) == int(tot.group(1).replace(",", "")) == 617189, sum(y26.values())
    assert sum(y25.values()) == int(tot.group(2).replace(",", "")) == 1206374, sum(y25.values())
    series = [("Oct", "2025", y25["October"]), ("Nov", "", y25["November"]), ("Dec", "", y25["December"])]
    series += [(ABBR[m], "2026" if m == "January" else "", y26[m]) for m in MONTHS[:10]]
    assert series[0][2] == 153074 and series[-1][2] == 43994, series
    # every supplied point within rounding of the report (the graphic truncates some, rounds others)
    for (lab, _, v), s in zip(series, SUPPLIED):
        assert abs(v / 1000 - s) < 1.0, (lab, v, s)
    yoy = (Decimal(series[-1][2]) / Decimal(series[0][2]) - 1) * 100
    assert yoy.quantize(Decimal("1"), rounding=ROUND_HALF_UP) == Decimal("-71"), yoy
    return series


def k(v):
    return f"{Decimal(v / 1000).quantize(Decimal('1'), rounding=ROUND_HALF_UP)}K"


def build():
    series = load()
    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.17, 0.89, 0.60])
    ax.set_facecolor(CREAM)
    n = len(series)
    for i, (lab, yr, v) in enumerate(series):
        last, first = i == n - 1, i == 0
        color = RED if first else GREEN if last else SAND
        ax.bar(i, v / 1000, width=0.68, color=color, zorder=3)
        ax.text(i, v / 1000 + 2.2, k(v), ha="center", va="bottom", fontsize=14 if (first or last) else 12,
                fontweight="bold", color=color if (first or last) else "#6f6450")
        ax.text(i, -6, lab, ha="center", va="top", fontsize=13, color=INK, fontweight="bold" if (first or last) else "normal")
        if yr:
            ax.text(i, -14, yr, ha="center", va="top", fontsize=11.5, color=MUTED)
    for y in (50, 100, 150):
        ax.axhline(y, color=GRID, lw=1, zorder=1)
        ax.text(-0.75, y, f"{y}K", ha="right", va="center", fontsize=11, color=MUTED)
    ax.axhline(0, color=AXIS, lw=1.4, zorder=4)
    ax.set_xlim(-0.8, n - 0.4)
    ax.set_ylim(0, 168)
    ax.axis("off")

    # the year over year call out, beside the last bar
    ax.annotate("", xy=(n - 1, series[-1][2] / 1000 + 14), xytext=(n - 1, 128),
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=2), zorder=5)
    ax.text(n - 1, 131, "−71% from\nOctober 2025", ha="center", va="bottom", fontsize=14, fontweight="bold",
            color=GREEN, linespacing=1.15)

    # California box, upper middle where the bars are short
    fig.text(0.47, 0.842, "California led all states in October", fontsize=13.5, fontweight="bold",
             color=ORANGE, ha="left", va="top")
    fig.text(0.47, 0.808, "10,032 cuts, down 29% from 14,206 a year earlier;\n124,850 so far in 2026, 20% of the U.S. total",
             fontsize=12.5, color=INK, ha="left", va="top", linespacing=1.35)

    fig.text(0.035, 0.955, "Layoff Announcements Cool Off", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.897, "Job cuts announced by U.S. employers each month, October 2025 to October 2026",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.03, "Source: Challenger, Gray & Christmas, Job Cut Announcement Report, October 2026. "
             "Announced cuts, which may take effect over months.", fontsize=10.2, color=MUTED, ha="left",
             va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"challenger-layoffs-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
