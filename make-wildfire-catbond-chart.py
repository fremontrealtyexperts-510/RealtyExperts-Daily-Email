#!/usr/bin/env python3
"""
make-wildfire-catbond-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the wildfire catastrophe bond graphic Harv
supplied for the 08/04/26 daily email. OUR OWN branded chart, not the source
image: warm cream ground, Real-Estate-orange bars by year, the 2026 year-to-date
bar highlighted, and the 2025 full-year record drawn as a reference line so the
"already almost there with half a year to go" point reads at a glance.

Story tie-in (Market Briefs "Wildfire Bonds Heat Up", 08/04/26): insurers are
offloading California wildfire risk to capital markets and investors are taking
it for the yield. That is an insurance-availability story before it is a markets
story, so it lands in the Real Estate section.

Data: Artemis, catastrophe bond issuance carrying some level of exposure to
wildfire risk, by year. Pulled from Artemis's published figures, NOT transcribed
from the source graphic.

TWO CORRECTIONS vs the supplied graphic:
  1. Its 2026 bar read $5.0B and its 2023/2024 bars read $2.5B/$2.7B. Artemis
     publishes $5.183bn YTD 2026, $2.57bn for 2023 and $2.84bn for 2024.
  2. Its 2022 bar ($1.7B) is NOT in any Artemis figure I could source. Artemis's
     own August 2025 piece calls 2024's $2.84bn the "previous highest full-year
     total," which bounds 2022 but does not give it. Rather than publish an
     unverified bar, the series starts at 2023.
The 2026 figure is year-to-date through early July 2026 (20 series, including a
couple of mid-year deals that settled in early July), not a full year.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "wildfire-catbond-080426.png"

# (label, $ billions of wildfire-exposed cat bond issuance) - Artemis
DATA = [
    ("2023",  2.57),
    ("2024",  2.84),
    ("2025",  5.55),
    ("2026*", 5.183),
]
labels = [k for k, _ in DATA]
vals = [v for _, v in DATA]

RECORD = 5.55          # 2025 full-year record
CUR_I = len(DATA) - 1  # 2026 year-to-date

ORANGE    = "#f4a06a"   # muted history bars
ORANGE_DK = "#ea580c"   # Real Estate brand orange, for the current reading
INK       = "#12263f"
MUTED     = "#6b7280"
GROUND    = "#fdf6e8"   # warm cream (house style)
GRID      = "#e7ddc9"

x = list(range(len(DATA)))

fig, ax = plt.subplots(figsize=(12, 6.4))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

colors = [ORANGE_DK if i == CUR_I else ORANGE for i in x]
ax.bar(x, vals, width=0.56, color=colors, zorder=3, edgecolor=GROUND,
       linewidth=1.4)

# No record reference line: 2025 IS the record and sits right next to 2026, so a
# dashed line only duplicated that bar and collided with the 2026 value label.

# value label above each bar
for xi, v in zip(x, vals):
    weight = "bold" if xi == CUR_I else "normal"
    color = INK if xi == CUR_I else "#8a8172"
    ax.text(xi, v + 0.13, f"${v:.2f}B", fontsize=15, fontweight=weight,
            color=color, ha="center", va="bottom", zorder=5)

# current reading callout
ax.annotate("already 93% of the 2025 record,\nwith half the year still to run",
            xy=(CUR_I, vals[CUR_I]),
            xytext=(CUR_I - 0.40, vals[CUR_I] + 1.05),
            fontsize=12, fontweight="bold", color=ORANGE_DK, ha="center",
            zorder=6,
            arrowprops=dict(arrowstyle="-", color=ORANGE_DK, linewidth=1.2,
                            shrinkA=4, shrinkB=32))

ax.set_xlim(-0.62, len(DATA) - 0.38)
ax.set_ylim(0, 7.2)
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=15, fontweight="bold", color=MUTED)
ax.set_yticks([])
ax.grid(axis="y", color=GRID, linewidth=1.0, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
ax.spines["bottom"].set_color("#d9cdb4")
ax.spines["bottom"].set_linewidth(1.2)

ax.set_title("Investors Are Buying California's Wildfire Risk", fontsize=25,
             fontweight="bold", color=INK, loc="left", pad=30)
ax.text(0.0, 1.045,
        "Catastrophe bond issuance exposed to wildfire, per year",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="left")
ax.text(1.0, 1.045, "$5.18B SO FAR IN 2026",
        transform=ax.transAxes, fontsize=14.5, fontweight="bold",
        color=ORANGE_DK, ha="right")

fig.text(0.012, 0.014,
         "*2026 is year to date through early July  |  Source: Artemis",
         fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.035, right=0.985, top=0.82, bottom=0.095)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, f"| bars: {len(DATA)} | 2026 YTD ${vals[-1]:.3f}B "
      f"= {vals[-1]/RECORD*100:.0f}% of the 2025 record "
      f"| 2023->2026 {(vals[-1]/vals[0]-1)*100:+.0f}%")
