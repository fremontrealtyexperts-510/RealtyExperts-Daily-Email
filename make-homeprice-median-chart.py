#!/usr/bin/env python3
"""
make-homeprice-median-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "U.S. Median Home Sale Price" graphic
for the 07/20/26 daily email. OUR OWN branded chart, not the source image: warm
cream ground, RE-orange line over a soft fill, a dashed line at the 2022 peak,
and callouts on the peak and the latest quarter.

Data: FRED MSPUS, "Median Sales Price of Houses Sold for the United States",
U.S. Census Bureau and HUD, quarterly, not seasonally adjusted, Q1 2016 to
Q1 2026. Values are the published series, not estimates.

CAREFUL, do not conflate series: this is the Census and HUD quarterly measure
($403,200 in Q1 2026). Market Briefs separately quotes the National Association
of REALTORS® June existing-home median of $446,400, which is a different survey,
a different universe, and a different frequency. Keep the two attributed
separately in any copy that mentions both.

Story: the national median is $403,200, about 8.9% below the Q4 2022 peak of
$442,600, even while affordability keeps tightening because rates did the work
prices did not.

No authorship label on the chart (per Harv, 06/29) - footer carries only the data
source. matplotlib only; build with python3.13 on Mac.
"""
import sys
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

OUT = sys.argv[1] if len(sys.argv) > 1 else "homeprice-median-072026.png"

# (quarter start, median sales price USD) - FRED MSPUS, faithful to source
SERIES = [
    ("2016-01-01", 299800),
    ("2016-04-01", 306000),
    ("2016-07-01", 303800),
    ("2016-10-01", 310900),
    ("2017-01-01", 313100),
    ("2017-04-01", 318200),
    ("2017-07-01", 320500),
    ("2017-10-01", 337900),
    ("2018-01-01", 331800),
    ("2018-04-01", 315600),
    ("2018-07-01", 330900),
    ("2018-10-01", 322800),
    ("2019-01-01", 313000),
    ("2019-04-01", 322500),
    ("2019-07-01", 318400),
    ("2019-10-01", 327100),
    ("2020-01-01", 329000),
    ("2020-04-01", 317100),
    ("2020-07-01", 327900),
    ("2020-10-01", 338600),
    ("2021-01-01", 355000),
    ("2021-04-01", 367800),
    ("2021-07-01", 395200),
    ("2021-10-01", 414000),
    ("2022-01-01", 413500),
    ("2022-04-01", 437700),
    ("2022-07-01", 438000),
    ("2022-10-01", 442600),
    ("2023-01-01", 429000),
    ("2023-04-01", 418500),
    ("2023-07-01", 435400),
    ("2023-10-01", 423200),
    ("2024-01-01", 426800),
    ("2024-04-01", 414500),
    ("2024-07-01", 415300),
    ("2024-10-01", 419300),
    ("2025-01-01", 423100),
    ("2025-04-01", 416100),
    ("2025-07-01", 410100),
    ("2025-10-01", 412300),
    ("2026-01-01", 403200)
]

dates = [datetime.strptime(d, "%Y-%m-%d") for d, _ in SERIES]
vals  = [v for _, v in SERIES]

ORANGE    = "#ea580c"   # RE section orange
ORANGE_DK = "#c2410c"
INK       = "#12263f"
MUTED     = "#6b7280"
GROUND    = "#fdf6e8"
GRID      = "#e7ddc9"

pk_i = max(range(len(vals)), key=lambda i: vals[i])
peak  = vals[pk_i]
last  = vals[-1]
off   = (last - peak) / peak * 100.0

fig, ax = plt.subplots(figsize=(12, 6.0))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.fill_between(dates, vals, 280000, color=ORANGE, alpha=0.12, zorder=2)
ax.plot(dates, vals, color=ORANGE, linewidth=2.6, zorder=4,
        solid_joinstyle="round", solid_capstyle="round")

# dashed line at the 2022 peak, so the gap since is visible
ax.axhline(peak, color=ORANGE_DK, linewidth=1.1, linestyle=(0, (5, 4)),
           alpha=0.5, zorder=3)

ax.scatter([dates[pk_i]], [peak], s=70, color=ORANGE_DK, zorder=6,
           edgecolor=GROUND, linewidth=2.0)
ax.annotate("Q4 2022 peak: $442,600",
            xy=(dates[pk_i], peak), xytext=(dates[pk_i - 11], 468000),
            fontsize=12, fontweight="bold", color=ORANGE_DK, ha="center", va="center",
            arrowprops=dict(arrowstyle="->", color=ORANGE_DK, lw=1.5,
                            connectionstyle="arc3,rad=0.2"))

ax.scatter([dates[-1]], [last], s=95, color=ORANGE, zorder=6,
           edgecolor=GROUND, linewidth=2.2)
ax.annotate(f"Q1 2026: ${last:,.0f}\n{off:.1f}% below the peak",
            xy=(dates[-1], last), xytext=(dates[-15], 336000),
            fontsize=12.5, fontweight="bold", color=ORANGE, ha="center", va="center",
            arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.7,
                            connectionstyle="arc3,rad=-0.22"))

ax.set_ylim(280000, 480000)
ax.set_yticks([300000, 340000, 380000, 420000, 460000])
ax.set_yticklabels(["$300K", "$340K", "$380K", "$420K", "$460K"])
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.tick_params(axis="y", labelsize=11, colors=MUTED, length=0)
ax.tick_params(axis="x", labelsize=12, colors=INK, length=0)
for lbl in ax.get_xticklabels():
    lbl.set_fontweight("bold")
ax.grid(axis="y", color=GRID, linewidth=1.0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#d8cbb0")

ax.set_title("U.S. Median Home Sale Price", fontsize=24, fontweight="bold",
             color=INK, loc="left", pad=26)
ax.text(0.0, 1.03, "Median sales price of houses sold, quarterly  (Q1 2016 to Q1 2026)",
        transform=ax.transAxes, fontsize=12.5, color=MUTED, ha="left")

fig.text(0.012, 0.014,
         "Source: U.S. Census Bureau and U.S. Dept. of Housing and Urban "
         "Development via FRED (MSPUS)",
         fontsize=9, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.075, right=0.975, top=0.84, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT)
