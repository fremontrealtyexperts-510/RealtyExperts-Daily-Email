#!/usr/bin/env python3
"""
make-portla-chart.py  [out.png]

REALTY EXPERTS recreation of the "Second-Busiest July Ever at the Port of L.A."
graphic Harv supplied for the 08/19/26 daily email. OUR OWN branded chart: warm
cream ground, monthly columns with each month's volume printed above its bar,
July highlighted in coral.

Data: VERIFIED point by point against the PRIMARY source, the Port of Los
Angeles' own "Historical TEU Statistics 2026" table, NOT taken from the supplied
graphic. All seven 2026 months matched the port's published Total TEUs exactly:

    Jan   812,000.25   ->  812K      May   840,164.50   ->  840K
    Feb   824,323.25   ->  824K      Jun 1,002,734.00   -> 1.00M
    Mar   752,519.50   ->  753K      Jul   960,464.25   ->  960K
    Apr   890,861.00   ->  891K

Today's Market Briefs told the same story and its headline count (960,464) also
matched the port's July figure, which is a better showing than usual for MB.

THE HEADLINE CLAIM WAS CHECKED, NOT ASSUMED. "Second-busiest July ever" holds:
pulling the port's July row for prior years gives July 2025 at 1,019,837 (the
record), then this July at 960,464, then July 2024 at 939,600, July 2022 at
935,424 and July 2021 at 890,800. So July 2026 is genuinely second. The supplied
graphic asserted that ranking but gave the reader nothing to check it against, so
this version draws the July 2025 record as a labeled dashed line. That single
addition is what turns the headline from a claim into something visible.

Worth carrying into the copy: July was the second-busiest July on record and was
still DOWN 5.82% from July 2025, per the port's own prior-year column. Both are
true, and the graphic showed only the flattering half.

UNIT: the port publishes TEUs (twenty-foot equivalent units), not container
counts. MB wrote "960,464 containers"; a TEU is a volume measure, so this chart
and the report copy both say TEUs.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "portla-081926.png"

# (month, Total TEUs) -- Port of Los Angeles, Historical TEU Statistics 2026
DATA = [
    ("JAN",   812000.25),
    ("FEB",   824323.25),
    ("MAR",   752519.50),
    ("APR",   890861.00),
    ("MAY",   840164.50),
    ("JUN",  1002734.00),
    ("JUL",   960464.25),
]

# Port of Los Angeles, Historical TEU Statistics 2025, July row
JULY_2025_RECORD = 1019837.30

INK    = "#12263f"
CORAL  = "#e2574c"
SLATE  = "#4a6b8a"
MUTED  = "#6b7280"
GROUND = "#fdf6e8"   # warm cream (house style)
GRID   = "#e7ddc9"


def teu_label(v):
    """Round half UP, never Python's default half-to-even (see memory note)."""
    if v >= 1_000_000:
        m = Decimal(v) / Decimal(1_000_000)
        return f"{m.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}M"
    k = Decimal(v) / Decimal(1_000)
    return f"{k.quantize(Decimal('1'), rounding=ROUND_HALF_UP)}K"


fig, ax = plt.subplots(figsize=(12.6, 6.8))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

# Value labels sit INSIDE the top of each bar. They were originally drawn above
# the bars, which is what the supplied graphic did, but the July 2025 record line
# lands at 1.02M and struck straight through the "960K" and "1.00M" labels. Only
# looking at the rendered PNG showed it.
xs = list(range(len(DATA)))
for x, (month, val) in zip(xs, DATA):
    is_july = month == "JUL"
    color = CORAL if is_july else SLATE
    ax.bar(x, val, width=0.62, color=color, zorder=3)
    ax.text(x, val - 30000, teu_label(val), ha="center", va="top",
            fontsize=15, fontweight="bold", color=GROUND, zorder=4)
    ax.text(x, -46000, month, ha="center", va="top", fontsize=13,
            fontweight="bold", color=INK if is_july else MUTED, zorder=4)

# the record July, so the "second-busiest" claim is checkable on the chart
ax.axhline(JULY_2025_RECORD, color=MUTED, linewidth=1.4,
           linestyle=(0, (6, 5)), zorder=2)
ax.text(-0.62, JULY_2025_RECORD + 22000,
        f"July 2025 record  {teu_label(JULY_2025_RECORD)}",
        ha="left", va="bottom", fontsize=11.5, fontstyle="italic",
        color=MUTED, zorder=4)

ax.set_xlim(-0.72, len(DATA) - 0.28)
ax.set_ylim(0, 1_180_000)
ax.set_xticks([])
ax.set_yticks([0, 250_000, 500_000, 750_000, 1_000_000])
ax.set_yticklabels(["0", "250K", "500K", "750K", "1M"], fontsize=12, color=MUTED)
ax.grid(axis="y", color=GRID, linewidth=1.1, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("Second-Busiest July Ever at the Port of L.A.", fontsize=25,
             fontweight="bold", color=INK, loc="left", pad=46)
ax.text(0.0, 1.045, "Total monthly container volume, 2026 (TEUs)",
        transform=ax.transAxes, fontsize=12.5, fontweight="bold", color=MUTED,
        ha="left")

fig.text(0.012, 0.014, "Source: Port of Los Angeles, historical TEU statistics "
         "(TEUs, twenty-foot equivalent units)", fontsize=9.5, color="#a99f88",
         ha="left")

fig.subplots_adjust(left=0.085, right=0.985, top=0.80, bottom=0.115)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)

ytd = sum(v for _, v in DATA)
print("wrote", OUT, "| months:", len(DATA))
print("  July 2026 %.0f vs July 2025 record %.0f -> %+.2f%% YoY"
      % (DATA[-1][1], JULY_2025_RECORD,
         (DATA[-1][1] / JULY_2025_RECORD - 1) * 100))
print("  YTD through July: %.0f TEUs" % ytd)
print("  labels:", ", ".join(f"{m} {teu_label(v)}" for m, v in DATA))
