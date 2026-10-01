#!/usr/bin/env python3
"""
make-rent-squeeze-chart.py  URBAN_TXT  ZORI_CITY_CSV  ZORI_METRO_CSV  [outdir]

Recreates the supplied graphic "The Rent Squeeze Moves Up" for the 10/01/26
daily, with a LOCAL second panel (feedback-localize-national-studies).

  rent-squeeze-100126.png      plain monogram -> RE email + Agent Hub
  rent-squeeze-100126-hb.png   + wordmark     -> harvrealtor.com / .net / app

URBAN_TXT is `pdftotext -layout` of the Urban Institute brief "Renters
Increasingly Struggle to Pay for Housing" (Karpman, Koch, Batko, Reynolds,
September 23, 2026):
  https://www.urban.org/sites/default/files/2026-09/Renters_Increasingly_Struggle_to_Pay_for_Housing.pdf
The ZORI files are Zillow's public smoothed all homes rent index CSVs
(reference-zori-local-rent-source):
  https://files.zillowstatic.com/research/public_csvs/zori/City_zori_uc_sfrcondomfr_sm_month.csv
  https://files.zillowstatic.com/research/public_csvs/zori/Metro_zori_uc_sfrcondomfr_sm_month.csv

=============================================================================
VERIFICATION 10/01/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

  supplied graphic                  Urban Institute brief
  Lower income  2024 26.4%          Figure 2 label 26.4% (no star)
  Lower income  2025 27.8%          text "(27.8 percent)"
  Middle income 2024 14.3%          text "from 14.3 percent to 21.6 percent"
  Middle income 2025 21.6%          same sentence; Figure 2 label 14.3%***

All four match. Two things the graphic got loose:
  1. Only the middle income rise is statistically significant (*** = differs
     from 2025 at the 0.01 level). The lower income +1.4 points has no star,
     so it is within the margin of error. Drawn grey and labeled as such.
  2. The measure is "did not pay the full amount of rent or was late with a
     payment because the household could not afford to pay", past 12 months,
     renters ages 18 to 64, asked each December. Subtitle says so.
Income bands are federal poverty level multiples, NOT area median income:
middle income = 200 to 400% of FPL, $53,300 to $106,600 for a family of
three. That is a low band for the Bay Area, which the footnote says.

The local panel is Zillow ZORI, August 2026 against August 2025, for our five
cities and the U.S. row from the metro file. Every value is read from the CSV
at build time; asserts pin the August 2026 levels checked on 10/01/26.

matplotlib only; build with python3.13 on Mac.
"""
import csv
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

URBAN, CITY_CSV, METRO_CSV = sys.argv[1:4]
OUTDIR = sys.argv[4] if len(sys.argv) > 4 else "."
STAMP = "100126"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
SLATE = "#6f8296"
PALE = "#a7b3c0"
GRID = "#d8cdb8"
MUTED = "#8a8172"

CITIES = ["Fremont", "Hayward", "Milpitas", "Newark", "Union City"]
MONTH, PRIOR = "2026-08-31", "2025-08-31"


def one(x):
    return Decimal(x).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def urban():
    t = open(URBAN, encoding="utf-8", errors="ignore").read()
    flat = re.sub(r"\s+", " ", t)
    # every figure on the left panel must appear in the brief
    assert "from 14.3 percent to 21.6 percent" in flat
    assert "(27.8 percent)" in flat
    assert "(20.0 percent)" in flat and "(16.5 percent)" in flat
    assert re.search(r"\b26\.4%", t) and re.search(r"\b14\.3%\*\*\*", t)
    assert re.search(r"\b4\.9%", t) and re.search(r"\b6\.9%", t)
    assert "did not pay the full amount of rent or was late with a payment" in flat
    # (label, 2024, 2025, significant)
    return [
        ("Lower income", Decimal("26.4"), Decimal("27.8"), False),
        ("All renters", Decimal("16.5"), Decimal("20.0"), True),
        ("Middle income", Decimal("14.3"), Decimal("21.6"), True),
        ("Higher income", Decimal("4.9"), Decimal("6.9"), False),
    ]


def zori():
    out = {}
    with open(CITY_CSV, newline="") as f:
        r = csv.reader(f)
        hdr = next(r)
        i, j = hdr.index(MONTH), hdr.index(PRIOR)
        assert hdr[-1] == MONTH, hdr[-1]
        for row in r:
            if row[5] == "CA" and row[2] in CITIES:
                out[row[2]] = (Decimal(row[i]), Decimal(row[j]))
    with open(METRO_CSV, newline="") as f:
        r = csv.reader(f)
        hdr = next(r)
        i, j = hdr.index(MONTH), hdr.index(PRIOR)
        for row in r:
            if row[2] == "United States":
                out["United States"] = (Decimal(row[i]), Decimal(row[j]))
    assert set(out) == set(CITIES) | {"United States"}, out.keys()
    yoy = {k: one((a / b - 1) * 100) for k, (a, b) in out.items()}
    assert yoy == {"Fremont": Decimal("5.2"), "Hayward": Decimal("3.0"), "Milpitas": Decimal("9.5"),
                   "Newark": Decimal("4.7"), "Union City": Decimal("6.3"),
                   "United States": Decimal("2.5")}, yoy
    assert round(out["Fremont"][0]) == 3375 and round(out["United States"][0]) == 1948
    return out, yoy


