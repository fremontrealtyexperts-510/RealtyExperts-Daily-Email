#!/usr/bin/env python3
"""
make-bayarea-young-tech-jobs-chart.py  DATA_DIR  [outdir]

The 10/23/26 daily's LOCAL answer to the UK youth jobs graphic: the same cut
for the Bay Area. Emits BOTH:

  bayarea-young-tech-jobs-102326.png      plain HB monogram    -> RE email + Agent Hub
  bayarea-young-tech-jobs-102326-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds qwi-bay5.csv, rows for Alameda (06001), Contra Costa (06013),
San Francisco (06075), San Mateo (06081) and Santa Clara (06085), 2022 on,
filtered from the Census Bureau's LEHD Quarterly Workforce Indicators file
lehd.ces.census.gov/data/qwi/latest_release/ca/qwi_ca_sa_f_gc_ns_op_u.csv.gz
(release R2026Q3, data through 2025 Q4; sex by age, all firms, county, NAICS
sector, all private ownership, not seasonally adjusted). Fetched Oct. 23, 2026.

=============================================================================
VERIFICATION 10/23/26
=============================================================================
* Measure = Emp, jobs on the first day of the quarter. EmpEnd for 2025 Q4 is
  blank (it needs the next quarter), so we compare Q4 2022 to Q4 2025: exactly
  three years, same season (Q3 carries a summer intern bump, so never mix it).
* Ages 19 to 24 = QWI groups A02 (19 to 21) + A03 (22 to 24); QWI has no 18.
* Every cell used carries status flag 1 (OK).
* Five county totals, Q4 2022 to Q4 2025:
    Information (NAICS 51)       13,281 -> 7,353    -44.6%
    Finance and insurance (52)    5,047 -> 4,233    -16.1%
    the two combined             18,328 -> 11,586   -36.8%
    all industries              229,495 -> 223,414   -2.6%
* Path, Q4 each year, information: 13,281, 9,137, 7,611, 7,353. Most of the
  drop came in 2023 and 2024; 2025 eased only 3.4%.

matplotlib; build with python3.13 on Mac.
"""
import csv
import os
import sys
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "102326"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e0614a"
SOFT = "#efa08f"
GREY = "#b9ad93"
MUTED = "#8a8172"
COUNTIES = {"06001", "06013", "06075", "06081", "06085"}


def pct(a, b):
    return float(((Decimal(b) / Decimal(a) - 1) * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def load():
    s = defaultdict(lambda: defaultdict(int))
    for r in csv.DictReader(open(os.path.join(DATA, "qwi-bay5.csv"))):
        if (r["geography"] in COUNTIES and r["sex"] == "0" and r["agegrp"] in ("A02", "A03")
                and r["industry"] in ("00", "51", "52") and r["ownercode"] == "A05"):
            q = (int(r["year"]), int(r["quarter"]))
            if q in ((2022, 4), (2023, 4), (2024, 4), (2025, 4)):
                assert r["Emp"] != "" and r["sEmp"] == "1", r
                s[r["industry"]][q] += int(r["Emp"])
    get = lambda ind: (s[ind][(2022, 4)], s[ind][(2025, 4)])
    d = {"tech": get("51"), "fin": get("52"), "all": get("00")}
    assert d == {"tech": (13281, 7353), "fin": (5047, 4233), "all": (229495, 223414)}, d
    assert [s["51"][(y, 4)] for y in (2022, 2023, 2024, 2025)] == [13281, 9137, 7611, 7353]
    d["both"] = (d["tech"][0] + d["fin"][0], d["tech"][1] + d["fin"][1])
    return d


def build():
    d = load()
    bars = [
        ("Information (tech)", pct(*d["tech"]), CORAL),
        ("Tech and finance\ncombined", pct(*d["both"]), CORAL),
        ("Finance and\ninsurance", pct(*d["fin"]), SOFT),
        ("All jobs, ages 19 to 24", pct(*d["all"]), GREY),
    ]
    assert [b[1] for b in bars] == [-44.6, -36.8, -16.1, -2.6], [b[1] for b in bars]
    counts = [d["tech"], d["both"], d["fin"], d["all"]]

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.25, 0.14, 0.50, 0.66])
    ax.set_facecolor(CREAM)

    ys = list(range(len(bars)))[::-1]
    for y, (name, v, col), (a, b) in zip(ys, bars, counts):
        ax.barh(y, abs(v), height=0.62, color=col, zorder=3)
        ax.text(abs(v) + 0.8, y + 0.07, f"−{abs(v):.1f}%", va="center", ha="left",
                fontsize=24, fontweight="bold", color=col if col != GREY else MUTED, zorder=4)
        ax.text(abs(v) + 0.8, y - 0.26, f"{a:,} to {b:,} jobs", va="center", ha="left",
                fontsize=11.5, color=MUTED, zorder=4)
        ax.text(-1.0, y, name, va="center", ha="right", fontsize=14.5, fontweight="bold", color=INK)

    ax.set_xlim(0, 61)
    ax.set_ylim(-0.6, len(bars) - 0.4)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.79, 0.70, "Same cut in the UK", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(0.79, 0.665, "tech −30.0%", fontsize=22, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.79, 0.61, "Dec. 2022 to Dec. 2025,\nages 18 to 24", fontsize=11.5, color=MUTED,
             ha="left", va="top", linespacing=1.35)
    fig.text(0.79, 0.49, "Young tech jobs,\nfall of each year", fontsize=13, color=MUTED, ha="left",
             va="top", linespacing=1.3)
    fig.text(0.79, 0.415, "2022  13,281\n2023    9,137\n2024    7,611\n2025    7,353", fontsize=14,
             fontweight="bold", color=INK, ha="left", va="top", linespacing=1.45, family="monospace")

    fig.text(0.035, 0.955, "Bay Area Tech Jobs for Young Workers Fell Even Faster", fontsize=25,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895,
             "Change in jobs held by 19 to 24 year olds, fall 2022 to fall 2025, in Alameda, Contra Costa,\n"
             "San Francisco, San Mateo and Santa Clara counties.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035,
             "Source: U.S. Census Bureau, Quarterly Workforce Indicators (LEHD), private jobs on the first day of the fourth quarter,\n"
             "2022 and 2025. Information is NAICS 51; finance and insurance is NAICS 52.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"bayarea-young-tech-jobs-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
