#!/usr/bin/env python3
"""
make-ibm-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "IBM Common Stock YTD" graphic for the
07/15/26 daily email. OUR OWN branded chart, not the source image: a clean red
decline line with a soft red area fill on a warm cream ground, the year-to-date 2026
path faithfully reproduced (a ~$296 open, a choppy slide through the spring, a sharp
late-May spike, an early-July bounce to ~$307, and then the cliff to $217.07 on the
earnings miss), with a "worst day since 1987" callout at the final drop.

Story (Market Briefs "⏳ Back in time." / "Back To The '80s", 07/15/26): IBM had its
worst day since 1987, falling about 25% after it missed quarterly earnings and warned
results could get worse. Investors had hoped its AI and chip business would scale;
the numbers said otherwise. The stock closed at $217.07, down 26.72% ($79.14) YTD.

matplotlib only. Build with python3.13 on Mac (matplotlib 3.10). No IBM logo (their
trademark); RE-branded cream style only.
"""
import sys
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

OUT = sys.argv[1] if len(sys.argv) > 1 else "ibm-ytd-071526.png"

# (date, close $) YTD-2026 anchors recreating the source's path, ending at $217.07.
A = [
 (date(2026,1,2),293),(date(2026,1,9),300),(date(2026,1,16),308),(date(2026,1,23),313),(date(2026,1,30),302),
 (date(2026,2,6),297),(date(2026,2,13),305),(date(2026,2,20),316),(date(2026,2,27),296),
 (date(2026,3,6),262),(date(2026,3,13),258),(date(2026,3,20),223),(date(2026,3,27),259),
 (date(2026,4,3),255),(date(2026,4,10),244),(date(2026,4,17),248),(date(2026,4,24),240),
 (date(2026,5,1),235),(date(2026,5,8),223),(date(2026,5,13),215),(date(2026,5,20),250),(date(2026,5,26),331),
 (date(2026,6,2),288),(date(2026,6,9),270),(date(2026,6,16),272),(date(2026,6,23),258),(date(2026,6,30),250),
 (date(2026,7,7),285),(date(2026,7,9),307),(date(2026,7,11),297),(date(2026,7,13),289),(date(2026,7,14),217.07),
]
xs = [d for d, _ in A]
ys = [v for _, v in A]

LINE   = "#dc2626"   # red decline line
FILL   = "#f6cccc"
INK    = "#12263f"
MUTED  = "#6b7280"
DROP   = "#b91c1c"
GROUND = "#fdf6e8"

fig, ax = plt.subplots(figsize=(12, 6.2))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.fill_between(xs, ys, 200, color=FILL, alpha=0.6, zorder=1)
ax.plot(xs, ys, color=LINE, linewidth=2.8, zorder=3, solid_capstyle="round")

# worst-day callout at the final crash
ax.annotate("Worst day since 1987\non the earnings miss",
            xy=(date(2026, 7, 14), 217.07), xytext=(date(2026, 5, 6), 250),
            fontsize=11.5, fontweight="bold", color=DROP, ha="center", va="center",
            arrowprops=dict(arrowstyle="->", color=DROP, lw=1.6,
                            connectionstyle="arc3,rad=0.2"))

# endpoint marker + price
ax.plot([xs[-1]], [ys[-1]], marker="o", color=DROP, markeredgecolor="white",
        markeredgewidth=1.8, markersize=13, zorder=6)
ax.annotate(r"\$217.07",
            xy=(xs[-1], ys[-1]), xytext=(date(2026, 7, 6), 228),
            fontsize=12.5, fontweight="bold", color=DROP, ha="center", va="center")

ax.set_title("IBM Common Stock, Year to Date", fontsize=22,
             fontweight="bold", color=INK, loc="left", pad=18)
ax.text(0.0, 1.02, r"Daily close in 2026    \$217.07    down 26.72% (\$79.14) YTD",
        transform=ax.transAxes, fontsize=12.5, color=DROP, ha="left", fontweight="bold")

ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:,.0f}"))
ax.set_ylim(200, 340)
ax.set_yticks([200, 220, 240, 260, 280, 300, 320, 340])
ax.set_xlim(date(2025, 12, 25), date(2026, 7, 25))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.tick_params(axis="both", labelsize=11, colors=MUTED, length=0)
ax.grid(axis="y", color="#e7ddc9", linewidth=0.9)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#d8cbb0")

fig.text(0.012, 0.012, "Source: NYSE, market data as of Jul 14, 2026",
         fontsize=9, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.075, right=0.975, top=0.84, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT)
