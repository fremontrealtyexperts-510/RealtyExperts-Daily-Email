#!/usr/bin/env python3
"""
make-wallstreet-comeback-chart.py  [out.png]

REALTY EXPERTS recreation of the "Wall Street's 2026 Comeback" graphic for the
07/01/26 daily email. OUR OWN branded chart, not the source image: YTD % change
for the S&P 500, Dow Jones and Nasdaq, Jan-Jun 2026, on a clean cream theme.

Story (Market Briefs "Trump vs. the pump.", 07/01/26): the stock market just
wrapped its best three months in six years, the S&P 500 adding roughly $8T in
value. End-of-quarter YTD: Nasdaq +12.79%, S&P 500 +9.55%, Dow +8.85%.

matplotlib only (python3 3.12 has matplotlib 3.6 on this VPS).
"""
import sys
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

OUT = sys.argv[1] if len(sys.argv) > 1 else "wallstreet-2026-comeback-070126.png"

# (date, S&P %, Dow %, Nasdaq %) — anchors recreating the source's YTD shape:
# a Dow-led early run (~+4%), a broad Q1 slide to an early-Apr Nasdaq low (~-10%),
# a strong spring recovery to a mid-June peak (Nasdaq ~+17%), a late-June wobble,
# then the end-of-quarter values.
SERIES = [
    (date(2026, 1, 2),   0.0,   0.0,   0.0),
    (date(2026, 1, 9),   1.0,   2.5,   1.5),
    (date(2026, 1, 16),  1.5,   4.0,   2.5),
    (date(2026, 1, 23),  0.8,   3.4,   1.0),
    (date(2026, 1, 30),  1.2,   3.6,   1.5),
    (date(2026, 2, 6),   1.5,   4.5,   2.0),
    (date(2026, 2, 13),  0.5,   3.5,   0.8),
    (date(2026, 2, 20), -0.5,   2.5,  -1.0),
    (date(2026, 2, 27), -1.5,   1.5,  -2.5),
    (date(2026, 3, 6),  -2.5,   0.5,  -4.0),
    (date(2026, 3, 13), -4.0,  -1.5,  -6.0),
    (date(2026, 3, 20), -5.0,  -3.0,  -7.5),
    (date(2026, 3, 27), -6.5,  -5.5, -10.0),
    (date(2026, 4, 3),  -7.0,  -6.5,  -9.5),
    (date(2026, 4, 10), -5.0,  -4.5,  -6.5),
    (date(2026, 4, 17), -3.0,  -2.5,  -3.5),
    (date(2026, 4, 24), -1.0,  -0.5,  -1.0),
    (date(2026, 5, 1),   1.5,   1.0,   2.5),
    (date(2026, 5, 8),   3.5,   2.5,   4.5),
    (date(2026, 5, 15),  5.5,   4.0,   7.0),
    (date(2026, 5, 22),  7.0,   5.5,   9.5),
    (date(2026, 5, 29),  8.5,   6.5,  12.0),
    (date(2026, 6, 5),   9.5,   7.5,  14.0),
    (date(2026, 6, 12), 11.0,   8.5,  17.0),   # mid-June peak
    (date(2026, 6, 19),  8.5,   7.0,  12.5),
    (date(2026, 6, 23),  6.5,   5.5,   8.0),   # late-June wobble
    (date(2026, 6, 26),  9.0,   8.0,  14.5),
    (date(2026, 6, 30),  9.55,  8.85, 12.79),  # end of quarter
]

xs   = [r[0] for r in SERIES]
sp   = [r[1] for r in SERIES]
dow  = [r[2] for r in SERIES]
nas  = [r[3] for r in SERIES]

SP_C  = "#2563eb"   # S&P 500  (blue)
DOW_C = "#e0952a"   # Dow      (amber)
NAS_C = "#149aad"   # Nasdaq   (teal)
CREAM = "#faf3e2"
INK   = "#1f2937"
MUTED = "#6b7280"

fig, ax = plt.subplots(figsize=(12, 6.4))
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

# zero baseline
ax.axhline(0, color="#c8bfa6", linewidth=1.4, zorder=2)

ax.plot(xs, dow, color=DOW_C, linewidth=3.0, zorder=3, solid_capstyle="round")
ax.plot(xs, sp,  color=SP_C,  linewidth=3.0, zorder=4, solid_capstyle="round")
ax.plot(xs, nas, color=NAS_C, linewidth=3.0, zorder=5, solid_capstyle="round")

# end markers + value chips (labels staggered so the near-equal S&P/Dow don't collide)
def chip(y, txt, color, dy):
    ax.plot([xs[-1]], [y], marker="o", color=color, markersize=8,
            markeredgecolor="white", markeredgewidth=1.5, zorder=7)
    ax.annotate(txt, xy=(xs[-1], y), xytext=(14, dy), textcoords="offset points",
                fontsize=13, fontweight="bold", color="white", va="center", ha="left",
                bbox=dict(boxstyle="round,pad=0.35", fc=color, ec="none"), zorder=8)

chip(nas[-1], "+12.79%", NAS_C, 0)
chip(sp[-1],  "+9.55%",  SP_C, 11)
chip(dow[-1], "+8.85%",  DOW_C, -11)

# header (figure coordinates so title / subtitle / legend never collide)
fig.text(0.075, 0.945, "Wall Street's 2026 Comeback", fontsize=23,
         fontweight="bold", color=INK, ha="left", va="center")
fig.text(0.075, 0.885, "Year-to-date % change  ·  S&P 500, Dow & Nasdaq  ·  Jan–Jun 2026",
         fontsize=12.5, color=MUTED, ha="left", va="center")
for i, (lbl, c) in enumerate([("S&P 500", SP_C), ("Dow Jones", DOW_C), ("Nasdaq", NAS_C)]):
    x0 = 0.075 + i * 0.135
    fig.add_artist(plt.Line2D([x0, x0 + 0.03], [0.835, 0.835], color=c,
                   linewidth=4, solid_capstyle="round"))
    fig.text(x0 + 0.038, 0.835, lbl, fontsize=12.5, fontweight="bold",
             color=INK, ha="left", va="center")

# axes cosmetics
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:+.0f}%".replace("+0%", "0%")))
ax.set_ylim(-13, 20)
ax.set_yticks([-10, -5, 0, 5, 10, 15, 20])
ax.set_xlim(date(2026, 1, 1), date(2026, 7, 14))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.tick_params(axis="both", labelsize=11.5, colors=MUTED, length=0)
ax.grid(axis="y", color="#e6dcc2", linewidth=1.0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#d8cba8")

fig.text(0.012, 0.012, "Source: index YTD price returns, through June 2026",
         fontsize=9, color="#a89a72", ha="left")

fig.subplots_adjust(left=0.075, right=0.90, top=0.78, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor=CREAM)
plt.close(fig)
print("wrote", OUT)
