#!/usr/bin/env python3
"""
make-aipoll-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the Market Briefs reader poll graphic
("How often do you use AI?") Harv supplied for the 07/27/26 daily email. OUR OWN
branded chart, not the source image: warm cream ground, horizontal bars in
frequency order (Daily to never), with the "I don't use AI" holdouts called out
in a contrasting teal so the split reads instantly.

Story tie-in (Market Briefs, 07/27/26): the newsletter published its reader poll
results, and roughly 8 in 10 readers now use AI at least weekly. Paired with the
"Old Bones" story about AI wealth reshaping collectibles markets, it lands in the
Economy section as a read on how fast the technology is being adopted.

Bars are kept in logical frequency order (Daily, Weekly, Monthly, I don't use AI)
rather than sorted by size, because the order itself carries the meaning.

Data: Market Briefs reader poll, transcribed faithfully from the source graphic
Harv provided. Shares sum to 98.1% in the source (rounding).

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "aipoll-072726.png"

# (answer, share of respondents %) - faithful to the Market Briefs source graphic,
# kept in frequency order rather than ranked by size.
DATA = [
    ("Daily",          63.3),
    ("Weekly",         18.1),
    ("Monthly",         2.8),
    ("I don't use AI", 13.9),
]

AMBER    = "#f59e0b"   # uses AI
AMBER_DK = "#d97706"   # Daily, the dominant answer
TEAL     = "#0d9488"   # the holdouts
INK      = "#12263f"
MUTED    = "#6b7280"
GROUND   = "#fdf6e8"   # warm cream (house style)

labels = [s for s, _ in DATA]
vals   = [v for _, v in DATA]
y = list(range(len(DATA)))[::-1]   # barh draws bottom-up

fig, ax = plt.subplots(figsize=(12, 6.2))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

colors = []
for s in labels:
    if s == "I don't use AI":
        colors.append(TEAL)
    elif s == "Daily":
        colors.append(AMBER_DK)
    else:
        colors.append(AMBER)

ax.barh(y, vals, height=0.58, color=colors, zorder=3,
        edgecolor=GROUND, linewidth=1.5)

for yi, v, s in zip(y, vals, labels):
    # label sits to the LEFT of the axis, value at the end of the bar
    ax.text(-1.2, yi, s, fontsize=15, fontweight="bold", color=INK,
            ha="right", va="center", zorder=4)
    ax.text(v + 1.2, yi, f"{v}%", fontsize=18, fontweight="bold",
            color=TEAL if s == "I don't use AI" else AMBER_DK,
            ha="left", va="center", zorder=4)

ax.set_xlim(0, 78)
ax.set_ylim(-0.7, len(DATA) - 0.3)
ax.set_yticks([])
ax.set_xticks([])
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("How Often Do You Use AI?", fontsize=25, fontweight="bold",
             color=INK, loc="left", x=-0.145, pad=26)
ax.text(-0.145, 1.03,
        "Share of Market Briefs readers, by how often they use AI",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="left")

fig.text(0.012, 0.014, "Source: Market Briefs reader poll", fontsize=9.5,
         color="#a99f88", ha="left")

fig.subplots_adjust(left=0.155, right=0.985, top=0.83, bottom=0.075)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, "| bars:", len(DATA), "| uses AI at least weekly:",
      f"{vals[0] + vals[1]:.1f}%")
