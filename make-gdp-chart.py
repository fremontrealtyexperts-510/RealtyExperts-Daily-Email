#!/usr/bin/env python3
"""
make-gdp-chart.py  [out.png]

REALTY EXPERTS recreation of the "World's 5 Biggest Economies" graphic Harv
supplied for the 08/18/26 daily email. OUR OWN branded chart: warm cream ground,
ranked horizontal bars with each economy's GDP printed at the end of its bar,
matching the ranked-bar language already used on the daily inventory charts.

Data: VERIFIED against the IMF World Economic Outlook (April 2026) nominal GDP
projections, NOT taken from the supplied graphic, whose source line credited
"Market Briefs". Worth recording: today's Market Briefs email contains no GDP
story at all (grep for GDP, trillion, Germany and India all return nothing), so
the graphic could not be checked against the newsletter it cited and had to be
verified upstream at the IMF instead. All five values matched exactly.

⚠️ ONE THING THAT LOOKED WRONG AND WAS NOT: India is absent from the top five.
That is correct for the April 2026 WEO, where India sits SIXTH at $4.15T, just
behind the UK at $4.26T. A February 2026 data revision plus a weaker rupee
pushed India's crossover past Japan out to late 2026 or early 2027. India is
drawn here as a greyed sixth bar precisely so the omission reads as deliberate
rather than as an error.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "gdp-081826.png"

# (rank, country, nominal GDP in $T, in_top_five) -- IMF WEO April 2026
DATA = [
    (1, "United States",  32.38, True),
    (2, "China",          20.85, True),
    (3, "Germany",         5.45, True),
    (4, "Japan",           4.38, True),
    (5, "United Kingdom",  4.26, True),
    (6, "India",           4.15, False),
]

INK    = "#12263f"
CORAL  = "#e2574c"
SLATE  = "#4a6b8a"
GREY   = "#b9b0a0"
MUTED  = "#6b7280"
GROUND = "#fdf6e8"   # warm cream (house style)
GRID   = "#e7ddc9"

fig, ax = plt.subplots(figsize=(12.6, 6.8))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ys = list(range(len(DATA)))[::-1]   # rank 1 on top

for y, (rank, name, val, top5) in zip(ys, DATA):
    color = CORAL if rank == 1 else (SLATE if top5 else GREY)
    ax.barh(y, val, height=0.62, color=color, zorder=3)
    ax.text(val + 0.42, y, f"${val:,.2f}T", va="center", ha="left",
            fontsize=15, fontweight="bold", color=color, zorder=4)
    label = f"{rank}.  {name}"
    ax.text(-0.45, y, label, va="center", ha="right", fontsize=14,
            fontweight="bold", color=INK if top5 else MUTED, zorder=4)

# make the sixth bar's status explicit
ax.text(DATA[-1][2] + 6.2, ys[-1], "6th, just outside the top five",
        va="center", ha="left", fontsize=11.5, fontstyle="italic",
        color=MUTED, zorder=4)

ax.set_xlim(0, 39)
ax.set_ylim(-0.75, len(DATA) - 0.25)
ax.set_yticks([])
ax.set_xticks([0, 10, 20, 30])
ax.set_xticklabels(["$0", "$10T", "$20T", "$30T"], fontsize=12, color=MUTED)
ax.grid(axis="x", color=GRID, linewidth=1.1, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("The World's 5 Biggest Economies", fontsize=25, fontweight="bold",
             color=INK, loc="left", pad=46)
ax.text(0.0, 1.045, "Nominal GDP in US dollars, 2026 projection",
        transform=ax.transAxes, fontsize=12.5, fontweight="bold", color=MUTED,
        ha="left")

fig.text(0.012, 0.014, "Source: International Monetary Fund, World Economic "
         "Outlook (April 2026), nominal GDP", fontsize=9.5, color="#a99f88",
         ha="left")

fig.subplots_adjust(left=0.185, right=0.985, top=0.80, bottom=0.115)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, "| economies:", len(DATA),
      "| top5 sum $%.2fT" % sum(d[2] for d in DATA if d[3]),
      "| US/China ratio %.2fx" % (DATA[0][2] / DATA[1][2]))
