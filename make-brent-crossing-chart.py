#!/usr/bin/env python3
"""
make-brent-crossing-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "Brent Crude Oil" graphic for the
07/20/26 daily email. OUR OWN branded chart, not the source image: warm cream
ground, Economy-green line over a soft fill, a dashed $90 line that the last
point crosses, and callouts on the April spike and the two week run up.

IMPORTANT, why this differs from the newsletter graphic Harv supplied: the
reference image tops out near $115, but the actual Brent spot series peaked at
$138.21 on 2026-04-07. This chart plots the real FRED/EIA daily series, so the
April spike is taller and truer than the reference.

Data: FRED DCOILBRENTEU (Europe Brent spot, EIA) daily, 2026-01-20 to 2026-07-13,
plus the 2026-07-17 close of $90.37 reported by ICE via Market Briefs. FRED had
not yet published 07/14 to 07/17 at build time, so the final segment connects two
real observations, 07/13 and 07/17, with no invented days between.

Story (Market Briefs "Crossing over", 07/20/26): oil jumped over the weekend as
the Iran and U.S. conflict continued, with Brent crossing $90 a barrel. Higher
oil can mean higher gas prices, which squeezes buyers already stretched by rates.

No authorship label on the chart (per Harv, 06/29) - footer carries only the data
source. matplotlib only; build with python3.13 on Mac.
"""
import sys
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

OUT = sys.argv[1] if len(sys.argv) > 1 else "brent-crossing-072026.png"

# (date, USD per barrel) - faithful to FRED DCOILBRENTEU + the 07/17 ICE close
SERIES = [
    ("2026-01-20", 67.68),
    ("2026-01-21", 66.72),
    ("2026-01-22", 65.46),
    ("2026-01-23", 68.16),
    ("2026-01-26", 67.7),
    ("2026-01-27", 70.28),
    ("2026-01-28", 70.9),
    ("2026-01-29", 71.0),
    ("2026-01-30", 72.25),
    ("2026-02-02", 67.72),
    ("2026-02-03", 70.01),
    ("2026-02-04", 71.15),
    ("2026-02-05", 69.87),
    ("2026-02-06", 70.45),
    ("2026-02-09", 71.19),
    ("2026-02-10", 71.01),
    ("2026-02-11", 71.52),
    ("2026-02-12", 69.8),
    ("2026-02-13", 69.96),
    ("2026-02-16", 70.81),
    ("2026-02-17", 69.77),
    ("2026-02-18", 71.78),
    ("2026-02-19", 73.17),
    ("2026-02-20", 72.75),
    ("2026-02-23", 71.9),
    ("2026-02-24", 71.21),
    ("2026-02-25", 70.69),
    ("2026-02-26", 71.66),
    ("2026-02-27", 71.32),
    ("2026-03-02", 77.24),
    ("2026-03-03", 83.28),
    ("2026-03-04", 81.56),
    ("2026-03-05", 88.59),
    ("2026-03-06", 95.74),
    ("2026-03-09", 94.35),
    ("2026-03-10", 89.84),
    ("2026-03-11", 90.98),
    ("2026-03-12", 102.38),
    ("2026-03-13", 103.23),
    ("2026-03-16", 101.04),
    ("2026-03-17", 108.39),
    ("2026-03-18", 118.09),
    ("2026-03-19", 111.05),
    ("2026-03-20", 118.42),
    ("2026-03-23", 103.79),
    ("2026-03-24", 108.42),
    ("2026-03-25", 109.14),
    ("2026-03-26", 113.39),
    ("2026-03-27", 121.47),
    ("2026-03-30", 121.88),
    ("2026-03-31", 126.69),
    ("2026-04-01", 119.56),
    ("2026-04-02", 127.61),
    ("2026-04-07", 138.21),
    ("2026-04-08", 122.11),
    ("2026-04-09", 119.03),
    ("2026-04-10", 119.07),
    ("2026-04-13", 123.28),
    ("2026-04-14", 118.69),
    ("2026-04-15", 114.93),
    ("2026-04-16", 116.63),
    ("2026-04-17", 98.63),
    ("2026-04-20", 103.4),
    ("2026-04-21", 106.14),
    ("2026-04-22", 113.44),
    ("2026-04-23", 113.25),
    ("2026-04-24", 111.86),
    ("2026-04-27", 113.89),
    ("2026-04-28", 117.62),
    ("2026-04-29", 124.16),
    ("2026-04-30", 124.24),
    ("2026-05-01", 118.26),
    ("2026-05-05", 114.51),
    ("2026-05-06", 103.7),
    ("2026-05-07", 101.82),
    ("2026-05-08", 103.48),
    ("2026-05-11", 106.11),
    ("2026-05-12", 111.37),
    ("2026-05-13", 110.28),
    ("2026-05-14", 110.91),
    ("2026-05-15", 113.96),
    ("2026-05-18", 116.73),
    ("2026-05-19", 114.64),
    ("2026-05-20", 108.93),
    ("2026-05-21", 105.84),
    ("2026-05-22", 106.9),
    ("2026-05-26", 102.75),
    ("2026-05-27", 97.11),
    ("2026-05-28", 95.47),
    ("2026-05-29", 92.88),
    ("2026-06-01", 98.29),
    ("2026-06-02", 98.49),
    ("2026-06-03", 101.69),
    ("2026-06-04", 98.98),
    ("2026-06-05", 97.29),
    ("2026-06-08", 97.46),
    ("2026-06-09", 94.15),
    ("2026-06-10", 95.73),
    ("2026-06-11", 92.84),
    ("2026-06-12", 88.64),
    ("2026-06-15", 84.36),
    ("2026-06-16", 80.5),
    ("2026-06-17", 80.33),
    ("2026-06-18", 79.35),
    ("2026-06-19", 80.46),
    ("2026-06-22", 76.49),
    ("2026-06-23", 75.69),
    ("2026-06-24", 72.09),
    ("2026-06-25", 73.74),
    ("2026-06-26", 70.16),
    ("2026-06-29", 71.59),
    ("2026-06-30", 70.46),
    ("2026-07-01", 69.24),
    ("2026-07-02", 68.53),
    ("2026-07-03", 68.68),
    ("2026-07-06", 69.56),
    ("2026-07-07", 71.78),
    ("2026-07-08", 76.5),
    ("2026-07-09", 74.46),
    ("2026-07-10", 74.34),
    ("2026-07-13", 81.62),
    ("2026-07-17", 90.37)
]

