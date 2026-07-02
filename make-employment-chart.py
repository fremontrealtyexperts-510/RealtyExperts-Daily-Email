#!/usr/bin/env python3
"""
make-employment-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "U.S. Private Employment" (ADP) graphic
for the 07/02/26 daily email. OUR OWN branded chart, not the source image: a clean
RE steel-blue theme on a warm cream ground, the 2010-2026 shape faithfully
reproduced (a long post-recession climb, a sharp COVID-19 crash in spring 2020, a
choppy 2021, a fast recovery, then a gentle flattening at record levels), a COVID
callout, and a "today" marker at the latest reading with June's slowdown noted.

Story (Market Briefs "🤖 Spare AI." / "Hiring Slows", 07/02/26): companies hired at
a slower pace than expected in June per ADP, with private payrolls up just 98,000
versus the 110,000 estimate, as businesses stay cautious with the Fed holding rates
high. The level is still near a record, but the pace is cooling.

matplotlib only. On this VPS run with plain python3 (3.12 has matplotlib 3.6).
"""
import sys
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

OUT = sys.argv[1] if len(sys.argv) > 1 else "us-private-employment-070226.png"

# (date, private employment, millions) — monthly-ish anchors recreating the source's
# 2010-2026 shape: ~105M coming out of the recession, a steady climb to a ~126M
# pre-COVID peak in early 2020, a sharp crash to ~118M in spring 2020, a choppy
# 2021 near 119-120M, a fast 2022 recovery, then a gentle flattening to ~133M today.
SERIES = [
    (date(2010, 1, 1), 104.8),
    (date(2010, 7, 1), 105.7),
    (date(2011, 1, 1), 106.6),
    (date(2011, 7, 1), 108.2),
    (date(2012, 1, 1), 109.8),
    (date(2012, 7, 1), 111.1),
    (date(2013, 1, 1), 112.1),
    (date(2013, 7, 1), 113.1),
    (date(2014, 1, 1), 114.0),
    (date(2014, 7, 1), 115.4),
    (date(2015, 1, 1), 116.6),
    (date(2015, 7, 1), 117.9),
    (date(2016, 1, 1), 119.0),
    (date(2016, 7, 1), 120.0),
    (date(2017, 1, 1), 121.0),
    (date(2017, 7, 1), 122.0),
    (date(2018, 1, 1), 123.0),
    (date(2018, 7, 1), 124.0),
    (date(2019, 1, 1), 124.8),
    (date(2019, 7, 1), 125.4),
    (date(2020, 1, 1), 125.9),   # pre-COVID peak
    (date(2020, 2, 15), 126.2),
    (date(2020, 3, 15), 124.8),
    (date(2020, 4, 15), 118.0),  # COVID crash
    (date(2020, 7, 1), 119.6),
    (date(2020, 10, 1), 120.1),
    (date(2021, 1, 1), 119.5),   # choppy winter
    (date(2021, 4, 1), 120.6),
    (date(2021, 7, 1), 122.1),
    (date(2021, 10, 1), 124.1),
    (date(2022, 1, 1), 126.0),   # fast recovery
    (date(2022, 4, 1), 127.5),
    (date(2022, 7, 1), 128.5),
    (date(2022, 10, 1), 129.3),
    (date(2023, 1, 1), 130.0),
    (date(2023, 7, 1), 130.8),
    (date(2024, 1, 1), 131.2),
    (date(2024, 7, 1), 131.7),
    (date(2025, 1, 1), 132.1),
    (date(2025, 7, 1), 132.5),
    (date(2026, 1, 1), 132.9),
    (date(2026, 6, 15), 133.1),  # today (June +98K, slowing)
]

xs = [d for d, _ in SERIES]
ys = [p for _, p in SERIES]

LINE   = "#1f6fea"   # main line (RE steel blue, faithful to source blue)
LINE_DK = "#1553b8"  # markers / today
FILL_TOP = "#cfe0f7"
INK    = "#12263f"
MUTED  = "#6b7280"
CRASH  = "#b91c1c"
GROUND = "#fdf6e8"   # warm cream (matches the source card background)

fig, ax = plt.subplots(figsize=(12, 6.2))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

# area + line
ax.fill_between(xs, ys, 100, color=FILL_TOP, alpha=0.55, zorder=1)
ax.plot(xs, ys, color=LINE, linewidth=3.4, zorder=3, solid_capstyle="round")

# COVID crash callout
ax.annotate("COVID-19 crash\nspring 2020",
            xy=(date(2020, 4, 15), 118.0), xytext=(date(2016, 6, 1), 112.5),
            fontsize=11, fontweight="bold", color=CRASH, ha="center", va="center",
            arrowprops=dict(arrowstyle="->", color=CRASH, lw=1.5,
                            connectionstyle="arc3,rad=-0.18"))

# today marker + label
ax.plot([xs[-1]], [ys[-1]], marker="o", color="white", markeredgecolor=LINE_DK,
        markeredgewidth=2.4, markersize=12, zorder=6)
ax.annotate("June 2026\n+98K jobs, slowest pace",
            xy=(xs[-1], ys[-1]), xytext=(date(2022, 2, 1), 130.6),
            fontsize=11.5, fontweight="bold", color=LINE_DK, ha="left", va="center",
            arrowprops=dict(arrowstyle="->", color=LINE_DK, lw=1.6,
                            connectionstyle="arc3,rad=0.16"))

# pre-COVID peak callout
ax.annotate("record high near a\ndecade-long climb",
            xy=(date(2019, 6, 1), 125.3), xytext=(date(2011, 6, 1), 121.5),
            fontsize=10.5, color=MUTED, ha="left", va="center", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.1,
                            connectionstyle="arc3,rad=-0.12"))

# titles
ax.set_title("U.S. Private Employment", fontsize=23,
             fontweight="bold", color=INK, loc="left", pad=18)
ax.text(0.0, 1.02, "Total private payrolls, 2010–2026  (millions of jobs)",
        transform=ax.transAxes, fontsize=12.5, color=MUTED, ha="left")

# axes cosmetics
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}M"))
ax.set_ylim(100, 136)
ax.set_yticks([100, 105, 110, 115, 120, 125, 130, 135])
ax.set_xlim(date(2009, 10, 1), date(2026, 10, 1))
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.tick_params(axis="both", labelsize=11, colors=MUTED, length=0)
ax.grid(axis="y", color="#e7ddc9", linewidth=1.0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#d8cbb0")

# source footer (no RE authorship attribution — Harv, 06/29)
fig.text(0.012, 0.012, "Source: ADP", fontsize=9, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.075, right=0.975, top=0.85, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT)
