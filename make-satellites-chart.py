#!/usr/bin/env python3
"""
make-satellites-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "Active Satellites In Earth's Orbit"
graphic Harv supplied for the 07/28/26 daily email. OUR OWN branded chart, not
the source image: warm cream ground, a stacked area splitting Starlink from every
other operator, and the 2026 total called out in a rounded pill.

Story tie-in (Market Briefs, 07/28/26): Amazon wants to launch 5,105 satellites
for a direct-to-phone network, racing to catch SpaceX's Starlink, which already
offers the service. If approved, Amazon would hold the second-most satellites in
orbit. The chart shows why that is such a climb: Starlink alone already accounts
for about two thirds of everything active up there.

Data: active satellites in Earth orbit by year, split Starlink vs all other
operators, transcribed faithfully from the source graphic Harv provided
(ESA Space Environment Statistics; CelesTrak SATCAT Boxscore; Jonathan's Space
Report, April 2026). 2026 totals 15,500: Starlink 10,200, all others 5,300.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "satellites-072826.png"

# (year, all other operators, Starlink) - faithful to the source graphic.
DATA = [
    (2010,  950,     0),
    (2011, 1000,     0),
    (2012, 1050,     0),
    (2013, 1150,     0),
    (2014, 1250,     0),
    (2015, 1350,     0),
    (2016, 1450,     0),
    (2017, 1600,     0),
    (2018, 1800,     0),
    (2019, 2000,   120),
    (2020, 2300,   900),
    (2021, 2700,  1950),
    (2022, 3000,  3300),
    (2023, 3200,  4800),
    (2024, 3700,  7800),
    (2025, 4700,  9300),
    (2026, 5300, 10200),
]

years  = [r[0] for r in DATA]
others = [r[1] for r in DATA]
stars  = [r[2] for r in DATA]
totals = [o + s for o, s in zip(others, stars)]

BLUE     = "#3b82f6"   # all other operators
ORANGE   = "#f59e0b"   # Starlink
ORANGE_D = "#b45309"
INK      = "#12263f"
MUTED    = "#6b7280"
GROUND   = "#fdf6e8"   # warm cream (house style)
GRID     = "#e7ddc9"

fig, ax = plt.subplots(figsize=(12, 6.4))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.fill_between(years, 0, others, color=BLUE, alpha=0.85, zorder=3,
                linewidth=0)
ax.fill_between(years, others, totals, color=ORANGE, alpha=0.9, zorder=3,
                linewidth=0)
ax.plot(years, totals, color=INK, linewidth=2.0, zorder=5)
ax.plot(years, others, color=GROUND, linewidth=1.6, zorder=4)

# 2026 total callout
ax.plot([years[-1]], [totals[-1]], "o", color=INK, markersize=8, zorder=6)
ax.annotate(f"{totals[-1]:,} total",
            xy=(years[-1], totals[-1]), xytext=(years[-1] - 4.6, 17000),
            fontsize=17, fontweight="bold", color=INK, zorder=7,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="white",
                      edgecolor="#e7ddc9", linewidth=1.2),
            arrowprops=dict(arrowstyle="-", color="#9ca3af", linewidth=1.2,
                            linestyle=(0, (3, 3)),
                            connectionstyle="angle,angleA=0,angleB=90,rad=0"))

# legend, drawn manually so the swatches read like the source
ax.add_patch(plt.Rectangle((2010.15, 19250), 0.55, 700, color=ORANGE,
                           clip_on=False, zorder=8))
ax.text(2010.95, 19600, "Starlink", fontsize=13.5, fontweight="bold",
        color=INK, va="center", zorder=8)
ax.text(2013.15, 19600, f"{stars[-1]:,}", fontsize=13.5, fontweight="bold",
        color=ORANGE_D, va="center", zorder=8)
ax.add_patch(plt.Rectangle((2014.75, 19250), 0.55, 700, color=BLUE,
                           clip_on=False, zorder=8))
ax.text(2015.55, 19600, "All other operators", fontsize=13.5,
        fontweight="bold", color=INK, va="center", zorder=8)
ax.text(2020.35, 19600, f"{others[-1]:,}", fontsize=13.5, fontweight="bold",
        color="#1d4ed8", va="center", zorder=8)

ax.set_xlim(2010, 2026.6)
ax.set_ylim(0, 20400)
ax.set_yticks([0, 5000, 10000, 15000])
ax.set_yticklabels(["0", "5,000", "10,000", "15,000"], fontsize=12,
                   color=MUTED)
ax.set_xticks([2012, 2016, 2020, 2024, 2026])
ax.set_xticklabels(["2012", "2016", "2020", "2024", "2026"], fontsize=12.5,
                   fontweight="bold", color=MUTED)
ax.grid(axis="y", color=GRID, linewidth=1.1, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("Active Satellites In Earth's Orbit", fontsize=25,
             fontweight="bold", color=INK, loc="left", pad=52)

fig.text(0.012, 0.014,
         "Sources: ESA Space Environment Statistics; CelesTrak SATCAT Boxscore; "
         "Jonathan's Space Report (Apr 2026)",
         fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.072, right=0.985, top=0.79, bottom=0.085)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, f"| total {totals[-1]:,} | Starlink {stars[-1]:,} "
      f"({stars[-1]/totals[-1]*100:.0f}%) | others {others[-1]:,}")
