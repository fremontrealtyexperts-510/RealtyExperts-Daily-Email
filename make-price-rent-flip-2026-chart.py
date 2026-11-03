#!/usr/bin/env python3
"""
make-price-rent-flip-2026-chart.py  DATA_DIR  [outdir]

The 11/03/26 daily's Real Estate chart, ADDED under the keep it local rule. The
national story (Redfin: the typical U.S. home sold for 0.1% less than a year
earlier, the first annual decline in three years; Apartment List: national rent
0.1% above a year ago, the first annual rise in three years) has been true in our
five cities for a while, and by a wider margin. Emits BOTH:

  price-rent-flip-110326.png      plain HB monogram    -> RE email + Agent Hub
  price-rent-flip-110326-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds Zillow's public research CSVs, fetched Nov. 3, 2026:
  City_zori.csv   zori/City_zori_uc_sfrcondomfr_sm_month.csv
  Metro_zori.csv  zori/Metro_zori_uc_sfrcondomfr_sm_month.csv
  City_zhvi.csv   zhvi/City_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv
  Metro_zhvi.csv  zhvi/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv

=============================================================================
VERIFICATION 11/03/26
=============================================================================
* One publisher on both sides (Zillow rent index and Zillow home value index), and
  its own U.S. row, so local and national compare like with like. Apartment List
  and Redfin are quoted in the copy only, never plotted against these.
* Newest month in all four files is 2026-09-30; October publishes mid November.
* Year over year, September 2026: rents rose in all five cities (3.9% to 10.1%)
  and typical values fell in all five (1.2% to 2.4%). U.S.: rent +2.7%, value
  +1.2%. The title's "all five" is asserted below.
* City rows matched on RegionName with State == "CA"; month values start at
  column 8 in the city files and column 5 in the metro files.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
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

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "110326"
MONTH = "2026-09-30"
YAGO = "2025-09-30"

CREAM = "#fdf6e8"
INK = "#1f2933"
GREEN = "#16a34a"
CORAL = "#e2725b"
GRID = "#d8cdb8"
MUTED = "#8a8172"

CITIES = ["Fremont", "Hayward", "Milpitas", "Newark", "Union City"]


def r1(x):
    return float(Decimal(str(round(x, 6))).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def series(fn, first, pick):
    with open(os.path.join(DATA, fn)) as f:
        rd = csv.reader(f)
        head = next(rd)
        assert head[-1] == MONTH, (fn, head[-1])
        i_now, i_ago = head.index(MONTH), head.index(YAGO)
        assert i_now >= first and i_ago >= first
        out = {}
        for row in rd:
            key = pick(row)
            if key:
                out[key] = (float(row[i_now]), float(row[i_ago]))
        return out


def load():
    city = lambda r: r[2] if r[5] == "CA" and r[2] in CITIES else None
    us = lambda r: "U.S." if r[2] == "United States" else None
    rent = {**series("City_zori.csv", 8, city), **series("Metro_zori.csv", 5, us)}
    value = {**series("City_zhvi.csv", 8, city), **series("Metro_zhvi.csv", 5, us)}
    rows = []
    for name in CITIES + ["U.S."]:
        (rn, ra), (vn, va) = rent[name], value[name]
        rows.append((name, rn, r1(100 * (rn / ra - 1)), vn, r1(100 * (vn / va - 1))))
    local = [r for r in rows if r[0] != "U.S."]
    assert all(r[2] > 0 for r in local) and all(r[4] < 0 for r in local), local
    got = {r[0]: (r[2], r[4]) for r in rows}
    assert got == {"Fremont": (6.0, -1.5), "Hayward": (3.9, -2.4), "Milpitas": (10.1, -1.2),
                   "Newark": (4.7, -2.4), "Union City": (7.8, -1.9), "U.S.": (2.7, 1.2)}, got
    return rows


def money_k(v):
    return f"\\${v / 1e6:.2f}M" if v >= 1e6 else f"\\${v / 1e3:.0f}K"


def pct(v):
    return f"{'+' if v > 0 else '−'}{abs(v):.1f}%"


def build():
    rows = load()
    fig = plt.figure(figsize=(14.0, 8.6), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.255, 0.10, 0.70, 0.70])
    ax.set_facecolor(CREAM)

    ys = [6.4, 5.4, 4.4, 3.4, 2.4, 0.9]
    H = 0.34
    for y, (name, rn, rp, vn, vp) in zip(ys, rows):
        ax.barh(y + 0.19, rp, height=H, color=GREEN, zorder=3)
        ax.barh(y - 0.19, vp, height=H, color=CORAL, zorder=3)
        ax.text(rp + 0.18, y + 0.19, pct(rp), fontsize=15, fontweight="bold", color=GREEN,
                ha="left", va="center", zorder=4)
        if vp < 0:
            ax.text(vp - 0.18, y - 0.19, pct(vp), fontsize=15, fontweight="bold", color=CORAL,
                    ha="right", va="center", zorder=4)
        else:
            ax.text(vp + 0.18, y - 0.19, pct(vp), fontsize=15, fontweight="bold", color=CORAL,
                    ha="left", va="center", zorder=4)
        label = "United States" if name == "U.S." else name
        ax.text(-4.35, y + 0.13, label, fontsize=17, fontweight="bold", color=INK, ha="right", va="center")
        ax.text(-4.35, y - 0.25, f"rent \\${rn:,.0f} · value {money_k(vn)}", fontsize=11.5, color=MUTED,
                ha="right", va="center")

    ax.axhline(1.65, xmin=0.0, xmax=1.0, color=GRID, lw=1.0, zorder=1)
    ax.axvline(0, color=INK, lw=1.2, zorder=2)
    ax.set_ylim(0.3, 7.0)
    ax.set_xlim(-4.2, 12.2)
    ticks = [-2, 0, 2, 4, 6, 8, 10, 12]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{'+' if t > 0 else '\u2212'}{abs(t)}%" if t else "0%" for t in ticks], fontsize=12,
                       color=MUTED)
    ax.set_yticks([])
    ax.tick_params(axis="x", length=0, pad=8)
    ax.grid(axis="x", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # legend chips under the subtitle
    fig.patches.extend([
        plt.Rectangle((0.035, 0.833), 0.016, 0.022, transform=fig.transFigure, color=GREEN, figure=fig),
        plt.Rectangle((0.185, 0.833), 0.016, 0.022, transform=fig.transFigure, color=CORAL, figure=fig),
    ])
    fig.text(0.057, 0.844, "Typical rent", fontsize=13.5, color=INK, ha="left", va="center")
    fig.text(0.207, 0.844, "Typical home value", fontsize=13.5, color=INK, ha="left", va="center")

    fig.text(0.035, 0.96, "Rents Up, Home Values Down in All Five of Our Cities", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.905, "Change from a year earlier, September 2026. Nationally, both are still rising.",
             fontsize=14, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.03, "Source: Zillow Observed Rent Index (all homes, smoothed) and Zillow Home Value Index "
                          "(middle tier, smoothed, seasonally adjusted), September 2026, the latest month.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"price-rent-flip-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
