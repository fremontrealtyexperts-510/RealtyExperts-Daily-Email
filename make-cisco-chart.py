#!/usr/bin/env python3
"""
make-cisco-chart.py  [out.png]

REALTY EXPERTS branded recreation of the "Cisco Stock, Year To Date" graphic for
the 08/13/26 daily email (Market Briefs "Insert coin." / the Good News Not Enough
story). OUR OWN branded chart, not the source image.

VERIFICATION against Yahoo Finance CSCO daily closes (chart API, range=1y):
  * 2026-08-12 close = $123.88  ->  the graphic's endpoint is EXACTLY right.
  * 2025-12-31 close = $77.03   ->  the graphic printed $76.71, which matches
    neither the raw close ($77.03) nor the dividend-adjusted close ($75.92).
    This chart uses raw closes throughout, which is what "closing price" means
    and what makes the YTD move +60.8%, matching the newsletter's "more than 60%
    this year."
  * The supplied graphic plotted ~9 monthly points. This one plots all 154 daily
    closes, so the actual path is visible rather than smoothed.

THE POINT OF THE UPDATE: the graphic ends on 08/12 with the stock at its highs,
but Cisco reported after that close, and the stock sold off hard the next
session. Publishing the YTD run without the reaction would have been a chart
that says "up 61%" on the exact day the stock gave back a ninth of its value.
The 08/13 SETTLED close is therefore drawn as a separate dashed segment and
labelled as its own day, not blended into the YTD line.

Run python3.13. Warm cream ground, no authorship label, footer = source only.
"""
import sys
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "cisco-081326.png"

# 2026-08-13 SETTLED close (regular session), pulled after the 4:00 PM ET bell.
REACTION_DATE = "2026-08-13"
REACTION_CLOSE = 113.47

