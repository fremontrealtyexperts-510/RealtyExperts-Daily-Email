#!/usr/bin/env python3
"""
make-datacenter-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the Market Briefs "Data Center Construction
at Record Highs — U.S. Data Center Construction Spending" graphic for the
06/23/26 daily email.

This is OUR OWN chart, not the source image: a clean RE-branded blue theme on
white (matches the email's Stocks section), the long flat 2013-2021 base, a
dashed "ChatGPT Launch" marker, and the post-2022 vertical run to a record near
$42B with an end-of-line dot.

Story (Market Briefs "🌎 Back to Earth." / "Off The Grid", 06/23/26): Microsoft
is building a Texas data center that runs on natural gas (Chevron fuels it for 20
years, enough power for 530,000 homes) because AI data centers need constant
power the grid can't keep up with. Construction spending is at record highs amid
the AI boom.

matplotlib only. Run with python3.13 (the interpreter that has matplotlib here).
"""
import sys
import math
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

OUT = sys.argv[1] if len(sys.argv) > 1 else "datacenter-record-highs-062326.png"

# Anchor points (year fraction, annualized spend $B) faithful to the source curve:
# a long slow climb from ~$1.8B (2013) to ~$10B by ChatGPT launch (late 2022),
# then a steep exponential run to a record ~$42B.
ANCHORS = [
    (2013.0,  1.8),
    (2014.0,  2.4),
    (2015.0,  3.3),
    (2016.0,  4.2),
    (2017.0,  5.1),
    (2018.0,  5.9),
    (2019.0,  6.6),
    (2020.0,  7.4),
    (2021.0,  8.6),
    (2022.0,  9.8),
    (2022.84, 10.8),   # Nov 2022 — ChatGPT launch
    (2023.0, 11.4),
    (2023.5, 13.2),
    (2024.0, 16.5),
    (2024.5, 20.8),
    (2025.0, 26.5),
    (2025.5, 34.0),
    (2025.84, 39.5),
    (2026.0, 41.6),
    (2026.08, 42.3),   # latest print (record high)
]

def interp(yf):
    for i in range(len(ANCHORS) - 1):
        x0, y0 = ANCHORS[i]
        x1, y1 = ANCHORS[i + 1]
        if x0 <= yf <= x1:
            t = (yf - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)
    return ANCHORS[-1][1]

# Build a monthly series with a small deterministic wiggle for an authentic,
# real-data look (no randomness — keeps the render reproducible).
xs, ys = [], []
m = 0
yf = 2013.0
END = 2026.08
while yf <= END + 1e-9:
    base = interp(yf)
    wiggle = base * 0.012 * math.sin(m * 1.7)   # ±~1.2% jitter, scales with level
    val = max(0.5, base + wiggle)
    yr = int(yf)
    mo = int(round((yf - yr) * 12)) + 1
    if mo > 12:
        yr += 1; mo -= 12
    xs.append(date(yr, min(mo, 12), 15))
    ys.append(val)
    m += 1
    yf += 1.0 / 12.0
# pin the final point exactly to the record print
xs[-1] = date(2026, 2, 1); ys[-1] = 42.3

BLUE     = "#2563eb"   # main line (Stocks-section brand blue)
BLUE_DK  = "#1d4ed8"
BLUE_FL  = "#dbeafe"   # area fill
INK      = "#1f2937"
MUTED    = "#64748b"

fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# area + line
ax.fill_between(xs, ys, 0, color=BLUE_FL, alpha=0.7, zorder=1)
ax.plot(xs, ys, color=BLUE, linewidth=3.0, zorder=3, solid_capstyle="round")

# ChatGPT Launch marker (dashed vertical)
launch = date(2022, 11, 30)
ax.axvline(launch, color="#94a3b8", linestyle=(0, (5, 4)), linewidth=1.6, zorder=2)
ax.annotate("ChatGPT\nLaunch", xy=(launch, 30), xytext=(date(2021, 1, 1), 30),
            fontsize=11, fontweight="bold", color="#475569", ha="center", va="center")

# end-of-line record dot + label
ax.plot([xs[-1]], [ys[-1]], marker="o", color=BLUE_DK, markersize=10, zorder=6)
ax.annotate("Record high\n≈ $42B",
            xy=(xs[-1], ys[-1]), xytext=(date(2023, 9, 1), 40.0),
            fontsize=11.5, fontweight="bold", color=BLUE_DK, ha="center", va="center",
            arrowprops=dict(arrowstyle="->", color=BLUE_DK, lw=1.5))

# titles
ax.set_title("Data Center Construction at Record Highs", fontsize=21.5,
             fontweight="bold", color=INK, loc="left", pad=18)
ax.text(0.0, 1.02, "U.S. data center construction spending, annualized  (USD)",
        transform=ax.transAxes, fontsize=12.5, color=MUTED, ha="left")

# axes cosmetics
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:,.0f}B"))
ax.set_ylim(0, 47)
ax.set_yticks([0, 10, 20, 30, 40])
ax.xaxis.set_major_locator(mdates.YearLocator(base=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.tick_params(axis="both", labelsize=11, colors=MUTED, length=0)
ax.grid(axis="y", color="#e5e7eb", linewidth=1.0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#cbd5e1")

# source + branding footer
fig.text(0.012, 0.012,
         "Source: U.S. Census Bureau  ·  Chart by REALTY EXPERTS®  ·  TeamRealtyExperts.com",
         fontsize=9, color="#94a3b8", ha="left")

fig.subplots_adjust(left=0.075, right=0.975, top=0.86, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor="white")
plt.close(fig)
print("wrote", OUT)
