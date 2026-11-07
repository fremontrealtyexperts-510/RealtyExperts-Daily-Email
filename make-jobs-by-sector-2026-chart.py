"""
make-jobs-by-sector-2026-chart.py  DATA_DIR  [outdir]

The 11/07/26 daily's second Economy chart. Harv supplied a screenshot, "JOBS
REPORT BY SECTOR: Professional and business services added the most jobs in Oct
2026; leisure and hospitality lost the most" (13 industries). Recreated as OUR
chart from BLS, with the two supersectors the screenshot left out (other
services, private education) added back so the bars account for the whole total.

Emits BOTH:
  jobs-by-sector-110726.png      plain HB monogram    -> RE email + Agent Hub
  jobs-by-sector-110726-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds raw BLS Public Data API v1 responses pulled 11/07/26:
  bls-2022-2026.json       incl. CES0000000001 total and 11 of the industries
  bls-sectors-extra.json   CES6000000001, CES1000000001, CES8000000001, CES6561000001

=============================================================================
VERIFICATION 11/07/26
=============================================================================
* Change = October 2026 level minus September 2026 level, thousands, SA.
* All 13 screenshot values match BLS exactly (asserted against SUPPLIED below).
  NOTE: professional and business services is CES6000000001 (+70.0K). Its
  component CES6054000001 (professional, scientific and technical) is +32.9K;
  do not confuse the two (this run briefly did).
* With other services (+6.0K) and private education (-2.0K) the 15 bars sum to
  164.9K against the +165K total; the gap is rounding (asserted within 0.5K).
* October 2026 is a first estimate that BLS revises twice.

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
GRID = "#e6dcc8"
MUTED = "#8a8172"
AXIS = "#8a7f6a"

SECTORS = [
    ("CES6000000001", "Professional and business services"),
    ("CES6562000001", "Health care and social assistance"),
    ("CES4300000001", "Transportation and warehousing"),
    ("CES3000000001", "Manufacturing"),
    ("CES5500000001", "Financial activities"),
    ("CES9000000001", "Government"),
    ("CES4200000001", "Retail trade"),
    ("CES8000000001", "Other services"),
    ("CES4422000001", "Utilities"),
    ("CES1000000001", "Mining and logging"),
    ("CES5000000001", "Information"),
    ("CES6561000001", "Private education"),
    ("CES2000000001", "Construction"),
    ("CES4142000001", "Wholesale trade"),
    ("CES7000000001", "Leisure and hospitality"),
]
# read off the supplied screenshot, thousands
SUPPLIED = {"CES6000000001": 70, "CES6562000001": 55.1, "CES4300000001": 24.8, "CES3000000001": 19,
            "CES5500000001": 7, "CES9000000001": 6, "CES4200000001": 6, "CES4422000001": 0.1,
            "CES1000000001": -1, "CES5000000001": -1, "CES2000000001": -3, "CES4142000001": -9.1,
            "CES7000000001": -13}


def levels():
    out = {}
    for f in ("bls-2022-2026.json", "bls-sectors-extra.json"):
        d = json.load(open(os.path.join(DATA, f)))
        assert d["status"] == "REQUEST_SUCCEEDED", (f, d["status"])
        for s in d["Results"]["series"]:
            out[s["seriesID"]] = {(int(r["year"]), int(r["period"][1:])): float(r["value"])
                                  for r in s["data"] if r["period"] != "M13" and r["value"] != "-"}
    return out


def load():
    lv = levels()
    chg = {sid: round(lv[sid][(2026, 10)] - lv[sid][(2026, 9)], 1) for sid, _ in SECTORS}
    for sid, v in SUPPLIED.items():
        assert abs(chg[sid] - v) < 0.05, (sid, chg[sid], v)
    total = round(lv["CES0000000001"][(2026, 10)] - lv["CES0000000001"][(2026, 9)], 1)
    assert total == 165.0, total
    assert abs(sum(chg.values()) - total) < 0.5, sum(chg.values())
    rows = sorted(((chg[sid], name) for sid, name in SECTORS), key=lambda r: -r[0])
    return rows


def lab(v):
    if abs(v) < 1 and v != 0:
        return f"{v:+.1f}K"
    return f"{v:+.1f}K" if v != int(v) else f"{int(v):+d}K"


def build():
    rows = load()
    fig = plt.figure(figsize=(14.0, 9.6), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.33, 0.12, 0.60, 0.70])
    ax.set_facecolor(CREAM)
    n = len(rows)
    for i, (v, name) in enumerate(rows):
        y = n - 1 - i
        color = GREEN if v > 0 else RED
        ax.barh(y, v, height=0.66, color=color, zorder=3)
        off = 1.2 if v >= 0 else -1.2
        ax.text(v + off, y, lab(v), ha="left" if v >= 0 else "right", va="center", fontsize=13,
                fontweight="bold", color=color)
        # names sit left of the plot in axes x, data y, so they track the bars
        ax.text(-0.03, y, name, transform=ax.get_yaxis_transform(), ha="right", va="center",
                fontsize=13.5, color=INK, clip_on=False)
    for xv in (-20, 20, 40, 60):
        ax.axvline(xv, color=GRID, lw=1, zorder=1)
        ax.text(xv, -1.05, f"{xv:+d}K", ha="center", va="top", fontsize=11, color=MUTED)
    ax.axvline(0, color=AXIS, lw=1.6, zorder=4)
    ax.set_xlim(-24, 82)
    ax.set_ylim(-1.2, n - 0.4)
    ax.axis("off")

    fig.text(0.035, 0.965, "Where October's 165,000 New Jobs Came From", fontsize=26, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.912, "Net change in U.S. jobs from September to October 2026, by industry, in thousands",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.022, "Source: U.S. Bureau of Labor Statistics, Employment Situation, October 2026, "
             "seasonally adjusted. First estimate; BLS revises it twice. Industries sum to the total within rounding.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"jobs-by-sector-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
