#!/usr/bin/env python3
"""
make-refinery-runs-chart.py  [out.png]

REALTY EXPERTS recreation of the "How much oil the world is refining" graphic
Harv supplied for the 08/24/26 daily email. Same design language (current year
vs prior year vs five year average, endpoint callouts), rebuilt on a series we
can actually verify.

WHY THE SUBJECT CHANGED FROM WORLD TO U.S.
The supplied graphic credits Energy Aspects, a private consultancy whose global
refinery runs series is proprietary and not published anywhere we can check. Its
levels (2025 running 88 to 93 million b/d) also sit well above the 82 to 85
million b/d range normally quoted for global refinery throughput, and its 2026
line implies a 6 million b/d year over year collapse. None of that could be
sourced, and the house rule is to drop what cannot be sourced rather than
republish it. So this chart shows the U.S. picture, from the U.S. Energy
Information Administration's own weekly series, which is the half of the story
that actually touches the newsletter's claim about U.S. refineries and Canadian
crude.

⚠️ AND THE NEWSLETTER'S CLAIM DOES NOT SURVIVE THE CHECK. Market Briefs wrote on
08/24/26 that "U.S. refinery output has been falling." EIA's weekly data says
the opposite: refiner net input of crude oil for the week ending August 14, 2026
was 17.395 million b/d, the highest week of the year, ABOVE the same week of
2025 (17.208) and well above the five year average for that week (16.587).
Utilization is averaging 93.1 percent year to date versus 90.0 percent last
year. U.S. refinery runs are at a seasonal high, not falling.

DATA PROVENANCE. EIA weekly series WCRRIUS2, "U.S. Refiner Net Input of Crude
Oil", thousand barrels per day, downloaded direct from
https://www.eia.gov/dnav/pet/hist_xls/WCRRIUS2w.xls (no API key needed, parsed
with pandas + xlrd). Series runs 1982-08-20 to 2026-08-14. Values are converted
to million b/d. The five year average is the mean of 2021 through 2025 at each
week index. 2026 carries 33 weekly observations, ending the week of August 14;
the next EIA release lands Wednesday August 26, so the line stops there rather
than being extended.

Weeks are aligned by ordinal week index within each year, which is how EIA's own
seasonal comparisons are built.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

OUT = sys.argv[1] if len(sys.argv) > 1 else "refinery-runs-082426.png"

# --- EIA WCRRIUS2, million b/d, by ordinal week index within the year ---------
CUR = [16.909, 16.958, 16.604, 16.209, 16.029, 16.000, 16.077, 15.661, 15.841,
       16.169, 16.232, 16.598, 16.379, 16.250, 16.042, 15.987, 16.071, 16.029,
       16.399, 16.319, 16.971, 16.881, 16.962, 17.192, 17.111, 17.196, 17.024,
       17.123, 17.065, 17.336, 17.153, 17.179, 17.395]

PREV = [16.902, 16.647, 15.522, 15.189, 15.349, 15.431, 15.416, 15.733, 15.387,
        15.708, 15.663, 15.750, 15.558, 15.627, 15.564, 15.889, 16.078, 16.071,
        16.401, 16.490, 16.328, 16.998, 17.226, 16.862, 16.987, 17.105, 17.006,
        16.849, 16.936, 16.911, 17.124, 17.180, 17.208, 16.880, 16.869, 16.818,
        16.424, 16.476, 16.168, 16.297, 15.130, 15.730, 15.219, 15.256, 15.973,
        16.232, 16.443, 16.876, 16.860, 16.988, 16.776, 16.847]

AVG5 = [15.604, 15.651, 15.207, 14.993, 15.163, 14.939, 15.013, 14.603, 14.180,
        14.935, 15.227, 15.559, 15.592, 15.512, 15.618, 15.608, 15.588, 15.741,
        15.920, 16.085, 16.170, 16.555, 16.621, 16.539, 16.510, 16.533, 16.706,
        16.555, 16.371, 16.261, 16.521, 16.603, 16.587, 16.531, 16.452, 16.140,
        15.989, 15.998, 15.767, 15.703, 15.378, 15.486, 15.483, 15.587, 15.880,
        15.954, 16.208, 16.441, 16.305, 16.349, 16.423, 15.981]

assert len(CUR) == 33, "2026 must stop at the week ending August 14"
assert len(PREV) == 52 and len(AVG5) == 52
assert abs(CUR[-1] - 17.395) < 1e-9, "endpoint must be the published Aug 14 figure"
assert CUR[-1] > PREV[len(CUR) - 1] > AVG5[len(CUR) - 1], "2026 > 2025 > 5yr avg"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
SLATE = "#4a5568"
GOLD = "#d99a2b"
GRID = "#d8cdb8"

fig, ax = plt.subplots(figsize=(12.4, 6.9), dpi=170)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

x_cur = list(range(1, len(CUR) + 1))
x_full = list(range(1, 53))

ax.plot(x_full, AVG5, color=GOLD, lw=2.6, ls=(0, (6, 3)), zorder=3,
        label="5 year average (2021 to 2025)")
ax.plot(x_full, PREV, color=SLATE, lw=2.6, zorder=4, label="2025")
ax.plot(x_cur, CUR, color=CORAL, lw=4.2, zorder=6, solid_capstyle="round",
        label="2026")
ax.plot([x_cur[-1]], [CUR[-1]], "o", color=CORAL, ms=10, zorder=7,
        markeredgecolor=CREAM, markeredgewidth=2)

# --- endpoint callouts, same idea as the supplied graphic ---------------------
def callout(x, y, text, face, textcolor, dx=1.4, dy=0.0):
    ax.annotate(text, xy=(x, y), xytext=(x + dx, y + dy),
                va="center", ha="left", fontsize=15, fontweight="bold",
                color=textcolor, zorder=9,
                bbox=dict(boxstyle="round,pad=0.42", fc=face, ec="none"))

callout(x_cur[-1], CUR[-1], "17.40", CORAL, "white", dx=1.4, dy=0.30)
callout(52, PREV[-1], "16.85", SLATE, "white", dx=0.9)
callout(52, AVG5[-1], "15.98", GOLD, INK, dx=0.9, dy=-0.16)

fig.text(0.055, 0.955, "How much oil the U.S. is refining",
         fontsize=27, fontweight="bold", color=INK, va="top")
fig.text(0.055, 0.885, "Refinery crude runs, million barrels per day, weekly",
         fontsize=14.5, color=SLATE, va="top")

ax.set_xlim(0.2, 57.5)
ax.set_ylim(13.9, 17.95)
ax.set_yticks([14.0, 14.5, 15.0, 15.5, 16.0, 16.5, 17.0, 17.5])
ax.set_yticklabels([f"{t:.1f}" for t in ax.get_yticks()])

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
ax.set_xticks([round((m * 52) / 12) + 1 for m in range(12)])
ax.set_xticklabels(MONTHS)

ax.grid(axis="y", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=13.5, colors=SLATE)

leg = ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.015), ncol=3,
                frameon=False, fontsize=13.5, handlelength=2.6,
                columnspacing=2.2)
for t in leg.get_texts():
    t.set_color(INK)
    t.set_fontweight("bold")

ax.text(24.0, 17.60, "Week ending Aug 14, 2026:\nhighest week of the year",
        fontsize=12.6, color=CORAL, fontweight="bold", ha="center", va="center")

fig.text(0.008, 0.022,
         "Source: U.S. Energy Information Administration, weekly refiner net "
         "input of crude oil (series WCRRIUS2), through the week ending "
         "August 14, 2026.",
         fontsize=11, color=SLATE)

fig.subplots_adjust(left=0.055, right=0.985, top=0.795, bottom=0.115)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
print(f"  2026 latest        {CUR[-1]:.3f} million b/d (week 33, ending Aug 14)")
print(f"  2025 same week     {PREV[len(CUR)-1]:.3f}")
print(f"  5yr avg same week  {AVG5[len(CUR)-1]:.3f}")
