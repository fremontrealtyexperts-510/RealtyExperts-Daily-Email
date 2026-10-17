#!/usr/bin/env python3
"""
make-cost-of-200-2026-chart.py  DATA_DIR  [outdir]

The 10/17/26 (Saturday) daily's Real Estate chart. Harv supplied screenshots of a
YouTube explainer ("Americans Are Spending More Money", ClearValue Tax, 10/16/26)
showing a grocery cart that went from "$200" to "$220, 10% higher price", and a
"+$4,000 more per year for a typical household" panel. Those are illustrations,
not data. This chart puts the real September 2026 numbers on the same idea:
what $200 of last September's spending costs now, nationally and in the Bay Area.
Emits BOTH:

  cost-of-200-101726.png      plain HB monogram    -> RE email + Agent Hub
  cost-of-200-101726-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds bls.json and bls2.json, BLS public API v1 pulls (CPI-U, not
seasonally adjusted, 2025 to 2026), fetched Oct. 17, 2026 about 11:30 AM PT.

=============================================================================
VERIFICATION 10/17/26
=============================================================================
* U.S. September 2026 vs September 2025: all items +3.74% (CUUR0000SA0
  336.940 / 324.800), groceries +1.81% (SAF11), restaurant meals +3.46% (SEFV),
  rent +2.78% (SEHA), electricity +4.37% (SEHF01), gasoline +34.17% (SETB01),
  motor vehicle insurance -4.98% (SETE).
* Bay Area (San Francisco, Oakland and Hayward area, S49B), September, the
  series BLS publishes monthly there: groceries +4.38%, rent +2.65%, gasoline
  +31.50%. Its all items index is bimonthly (August +3.39%, U.S. August +3.40%),
  so it is not drawn.
* The video's cart (+10%) is about five times the national grocery number.
  Its insurance arrow points up; car insurance prices are DOWN 5% on the year.

matplotlib; build with python3.13 on Mac.
"""
import json
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
STAMP = "101726"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#d6363c"
GREEN = "#2f7d4f"
BLUE = "#2b6cb0"
SLATE = "#7a8aa0"
GOLD = "#b8862b"
GRID = "#d8cdb8"
MUTED = "#8a8172"

ROWS = [  # label, U.S. series, Bay Area series or None
    ("Car insurance", "CUUR0000SETE", None),
    ("Groceries", "CUUR0000SAF11", "CUURS49BSAF11"),
    ("Rent", "CUUR0000SEHA", "CUURS49BSEHA"),
    ("Restaurant meals", "CUUR0000SEFV", None),
    ("Everything (all items)", "CUUR0000SA0", None),
    ("Electricity", "CUUR0000SEHF01", None),
    ("Gasoline", "CUUR0000SETB01", "CUURS49BSETB01"),
]
EXPECT = {"CUUR0000SETE": -4.98, "CUUR0000SAF11": 1.81, "CUUR0000SEHA": 2.78,
          "CUUR0000SEFV": 3.46, "CUUR0000SA0": 3.74, "CUUR0000SEHF01": 4.37,
          "CUUR0000SETB01": 34.17, "CUURS49BSAF11": 4.38, "CUURS49BSEHA": 2.65,
          "CUURS49BSETB01": 31.50}


def q2(x):
    return Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def load():
    ser = {}
    for f in ("bls.json", "bls2.json"):
        for s in json.load(open(os.path.join(DATA, f)))["Results"]["series"]:
            obs = {(o["year"], o["period"]): o["value"] for o in s["data"]}
            if ("2026", "M09") in obs and ("2025", "M09") in obs:
                ser[s["seriesID"]] = (Decimal(obs[("2026", "M09")]), Decimal(obs[("2025", "M09")]))
    out = {}
    for sid, exp in EXPECT.items():
        now, ago = ser[sid]
        pct = q2((now / ago - 1) * 100)
        assert float(pct) == exp, (sid, pct, exp)
        out[sid] = (pct, q2(Decimal(200) * now / ago))
    return out


def build():
    v = load()
    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.225, 0.15, 0.715, 0.66])
    ax.set_facecolor(CREAM)

    n = len(ROWS)
    for i, (label, us, bay) in enumerate(ROWS):
        y = n - 1 - i
        pct, dol = v[us]
        col = GREEN if dol < 200 else (CORAL if label == "Gasoline" else SLATE)
        ax.barh(y, float(dol) - 200, left=200, height=0.56, color=col, zorder=3)
        sign = "+" if pct > 0 else "−"
        txt = f"${dol:,.2f}  ({sign}{abs(pct):.1f}%)"
        if dol < 200:
            ax.text(float(dol) - 1.0, y, txt, va="center", ha="right", fontsize=13.5,
                    fontweight="bold", color=GREEN)
        else:
            ax.text(float(dol) + 1.0, y, txt, va="center", ha="left", fontsize=13.5,
                    fontweight="bold", color=CORAL if label == "Gasoline" else INK)
        ax.text(-0.012, y, label, va="center", ha="right", fontsize=14.5, fontweight="bold",
                color=INK, transform=ax.get_yaxis_transform())
        if bay:
            bpct, bdol = v[bay]
            ax.scatter([float(bdol)], [y - 0.42], marker="D", s=70, color=GOLD,
                       edgecolor=CREAM, linewidth=1.2, zorder=5)
            far = bdol > 250   # keep the gasoline label off the right edge
            ax.text(float(bdol) + (-1.2 if far else 1.2), y - 0.42,
                    f"Bay Area ${bdol:,.2f} (+{bpct:.1f}%)", va="center",
                    ha="right" if far else "left", fontsize=11.5, color=GOLD, fontweight="bold")

    ax.axvline(200, color=INK, lw=1.4, zorder=4)
    ax.text(201.0, n - 0.32, "$200 a year ago", ha="left", va="bottom", fontsize=12,
            color=INK)
    ax.set_xlim(165, 285)
    ax.set_ylim(-0.95, n - 0.15)
    ax.set_xticks([180, 200, 220, 240, 260, 280])
    ax.set_xticklabels(["$180", "$200", "$220", "$240", "$260", "$280"], fontsize=12,
                       color=MUTED)
    ax.set_yticks([])
    ax.tick_params(axis="x", length=0, pad=8)
    ax.grid(axis="x", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.035, 0.955, "What $200 of Last September's Spending Costs Now", fontsize=25,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895, "Same items, priced in September 2026 vs. September 2025. Bars are "
             "the U.S.; gold diamonds are the Bay Area where BLS reports it monthly.",
             fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035, "Source: U.S. Bureau of Labor Statistics, Consumer Price Index "
             "(CPI-U, not seasonally adjusted), September 2026. Bay Area = San Francisco, "
             "Oakland and Hayward area.", fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"cost-of-200-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