dates = [datetime.strptime(d, "%Y-%m-%d") for d, _ in SERIES]
vals  = [v for _, v in SERIES]

GREEN    = "#16a34a"   # Economy section green
GREEN_DK = "#0f7a37"
INK      = "#12263f"
MUTED    = "#6b7280"
GROUND   = "#fdf6e8"   # warm cream (house style)
GRID     = "#e7ddc9"
ACCENT   = "#b45309"   # amber for the peak callout

fig, ax = plt.subplots(figsize=(12, 6.0))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.fill_between(dates, vals, 60, color=GREEN, alpha=0.13, zorder=2)
ax.plot(dates, vals, color=GREEN_DK, linewidth=2.3, zorder=4,
        solid_joinstyle="round", solid_capstyle="round")

# the $90 threshold the story turns on
ax.axhline(90, color=GREEN_DK, linewidth=1.15, linestyle=(0, (5, 4)), alpha=0.55, zorder=3)
ax.text(dates[2], 91.6, "$90 a barrel", fontsize=11, fontweight="bold",
        color=GREEN_DK, alpha=0.85, ha="left", va="bottom")

# final point, the crossing
ax.scatter([dates[-1]], [vals[-1]], s=95, color=GREEN_DK, zorder=6,
           edgecolor=GROUND, linewidth=2.2)
ax.annotate("Jul 17: $90.37\nfirst close above $90\nsince June 11",
            xy=(dates[-1], vals[-1]), xytext=(dates[-20], 124),
            fontsize=12.5, fontweight="bold", color=GREEN_DK, ha="center", va="center",
            arrowprops=dict(arrowstyle="->", color=GREEN_DK, lw=1.7,
                            connectionstyle="arc3,rad=-0.25"))

# the April spike, the real high in this window
pk_i = max(range(len(vals)), key=lambda i: vals[i])
ax.scatter([dates[pk_i]], [vals[pk_i]], s=62, color=ACCENT, zorder=6,
           edgecolor=GROUND, linewidth=2.0)
ax.annotate("Apr 7 spike: $138.21",
            xy=(dates[pk_i], vals[pk_i]), xytext=(dates[pk_i + 16], 133),
            fontsize=11.5, fontweight="bold", color=ACCENT, ha="left", va="center",
            arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.4,
                            connectionstyle="arc3,rad=0.18"))

ax.set_ylim(60, 145)
ax.set_yticks([70, 90, 110, 130])
ax.set_yticklabels(["$70", "$90", "$110", "$130"])
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.tick_params(axis="y", labelsize=11, colors=MUTED, length=0)
ax.tick_params(axis="x", labelsize=12.5, colors=INK, length=0)
for lbl in ax.get_xticklabels():
    lbl.set_fontweight("bold")
ax.grid(axis="y", color=GRID, linewidth=1.0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#d8cbb0")

ax.set_title("Brent Crude Oil Crosses $90", fontsize=24, fontweight="bold",
             color=INK, loc="left", pad=26)
ax.text(0.0, 1.03, "Price per barrel (USD), daily  (Jan 20 to Jul 17, 2026)",
        transform=ax.transAxes, fontsize=12.5, color=MUTED, ha="left")

fig.text(0.012, 0.014,
         "Source: U.S. EIA Europe Brent spot price via FRED (DCOILBRENTEU); "
         "Jul 17 close per ICE",
         fontsize=9, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.062, right=0.975, top=0.84, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT)
