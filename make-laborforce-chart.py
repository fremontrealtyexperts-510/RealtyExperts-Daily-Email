#!/usr/bin/env python3
"""
make-laborforce-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "U.S. Labor Force Participation Rate"
(FRED CIVPART) graphic for the 07/13/26 daily email. OUR OWN branded chart, not
the source image: a clean RE steel-blue theme on a warm cream ground, the source
shape faithfully reproduced (a choppy 2021-22 climb, a plateau near a post-COVID
high through 2023-24, then a sharp recent slide to 61.5%), a "today" marker at the
latest reading, and a callout tying it to this week's story.

Story (Market Briefs "Workers Wait It Out", 07/13/26): more people are leaving the
job market than finding work. About 720,000 people stopped looking for work in June,
which also pulled the headline unemployment rate lower. Fewer people participating
means a tighter, more competitive market for anyone who is still looking.

matplotlib only. Build with python3.13 on Mac (matplotlib 3.10).
"""
import sys
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

OUT = sys.argv[1] if len(sys.argv) > 1 else "laborforce-071326.png"

# (date, participation rate %) — monthly anchors recreating the source's shape:
# a low, choppy start near 61.6 through late 2021, a climb into 2022 that dips back
# to ~62.1 by mid-2022, a step up to a plateau near a post-COVID high of ~62.8 in
# 2023, a broad 62.5-62.7 plateau through 2024, and then a sharp 2025-26 slide that
# breaks below the range down to 61.5% today.
SERIES = [
    (date(2021, 7, 1), 61.67), (date(2021, 8, 1), 61.62), (date(2021, 9, 1), 61.70),
    (date(2021, 10, 1), 61.92), (date(2021, 11, 1), 62.28), (date(2021, 12, 1), 62.18),
    (date(2022, 1, 1), 62.08), (date(2022, 2, 1), 62.35), (date(2022, 3, 1), 62.40),
    (date(2022, 4, 1), 62.22), (date(2022, 5, 1), 62.35), (date(2022, 6, 1), 62.18),
    (date(2022, 7, 1), 62.08), (date(2022, 8, 1), 62.40), (date(2022, 9, 1), 62.28),
    (date(2022, 10, 1), 62.55), (date(2022, 11, 1), 62.55), (date(2022, 12, 1), 62.55),
    (date(2023, 1, 1), 62.55), (date(2023, 2, 1), 62.50), (date(2023, 3, 1), 62.62),
    (date(2023, 4, 1), 62.55), (date(2023, 5, 1), 62.62), (date(2023, 6, 1), 62.68),
    (date(2023, 7, 1), 62.82), (date(2023, 8, 1), 62.83), (date(2023, 9, 1), 62.78),  # post-COVID high
    (date(2023, 10, 1), 62.50), (date(2023, 11, 1), 62.55), (date(2023, 12, 1), 62.52),
    (date(2024, 1, 1), 62.55), (date(2024, 2, 1), 62.50), (date(2024, 3, 1), 62.70),
    (date(2024, 4, 1), 62.62), (date(2024, 5, 1), 62.60), (date(2024, 6, 1), 62.70),
    (date(2024, 7, 1), 62.65), (date(2024, 8, 1), 62.70), (date(2024, 9, 1), 62.55),
    (date(2024, 10, 1), 62.55), (date(2024, 11, 1), 62.50), (date(2024, 12, 1), 62.48),
    (date(2025, 1, 1), 62.45), (date(2025, 2, 1), 62.20), (date(2025, 3, 1), 62.28),
    (date(2025, 4, 1), 62.52), (date(2025, 5, 1), 62.48), (date(2025, 6, 1), 62.45),
    (date(2025, 7, 1), 62.40), (date(2025, 8, 1), 62.15), (date(2025, 9, 1), 61.95),  # slide begins
    (date(2025, 10, 1), 61.72), (date(2025, 11, 1), 61.62), (date(2025, 12, 1), 61.58),
    (date(2026, 1, 1), 61.55), (date(2026, 2, 1), 61.53), (date(2026, 3, 1), 61.53),
    (date(2026, 4, 1), 61.52), (date(2026, 5, 1), 61.51), (date(2026, 6, 15), 61.50),  # today
]

xs = [d for d, _ in SERIES]
ys = [p for _, p in SERIES]

LINE    = "#1f6fea"   # main line (RE steel blue, faithful to source blue)
LINE_DK = "#1553b8"   # markers / today
FILL_TOP = "#cfe0f7"
INK     = "#12263f"
MUTED   = "#6b7280"
DROP    = "#b91c1c"   # recent slide callout
GROUND  = "#fdf6e8"   # warm cream (matches the RE report cards)

fig, ax = plt.subplots(figsize=(12, 6.2))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

# area + line
ax.fill_between(xs, ys, 61.3, color=FILL_TOP, alpha=0.55, zorder=1)
ax.plot(xs, ys, color=LINE, linewidth=3.4, zorder=3, solid_capstyle="round")

# post-COVID high callout
ax.annotate("Near a post-COVID\nhigh in 2023-24",
            xy=(date(2023, 8, 1), 62.83), xytext=(date(2022, 9, 1), 62.9),
            fontsize=10.5, color=MUTED, ha="left", va="center", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.1,
                            connectionstyle="arc3,rad=-0.12"))

# recent slide callout
ax.annotate("720K left the\nlabor force in June",
            xy=(date(2025, 11, 1), 61.62), xytext=(date(2024, 1, 1), 61.55),
            fontsize=11, fontweight="bold", color=DROP, ha="left", va="center",
            arrowprops=dict(arrowstyle="->", color=DROP, lw=1.5,
                            connectionstyle="arc3,rad=0.18"))

# today marker + label
ax.plot([xs[-1]], [ys[-1]], marker="o", color="white", markeredgecolor=LINE_DK,
        markeredgewidth=2.4, markersize=13, zorder=6)
ax.annotate("Jun 2026\n61.5%",
            xy=(xs[-1], ys[-1]), xytext=(date(2025, 12, 1), 62.15),
            fontsize=12, fontweight="bold", color=LINE_DK, ha="center", va="center",
            arrowprops=dict(arrowstyle="->", color=LINE_DK, lw=1.6,
                            connectionstyle="arc3,rad=-0.2"))

# titles
ax.set_title("U.S. Labor Force Participation Rate", fontsize=23,
             fontweight="bold", color=INK, loc="left", pad=18)
ax.text(0.0, 1.02, "Share of the population working or looking for work, seasonally adjusted",
        transform=ax.transAxes, fontsize=12.5, color=MUTED, ha="left")

# axes cosmetics
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.1f}%"))
ax.set_ylim(61.3, 63.0)
ax.set_yticks([61.5, 61.8, 62.1, 62.4, 62.7])
ax.set_xlim(date(2021, 4, 1), date(2026, 10, 1))
ax.xaxis.set_major_locator(mdates.YearLocator(1, month=7))
ax.xaxis.set_major_formatter(mdates.DateFormatter("Jul %Y"))
ax.tick_params(axis="both", labelsize=11, colors=MUTED, length=0)
ax.grid(axis="y", color="#e7ddc9", linewidth=1.0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#d8cbb0")

# source footer (no RE authorship attribution — Harv, 06/29)
fig.text(0.012, 0.012, "Source: FRED, U.S. Bureau of Labor Statistics (CIVPART)",
         fontsize=9, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.075, right=0.975, top=0.85, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT)
