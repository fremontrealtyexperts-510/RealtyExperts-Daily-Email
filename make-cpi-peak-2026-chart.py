#!/usr/bin/env python3
"""
make-cpi-peak-2026-chart.py  DATA_DIR  [outdir]

The 10/13/26 daily's inflation chart. Harv attached the newsletter graphic
"Inflation Peaked In May" (U.S. CPI, year over year, 2026: 2.4, 2.4, 3.3, 3.8,
4.2 PEAK, 3.5, 3.4, 3.4, and September 3.6 dashed as the Kalshi traders'
forecast; "Source: BLS, Kalshi via CNBC (Oct. 2026)"). Emits BOTH:

  cpi-peak-101326.png      plain HB monogram    -> RE email + Agent Hub
  cpi-peak-101326-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds bls.json, a BLS public API v2 pull (fetched Oct. 13, 2026 about
10:36 AM PT) of CUUR0000SA0 (CPI-U all items, U.S. city average, not seasonally
adjusted) and CUURS49BSA0 (CPI-U all items, San Francisco-Oakland-Hayward,
bimonthly, even months), 2025 to 2026.

=============================================================================
VERIFICATION 10/13/26
=============================================================================
All eight supplied U.S. points match the 12-month change computed from BLS
index levels (rounded half up): 2.386, 2.414, 3.256, 3.811, 4.249, 3.531,
3.365, 3.397. August is the newest month BLS has out (released Sept. 11:
"The all items index rose 3.4 percent for the 12 months ending August").
September is NOT released; BLS publishes it Wednesday, Oct. 14, 2026 at
8:30 a.m. ET. The 3.6% is a forecast: CNBC (Oct. 12) "Traders think the
September consumer price index ... will show a 3.6% increase year over year.
That's in line with a FactSet consensus estimate." Kalshi at 10:36 AM PT Oct. 13
priced a 3.6 print about 38% and 3.7 about 40%, so the bar is labeled a
forecast, not a reading. Note 3.6 would be UP from August's 3.4, still under
May's 4.2 peak.

Our addition (keep it local): the Bay Area's own CPI. BLS prices the
San Francisco area every other month: Feb 2.5, April 3.8, June 3.8, Aug 3.4.
Shown as chips under those months, because the two series coincide in April
and August and a second line would sit on top of the first.

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
STAMP = "101326"
FORECAST = 3.6

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e05a47"
DEEP = "#b8432f"
BLUE = "#2b6cb0"
GREEN = "#2f7d4f"
GREEN_BG = "#e3efe4"
GRID = "#d8cdb8"
MUTED = "#8a8172"
SHORT = ["Jan.", "Feb.", "March", "April", "May", "June", "July", "Aug.", "Sept."]


def yoy(levels, year, m):
    a = Decimal(levels[(year, m)])
    b = Decimal(levels[(year - 1, m)])
    return (a / b - 1) * 100


def r1(x):
    return float(x.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def load():
    d = json.load(open(os.path.join(DATA, "bls.json")))
    series = {s["seriesID"]: s["data"] for s in d["Results"]["series"]}
    lv = lambda sid: {(int(x["year"]), int(x["period"][1:])): x["value"]
                      for x in series[sid] if x["value"] not in ("-", "")}
    us, sf = lv("CUUR0000SA0"), lv("CUURS49BSA0")
    latest = max(k for k in us if k[0] == 2026)
    assert latest == (2026, 8), latest            # September not released yet
    usv = [r1(yoy(us, 2026, m)) for m in range(1, 9)]
    assert usv == [2.4, 2.4, 3.3, 3.8, 4.2, 3.5, 3.4, 3.4], usv
    sfv = {m: r1(yoy(sf, 2026, m)) for m in (2, 4, 6, 8)}
    assert sfv == {2: 2.5, 4: 3.8, 6: 3.8, 8: 3.4}, sfv
    assert max(usv) == usv[4] and FORECAST < usv[4] and FORECAST > usv[7]
    return usv, sfv


def build():
    usv, sfv = load()
    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.06, 0.30, 0.86, 0.51])
    ax.set_facecolor(CREAM)

    x = list(range(8))
    ax.fill_between(x, 1.5, usv, color="#dbe6f3", lw=0, zorder=1)
    ax.plot(x, usv, color=BLUE, lw=3.2, solid_joinstyle="round", zorder=4)
    ax.plot([7, 8], [usv[-1], FORECAST], color=CORAL, lw=3.0, ls=(0, (3, 2.2)), zorder=4)
    ax.scatter(x, usv, s=60, color=BLUE, edgecolor=CREAM, linewidth=1.5, zorder=5)

    # labels: above the line on the rising leg and the plateau, below where the line climbs into them
    place = {0: (0, 12, "center", "bottom"), 1: (0, 12, "center", "bottom"),
             2: (-12, 6, "right", "bottom"), 3: (-12, 6, "right", "bottom"),
             5: (0, 12, "center", "bottom"), 6: (0, 12, "center", "bottom"),
             7: (0, -14, "center", "top")}
    for i, v in enumerate(usv):
        if i == 4:
            continue
        dx, dy, ha, va = place[i]
        ax.annotate(f"{v:.1f}%", xy=(i, v), xytext=(dx, dy), textcoords="offset points",
                    fontsize=14, fontweight="bold", color=INK, ha=ha, va=va)
    ax.scatter([4], [usv[4]], s=140, color=DEEP, edgecolor=CREAM, linewidth=2, zorder=6)
    ax.annotate(f"{usv[4]:.1f}% peak", xy=(4, usv[4]), xytext=(0, 16), textcoords="offset points",
                fontsize=16, fontweight="bold", color="white", ha="center", va="bottom", zorder=7,
                bbox=dict(boxstyle="round,pad=0.35", facecolor=DEEP, edgecolor="none"))

    ax.scatter([8], [FORECAST], s=130, color=CREAM, edgecolor=CORAL, linewidth=2.6, zorder=6)
    ax.annotate(f"{FORECAST:.1f}%", xy=(8, FORECAST), xytext=(0, 16), textcoords="offset points",
                fontsize=16, fontweight="bold", color="white", ha="center", va="bottom", zorder=7,
                bbox=dict(boxstyle="round,pad=0.35", facecolor=CORAL, edgecolor="none"))
    ax.text(8, FORECAST - 0.22, "forecast\nBLS reports\nOct. 14", fontsize=11.5, color=DEEP,
            ha="center", va="top", linespacing=1.2)

    ax.set_xticks(list(range(9)))
    ax.set_xticklabels(SHORT, fontsize=13, color=MUTED)
    ax.get_xticklabels()[-1].set_color(DEEP)
    ax.set_xlim(-0.45, 8.45)
    ax.set_ylim(1.5, 5.0)
    ax.set_yticks([2, 3, 4, 5])
    ax.set_yticklabels(["2%", "3%", "4%", "5%"], fontsize=12, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # Bay Area strip: chips under the months BLS prices the San Francisco area
    strip = fig.add_axes([0.06, 0.095, 0.86, 0.06], sharex=ax)
    strip.set_facecolor(CREAM)
    strip.set_ylim(0, 1)
    strip.axis("off")
    for m, v in sfv.items():
        strip.text(m - 1, 0.5, f"{v:.1f}%", fontsize=14, fontweight="bold", color=GREEN,
                   ha="center", va="center",
                   bbox=dict(boxstyle="round,pad=0.4", facecolor=GREEN_BG, edgecolor="none"))
    fig.text(0.035, 0.172, "Bay Area (San Francisco, Oakland, Hayward), priced every other month:",
             fontsize=12.5, color=GREEN, ha="left", va="bottom", fontweight="bold")

    fig.text(0.035, 0.955, "Inflation Peaked In May, But It Is Not Falling Fast", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895, "Consumer price index, change from a year earlier, 2026. "
             "September is the traders' forecast.", fontsize=13.2, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035, "Source: U.S. Bureau of Labor Statistics, CPI for all urban consumers, not "
             "seasonally adjusted. September forecast: Kalshi traders and FactSet consensus, via CNBC "
             "(Oct. 12, 2026).", fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"cpi-peak-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
