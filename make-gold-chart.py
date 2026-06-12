#!/usr/bin/env python3
"""
make-gold-chart.py  [out.png]

Renders the "Looking Dull" gold chart for the daily email: gold spot price,
2026 year-to-date. Inspired by the Market Briefs 06/12/26 "Looking Dull" story
(gold tumbled to a ~6-month low this week, down ~6.3%, even with inflation at a
3-year high, as traders bet the Fed could hike by December).

Illustrative YTD trajectory anchored on publicly reported spot levels:
  Jan 28 peak  $5,414  (JM Bullion)
  Jun 1        $4,460  (Fortune)
  Jun 10 low   $4,161  (USAGOLD daily report)
  Jun 12 today $4,186  (Trading Economics, -0.63% on the day)
Intermediate month points are smoothed estimates between those anchors.

No external deps beyond matplotlib (already used by mls-csv-to-images.py).
"""
import sys
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

OUT = sys.argv[1] if len(sys.argv) > 1 else "gold-looking-dull-061226.png"

# (date, price USD/oz)
SERIES = [
    (date(2026, 1, 2),  4250),
    (date(2026, 1, 15), 4880),
    (date(2026, 1, 28), 5414),   # peak (sourced)
    (date(2026, 2, 12), 5180),
    (date(2026, 2, 26), 5040),
    (date(2026, 3, 12), 4880),
    (date(2026, 3, 26), 4760),
    (date(2026, 4, 10), 4650),
    (date(2026, 4, 24), 4575),
    (date(2026, 5, 8),  4515),
    (date(2026, 5, 22), 4475),
    (date(2026, 6, 1),  4460),   # (sourced)
    (date(2026, 6, 8),  4305),
    (date(2026, 6, 10), 4161),   # recent low (sourced)
    (date(2026, 6, 12), 4186),   # today (sourced)
]

xs = [d for d, _ in SERIES]
ys = [p for _, p in SERIES]

GOLD = "#C8A02A"        # line
GOLD_DK = "#9A7B16"     # markers / peak
GOLD_FILL = "#F4E5B8"   # area under curve
INK = "#1f2937"         # dark text
MUTED = "#64748b"
RED = "#b91c1c"

fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# area + line
ax.fill_between(xs, ys, min(ys) - 200, color=GOLD_FILL, alpha=0.55, zorder=1)
ax.plot(xs, ys, color=GOLD, linewidth=3.2, zorder=3, solid_capstyle="round")
ax.plot(xs, ys, marker="o", linestyle="none", color=GOLD_DK,
        markersize=4.5, zorder=4)

# highlight the recent tumble segment (Jun 1 -> Jun 12) in red
tail_x = [d for d, _ in SERIES[-4:]]
tail_y = [p for _, p in SERIES[-4:]]
ax.plot(tail_x, tail_y, color=RED, linewidth=3.2, zorder=5, solid_capstyle="round")

# annotate peak
ax.annotate("Jan peak\n$5,414",
            xy=(date(2026, 1, 28), 5414), xytext=(date(2026, 2, 18), 5300),
            fontsize=11, fontweight="bold", color=GOLD_DK, ha="left", va="center",
            arrowprops=dict(arrowstyle="-", color=GOLD_DK, lw=1.2))

# annotate today
ax.annotate("Jun 12\n$4,186  (-0.63%)",
            xy=(date(2026, 6, 12), 4186), xytext=(date(2026, 5, 6), 3980),
            fontsize=11, fontweight="bold", color=RED, ha="left", va="center",
            arrowprops=dict(arrowstyle="->", color=RED, lw=1.4))

# "this week" callout
ax.annotate("-6.3% this week\n~6-month low",
            xy=(date(2026, 6, 9), 4230), xytext=(date(2026, 4, 2), 4980),
            fontsize=10.5, color=RED, ha="center", va="center", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=RED, lw=1.2,
                            connectionstyle="arc3,rad=-0.25"))

# titles
ax.set_title("Gold — “Looking Dull”", fontsize=22, fontweight="bold",
             color=INK, loc="left", pad=18)
ax.text(0.0, 1.02, "Spot price, 2026 year-to-date  (USD / troy oz)",
        transform=ax.transAxes, fontsize=12.5, color=MUTED, ha="left")

# axes cosmetics
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:,.0f}"))
ax.set_ylim(3850, 5650)
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.tick_params(axis="both", labelsize=11, colors=MUTED, length=0)
ax.grid(axis="y", color="#e5e7eb", linewidth=1.0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#cbd5e1")

# source footer
fig.text(0.012, 0.012,
         "Source: gold spot via Trading Economics, USAGOLD & Fortune  ·  "
         "REALTY EXPERTS® · TeamRealtyExperts.com",
         fontsize=9, color="#94a3b8", ha="left")

fig.subplots_adjust(left=0.075, right=0.975, top=0.86, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor="white")
plt.close(fig)
print("wrote", OUT)
