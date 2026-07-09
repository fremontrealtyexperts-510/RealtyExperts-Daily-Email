#!/usr/bin/env python3
"""
make-autoloan-chart.py  [out.png]

REALTY EXPERTS branded recreation of the "Outstanding auto loan debt" chart for
the 07/09/26 daily email (Market Briefs "Search party"; the New Record car-payment
story). OUR OWN branded chart, not the source image.

Warm cream ground (Meridian paper), a green line over a soft green area fill, a
value label at every year-end, and the current year (2025) called out in gold as
a fresh record high. Source line only. Run with python3.13.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "autoloan-debt-070926.png"

# Year-end outstanding auto loan debt, $ billions (NY Fed Household Debt & Credit Report)
YEARS = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
VALS  = [1145, 1210, 1265, 1320, 1365, 1445, 1540, 1595, 1640, 1655]
CUR_IDX = len(YEARS) - 1  # 2025, the fresh record high

x = list(range(len(YEARS)))

GREEN  = "#15803d"   # deep economy green line (RE Economy palette)
FILL   = "#bbe6c8"   # soft green area fill
GOLD   = "#B08C1E"   # current year record marker (Meridian gold)
GROUND = "#FAF7F0"   # Meridian paper
INK    = "#2e2e2e"
MUTED  = "#8a8172"

Y_LO, Y_HI = 1000, 1750

fig, ax = plt.subplots(figsize=(12, 6.4))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

# soft area under the line
ax.fill_between(x, VALS, Y_LO, color=FILL, alpha=0.55, zorder=1)
# the trend line
ax.plot(x, VALS, color=GREEN, linewidth=3.4, zorder=3, solid_capstyle="round")

# markers: green history dots, gold record dot for 2025
ax.scatter(x[:-1], VALS[:-1], s=70, color=GROUND, edgecolors=GREEN,
           linewidths=2.6, zorder=4)
ax.scatter([x[CUR_IDX]], [VALS[CUR_IDX]], s=150, color=GOLD, edgecolors=GROUND,
           linewidths=2.4, zorder=5)

# value labels above each point
for xi, v in zip(x, VALS):
    ax.text(xi, v + 20, f"${v:,}", ha="center", va="bottom",
            fontsize=12.5, fontweight="bold",
            color=(GOLD if xi == CUR_IDX else INK))

# record-high callout on 2025
ax.annotate("Record high", xy=(x[CUR_IDX], VALS[CUR_IDX]),
            xytext=(x[CUR_IDX] - 1.15, VALS[CUR_IDX] - 95),
            fontsize=12.5, fontweight="bold", color=GOLD, ha="center",
            arrowprops=dict(arrowstyle="-", color=GOLD, linewidth=1.6))

# titles
ax.set_title("Outstanding Auto Loan Debt", fontsize=23,
             fontweight="bold", color=INK, loc="center", pad=26)
ax.text(0.5, 1.015, "$ billions, year-end balance",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="center")

# axes cosmetics
ax.set_xticks(x)
ax.set_xticklabels([str(y) for y in YEARS], fontsize=12.5, fontweight="bold", color=INK)
for i, lbl in enumerate(ax.get_xticklabels()):
    lbl.set_color(GOLD if i == CUR_IDX else INK)
ax.set_ylim(Y_LO, Y_HI)
ax.set_yticks([1000, 1150, 1300, 1450, 1600, 1750])
ax.set_yticklabels(["$1,000", "$1,150", "$1,300", "$1,450", "$1,600", "$1,750"],
                   fontsize=12, color=MUTED)
ax.tick_params(axis="both", length=0)
ax.grid(axis="y", color="#e7ddc9", linewidth=1.0, zorder=0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#d8cbb0")
ax.set_xlim(-0.5, len(YEARS) - 0.5)

fig.text(0.012, 0.012, "Source: NY Fed Household Debt & Credit Report",
         fontsize=10, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.075, right=0.975, top=0.84, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT)
