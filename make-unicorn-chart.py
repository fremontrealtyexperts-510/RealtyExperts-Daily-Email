#!/usr/bin/env python3
"""
make-unicorn-chart.py  [out.png]

REALTY EXPERTS branded recreation of the "Global New Unicorn Count" bar chart for
the 07/07/26 daily email (Market Briefs "🔔 Ring the bell." — the AI boom has
minted 90 new unicorns so far this year; a unicorn is a startup valued over $1B).
OUR OWN branded chart, not the source image.

Warm cream ground (Meridian paper), blue bars, the current-year 2026 bar
highlighted in gold with a "so far" note. Source line only (no RE authorship
label, per Harv 06/29). Run with python3.13.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "unicorn-count-070726.png"

# (year label, new unicorns created that year) — Crunchbase. 2026 is partial.
BARS = [
    ("2021", 622), ("2022", 328), ("2023", 102),
    ("2024", 117), ("2025", 187), ("2026", 90),
]
PARTIAL_IDX = 5  # 2026 is "so far"

labels = [b[0] for b in BARS]
vals   = [b[1] for b in BARS]
x = list(range(len(BARS)))

BLUE   = "#3b82f6"   # standard bars (faithful to source blue)
GOLD   = "#B08C1E"   # highlight the current year (Meridian gold)
GROUND = "#FAF7F0"   # Meridian paper
INK    = "#2e2e2e"
MUTED  = "#8a8172"

fig, ax = plt.subplots(figsize=(12, 6.6))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

colors = [BLUE] * len(BARS)
colors[PARTIAL_IDX] = GOLD  # 2026 "so far" stands out
bars = ax.bar(x, vals, width=0.62, color=colors, zorder=3)

# value labels above each bar
for xi, v in zip(x, vals):
    ax.text(xi, v + 9, f"{v}", ha="center", va="bottom",
            fontsize=16, fontweight="bold", color=INK)

# titles
ax.set_title("Global New Unicorn Count", fontsize=24,
             fontweight="bold", color=INK, loc="center", pad=26)
ax.text(0.5, 1.015, "New $1B+ startups created per year, 2021 to 2026",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="center")

# axes cosmetics
ax.set_xticks(x)
xlabels = list(labels)
xlabels[PARTIAL_IDX] = "2026\n(so far)"
ax.set_xticklabels(xlabels, fontsize=13.5, fontweight="bold", color=INK)
ax.set_ylim(0, 700)
ax.set_yticks([0, 100, 200, 300, 400, 500, 600, 700])
ax.set_yticklabels(["0", "100", "200", "300", "400", "500", "600", "700"],
                   fontsize=12, color=MUTED)
ax.tick_params(axis="both", length=0)
ax.grid(axis="y", color="#e7ddc9", linewidth=1.0, zorder=0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#d8cbb0")
ax.set_xlim(-0.6, len(BARS) - 0.4)

fig.text(0.012, 0.012, "Source: Crunchbase", fontsize=10, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.06, right=0.975, top=0.84, bottom=0.12)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT)
