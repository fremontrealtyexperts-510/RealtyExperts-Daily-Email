#!/usr/bin/env python3
"""
make-mostvaluable-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "5 Most Valuable Companies on Earth"
graphic Harv supplied for the 07/29/26 daily email. OUR OWN branded chart, not
the source image: warm cream ground, ranked horizontal bars with each ticker
called out, Apple highlighted as the new leader, and a dashed $5T reference line
so the milestone in the story is visible.

Company logos in the source graphic are deliberately NOT reproduced (they are
trademarks); the bars carry a per-company accent color and the ticker instead.

Story tie-in (Market Briefs, 07/29/26): Apple became only the second company ever
to reach $5 trillion in value and is now the most valuable public company on
Earth, overtaking Nvidia. It lands in the Stocks section.

Data: market capitalization as of July 28, 2026, transcribed faithfully from the
source graphic Harv provided.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "mostvaluable-072926.png"

# (company, ticker, market cap $T, accent) - faithful to the source graphic.
DATA = [
    ("Apple",     "AAPL", 4.994, "#4b5563"),
    ("NVIDIA",    "NVDA", 4.771, "#65a30d"),
    ("Alphabet",  "GOOG", 4.067, "#2563eb"),
    ("Microsoft", "MSFT", 2.921, "#0891b2"),
    ("Amazon",    "AMZN", 2.483, "#ea9010"),
]
DATA = sorted(DATA, key=lambda r: r[2], reverse=True)
MILESTONE = 5.0   # the $5T mark Apple just touched

INK    = "#12263f"
MUTED  = "#6b7280"
GROUND = "#fdf6e8"   # warm cream (house style)

names  = [r[0] for r in DATA]
tick   = [r[1] for r in DATA]
vals   = [r[2] for r in DATA]
colors = [r[3] for r in DATA]
y = list(range(len(DATA)))[::-1]   # barh draws bottom-up

fig, ax = plt.subplots(figsize=(12, 6.4))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.barh(y, vals, height=0.6, color=colors, zorder=3, edgecolor=GROUND,
        linewidth=1.5)

# $5 trillion milestone marker
ax.axvline(MILESTONE, color="#9ca3af", linewidth=1.3, linestyle=(0, (5, 4)),
           zorder=2)
ax.text(MILESTONE + 0.03, y[0] + 0.52, "$5T", fontsize=11.5, fontweight="bold",
        color=MUTED, ha="left", va="center")

for yi, v, nm, tk, c in zip(y, vals, names, tick, colors):
    ax.text(-0.06, yi + 0.10, nm, fontsize=15, fontweight="bold", color=INK,
            ha="right", va="center", zorder=4)
    ax.text(-0.06, yi - 0.19, tk, fontsize=10.5, fontweight="bold",
            color=MUTED, ha="right", va="center", zorder=4)
    lift = 0.12 if nm == "Apple" else 0.0
    ax.text(v + 0.07, yi + lift, f"${v:.3f}T", fontsize=15.5,
            fontweight="bold", color=c, ha="left", va="center", zorder=4)
    if nm == "Apple":
        ax.text(v + 0.07, yi - 0.22, "new leader", fontsize=11,
                fontweight="bold", color=MUTED, ha="left", va="center",
                zorder=4)

ax.set_xlim(0, 6.5)
ax.set_ylim(-0.75, len(DATA) - 0.15)
ax.set_yticks([])
ax.set_xticks([])
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("The 5 Most Valuable Companies on Earth", fontsize=25,
             fontweight="bold", color=INK, loc="left", x=-0.128, pad=26)
ax.text(-0.128, 1.035, "Market capitalization, ranked",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="left")

fig.text(0.012, 0.014, "Source: Market capitalization as of July 28, 2026",
         fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.135, right=0.985, top=0.83, bottom=0.075)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, f"| bars: {len(DATA)} | leader {names[0]} ${vals[0]:.3f}T")
