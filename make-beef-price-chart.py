#!/usr/bin/env python3
"""
make-beef-price-chart.py  [outdir] [bls.json]

REALTY EXPERTS recreation of the "Beef Keeps Getting More Expensive" graphic for
the 09/24/26 daily email. OUR OWN branded chart, not the source image.

WHAT CHANGED FROM THE SUPPLIED GRAPHIC, and why (a supplied graphic is a design
brief, never a data source):

  * Its 2021 to 2025 bars ($4.48, $4.85, $5.09, $5.35, $6.12) match NO single
    BLS basis. Not July of each year (4.39, 4.89, 5.10, 5.50, 6.25), not the
    annual average (4.33, 4.81, 5.02, 5.39, 6.09), not August. The bars mixed
    bases, so the chart's five year change was not measured like for like.
  * Its 2026 bar was July, $6.88, labelled "latest month". August 2026 was
    already published at \\$6.923, which is the real record.

OUR BASIS: the SAME month every year, August, the latest month BLS has out.
U.S. city average, series APU0000703112, 100% ground beef, per pound.

THE LOCAL ANSWER, same publisher, same month, same series type: BLS does not
publish a Bay Area or San Francisco metro price for ground beef (APUS49B703112
does not exist), so the West region, APU0400703112, is the closest geography it
offers. Drawn beside the U.S. bar and labelled as a region, not as the Bay Area.

Every value is read from the BLS API response at run time, never hand typed.
Money rounds half up with Decimal.

matplotlib only; build with python3.13 on Mac.
"""
import json
import os
import sys
import urllib.request
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
BLS_JSON = sys.argv[2] if len(sys.argv) > 2 else "/tmp/bls_beef.json"
STAMP = "092426"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
RUST = "#c8692f"
DEEP = "#b8433a"
MUTED = "#8a8172"
GRID = "#d8cdb8"

US = "APU0000703112"
WEST = "APU0400703112"
YEARS = ["2021", "2022", "2023", "2024", "2025", "2026"]
MONTH = "M08"


def load():
    if not os.path.exists(BLS_JSON):
        body = json.dumps({"seriesid": [US, WEST], "startyear": "2020",
                           "endyear": "2026"}).encode()
        req = urllib.request.Request(
            "https://api.bls.gov/publicAPI/v1/timeseries/data/", data=body,
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            open(BLS_JSON, "wb").write(r.read())
    d = json.load(open(BLS_JSON))
    out = {}
    for s in d["Results"]["series"]:
        out[s["seriesID"]] = {r["year"]: Decimal(r["value"]) for r in s["data"]
                              if r["period"] == MONTH}
    for sid in (US, WEST):
        missing = [y for y in YEARS if y not in out.get(sid, {})]
        assert not missing, f"{sid} missing August for {missing}"
    return out


def cents(x):
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def pct(a, b):
    return ((a / b - 1) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def build(data):
    us = [data[US][y] for y in YEARS]
    west = [data[WEST][y] for y in YEARS]
    us_chg = pct(us[-1], us[0])
    west_chg = pct(west[-1], west[0])

    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    fig.text(0.062, 0.925, "Beef Keeps Getting More Expensive",
             fontsize=30, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.062, 0.858,
             f"Average retail price per pound of 100% ground beef, every August. "
             f"U.S. up {us_chg}% since 2021 to a record ${cents(us[-1])}",
             fontsize=14.5, color=MUTED, ha="left", va="top")

    ax = fig.add_axes((0.062, 0.215, 0.876, 0.53))
    ax.set_facecolor(CREAM)
    w = 0.36
    xs = list(range(len(YEARS)))
    for i, (u, wv) in enumerate(zip(us, west)):
        ax.bar(i - w / 2, float(u), width=w, color=RUST, zorder=3)
        ax.bar(i + w / 2, float(wv), width=w, color=CORAL, zorder=3)
        ax.text(i - w / 2, float(u) + 0.1, f"${cents(u)}", ha="center",
                va="bottom", fontsize=13, fontweight="bold", color=RUST)
        ax.text(i + w / 2, float(wv) + 0.1, f"${cents(wv)}", ha="center",
                va="bottom", fontsize=13, fontweight="bold", color=DEEP)
    ax.set_xticks(xs)
    ax.set_xticklabels(YEARS, fontsize=15, fontweight="bold", color=INK)
    ax.tick_params(axis="x", length=0, pad=10)
    ax.set_yticks([])
    ax.set_ylim(0, 8.6)
    ax.set_xlim(-0.6, len(YEARS) - 0.4)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)

    # legend as plain text chips, top left inside the plot area
    fig.patches.append(plt.Rectangle((0.075, 0.742), 0.014, 0.024, color=RUST,
                                     transform=fig.transFigure, figure=fig))
    fig.text(0.094, 0.754, f"U.S. city average, up {us_chg}%", fontsize=12.5,
             fontweight="bold", color=INK, va="center")
    fig.patches.append(plt.Rectangle((0.325, 0.742), 0.014, 0.024, color=CORAL,
                                     transform=fig.transFigure, figure=fig))
    fig.text(0.344, 0.754, f"West region, up {west_chg}%", fontsize=12.5,
             fontweight="bold", color=INK, va="center")

    fig.text(0.062, 0.128,
             "The West is the closest geography BLS publishes for this item; it "
             "does not release a Bay Area or San Francisco price for ground beef.",
             fontsize=11.5, color=MUTED, ha="left", va="top")
    fig.text(0.062, 0.045,
             "Source: Bureau of Labor Statistics average price data, series "
             "APU0000703112 and APU0400703112, August of each year.",
             fontsize=10.5, color=MUTED, ha="left", va="bottom")
    return fig, us, west, us_chg, west_chg


if __name__ == "__main__":
    data = load()
    fig, us, west, uc, wc = build(data)
    for y, u, w in zip(YEARS, us, west):
        print(f"  Aug {y}: U.S. ${cents(u)}  West ${cents(w)}")
    print(f"  five year change: U.S. +{uc}%  West +{wc}%")
    out = os.path.join(OUTDIR, f"beef-price-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
