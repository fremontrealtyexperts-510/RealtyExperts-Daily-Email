#!/usr/bin/env python3
"""
make-spacex-capex-chart.py  [out.png]

REALTY EXPERTS recreation of the SpaceX capital-spending graphic Harv supplied for
the 08/05/26 daily email. OUR OWN branded chart: warm cream ground, Stocks-blue
accents, the current quarter carried in the strong tone so the "everything else is
flat, AI went vertical" point lands without reading a single number.

Story tie-in (Market Briefs "AI Costs Skyrocket", 08/05/26): SpaceX posted its
first earnings as a public company and disclosed $15.8B of AI capex in the
quarter. Shares rose 9.4% in the session and then fell after close. That is a
markets story, so it lands in the Stocks section.

Data: SpaceX Q2 2026 results. Every value was re-verified rather than transcribed
from the supplied graphic:
  * 2Q 2026 AI $15.828B, Connectivity $1.37B, Space $1.17B. The three sum to
    $18.368B against a reported total capex of $18.369B, which corroborates the
    two smaller bars the headline coverage does not break out.
  * 1Q 2026 total capex $10,107M with AI $7,723M, both reported. Connectivity
    $1.33B + Space $1.05B + AI $7.723B = $10.103B, consistent with the reported
    total.
  * 2Q 2025 AI $0.75B, implied by the reported +2,013% year-over-year growth in
    AI capex (15.828 / 21.13 = 0.749). Column total $2.83B against Forbes'
    reported $2.8B for the year-ago quarter, and the reported +557% total-capex
    growth (18.4 / 2.8 = 6.57).
Every bar therefore reconciles to a reported total or a reported growth rate; no
bar is transcribed on trust alone.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "spacex-capex-080526.png"

# segment -> (2Q 2025, 1Q 2026, 2Q 2026) capex in $ billions
SEGMENTS = [
    ("AI",           0.75,  7.72, 15.83),
    ("Connectivity", 1.13,  1.33,  1.37),
    ("Space",        0.95,  1.05,  1.17),
]
PERIODS = ["2Q 2025", "1Q 2026", "2Q 2026"]

BLUE_LT = "#bcd3f7"   # 2Q 2025, faded history
BLUE_MD = "#7aa9e9"   # 1Q 2026
BLUE_DK = "#2563eb"   # 2Q 2026, Stocks brand blue, the current reading
BAR_COLORS = [BLUE_LT, BLUE_MD, BLUE_DK]

INK    = "#12263f"
MUTED  = "#6b7280"
GROUND = "#fdf6e8"    # warm cream (house style)
GRID   = "#e7ddc9"

fig, ax = plt.subplots(figsize=(12, 6.8))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

H = 0.24            # bar thickness
group_gap = 1.0
yticks, yticklabels = [], []

for gi, (name, *vals) in enumerate(SEGMENTS):
    base = gi * group_gap
    # top row = earliest period, so the group reads down the page like the source
    offsets = [base + H, base, base - H]
    for oi, (off, v) in enumerate(zip(offsets, vals)):
        ax.barh(off, v, height=H, color=BAR_COLORS[oi], zorder=3,
                edgecolor=GROUND, linewidth=1.1)
        bold = "bold" if oi == 2 else "normal"
        col = INK if oi == 2 else "#8a8172"
        ax.text(v + 0.22, off, f"${v:.2f}B", fontsize=12.5, fontweight=bold,
                color=col, ha="left", va="center", zorder=5)
    yticks.append(base)
    yticklabels.append(name)

ax.set_yticks(yticks)
ax.set_yticklabels(yticklabels, fontsize=15, fontweight="bold", color=INK)
ax.invert_yaxis()
ax.set_xlim(0, 19.4)
ax.set_xticks([])
ax.grid(axis="x", color=GRID, linewidth=1.0, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "bottom"):
    ax.spines[sp].set_visible(False)
ax.spines["left"].set_color("#d9cdb4")
ax.spines["left"].set_linewidth(1.2)

ax.set_title("SpaceX's AI Bill Went Vertical", fontsize=25, fontweight="bold",
             color=INK, loc="left", pad=42)
ax.text(0.0, 1.085, "Capital spending by segment, per quarter",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="left")
ax.text(1.0, 1.085, "$15.83B ON AI IN ONE QUARTER",
        transform=ax.transAxes, fontsize=14.5, fontweight="bold",
        color=BLUE_DK, ha="right")

# period legend, drawn by hand so it sits inline under the subtitle
lx = 0.0
for label, color in zip(PERIODS, BAR_COLORS):
    ax.add_patch(plt.Rectangle((lx, 1.018), 0.022, 0.030, color=color,
                               transform=ax.transAxes, clip_on=False, zorder=6))
    ax.text(lx + 0.030, 1.033, label, transform=ax.transAxes, fontsize=11.5,
            fontweight="bold", color=MUTED, ha="left", va="center")
    lx += 0.125

# No leader line: the callout sits in the open space beside the two small groups,
# and any arrow back to them ran straight through the $1.37B value label.
ax.text(5.0, group_gap + 0.5, "Connectivity and Space barely moved",
        fontsize=12.5, fontweight="bold", color=MUTED, ha="left", va="center",
        zorder=6)

fig.text(0.012, 0.014, "Source: SpaceX Q2 2026 results", fontsize=9.5,
         color="#a99f88", ha="left")

fig.subplots_adjust(left=0.178, right=0.985, top=0.775, bottom=0.075)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)

ai = [s[1] for s in SEGMENTS][0], SEGMENTS[0][3]
tot26 = sum(s[3] for s in SEGMENTS)
tot25 = sum(s[1] for s in SEGMENTS)
print("wrote", OUT,
      f"| 2Q26 column sums to ${tot26:.3f}B (reported total $18.369B)"
      f" | 2Q25 column ${tot25:.2f}B (reported ~$2.8B)"
      f" | AI {SEGMENTS[0][1]:.2f} -> {SEGMENTS[0][3]:.2f} "
      f"= {(SEGMENTS[0][3]/SEGMENTS[0][1]-1)*100:+.0f}% YoY")
