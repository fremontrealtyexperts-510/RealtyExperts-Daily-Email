#!/usr/bin/env python3
"""
make-gdp-quarterly-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "Quarterly change in gross domestic
product" graphic Harv supplied for the 07/31/26 daily email. OUR OWN branded
chart, not the source image: warm Meridian cream ground in place of the dark
source, gold bars for growth, coral for contractions, and the newly released
quarter highlighted with its value in a pill.

Sibling of make-gdp-chart.py, which is the SHORT six-quarter version built for
the 06/26/26 run. This one carries the full five-year run (20 quarters).

Story tie-in (Market Briefs, 07/31/26, "Growth Stalls, Inflation Sticks"): BEA's
advance estimate put Q2 2026 growth at 1.5%, down from 2.1% in Q1, while
inflation ran at 3.7%. Slower growth plus sticky inflation is the hard
combination, and it lands in the Economy section.

DATA NOTE (important): the values below are BEA's CURRENT vintage, pulled
2026-07-31 from ALFRED (`alfredgraph.csv?id=A191RL1Q225SBEA`, vintage column
`_20260731`), which includes the July 30 advance estimate for Q2 2026. The
source graphic Harv supplied ran 0.2 to 0.7 points LOW on every one of its 20
quarters, the signature of a pre-revision vintage, so this was rebuilt on the
current series rather than transcribed. Its last bar read 1.3 where BEA now
publishes 1.5. Cross-checked against make-gdp-chart.py (06/26 run), whose six
quarters match this series exactly.

(FRED's own fredgraph.csv endpoint returned 502s and timeouts all morning on
2026-07-31; alfredgraph.csv on alfred.stlouisfed.org served the same series
fine. Worth remembering as the fallback.)

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "gdp-quarterly-073126.png"

# BEA real GDP, percent change from preceding quarter, seasonally adjusted
# annual rate. 2021 Q3 through 2026 Q2 (current vintage, 2026-07-31).
QUARTERS = [
    ("2021", "Q3", 3.3), ("2021", "Q4", 7.0),
    ("2022", "Q1", -1.0), ("2022", "Q2", 0.6), ("2022", "Q3", 2.9), ("2022", "Q4", 2.8),
    ("2023", "Q1", 2.9), ("2023", "Q2", 2.5), ("2023", "Q3", 4.7), ("2023", "Q4", 3.4),
    ("2024", "Q1", 0.8), ("2024", "Q2", 3.6), ("2024", "Q3", 3.3), ("2024", "Q4", 1.9),
    ("2025", "Q1", -0.6), ("2025", "Q2", 3.8), ("2025", "Q3", 4.4), ("2025", "Q4", 0.5),
    ("2026", "Q1", 2.1), ("2026", "Q2", 1.5),
]
VALS = [v for _, _, v in QUARTERS]
CUR_I = len(VALS) - 1          # 2026 Q2, the newly released quarter
PREV = VALS[CUR_I - 1]         # 2026 Q1, for the deceleration callout

GOLD     = "#D9B65A"   # growth quarters
GOLD_CUR = "#B08C1E"   # the quarter just released (Meridian gold)
CORAL    = "#E8654F"   # contractions
GROUND   = "#FAF7F0"   # Meridian paper
INK      = "#2e2e2e"
MUTED    = "#8a8172"
GRID     = "#e7ddc9"

x = list(range(len(VALS)))

fig, ax = plt.subplots(figsize=(12.6, 6.6))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

colors = [CORAL if v < 0 else GOLD for v in VALS]
colors[CUR_I] = GOLD_CUR
ax.bar(x, VALS, width=0.68, color=colors, zorder=3)

# value label on every bar: above the positives, below the negatives.
# The highlighted quarter is skipped, since its pill already carries the value
# and the leader line would run straight through a second label.
for xi, v in zip(x, VALS):
    if xi == CUR_I:
        continue
    above = v >= 0
    ax.text(xi, v + (0.18 if above else -0.18), f"{v:+.1f}",
            ha="center", va="bottom" if above else "top",
            fontsize=11.5, fontweight="bold",
            color=(GOLD_CUR if xi == CUR_I else (CORAL if v < 0 else INK)),
            zorder=5)

# zero baseline
ax.axhline(0, color="#6b6155", linewidth=1.6, zorder=4)

# callout on the newly released quarter
ax.annotate(f"Q2 2026\n{VALS[CUR_I]:+.1f}%",
            xy=(CUR_I, VALS[CUR_I]), xytext=(CUR_I - 0.15, 6.0),
            fontsize=12.5, fontweight="bold", color="white", ha="center",
            va="center", zorder=7,
            bbox=dict(boxstyle="round,pad=0.45", facecolor=GOLD_CUR, edgecolor="none"),
            arrowprops=dict(arrowstyle="-", color=GOLD_CUR, linewidth=1.6,
                            shrinkA=6, shrinkB=4))

# year group labels under the axis
year_pos = {}
for i, (y, _, _) in enumerate(QUARTERS):
    year_pos.setdefault(y, []).append(i)
ax.set_xticks([sum(v) / len(v) for v in year_pos.values()])
ax.set_xticklabels(list(year_pos.keys()), fontsize=13.5,
                   fontweight="bold", color=MUTED)

ax.set_ylim(-2.2, 8.3)
ax.set_yticks([-2, 0, 2, 4, 6, 8])
ax.set_yticklabels(["−2%", "0", "+2", "+4", "+6", "+8"],
                   fontsize=12, color=MUTED)
ax.grid(axis="y", color=GRID, linewidth=1.1, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)
ax.set_xlim(-0.75, len(VALS) - 0.25)
ax.set_axisbelow(True)

ax.set_title("Growth Stalls To 1.5%", fontsize=25, fontweight="bold",
             color=INK, loc="left", pad=30)
ax.text(0.0, 1.045, "Quarterly change in real gross domestic product",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="left")
ax.text(1.0, 1.045, f"DOWN FROM {PREV:+.1f}% IN Q1",
        transform=ax.transAxes, fontsize=14.5, fontweight="bold",
        color=GOLD_CUR, ha="right")

fig.text(0.012, 0.014,
         "Source: Bureau of Economic Analysis. Seasonally adjusted annual rate. "
         "Q2 2026 advance estimate, released July 30, 2026.",
         fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.055, right=0.985, top=0.82, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT,
      f"| quarters: {len(VALS)} | latest {QUARTERS[CUR_I][0]} {QUARTERS[CUR_I][1]} = {VALS[CUR_I]:+.1f}%"
      f" | prior {PREV:+.1f}%")
