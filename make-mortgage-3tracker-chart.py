#!/usr/bin/env python3
"""
make-mortgage-3tracker-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "30-Year Fixed Mortgage Rates" graphic
(Mortgage News Daily, July 2025 to July 2026) for the 07/16/26 daily email. OUR OWN
branded chart, not the source image: three tracker lines (Mortgage News Daily, MBA,
Freddie Mac) on a warm cream ground, the round trip faithfully reproduced (about
6.77% last August, easing to a 6.02% low in March 2026, then climbing back to 6.64%
today), with end-of-line labels and a callout on the March low.

Story (Market Briefs "🔨 Tool toll." 07/16/26): the daily 30-year sits at 6.64% and
the weekly average just printed its highest level in nearly a year, so purchase
applications slid 7% in a week. Rising fuel costs and Middle East unrest pushed
bond yields higher, dragging mortgage rates with them.

matplotlib only. Build with python3.13 on Mac (matplotlib 3.10).
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

OUT = sys.argv[1] if len(sys.argv) > 1 else "mortgage-3tracker-071626.png"

MONTHS = ["Aug '25", "Sep '25", "Oct '25", "Nov '25", "Dec '25", "Jan '26",
          "Feb '26", "Mar '26", "Apr '26", "May '26", "Jun '26", "Jul '26"]
X = range(len(MONTHS))

# Monthly anchors recreating the source's shape (Mortgage News Daily chart).
MND     = [6.77, 6.62, 6.31, 6.16, 6.22, 6.10, 6.16, 6.02, 6.42, 6.52, 6.57, 6.64]
MBA     = [6.75, 6.62, 6.46, 6.36, 6.29, 6.22, 6.22, 6.12, 6.35, 6.52, 6.55, 6.58]
FREDDIE = [6.70, 6.60, 6.32, 6.22, 6.16, 6.16, 6.10, 6.06, 6.28, 6.44, 6.42, 6.46]

GOLD  = "#B08C1E"   # Mortgage News Daily (lead series)
SLATE = "#3E5C76"   # MBA
CLAY  = "#A65A44"   # Freddie Mac
INK    = "#12263f"
MUTED  = "#6b7280"
GROUND = "#fdf6e8"
HAIR   = "#e0d6c0"

fig, ax = plt.subplots(figsize=(12, 6.2))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

series = [("Mortgage News Daily", MND, GOLD, 2.8, 5),
          ("MBA", MBA, SLATE, 2.0, 3),
          ("Freddie Mac", FREDDIE, CLAY, 2.0, 3)]
for name, ys, color, lw, z in series:
    ax.plot(X, ys, color=color, linewidth=lw, zorder=z, solid_capstyle="round", label=name)
    ax.plot(X[-1], ys[-1], "o", color=color, markersize=6, zorder=z + 1)
    ax.annotate(f"{ys[-1]:.2f}%", xy=(X[-1], ys[-1]), xytext=(8, 0),
                textcoords="offset points", fontsize=11, fontweight="bold",
                color=color, va="center")

# March low callout on the lead series
ax.annotate("March low 6.02%",
            xy=(7, 6.02), xytext=(7, 5.90),
            fontsize=10, color=MUTED, ha="center", va="top",
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))

ax.set_ylim(5.8, 6.95)
ax.set_xlim(-0.3, 11.9)
ax.set_xticks(list(X))
ax.set_xticklabels(MONTHS, fontsize=9.5, color=MUTED)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.1f}%"))
ax.tick_params(axis="y", labelsize=10, colors=MUTED, length=0)
ax.tick_params(axis="x", length=0)
ax.grid(axis="y", color=HAIR, linewidth=0.8, alpha=0.8)
for spine in ax.spines.values():
    spine.set_visible(False)

ax.set_title("30-Year Fixed Mortgage Rates: The Round Trip",
             fontsize=17, fontweight="bold", color=INK, loc="left", pad=26)
ax.text(0, 1.035, "Three national trackers, July 2025 to July 2026. Daily rate now 6.64%, back near a one year high.",
        transform=ax.transAxes, fontsize=10.5, color=MUTED)

leg = ax.legend(loc="lower left", bbox_to_anchor=(0.0, 0.02), frameon=False,
                fontsize=10, ncol=3, handlelength=1.6, columnspacing=1.4)
for t in leg.get_texts():
    t.set_color(INK)

fig.text(0.065, 0.022, "Source: Mortgage News Daily", fontsize=8.5, color="#a99f88")
fig.tight_layout(rect=(0.01, 0.045, 0.985, 0.97))
fig.savefig(OUT, dpi=160, facecolor=GROUND)
print(f"wrote {OUT}")
