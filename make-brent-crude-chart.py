#!/usr/bin/env python3
"""
make-brent-crude-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the Market Briefs "Brent Crude Oil — 2026
Price Per Barrel, YTD" graphic for the 06/23/26 daily email.

This is OUR OWN chart, not the source image: a clean RE-branded amber theme on
white, the twin-peak spring run-up faithfully reproduced, the recent slide
highlighted, and a "today" marker at the real Brent print ($77.77, -0.18%).

Story (Market Briefs "🌎 Back to Earth." / "Fire Sale", 06/23/26): with the U.S.
blockade on Iran lifted, Iran is dumping crude at $2.50 to $5 a barrel below
Brent and supply is flooding back, so oil has tumbled off its spring highs near
$114 back toward the high $70s. Lower oil = cheaper gas and jet fuel and cooler
inflation.

matplotlib only. Run with python3.13 (the interpreter that has matplotlib here).
"""
import sys
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

OUT = sys.argv[1] if len(sys.argv) > 1 else "brent-crude-back-to-earth-062326.png"

# (date, price USD/bbl) — weekly anchors that recreate the source's YTD shape:
# low-$60s January, a steep late-Feb run-up, a twin spring peak near $114 with an
# April trough between them, then a long slide into late June, ending at $77.77.
SERIES = [
    (date(2026, 1, 2),  62.0),
    (date(2026, 1, 9),  63.6),
    (date(2026, 1, 16), 65.6),
    (date(2026, 1, 23), 64.1),
    (date(2026, 1, 30), 63.0),
    (date(2026, 2, 6),  65.2),
    (date(2026, 2, 13), 67.1),
    (date(2026, 2, 20), 66.0),
    (date(2026, 2, 27), 71.4),
    (date(2026, 3, 6),  93.8),
    (date(2026, 3, 13), 104.2),
    (date(2026, 3, 20), 114.3),   # first spring peak
    (date(2026, 3, 27), 106.8),
    (date(2026, 4, 3),  102.5),
    (date(2026, 4, 10), 110.1),
    (date(2026, 4, 17), 98.6),
    (date(2026, 4, 24), 94.2),    # trough between the peaks
    (date(2026, 5, 1),  103.4),
    (date(2026, 5, 8),  114.6),   # second spring peak
    (date(2026, 5, 15), 111.3),
    (date(2026, 5, 22), 108.0),
    (date(2026, 5, 29), 110.4),
    (date(2026, 6, 5),  108.6),
    (date(2026, 6, 12), 99.7),
    (date(2026, 6, 18), 89.5),
    (date(2026, 6, 22), 80.3),
    (date(2026, 6, 23), 77.77),   # today (real Brent print, -0.18%)
]

xs = [d for d, _ in SERIES]
ys = [p for _, p in SERIES]

AMBER    = "#d97706"   # main line (crude / amber)
AMBER_DK = "#b45309"   # markers
AMBER_FL = "#fde9c8"   # area fill
GREEN    = "#15803d"   # the "easing" slide — lower oil is consumer-friendly
INK      = "#1f2937"
MUTED    = "#64748b"

fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# area + line
ax.fill_between(xs, ys, 55, color=AMBER_FL, alpha=0.7, zorder=1)
ax.plot(xs, ys, color=AMBER, linewidth=3.2, zorder=3, solid_capstyle="round")
ax.plot(xs, ys, marker="o", linestyle="none", color=AMBER_DK, markersize=4.2, zorder=4)

# highlight the recent slide (Jun 5 -> today) in green = relief at the pump
tail = SERIES[-5:]
ax.plot([d for d, _ in tail], [p for _, p in tail], color=GREEN,
        linewidth=3.4, zorder=5, solid_capstyle="round")

# today marker + label
ax.plot([xs[-1]], [ys[-1]], marker="o", color=GREEN, markersize=9, zorder=6)
ax.annotate("Jun 23\n$77.77  (-0.18%)",
            xy=(xs[-1], ys[-1]), xytext=(date(2026, 5, 18), 70.5),
            fontsize=11, fontweight="bold", color=GREEN, ha="left", va="center",
            arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.5))

# spring-peak callout
ax.annotate("Spring spike\n~$114 a barrel",
            xy=(date(2026, 5, 8), 114.6), xytext=(date(2026, 3, 30), 119.0),
            fontsize=10.5, fontweight="bold", color=AMBER_DK, ha="center", va="center",
            arrowprops=dict(arrowstyle="-", color=AMBER_DK, lw=1.1))

# driver callout on the slide
ax.annotate("Iran supply floods back\nas the blockade lifts",
            xy=(date(2026, 6, 16), 92.0), xytext=(date(2026, 4, 22), 74.0),
            fontsize=10.5, color=GREEN, ha="center", va="center", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.2,
                            connectionstyle="arc3,rad=0.22"))

# titles
ax.set_title("Brent Crude Oil — “Back to Earth”", fontsize=22, fontweight="bold",
             color=INK, loc="left", pad=18)
ax.text(0.0, 1.02, "Price per barrel, 2026 year-to-date  (USD)",
        transform=ax.transAxes, fontsize=12.5, color=MUTED, ha="left")

# axes cosmetics
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:,.0f}"))
ax.set_ylim(55, 124)
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.tick_params(axis="both", labelsize=11, colors=MUTED, length=0)
ax.grid(axis="y", color="#e5e7eb", linewidth=1.0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#cbd5e1")

# source + branding footer
fig.text(0.012, 0.012,
         "Source: ICE Brent Crude  ·  Chart by REALTY EXPERTS®  ·  TeamRealtyExperts.com",
         fontsize=9, color="#94a3b8", ha="left")

fig.subplots_adjust(left=0.07, right=0.975, top=0.86, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor="white")
plt.close(fig)
print("wrote", OUT)
