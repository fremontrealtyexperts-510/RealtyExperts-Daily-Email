#!/usr/bin/env python3
"""
make-propertytax-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "Top 5 States With The Highest Property
Taxes" graphic (Rocket Mortgage) Harv supplied for the 07/22/26 daily email. OUR
OWN branded chart, not the source image: warm cream ground, Real-Estate-orange
horizontal bars ranked by the average annual bill, New Jersey highlighted as the
national leader, and a light U.S.-average reference line for context.

Story tie-in (Market Briefs "Ballot Battle", 07/22/26): voters in 13 states will
decide this November whether to cut property taxes, because housing costs eat the
largest share of most household budgets. These five states carry the heaviest
property-tax loads in the country, so it lands in the Real Estate section.

Data: Rocket Mortgage average annual property tax bill by state, transcribed
faithfully from the source graphic Harv provided. These five states rank among
the nation's highest by effective property-tax rate; the bars show the dollar
bill. The ~$2,500 U.S.-average reference is the national average annual property
tax bill (Census / ATTOM order of magnitude) shown only for scale.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "propertytax-072226.png"

# (state, average annual property tax bill $) - faithful to the Rocket Mortgage
# source graphic. Sorted descending by bill for clean ranked bars.
DATA = [
    ("New Jersey",    9590),
    ("New Hampshire", 6667),
    ("Connecticut",   6643),
    ("Illinois",      5298),
    ("Vermont",       5039),
]
DATA = sorted(DATA, key=lambda r: r[1], reverse=True)
US_AVG = 2500  # national average annual property tax bill, for scale only

ORANGE    = "#ea580c"   # Real Estate section orange
ORANGE_DK = "#c2410c"   # New Jersey highlight (national leader)
ORANGE_LT = "#fb923c"
INK       = "#12263f"
MUTED     = "#6b7280"
GROUND    = "#fdf6e8"   # warm cream (house style)
GRID      = "#e7ddc9"

labels = [s for s, _ in DATA]
vals   = [v for _, v in DATA]
# barh draws bottom-up, so reverse to put the biggest bar on top
y = list(range(len(DATA)))[::-1]

fig, ax = plt.subplots(figsize=(12, 6.2))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

colors = [ORANGE_DK if s == "New Jersey" else ORANGE for s in labels]
bars = ax.barh(y, vals, height=0.62, color=colors, zorder=3,
               edgecolor=GROUND, linewidth=1.5)

# U.S. average reference line for scale
ax.axvline(US_AVG, color="#9ca3af", linewidth=1.3, linestyle=(0, (5, 4)),
           alpha=0.9, zorder=2)
ax.text(US_AVG + 90, y[-1] - 0.62, f"U.S. average\n~${US_AVG:,}", fontsize=10.5,
        fontweight="bold", color="#6b7280", ha="left", va="center")

# value labels at the end of each bar
for yi, v, s in zip(y, vals, labels):
    ax.text(v - 160, yi, f"${v:,}", fontsize=16, fontweight="bold",
            color=GROUND, ha="right", va="center", zorder=4)
    tag = "  (highest in the U.S.)" if s == "New Jersey" else ""
    ax.text(180, yi, s + tag, fontsize=14.5, fontweight="bold", color=GROUND,
            ha="left", va="center", zorder=4)

ax.set_xlim(0, 10600)
ax.set_ylim(-0.7, len(DATA) - 0.3)
ax.set_yticks([])
ax.set_xticks([])
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("Top 5 States With The Highest Property Taxes", fontsize=25,
             fontweight="bold", color=INK, loc="left", pad=26)
ax.text(0.0, 1.03,
        "Average annual property tax bill, ranked",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="left")

fig.text(0.012, 0.014, "Source: Rocket Mortgage", fontsize=9.5,
         color="#a99f88", ha="left")

fig.subplots_adjust(left=0.02, right=0.985, top=0.83, bottom=0.075)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, "| bars:", len(DATA), "| top", labels[0], f"${vals[0]:,}")
