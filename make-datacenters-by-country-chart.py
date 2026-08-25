#!/usr/bin/env python3
"""
make-datacenters-by-country-chart.py  [out.png]

REALTY EXPERTS recreation of the "Where The World's 12,000 Data Centers Live"
graphic Harv supplied for the 08/25/26 daily email.

NAME NOTE: this is NOT make-datacenter-chart.py, which already exists and is a
different chart (U.S. data center construction SPENDING, built 06/23/26). Do not
merge or overwrite the two.

⚠️ TWO FIXES TO THE SUPPLIED GRAPHIC.

1. Its title says 12,000 while its own footer says ~11,700. Cloudscene's May 2026
   count is "more than 11,700 data centers operational worldwide", so the title
   overstated its own source by roughly 300. This chart says 11,700.

2. Its bars are not proportional. Germany (529), the United Kingdom (523), China
   (449), Canada (337) and France (316) are all drawn as identical width blocks,
   so a reader cannot see that Germany has two thirds more than France. Here every
   bar is drawn to scale, which is the whole point of a bar chart.

VALUES, all verified against reporting of the Cloudscene May 2026 count:
United States 5,427 (46% of the global total), Germany 529, United Kingdom 523,
China 449, Canada 337, France 316. Worldwide total more than 11,700.

⚠️ WHAT THE NUMBER IS NOT. This is a count of FACILITIES in Cloudscene's
directory, not capacity, floor space or power draw. A country with fewer, larger
sites can hold far more compute than one with many small ones, and directory
coverage varies by country, which is the most likely reason China's 449 sits
below Germany's 529. The chart says so on its face rather than letting the
ranking imply more than it can carry.

CREDIT LINE (new standing instruction, Harv, 08/25/26): our recreations now carry
"Created by Harv Balu" because the charts were being reshared without
attribution. This REVERSES the 06/29 rule that the footer carry only the data
source. See feedback-custom-chart-recreate-host-wordpress-show-first.md.

matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "datacenters-082526.png"

COUNTRIES = ["United States", "Germany", "United Kingdom", "China",
             "Canada", "France"]
COUNTS = [5427, 529, 523, 449, 337, 316]
WORLD_TOTAL = 11700

assert COUNTS == sorted(COUNTS, reverse=True), "bars must be ranked"
assert round(COUNTS[0] / WORLD_TOTAL * 100) == 46, "US share must be the reported 46%"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
SLATE = "#4a5568"
STEEL = "#7b8794"
GRID = "#d8cdb8"
MUTED = "#8a8172"

fig, ax = plt.subplots(figsize=(12.6, 7.0), dpi=170)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

ys = list(range(len(COUNTRIES)))[::-1]
colors = [CORAL] + [SLATE, SLATE, STEEL, STEEL, STEEL]

ax.barh(ys, COUNTS, height=0.62, color=colors, zorder=3)

for y, c, n in zip(ys, COUNTS, COUNTRIES):
    ax.text(c + 70, y, f"{c:,}", va="center", ha="left",
            fontsize=16, fontweight="bold",
            color=CORAL if c == COUNTS[0] else INK, zorder=5)

ax.text(COUNTS[0] - 120, ys[0], "46% of every data center on Earth",
        va="center", ha="right", fontsize=14.5, fontweight="bold",
        color="white", zorder=6)

ax.set_yticks(ys)
ax.set_yticklabels(COUNTRIES, fontsize=15, fontweight="bold")
ax.set_xlim(0, 6350)
ax.set_xticks([0, 1000, 2000, 3000, 4000, 5000])
ax.set_xticklabels(["0", "1,000", "2,000", "3,000", "4,000", "5,000"])

ax.grid(axis="x", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=13, colors=SLATE)
for lbl in ax.get_yticklabels():
    lbl.set_color(INK)

fig.text(0.046, 0.958, "Where the world's 11,700 data centers live",
         fontsize=26.5, fontweight="bold", color=INK, va="top")
fig.text(0.046, 0.897,
         "Data centers by country, and the one country that holds nearly half of them",
         fontsize=14, color=SLATE, va="top")

# Caveat block, parked in the open space to the right of the short bars.
ax.text(1520, 2.10, "What this counts, and what it does not",
        fontsize=13, color=INK, fontweight="bold", ha="left", va="center")
ax.text(1520, 1.14,
        "Facilities, not capacity. One large campus can hold more\n"
        "compute than a dozen small sites. Coverage also varies by\n"
        "country, the likeliest reason China sits below Germany.",
        fontsize=12.2, color=MUTED, ha="left", va="center", linespacing=1.75)
ax.plot([1440, 1440], [0.42, 2.30], color=GRID, lw=2.4, zorder=2)

fig.text(0.008, 0.022,
         "Source: Cloudscene, May 2026. More than 11,700 data centers operational "
         "worldwide.",
         fontsize=11, color=SLATE)
# Faint attribution watermark. Deliberately low contrast: present for credit,
# never competing with the data (Harv, 08/25/26).
fig.text(0.992, 0.022, "Created by Harv Balu",
         fontsize=9.5, color=MUTED, alpha=0.5, ha="right")

fig.subplots_adjust(left=0.175, right=0.988, top=0.805, bottom=0.115)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
for n, c in zip(COUNTRIES, COUNTS):
    print(f"  {n:16} {c:>6,}  ({c / WORLD_TOTAL * 100:4.1f}% of world)")
