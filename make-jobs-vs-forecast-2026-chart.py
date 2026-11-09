"""
make-jobs-vs-forecast-2026-chart.py  DATA_DIR  [outdir]

The 11/09/26 daily's Economy chart. Harv supplied a newsletter graphic ("October
Hiring Crushed Forecasts": Aug +186K, Sep +60K, Oct +165K against a +59K forecast,
Source BLS, forecast via Dow Jones). Recreated as OUR chart from the Bureau of Labor
Statistics series itself, never from the graphic.

Emits BOTH:
  jobs-vs-forecast-110926.png      plain HB monogram    -> RE email + Agent Hub
  jobs-vs-forecast-110926-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR/payroll.json is the raw BLS Public Data API v1 response
(api.bls.gov/publicAPI/v1/timeseries/data/CES0000000001, keyless) pulled 11/09/26:
total nonfarm employment, thousands, seasonally adjusted.

=============================================================================
VERIFICATION 11/09/26
=============================================================================
* Monthly change = this month's level minus last month's.
* August +186K, September +60K, October +165K: all three match the supplied
  graphic and the BLS release (asserted below). September and October are
  preliminary (BLS footnote P) and will be revised.
* Forecast 59,000: "economists surveyed by Dow Jones", per CNBC's 11/06/26 jobs
  story. LSEG's poll was 65,000 (Fox Business). The graphic's 59K is the Dow
  Jones figure, so it stands as labeled.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
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
STAMP = "110926"
FORECAST = 59

CREAM = "#fdf6e8"
INK = "#1f2933"
GREEN = "#2e8b57"
SAND = "#c9b48f"
GRID = "#e6dcc8"
MUTED = "#8a8172"
AXIS = "#8a7f6a"
ORANGE = "#ea580c"


def load():
    d = json.load(open(os.path.join(DATA, "payroll.json")))
    assert d["status"] == "REQUEST_SUCCEEDED", d["status"]
    s = d["Results"]["series"][0]
    assert s["seriesID"] == "CES0000000001", s["seriesID"]
    lv = {(int(r["year"]), int(r["period"][1:])): float(r["value"]) for r in s["data"] if r["period"] != "M13"}
    ch = {m: round(lv[(2026, m)] - lv[(2026, m - 1)]) for m in (8, 9, 10)}
    assert ch == {8: 186, 9: 60, 10: 165}, ch
    return [("August", ch[8]), ("September", ch[9]), ("October", ch[10])]


def bar(ax, x, h, color, w=0.62):
    ax.bar(x, h, width=w, color=color, zorder=3, lw=0)


def build():
    data = load()
    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.06, 0.17, 0.88, 0.60])
    ax.set_facecolor(CREAM)

    for i, (name, v) in enumerate(data):
        last = i == len(data) - 1
        bar(ax, i, v, GREEN if last else SAND)
        ax.text(i, v + 6, f"+{v}K", ha="center", va="bottom", fontsize=30 if last else 24,
                fontweight="bold", color=GREEN if last else INK)
        ax.text(i, -10, name, ha="center", va="top", fontsize=17,
                fontweight="bold" if last else "normal", color=INK)

    # the forecast line across October's bar
    x2 = len(data) - 1
    ax.plot([x2 - 0.38, x2 + 0.38], [FORECAST, FORECAST], color=INK, lw=2.6, ls=(0, (5, 4)), zorder=5)
    ax.text(x2, FORECAST + 5, f"Forecast: +{FORECAST}K", ha="center", va="bottom", fontsize=15,
            fontweight="bold", color=INK, zorder=6)
    ax.text(x2 + 0.36, 128, "about\n2.8 times\nthe forecast", ha="left", va="center", fontsize=13.5,
            color=ORANGE, fontweight="bold", linespacing=1.1)

    for yv in (50, 100, 150):
        ax.axhline(yv, color=GRID, lw=1, zorder=1)
    ax.axhline(0, color=AXIS, lw=1.6, zorder=4)
    ax.set_xlim(-0.6, len(data) - 0.15)
    ax.set_ylim(-2, 222)
    ax.axis("off")

    fig.text(0.035, 0.955, "October Hiring Nearly Tripled The Forecast", fontsize=26, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.897, "Net change in U.S. nonfarm payroll jobs, August to October 2026",
             fontsize=14, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.03, "Source: U.S. Bureau of Labor Statistics, Employment Situation, October 2026 "
             "(CES0000000001), seasonally adjusted; September and October are preliminary.\n"
             "Forecast: economists surveyed by Dow Jones, as reported by CNBC (an LSEG poll had 65,000).",
             fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.4)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"jobs-vs-forecast-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
