#!/usr/bin/env python3
"""
make-foreclosure-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "First-Half U.S. Foreclosure Activity"
graphic Harv supplied for the 08/03/26 daily email. OUR OWN branded chart, not the
source image: warm cream ground, Real-Estate-orange bars by year, the 2026 bar
highlighted as the current reading, and the 2010 crisis peak flagged so the scale
of today's number reads honestly.

Story tie-in (Market Briefs "Foreclosure Filings Flip", 08/03/26): foreclosure
filings rose 21% in the first half of the year and economists point to household
financial stress, but the level is still nowhere near the housing collapse. That
context is the whole point of the chart, so it lands in the Real Estate section.

Data: ATTOM (RealtyTrac for the pre-2016 years) mid-year U.S. Foreclosure Market
Reports, properties with foreclosure filings in the first six months of each year.
Pulled from the primary ATTOM/RealtyTrac releases, NOT transcribed from the source
graphic. Two points in the source graphic were about 1% high: it showed 536K for
2016 (ATTOM published 533,813) and 428K for 2017 (ATTOM published 424,800). The
published figures are used here.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "foreclosure-080326.png"

# (year, U.S. properties with foreclosure filings, first six months)
DATA = [
    (2008, 1343331), (2009, 1528364), (2010, 1654634), (2011, 1170402),
    (2012, 1045801), (2013,  801359), (2014,  613874), (2015,  597589),
    (2016,  533813), (2017,  424800), (2018,  362275), (2019,  296458),
    (2020,  165530), (2021,   65082), (2022,  164581), (2023,  185580),
    (2024,  177431), (2025,  187659), (2026,  227548),
]
years = [y for y, _ in DATA]
vals = [v for _, v in DATA]

PEAK_I = vals.index(max(vals))      # 2010, the crisis peak
LOW_I = vals.index(min(vals))       # 2021, the all-time low
CUR_I = len(DATA) - 1               # 2026, the current reading

ORANGE    = "#f4a06a"   # muted history bars
ORANGE_DK = "#ea580c"   # Real Estate brand orange, for the bars that carry story
INK       = "#12263f"
MUTED     = "#6b7280"
GROUND    = "#fdf6e8"   # warm cream (house style)
GRID      = "#e7ddc9"


def fmt(v):
    """Match the newsletter's own shorthand: 1.7M / 801K."""
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    return f"{round(v/1000):,.0f}K"


x = list(range(len(DATA)))

fig, ax = plt.subplots(figsize=(12.6, 6.4))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

colors = [ORANGE_DK if i in (PEAK_I, CUR_I) else ORANGE for i in x]
ax.bar(x, vals, width=0.68, color=colors, zorder=3, edgecolor=GROUND,
       linewidth=1.2)

# value label above each bar
for xi, v in zip(x, vals):
    weight = "bold" if xi in (PEAK_I, CUR_I) else "normal"
    color = INK if xi in (PEAK_I, CUR_I) else "#8a8172"
    ax.text(xi, v + 34000, fmt(v), fontsize=11.5, fontweight=weight,
            color=color, ha="center", va="bottom", zorder=4)

# crisis peak callout
ax.annotate("2010 crisis peak",
            xy=(PEAK_I, vals[PEAK_I]), xytext=(PEAK_I + 0.9, vals[PEAK_I] + 155000),
            fontsize=12, fontweight="bold", color=ORANGE_DK, zorder=5)

# all-time low callout, stacked straight above the 2021 bar so it cannot
# collide with the 2020 value label sitting to its left
ax.annotate("2021 all-time low",
            xy=(LOW_I, vals[LOW_I]), xytext=(LOW_I, vals[LOW_I] + 330000),
            fontsize=11, color="#8a8172", ha="center", va="bottom", zorder=5,
            arrowprops=dict(arrowstyle="-", color="#c9bda4", linewidth=1.1,
                            shrinkA=6, shrinkB=42))

# current reading callout
ax.annotate("2026: up 21%\nyear over year",
            xy=(CUR_I, vals[CUR_I]),
            xytext=(CUR_I - 0.35, vals[CUR_I] + 205000),
            fontsize=11.5, fontweight="bold", color=ORANGE_DK, ha="center",
            zorder=5,
            arrowprops=dict(arrowstyle="-", color=ORANGE_DK, linewidth=1.2,
                            shrinkA=0, shrinkB=22))

ax.set_xlim(-0.85, len(DATA) - 0.15)
ax.set_ylim(0, 1_980_000)
ax.set_xticks(x)
ax.set_xticklabels([str(y) for y in years], fontsize=10.5, fontweight="bold",
                   color=MUTED)
ax.set_yticks([])
ax.grid(axis="y", color=GRID, linewidth=1.0, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
ax.spines["bottom"].set_color("#d9cdb4")
ax.spines["bottom"].set_linewidth(1.2)

ax.set_title("Foreclosures Are Rising, And Still Far From A Crisis",
             fontsize=25, fontweight="bold", color=INK, loc="left", pad=30)
ax.text(0.0, 1.045,
        "U.S. properties with foreclosure filings, January to June",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="left")
ax.text(1.0, 1.045, "227,548  IN THE FIRST HALF OF 2026",
        transform=ax.transAxes, fontsize=14.5, fontweight="bold",
        color=ORANGE_DK, ha="right")

fig.text(0.012, 0.014,
         "Source: ATTOM mid-year U.S. Foreclosure Market Reports "
         "(RealtyTrac for years before 2016).",
         fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.022, right=0.988, top=0.82, bottom=0.085)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, f"| bars: {len(DATA)} | 2026 {vals[-1]:,} "
      f"| vs 2025 {vals[-2]:,} = {(vals[-1]/vals[-2]-1)*100:.1f}% "
      f"| vs 2010 peak {vals[PEAK_I]:,} = {vals[-1]/vals[PEAK_I]*100:.1f}% of peak")
