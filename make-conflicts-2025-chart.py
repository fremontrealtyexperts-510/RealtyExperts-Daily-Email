#!/usr/bin/env python3
"""
make-conflicts-2025-chart.py  [outdir]

Recreation of the NPR "Last year, the world saw the highest number of conflicts
since WWII" graphic Harv supplied for the 09/19/26 edition. Emits BOTH variants:

  conflicts-2025-091926.png      plain monogram  -> RE email + Agent Hub
  conflicts-2025-091926-hb.png   + wordmark      -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/19/26
=============================================================================

Series re-pulled, not traced off the graphic. Source is the UCDP/PRIO Armed
Conflict Dataset (state-based conflicts, 25+ battle deaths in the calendar
year), taken as the World totals from Our World in Data's machine readable
copy, 1946 to 2025:
  https://ourworldindata.org/grapher/number-of-state-based-conflicts.csv
A year's total is the sum of its four types: internationalized intrastate,
non-internationalized intrastate, extrasystemic (colonial, ends 1975) and
interstate.

RECONCILES EXACTLY with UCDP's own release (Uppsala University, June 9, 2026,
"UCDP: record number of conflicts between states"), which states verbatim:
  "In all, UCDP registered 65 conflicts in which states were involved on one or
   both sides during 2025, which is also the highest number since statistics
   began to be recorded in 1946."
  "In 2025, the number of interstate conflicts doubled for the second year in a
   row, from two in 2023 to eight in 2025."
Our sum for 2025 is 22 + 35 + 0 + 8 = 65, and the interstate column reads
2 (2023), 4 (2024), 8 (2025). Both match. Wars that year: 13, the most since
1992. Deaths in organized violence: about 244,600.

★ WHY THE SECOND LINE. The supplied graphic plots the 65 total only. The number
that actually reaches a Bay Area reader is the interstate subset: state against
state is the kind of conflict that moves oil, shipping lanes and insurance, and
8 in 2025 is itself the highest since 1946. It is the same dataset and the same
column, so nothing here is a new claim.

★ EARLY YEARS DIFFER FROM THE SUPPLIED GRAPHIC. Ours starts at 11 for 1946
where the NPR version reads nearer 17. UCDP revises its history with each
release, and the supplied graphic cites the 2025 article (data through 2024)
while plotting a 2025 point, so it is mixing vintages. This chart uses one
vintage throughout, the current one that produced the 65.

NOT DRAWN: an oil panel. Brent annual averages were considered and dropped.
FRED's DCOILBRENTEU spot series printed $120 to $130 in mid September against a
$104 futures settlement, and Yahoo's BZ=F monthly bars are missing five months
since 2024, so neither could carry an honest average. Friday's verified Brent
settlement is quoted in the copy instead.

matplotlib only; build with python3.13 on Mac.
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "091926"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
NAVY = "#3d5a80"
GRID = "#d8cdb8"
MUTED = "#8a8172"

# World totals, UCDP/PRIO via Our World in Data, pulled 09/19/26.
TOTAL = {
    1946: 11, 1947: 11, 1948: 17, 1949: 19, 1950: 17, 1951: 14, 1952: 14,
    1953: 16, 1954: 15, 1955: 13, 1956: 17, 1957: 17, 1958: 18, 1959: 16,
    1960: 15, 1961: 20, 1962: 19, 1963: 19, 1964: 24, 1965: 26, 1966: 27,
    1967: 32, 1968: 25, 1969: 28, 1970: 25, 1971: 29, 1972: 26, 1973: 25,
    1974: 27, 1975: 29, 1976: 31, 1977: 35, 1978: 37, 1979: 40, 1980: 40,
    1981: 41, 1982: 43, 1983: 42, 1984: 41, 1985: 37, 1986: 43, 1987: 46,
    1988: 38, 1989: 41, 1990: 49, 1991: 53, 1992: 51, 1993: 44, 1994: 50,
    1995: 41, 1996: 41, 1997: 39, 1998: 40, 1999: 40, 2000: 40, 2001: 38,
    2002: 33, 2003: 33, 2004: 33, 2005: 33, 2006: 33, 2007: 35, 2008: 39,
    2009: 37, 2010: 31, 2011: 37, 2012: 33, 2013: 39, 2014: 46, 2015: 54,
    2016: 54, 2017: 54, 2018: 52, 2019: 57, 2020: 57, 2021: 54, 2022: 56,
    2023: 59, 2024: 59, 2025: 65
}
INTERSTATE = {
    1946: 2, 1947: 0, 1948: 3, 1949: 3, 1950: 2, 1951: 2, 1952: 2, 1953: 1,
    1954: 1, 1955: 0, 1956: 2, 1957: 1, 1958: 1, 1959: 0, 1960: 0, 1961: 1,
    1962: 2, 1963: 2, 1964: 3, 1965: 3, 1966: 2, 1967: 5, 1968: 1, 1969: 5,
    1970: 2, 1971: 2, 1972: 2, 1973: 3, 1974: 4, 1975: 2, 1976: 1, 1977: 3,
    1978: 4, 1979: 3, 1980: 3, 1981: 2, 1982: 2, 1983: 4, 1984: 3, 1985: 2,
    1986: 3, 1987: 5, 1988: 3, 1989: 2, 1990: 2, 1991: 2, 1992: 1, 1993: 0,
    1994: 1, 1995: 1, 1996: 2, 1997: 1, 1998: 2, 1999: 2, 2000: 2, 2001: 2,
    2002: 1, 2003: 2, 2004: 0, 2005: 0, 2006: 0, 2007: 0, 2008: 1, 2009: 0,
    2010: 0, 2011: 1, 2012: 1, 2013: 1, 2014: 1, 2015: 1, 2016: 2, 2017: 1,
    2018: 2, 2019: 2, 2020: 3, 2021: 2, 2022: 3, 2023: 2, 2024: 4, 2025: 8
}

_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conflicts-source.json")
if os.path.exists(_src):  # optional re-check against the pull, if kept alongside
    _d = json.load(open(_src))
    assert {int(k): v for k, v in _d["total"].items()} == TOTAL, "total series drift"
    assert {int(k): v for k, v in _d["interstate"].items()} == INTERSTATE, "interstate drift"

years = sorted(TOTAL)
tot = [TOTAL[y] for y in years]
inter = [INTERSTATE[y] for y in years]
assert TOTAL[2025] == 65 and INTERSTATE[2025] == 8, "2025 must match the UCDP release"

fig, ax = plt.subplots(figsize=(11.2, 6.3), dpi=115)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

ax.fill_between(years, tot, 0, color=CORAL, alpha=0.13, zorder=2)
ax.plot(years, tot, color=CORAL, linewidth=2.6, zorder=4, label="All conflicts involving a state")
ax.plot(years, inter, color=NAVY, linewidth=2.2, zorder=5, label="State against state only")

ax.scatter([2025], [65], s=80, facecolor=CREAM, edgecolor=DEEP, linewidth=2.6, zorder=6)
ax.scatter([2025], [8], s=70, facecolor=CREAM, edgecolor=NAVY, linewidth=2.4, zorder=6)

ax.annotate("65 in 2025,\nthe most since 1946", xy=(2025, 65), xytext=(2007.5, 68.5),
            fontsize=12.5, fontweight="bold", color=DEEP, ha="left",
            arrowprops=dict(arrowstyle="-", color=DEEP, linewidth=1.3))
ax.annotate("8 state against state,\nalso the most since 1946", xy=(2025, 8),
            xytext=(2002.5, 15.5), fontsize=11.5, fontweight="bold", color=NAVY,
            ha="left", arrowprops=dict(arrowstyle="-", color=NAVY, linewidth=1.2))

ax.set_xlim(1944, 2032)
ax.set_ylim(0, 79)
ax.set_xticks([1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020, 2025])
ax.set_xticklabels(["1950", "1960", "1970", "1980", "1990", "2000", "2010", "2020", "2025"],
                   fontsize=11.5, color=INK)
ax.set_yticks([0, 20, 40, 60])
ax.set_yticklabels(["0", "20", "40", "60"], fontsize=11, color=MUTED)
ax.tick_params(axis="x", length=0, pad=7, colors=INK)
ax.tick_params(axis="y", length=0, colors=MUTED)
ax.grid(axis="y", color=GRID, linewidth=0.9, alpha=0.7, zorder=0)
ax.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(GRID)

ax.set_title("A Record Number of Armed Conflicts", fontsize=25, fontweight="bold",
             color=INK, pad=32, loc="left", x=0)
ax.text(0, 1.045,
        "Active conflicts with a government on at least one side and 25 or more battle deaths in the year",
        transform=ax.transAxes, fontsize=12.5, color=MUTED)

ax.legend(loc="upper left", frameon=False, fontsize=11.5,
          bbox_to_anchor=(0.005, 0.80))

fig.text(0.008, 0.028,
         "Source: UCDP/PRIO Armed Conflict Dataset, world totals 1946 to 2025, via Our World in Data. The 2025 figures match Uppsala\n"
         "University's release of June 9, 2026, which also counted 13 wars, the most since 1992.",
         fontsize=9.2, color=MUTED, ha="left", va="bottom", linespacing=1.5)

fig.subplots_adjust(left=0.062, right=0.985, top=0.845, bottom=0.165)

out = os.path.join(OUTDIR, f"conflicts-2025-{STAMP}.png")
plain, branded = save_pair(fig, out, facecolor=CREAM)
print("wrote", plain)
print("wrote", branded)
