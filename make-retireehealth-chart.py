#!/usr/bin/env python3
"""
make-retireehealth-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "A Big Jump in Projected Retiree
Healthcare Costs" graphic Harv supplied for the 07/23/26 daily email. OUR OWN
branded chart, not the source image: warm cream ground, an Economy-green line,
markers on every year, and a highlighted 2026 endpoint carrying the big jump.

Story tie-in (Market Briefs "Golden Costs", 07/23/26): a 65-year-old retiring in
2026 now faces an average of about $185,500 in lifetime medical expenses, and
the annual Fidelity estimate jumped roughly 7% this year, the biggest one-year
increase in the series. It lands in the Economy section as a household cost story.

Data: year-over-year percent change in Fidelity's annual Retiree Health Care Cost
Estimate, 2018 to 2026, transcribed faithfully from the source graphic.

No authorship label on the chart (per Harv, 06/29): footer carries only the data
source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "retireehealth-072326.png"

# (year, % change in the annual Fidelity estimate) - faithful to the source graphic.
SERIES = [
    (2018, 1.5), (2019, 1.5), (2020, 3.3), (2021, 1.5), (2022, 4.7),
    (2023, 0.0), (2024, 4.5), (2025, 4.3), (2026, 7.0),
]
years = [y for y, _ in SERIES]
vals  = [v for _, v in SERIES]

GREEN    = "#16a34a"   # Economy section green
GREEN_DK = "#0f7a37"
INK      = "#12263f"
MUTED    = "#6b7280"
GROUND   = "#fdf6e8"   # warm cream (house style)
GRID     = "#e7ddc9"

fig, ax = plt.subplots(figsize=(12, 6.0))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

FLOOR = -0.6
ax.fill_between(years, vals, FLOOR, color=GREEN, alpha=0.10, zorder=2)
ax.plot(years, vals, color=GREEN_DK, linewidth=2.8, zorder=4,
        solid_joinstyle="round", solid_capstyle="round")
ax.scatter(years[:-1], vals[:-1], s=46, color=GREEN_DK, zorder=5,
           edgecolor=GROUND, linewidth=1.6)

# per-point value labels, always above the marker so none collide with the
# x-axis year labels (2023 sits on the 0% line).
for y, v in SERIES[:-1]:
    ax.annotate(f"{v:.1f}%", xy=(y, v), xytext=(y, v + 0.55),
                fontsize=11, fontweight="bold", color=MUTED, ha="center", va="bottom")

# 2026 endpoint - the big jump
iL = len(years) - 1
ax.scatter([years[iL]], [vals[iL]], s=150, color=GREEN, zorder=6,
           edgecolor=GROUND, linewidth=2.4)
ax.annotate(f"2026: +{vals[iL]:.1f}%\nbiggest jump in the series",
            xy=(years[iL], vals[iL]), xytext=(years[iL] - 1.15, vals[iL] + 0.15),
            fontsize=12.5, fontweight="bold", color=GREEN_DK, ha="right", va="center",
            arrowprops=dict(arrowstyle="->", color=GREEN_DK, lw=1.7,
                            connectionstyle="arc3,rad=0.25"))

ax.set_ylim(FLOOR, 8.2)
ax.set_yticks([0, 2, 4, 6, 8])
ax.set_yticklabels(["0%", "2%", "4%", "6%", "8%"])
ax.set_xticks(years)
ax.tick_params(axis="y", labelsize=12, colors=MUTED, length=0)
ax.tick_params(axis="x", labelsize=12.5, colors=INK, length=0)
for lbl in ax.get_xticklabels():
    lbl.set_fontweight("bold")
ax.grid(axis="y", color=GRID, linewidth=1.0)
ax.set_axisbelow(True)
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
ax.spines["bottom"].set_color("#d8cbb0")

ax.set_title("A Big Jump in Projected Retiree Healthcare Costs", fontsize=23,
             fontweight="bold", color=INK, loc="left", pad=26)
ax.text(0.0, 1.03,
        "Year-over-year change in Fidelity's annual retiree health care cost estimate",
        transform=ax.transAxes, fontsize=12.5, color=MUTED, ha="left")

fig.text(0.012, 0.014,
         "Source: Fidelity Investments 2026 Retiree Health Care Cost Estimate. "
         "For a 65-year-old retiring in 2026; long-term care excluded.",
         fontsize=9, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.06, right=0.975, top=0.84, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, "| points:", len(SERIES), f"| 2026 +{vals[-1]:.1f}%")
