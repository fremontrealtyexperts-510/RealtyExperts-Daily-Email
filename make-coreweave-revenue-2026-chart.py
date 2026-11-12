"""
make-coreweave-revenue-2026-chart.py  XBRL_JSON  [outdir]

The 11/12/26 daily's Stocks chart. Harv supplied "CoreWeave's Revenue Keeps
Climbing" (quarterly revenue Q3 '25 to Q3 '26: $1.4B, $1.6B, $2.1B, $2.6B,
$3.7B, "up 168% from a year ago"). Rebuilt as OUR chart from CoreWeave's own SEC
filings, with the fourth quarter that the company's raised full year forecast
implies drawn as a dashed range.

Emits BOTH:
  coreweave-revenue-111226.png      plain HB monogram    -> RE email + Agent Hub
  coreweave-revenue-111226-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

XBRL_JSON is SEC's company concept file for CoreWeave, Inc. (CIK 1769628):
  https://data.sec.gov/api/xbrl/companyconcept/CIK0001769628/us-gaap/
          RevenueFromContractWithCustomerExcludingAssessedTax.json

=============================================================================
VERIFICATION 11/12/26
=============================================================================
* Quarters, $ millions, as filed in the 10-Qs and the 10-K: Q3 2025 1,365;
  Q4 2025 1,572 (= FY2025 5,131 less 982 + 1,212 + 1,365, and printed as 1,572
  in the Q4 2025 earnings release, 8-K filed Feb. 26, 2026); Q1 2026 2,078;
  Q2 2026 2,575; Q3 2026 3,661 (10-Q filed Nov. 12, 2026; earnings release
  8-K filed Nov. 10, 2026). All five bars of the supplied graphic match.
* Q3 2026 is up 168.2% from Q3 2025 and up 1,086 from Q2 2026, matching the
  release's "revenue increasing by more than $1 billion sequentially".
* Full year 2026 guidance raised to $13.0B to $13.3B (Nov. 10 release), so the
  fourth quarter it implies is 13,000 or 13,300 less 8,314 = $4.69B to $4.99B.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import json
import os
import sys
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

SRC = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "111226"

CREAM = "#fdf6e8"
INK = "#1f2933"
RED = "#c8102e"
SAND = "#b9a888"
GRID = "#e6dcc8"
MUTED = "#8a8172"
GREEN = "#2f7d4f"

GUIDE_LO, GUIDE_HI = 13000, 13300          # FY2026 revenue guidance, $M (Nov. 10, 2026 release)


def load():
    d = json.load(open(SRC))
    q, fy = {}, {}
    for u in d["units"]["USD"]:
        s, e = date.fromisoformat(u["start"]), date.fromisoformat(u["end"])
        days = (e - s).days
        rec = (u["filed"], u["val"] / 1e6)              # 2025 10-Qs carry thousands; 2026 filings print millions
        if 80 < days < 100:
            q.setdefault(u["end"], []).append(rec)
        elif days > 300:
            fy.setdefault(u["end"], []).append(rec)
    def one(dic, k):
        recs = sorted(dic[k])
        vals = [v for _, v in recs]
        assert max(vals) - min(vals) <= 1, (k, recs)     # every filing that repeats a period agrees within rounding
        return round(recs[-1][1])                        # the latest filing, as CoreWeave now presents it
    q3_25 = one(q, "2025-09-30")
    q1_25, q2_25 = one(q, "2025-03-31"), one(q, "2025-06-30")
    fy25 = one(fy, "2025-12-31")
    q4_25 = fy25 - q1_25 - q2_25 - q3_25
    q1, q2, q3 = one(q, "2026-03-31"), one(q, "2026-06-30"), one(q, "2026-09-30")
    vals = [q3_25, q4_25, q1, q2, q3]
    assert vals == [1365, 1572, 2078, 2575, 3661], vals
    yoy = (Decimal(q3) / Decimal(q3_25) - 1) * 100
    assert yoy.quantize(Decimal("1"), rounding=ROUND_HALF_UP) == 168, yoy
    assert q3 - q2 == 1086
    nine = q1 + q2 + q3
    return vals, (GUIDE_LO - nine, GUIDE_HI - nine)


def b2(m):
    return str((Decimal(m) / 1000).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def build():
    vals, (lo, hi) = load()
    assert (lo, hi) == (4686, 4986), (lo, hi)
    fig = plt.figure(figsize=(14.0, 7.8), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.16, 0.86, 0.60])
    ax.set_facecolor(CREAM)
    x = list(range(5))
    y = [v / 1000 for v in vals]

    ax.fill_between(x, 0, y, color=RED, alpha=0.08, zorder=2, lw=0)
    ax.plot(x, y, color=RED, lw=3.6, zorder=4, marker="o", ms=8, mfc=CREAM, mew=2.4)
    ax.plot([4], [y[4]], marker="o", ms=14, color=RED, zorder=5)

    # implied fourth quarter from the raised full year forecast
    ax.plot([4, 5], [y[4], (lo + hi) / 2000], color=RED, lw=2.2, ls=(0, (4, 4)), zorder=3, alpha=0.65)
    ax.add_patch(plt.Rectangle((4.82, lo / 1000), 0.36, (hi - lo) / 1000, facecolor=CREAM,
                               edgecolor=RED, hatch="///", lw=1.6, zorder=4, alpha=0.9))
    ax.text(5, hi / 1000 + 0.68, f"\\${b2(lo)}B to \\${b2(hi)}B", ha="center", va="bottom", fontsize=13.5,
            fontweight="bold", color=RED)
    ax.text(5, hi / 1000 + 0.12, "implied by the raised\nfull year forecast", ha="center", va="bottom",
            fontsize=11.5, color=MUTED, linespacing=1.2)

    for i in range(4):
        ax.text(i, y[i] + 0.20, f"\\${b2(vals[i])}B", ha="center", va="bottom", fontsize=15, fontweight="bold",
                color=INK)
    ax.text(3.78, 4.62, f"\\${b2(vals[4])}B", ha="right", va="bottom", fontsize=26, fontweight="bold",
            color=RED)
    ax.text(3.78, 4.55, "up 168% from a year ago\nand \\$1.09B from Q2", ha="right", va="top",
            fontsize=13, color=INK, linespacing=1.3)

    for g in (1, 2, 3, 4, 5):
        ax.axhline(g, color=GRID, lw=1, zorder=1, ls=(0, (4, 4)))
        ax.text(-0.42, g, f"\\${g}B", ha="right", va="center", fontsize=12, color=MUTED)
    labels = ["Q3 '25", "Q4 '25", "Q1 '26", "Q2 '26", "Q3 '26", "Q4 '26"]
    for i, lab in enumerate(labels):
        ax.text(i, -0.18, lab, ha="center", va="top", fontsize=14, color=MUTED if i == 5 else INK,
                fontweight="bold" if i == 4 else "normal")
    ax.axhline(0, color=SAND, lw=1.4, zorder=1)
    ax.set_xlim(-0.55, 5.45)
    ax.set_ylim(-0.05, 5.95)
    ax.axis("off")

    fig.text(0.035, 0.955, "CoreWeave's Revenue Keeps Climbing", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.897, "Quarterly revenue, third quarter 2025 to third quarter 2026, with the fourth quarter "
             "its 2026 forecast implies", fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.03, "Source: CoreWeave 10-Q and 10-K filings and earnings releases (SEC). Fourth quarter 2026 "
             "range = \\$13.0B to \\$13.3B full year guidance less nine months reported.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"coreweave-revenue-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
