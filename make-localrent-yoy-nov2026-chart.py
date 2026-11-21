#!/usr/bin/env python3
"""
make-localrent-yoy-nov2026-chart.py  ZORI_DIR  [outdir]

The 11/21/26 daily's Real Estate chart. Harv forwarded realtor.com's Nov. 19
"Weekly Housing Trends" (October 2026 Rental Report: median asking rent for 0 to
2 bedroom units in the 50 largest metros $1,692, up 0.1% from a year ago, the
first annual increase since June 2023). This gives the LOCAL answer.

⚠️ Realtor.com's number and these bars are DIFFERENT SERIES (0 to 2 bedroom
units in the 50 largest metros vs Zillow's ZORI, all home types). Realtor.com is
quoted in the copy and never plotted. Every bar here, the U.S. reference bar
included, is ZORI, so the comparison inside the chart is on one basis.
See memory reference-zori-local-rent-source.

ZORI_DIR holds the public CSVs pulled from files.zillowstatic.com on 11/21/26:
  city.csv   City_zori_uc_sfrcondomfr_sm_month.csv  (month values from column 8)
  metro.csv  Metro_zori_uc_sfrcondomfr_sm_month.csv (United States row; from column 5)
Newest month: October 2026 (column 2026-10-31), compared with 2025-10-31.

Values generated on 11/21/26 (asserted below):
  Milpitas   $3,628  +9.4%     Union City $2,819  +7.1%
  Fremont    $3,309  +6.8%     Newark     $3,554  +5.5%
  Hayward    $2,670  +3.9%     U.S.       $1,913  +2.9%

Emits BOTH:
  localrent-yoy-112126.png      plain HB monogram    -> RE email + Agent Hub
  localrent-yoy-112126-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

matplotlib only; build with python3.13 on Mac, run from the workspace.
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

ZD = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "112126"
NOW, THEN = "2026-10-31", "2025-10-31"
CITIES = ["Fremont", "Hayward", "Milpitas", "Newark", "Union City"]

CREAM = "#fdf6e8"
INK = "#1f2933"
GRID = "#e6dcc8"
MUTED = "#8a8172"
ORANGE = "#ea580c"
SLATE = "#4f6d8a"


def q(x, p="0.1"):
    return Decimal(str(x)).quantize(Decimal(p), ROUND_HALF_UP)


def load():
    c = list(csv.reader(open(os.path.join(ZD, "city.csv"), newline="")))
    m = list(csv.reader(open(os.path.join(ZD, "metro.csv"), newline="")))
    ci, ti = c[0].index(NOW), c[0].index(THEN)
    mi, mti = m[0].index(NOW), m[0].index(THEN)
    assert c[0][-1] == NOW and m[0][-1] == NOW, (c[0][-1], m[0][-1])
    out = {}
    for r in c[1:]:
        if r[5] == "CA" and r[2] in CITIES:
            assert r[2] not in out, r[2]
            out[r[2]] = (float(r[ci]), float(r[ti]))
    us = [r for r in m[1:] if r[2] == "United States"]
    assert len(us) == 1
    out["United States"] = (float(us[0][mi]), float(us[0][mti]))
    assert set(out) == set(CITIES) | {"United States"}, out.keys()
    rows = [(k, v[0], float(q((v[0] / v[1] - 1) * 100))) for k, v in out.items()]
    chk = {k: (int(q(a, "1")), y) for k, a, y in rows}
    assert chk == {"Milpitas": (3628, 9.4), "Union City": (2819, 7.1), "Fremont": (3309, 6.8), "Newark": (3554, 5.5),
                   "Hayward": (2670, 3.9), "United States": (1913, 2.9)}, chk
    return sorted(rows, key=lambda r: (r[0] == "United States", -r[2]))


def build():
    rows = load()
    fig = plt.figure(figsize=(14.0, 7.9), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.20, 0.15, 0.55, 0.62])
    ax.set_facecolor(CREAM)
    n = len(rows)
    for i, (name, rent, yoy) in enumerate(rows):
        y = n - 1 - i - (0.35 if name == "United States" else 0)
        us = name == "United States"
        ax.barh(y, yoy, height=0.6, color=SLATE if us else ORANGE, zorder=3)
        ax.text(yoy + 0.15, y, f"+{yoy:.1f}%", va="center", ha="left", fontsize=16, fontweight="bold",
                color=SLATE if us else ORANGE)
        ax.text(-0.03, y, "United States" if us else name, transform=ax.get_yaxis_transform(), ha="right", va="center",
                fontsize=16, fontweight="bold", color=INK)
        ax.text(1.06, y, f"\\${rent:,.0f}", transform=ax.get_yaxis_transform(), ha="center", va="center",
                fontsize=16, color=INK, fontweight="bold" if not us else "normal")
    ax.text(1.06, n - 0.35, "Typical rent,\nOctober 2026", transform=ax.get_yaxis_transform(), ha="center",
            va="bottom", fontsize=12, color=MUTED, linespacing=1.25)
    ax.axhline(0.5 - 0.35 + 0.0, color=GRID, lw=1.2, zorder=1)
    for x in (2, 4, 6, 8, 10):
        ax.axvline(x, color=GRID, lw=0.9, zorder=1)
        ax.text(x, -1.05, f"+{x}%", ha="center", va="top", fontsize=11.5, color=MUTED)
    ax.axvline(0, color=INK, lw=1.4, zorder=4)
    ax.set_xlim(0, 11.2)
    ax.set_ylim(-0.9, n - 0.4)
    ax.axis("off")

    fig.text(0.035, 0.955, "Rents Are Rising Faster Here", fontsize=26, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.897, "Change in typical asking rent, October 2025 to October 2026, all home types", fontsize=13.5,
             color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.862, "Every one of our five cities is up more than the national 2.9%", fontsize=13.5, color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.022, "Source: Zillow Observed Rent Index (ZORI), smoothed, all home types, October 2026. Realtor.com's "
             "+0.1% for October measures 0 to 2 bedroom\nunits in the 50 largest metros, a different series, so it is "
             "not shown here.", fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.45)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"localrent-yoy-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    print("wrote", out)
