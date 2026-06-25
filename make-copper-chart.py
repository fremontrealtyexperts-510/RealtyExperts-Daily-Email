#!/usr/bin/env python3
"""
make-copper-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "Copper Price in 2026" graphic for the
06/25/26 daily email. This is OUR OWN branded chart, not the source image: a clean
RE-branded copper theme on white, the YTD shape faithfully reproduced (a choppy
near-$6 winter, an April low near $5.45, the May to June run up toward $6.65, then
the recent slide back), a $6.00 reference line, and a "today" marker at $5.9815.

Story (Market Briefs "🧠 Day to remember." / "Copper Runs Out Of Steam", 06/25/26):
copper had been sliding before ticking up a touch, held down by three forces, a
strong dollar that makes copper pricier for overseas buyers, the Fed's higher for
longer rates that make raw materials less appealing, and global supply at its
highest level since 2003.

matplotlib only. Run with python3.13 (the interpreter that has matplotlib here).
"""
import sys
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

OUT = sys.argv[1] if len(sys.argv) > 1 else "copper-runs-out-of-steam-062526.png"

# (date, price USD/lb) — anchors recreating the source's YTD shape:
# a choppy ~$5.8-6.0 winter, a sharp April low near $5.45, a big May->June run-up
# to ~$6.65, then a slide back toward $6, ending at $5.9815 (+0.55% YTD).
SERIES = [
    (date(2026, 1, 2),  5.70),
    (date(2026, 1, 9),  5.90),
    (date(2026, 1, 16), 5.96),
    (date(2026, 1, 23), 6.04),   # early peak
    (date(2026, 1, 30), 5.83),
    (date(2026, 2, 6),  5.80),
    (date(2026, 2, 13), 5.86),
    (date(2026, 2, 20), 5.79),
    (date(2026, 2, 27), 5.83),
    (date(2026, 3, 6),  5.93),
    (date(2026, 3, 13), 6.00),   # March peak
    (date(2026, 3, 20), 5.89),
    (date(2026, 3, 27), 5.99),
    (date(2026, 4, 3),  6.00),
    (date(2026, 4, 10), 5.61),
    (date(2026, 4, 14), 5.45),   # April low (YTD low)
    (date(2026, 4, 21), 5.62),
    (date(2026, 4, 28), 5.66),
    (date(2026, 5, 4),  5.80),
    (date(2026, 5, 8),  6.05),
    (date(2026, 5, 12), 5.90),
    (date(2026, 5, 18), 5.86),
    (date(2026, 5, 22), 6.10),
    (date(2026, 5, 26), 6.55),
    (date(2026, 5, 29), 6.66),   # spring peak
    (date(2026, 6, 2),  6.34),
    (date(2026, 6, 5),  6.50),
    (date(2026, 6, 9),  6.36),
    (date(2026, 6, 12), 6.64),   # June peak
    (date(2026, 6, 16), 6.44),
    (date(2026, 6, 19), 6.30),
    (date(2026, 6, 22), 6.50),   # last bounce
    (date(2026, 6, 24), 6.27),
    (date(2026, 6, 25), 5.9815), # today ($5.9815, +0.55% YTD)
]

xs = [d for d, _ in SERIES]
ys = [p for _, p in SERIES]

COPPER    = "#c2703d"   # main line (copper)
COPPER_DK = "#8c5224"   # markers
COPPER_FL = "#f6e2d2"   # area fill
SLIDE     = "#b91c1c"   # the recent slide (runs out of steam)
INK       = "#1f2937"
MUTED     = "#64748b"

fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# area + line
ax.fill_between(xs, ys, 5.30, color=COPPER_FL, alpha=0.8, zorder=1)
ax.plot(xs, ys, color=COPPER, linewidth=3.2, zorder=3, solid_capstyle="round")
ax.plot(xs, ys, marker="o", linestyle="none", color=COPPER_DK, markersize=4.0, zorder=4)

# $6.00 reference line
ax.axhline(6.00, color="#dc2626", linewidth=1.4, linestyle=(0, (6, 5)), alpha=0.75, zorder=2)
ax.text(date(2026, 1, 3), 6.02, "$6.00", color="#dc2626", fontsize=10,
        fontweight="bold", va="bottom", ha="left")

# highlight the recent slide (last bounce -> today) = runs out of steam
tail = SERIES[-3:]
ax.plot([d for d, _ in tail], [p for _, p in tail], color=SLIDE,
        linewidth=3.4, zorder=5, solid_capstyle="round")

# today marker + label
ax.plot([xs[-1]], [ys[-1]], marker="o", color="white", markeredgecolor=COPPER_DK,
        markeredgewidth=2, markersize=11, zorder=6)
ax.annotate("Jun 25\n$5.9815  (+0.55% YTD)",
            xy=(xs[-1], ys[-1]), xytext=(date(2026, 3, 20), 6.28),
            fontsize=11, fontweight="bold", color=COPPER_DK, ha="left", va="center",
            arrowprops=dict(arrowstyle="->", color=COPPER_DK, lw=1.5,
                            connectionstyle="arc3,rad=-0.12"))

# April low callout
ax.annotate("April low\n~$5.45",
            xy=(date(2026, 4, 14), 5.45), xytext=(date(2026, 2, 22), 5.50),
            fontsize=10.5, fontweight="bold", color=MUTED, ha="center", va="center",
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.1))

# driver callout near the peak/slide
ax.annotate("A strong dollar and higher\nfor longer rates cap copper",
            xy=(date(2026, 6, 5), 6.50), xytext=(date(2026, 1, 20), 6.70),
            fontsize=10.5, color=SLIDE, ha="left", va="center", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=SLIDE, lw=1.2,
                            connectionstyle="arc3,rad=0.18"))

# titles
ax.set_title("Copper Price in 2026 — “Running Out of Steam”", fontsize=21,
             fontweight="bold", color=INK, loc="left", pad=18)
ax.text(0.0, 1.02, "Front-month HG futures, year-to-date  (USD / lb)",
        transform=ax.transAxes, fontsize=12.5, color=MUTED, ha="left")

# axes cosmetics
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:,.2f}"))
ax.set_ylim(5.30, 6.85)
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
         "Source: COMEX copper (HG), USD/lb  ·  Chart by REALTY EXPERTS®  ·  TeamRealtyExperts.com",
         fontsize=9, color="#94a3b8", ha="left")

fig.subplots_adjust(left=0.07, right=0.975, top=0.86, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor="white")
plt.close(fig)
print("wrote", OUT)
