#!/usr/bin/env python3
"""
make-retirement-start-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "Age People Start Saving for Retirement"
graphic (SoFi survey) for the 07/16/26 daily email. OUR OWN branded chart, not the
source image: horizontal bars on a warm cream ground, gold for the age cohorts and
a clay bar flagging the 13% who have not started at all, with the share labeled at
the end of each bar.

Story (Market Briefs "🔨 Tool toll." 07/16/26, "Short On Retirement?"): Americans say
they need $1.2M to retire, but most expect to land under $500K. Half of adults start
saving by 35; 13% never start.

matplotlib only. Build with python3.13 on Mac (matplotlib 3.10).
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "retirement-start-071626.png"

LABELS = ["Under 25", "25 to 35", "36 to 45", "46 to 55", "56 to 65", "Over 65",
          "Haven't started"]
VALUES = [17, 34, 19, 9, 6, 2, 13]

GOLD   = "#C9A227"
GOLD_D = "#B08C1E"
CLAY   = "#A65A44"
INK    = "#12263f"
MUTED  = "#6b7280"
GROUND = "#fdf6e8"
HAIR   = "#e0d6c0"

colors = [GOLD] * 6 + [CLAY]

fig, ax = plt.subplots(figsize=(12, 6.2))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ypos = list(range(len(LABELS)))[::-1]  # source order top to bottom
bars = ax.barh(ypos, VALUES, height=0.62, color=colors, zorder=3)
for y, v, c in zip(ypos, VALUES, colors):
    ax.text(v + 0.7, y, f"{v}%", va="center", ha="left",
            fontsize=13, fontweight="bold", color=INK, zorder=4)

ax.set_yticks(ypos)
ax.set_yticklabels(LABELS, fontsize=12.5, color=INK)
# emphasize the never-started row label
ax.get_yticklabels()[-1].set_color(CLAY)
ax.get_yticklabels()[-1].set_fontweight("bold")

ax.set_xlim(0, 40)
ax.set_xticks([])
ax.grid(axis="x", color=HAIR, linewidth=0.8, alpha=0.7, zorder=0)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(length=0)

ax.set_title("When Americans Start Saving For Retirement",
             fontsize=17, fontweight="bold", color=INK, loc="left", pad=30)
ax.text(0, 1.045, "Share of adults by the age they began saving. Half start by 35; 13% have not started at all.",
        transform=ax.transAxes, fontsize=10.5, color=MUTED)

fig.text(0.065, 0.025, "Source: SoFi", fontsize=8.5, color="#a99f88")
fig.tight_layout(rect=(0.01, 0.05, 0.985, 0.97))
fig.savefig(OUT, dpi=160, facecolor=GROUND)
print(f"wrote {OUT}")
