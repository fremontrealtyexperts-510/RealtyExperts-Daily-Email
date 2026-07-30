#!/usr/bin/env python3
"""
make-fedrate-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "Fed Interest Rates Over Time" graphic
Harv supplied for the 07/30/26 daily email. OUR OWN branded chart, not the source
image: warm Meridian cream ground, a gold rate line with a soft fill, the three
turning points of the decade flagged (the 2020 cut to zero, the 2023 peak at
5.33%, and today's hold), and the current rate called out in a pill.

Story tie-in (Market Briefs, 07/30/26, "Warsh Waits"): Fed Chairman Kevin Warsh
and the committee held rates unchanged. Three officials wanted a hike, and the
odds of a September hike now sit near 70%, which feeds straight into mortgage
rates and auto loans. The decade long path lands in the Economy section.

Data: Federal Reserve Economic Data (FRED) series FEDFUNDS, federal funds
effective rate, monthly, July 2016 through June 2026 (the latest published
month). Pulled live from the keyless endpoint
https://fred.stlouisfed.org/graph/fredgraph.csv?id=FEDFUNDS and frozen below so
the chart is reproducible.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "fedrate-073026.png"

# FRED FEDFUNDS, monthly, 2016-07 through 2026-06 (120 points).
RATES = [
    0.39, 0.4, 0.4, 0.4, 0.41, 0.54, 0.65, 0.66, 0.79, 0.9, 0.91, 1.04, 1.15, 1.16, 1.15,
    1.15, 1.16, 1.3, 1.41, 1.42, 1.51, 1.69, 1.7, 1.82, 1.91, 1.91, 1.95, 2.19, 2.2, 2.27,
    2.4, 2.4, 2.41, 2.42, 2.39, 2.38, 2.4, 2.13, 2.04, 1.83, 1.55, 1.55, 1.55, 1.58, 0.65,
    0.05, 0.05, 0.08, 0.09, 0.1, 0.09, 0.09, 0.09, 0.09, 0.09, 0.08, 0.07, 0.07, 0.06,
    0.08, 0.1, 0.09, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.2, 0.33, 0.77, 1.21, 1.68, 2.33,
    2.56, 3.08, 3.78, 4.1, 4.33, 4.57, 4.65, 4.83, 5.06, 5.08, 5.12, 5.33, 5.33, 5.33,
    5.33, 5.33, 5.33, 5.33, 5.33, 5.33, 5.33, 5.33, 5.33, 5.33, 5.13, 4.83, 4.64, 4.48,
    4.33, 4.33, 4.33, 4.33, 4.33, 4.33, 4.33, 4.33, 4.22, 4.09, 3.88, 3.72, 3.64, 3.64,
    3.64, 3.64, 3.63, 3.63,
]
START_YEAR, START_MONTH = 2016, 7      # first point is July 2016
CURRENT = RATES[-1]                    # 3.63%

# index of January for each year label on the axis
YEAR_TICKS = [((y - START_YEAR) * 12 + (1 - START_MONTH), str(y))
              for y in range(2017, 2027)]

GOLD    = "#B08C1E"   # Meridian gold
GOLD_D  = "#8a6d13"
GROUND  = "#FAF7F0"   # Meridian paper
INK     = "#2e2e2e"
MUTED   = "#8a8172"
GRID    = "#e7ddc9"

x = list(range(len(RATES)))

fig, ax = plt.subplots(figsize=(12, 6.4))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.plot(x, RATES, color=GOLD, linewidth=2.8, zorder=4, solid_capstyle="round")
ax.fill_between(x, RATES, 0, color=GOLD, alpha=0.13, zorder=2)

# --- turning points of the decade -------------------------------------------
covid_i = RATES.index(min(RATES))              # spring 2020, effectively zero
peak_i = RATES.index(max(RATES))               # first month at the 5.33% plateau

ax.plot([covid_i], [RATES[covid_i]], "o", color=GOLD_D, markersize=7, zorder=5)
ax.annotate("2020: cut to near zero",
            xy=(covid_i, RATES[covid_i]), xytext=(covid_i - 28, 0.58),
            fontsize=11.5, fontweight="bold", color=GOLD_D, zorder=6)

ax.plot([peak_i], [RATES[peak_i]], "o", color=GOLD_D, markersize=7, zorder=5)
ax.annotate(f"2023 peak  {RATES[peak_i]:.2f}%",
            xy=(peak_i, RATES[peak_i]), xytext=(peak_i - 15, RATES[peak_i] + 0.42),
            fontsize=12, fontweight="bold", color=GOLD_D, zorder=6)

# current rate pill
ax.plot([x[-1]], [CURRENT], "o", color=GOLD_D, markersize=8, zorder=6)
ax.annotate(f"{CURRENT:.2f}%", xy=(x[-1], CURRENT), xytext=(x[-1] + 2.2, CURRENT),
            fontsize=15, fontweight="bold", color="white", va="center", zorder=7,
            bbox=dict(boxstyle="round,pad=0.42", facecolor=GOLD_D, edgecolor="none"))

ax.set_xlim(-1.5, len(RATES) + 12)
ax.set_ylim(0, 6.15)
ax.set_yticks([0, 1, 2, 3, 4, 5, 6])
ax.set_yticklabels(["0%", "1%", "2%", "3%", "4%", "5%", "6%"],
                   fontsize=12, color=MUTED)
ax.set_xticks([i for i, _ in YEAR_TICKS])
ax.set_xticklabels([lbl for _, lbl in YEAR_TICKS], fontsize=12.5,
                   fontweight="bold", color=MUTED)
ax.grid(axis="y", color=GRID, linewidth=1.1, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
ax.spines["bottom"].set_color("#d8cbb0")
ax.set_axisbelow(True)

ax.set_title("The Fed Holds At 3.63%", fontsize=25, fontweight="bold",
             color=INK, loc="left", pad=30)
ax.text(0.0, 1.045, "Federal funds effective rate, monthly, past 10 years",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="left")
ax.text(1.0, 1.045, "NO CHANGE THIS MEETING",
        transform=ax.transAxes, fontsize=14.5, fontweight="bold",
        color=GOLD_D, ha="right")

fig.text(0.012, 0.014,
         "Source: Federal Reserve Economic Data (FRED), federal funds effective rate, monthly through June 2026.",
         fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.058, right=0.985, top=0.82, bottom=0.085)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT,
      f"| months: {len(RATES)} | current {CURRENT:.2f}% | peak {max(RATES):.2f}% | low {min(RATES):.2f}%")
