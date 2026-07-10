#!/usr/bin/env python3
"""
make-homeprice-chart.py  [out.png]

REALTY EXPERTS branded recreation of the "Home prices" chart for the 07/10/26
daily email (Market Briefs "Fed force"; the Record Home Prices story). OUR OWN
branded chart, not the source image.

Warm cream ground (Meridian paper), a REALTY EXPERTS orange line over a soft
orange area fill, seasonal monthly detail from 2020 to now, and the current month
(June 2026) called out as a fresh record high of $440,600. Source line only.
Run with python3.13.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "homeprice-071026.png"

# Median existing-home price, monthly ($ thousands), Jan 2020 -> Jun 2026 (NAR).
# Seasonal saw-tooth (spring/summer peaks, winter troughs). June 2026 = 440.6, a
# record high (+1.8% YoY vs 432.7), matching today's NAR report.
VALS = [
    266, 270, 280, 286, 284, 295, 305, 311, 311, 317, 311, 314,   # 2020
    305, 313, 329, 342, 350, 363, 359, 356, 352, 353, 354, 358,   # 2021
    355, 363, 383, 397, 408, 416, 404, 391, 384, 379, 370, 366,   # 2022
    359, 367, 378, 388, 396, 410, 406, 405, 399, 391, 388, 387,   # 2023
    379, 385, 394, 407, 419, 427, 422, 417, 407, 407, 407, 404,   # 2024
    397, 402, 407, 418, 426, 432.7, 424, 419, 414, 410, 405, 401, # 2025
    399, 404, 414, 427, 438, 440.6,                                # 2026 (Jun record)
]
CUR_IDX = len(VALS) - 1  # June 2026, the record high
x = list(range(len(VALS)))

ORANGE = "#ea580c"   # REALTY EXPERTS real-estate orange
FILL   = "#fbdcc4"   # soft orange area fill
GOLD   = "#B08C1E"   # record marker (Meridian gold)
GROUND = "#FAF7F0"   # Meridian paper
INK    = "#2e2e2e"
MUTED  = "#8a8172"

Y_LO, Y_HI = 250, 460

fig, ax = plt.subplots(figsize=(12, 6.4))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.fill_between(x, VALS, Y_LO, color=FILL, alpha=0.7, zorder=1)
ax.plot(x, VALS, color=ORANGE, linewidth=2.8, zorder=3, solid_capstyle="round")

# record marker on June 2026
ax.scatter([x[CUR_IDX]], [VALS[CUR_IDX]], s=150, color=GOLD, edgecolors=GROUND,
           linewidths=2.4, zorder=5)

# callout box for the record
ax.annotate("Jun 2026\n$440,600", xy=(x[CUR_IDX], VALS[CUR_IDX]),
            xytext=(x[CUR_IDX] - 9.5, VALS[CUR_IDX] + 2),
            fontsize=13.5, fontweight="bold", color="white", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.5", fc=GOLD, ec="none"),
            zorder=6)

# titles
ax.set_title("Home Prices", fontsize=24, fontweight="bold", color=INK,
             loc="left", x=0.012, pad=26)
ax.text(0.012, 1.02, "Median existing-home price, monthly (record high in June)",
        transform=ax.transAxes, fontsize=13.5, color=MUTED, ha="left")

# axes cosmetics: year ticks at each January
year_ticks = list(range(0, len(VALS), 12))
ax.set_xticks(year_ticks)
ax.set_xticklabels([str(2020 + i) for i in range(len(year_ticks))],
                   fontsize=12.5, fontweight="bold", color=INK)
ax.set_ylim(Y_LO, Y_HI)
ax.set_yticks([250, 300, 350, 400, 450])
ax.set_yticklabels(["$250K", "$300K", "$350K", "$400K", "$450K"], fontsize=12, color=MUTED)
ax.tick_params(axis="both", length=0)
ax.grid(axis="y", color="#e7ddc9", linewidth=1.0, zorder=0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#d8cbb0")
ax.set_xlim(-1, len(VALS))

fig.text(0.012, 0.012, "Source: National Association of Realtors",
         fontsize=10, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.075, right=0.975, top=0.83, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT)
