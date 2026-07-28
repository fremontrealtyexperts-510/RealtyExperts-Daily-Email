#!/usr/bin/env python3
"""
make-tariffrate-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "Average Statutory Tariff Rate on
Select Goods" graphic (Tax Policy Center) Harv supplied for the 07/28/26 daily
email. OUR OWN branded chart, not the source image: warm cream ground, step
lines by product category, and each series' latest rate called out in a rounded
pill at the right edge.

Story tie-in (Market Briefs, 07/28/26): China said the U.S. agreed to cap a new
set of tariffs on Chinese goods at 20%, while the two sides still argue over AI
sanctions, and the Fed meets this week with inflation running at 3.5% partly on
tariff costs. Steel and aluminum carry by far the heaviest statutory rate, which
is why this lands in the Economy section and matters to anyone pricing a build.

Data: U.S. effective statutory tariff rate by product category, Oct 2024 through
early 2027, transcribed faithfully from the Tax Policy Center source graphic
Harv provided. Latest values: Steel & Aluminum 52.6%, Semiconductors 10.3%,
All Goods 10.2%, Automobiles 9.4%, Food 5.7%, Pharmaceuticals 4.7%.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "tariffrate-072826.png"

# month index 0 = Oct 2024 ... 29 = Mar 2027
N = 30

# (label, color, linestyle, monthly step series)
SERIES = [
    ("Steel & Aluminum", "#1d4ed8", "-", [
        6.0, 6.0, 6.0, 6.0, 6.0, 30.0, 31.0, 53.5, 53.5, 54.5,
        54.5, 53.0, 53.0, 53.0, 52.3, 52.3, 52.6, 52.6, 52.6, 52.6,
        52.6, 52.6, 52.6, 52.6, 52.6, 52.6, 52.6, 52.6, 52.6, 52.6]),
    ("All Goods", "#111111", ":", [
        1.5, 1.5, 1.5, 1.5, 2.5, 8.0, 19.5, 13.0, 14.0, 15.0,
        14.5, 16.0, 13.0, 12.0, 11.5, 8.0, 10.2, 10.2, 10.2, 10.2,
        10.2, 10.2, 10.2, 10.2, 10.2, 10.2, 10.2, 10.2, 10.2, 10.2]),
    ("Semiconductors", "#6b7280", "-", [
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 11.0, 10.0, 10.5, 10.5,
        10.5, 10.5, 11.0, 11.0, 11.5, 14.0, 13.5, 13.5, 11.0, 10.3,
        10.3, 10.3, 10.3, 10.3, 10.3, 10.3, 10.3, 10.3, 10.3, 10.3]),
    ("Automobiles", "#ef4444", "-", [
        1.0, 1.0, 1.0, 1.0, 1.0, 1.5, 15.5, 15.0, 16.0, 16.0,
        14.0, 14.0, 12.5, 12.0, 11.5, 9.4, 9.4, 9.4, 9.4, 9.4,
        9.4, 9.4, 9.4, 9.4, 9.4, 9.4, 9.4, 9.4, 9.4, 9.4]),
    ("Food", "#eab308", "-", [
        1.0, 1.0, 1.0, 1.0, 1.2, 11.8, 12.0, 9.0, 10.0, 12.0,
        12.0, 14.0, 14.0, 14.0, 14.0, 2.5, 5.7, 5.7, 5.7, 5.7,
        5.7, 5.7, 5.7, 5.7, 5.7, 5.7, 5.7, 5.7, 5.7, 5.7]),
    ("Pharmaceuticals", "#0d9488", "-", [
        0.2, 0.2, 0.2, 0.2, 0.2, 0.3, 0.5, 0.5, 0.5, 0.5,
        0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,
        0.5, 0.5, 0.5, 0.5, 4.7, 4.7, 4.7, 4.7, 4.7, 4.7]),
]

INK    = "#12263f"
MUTED  = "#6b7280"
GROUND = "#fdf6e8"   # warm cream (house style)
GRID   = "#e7ddc9"

XTICKS = [(0, "Oct\n2024"), (3, "Jan\n2025"), (6, "Apr"), (9, "Jul"),
          (12, "Oct"), (15, "Jan\n2026"), (18, "Apr"), (21, "Jul"),
          (24, "Oct"), (27, "Jan\n2027")]

x = list(range(N))

fig, ax = plt.subplots(figsize=(12.6, 6.6))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

for label, color, ls, vals in SERIES:
    ax.step(x, vals, where="post", color=color, linewidth=2.6 if ls == "-" else 2.4,
            linestyle=ls, zorder=4, solid_capstyle="butt")

# end-value pills, nudged apart so the crowded low band stays readable
END_Y = {"Steel & Aluminum": 52.6, "Semiconductors": 15.5, "All Goods": 11.4,
         "Automobiles": 7.3, "Food": 3.2, "Pharmaceuticals": -0.9}
for label, color, ls, vals in SERIES:
    v = vals[-1]
    ty = END_Y[label]
    ax.annotate(f"{v}%", xy=(N - 1, v), xytext=(N + 1.5, ty),
                fontsize=13, fontweight="bold", color="white", va="center",
                ha="center", zorder=7, annotation_clip=False,
                bbox=dict(boxstyle="round,pad=0.34", facecolor=color,
                          edgecolor="none"),
                arrowprops=dict(arrowstyle="-", color="#b9b0a0", linewidth=0.9,
                                linestyle=(0, (2, 2))))
    ax.plot([N - 1], [v], "o", color=color, markersize=6, zorder=6)

ax.set_xlim(0, N + 3.2)
ax.set_ylim(-3.2, 58)
ax.set_yticks([0, 10, 20, 30, 40, 50])
ax.set_yticklabels(["0%", "10%", "20%", "30%", "40%", "50%"], fontsize=12,
                   color=MUTED)
ax.set_xticks([i for i, _ in XTICKS])
ax.set_xticklabels([m for _, m in XTICKS], fontsize=11.5, fontweight="bold",
                   color=MUTED)
ax.grid(axis="y", color=GRID, linewidth=1.1, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("Average Statutory Tariff Rate on Select Goods", fontsize=24,
             fontweight="bold", color=INK, loc="left", pad=54)
ax.text(0.0, 1.105, "U.S. effective statutory rate by product category, "
        "Oct 2024 to early 2027",
        transform=ax.transAxes, fontsize=12.5, color=MUTED, ha="left")

# legend row under the subtitle
handles = [plt.Line2D([], [], color=c, linewidth=2.8, linestyle=ls, label=lab)
           for lab, c, ls, _ in SERIES]
ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.0, 1.005),
          ncol=6, frameon=False, fontsize=11.5, handlelength=1.6,
          columnspacing=1.25, handletextpad=0.5,
          prop={"weight": "bold", "size": 11.5})

fig.text(0.012, 0.014, "Source: Tax Policy Center", fontsize=9.5,
         color="#a99f88", ha="left")

fig.subplots_adjust(left=0.055, right=0.925, top=0.775, bottom=0.115)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, "| series:", len(SERIES),
      "| steel", SERIES[0][3][-1], "% vs all goods", SERIES[1][3][-1], "%")
