#!/usr/bin/env python3
"""
make-bitcoin-2026-chart.py  [out.png]

REALTY EXPERTS recreation of the "Bitcoin's Price in 2026" graphic for the
07/01/26 daily email. OUR OWN branded chart, not the source image: BTC's 2026
price path on a dark navy theme with a coral line and soft area fill.

Story (Market Briefs "Trump vs. the pump.", 07/01/26): Strategy (MSTR), the
largest corporate holder of Bitcoin, sold over $1B in BTC this week; the coin
slid more than 3% toward $58,000. As of Jul 1: $59,046, down 32.45% YTD.

matplotlib only (python3 3.12 has matplotlib 3.6 on this VPS).
"""
import sys
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

OUT = sys.argv[1] if len(sys.argv) > 1 else "bitcoin-price-2026-070126.png"

# (date, price USD) — anchors recreating the source's 2026 shape: a late-Jan peak
# near $95K, a sharp early-March break to a mid-March low near $63K, a choppy
# spring in the mid-$60Ks to low-$70Ks, an early-June bounce to ~$82K, then a
# steep slide into July ending at $59,046.
SERIES = [
    (date(2026, 1, 2),  88000),
    (date(2026, 1, 12), 91000),
    (date(2026, 1, 22), 95000),   # YTD peak
    (date(2026, 2, 1),  92000),
    (date(2026, 2, 10), 89000),
    (date(2026, 2, 20), 87000),
    (date(2026, 3, 1),  80000),   # break begins
    (date(2026, 3, 5),  80000),
    (date(2026, 3, 10), 64000),
    (date(2026, 3, 15), 63000),   # spring low
    (date(2026, 3, 22), 66000),
    (date(2026, 3, 29), 68000),
    (date(2026, 4, 5),  65000),
    (date(2026, 4, 12), 67000),
    (date(2026, 4, 20), 69000),
    (date(2026, 4, 27), 66000),
    (date(2026, 5, 4),  70000),
    (date(2026, 5, 11), 73000),
    (date(2026, 5, 15), 72000),
    (date(2026, 5, 20), 67000),
    (date(2026, 5, 25), 74000),
    (date(2026, 6, 1),  79000),
    (date(2026, 6, 5),  82000),   # early-June bounce
    (date(2026, 6, 12), 80000),
    (date(2026, 6, 18), 76000),
    (date(2026, 6, 24), 62000),
    (date(2026, 6, 27), 65000),
    (date(2026, 6, 30), 60000),
    (date(2026, 7, 1),  59046),   # today
]

xs = [d for d, _ in SERIES]
ys = [p for _, p in SERIES]

NAVY   = "#182a44"   # background
GRID   = "#2b3f5c"
CORAL  = "#f2696b"   # line
FILL   = "#3a3b5c"   # area (blends coral into navy)
LIGHT  = "#e8eef6"
MUTED  = "#9fb0c6"

fig, ax = plt.subplots(figsize=(12, 6.6))
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)

ax.fill_between(xs, ys, 50000, color=FILL, alpha=0.55, zorder=1)
ax.plot(xs, ys, color=CORAL, linewidth=3.4, zorder=3, solid_capstyle="round")

# today marker + chip
ax.plot([xs[-1]], [ys[-1]], marker="o", color=CORAL, markersize=11,
        markeredgecolor="white", markeredgewidth=1.6, zorder=6)
ax.annotate("$59,046", xy=(xs[-1], ys[-1]), xytext=(-6, -34),
            textcoords="offset points", fontsize=15, fontweight="bold",
            color="white", ha="right", va="center",
            bbox=dict(boxstyle="round,pad=0.45", fc=CORAL, ec="none"), zorder=7)

# titles + YTD readout
ax.set_title("Bitcoin's Price in 2026", fontsize=25, fontweight="bold",
             color="white", loc="left", pad=44)
ax.text(0.0, 1.085, "$59,046", transform=ax.transAxes, fontsize=20,
        fontweight="bold", color="white", ha="left", va="center")
ax.text(0.145, 1.085, "▼ 32.45% YTD", transform=ax.transAxes, fontsize=15,
        fontweight="bold", color=CORAL, ha="left", va="center")

# axes cosmetics
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v/1000:.0f}K"))
ax.set_ylim(50000, 100000)
ax.set_yticks([50000, 60000, 70000, 80000, 90000, 100000])
ax.set_xlim(date(2026, 1, 1), date(2026, 7, 6))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.tick_params(axis="both", labelsize=12, colors=MUTED, length=0)
ax.grid(axis="y", color=GRID, linewidth=1.0, linestyle=(0, (2, 4)))
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)

fig.text(0.012, 0.012, "Source: Google Finance  ·  as of Jul 1, 2026",
         fontsize=9, color="#6f83a0", ha="left")

fig.subplots_adjust(left=0.075, right=0.965, top=0.80, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor=NAVY)
plt.close(fig)
print("wrote", OUT)
