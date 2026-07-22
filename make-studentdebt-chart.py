#!/usr/bin/env python3
"""
make-studentdebt-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "Historic Total National Student Loan
Debt (in trillions)" line chart Harv supplied for the 07/22/26 daily email. OUR
OWN branded chart, not the source image: warm cream ground, an Economy-green
line over a soft fill, dotted markers on every year, and clean callouts on the
2006 start, the first year above $1 trillion (2012), and the 2025 latest.

Story tie-in (Market Briefs "New Record", 07/22/26): a record 9.5 million
federal student loan borrowers are now in default after the pandemic payment
pause ended and income-driven plans were cut, and about a third of the balance
(~$675B) is held by borrowers aged 35 to 49. The debt itself has roughly tripled
in a generation, which is why it lands in the Economy section as a household
balance-sheet story that touches every would-be buyer.

Data: Education Data Initiative / U.S. Federal Reserve total outstanding student
loan debt, Q4 each year 2006 to 2025 (in trillions), transcribed faithfully from
the source graphic Harv provided.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "studentdebt-072226.png"

# (year, $ trillions) - faithful to the source graphic (Education Data Initiative
# / U.S. Federal Reserve), totals as of each year's fourth fiscal quarter.
SERIES = [
    (2006, 0.52), (2007, 0.59), (2008, 0.68), (2009, 0.77), (2010, 0.86),
    (2011, 0.96), (2012, 1.05), (2013, 1.15), (2014, 1.24), (2015, 1.32),
    (2016, 1.41), (2017, 1.49), (2018, 1.57), (2019, 1.64), (2020, 1.69),
    (2021, 1.73), (2022, 1.76), (2023, 1.73), (2024, 1.78), (2025, 1.83),
]
years = [y for y, _ in SERIES]
vals  = [v for _, v in SERIES]

GREEN    = "#16a34a"   # Economy section green
GREEN_DK = "#0f7a37"
INK      = "#12263f"
MUTED    = "#6b7280"
GROUND   = "#fdf6e8"   # warm cream (house style)
GRID     = "#e7ddc9"
ACCENT   = "#b45309"   # amber for the $1T-crossing callout

fig, ax = plt.subplots(figsize=(12, 6.0))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

FLOOR = 0.4
ax.fill_between(years, vals, FLOOR, color=GREEN, alpha=0.12, zorder=2)
ax.plot(years, vals, color=GREEN_DK, linewidth=2.6, zorder=4,
        solid_joinstyle="round", solid_capstyle="round")
ax.scatter(years, vals, s=26, color=GREEN_DK, zorder=5,
           edgecolor=GROUND, linewidth=1.2)

# 2006 start
i0 = 0
ax.scatter([years[i0]], [vals[i0]], s=70, color=GREEN_DK, zorder=6,
           edgecolor=GROUND, linewidth=2.0)
ax.annotate(f"2006: ${vals[i0]:.2f}T",
            xy=(years[i0], vals[i0]), xytext=(years[i0] + 0.5, vals[i0] + 0.22),
            fontsize=11.5, fontweight="bold", color=INK, ha="left", va="center",
            arrowprops=dict(arrowstyle="->", color=INK, lw=1.2,
                            connectionstyle="arc3,rad=-0.20"))

# first year above $1 trillion (2012, $1.05T)
ic = years.index(2012)
ax.scatter([years[ic]], [vals[ic]], s=62, color=ACCENT, zorder=6,
           edgecolor=GROUND, linewidth=2.0)
ax.annotate("2012: crossed\n$1 trillion",
            xy=(years[ic], vals[ic]), xytext=(years[ic] - 0.3, vals[ic] + 0.34),
            fontsize=11, fontweight="bold", color=ACCENT, ha="center", va="center",
            arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.4,
                            connectionstyle="arc3,rad=0.20"))

# 2025 latest
iL = len(years) - 1
ax.scatter([years[iL]], [vals[iL]], s=100, color=GREEN_DK, zorder=6,
           edgecolor=GROUND, linewidth=2.2)
ax.annotate(f"2025: ${vals[iL]:.2f}T\nabout 3.5x the 2006 total",
            xy=(years[iL], vals[iL]), xytext=(years[iL] - 0.4, vals[iL] - 0.30),
            fontsize=12.5, fontweight="bold", color=GREEN_DK, ha="right", va="center",
            arrowprops=dict(arrowstyle="->", color=GREEN_DK, lw=1.7,
                            connectionstyle="arc3,rad=0.30"))

ax.set_ylim(FLOOR, 2.05)
ax.set_yticks([0.5, 1.0, 1.5, 2.0])
ax.set_yticklabels(["$0.5T", "$1.0T", "$1.5T", "$2.0T"])
ax.set_xticks([2006, 2009, 2012, 2015, 2018, 2021, 2025])
ax.tick_params(axis="y", labelsize=11.5, colors=MUTED, length=0)
ax.tick_params(axis="x", labelsize=12, colors=INK, length=0)
for lbl in ax.get_xticklabels():
    lbl.set_fontweight("bold")
ax.grid(axis="y", color=GRID, linewidth=1.0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#d8cbb0")

ax.set_title("Total U.S. Student Loan Debt Keeps Climbing", fontsize=24,
             fontweight="bold", color=INK, loc="left", pad=26)
ax.text(0.0, 1.03,
        "Total outstanding balance, in trillions  (Q4 each year, 2006 to 2025)",
        transform=ax.transAxes, fontsize=12.5, color=MUTED, ha="left")

fig.text(0.012, 0.014,
         "Source: Education Data Initiative; U.S. Federal Reserve. Totals as of "
         "each year's fourth fiscal quarter.",
         fontsize=9, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.062, right=0.975, top=0.84, bottom=0.11)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, "| points:", len(SERIES),
      f"| 2006 ${vals[0]:.2f}T -> 2025 ${vals[-1]:.2f}T | x{vals[-1]/vals[0]:.2f}")
