#!/usr/bin/env python3
"""
make-rent-vs-buy-zillow-2026-chart.py  DATA_DIR  [outdir]

The 10/29/26 daily's housing chart. Harv attached the newsletter's "Renting Is
the Cheaper Move" graphic: typical U.S. rent $1,932 (26% of income) vs new buyer
payment $3,037 (41% of income), "$1,105 more every month", source Zillow (Oct.
2026), 10% down, 30 year fixed. Emits BOTH:

  rent-vs-buy-102926.png      plain HB monogram    -> RE email + Agent Hub
  rent-vs-buy-102926-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

KEEP IT LOCAL ([[feedback-localize-national-studies]]): the same four Zillow
files carry our two metros, so the local rows come from the SAME publisher,
month and definitions as the national row. No cross vendor mixing.

DATA_DIR (files.zillowstatic.com/research/public_csvs, fetched Oct. 29, 2026):
  Metro_zori_uc_sfrcondomfr_sm_month.csv                      rent (ZORI)
  Metro_total_monthly_payment_downpayment_0.10_..._sm_sa_month.csv   buyer payment
  Metro_new_renter_affordability_uc_sfrcondomfr_sm_sa_month.csv      rent share of income
  Metro_new_homeowner_affordability_downpayment_0.10_..._sm_sa_month.csv  payment share

=============================================================================
VERIFICATION 10/29/26
=============================================================================
* Zillow release, Oct. 15, 2026 ("Rental demand is up 20% as high lending
  costs stifle the for-sale market", zillow.mediaroom.com): "The typical U.S.
  rent was $1,932 a month in September" and the new buyer payment "has risen
  5%, to $3,037", footnoted "with 10% down and a 30-year fixed rate, including
  principal and interest, property taxes and insurance."
* CSVs, September 2026, United States: ZORI 1,931.937, payment 3,037.389,
  renter share 0.262742, owner share 0.413083. Gap 1,105.45. All four of the
  graphic's numbers reproduce exactly.
* Release metro table: San Francisco, CA $3,445 rent / $8,931 payment, San
  Jose, CA $3,812 / $11,845. CSVs give 3,444.848 / 8,931.125 and 3,812.499 /
  11,844.62, so the local rows reproduce the release too.
* Release: rental demand (ZORDI) up 19.2% nationally, "the most in San Jose,
  where ZORDI is up 82.5% from a year ago", then San Francisco (66.9%).
* Zillow's "San Francisco, CA" metro is the San Francisco-Oakland-Fremont area
  (Alameda County included); "San Jose, CA" includes Milpitas.

matplotlib; build with python3.13 on Mac.
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
STAMP = "102926"
MONTH = "2026-09-30"

CREAM = "#fdf6e8"
INK = "#1f2933"
GREEN = "#2f7d4f"
RED = "#c8412f"
GRID = "#d8cdb8"
MUTED = "#8a8172"

FILES = {
    "rent": "Metro_zori_uc_sfrcondomfr_sm_month.csv",
    "pay": "Metro_total_monthly_payment_downpayment_0.10_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
    "rshare": "Metro_new_renter_affordability_uc_sfrcondomfr_sm_sa_month.csv",
    "oshare": "Metro_new_homeowner_affordability_downpayment_0.10_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
}
REGIONS = [("United States", "United States", None),
           ("San Francisco, CA", "San Francisco metro", "incl. Oakland, Fremont, Hayward"),
           ("San Jose, CA", "San Jose metro", "incl. Milpitas")]


def r0(x):
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def load():
    out = {}
    for key, fname in FILES.items():
        rows = list(csv.reader(open(os.path.join(DATA, fname))))
        col = rows[0].index(MONTH)
        assert col == len(rows[0]) - 1, (fname, rows[0][-1])  # September is the newest month
        for row in rows[1:]:
            if row[2] in [r[0] for r in REGIONS]:
                out.setdefault(row[2], {})[key] = float(row[col])
    us, sf, sj = (out[r[0]] for r in REGIONS)
    assert (r0(us["rent"]), r0(us["pay"])) == (1932, 3037), us
    assert r0(us["pay"] - us["rent"]) == 1105
    assert (r0(us["rshare"] * 100), r0(us["oshare"] * 100)) == (26, 41), us
    assert (r0(sf["rent"]), r0(sf["pay"])) == (3445, 8931), sf
    assert (r0(sj["rent"]), r0(sj["pay"])) == (3812, 11845), sj
    return out


def build():
    d = load()
    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.205, 0.13, 0.62, 0.68])
    ax.set_facecolor(CREAM)

    H = 0.36
    centers = [2.2, 1.1, 0.0]
    xmax = 12500
    for (key, name, sub), c in zip(REGIONS, centers):
        v = d[key]
        rent, pay = v["rent"], v["pay"]
        ax.barh(c + H / 2 + 0.02, rent, height=H, color=GREEN, zorder=3)
        ax.barh(c - H / 2 - 0.02, pay, height=H, color=RED, zorder=3)
        ax.text(rent + 140, c + H / 2 + 0.02, f"Rent ${r0(rent):,}  ({r0(v['rshare'] * 100)}% of income)",
                fontsize=13, fontweight="bold", color=GREEN, va="center", ha="left")
        ax.text(pay + 140, c - H / 2 - 0.02, f"Buy ${r0(pay):,}  ({r0(v['oshare'] * 100)}%)",
                fontsize=13, fontweight="bold", color=RED, va="center", ha="left")
        ax.text(-250, c + 0.10, name, fontsize=16, fontweight="bold", color=INK, ha="right", va="center")
        gap = f"Buying costs ${r0(pay - rent):,} more"
        ax.text(-250, c - 0.20, gap, fontsize=12, color=RED, ha="right", va="center")
        if sub:
            ax.text(-250, c - 0.44, sub, fontsize=10.5, color=MUTED, ha="right", va="center")

    ax.set_xlim(0, xmax)
    ax.set_ylim(-0.55, 2.75)
    ticks = [0, 2000, 4000, 6000, 8000, 10000, 12000]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"${t:,}" for t in ticks], fontsize=12, color=MUTED)
    ax.set_yticks([])
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="x", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # rental demand, the release's own local headline. Top right, where the short
    # U.S. bars leave room; at the right edge it collided with the $11,845 label
    fig.text(0.585, 0.80, "Rental demand, year over year", fontsize=12.5, color=MUTED,
             ha="left", va="top")
    for x, num, cap in [(0.585, "+82.5%", "San Jose, the most\nof any metro"),
                        (0.715, "+66.9%", "San Francisco,\nsecond"),
                        (0.845, "+19.2%", "United States")]:
        fig.text(x, 0.765, num, fontsize=23, fontweight="bold", color=INK, ha="left", va="top")
        fig.text(x, 0.705, cap, fontsize=11.5, color=MUTED, ha="left", va="top", linespacing=1.25)

    fig.text(0.035, 0.955, "Renting Is the Cheaper Move, Most of All Here", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895,
             "Typical monthly housing cost, September 2026. Buy = new buyer payment, 10% down, 30 year fixed, with taxes and insurance.",
             fontsize=13.2, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035,
             "Source: Zillow, Oct. 15, 2026 release and research data (ZORI rent, total monthly payment, affordability). Share of income = share of the area's median household income.",
             fontsize=9.8, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"rent-vs-buy-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
