#!/usr/bin/env python3
"""
make-nahb-chart.py  [out.png]

Recreates the Market Briefs "US NAHB Housing Market Index" bar chart for the
06/16/26 daily email ("Builders Stay Gloomy" story — homebuilder confidence
fell to 35 in June, its longest slump since 2012, under 40 for 14 months).

CONTENT IS IDENTICAL to the source graphic (same 9 monthly readings, same
labels, same title/source) — only the styling is our own (clean light theme,
REALTY EXPERTS branding, RE-section orange). Do not change the values.

  Oct 37 · Nov 38 · Dec 39 · Jan(2026) 37 · Feb 37 · Mar 38 · Apr 34 · May 37 · Jun 35

No external deps beyond matplotlib (already used by mls-csv-to-images.py).
Run with python3.13 (the interpreter that has matplotlib on this Mac).
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "nahb-housing-index-061626.png"

# (x-label, value) — labels match the source exactly (the Jan bar is shown as "2026")
SERIES = [
    ("Oct", 37), ("Nov", 38), ("Dec", 39), ("2026", 37), ("Feb", 37),
    ("Mar", 38), ("Apr", 34), ("May", 37), ("Jun", 35),
]
labels = [s[0] for s in SERIES]
vals = [s[1] for s in SERIES]

ORANGE = "#ea580c"       # RE-section orange (matches the daily email)
ORANGE_LT = "#f59e63"    # lighter fill for prior months
INK = "#1f2937"
MUTED = "#64748b"
GRID = "#e5e7eb"

# emphasize the latest reading (Jun 35) so the current month reads at a glance
colors = [ORANGE_LT] * len(vals)
colors[-1] = ORANGE

fig, ax = plt.subplots(figsize=(11, 5.6))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

bars = ax.bar(range(len(vals)), vals, width=0.66, color=colors, zorder=3)

# value labels on top of each bar
for i, v in enumerate(vals):
    ax.text(i, v + 0.18, str(v), ha="center", va="bottom",
            fontsize=15, fontweight="bold",
            color=INK if i == len(vals) - 1 else MUTED)

# baseline cut so small differences read (index hovers 34-39)
ax.set_ylim(32, 40.5)
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, fontsize=13, fontweight="bold", color=INK)
ax.set_yticks([33, 34, 35, 36, 37, 38, 39])
ax.tick_params(axis="y", labelsize=10, colors=MUTED, length=0)
ax.tick_params(axis="x", length=0)
ax.grid(axis="y", color=GRID, linewidth=1.0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#cbd5e1")

# titles
ax.set_title("US NAHB Housing Market Index", fontsize=23, fontweight="bold",
             color=INK, loc="left", pad=30)
ax.text(0.0, 1.045, "Homebuilder sentiment, last 9 months",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="left")

# source + branding footer
fig.text(0.012, 0.015,
         "Source: National Association of Home Builders (NAHB)  ·  "
         "REALTY EXPERTS® · TeamRealtyExperts.com",
         fontsize=9, color="#94a3b8", ha="left")

fig.subplots_adjust(left=0.055, right=0.975, top=0.82, bottom=0.11)
fig.savefig(OUT, dpi=150, facecolor="white")
plt.close(fig)
print("wrote", OUT)
