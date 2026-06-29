#!/usr/bin/env python3
"""
make-aluminum-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "Aluminum Prices 2026" graphic for the
06/29/26 daily email. This is OUR OWN branded chart, not the source image: a clean
RE-branded steel-blue theme on white, the YTD shape faithfully reproduced (a choppy
winter near $3.0-3.2K, a late-Feb low near $3,030, a strong spring run up to a
mid-June peak near $3,750, then the recent sharp slide), a $3,000 reference line,
and a "today" marker at $3,175.62 (+9.6% YTD).

Story (Market Briefs "⚡️ Shorting out." / "Aluminum Slides Again", 06/29/26):
aluminum just notched its fourth straight weekly drop, falling 6.4% in the last
week alone, as a possible Mideast ceasefire looks set to restart regional supply.
Cheaper aluminum could mean cheaper cans, cars, and construction, but only if the
peace holds.

matplotlib only. On this VPS run with plain python3 (3.12 has matplotlib 3.6).
"""
import sys
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

OUT = sys.argv[1] if len(sys.argv) > 1 else "aluminum-slides-again-062926.png"

# (date, price USD/metric ton) — anchors recreating the source's YTD shape:
# a choppy winter ($2.9-3.27K), a late-Feb YTD low ~$3,030, a strong spring run up
# to a mid-June peak ~$3,750, then a sharp four-week slide ending at $3,175.62
# (+9.6% YTD; Jan base ~$2,898 makes the YTD math honest).
SERIES = [
    (date(2026, 1, 2),  2898),   # YTD base (+9.6% to today)
    (date(2026, 1, 9),  3030),
    (date(2026, 1, 16), 3190),   # first peak
    (date(2026, 1, 23), 3110),
    (date(2026, 1, 30), 3180),
    (date(2026, 2, 6),  3270),   # Feb peak
    (date(2026, 2, 13), 3150),
    (date(2026, 2, 20), 3060),
    (date(2026, 2, 27), 3030),   # YTD low
    (date(2026, 3, 6),  3090),
    (date(2026, 3, 13), 3170),
    (date(2026, 3, 20), 3260),
    (date(2026, 3, 27), 3400),
    (date(2026, 4, 3),  3520),   # April peak
    (date(2026, 4, 10), 3430),
    (date(2026, 4, 14), 3360),   # dip
    (date(2026, 4, 21), 3470),
    (date(2026, 4, 28), 3520),
    (date(2026, 5, 4),  3600),
    (date(2026, 5, 8),  3650),   # mid-May peak
    (date(2026, 5, 12), 3560),
    (date(2026, 5, 15), 3480),   # dip
    (date(2026, 5, 22), 3600),
    (date(2026, 5, 26), 3660),   # late-May peak
    (date(2026, 5, 29), 3600),
    (date(2026, 6, 2),  3640),
    (date(2026, 6, 5),  3660),
    (date(2026, 6, 9),  3700),
    (date(2026, 6, 12), 3750),   # June peak / YTD high
    (date(2026, 6, 16), 3680),
    (date(2026, 6, 19), 3560),
    (date(2026, 6, 22), 3540),
    (date(2026, 6, 25), 3400),
    (date(2026, 6, 29), 3175.62),  # today ($3,175.62, +9.6% YTD)
]

xs = [d for d, _ in SERIES]
ys = [p for _, p in SERIES]

ALU    = "#5b7fa6"   # main line (steel / aluminum blue)
ALU_DK = "#3c587a"   # markers
ALU_FL = "#dde7f0"   # area fill
SLIDE  = "#b91c1c"   # the recent slide (slides again)
INK    = "#1f2937"
MUTED  = "#64748b"

fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# area + line
ax.fill_between(xs, ys, 2850, color=ALU_FL, alpha=0.9, zorder=1)
ax.plot(xs, ys, color=ALU, linewidth=3.2, zorder=3, solid_capstyle="round")
ax.plot(xs, ys, marker="o", linestyle="none", color=ALU_DK, markersize=4.0, zorder=4)

# $3,000 reference line
ax.axhline(3000, color="#dc2626", linewidth=1.4, linestyle=(0, (6, 5)), alpha=0.7, zorder=2)
ax.text(date(2026, 1, 3), 3012, "$3,000", color="#dc2626", fontsize=10,
        fontweight="bold", va="bottom", ha="left")

# highlight the recent slide (June peak -> today) = slides again
tail = SERIES[-6:]
ax.plot([d for d, _ in tail], [p for _, p in tail], color=SLIDE,
        linewidth=3.4, zorder=5, solid_capstyle="round")

# today marker + label
ax.plot([xs[-1]], [ys[-1]], marker="o", color="white", markeredgecolor=ALU_DK,
        markeredgewidth=2, markersize=11, zorder=6)
ax.annotate("Jun 29\n$3,175.62  (+9.6% YTD)",
            xy=(xs[-1], ys[-1]), xytext=(date(2026, 4, 18), 3120),
            fontsize=11, fontweight="bold", color=ALU_DK, ha="left", va="center",
            arrowprops=dict(arrowstyle="->", color=ALU_DK, lw=1.5,
                            connectionstyle="arc3,rad=-0.12"))

# June high callout
ax.annotate("June high\n~$3,750",
            xy=(date(2026, 6, 12), 3750), xytext=(date(2026, 4, 26), 3760),
            fontsize=10.5, fontweight="bold", color=MUTED, ha="center", va="center",
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.1))

# driver callout near the slide
ax.annotate("Fourth straight weekly drop as\nMideast supply looks set to return",
            xy=(date(2026, 6, 24), 3470), xytext=(date(2026, 1, 20), 3560),
            fontsize=10.5, color=SLIDE, ha="left", va="center", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=SLIDE, lw=1.2,
                            connectionstyle="arc3,rad=0.16"))

# titles
ax.set_title("Aluminum Price in 2026 — “Sliding Again”", fontsize=21,
             fontweight="bold", color=INK, loc="left", pad=18)
ax.text(0.0, 1.02, "LME aluminum, year-to-date  (USD / metric ton)",
        transform=ax.transAxes, fontsize=12.5, color=MUTED, ha="left")

# axes cosmetics
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:,.0f}"))
ax.set_ylim(2850, 3850)
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.tick_params(axis="both", labelsize=11, colors=MUTED, length=0)
ax.grid(axis="y", color="#e5e7eb", linewidth=1.0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#cbd5e1")

# source footer (no RE authorship attribution — Harv, 06/29: do not label charts "Chart by REALTY EXPERTS")
fig.text(0.012, 0.012,
         "Source: LME aluminum, USD/metric ton",
         fontsize=9, color="#94a3b8", ha="left")

fig.subplots_adjust(left=0.085, right=0.975, top=0.86, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor="white")
plt.close(fig)
print("wrote", OUT)