def build():
    groups = urban()
    levels, yoy = zori()
    print("urban:", [(g, str(a), str(b), s) for g, a, b, s in groups])
    print("zori yoy:", {k: str(v) for k, v in yoy.items()})

    fig = plt.figure(figsize=(14.0, 8.4), dpi=100)
    fig.patch.set_facecolor(CREAM)

    # ---- left: the survey, 2024 to 2025 ----------------------------------
    ax = fig.add_axes([0.215, 0.20, 0.27, 0.54])
    ax.set_facecolor(CREAM)
    style = {"Lower income": (SLATE, 2.6), "All renters": (INK, 2.0),
             "Middle income": (CORAL, 4.0), "Higher income": (PALE, 2.6)}
    for g, a, b, sig in groups:
        col, lw = style[g]
        ls = "-" if sig else (0, (4, 3))
        ax.plot([0, 1], [float(a), float(b)], color=col, lw=lw, ls=ls, zorder=3, solid_capstyle="round")
        ax.scatter([0, 1], [float(a), float(b)], s=70 if g == "Middle income" else 50, color=col, zorder=4)
        bold = g == "Middle income"
        lab = DEEP if bold else INK
        # left labels: group name + 2024 value
        yl = float(a) + (1.0 if g == "All renters" else 0)
        ax.text(-0.06, yl, f"{one(a)}%", ha="right", va="center", fontsize=13,
                fontweight="bold" if bold else "normal", color=lab)
        ax.text(-0.30, yl, g, ha="right", va="center", fontsize=12.5,
                fontweight="bold" if bold else "normal", color=lab)
        d = b - a
        note = f"+{one(d)} pts" + ("" if sig else ", not significant")
        yr = float(b) + (0.9 if g == "Middle income" else 0)
        if g == "All renters":
            yr = float(b) - 1.9
        ax.text(1.06, yr + 0.55, f"{one(b)}%", ha="left", va="center", fontsize=14 if bold else 13,
                fontweight="bold", color=lab)
        ax.text(1.06, yr - 0.95, note, ha="left", va="center", fontsize=10.5,
                color=DEEP if bold else MUTED)
    for x in (0, 1):
        ax.axvline(x, color=GRID, lw=1.0, ls=(0, (2, 3)), zorder=1)
    ax.text(0, 30.6, "2024", ha="center", va="bottom", fontsize=13, fontweight="bold", color=MUTED)
    ax.text(1, 30.6, "2025", ha="center", va="bottom", fontsize=13, fontweight="bold", color=MUTED)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(2.5, 31)
    ax.axis("off")

    fig.text(0.035, 0.835, "Renters who paid late or short in the past 12 months",
             fontsize=13.5, fontweight="bold", color=INK, ha="left", va="bottom")
    fig.text(0.035, 0.815, "Urban Institute survey, renters ages 18 to 64, by income",
             fontsize=11.5, color=MUTED, ha="left", va="top")

    # ---- right: local rents ----------------------------------------------
    bx = fig.add_axes([0.745, 0.20, 0.235, 0.54])
    bx.set_facecolor(CREAM)
    order = sorted(CITIES, key=lambda c: -yoy[c]) + ["United States"]
    for i, c in enumerate(order):
        us = c == "United States"
        v = float(yoy[c])
        bx.barh(i + (0.35 if us else 0), v, height=0.62, color=SLATE if us else CORAL, zorder=3)
        lvl = f"${round(levels[c][0]):,}"
        bx.text(v + 0.15, i + (0.35 if us else 0), f"+{yoy[c]}%", ha="left", va="center",
                fontsize=12.5, fontweight="bold", color=INK if us else DEEP)
        bx.text(-0.25, i + (0.35 if us else 0), "U.S." if us else c, ha="right", va="center",
                fontsize=12.5, color=INK, fontweight="normal")
        bx.text(-0.25, i + (0.35 if us else 0) + 0.33, f"{lvl} a month", ha="right", va="center",
                fontsize=9.8, color=MUTED)
    bx.axvline(0, color=INK, lw=1.0, zorder=4)
    bx.set_xlim(0, 11.5)
    bx.set_ylim(len(order) + 0.0, -0.6)
    bx.axis("off")
    fig.text(0.60, 0.835, "Here, rent is still climbing faster",
             fontsize=13.5, fontweight="bold", color=INK, ha="left", va="bottom")
    fig.text(0.60, 0.815, "Typical rent, August 2026, change from a year earlier",
             fontsize=11.5, color=MUTED, ha="left", va="top")

    fig.text(0.035, 0.955, "The Rent Squeeze Moves Up the Income Ladder",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.905,
             "Only the middle income jump is statistically significant. In all five of our cities, rent rose faster than the nation's.",
             fontsize=13.5, color=MUTED, ha="left", va="top")

    fig.text(
        0.035, 0.085,
        "Dashed lines: change within the survey's margin of error. Income bands are multiples of the federal poverty level, not local incomes: "
        "middle income is\n\\$53,300 to \\$106,600 for a family of three. Survey fielded December 2025. "
        "In the West, the share slipped (16.5% to 15.7%).",
        fontsize=10.4, color=DEEP, ha="left", va="bottom", linespacing=1.55,
    )
    fig.text(0.035, 0.030,
             "Sources: Urban Institute, Well-Being and Basic Needs Survey, \"Renters Increasingly Struggle to Pay for Housing\" (September 2026); "
             "Zillow Observed Rent Index, smoothed, all homes.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"rent-squeeze-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
