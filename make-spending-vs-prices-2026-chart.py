#!/usr/bin/env python3
"""
make-spending-vs-prices-2026-chart.py  DATA_DIR  [outdir]

The 10/17/26 (Saturday) daily's Economy chart. Harv supplied the week's headlines
on September retail sales (DPA/Yahoo "far exceed expectations", Reuters "beat
expectations ... on higher gasoline prices", Investopedia "Americans keep
shopping as they shrug off higher prices", AP "up 0.8% ... but a big chunk of
spending went to paying gasoline bills") and a YouTube explainer whose panel says
"Higher spending doesn't always mean buying more." This chart tests that idea
store type by store type: sales growth (Census) next to the price growth of what
those stores sell (BLS). Where sales outgrew prices, people bought more. Emits BOTH:

  spending-vs-prices-101726.png      plain HB monogram    -> RE email + Agent Hub
  spending-vs-prices-101726-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds marts.txt (pdftotext -layout of census.gov/retail/marts/www/
marts_current.pdf, the Advance Monthly Retail release CB26-165, Oct. 15, 2026)
and bls.json (BLS API v1, CPI-U NSA), both fetched Oct. 17, 2026.

=============================================================================
VERIFICATION 10/17/26
=============================================================================
* Census Table 2, September 2026 from September 2025 (seasonally adjusted, not
  price adjusted): total retail and food services +6.3, food services and
  drinking places +7.0, grocery stores +0.9, gasoline stations +28.1. Month
  over month the total rose 0.8% (AP's headline), only 0.2% excluding gasoline
  stations.
* CPI-U September 2026 from September 2025: all items +3.74, food away from
  home +3.46, food at home +1.81, gasoline +34.17.
* The pairing is store type vs the main thing it sells (gas stations also sell
  snacks, grocery stores sell more than food), so read it as direction, not
  decimals. The footer says so.

matplotlib; build with python3.13 on Mac.
"""
import json
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
STAMP = "101726"

CREAM = "#fdf6e8"
INK = "#1f2933"
BLUE = "#2b6cb0"
CORAL = "#d6363c"
GREEN = "#2f7d4f"
GRID = "#d8cdb8"
MUTED = "#8a8172"

# label, Census Table 2 row pattern, CPI series, price label
ROWS = [
    ("All stores and restaurants", r"total \…", "CUUR0000SA0", "all consumer prices"),
    ("Restaurants and bars", r"Food services & drinking places", "CUUR0000SEFV", "restaurant menu prices"),
    ("Grocery stores", r"Grocery stores", "CUUR0000SAF11", "grocery prices"),
    ("Gas stations", r"Gasoline stations", "CUUR0000SETB01", "gasoline prices"),
]
EXPECT_SALES = [6.3, 7.0, 0.9, 28.1]
EXPECT_PRICE = [3.7, 3.5, 1.8, 34.2]


def census():
    txt = open(os.path.join(DATA, "marts.txt")).read()
    t2 = txt[txt.index("Table 2."):txt.index("Table 3.")]
    out = []
    for _, pat, _, _ in ROWS:
        line = next(l for l in t2.splitlines() if re.search(pat, l))
        nums = re.findall(r"-?\d+\.\d", line)
        out.append(float(nums[1]))      # Sep. 2026 from Sep. 2025
    assert out == EXPECT_SALES, out
    return out


def cpi():
    ser = {}
    for s in json.load(open(os.path.join(DATA, "bls.json")))["Results"]["series"]:
        obs = {(o["year"], o["period"]): o["value"] for o in s["data"]}
        if ("2026", "M09") in obs:
            ser[s["seriesID"]] = (Decimal(obs[("2026", "M09")]), Decimal(obs[("2025", "M09")]))
    out = []
    for _, _, sid, _ in ROWS:
        now, ago = ser[sid]
        out.append(float(((now / ago - 1) * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)))
    assert out == EXPECT_PRICE, out
    return out


def build():
    sales, prices = census(), cpi()
    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.25, 0.17, 0.70, 0.60])
    ax.set_facecolor(CREAM)

    H = 0.34
    n = len(ROWS)
    for i, (label, _, _, plabel) in enumerate(ROWS):
        yc = n - 1 - i
        ys, yp = yc + H / 2 + 0.02, yc - H / 2 - 0.02
        ax.barh(ys, sales[i], height=H, color=BLUE, zorder=3)
        ax.barh(yp, prices[i], height=H, color=CORAL, alpha=0.85, zorder=3)
        ax.text(sales[i] + 0.4, ys, f"sales +{sales[i]:.1f}%", va="center", ha="left",
                fontsize=13.5, fontweight="bold", color=BLUE)
        ax.text(prices[i] + 0.4, yp, f"{plabel} +{prices[i]:.1f}%", va="center", ha="left",
                fontsize=12.5, color=CORAL)
        ax.text(-0.015, yc + 0.13, label, va="center", ha="right", fontsize=15,
                fontweight="bold", color=INK, transform=ax.get_yaxis_transform())
        more = sales[i] > prices[i]
        ax.text(-0.015, yc - 0.17, "buying more" if more else "paying more, buying a bit less",
                transform=ax.get_yaxis_transform(), va="center", ha="right", fontsize=12.5,
                fontstyle="italic", color=GREEN if more else MUTED)

    ax.set_xlim(0, 46)
    ax.set_ylim(-0.6, n - 0.4)
    ax.set_xticks([0, 10, 20, 30, 40])
    ax.set_xticklabels(["0%", "10%", "20%", "30%", "40%"], fontsize=12, color=MUTED)
    ax.set_yticks([])
    ax.tick_params(axis="x", length=0, pad=8)
    ax.grid(axis="x", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.035, 0.955, "Where Spending Beat Prices, and Where It Didn't", fontsize=25,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895, "September 2026 vs. a year earlier: sales by store type next to the "
             "prices of what those stores sell.", fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.25, 0.815, "When sales grow faster than prices, shoppers are buying more, "
             "not just paying more.", fontsize=12.5, color=INK, ha="left", va="center")
    fig.text(0.035, 0.055, "Source: U.S. Census Bureau, Advance Monthly Retail Sales, Oct. 15, 2026 "
             "(seasonally adjusted, not adjusted for prices); U.S. Bureau of Labor Statistics, CPI-U.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    fig.text(0.035, 0.025, "Store sales are matched to the main item each store type sells, so "
             "read the pairs as direction rather than an exact volume measure.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"spending-vs-prices-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
