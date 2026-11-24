#!/usr/bin/env python3
"""
make-real-estate-by-generation-chart.py  DFA_GENERATION_LEVELS_CSV  [outdir]

The 11/24/26 daily's Real Estate chart. Harv supplied a "Who Owns America's Real
Estate?" graphic (Federal Reserve Distributional Financial Accounts via NAHB,
Q4 2025: Silent $4.1T 9%, Boomers $19.4T 40%, Gen X $14.3T 30%, Millennials and
Gen Z $10.2T 21%). A supplied graphic is a design brief, not a data source:

  * The Fed's current release (last update Sept. 18, 2026) runs through Q2 2026,
    so Q4 2025 is a superseded period. This chart uses Q2 2026.
  * In the current vintage Q4 2025 reads Boomers $19.34T and Gen X $14.25T, so
    the graphic's $19.4T / $14.3T came from an earlier vintage.
  * The Fed's "Millennial" group is everyone born 1981 or later, which is why
    the graphic said "Millennials and Gen Z".
  * "Real estate" in the DFA = owner-occupied real estate (incl. vacant land and
    mobile homes) at market value. Rentals households own sit in
    "Unincorporated businesses", not here.

Input: dfa-generation-levels.csv from
https://www.federalreserve.gov/releases/z1/dataviz/download/zips/dfa.zip
(values in millions of dollars).

Emits BOTH:
  real-estate-by-generation-112426.png      plain HB monogram    -> RE email + Agent Hub
  real-estate-by-generation-112426-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app
"""
import csv
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

SRC = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "112426"
Q = "2026:Q2"

CREAM = "#fdf6e8"
INK = "#1f2933"
GRID = "#e6dcc8"
MUTED = "#8a8172"
CORAL = "#e2574c"
TEAL = "#2a8c82"

ORDER = [("Silent", "Silent", "Born before 1946"), ("BabyBoom", "Boomers", "Born 1946 to 1964"),
         ("GenX", "Gen X", "Born 1965 to 1980"), ("Millennial", "Millennials\nand younger", "Born 1981 or later")]
# The claim the copy makes, asserted at printed precision.
EXPECT = {"Silent": ("3.8", "7.6"), "BabyBoom": ("20.5", "41.3"), "GenX": ("14.3", "28.7"), "Millennial": ("11.2", "22.4")}
EXPECT_2019Q4_MILL = "11.5"


def r1(x):
    return Decimal(str(x)).quantize(Decimal("0.1"), ROUND_HALF_UP)


def quarter(rows, q):
    v = {r["Category"]: Decimal(r["Real estate"]) for r in rows if r["Date"] == q}
    assert set(v) == {k for k, _, _ in ORDER}, (q, v)
    return v


def build():
    rows = list(csv.DictReader(open(SRC)))
    latest = max(r["Date"] for r in rows)
    assert latest == Q, latest
    v = quarter(rows, Q)
    tot = sum(v.values())
    sh = {k: v[k] / tot * 100 for k in v}
    for k, (t, s) in EXPECT.items():
        assert str(r1(v[k] / Decimal(1e6))) == t and str(r1(sh[k])) == s, (k, v[k], sh[k])
    old = quarter(rows, "2019:Q4")
    assert str(r1(old["Millennial"] / sum(old.values()) * 100)) == EXPECT_2019Q4_MILL

    fig = plt.figure(figsize=(14.0, 7.9), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.085, 0.2, 0.62, 0.6])
    ax.set_facecolor(CREAM)
    for i, (k, name, born) in enumerate(ORDER):
        col = CORAL if k == "BabyBoom" else TEAL
        tv = float(v[k]) / 1e6
        ax.bar(i, tv, width=0.62, color=col, zorder=3)
        ax.text(i, tv + 0.45, f"${r1(tv)}T", ha="center", va="bottom", fontsize=19, fontweight="bold", color=INK)
        ax.text(i, tv - 0.6, f"{r1(sh[k])}%", ha="center", va="top", fontsize=16, fontweight="bold", color=CREAM)
        ax.text(i, -1.0, name, ha="center", va="top", fontsize=14.5, fontweight="bold", color=INK, linespacing=1.15)
        ax.text(i, -3.75, born, ha="center", va="top", fontsize=11.5, color=MUTED)
    ax.set_xlim(-0.55, 3.55)
    ax.set_ylim(0, 23.5)
    ax.set_xticks([])
    ax.set_yticks([0, 5, 10, 15, 20])
    ax.set_yticklabels(["$0", "$5T", "$10T", "$15T", "$20T"], fontsize=12, color=MUTED)
    ax.tick_params(length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.745, 0.73, f"{r1(sh['BabyBoom'])}%", fontsize=46, fontweight="bold", color=CORAL, ha="left", va="center")
    fig.text(0.75, 0.635, "of household real estate\nbelongs to Boomers", fontsize=14.5, color=INK, ha="left",
             va="top", linespacing=1.4)
    fig.text(0.75, 0.50, f"Total: ${r1(tot / Decimal(1e6))} trillion", fontsize=13.5, color=INK, ha="left", va="top")
    fig.text(0.75, 0.42, f"Millennials and younger hold\n{r1(sh['Millennial'])}%, up from "
             f"{EXPECT_2019Q4_MILL}% at the\nend of 2019", fontsize=13.5, color=MUTED, ha="left", va="top",
             linespacing=1.4)

    fig.text(0.035, 0.955, "Who Owns America's Real Estate", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.897, "Owner-occupied real estate held by households, at market value, by generation of the "
             "household head, Q2 2026", fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.022, "Federal Reserve Distributional Financial Accounts, Q2 2026 (latest release, Sept. 18, 2026). "
             "Rental property households own is not included.\nSource: Federal Reserve Board.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.45)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"real-estate-by-generation-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    print("wrote", out)
