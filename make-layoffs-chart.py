#!/usr/bin/env python3
"""
make-layoffs-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "Companies That Announced Layoffs in
2026" graphic (Intellizence) Harv supplied for the 07/24/26 daily email. OUR OWN
branded chart, not the source image: warm cream ground, ranked slate-blue
horizontal bars by announced job cuts, Volkswagen highlighted as the largest cut.

Story tie-in (Market Briefs, 07/24/26): Disney announced its third round of
layoffs this year (including 116 Pixar staff) and Albertsons warned that squeezed
shoppers are spending less. Big employers keep trimming headcount even as some
earnings beat, so a ranked look at 2026's largest announced cuts lands in the
Economy section.

Data: announced 2026 job cuts by company, transcribed faithfully from the
Intellizence source graphic Harv provided (last updated June 2026).

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "layoffs-072426.png"

# (company, announced 2026 job cuts) - faithful to the Intellizence source graphic.
DATA = [
    ("Volkswagen", 50000),
    ("UPS",        30000),
    ("Oracle",     30000),
    ("Amazon",     16000),
    ("Dell",       11000),
]
DATA = sorted(DATA, key=lambda r: r[1], reverse=True)

SLATE    = "#334155"   # ranked bars (serious / neutral)
SLATE_DK = "#1e293b"   # Volkswagen highlight (largest cut)
INK      = "#12263f"
MUTED    = "#6b7280"
GROUND   = "#fdf6e8"   # warm cream (house style)

labels = [s for s, _ in DATA]
vals   = [v for _, v in DATA]
# barh draws bottom-up, so reverse to put the biggest bar on top
y = list(range(len(DATA)))[::-1]

fig, ax = plt.subplots(figsize=(12, 6.2))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

colors = [SLATE_DK if s == "Volkswagen" else SLATE for s in labels]
bars = ax.barh(y, vals, height=0.62, color=colors, zorder=3,
               edgecolor=GROUND, linewidth=1.5)

# value labels and company names inside / at the end of each bar
for yi, v, s in zip(y, vals, labels):
    ax.text(v - 800, yi, f"{v:,}", fontsize=16, fontweight="bold",
            color=GROUND, ha="right", va="center", zorder=4)
    tag = "  (largest 2026 cut)" if s == "Volkswagen" else ""
    ax.text(900, yi, s + tag, fontsize=14.5, fontweight="bold", color=GROUND,
            ha="left", va="center", zorder=4)

ax.set_xlim(0, 55000)
ax.set_ylim(-0.7, len(DATA) - 0.3)
ax.set_yticks([])
ax.set_xticks([])
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("Companies That Announced Layoffs in 2026", fontsize=25,
             fontweight="bold", color=INK, loc="left", pad=26)
ax.text(0.0, 1.03,
        "Announced job cuts in 2026, ranked",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="left")

fig.text(0.012, 0.014, "Source: Intellizence, layoffs announced in 2026 (updated June 2026)",
         fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.02, right=0.985, top=0.83, bottom=0.075)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, "| bars:", len(DATA), "| top", labels[0], f"{vals[0]:,}")
