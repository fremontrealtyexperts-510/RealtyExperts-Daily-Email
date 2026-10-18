#!/usr/bin/env python3
"""
make-eastbay-homes-vs-income-chart.py  DATA_DIR  [outdir]

The 10/18/26 Sunday daily's Real Estate chart. Market Briefs' Sunday essay
("Inflation nation") said that since 1971 U.S. household income grew about 8
times and home prices 17 times. KEEP IT LOCAL: this is the East Bay version, on
the longest window where all three local series exist (1989 to 2024). Emits BOTH:

  eastbay-homes-vs-income-101826.png      plain HB monogram    -> RE email + Agent Hub
  eastbay-homes-vs-income-101826-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds (fetched Oct. 18, 2026 about 11:25 AM PT):
  fred-ATNHPIUS36084Q.csv  FHFA all-transactions house price index, Oakland-
                           Berkeley-Livermore MSAD (Alameda + Contra Costa), quarterly
  fred-MHICA06001A052NCEN.csv  Census SAIPE median household income, Alameda County,
                           annual (1989, 1993, 1995 on; 1990 to 92, 94, 96 blank)
  bls-*.json               BLS API v1, CUUSS49BSA0 (CPI-U, San Francisco-Oakland-
                           Hayward), semiannual S01/S02; annual = their mean

Each line is indexed to its 1989 annual average = 1x.

=============================================================================
VERIFICATION 10/18/26
=============================================================================
1989 -> 2024: HPI 100.89 -> 478.53 (4.74x); income $34,732 -> $128,031
(3.69x); Bay Area CPI 126.35 -> 348.42 (2.76x).
Latest HPI: Q2 2026 456.00, down 4.8% from Q2 2025 (478.99) and 4.7% below the
2024 average. Footer says values have eased since 2024.
National check of the Market Briefs claim: MSPUS 1971 avg $25,225 -> 2025 avg
$415,400 = 16.5x ("17 times": about right).

matplotlib; build with python3.13 on Mac.
"""
import csv
import glob
import json
import os
import sys
from statistics import mean

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "101826"
Y0, Y1 = 1989, 2024

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e05a47"
DEEP = "#b8432f"
GREEN = "#2f855a"
GREEN_D = "#22643f"
SLATE = "#6b7280"
GRID = "#d8cdb8"
MUTED = "#8a8172"


def fred(name):
    out = {}
    with open(os.path.join(DATA, f"fred-{name}.csv")) as f:
        for row in list(csv.reader(f))[1:]:
            if row[1] in ("", "."):
                continue
            out.setdefault(int(row[0][:4]), []).append(float(row[1]))
    return out


def bay_cpi():
    halves = {}
    for path in glob.glob(os.path.join(DATA, "bls-*.json")):
        for s in json.load(open(path))["Results"]["series"]:
            if s["seriesID"] != "CUUSS49BSA0":
                continue
            for x in s["data"]:
                halves.setdefault(int(x["year"]), {})[x["period"]] = float(x["value"])
    return {y: mean(v.values()) for y, v in halves.items() if len(v) == 2}


def build():
    hpi_q = fred("ATNHPIUS36084Q")
    hpi = {y: mean(v) for y, v in hpi_q.items() if len(v) == 4}
    inc = {y: v[0] for y, v in fred("MHICA06001A052NCEN").items()}
    cpi = bay_cpi()

    lines = {
        "hpi": {y: hpi[y] / hpi[Y0] for y in range(Y0, Y1 + 1)},
        "inc": {y: inc[y] / inc[Y0] for y in range(Y0, Y1 + 1) if y in inc},
        "cpi": {y: cpi[y] / cpi[Y0] for y in range(Y0, Y1 + 1)},
    }
    end = {k: v[Y1] for k, v in lines.items()}
    assert round(end["hpi"], 2) == 4.74 and round(end["inc"], 2) == 3.69 and round(end["cpi"], 2) == 2.76, end
    q2 = hpi_q[2026][1]
    assert q2 == 456.00, q2
    eased = (q2 / hpi[2024] - 1) * 100
    assert round(eased, 1) == -4.7, eased

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.065, 0.15, 0.66, 0.62])
    ax.set_facecolor(CREAM)

    style = {
        "hpi": (CORAL, 3.0, "East Bay\nhome values"),
        "inc": (GREEN, 2.6, "Alameda County\nmedian household\nincome"),
        "cpi": (SLATE, 2.2, "Bay Area\nconsumer prices"),
    }
    for key in ("cpi", "inc", "hpi"):
        color, lw, _ = style[key]
        ys = sorted(lines[key])
        ax.plot(ys, [lines[key][y] for y in ys], color=color, lw=lw, solid_joinstyle="round",
                marker="o" if key == "inc" else None, markersize=3.5, zorder=4)

    # direct end labels
    label_y = {"hpi": end["hpi"], "inc": end["inc"], "cpi": end["cpi"]}
    for key, (color, _, name) in style.items():
        ax.scatter([Y1], [end[key]], s=90, color=color, edgecolor=CREAM, linewidth=1.8, zorder=6)
        ax.text(Y1 + 0.8, label_y[key], f"{end[key]:.1f}x", fontsize=21, fontweight="bold",
                color=color, ha="left", va="center")
        ax.text(Y1 + 4.6, label_y[key], name, fontsize=12.5, color=color, ha="left", va="center",
                linespacing=1.15, fontweight="bold")

    ax.set_xlim(Y0 - 0.5, Y1 + 0.5)
    ax.set_ylim(0.6, 5.4)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1x", "2x", "3x", "4x", "5x"], fontsize=11.5, color=MUTED)
    ax.set_xticks([1989, 1994, 1999, 2004, 2009, 2014, 2019, 2024])
    for t in ax.get_xticklabels():
        t.set_fontsize(12)
        t.set_color(MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.035, 0.955, "East Bay Homes Outran Paychecks and Prices", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895, f"Growth since {Y0}, each line indexed to its {Y0} level (1x), "
             f"through {Y1}, the latest year all three are published", fontsize=13.2,
             color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.845, "Incomes beat inflation, and owning beat both.",
             fontsize=14, color=INK, ha="left", va="top")
    fig.text(0.035, 0.068, "Sources: FHFA all-transactions house price index (Oakland-Berkeley-"
             "Livermore: Alameda and Contra Costa counties); Census SAIPE; BLS CPI-U San Francisco-"
             "Oakland-Hayward.", fontsize=10.2, color=MUTED, ha="left", va="bottom")
    fig.text(0.035, 0.035, f"Home values have eased since: the index for spring 2026 is "
             f"{abs(eased):.1f}% below its 2024 average. Income is missing for 1990 to 1992, 1994 and 1996.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"eastbay-homes-vs-income-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