# (ISO date, closing price USD). Source: Yahoo Finance CSCO daily closes.
SERIES = [
    ("2025-12-31", 77.03),
    ("2026-01-02", 76.04),
    ("2026-01-05", 75.58),
    ("2026-01-06", 75.23),
    ("2026-01-07", 74.72),
    ("2026-01-08", 73.96),
    ("2026-01-09", 73.88),
    ("2026-01-12", 74.01),
    ("2026-01-13", 75.47),
    ("2026-01-14", 74.41),
    ("2026-01-15", 75.25),
    ("2026-01-16", 75.19),
    ("2026-01-20", 73.35),
    ("2026-01-21", 73.69),
    ("2026-01-22", 74.33),
    ("2026-01-23", 74.59),
    ("2026-01-26", 77.01),
    ("2026-01-27", 78.68),
    ("2026-01-28", 78.96),
    ("2026-01-29", 78.43),
    ("2026-01-30", 78.32),
    ("2026-02-02", 80.64),
    ("2026-02-03", 83.11),
    ("2026-02-04", 81.16),
    ("2026-02-05", 82.36),
    ("2026-02-06", 84.82),
    ("2026-02-09", 86.78),
    ("2026-02-10", 86.29),
    ("2026-02-11", 85.54),
    ("2026-02-12", 75.00),
    ("2026-02-13", 76.85),
    ("2026-02-17", 76.85),
    ("2026-02-18", 78.18),
    ("2026-02-19", 78.56),
    ("2026-02-20", 79.20),
    ("2026-02-23", 77.74),
    ("2026-02-24", 78.14),
    ("2026-02-25", 79.12),
    ("2026-02-26", 78.10),
    ("2026-02-27", 79.46),
    ("2026-03-02", 79.42),
    ("2026-03-03", 78.96),
    ("2026-03-04", 80.87),
    ("2026-03-05", 80.01),
    ("2026-03-06", 78.64),
    ("2026-03-09", 76.21),
    ("2026-03-10", 77.70),
    ("2026-03-11", 78.10),
    ("2026-03-12", 77.74),
    ("2026-03-13", 78.33),
    ("2026-03-16", 78.90),
    ("2026-03-17", 79.27),
    ("2026-03-18", 77.60),
    ("2026-03-19", 78.51),
    ("2026-03-20", 77.65),
    ("2026-03-23", 78.82),
    ("2026-03-24", 80.86),
    ("2026-03-25", 81.83),
    ("2026-03-26", 82.16),
    ("2026-03-27", 79.92),
    ("2026-03-30", 77.04),
    ("2026-03-31", 77.59),
    ("2026-04-01", 77.93),
    ("2026-04-02", 79.02),
    ("2026-04-06", 80.44),
    ("2026-04-07", 80.68),
    ("2026-04-08", 83.70),
    ("2026-04-09", 83.17),
    ("2026-04-10", 82.22),
    ("2026-04-13", 82.35),
    ("2026-04-14", 82.61),
    ("2026-04-15", 82.36),
    ("2026-04-16", 84.50),
    ("2026-04-17", 86.25),
    ("2026-04-20", 87.71),
    ("2026-04-21", 89.70),
    ("2026-04-22", 89.80),
    ("2026-04-23", 88.59),
    ("2026-04-24", 89.01),
    ("2026-04-27", 88.26),
    ("2026-04-28", 86.86),
    ("2026-04-29", 89.57),
    ("2026-04-30", 91.50),
    ("2026-05-01", 91.85),
    ("2026-05-04", 92.63),
    ("2026-05-05", 94.30),
    ("2026-05-06", 91.64),
    ("2026-05-07", 92.16),
    ("2026-05-08", 96.57),
    ("2026-05-11", 98.72),
    ("2026-05-12", 99.29),
    ("2026-05-13", 101.87),
    ("2026-05-14", 115.53),
    ("2026-05-15", 118.21),
    ("2026-05-18", 118.88),
    ("2026-05-19", 115.38),
    ("2026-05-20", 114.35),
    ("2026-05-21", 118.20),
    ("2026-05-22", 120.41),
    ("2026-05-26", 118.33),
    ("2026-05-27", 119.67),
    ("2026-05-28", 118.64),
    ("2026-05-29", 120.42),
    ("2026-06-01", 121.33),
    ("2026-06-02", 128.00),
    ("2026-06-03", 126.50),
    ("2026-06-04", 130.00),
    ("2026-06-05", 121.64),
    ("2026-06-08", 124.15),
    ("2026-06-09", 120.36),
    ("2026-06-10", 118.80),
    ("2026-06-11", 121.83),
    ("2026-06-12", 121.10),
    ("2026-06-15", 120.17),
    ("2026-06-16", 119.57),
    ("2026-06-17", 117.33),
    ("2026-06-18", 119.54),
    ("2026-06-22", 121.53),
    ("2026-06-23", 121.15),
    ("2026-06-24", 119.73),
    ("2026-06-25", 118.97),
    ("2026-06-26", 113.77),
    ("2026-06-29", 117.70),
    ("2026-06-30", 117.46),
    ("2026-07-01", 117.01),
    ("2026-07-02", 112.69),
    ("2026-07-06", 113.98),
    ("2026-07-07", 111.79),
    ("2026-07-08", 113.82),
    ("2026-07-09", 118.31),
    ("2026-07-10", 121.31),
    ("2026-07-13", 119.25),
    ("2026-07-14", 117.09),
    ("2026-07-15", 111.77),
    ("2026-07-16", 109.66),
    ("2026-07-17", 111.94),
    ("2026-07-20", 110.70),
    ("2026-07-21", 112.18),
    ("2026-07-22", 112.21),
    ("2026-07-23", 112.76),
    ("2026-07-24", 114.17),
    ("2026-07-27", 114.57),
    ("2026-07-28", 115.58),
    ("2026-07-29", 112.48),
    ("2026-07-30", 113.56),
    ("2026-07-31", 115.99),
    ("2026-08-03", 115.86),
    ("2026-08-04", 121.74),
    ("2026-08-05", 121.50),
    ("2026-08-06", 120.88),
    ("2026-08-07", 121.43),
    ("2026-08-10", 122.57),
    ("2026-08-11", 120.43),
    ("2026-08-12", 123.88),]

TEAL   = "#1f7a99"   # the YTD line (Cisco's own blue, muted for our ground)
FILL   = "#bcd9e4"
CORAL  = "#c9532c"   # the earnings reaction
GROUND = "#FAF7F0"   # Meridian paper
INK    = "#2e2e2e"
MUTED  = "#8a8172"
GRID   = "#ddd5c6"

dates = [date.fromisoformat(d) for d, _ in SERIES]
vals  = [v for _, v in SERIES]
x = list(range(len(SERIES)))

start_v, end_v = vals[0], vals[-1]
ytd = (end_v / start_v - 1.0) * 100.0
reaction = (REACTION_CLOSE / end_v - 1.0) * 100.0
rx = len(SERIES)          # the 08/13 point sits one slot past the YTD series

Y_LO, Y_HI = 68, 140

