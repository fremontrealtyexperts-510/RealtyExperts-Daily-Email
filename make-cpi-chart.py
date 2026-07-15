#!/usr/bin/env python3
"""
make-cpi-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "CPI Inflation Over Time" graphic
(U.S. Bureau of Labor Statistics, CPI-U all items, 12-month % change) for the
07/15/26 daily email. OUR OWN branded chart, not the source image: a clean coral
inflation line on a warm cream ground, the 2006-2026 shape faithfully reproduced
(the 2008 spike then 2009 deflation dip below zero, the flat 2012-2015 stretch, the
2021-2022 surge to a ~9% peak, and the sticky glide back up to 3.5% today), with the
2008 and 2020 recessions shaded and a "today" callout at the latest reading.

Story (Market Briefs "⏳ Back in time." / "Chair Takes A Stand", 07/15/26): new Fed
Chair Kevin Warsh told the House the Fed will not back down on inflation, with high
prices still burdening households. Many investors now expect at least one more rate
hike in 2026. Headline CPI is running about 3.5%, still above the Fed's 2% target.

matplotlib only. Build with python3.13 on Mac (matplotlib 3.10).
"""
import sys
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

OUT = sys.argv[1] if len(sys.argv) > 1 else "cpi-071526.png"

# (year, month, CPI-U YoY %) anchors recreating the source's shape.
A = [
 (2006,1,4.0),(2006,3,3.4),(2006,6,4.3),(2006,9,2.1),(2006,12,2.5),
 (2007,3,2.8),(2007,6,2.7),(2007,9,2.8),(2007,12,4.1),
 (2008,3,4.0),(2008,6,5.0),(2008,7,5.6),(2008,9,4.9),(2008,11,1.1),(2008,12,0.1),
 (2009,2,0.2),(2009,4,-0.7),(2009,6,-1.4),(2009,7,-2.1),(2009,10,-0.2),(2009,12,2.7),
 (2010,3,2.3),(2010,6,1.1),(2010,9,1.1),(2010,12,1.5),
 (2011,3,2.7),(2011,6,3.6),(2011,9,3.9),(2011,12,3.0),
 (2012,3,2.7),(2012,6,1.7),(2012,9,2.0),(2012,12,1.7),
 (2013,3,1.5),(2013,6,1.8),(2013,9,1.2),(2013,12,1.5),
 (2014,3,1.5),(2014,6,2.1),(2014,9,1.7),(2014,12,0.8),
 (2015,1,-0.1),(2015,4,-0.2),(2015,7,0.2),(2015,10,0.2),(2015,12,0.7),
 (2016,3,0.9),(2016,6,1.0),(2016,9,1.5),(2016,12,2.1),
 (2017,3,2.4),(2017,6,1.6),(2017,9,2.2),(2017,12,2.1),
 (2018,3,2.4),(2018,6,2.9),(2018,7,2.9),(2018,10,2.5),(2018,12,1.9),
 (2019,3,1.9),(2019,6,1.6),(2019,9,1.7),(2019,12,2.3),
 (2020,2,2.3),(2020,3,1.5),(2020,4,0.3),(2020,5,0.1),(2020,8,1.3),(2020,12,1.4),
 (2021,3,2.6),(2021,5,5.0),(2021,6,5.4),(2021,9,5.4),(2021,10,6.2),(2021,12,7.0),
 (2022,3,8.5),(2022,6,9.1),(2022,9,8.2),(2022,12,6.5),
 (2023,3,5.0),(2023,6,3.0),(2023,9,3.7),(2023,12,3.4),
 (2024,3,3.5),(2024,6,3.0),(2024,9,2.4),(2024,12,2.9),
 (2025,3,2.8),(2025,6,2.7),(2025,9,3.0),(2025,12,3.2),
 (2026,3,3.3),(2026,6,3.5),
]
xs = [date(y, m, 15) for y, m, _ in A]
ys = [v for _, _, v in A]

LINE   = "#e5484d"   # coral inflation line
LINE_DK = "#b91c1c"
INK    = "#12263f"
MUTED  = "#6b7280"
GROUND = "#fdf6e8"
BAND   = "#e7ddc9"

fig, ax = plt.subplots(figsize=(12, 6.2))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

# recession shading
ax.axvspan(date(2007, 12, 1), date(2009, 6, 1), color=BAND, alpha=0.7, zorder=0)
ax.axvspan(date(2020, 2, 1), date(2020, 4, 30), color=BAND, alpha=0.7, zorder=0)
ax.text(date(2008, 9, 1), 9.4, "2008", fontsize=9, color="#a99f88", ha="center")
ax.text(date(2020, 3, 1), 9.4, "2020", fontsize=9, color="#a99f88", ha="center")

ax.axhline(0, color="#c9bfa6", linewidth=1.2, zorder=1)
ax.plot(xs, ys, color=LINE, linewidth=2.6, zorder=3, solid_capstyle="round")

# 2022 peak callout
ax.annotate("2022 peak ~9.1%",
            xy=(date(2022, 6, 15), 9.1), xytext=(date(2019, 1, 1), 8.7),
            fontsize=10.5, color=MUTED, ha="center", va="center", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.1,
                            connectionstyle="arc3,rad=-0.15"))
# 2009 deflation callout
ax.annotate("2009 deflation dip",
            xy=(date(2009, 7, 15), -2.1), xytext=(date(2012, 6, 1), -1.9),
            fontsize=10, color=MUTED, ha="center", va="center", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0,
                            connectionstyle="arc3,rad=0.15"))
# today marker + label
ax.plot([xs[-1]], [ys[-1]], marker="o", color="white", markeredgecolor=LINE_DK,
        markeredgewidth=2.4, markersize=12, zorder=6)
ax.annotate("Jun 2026\n3.5%",
            xy=(xs[-1], ys[-1]), xytext=(date(2024, 10, 1), 5.4),
            fontsize=12, fontweight="bold", color=LINE_DK, ha="center", va="center",
            arrowprops=dict(arrowstyle="->", color=LINE_DK, lw=1.5,
                            connectionstyle="arc3,rad=-0.2"))

ax.set_title("CPI Inflation Over Time", fontsize=23,
             fontweight="bold", color=INK, loc="left", pad=18)
ax.text(0.0, 1.02, "Consumer prices, all items, 12-month % change  (June 2006 to June 2026)",
        transform=ax.transAxes, fontsize=12.5, color=MUTED, ha="left")

ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax.set_ylim(-3, 10)
ax.set_yticks([-2, 0, 2, 4, 6, 8, 10])
ax.set_xlim(date(2006, 1, 1), date(2026, 12, 1))
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.tick_params(axis="both", labelsize=11, colors=MUTED, length=0)
ax.grid(axis="y", color="#e7ddc9", linewidth=0.9)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#d8cbb0")

fig.text(0.012, 0.012, "Source: U.S. Bureau of Labor Statistics (CPI-U, not seasonally adjusted)",
         fontsize=9, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.065, right=0.975, top=0.85, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT)
