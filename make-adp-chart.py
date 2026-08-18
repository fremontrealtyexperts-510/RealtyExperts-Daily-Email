#!/usr/bin/env python3
"""
make-adp-chart.py  [out.png]

REALTY EXPERTS recreation of the ADP private-payroll graphic Harv supplied for the
08/06/26 daily email. OUR OWN branded chart: warm cream ground, Economy green, and
July carried in coral because the cooldown IS the story.

Story tie-in (Market Briefs "July Hiring Stalls", 08/06/26): ADP said private
employers added just 44,000 jobs in July against expectations near 70-75K. That is
a macro labor story, so it lands in the Economy section.

Data: ADP National Employment Report, total nonfarm private employment, seasonally
adjusted, CURRENT vintage (FRED series ADPMNUSNERSA), differenced month over month.
Pulled from the series rather than transcribed from the graphic. The series diffs
reproduce ADP's own published prints exactly: July +44K and the revised June +95K
(ADP revised June down from 98K in the July release), and May +122K.

CORRECTIONS vs the supplied graphic (every month re-pulled and diffed):
    supplied:  Aug 48  Sep 86  Oct 21  Nov 74  Dec 38  Jan 12
               Feb 66  Mar 61  Apr 104 May 120 Jun 94  Jul 45
    actual:    Aug 49  Sep 88  Oct 20  Nov 74  Dec 37  Jan 11
               Feb 66  Mar 61  Apr 105 May 122 Jun 95  Jul 44
Ten of the twelve bars were off by 1 to 2 thousand, including the headline: the
graphic labeled July 45 where ADP published 44, and June 94 where ADP's revision
puts it at 95. Nov, Feb and Mar were the only exact matches. Nothing is inferred
here and no bar was dropped; all twelve reconcile to the published series.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "adp-payrolls-080626.png"

# (label, year, change in thousands) - ADP NER, SA, month over month
DATA = [
    ("Aug", "2025",  49),
    ("Sep", "2025",  88),
    ("Oct", "2025",  20),
    ("Nov", "2025",  74),
    ("Dec", "2025",  37),
    ("Jan", "2026",  11),
    ("Feb", "2026",  66),
    ("Mar", "2026",  61),
    ("Apr", "2026", 105),
    ("May", "2026", 122),
    ("Jun", "2026",  95),
    ("Jul", "2026",  44),
]
HILITE = len(DATA) - 1          # July 2026, the cooldown

GREEN     = "#9cc7a6"   # muted Economy green
GREEN_DK  = "#16a34a"   # Economy brand green
CORAL     = "#e2634a"   # the July bar
INK       = "#12263f"
MUTED     = "#6b7280"
GROUND    = "#fdf6e8"   # warm cream (house style)
GRID      = "#e7ddc9"

labels = [d[0] for d in DATA]
years  = [d[1] for d in DATA]
vals   = [d[2] for d in DATA]
x = list(range(len(DATA)))
avg = sum(vals) / len(vals)

fig, ax = plt.subplots(figsize=(12.4, 6.9))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

colors = [CORAL if i == HILITE else GREEN for i in x]
ax.bar(x, vals, width=0.66, color=colors, zorder=3, edgecolor=GROUND,
       linewidth=1.2)

span = max(vals)

# 12-month average reference, drawn UNDER the value labels
ax.axhline(avg, color="#c9bfa8", linewidth=1.4, linestyle=(0, (6, 5)), zorder=2)
ax.text(len(DATA) - 0.42, avg + span * 0.022, f"12-mo avg {avg:.0f}K",
        fontsize=10.5, color="#a2977f", ha="right", va="bottom", zorder=4)

for xi, v in zip(x, vals):
    strong = xi == HILITE
    ax.text(xi, v + span * 0.030, f"{v}",
            fontsize=15 if strong else 13.5,
            fontweight="bold",
            color=CORAL if strong else INK,
            ha="center", va="bottom", zorder=5)

ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=13, color=INK)
for tick, i in zip(ax.get_xticklabels(), x):
    if i == HILITE:
        tick.set_fontweight("bold")
        tick.set_color(CORAL)

# year markers under the month row, only where the year turns over
for xi, (lb, yr) in enumerate(zip(labels, years)):
    if xi == 0 or years[xi - 1] != yr:
        ax.text(xi, -span * 0.115, yr, fontsize=11, color=MUTED,
                ha="center", va="top", fontweight="bold")

ax.set_ylim(0, span * 1.17)
ax.set_yticks([])
ax.grid(axis="y", color=GRID, linewidth=1.0, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
ax.spines["bottom"].set_color("#d9cdb4")
ax.spines["bottom"].set_linewidth(1.2)

ax.set_title("US Private Payroll Growth Cooled In July", fontsize=24,
             fontweight="bold", color=INK, loc="left", pad=34)
ax.text(0.0, 1.055, "ADP employment change, month over month, in thousands",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="left")
ax.text(1.0, 1.055, "WEAKEST IN SIX MONTHS",
        transform=ax.transAxes, fontsize=14, fontweight="bold",
        color=CORAL, ha="right")

fig.text(0.012, 0.014,
         "Seasonally adjusted  |  Source: ADP National Employment Report",
         fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.045, right=0.985, top=0.840, bottom=0.135)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)

lowest6 = min(vals[-6:])
print("wrote", OUT, f"| {len(DATA)} months | Jul {vals[-1]}K "
      f"| 12-mo avg {avg:.1f}K | peak {max(vals)}K ({labels[vals.index(max(vals))]}) "
      f"| Jul is min of last 6 ({lowest6}K)")
