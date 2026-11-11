"""
make-tsmc-monthly-2026-chart.py  DATA_DIR  [outdir]

The 11/11/26 daily's second Stocks chart. Harv supplied "TSMC Sales Hit a
Record in October" (monthly revenue in 2026, NT$ billions, Jan 401 to Oct 587,
+59.7% YoY). Rebuilt as OUR chart from TSMC's own monthly revenue reports, with
the same months of 2025 drawn underneath so the year over year gap is visible.

Emits BOTH:
  tsmc-monthly-111126.png      plain HB monogram    -> RE email + Agent Hub
  tsmc-monthly-111126-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds TSMC's monthly revenue reports as filed with the SEC on Form 6-K
(CIK 1046179, tsm-revenueYYYYMMDD.htm, Oct. 2025 through Nov. 10, 2026). Each
report's table gives the month, the prior month and the same month a year
earlier (NT$ million, consolidated, unaudited).

=============================================================================
VERIFICATION 11/11/26
=============================================================================
* Every month is printed in up to three reports; all copies agree (asserted).
* 2026: 401,255 / 317,657 / 415,191 / 410,726 / 416,975 / 442,680 / 467,580 /
  514,806 / 511,857 / 586,890. All ten points of the supplied graphic match.
* October 2026 is up 59.7% from 367,473 a year earlier and 14.7% from September,
  and it is the largest month in every report back to September 2024 (the
  previous high was August 2026's 514,806).

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import glob
import html
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
STAMP = "111126"

CREAM = "#fdf6e8"
INK = "#1f2933"
RED = "#c8102e"
SAND = "#b9a888"
GRID = "#e6dcc8"
MUTED = "#8a8172"

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


def load():
    ser = {}
    for f in sorted(glob.glob(os.path.join(DATA, "tsm-revenue*.htm"))):
        t = open(f, encoding="utf-8", errors="ignore").read()
        t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
        t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))
        m = re.search(r"Period (\w+) (\d{4}) (\w+) (\d{4}) M-o-M.*?(\w+) (\d{4}) Y-o-Y.*?"
                      r"Net Revenue ([\d,]+) ([\d,]+) \(?-?[\d.]+\)? ([\d,]+) \(?-?[\d.]+\)?", t)
        assert m, f
        cm, cy, pm, py, am, ay, cur, prev, ago = m.groups()
        for mm, yy, v in ((cm, cy, cur), (pm, py, prev), (am, ay, ago)):
            k = (int(yy), MONTHS.index(mm) + 1)
            v = int(v.replace(",", ""))
            assert ser.get(k, v) == v, (k, ser[k], v, f)       # every repeat of a month agrees
            ser[k] = v
    y26 = [ser[(2026, m)] for m in range(1, 11)]
    y25 = [ser[(2025, m)] for m in range(1, 11)]
    assert y26 == [401255, 317657, 415191, 410726, 416975, 442680, 467580, 514806, 511857, 586890], y26
    assert max(ser.values()) == 586890 and min(ser) <= (2024, 9), (max(ser.values()), min(ser))
    yoy = (Decimal(y26[-1]) / Decimal(y25[-1]) - 1) * 100
    assert yoy.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP) == Decimal("59.7"), yoy
    return y25, y26


def bn(v):
    return int((Decimal(v) / 1000).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def build():
    y25, y26 = load()
    fig = plt.figure(figsize=(14.0, 7.8), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.16, 0.80, 0.60])
    ax.set_facecolor(CREAM)
    x = list(range(10))
    a = [v / 1000 for v in y26]
    p = [v / 1000 for v in y25]
    ax.fill_between(x, p, a, color=RED, alpha=0.10, zorder=2, lw=0)
    ax.plot(x, p, color=SAND, lw=3, zorder=3, marker="o", ms=6, mfc=CREAM, mew=2)
    ax.plot(x, a, color=RED, lw=3.6, zorder=4, marker="o", ms=7, mfc=CREAM, mew=2.2)
    ax.plot([9], [a[-1]], marker="o", ms=13, color=RED, zorder=5)
    for i in (0, 2, 5, 7):
        ax.text(i, a[i] + 14, str(bn(y26[i])), ha="center", va="bottom", fontsize=12.5, fontweight="bold", color=RED)
    ax.text(1, a[1] - 18, str(bn(y26[1])), ha="center", va="top", fontsize=12.5, fontweight="bold", color=RED)
    ax.text(9.35, a[-1], f"{bn(y26[-1])}", ha="left", va="center", fontsize=24, fontweight="bold", color=RED)
    ax.text(9.35, a[-1] - 34, "up 59.7% from\nOctober 2025", ha="left", va="top", fontsize=12.5, color=INK,
            linespacing=1.25)
    ax.text(9.35, p[-1], f"{bn(y25[-1])}", ha="left", va="center", fontsize=14, fontweight="bold", color="#8f7f5f")
    ax.text(3.0, p[3] - 40, "2025", ha="center", va="top", fontsize=13, fontweight="bold", color="#8f7f5f")
    ax.text(3.0, a[3] + 34, "2026", ha="center", va="bottom", fontsize=13, fontweight="bold", color=RED)
    for y in (300, 400, 500, 600):
        ax.axhline(y, color=GRID, lw=1, zorder=1, ls=(0, (4, 4)))
        ax.text(-0.45, y, str(y), ha="right", va="center", fontsize=12, color=MUTED)
    for i, m in enumerate(MONTHS[:10]):
        ax.text(i, 222, m[:3], ha="center", va="top", fontsize=13, color=INK, fontweight="bold" if i == 9 else "normal")
    ax.set_xlim(-0.6, 10.6)
    ax.set_ylim(230, 640)
    ax.axis("off")

    fig.text(0.035, 0.955, "TSMC Sales Hit a Record in October", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.897, "Monthly revenue, NT$ billions, January to October, 2026 against 2025", fontsize=13.5,
             color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.03, "Source: TSMC monthly revenue reports (consolidated, unaudited), filed with the SEC on Form 6-K.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"tsmc-monthly-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
