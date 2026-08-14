#!/usr/bin/env python3
"""
make-ppi-chart.py  [out.png]

REALTY EXPERTS recreation of the "US Producer Price Inflation Eases More Than
Expected" graphic Harv supplied for the 08/14/26 daily email. OUR OWN branded
chart, not the source image: warm cream ground, core PPI as amber bars, headline
PPI as a dark ink line, and the July 2026 endpoint called out at the right.

Story tie-in (Market Briefs, 08/14/26): wholesale prices were expected to rise
0.2% in July and came in flat instead (final demand SA was -0.03% month over
month). Year over year the headline eased to 4.7% from 5.5% in June, the third
straight month of cooling off the April to May peak. Mortgage News Daily called
out the PPI read as one reason the 30-year fixed hit a four week low, which is
why this lands in the Economy section and matters to anyone quoting a rate.

Data: VERIFIED against the BLS public API, not traced off the supplied graphic.
  headline = WPUFD4     (PPI final demand, NSA index)
  core     = WPUFD49104 (final demand less foods and energy, NSA index)
Year over year computed as index[m] / index[m-12] - 1, Jan 2022 through Jul 2026
(55 months). Endpoint July 2026: headline 4.69%, core 4.16%, which is what the
supplied graphic rounded to 4.7% and 4.2%. Every point diffed against the
graphic before this was drawn; the graphic read the May 2026 headline peak as
about 6.0% where BLS has 5.86%, and the bars follow BLS.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "ppi-081426.png"

# (year, month, headline YoY %, core YoY %) -- from BLS WPUFD4 / WPUFD49104
DATA = [
    (2022, 1, 10.07, 8.61), (2022, 2, 10.40, 8.86), (2022, 3, 11.66, 9.71),
    (2022, 4, 11.17, 8.96), (2022, 5, 11.09, 8.62), (2022, 6, 11.23, 8.30),
    (2022, 7, 9.75, 7.60),  (2022, 8, 8.71, 7.21),  (2022, 9, 8.48, 7.17),
    (2022, 10, 8.18, 6.93), (2022, 11, 7.40, 6.25), (2022, 12, 6.42, 5.71),
    (2023, 1, 5.74, 5.02),  (2023, 2, 4.74, 4.63),  (2023, 3, 2.66, 3.34),
    (2023, 4, 2.26, 3.11),  (2023, 5, 1.07, 2.79),  (2023, 6, 0.26, 2.54),
    (2023, 7, 1.13, 2.73),  (2023, 8, 1.91, 2.51),  (2023, 9, 1.82, 2.33),
    (2023, 10, 1.08, 2.16), (2023, 11, 0.77, 1.94), (2023, 12, 1.06, 1.79),
    (2024, 1, 1.05, 2.04),  (2024, 2, 1.63, 2.14),  (2024, 3, 1.98, 2.28),
    (2024, 4, 2.31, 2.54),  (2024, 5, 2.55, 2.70),  (2024, 6, 2.93, 3.27),
    (2024, 7, 2.39, 2.58),  (2024, 8, 2.07, 2.83),  (2024, 9, 2.14, 3.28),
    (2024, 10, 2.83, 3.58), (2024, 11, 2.91, 3.36), (2024, 12, 3.48, 3.75),
    (2025, 1, 3.81, 3.93),  (2025, 2, 3.43, 3.73),  (2025, 3, 3.15, 3.79),
    (2025, 4, 2.38, 3.07),  (2025, 5, 2.71, 3.20),  (2025, 6, 2.42, 2.68),
    (2025, 7, 3.19, 3.55),  (2025, 8, 2.66, 2.90),  (2025, 9, 3.04, 2.98),
    (2025, 10, 2.84, 2.97), (2025, 11, 3.14, 3.22), (2025, 12, 3.14, 3.43),
    (2026, 1, 3.08, 3.71),  (2026, 2, 3.37, 3.84),  (2026, 3, 4.29, 3.94),
    (2026, 4, 5.71, 4.93),  (2026, 5, 5.86, 4.43),  (2026, 6, 5.54, 4.72),
    (2026, 7, 4.69, 4.16),
]

INK    = "#12263f"
AMBER  = "#e0952a"
CORAL  = "#e2574c"
MUTED  = "#6b7280"
GROUND = "#fdf6e8"   # warm cream (house style)
GRID   = "#e7ddc9"

x    = list(range(len(DATA)))
head = [d[2] for d in DATA]
core = [d[3] for d in DATA]

fig, ax = plt.subplots(figsize=(12.6, 6.6))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.bar(x, core, width=0.68, color=AMBER, zorder=3, label="PPI excluding food and energy (year over year)")
ax.plot(x, head, color=INK, linewidth=2.9, zorder=5, solid_capstyle="round",
        label="Producer price index (year over year)")

# endpoint marker on the headline line
ax.plot([x[-1]], [head[-1]], "o", color=GROUND, markersize=11,
        markeredgecolor=INK, markeredgewidth=2.6, zorder=7)

# July 2026 callout block, right side
ax.text(0.995, 0.955, "JULY 2026", transform=ax.transAxes, fontsize=11.5,
        fontweight="bold", color=MUTED, ha="right", va="top",
        family="DejaVu Sans")
ax.text(0.995, 0.885, "4.7%", transform=ax.transAxes, fontsize=34,
        fontweight="bold", color=INK, ha="right", va="top")
ax.text(0.868, 0.858, "HEADLINE", transform=ax.transAxes, fontsize=11.5,
        fontweight="bold", color=MUTED, ha="right", va="top")
ax.text(0.995, 0.712, "4.2%", transform=ax.transAxes, fontsize=34,
        fontweight="bold", color=AMBER, ha="right", va="top")
ax.text(0.868, 0.685, "CORE", transform=ax.transAxes, fontsize=11.5,
        fontweight="bold", color=AMBER, ha="right", va="top")

# year ticks at each January
XT = [(i, str(d[0])) for i, d in enumerate(DATA) if d[1] == 1]
ax.set_xticks([i for i, _ in XT])
ax.set_xticklabels([lab for _, lab in XT], fontsize=13, fontweight="bold",
                   color=MUTED)

ax.set_ylim(0, 13.2)
ax.set_yticks([0, 2, 4, 6, 8, 10, 12])
ax.set_yticklabels(["0", "2", "4", "6", "8", "10", "12%"], fontsize=12,
                   color=MUTED)
ax.set_xlim(-1.1, len(DATA) + 0.2)
ax.grid(axis="y", color=GRID, linewidth=1.1, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("US Producer Price Inflation Eases More Than Expected",
             fontsize=24, fontweight="bold", color=INK, loc="left", pad=52)

handles = [
    plt.Line2D([], [], color=INK, linewidth=3.0,
               label="Producer price index (year over year)"),
    plt.Rectangle((0, 0), 1, 1, facecolor=AMBER,
                  label="PPI excluding food and energy (year over year)"),
]
ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.0, 1.005),
          ncol=2, frameon=False, handlelength=1.7, columnspacing=1.4,
          handletextpad=0.6, prop={"weight": "bold", "size": 12})

fig.text(0.012, 0.014, "Source: Bureau of Labor Statistics, producer price "
         "index for final demand", fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.052, right=0.985, top=0.80, bottom=0.115)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, "| months:", len(DATA),
      "| Jul 2026 headline", head[-1], "core", core[-1],
      "| peak headline", max(head), "at index", head.index(max(head)))
