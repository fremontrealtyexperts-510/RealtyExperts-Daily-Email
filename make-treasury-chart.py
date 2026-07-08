#!/usr/bin/env python3
"""
make-treasury-chart.py  [out.png]

REALTY EXPERTS branded recreation of the "U.S. 10-Year Treasury: 12 Month View"
bar chart for the 07/08/26 daily email (Market Briefs "Deja vu"). OUR OWN branded
chart, not the source image.

Warm cream ground (Meridian paper), blue bars, the current month (July) in gold,
value labels above each bar, and a zoomed y-axis so the monthly yield swings read
clearly (standard for a rate chart). Source line only. Run with python3.13.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "treasury-10yr-070826.png"

# Trailing 12 months, monthly 10-year Treasury yield (%). Current month (July) = 4.45,
# matching today's reading; June dip 4.38, spring peak 4.65.
MONTHS = ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan",
          "Feb", "Mar", "Apr", "May", "Jun", "Jul"]
VALS   = [4.24, 4.13, 4.02, 3.97, 4.05, 4.16,
          4.27, 4.46, 4.65, 4.46, 4.38, 4.45]
CUR_IDX = 11  # July, the current reading

x = list(range(len(MONTHS)))

BLUE   = "#93c5fd"   # light blue history bars (faithful to source)
GOLD   = "#B08C1E"   # current month stands out (Meridian gold)
GROUND = "#FAF7F0"   # Meridian paper
INK    = "#2e2e2e"
MUTED  = "#8a8172"

Y_LO, Y_HI = 3.8, 4.8  # zoomed axis so yield swings are visible (bars sit on 3.8)

fig, ax = plt.subplots(figsize=(12, 6.4))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

colors = [BLUE] * len(MONTHS)
colors[CUR_IDX] = GOLD
ax.bar(x, VALS, width=0.68, color=colors, zorder=3)

# value labels above each bar
for xi, v in zip(x, VALS):
    ax.text(xi, v + 0.012, f"{v:.2f}", ha="center", va="bottom",
            fontsize=13, fontweight="bold",
            color=(GOLD if xi == CUR_IDX else INK))

# titles
ax.set_title("U.S. 10-Year Treasury Yield", fontsize=23,
             fontweight="bold", color=INK, loc="center", pad=26)
ax.text(0.5, 1.015, "Trailing 12-month view, monthly (%)",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="center")

# axes cosmetics (zoomed)
ax.set_xticks(x)
ax.set_xticklabels(MONTHS, fontsize=12.5, fontweight="bold", color=INK)
for i, lbl in enumerate(ax.get_xticklabels()):
    lbl.set_color(GOLD if i == CUR_IDX else INK)
ax.set_ylim(Y_LO, Y_HI)
ax.set_yticks([3.8, 4.0, 4.2, 4.4, 4.6, 4.8])
ax.set_yticklabels(["3.8", "4.0", "4.2", "4.4", "4.6", "4.8"], fontsize=12, color=MUTED)
ax.tick_params(axis="both", length=0)
ax.grid(axis="y", color="#e7ddc9", linewidth=1.0, zorder=0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#d8cbb0")
ax.set_xlim(-0.6, len(MONTHS) - 0.4)

fig.text(0.012, 0.012, "Source: U.S. Treasury", fontsize=10, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.06, right=0.975, top=0.84, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT)
