#!/usr/bin/env python3
"""
make-mortgage-apps-hmda-2026-chart.py  DATA_DIR  [outdir]

The 10/28/26 daily's Real Estate chart. Harv asked for deep research on mortgage
applications ("are they falling? are they growing?"). The weekly answer is the
MBA Weekly Applications Survey, but MBA's site terms bar copying or creating
derivative works from its content without written permission, and MBA sells the
weekly series by subscription. Same handling as ISM and S&P Global (memory
reference-ism-pmi-license-no-derived-charts): MBA's numbers go in the COPY as
text with attribution, and this chart tells the story from public data instead.

Public data here is HMDA, the federal Home Mortgage Disclosure Act filings that
lenders report every year (FFIEC / CFPB). It is the only official count of
mortgage applications by COUNTY, so it also answers "what about here"
(feedback-localize-national-studies). Emits BOTH:

  mortgage-apps-hmda-102826.png      plain HB monogram    -> RE email + Agent Hub
  mortgage-apps-hmda-102826-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds the HMDA Data Browser API pulls, one file per geography and year:
  alameda_YYYY.json  ffiec.cfpb.gov/v2/data-browser-api/view/aggregations
                     ?counties=06001&years=YYYY&loan_purposes=1,31,32&actions_taken=1,2,3,4,5
  us_YYYY.json       .../view/nationwide/aggregations?years=YYYY&loan_purposes=1,31,32
                     &actions_taken=1,2,3,4,5
An APPLICATION is a record with action taken 1 to 5 (originated, approved but not
accepted, denied, withdrawn, closed for incompleteness). Action 6 (loans bought
from another lender) is excluded so nothing counts twice; 7 and 8 are
preapproval requests, not applications. loan_purposes 1 = home purchase.

=============================================================================
VERIFICATION 10/28/26
=============================================================================
* Method check against a published number: the CFPB's 2023 Data Point
  ("Mortgage Market Activity and Trends", Dec. 2024) says closed end site built
  single family home purchase originations fell 21.3 percent, 4.1 million in
  2022 to 3.2 million in 2023. The same API with action 1 and purpose 1 gives
  4,381,012 to 3,452,630, down 21.2 percent. The 0.1 point gap is the
  manufactured and multifamily loans the CFPB leaves out.
* 2025 is the Snapshot published June 23, 2026 (FFIEC announcement, data as of
  June 1, 2026; 4,782 reporting institutions).

matplotlib; build with python3.13 on Mac.
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "102826"
YEARS = list(range(2018, 2026))

CREAM = "#fdf6e8"
INK = "#1f2933"
SLATE = "#6b7f99"
CORAL = "#e8734a"
GREEN = "#2f7d4f"
RED = "#d6363c"
GRID = "#d8cdb8"
MUTED = "#8a8172"


def purchase_apps(geo, year):
    d = json.load(open(os.path.join(DATA, f"{geo}_{year}.json")))
    p = d["parameters"]
    assert p["actions_taken"] == "1,2,3,4,5" and "1" in p["loan_purposes"].split(","), p
    rows = [a for a in d["aggregations"] if a["loan_purposes"] == "1"]
    assert sorted(a["actions_taken"] for a in rows) == ["1", "2", "3", "4", "5"], rows
    return sum(a["count"] for a in rows)


def pct(a, b):
    return (a / b - 1) * 100


def minus(s):
    return s.replace("-", "−")


def load():
    ala = {y: purchase_apps("alameda", y) for y in YEARS}
    us = {y: purchase_apps("us", y) for y in YEARS}
    # the numbers the copy quotes; a re-pull that moves them must fail loudly
    assert ala[2025] == 13940 and ala[2024] == 14973 and ala[2021] == 26227 and ala[2019] == 21382, ala
    assert us[2025] == 5374348 and us[2024] == 5316851 and us[2019] == 6422207, us
    assert max(ala, key=ala.get) == 2021
    return ala, us


def build():
    ala, us = load()
    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)

    # left: Alameda County by year
    ax = fig.add_axes([0.080, 0.15, 0.535, 0.63])
    ax.set_facecolor(CREAM)
    x = list(range(len(YEARS)))
    vals = [ala[y] for y in YEARS]
    colors = [CORAL if y == 2025 else SLATE for y in YEARS]
    ax.bar(x, vals, width=0.66, color=colors, zorder=3)
    for xi, v in zip(x, vals):
        ax.text(xi, v + 450, f"{v:,}", ha="center", va="bottom", fontsize=12.5,
                fontweight="bold", color=INK, zorder=5)
    ax.text(x[YEARS.index(2021)], ala[2021] + 2300, "2021 peak", ha="center",
            va="bottom", fontsize=12.5, color=MUTED, fontweight="bold")
    ax.text(x[-1], ala[2025] + 2300, "About half\nthe peak", ha="center", va="bottom",
            fontsize=12.5, color=CORAL, fontweight="bold", linespacing=1.1)
    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in YEARS], fontsize=13, color=MUTED, fontweight="bold")
    ax.set_xlim(-0.6, len(YEARS) - 0.4)
    ax.set_ylim(0, 33000)
    ax.set_yticks([0, 10000, 20000, 30000])
    ax.set_yticklabels(["0", "10,000", "20,000", "30,000"], fontsize=11.5, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=6)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.text(0.0, 1.035, "Alameda County, applications per year", transform=ax.transAxes,
            fontsize=14.5, fontweight="bold", color=INK, ha="left", va="bottom")

    # right: 2025 against 2024 and 2019, county vs nation
    bx = fig.add_axes([0.665, 0.15, 0.31, 0.63])
    bx.set_facecolor(CREAM)
    groups = [("vs. 2024", 2024), ("vs. 2019", 2019)]
    ypos = []
    for gi, (label, base) in enumerate(groups):
        yc = 1.6 - gi * 1.75
        for off, geo, series in ((0.32, "Alameda County", ala), (-0.32, "United States", us)):
            v = pct(series[2025], series[base])
            col = CORAL if geo.startswith("Alameda") else SLATE
            bx.barh(yc + off, v, height=0.5, color=col, zorder=3)
            txt = minus(f"{v:+.1f}%")
            if v >= 0:
                bx.text(v + 1.2, yc + off, txt, ha="left", va="center", fontsize=13,
                        fontweight="bold", color=GREEN, zorder=5)
            else:
                bx.text(v - 1.2, yc + off, txt, ha="right", va="center", fontsize=13,
                        fontweight="bold", color=RED, zorder=5)
            bx.text(1.5 if v < 0 else -1.5, yc + off, geo, ha="left" if v < 0 else "right",
                    va="center", fontsize=11.5, color=INK, zorder=5)
            ypos.append(yc + off)
        bx.text(-49, yc + 0.78, f"2025 {label}", ha="left", va="bottom", fontsize=13,
                fontweight="bold", color=MUTED)
    bx.axvline(0, color=INK, lw=1.1, zorder=4)
    bx.set_xlim(-50, 22)
    bx.set_ylim(-0.95, 2.75)
    bx.set_yticks([])
    bx.set_xticks([-40, -20, 0, 20])
    bx.set_xticklabels([minus("-40%"), minus("-20%"), "0%", "+20%"], fontsize=11.5, color=MUTED)
    bx.tick_params(axis="both", length=0, pad=6)
    bx.grid(axis="x", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    bx.set_axisbelow(True)
    for sp in bx.spines.values():
        sp.set_visible(False)
    bx.text(0.0, 1.035, "Change in applications", transform=bx.transAxes,
            fontsize=14.5, fontweight="bold", color=INK, ha="left", va="bottom")

    fig.text(0.035, 0.955, "Fewer Purchase Loan Applications in Alameda County", fontsize=25,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.897,
             "Home purchase loan applications reported by lenders under the federal Home Mortgage Disclosure Act.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035,
             "Source: FFIEC HMDA Data Browser (CFPB), 2018 to 2025; 2025 is the snapshot published June 2026. Applications that were approved, denied,\n"
             "withdrawn or closed incomplete, plus loans made; loans bought from other lenders are excluded.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.35)
    return fig, ala, us


if __name__ == "__main__":
    fig, ala, us = build()
    out = os.path.join(OUTDIR, f"mortgage-apps-hmda-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    print("wrote", out)
    for y in YEARS:
        print(f"  {y}  Alameda {ala[y]:>7,}   U.S. {us[y]:>10,}")
    print("  2025 vs 2024: Alameda %+.1f%%, U.S. %+.1f%%" % (pct(ala[2025], ala[2024]), pct(us[2025], us[2024])))
    print("  2025 vs 2019: Alameda %+.1f%%, U.S. %+.1f%%" % (pct(ala[2025], ala[2019]), pct(us[2025], us[2019])))
    print("  2025 vs 2021 peak: Alameda %+.1f%%" % pct(ala[2025], ala[2021]))
