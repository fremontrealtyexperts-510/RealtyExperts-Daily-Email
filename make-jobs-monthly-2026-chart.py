"""
make-jobs-monthly-2026-chart.py  DATA_DIR  [outdir]

The 11/07/26 daily's first Economy chart. Harv supplied a screenshot from a jobs
report video ("Jobs added each month (thousands), below the line = jobs lost",
January 2023 to October 2026, +165k in Oct 2026). Recreated as OUR chart from
the Bureau of Labor Statistics series itself, never from the screenshot.

Emits BOTH:
  jobs-monthly-110726.png      plain HB monogram    -> RE email + Agent Hub
  jobs-monthly-110726-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR/bls-2022-2026.json is the raw BLS Public Data API v1 response
(api.bls.gov/publicAPI/v1/timeseries/data/, keyless) pulled 11/07/26 for
CES0000000001 (total nonfarm employment, thousands, seasonally adjusted) and
LNS14000000 (unemployment rate, seasonally adjusted), 2022 to 2026.

=============================================================================
VERIFICATION 11/07/26
=============================================================================
* Monthly change = this month's level minus last month's (Dec 2022 seeds Jan 2023).
* October 2026 = +165K and September = +60K, the BLS release figures (asserted).
* The supplied screenshot's shape matches point for point: Jan 2023 434K (its
  tallest bar, above +400k), the 2025 and 2026 negative months (Jan 2025 -48,
  Jun -20, Aug -70, Oct 2025 -140, Dec -17, Feb 2026 -156, Jul -10).
* Unemployment 4.1% in October from 4.2% in September (asserted). October 2025
  has no unemployment reading ("Data unavailable due to the 2025 lapse in
  appropriations"); payrolls for that month do exist and are plotted.
* The two newest months are preliminary (BLS footnote P) and will be revised.

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
STAMP = "110726"

CREAM = "#fdf6e8"
INK = "#1f2933"
RED = "#d1495b"
GREEN = "#2e8b57"
SAND = "#c9b48f"
GRID = "#e6dcc8"
MUTED = "#8a8172"
AXIS = "#8a7f6a"
ORANGE = "#ea580c"


def series(sid):
    d = json.load(open(os.path.join(DATA, "bls-2022-2026.json")))
    assert d["status"] == "REQUEST_SUCCEEDED", d["status"]
    s = next(x for x in d["Results"]["series"] if x["seriesID"] == sid)
    return {(int(r["year"]), int(r["period"][1:])): r["value"] for r in s["data"] if r["period"] != "M13"}


def load():
    lv = {k: float(v) for k, v in series("CES0000000001").items()}
    months = [(y, m) for y in range(2023, 2027) for m in range(1, 13) if (y, m) <= (2026, 10)]
    out = []
    for y, m in months:
        prev = (y, m - 1) if m > 1 else (y - 1, 12)
        out.append(((y, m), round(lv[(y, m)] - lv[prev])))
    ch = dict(out)
    assert ch[(2026, 10)] == 165 and ch[(2026, 9)] == 60, (ch[(2026, 10)], ch[(2026, 9)])
    assert ch[(2023, 1)] == 434 and ch[(2025, 10)] == -140 and ch[(2026, 2)] == -156, ch
    ur = series("LNS14000000")
    assert ur[(2026, 10)] == "4.1" and ur[(2026, 9)] == "4.2", (ur[(2026, 10)], ur[(2026, 9)])
    assert ur[(2025, 10)] == "-", ur[(2025, 10)]
    return out


def build():
    data = load()
    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.17, 0.89, 0.60])
    ax.set_facecolor(CREAM)
    n = len(data)
    for i, ((y, m), v) in enumerate(data):
        last = i == n - 1
        color = GREEN if last else (RED if v < 0 else SAND)
        ax.bar(i, v, width=0.72, color=color, zorder=3)
        if m == 1:
            ax.text(i - 0.4, -232, str(y), ha="left", va="top", fontsize=13, color=INK, fontweight="bold")
            ax.plot([i - 0.5, i - 0.5], [-215, -200], color=AXIS, lw=1.2, zorder=2)
    for yv in (-200, -100, 100, 200, 300, 400):
        ax.axhline(yv, color=GRID, lw=1, zorder=1)
        ax.text(-1.4, yv, f"{yv:+d}K", ha="right", va="center", fontsize=11, color=MUTED)
    ax.axhline(0, color=AXIS, lw=1.6, zorder=4)
    ax.text(-1.4, 0, "0", ha="right", va="center", fontsize=11, color=MUTED)
    ax.set_xlim(-1.0, n + 0.2)
    ax.set_ylim(-215, 470)
    ax.axis("off")

    # October 2026 call out, above the last bar
    ax.annotate("", xy=(n - 1, 175), xytext=(n - 1, 300),
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=2), zorder=5)
    ax.text(n - 1, 306, "+165K\nin October", ha="center", va="bottom", fontsize=14.5, fontweight="bold",
            color=GREEN, linespacing=1.15)

    # unemployment note, upper middle where 2025 bars are short
    fig.text(0.47, 0.842, "Unemployment rate: 4.1% in October", fontsize=13.5, fontweight="bold",
             color=ORANGE, ha="left", va="top")
    fig.text(0.47, 0.808, "down from 4.2% in September; red bars are months with fewer jobs",
             fontsize=12.5, color=INK, ha="left", va="top")

    fig.text(0.035, 0.955, "Employers Added 165,000 Jobs In October", fontsize=26, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.897, "Net change in U.S. nonfarm payroll jobs each month, January 2023 to October 2026",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.03, "Source: U.S. Bureau of Labor Statistics, Employment Situation, October 2026 "
             "(CES0000000001, LNS14000000), seasonally adjusted. September and October are preliminary.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"jobs-monthly-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