fig, ax = plt.subplots(figsize=(12, 6.5))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.fill_between(x, vals, Y_LO, color=FILL, alpha=0.55, zorder=1)
ax.plot(x, vals, color=TEAL, linewidth=2.8, zorder=3, solid_capstyle="round")

# the earnings reaction, drawn as its own dashed leg so it is never read as
# part of the year to date run
ax.plot([x[-1], rx], [end_v, REACTION_CLOSE], color=CORAL, linewidth=2.6,
        linestyle=(0, (4, 3)), zorder=4)
ax.scatter([rx], [REACTION_CLOSE], s=165, color=CORAL, edgecolors=GROUND,
           linewidths=2.4, zorder=6)
ax.annotate("$%.2f\nAug 13 close, down %.1f%% after earnings"
            % (REACTION_CLOSE, abs(reaction)),
            xy=(rx, REACTION_CLOSE), xytext=(rx - 5, REACTION_CLOSE - 16.5),
            fontsize=12.5, fontweight="bold", color=CORAL, ha="right",
            linespacing=1.5,
            arrowprops=dict(arrowstyle="-", color=CORAL, linewidth=1.5))

# start and Aug 12 peak-of-the-run labels
ax.scatter([0], [start_v], s=120, color=GROUND, edgecolors=TEAL,
           linewidths=2.6, zorder=6)
ax.text(2.5, start_v - 5.5, "$%.2f" % start_v, fontsize=14, fontweight="bold",
        color=INK, ha="left", va="center", zorder=6)
ax.scatter([x[-1]], [end_v], s=150, color=TEAL, edgecolors=GROUND,
           linewidths=2.4, zorder=6)
ax.annotate("$%.2f" % end_v, xy=(x[-1], end_v), xytext=(x[-1] - 15, end_v + 8.5),
            fontsize=15, fontweight="bold", color=TEAL, ha="center",
            arrowprops=dict(arrowstyle="-", color=TEAL, linewidth=1.5))

for gy in range(70, 141, 10):
    ax.axhline(gy, color=GRID, linewidth=0.9, linestyle=(0, (5, 5)), zorder=0)

ax.set_title("Cisco Stock, Year To Date", fontsize=25, fontweight="bold",
             color=INK, loc="left", pad=38, x=-0.055)
ax.text(-0.055, 1.045,
        "Closing price  ·  Dec 31, 2025 to Aug 13, 2026  ·  up %.0f%% on the year "
        "before the earnings reaction" % ytd,
        transform=ax.transAxes, fontsize=13.5, color=MUTED, ha="left")

ax.set_xlim(0, rx + 3)
ax.set_ylim(Y_LO, Y_HI)
ax.set_yticks(list(range(70, 141, 10)))
ax.set_yticklabels(["$%d" % v for v in range(70, 141, 10)])

# month ticks. The series starts on Dec 31, so December owns a single point and
# its label would sit on top of January's; drop any tick closer than 5 points to
# the next one.
tick_pos, tick_lab = [], []
seen = set()
for i, d in enumerate(dates):
    key = (d.year, d.month)
    if key not in seen:
        seen.add(key)
        tick_pos.append(i)
        tick_lab.append(d.strftime("%b"))
keep = [j for j in range(len(tick_pos))
        if j == len(tick_pos) - 1 or tick_pos[j + 1] - tick_pos[j] >= 5]
tick_pos = [tick_pos[j] for j in keep]
tick_lab = [tick_lab[j] for j in keep]
ax.set_xticks(tick_pos)
ax.set_xticklabels(tick_lab)

ax.tick_params(axis="both", labelsize=14, colors=MUTED, length=0)
for lbl in ax.get_xticklabels() + ax.get_yticklabels():
    lbl.set_fontweight("bold")
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.spines["bottom"].set_linewidth(1.4)

fig.text(0.055, 0.028,
         "Source: Yahoo Finance, CSCO daily closing prices, Dec 31, 2025 to Aug 13, 2026",
         fontsize=11.5, color=MUTED, ha="left")

plt.subplots_adjust(left=0.075, right=0.975, top=0.815, bottom=0.135)
fig.savefig(OUT, dpi=170, facecolor=GROUND)
print("wrote", OUT)
print("  %s $%.2f -> %s $%.2f  YTD %+.2f%%" % (dates[0], start_v, dates[-1], end_v, ytd))
print("  %s settled $%.2f  (%+.2f%% on the earnings reaction)"
      % (REACTION_DATE, REACTION_CLOSE, reaction))
