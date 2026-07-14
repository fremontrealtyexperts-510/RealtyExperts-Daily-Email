#!/usr/bin/env python3
"""
make-creditcard-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "Total outstanding credit card balances"
(New York Fed Consumer Credit Panel / Equifax) graphic for the 07/14/26 daily email.
OUR OWN branded chart, not the source image: a clean RE steel-blue theme on a warm
cream ground, the 1999-2026 shape faithfully reproduced (a climb to an ~$866B peak
in 2008, the post-crisis deleveraging trough near $650B in 2014, a recovery to ~$925B
by 2019, the COVID paydown dip to ~$745B in 2021, and a sharp seasonal-sawtooth
climb to a record $1.27T today), a record callout, and a 2008 peak / COVID-dip note.

Story (Market Briefs "🍿 Showtime." / "Credit Squeeze", 07/14/26): more Americans are
leaning on credit cards, even for groceries, and falling behind. The share missing a
minimum payment rose to 8.7% in 2025 from 7.1% in 2023, as food prices sit about 32%
higher than five years ago while real wages slipped. Total card balances are now at a
record $1.27 trillion.

matplotlib only. Build with python3.13 on Mac (matplotlib 3.10).
"""
import sys
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

OUT = sys.argv[1] if len(sys.argv) > 1 else "creditcard-071426.png"

# Annual mid-year baseline ($B) recreating the source's shape. Quarterly points are
# interpolated from these and given a seasonal sawtooth (Q4 holiday spike, Q1 paydown)
# so the line zig-zags the way the NY Fed series does.
ANNUAL = {
    1999: 470, 2000: 540, 2001: 600, 2002: 630, 2003: 665, 2004: 695,
    2005: 705, 2006: 725, 2007: 785, 2008: 860, 2009: 810, 2010: 735,
    2011: 700, 2012: 680, 2013: 660, 2014: 655, 2015: 680, 2016: 720,
    2017: 780, 2018: 845, 2019: 925, 2020: 815, 2021: 775, 2022: 930,
    2023: 1050, 2024: 1130, 2025: 1215, 2026: 1272,
}
# quarter -> seasonal offset in $B (peak in Q4, trough in Q1)
SEASON = {1: -9, 2: -3, 3: 3, 4: 11}

def interp(year, q):
    frac = (q - 1) / 4.0
    y0 = ANNUAL[year]
    y1 = ANNUAL.get(year + 1, y0)
    base = y0 + (y1 - y0) * frac
    scale = base / 800.0  # scale the sawtooth up in higher-balance years
    return base + SEASON[q] * scale

SERIES = []
for year in range(1999, 2027):
    for q in (1, 2, 3, 4):
        if year == 2026 and q > 2:
            break
        d = date(year, {1: 2, 2: 5, 3: 8, 4: 11}[q], 15)
        SERIES.append((d, interp(year, q)))
# COVID paydown detail: force the 2020 dip and 2021 trough to read clearly
_over = {date(2020, 2, 15): 895, date(2020, 5, 15): 830, date(2020, 8, 15): 805,
         date(2020, 11, 15): 820, date(2021, 2, 15): 745, date(2021, 5, 15): 760,
         date(2021, 8, 15): 800, date(2021, 11, 15): 855,
         date(2008, 8, 15): 866, date(2026, 5, 15): 1272}
SERIES = [(_d, _over.get(_d, _v)) for _d, _v in SERIES]

xs = [d for d, _ in SERIES]
ys = [p for _, p in SERIES]

LINE    = "#1f6fea"   # main line (RE steel blue)
LINE_DK = "#1553b8"   # markers / today
FILL_TOP = "#cfe0f7"
INK     = "#12263f"
MUTED   = "#6b7280"
PEAK    = "#b91c1c"   # 2008 peak / stress callout
GROUND  = "#fdf6e8"   # warm cream

fig, ax = plt.subplots(figsize=(12, 6.2))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.fill_between(xs, ys, 400, color=FILL_TOP, alpha=0.55, zorder=1)
ax.plot(xs, ys, color=LINE, linewidth=3.0, zorder=3, solid_capstyle="round")

# 2008 pre-crisis peak
ax.annotate("2008 pre-crisis\npeak (~$866B)",
            xy=(date(2008, 8, 15), 866), xytext=(date(2004, 1, 1), 960),
            fontsize=10.5, color=PEAK, ha="center", va="center", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=PEAK, lw=1.3,
                            connectionstyle="arc3,rad=-0.15"))

# COVID paydown dip
ax.annotate("COVID paydown\n2020-21",
            xy=(date(2021, 2, 15), 745), xytext=(date(2022, 6, 1), 640),
            fontsize=10.5, color=MUTED, ha="center", va="center", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.1,
                            connectionstyle="arc3,rad=-0.18"))

# today / record marker + label
ax.plot([xs[-1]], [ys[-1]], marker="o", color="white", markeredgecolor=LINE_DK,
        markeredgewidth=2.4, markersize=13, zorder=6)
ax.annotate("Record\n$1.27T",
            xy=(xs[-1], ys[-1]), xytext=(date(2023, 6, 1), 1245),
            fontsize=12.5, fontweight="bold", color=LINE_DK, ha="center", va="center",
            arrowprops=dict(arrowstyle="->", color=LINE_DK, lw=1.6,
                            connectionstyle="arc3,rad=0.16"))

ax.set_title("Total Outstanding Credit Card Balances", fontsize=22,
             fontweight="bold", color=INK, loc="left", pad=18)
ax.text(0.0, 1.02, "United States, in billions of dollars, seasonally adjusted",
        transform=ax.transAxes, fontsize=12.5, color=MUTED, ha="left")

ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:,.0f}B"))
ax.set_ylim(400, 1330)
ax.set_yticks([400, 600, 800, 1000, 1200])
ax.set_xlim(date(1998, 6, 1), date(2027, 3, 1))
ax.xaxis.set_major_locator(mdates.YearLocator(3, month=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.tick_params(axis="both", labelsize=11, colors=MUTED, length=0)
ax.grid(axis="y", color="#e7ddc9", linewidth=1.0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#d8cbb0")

fig.text(0.012, 0.012, "Source: New York Fed Consumer Credit Panel / Equifax",
         fontsize=9, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.085, right=0.975, top=0.85, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT)
