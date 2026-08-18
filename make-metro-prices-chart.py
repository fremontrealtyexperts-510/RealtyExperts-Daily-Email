#!/usr/bin/env python3
"""
make-metro-prices-chart.py  [out.png]

REALTY EXPERTS recreation of the "most expensive metros" graphic Harv supplied for
the 08/05/26 daily email. OUR OWN branded chart: warm cream ground, Real-Estate
orange, and the two Bay Area metros carried in the strong tone because those are
the markets our Fremont readers actually shop against.

Story tie-in (Market Briefs "Money Metros", 08/05/26): NAR's quarterly metro price
report. Prices rose in 80% of metro areas last quarter, but the West was the only
region that fell. That is a housing story, so it lands in the Real Estate section.

Data: National Association of REALTORS, median existing single-family home price,
Q2 2026, pulled from NAR's own release rather than transcribed from the graphic.

TWO CORRECTIONS vs the supplied graphic:
  1. It showed San Diego at $1.07M. NAR reports $1,075,000, which rounds to
     $1.08M.
  2. It showed only six metros and stopped at Salinas. NAR publishes a top ten,
     and the four it dropped (Oxnard, San Luis Obispo, Bridgeport, Los Angeles)
     carry the actual point: eight of the ten priciest metros in the country are
     in California, and Los Angeles was dead flat year over year. The full ten
     are charted here.
Every value below matches NAR's published table; nothing is inferred.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
from decimal import Decimal, ROUND_HALF_UP
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "metro-prices-080526.png"

# (metro, median price $, year-over-year %) - NAR, Q2 2026
DATA = [
    ("San Jose, CA",     2_050_000, -4.2),
    ("San Francisco, CA", 1_500_000, +5.2),
    ("Anaheim, CA",       1_485_000, +3.7),
    ("Honolulu, HI",      1_183_000, +3.0),
    ("San Diego, CA",     1_075_000, +4.9),
    ("Salinas, CA",         982_600, +0.4),
    ("Oxnard, CA",          961_800, +0.4),
    ("San Luis Obispo, CA", 954_400, +2.8),
    ("Bridgeport, CT",      885_100, +4.7),
    ("Los Angeles, CA",     879_900,  0.0),
]
# the two metros Fremont buyers actually cross-shop
HILITE = {"San Jose, CA", "San Francisco, CA"}

ORANGE    = "#f4a06a"   # muted
ORANGE_DK = "#ea580c"   # Real Estate brand orange
INK       = "#12263f"
MUTED     = "#6b7280"
GROUND    = "#fdf6e8"   # warm cream (house style)
GRID      = "#e7ddc9"
UP        = "#16a34a"
DOWN      = "#dc2626"
FLAT      = "#8a8172"


def money(v):
    """$2.05M / $983K, with no stray math-mode dollar signs.

    Rounds half UP explicitly. Python's default half-to-even renders San Diego's
    $1,075,000 as $1.07M, which is the exact rounding slip in the supplied
    graphic; NAR's figure belongs at $1.08M.
    """
    if v >= 1_000_000:
        m = Decimal(v) / Decimal(1_000_000)
        return f"${m.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}M"
    k = Decimal(v) / Decimal(1000)
    return f"${k.quantize(Decimal('1'), rounding=ROUND_HALF_UP)}K"


labels = [d[0] for d in DATA]
vals = [d[1] for d in DATA]
pcts = [d[2] for d in DATA]
y = list(range(len(DATA)))

fig, ax = plt.subplots(figsize=(12, 7.6))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

colors = [ORANGE_DK if lb in HILITE else ORANGE for lb in labels]
ax.barh(y, vals, height=0.62, color=colors, zorder=3, edgecolor=GROUND,
        linewidth=1.3)

span = max(vals)
for yi, (v, p, lb) in enumerate(zip(vals, pcts, labels)):
    bold = "bold" if lb in HILITE else "normal"
    # price sits just inside the bar end
    ax.text(v - span * 0.012, yi, money(v), fontsize=13.5, fontweight="bold",
            color="#ffffff" if lb in HILITE else INK, ha="right", va="center",
            zorder=5)
    # year-over-year change rides outside the bar
    if p > 0:
        mark, pcol = "▲", UP
    elif p < 0:
        mark, pcol = "▼", DOWN
    else:
        mark, pcol = "–", FLAT
    ax.text(v + span * 0.018, yi, f"{mark} {abs(p):.1f}%", fontsize=12,
            fontweight=bold, color=pcol, ha="left", va="center", zorder=5)

ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=13, color=INK)
for tick, lb in zip(ax.get_yticklabels(), labels):
    if lb in HILITE:
        tick.set_fontweight("bold")
ax.invert_yaxis()
ax.set_xlim(0, span * 1.20)
ax.set_xticks([])
ax.grid(axis="x", color=GRID, linewidth=1.0, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "bottom"):
    ax.spines[sp].set_visible(False)
ax.spines["left"].set_color("#d9cdb4")
ax.spines["left"].set_linewidth(1.2)

ax.set_title("America's 10 Priciest Metros", fontsize=24, fontweight="bold",
             color=INK, loc="left", pad=34)
ax.text(0.0, 1.052, "Median existing single-family home price, Q2 2026",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="left")
ax.text(1.0, 1.052, "8 OF THE TOP 10 ARE IN CALIFORNIA",
        transform=ax.transAxes, fontsize=14, fontweight="bold",
        color=ORANGE_DK, ha="right")

fig.text(0.012, 0.014,
         "Percentages are year over year  |  Source: National Association of "
         "REALTORS, Q2 2026",
         fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.163, right=0.985, top=0.845, bottom=0.065)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)

ca = sum(1 for lb in labels if lb.endswith(", CA"))
print("wrote", OUT, f"| {len(DATA)} metros | {ca} in California "
      f"| top {money(vals[0])} {pcts[0]:+.1f}% "
      f"| only decliner: {[l for l,p in zip(labels,pcts) if p<0]}")
