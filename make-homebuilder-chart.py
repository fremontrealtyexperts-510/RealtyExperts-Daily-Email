#!/usr/bin/env python3
"""
make-homebuilder-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "U.S. Homebuilder Confidence" graphic
(NAHB Housing Market Index, monthly) for the 07/17/26 daily email. OUR OWN
branded chart, not the source image: a warm cream ground, RE orange bars with the
latest month emphasized, a dashed floor at 34 that the April and July readings
both touch, and a year-low callout on July. Values are faithful to the source
(Aug 2025 to Jul 2026).

Story (Market Briefs "Confidence Craters", 07/17/26): homebuilder confidence fell
to 34, matching its 2024 low, as high mortgage rates, expensive land, and costly
materials squeeze buyers and builders alike. That points to fewer new homes, which
keeps prices firm for anyone looking to buy.

No authorship label on the chart (per Harv, 06/29) — footer carries only the data
source. matplotlib only; build with python3.13 on Mac (matplotlib 3.10).
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "homebuilder-confidence-071726.png"

# (month label, NAHB HMI) — faithful to the source, Aug 2025 to Jul 2026
SERIES = [
    ("Aug", 32), ("Sep", 32), ("Oct", 37), ("Nov", 38), ("Dec", 39),
    ("Jan", 37), ("Feb", 37), ("Mar", 38), ("Apr", 34), ("May", 37),
    ("Jun", 36), ("Jul", 34),
]
labels = [s[0] for s in SERIES]
vals = [s[1] for s in SERIES]

ORANGE    = "#ea580c"   # RE-section orange (latest month)
ORANGE_LT = "#f6b884"   # lighter fill for prior months
INK       = "#12263f"
MUTED     = "#6b7280"
GROUND    = "#fdf6e8"   # warm cream (house style)
GRID      = "#e7ddc9"

colors = [ORANGE_LT] * len(vals)
colors[-1] = ORANGE     # emphasize July (latest reading)

fig, ax = plt.subplots(figsize=(12, 6.0))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.bar(range(len(vals)), vals, width=0.64, color=colors, zorder=3)

# value labels atop each bar
for i, v in enumerate(vals):
    ax.text(i, v + 0.25, str(v), ha="center", va="bottom",
            fontsize=14, fontweight="bold",
            color=INK if i == len(vals) - 1 else MUTED)

# dashed floor at 34 — the April and July readings both sit on it
ax.axhline(34, color=ORANGE, linewidth=1.1, linestyle=(0, (4, 3)), alpha=0.5, zorder=2)

# callout on the latest reading
ax.annotate("Jul 2026: 34\nmatches the 2024 low",
            xy=(len(vals) - 1, 34), xytext=(len(vals) - 3.7, 26.6),
            fontsize=12, fontweight="bold", color=ORANGE, ha="center", va="center",
            arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.6,
                            connectionstyle="arc3,rad=0.22"))

ax.set_ylim(20, 42)
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, fontsize=12.5, fontweight="bold", color=INK)
ax.set_yticks([20, 25, 30, 35, 40])
ax.tick_params(axis="y", labelsize=10.5, colors=MUTED, length=0)
ax.tick_params(axis="x", length=0)
ax.grid(axis="y", color=GRID, linewidth=1.0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#d8cbb0")

ax.set_title("U.S. Homebuilder Confidence", fontsize=24, fontweight="bold",
             color=INK, loc="left", pad=26)
ax.text(0.0, 1.03, "NAHB Housing Market Index, monthly  (Aug 2025 to Jul 2026)",
        transform=ax.transAxes, fontsize=12.5, color=MUTED, ha="left")

fig.text(0.012, 0.014, "Source: National Association of Home Builders (NAHB)",
         fontsize=9, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.055, right=0.975, top=0.84, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT)
