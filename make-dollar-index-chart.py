#!/usr/bin/env python3
"""
make-dollar-index-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the U.S. Dollar Index (DXY) chart for the
06/24/26 daily email. This is OUR OWN branded chart, not the source image.

Story (Market Briefs "🍪 Double dip." / "Feeling Green", 06/24/26): markets
closed in the red, but the U.S. dollar is in the green, hitting a 13-month high
against major currencies. Wall Street puts an ~85% chance the Fed hikes rates by
September, and rate-hike bets pull money into the dollar (fewer dollars to borrow,
each one worth more). The stronger dollar is also what knocked gold and silver
down hard the same day.

Green theme on white to match both the Economy section color and the "Feeling
Green" pun. Faithfully reproduces the source shape: an early-Feb trough near 96.8,
a spring double-top near 100.9, a May dip, then the late-June run-up to a 13-month
high at 101.64 (+3.42% YTD).

matplotlib only. Run with python3.13 (the interpreter that has matplotlib here).
"""
import sys
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

OUT = sys.argv[1] if len(sys.argv) > 1 else "dollar-index-feeling-green-062426.png"

# (date, DXY level) — weekly anchors recreating the source's YTD shape.
# Starts at 98.28 (101.64 / 1.0342 -> +3.42% YTD), dips to a Feb trough ~96.8,
# climbs to a spring double-top ~100.9, eases through May, then runs up to a
# 13-month high of 101.64 today.
SERIES = [
    (date(2026, 1, 2),  98.28),
    (date(2026, 1, 9),  98.95),
    (date(2026, 1, 16), 99.30),   # mid-Jan local high
    (date(2026, 1, 23), 98.65),
    (date(2026, 1, 30), 97.10),
    (date(2026, 2, 6),  96.80),   # Feb trough (YTD low)
    (date(2026, 2, 13), 97.95),
    (date(2026, 2, 20), 97.55),
    (date(2026, 2, 27), 97.35),
    (date(2026, 3, 6),  97.85),
    (date(2026, 3, 13), 98.60),
    (date(2026, 3, 20), 99.65),
    (date(2026, 3, 27), 100.78),  # first spring peak
    (date(2026, 4, 3),  100.05),
    (date(2026, 4, 10), 100.92),  # second spring peak (double top)
    (date(2026, 4, 17), 100.05),
    (date(2026, 4, 24), 99.30),
    (date(2026, 5, 1),  98.30),
    (date(2026, 5, 8),  97.80),   # May dip
    (date(2026, 5, 15), 98.50),
    (date(2026, 5, 22), 98.20),
    (date(2026, 5, 29), 98.80),
    (date(2026, 6, 5),  99.35),
    (date(2026, 6, 12), 99.85),
    (date(2026, 6, 19), 100.45),
    (date(2026, 6, 24), 101.64),  # today — 13-month high (+3.42% YTD)
]

xs = [d for d, _ in SERIES]
ys = [p for _, p in SERIES]

GREEN    = "#16a34a"   # main line (economy green / "in the green")
GREEN_DK = "#15803d"   # markers
GREEN_FL = "#dcfce7"   # area fill
GREEN_HL = "#0d9f57"   # the recent run-up highlight
INK      = "#1f2937"
MUTED    = "#64748b"

fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# area + line
ax.fill_between(xs, ys, 96.0, color=GREEN_FL, alpha=0.85, zorder=1)
ax.plot(xs, ys, color=GREEN, linewidth=3.2, zorder=3, solid_capstyle="round")
ax.plot(xs, ys, marker="o", linestyle="none", color=GREEN_DK, markersize=4.2, zorder=4)

# highlight the recent run-up (May dip -> today) — the dollar's comeback
tail = SERIES[-6:]
ax.plot([d for d, _ in tail], [p for _, p in tail], color=GREEN_HL,
        linewidth=3.6, zorder=5, solid_capstyle="round")

# today marker + label
ax.plot([xs[-1]], [ys[-1]], marker="o", color=GREEN_DK, markersize=9, zorder=6)
ax.annotate("Jun 24\n101.64  (+3.42% YTD)\n13-month high",
            xy=(xs[-1], ys[-1]), xytext=(date(2026, 4, 26), 99.55),
            fontsize=11, fontweight="bold", color=GREEN_DK, ha="left", va="center",
            arrowprops=dict(arrowstyle="->", color=GREEN_DK, lw=1.5))

# Feb trough callout
ax.annotate("Feb low\n~96.8",
            xy=(date(2026, 2, 6), 96.80), xytext=(date(2026, 1, 6), 97.35),
            fontsize=10.5, fontweight="bold", color=MUTED, ha="left", va="center",
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.1))

# driver callout on the run-up
ax.annotate("Fed-hike bets pull\nmoney into the dollar",
            xy=(date(2026, 6, 10), 99.85), xytext=(date(2026, 3, 30), 97.0),
            fontsize=10.5, color=GREEN_HL, ha="center", va="center", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=GREEN_HL, lw=1.2,
                            connectionstyle="arc3,rad=-0.25"))

# titles
ax.set_title("U.S. Dollar Index — “Feeling Green”", fontsize=22, fontweight="bold",
             color=INK, loc="left", pad=18)
ax.text(0.0, 1.02, "ICE U.S. Dollar Index (DXY), 2026 year-to-date",
        transform=ax.transAxes, fontsize=12.5, color=MUTED, ha="left")

# axes cosmetics
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
ax.set_ylim(96.0, 102.6)
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
         "Source: ICE U.S. Dollar Index (DX-Y.NYB)  ·  Chart by REALTY EXPERTS®  ·  TeamRealtyExperts.com",
         fontsize=9, color="#94a3b8", ha="left")

fig.subplots_adjust(left=0.06, right=0.975, top=0.86, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor="white")
plt.close(fig)
print("wrote", OUT)
