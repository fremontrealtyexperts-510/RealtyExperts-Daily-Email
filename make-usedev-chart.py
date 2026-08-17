#!/usr/bin/env python3
"""
make-usedev-chart.py  [out.png]

REALTY EXPERTS chart for the 08/17/26 daily email, built for the "used EV prices
are climbing again" story Harv supplied as a graphic.

⚠️ REBUILT ON A DIFFERENT SERIES THAN THE SUPPLIED GRAPHIC, ON PURPOSE.

The supplied graphic was labeled "Manheim average used EV value, monthly" and ran
2018 to 2026 with a $38.1K peak in mid 2022 and a $29.4K endpoint. Three problems
turned up when the numbers were re-pulled:

  1. Manheim does NOT publish a dollar average for used EVs. Cox Automotive
     publishes the Manheim EV Index in INDEX POINTS (July 2026 = 211.6, up 10.5%
     year over year, vs the Non-EV Index at 149.3, up 0.4%). Confirmed in the
     July 2026 Manheim release and in WardsAuto's writeup of it. No dollars.
  2. The $29.4K endpoint contradicts the actual published dollar series. Cox's
     average used EV LISTING price was $38,342 in June 2026, not $29.4K.
  3. $29,400 appears to be Recurrent's "average minimum listing price" from a Q1
     2026 report, a different metric from a different company in a stale quarter.

So the graphic's headline claim is TRUE and well supported, but its dollar series
is not sourceable. Per the standing rule that a supplied graphic is a design
brief and not a data source, this chart keeps the story and rebuilds it on the
series that IS published month by month in dollars:

  Cox Automotive EV Market Monitor, average used EV listing price, monthly.

Every point below is a figure stated directly in that month's own report, not
interpolated. Cross-check that the series is coherent: the April 2026 report
calls April "the first positive year-over-year reading since July 2025", and
July 2025 is indeed the last positive YoY in this series at +1.6%.

Story: the series bottomed at $34,653 in March 2026 and has risen four straight
months to $38,342 in June, up 10.6% off the low and up 7.0% year over year. The
October 2025 jump is the federal EV tax credit expiring on 09/30/2025.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
from decimal import Decimal, ROUND_HALF_UP
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "usedev-081726.png"

# (label, average used EV listing price) -- each from that month's Cox EV Market Monitor
DATA = [
    ("Jul\n2025", 35263),
    ("Aug",       34704),
    ("Sep",       34575),
    ("Oct",       37538),
    ("Nov",       36440),
    ("Dec",       36408),
    ("Jan\n2026", 35442),
    ("Feb",       34821),
    ("Mar",       34653),
    ("Apr",       35895),
    ("May",       37083),
    ("Jun",       38342),
]

INK    = "#12263f"
CORAL  = "#e2574c"
GREEN  = "#2f8f5b"
MUTED  = "#6b7280"
GROUND = "#fdf6e8"   # warm cream (house style)
GRID   = "#e7ddc9"

labels = [d[0] for d in DATA]
vals   = [d[1] for d in DATA]
x      = list(range(len(DATA)))

# Mar 2026 is the local low that STARTS the current run, not the 12-month min
# (Sep 2025 prints $34,575, a hair lower, but the climb dates from March).
TROUGH = [i for i, d in enumerate(DATA) if d[0] == "Mar"][0]
LAST   = len(vals) - 1           # Jun 2026
assert vals[TROUGH] == 34653, "March 2026 anchor moved"


def money(n):
    return "$" + format(int(Decimal(n).quantize(Decimal("1"), rounding=ROUND_HALF_UP)), ",")


fig, ax = plt.subplots(figsize=(12.6, 6.8))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

# area fill under the line
ax.fill_between(x, vals, 33200, color=CORAL, alpha=0.13, zorder=2)
ax.plot(x, vals, color=CORAL, linewidth=3.4, zorder=5, solid_capstyle="round")

# shade the four month climb
ax.axvspan(TROUGH, LAST, color=GREEN, alpha=0.055, zorder=1)

# trough callout
ax.plot([TROUGH], [vals[TROUGH]], "o", color=CORAL, markersize=10, zorder=7)
ax.annotate(f"{money(vals[TROUGH])}\nMarch low",
            xy=(TROUGH, vals[TROUGH]), xytext=(TROUGH - 0.85, 33900),
            fontsize=12.5, fontweight="bold", color=MUTED, ha="center",
            va="top", zorder=8, annotation_clip=False)

# current value pill
ax.plot([LAST], [vals[LAST]], "o", color=CORAL, markersize=11, zorder=7)
ax.annotate(money(vals[LAST]), xy=(LAST, vals[LAST]),
            xytext=(LAST + 0.62, vals[LAST]),
            fontsize=19, fontweight="bold", color="white", va="center",
            ha="center", zorder=9, annotation_clip=False,
            bbox=dict(boxstyle="round,pad=0.42", facecolor=CORAL,
                      edgecolor="none"))

# the climb, stated once, above the shaded band
ax.text((TROUGH + LAST) / 2.0, 39050,
        "Four straight monthly gains, up 10.6% off the March low",
        fontsize=12.5, fontweight="bold", color=GREEN, ha="center", va="bottom",
        zorder=8)

ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=11.5, fontweight="bold", color=MUTED)
ax.set_ylim(33200, 39600)
ax.set_yticks([34000, 35000, 36000, 37000, 38000, 39000])
ax.set_yticklabels(["$34K", "$35K", "$36K", "$37K", "$38K", "$39K"],
                   fontsize=12, color=MUTED)
ax.set_xlim(-0.75, len(DATA) + 0.55)
ax.grid(axis="y", color=GRID, linewidth=1.1, linestyle=(0, (5, 5)), zorder=0)
ax.tick_params(length=0)
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("Used EV Prices Are Climbing Again", fontsize=25,
             fontweight="bold", color=INK, loc="left", pad=42)
ax.text(0.0, 1.045, "Average used EV listing price, monthly. June 2026 is up "
        "7.0% year over year, the strongest reading in over a year.",
        transform=ax.transAxes, fontsize=12.5, color=MUTED, ha="left")

fig.text(0.012, 0.014, "Source: Cox Automotive EV Market Monitor, average used "
         "EV listing price", fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.062, right=0.925, top=0.815, bottom=0.125)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, "| months:", len(DATA),
      "| trough", labels[TROUGH].replace("\n", " "), money(vals[TROUGH]),
      "| latest Jun 2026", money(vals[LAST]),
      "| off low +%.1f%%" % ((vals[LAST] / vals[TROUGH] - 1) * 100))
