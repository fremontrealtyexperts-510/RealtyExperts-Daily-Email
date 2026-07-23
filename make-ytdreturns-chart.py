#!/usr/bin/env python3
"""
make-ytdreturns-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "Google, Tesla & IBM - 2026 YTD Returns"
graphic Harv supplied for the 07/23/26 daily email. OUR OWN branded chart, not the
source image: warm cream ground, three ranked lines (Alphabet blue, Tesla teal,
IBM orange), and rounded end-value pills carrying each stock's YTD return.

Story tie-in (Market Briefs "Roll Call", 07/23/26): Google, Tesla, and IBM all
reported earnings after the 07/22 close. Google beat but flagged heavier AI spend,
Tesla's sales rose while profit sank on AI/robotics, and IBM missed and fell on AI
fears. Their 2026 paths could hardly be more different, so it lands in Stocks.

Data: YTD price return through Jul 22, 2026 (Google Finance basis), transcribed
faithfully from the source graphic. End values are exact: Alphabet +9.29%,
Tesla -16.83%, IBM -30.53%. The weekly path between is read off the reference.

No authorship label on the chart (per Harv, 06/29): footer carries only the data
source. matplotlib only; build with python3.13 on Mac.
"""
import sys
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D

OUT = sys.argv[1] if len(sys.argv) > 1 else "ytdreturns-072326.png"

WEEKS = ["2026-01-02","2026-01-09","2026-01-16","2026-01-23","2026-01-30",
         "2026-02-06","2026-02-13","2026-02-20","2026-02-27","2026-03-06",
         "2026-03-13","2026-03-20","2026-03-27","2026-04-03","2026-04-10",
         "2026-04-17","2026-04-24","2026-05-01","2026-05-08","2026-05-15",
         "2026-05-22","2026-05-29","2026-06-05","2026-06-12","2026-06-19",
         "2026-06-26","2026-07-03","2026-07-10","2026-07-17","2026-07-22"]

# YTD % return per week, faithful to the reference graphic (exact end values).
GOOGL = [0, 2, 4, 6, 8, 7, 4, -2, -5, -3, 3, 10, 18, 24, 27, 25, 20, 22, 18, 16,
         18, 17, 19, 20, 17, 14, 11, 12, 11, 9.29]
TSLA  = [0, 1, 0, -3, -6, -9, -13, -17, -19, -17, -12, -13, -15, -13, -9, -6, -6,
         -7, -9, -6, -1, 8, 4, -1, -4, -6, -9, -12, -15, -16.83]
IBM   = [0, 3, 6, 8, 7, 3, -6, -15, -18, -19, -21, -22, -20, -19, -23, -25, -24,
         -24, -21, -15, -8, -1, 6, 11, 6, -3, -12, -20, -25, -30.53]
for name, s in (("GOOGL", GOOGL), ("TSLA", TSLA), ("IBM", IBM)):
    if len(s) != len(WEEKS):
        raise SystemExit(f"{name}: {len(s)} pts vs {len(WEEKS)} weeks")

dates = [datetime.strptime(d, "%Y-%m-%d") for d in WEEKS]

BLUE   = "#2563eb"   # Alphabet
TEAL   = "#0d9aa8"   # Tesla
ORANGE = "#d97706"   # IBM
INK    = "#12263f"
MUTED  = "#6b7280"
GROUND = "#fdf6e8"   # warm cream (house style)
GRID   = "#e7ddc9"

SERIES = [("Alphabet (GOOGL)", GOOGL, BLUE), ("Tesla (TSLA)", TSLA, TEAL),
          ("IBM", IBM, ORANGE)]

fig, ax = plt.subplots(figsize=(12, 6.4))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.axhline(0, color="#a99f88", linewidth=1.2, zorder=2)
for label, s, color in SERIES:
    ax.plot(dates, s, color=color, linewidth=2.8, zorder=4,
            solid_joinstyle="round", solid_capstyle="round")
    ax.scatter([dates[-1]], [s[-1]], s=42, color=color, zorder=6,
               edgecolor=GROUND, linewidth=1.6)

# end-value pills, nudged apart so they never overlap
ends = sorted([(s[-1], color) for _, s, color in SERIES], key=lambda t: t[0], reverse=True)
pill_y = {}
prev = None
for val, color in ends:
    y = val
    if prev is not None and prev - y < 7:
        y = prev - 7
    pill_y[color] = y
    prev = y
for label, s, color in SERIES:
    val = s[-1]
    ax.annotate(f"{val:+.2f}%", xy=(dates[-1], val),
                xytext=(dates[-1] + (dates[-1] - dates[-2]) * 1.6, pill_y[color]),
                fontsize=15, fontweight="bold", color="white", ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.45", fc=color, ec="none"), zorder=7,
                annotation_clip=False)

ax.set_ylim(-40, 32)
ax.set_yticks([-40, -30, -20, -10, 0, 10, 20, 30])
ax.set_yticklabels([f"{v}%" for v in [-40, -30, -20, -10, 0, 10, 20, 30]])
ax.set_xticks([datetime(2026, m, 1) for m in range(1, 8)])
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.tick_params(axis="y", labelsize=12, colors=MUTED, length=0)
ax.tick_params(axis="x", labelsize=13, colors=INK, length=0)
for lbl in ax.get_xticklabels():
    lbl.set_fontweight("bold")
ax.grid(axis="y", color=GRID, linewidth=1.0, linestyle=(0, (4, 4)))
ax.set_axisbelow(True)
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
ax.spines["bottom"].set_color("#d8cbb0")
ax.set_xlim(dates[0], dates[-1] + (dates[-1] - dates[-2]) * 3.2)

ax.set_title("Google, Tesla & IBM: 2026 YTD Returns", fontsize=24,
             fontweight="bold", color=INK, loc="left", pad=46)
# legend (proper handles so labels never overlap)
handles = [Line2D([0], [0], color=c, lw=3.2, marker="o", markersize=8,
                  markeredgecolor=GROUND, label=l) for l, s, c in SERIES]
leg = ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.0, 1.005),
                ncol=3, frameon=False, fontsize=13, handletextpad=0.4,
                columnspacing=1.8, borderaxespad=0)
for txt, (_, _, c) in zip(leg.get_texts(), SERIES):
    txt.set_color(c)
    txt.set_fontweight("bold")

fig.text(0.012, 0.014,
         "Source: Google Finance. YTD price return through Jul 22, 2026.",
         fontsize=9, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.058, right=0.90, top=0.80, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, "| weeks:", len(WEEKS),
      f"| ends GOOGL {GOOGL[-1]:+.2f} TSLA {TSLA[-1]:+.2f} IBM {IBM[-1]:+.2f}")
