#!/usr/bin/env python3
"""
make-homeequity-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "Homeowner Equity Holds Near Record
Highs" graphic Harv supplied for the 07/29/26 daily email. OUR OWN branded
chart, not the source image: warm cream ground, a Real-Estate-orange line with a
soft fill, the 2008 crash trough flagged for context, and the current share
called out in a rounded pill.

Story tie-in (Market Briefs, 07/29/26): Americans are sitting on a record pile of
home equity, a combined $17.9 trillion of home value, but most cannot afford to
cash it out because selling means giving up an ultra-low mortgage rate. Equity as
a share of total U.S. real estate value is back near its all-time high, which is
exactly the lock-in story, so it lands in the Real Estate section.

Data: homeowner equity as a share of total U.S. real estate value, annual
1976 through 2026 Q1, transcribed faithfully from the source graphic Harv
provided (Realtor.com, Federal Reserve).

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "homeequity-072926.png"

# (year, homeowner equity as % of total U.S. real estate value)
DATA = [
    (1976, 67.5), (1977, 68.0), (1978, 68.5), (1979, 68.7), (1980, 68.6),
    (1981, 68.8), (1982, 69.6), (1983, 70.2), (1984, 70.5), (1985, 70.3),
    (1986, 70.2), (1987, 70.1), (1988, 70.0), (1989, 69.8), (1990, 69.2),
    (1991, 68.4), (1992, 67.4), (1993, 66.4), (1994, 65.4), (1995, 64.4),
    (1996, 63.5), (1997, 62.6), (1998, 61.7), (1999, 61.0), (2000, 60.4),
    (2001, 60.1), (2002, 60.5), (2003, 61.8), (2004, 63.2), (2005, 63.6),
    (2006, 63.0), (2007, 61.9), (2008, 55.0), (2009, 47.2), (2010, 46.6),
    (2011, 46.2), (2012, 49.5), (2013, 54.5), (2014, 57.8), (2015, 60.0),
    (2016, 62.0), (2017, 63.4), (2018, 63.9), (2019, 64.4), (2020, 66.2),
    (2021, 69.4), (2022, 71.8), (2023, 70.9), (2024, 71.0), (2025, 71.2),
    (2026, 71.6),
]

END = DATA[-1][1]
ORANGE   = "#ea580c"   # Real Estate section orange
ORANGE_D = "#c2410c"
INK      = "#12263f"
MUTED    = "#6b7280"
GROUND   = "#fdf6e8"   # warm cream (house style)
GRID     = "#e7ddc9"

years = [r[0] for r in DATA]
vals  = [r[1] for r in DATA]

fig, ax = plt.subplots(figsize=(12, 6.4))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.plot(years, vals, color=ORANGE, linewidth=2.9, zorder=4,
        solid_capstyle="round")
ax.fill_between(years, vals, 42, color=ORANGE, alpha=0.12, zorder=2)

# crash trough callout
tro_i = vals.index(min(vals))
ax.plot([years[tro_i]], [vals[tro_i]], "o", color=ORANGE_D, markersize=7,
        zorder=5)
ax.annotate(f"{years[tro_i]} low  {vals[tro_i]}%",
            xy=(years[tro_i], vals[tro_i]),
            xytext=(years[tro_i] - 1.5, vals[tro_i] - 3.4),
            fontsize=11.5, fontweight="bold", color=ORANGE_D, ha="center",
            zorder=6)

# current value pill
ax.plot([years[-1]], [END], "o", color=ORANGE_D, markersize=8, zorder=6)
ax.annotate(f"{END}%", xy=(years[-1], END), xytext=(years[-1] + 1.6, END + 1.6),
            fontsize=15.5, fontweight="bold", color="white", va="center",
            zorder=7,
            bbox=dict(boxstyle="round,pad=0.42", facecolor=ORANGE_D,
                      edgecolor="none"))

ax.set_xlim(1976, 2032)
ax.set_ylim(42, 77)
ax.set_yticks([45, 50, 55, 60, 65, 70, 75])
ax.set_yticklabels(["45%", "50%", "55%", "60%", "65%", "70%", "75%"],
                   fontsize=12, color=MUTED)
ax.set_xticks([1976, 1980, 1990, 2000, 2010, 2020, 2026])
ax.set_xticklabels(["1976", "1980", "1990", "2000", "2010", "2020", "2026"],
                   fontsize=12.5, fontweight="bold", color=MUTED)
ax.grid(axis="y", color=GRID, linewidth=1.1, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("Homeowner Equity Holds Near Record Highs", fontsize=25,
             fontweight="bold", color=INK, loc="left", pad=30)
ax.text(0.0, 1.045,
        "Homeowner equity as a share of total U.S. real estate value",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="left")

fig.text(0.012, 0.014, "Source: Realtor.com, Federal Reserve. 2026 Q1.",
         fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.062, right=0.985, top=0.82, bottom=0.085)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, f"| {len(DATA)} years | now {END}% | trough "
      f"{min(vals)}% in {years[tro_i]}")
