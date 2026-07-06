#!/usr/bin/env python3
"""
make-dow-ytd-chart.py  [out.png]

REALTY EXPERTS branded recreation of the Dow Jones Industrial Average YTD chart
for the 07/06/26 daily email (Market Briefs "✌️ Moving out." — the Dow set a
record high close last week). OUR OWN branded chart, not the source image.

Endpoint 52,900.07, +10.06% YTD (+4,836.78). Warm cream ground (Meridian paper),
green line/area for the record-high gains story. Faithfully reproduces the source
shape: a choppy Jan plateau near 49,000, an early-March peak ~50,100, an April
low near 45,300, a strong V recovery, and a steady climb to today's record.

Source line only (no RE authorship label, per Harv 06/29). Run with python3.13.
"""
import sys
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

OUT = sys.argv[1] if len(sys.argv) > 1 else "dow-record-high-070626.png"

# (date, DJIA close) — weekly anchors recreating the source's YTD shape.
# Start 48,063.29 (52,900.07 / 1.1006 -> +10.06% YTD), end at today's record.
SERIES = [
    (date(2026, 1, 2),  48063.29),
    (date(2026, 1, 9),  48950.0),
    (date(2026, 1, 16), 49300.0),   # mid-Jan local high
    (date(2026, 1, 23), 49050.0),
    (date(2026, 1, 30), 48800.0),
    (date(2026, 2, 6),  49200.0),
    (date(2026, 2, 13), 49000.0),
    (date(2026, 2, 20), 49350.0),
    (date(2026, 2, 27), 49150.0),
    (date(2026, 3, 6),  49650.0),
    (date(2026, 3, 13), 50100.0),   # early-spring peak
    (date(2026, 3, 20), 49500.0),
    (date(2026, 3, 27), 48600.0),
    (date(2026, 4, 3),  47600.0),
    (date(2026, 4, 10), 46700.0),
    (date(2026, 4, 17), 46100.0),
    (date(2026, 4, 24), 45300.0),   # April low (YTD low)
    (date(2026, 5, 1),  46600.0),
    (date(2026, 5, 8),  48400.0),
    (date(2026, 5, 15), 50000.0),
    (date(2026, 5, 22), 51500.0),   # mid-May local peak
    (date(2026, 5, 29), 50600.0),
    (date(2026, 6, 5),  49950.0),   # early-June dip
    (date(2026, 6, 12), 51000.0),
    (date(2026, 6, 19), 51900.0),
    (date(2026, 6, 26), 52300.0),
    (date(2026, 7, 2),  52650.0),
    (date(2026, 7, 6),  52900.07),  # today — record high (+10.06% YTD)
]

xs = [d for d, _ in SERIES]
ys = [p for _, p in SERIES]

GREEN    = "#16a34a"   # main line (gains / "in the green")
GREEN_DK = "#15803d"   # markers
GREEN_FL = "#d9f0e0"   # area fill
GREEN_HL = "#0d9f57"   # recovery highlight
GROUND   = "#FAF7F0"   # Meridian paper
INK      = "#2e2e2e"
MUTED    = "#8a8172"

fig, ax = plt.subplots(figsize=(12, 6.2))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

# area + line
ax.fill_between(xs, ys, 44000, color=GREEN_FL, alpha=0.9, zorder=1)
ax.plot(xs, ys, color=GREEN, linewidth=3.0, zorder=3, solid_capstyle="round")

# highlight the April-low -> record run-up
tail = SERIES[16:]
ax.plot([d for d, _ in tail], [p for _, p in tail], color=GREEN_HL,
        linewidth=3.4, zorder=4, solid_capstyle="round")

# today marker + record-high label (top area, clear of the line)
ax.plot([xs[-1]], [ys[-1]], marker="o", color=GREEN_DK, markersize=10, zorder=6)
ax.annotate("Record high  52,900\n+10.06% YTD  ·  +4,836.78",
            xy=(xs[-1], ys[-1]), xytext=(date(2026, 3, 16), 53380),
            fontsize=12, fontweight="bold", color=GREEN_DK, ha="left", va="center",
            arrowprops=dict(arrowstyle="->", color=GREEN_DK, lw=1.5))

# April low callout
ax.annotate("Apr low\n~45,300",
            xy=(date(2026, 4, 24), 45300), xytext=(date(2026, 2, 20), 45600),
            fontsize=10.5, fontweight="bold", color=MUTED, ha="left", va="center",
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.1))

# titles
ax.set_title("Dow Jones Industrial Average — Record High", fontsize=22,
             fontweight="bold", color=INK, loc="left", pad=18)
ax.text(0.0, 1.02, "DJIA, 2026 year-to-date", transform=ax.transAxes,
        fontsize=12.5, color=MUTED, ha="left")

# axes cosmetics
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
ax.set_ylim(44000, 54000)
ax.set_yticks([44000, 46000, 48000, 50000, 52000, 54000])
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.tick_params(axis="both", labelsize=11, colors=MUTED, length=0)
ax.grid(axis="y", color="#e7ddc9", linewidth=1.0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#d8cbb0")

fig.text(0.012, 0.012, "Source: S&P Dow Jones Indices  ·  YTD 2026",
         fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.065, right=0.975, top=0.86, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT)
