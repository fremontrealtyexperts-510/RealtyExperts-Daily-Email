#!/usr/bin/env python3
"""
make-gdp-chart.py  [out.png]

Clean recreation of the "U.S. GDP, % Change From Prior Quarter" bar chart for the
06/26/26 daily email, matching the Market Briefs "GDP Beats Forecasts" story
(final Q1 2026 real GDP grew 2.1%, beating the 1.6% forecast, revised up on AI
investment).

NOTE: per request, this chart carries NO Realty Experts branding. Source line is
the U.S. Bureau of Economic Analysis only.

matplotlib only. Run with python3.13 (the interpreter that has matplotlib here).
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "us-gdp-quarterly-062626.png"

# (quarter label, year label under the group, value %)
BARS = [
    ("Q4", "2024",  1.9),
    ("Q1", "",      -0.6),
    ("Q2", "",       3.8),
    ("Q3", "2025",   4.4),
    ("Q4", "",       0.5),
    ("Q1", "2026",   2.1),
]

labels = [b[0] for b in BARS]
years  = [b[1] for b in BARS]
vals   = [b[2] for b in BARS]
x = list(range(len(BARS)))

ORANGE     = "#d97706"   # standard bars
ORANGE_HL  = "#b45309"   # highlight the latest quarter
INK        = "#1f2937"
MUTED      = "#6b7280"

fig, ax = plt.subplots(figsize=(12, 6.4))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

colors = [ORANGE] * len(BARS)
colors[-1] = ORANGE_HL  # latest quarter stands out
bars = ax.bar(x, vals, width=0.62, color=colors, zorder=3)

# value labels above (positive) / below (negative) each bar
for xi, v in zip(x, vals):
    va = "bottom" if v >= 0 else "top"
    off = 0.12 if v >= 0 else -0.12
    ax.text(xi, v + off, f"{'+' if v >= 0 else ''}{v:.1f}", ha="center", va=va,
            fontsize=16, fontweight="bold", color=INK)

# zero baseline
ax.axhline(0, color="#9ca3af", linewidth=1.3, zorder=2)

# quarter labels + year sub-labels
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=14, color=INK)
for xi, yr in zip(x, years):
    if yr:
        ax.text(xi, -1.55, yr, ha="center", va="top", fontsize=14,
                fontweight="bold", color=MUTED)

# titles
ax.set_title("U.S. GDP, % Change From Prior Quarter", fontsize=23,
             fontweight="bold", color=INK, loc="center", pad=26)
ax.text(0.5, 1.015, "Real GDP growth, quarterly", transform=ax.transAxes,
        fontsize=13.5, color=MUTED, ha="center")

# axes cosmetics
ax.set_ylim(-1.2, 5.2)
ax.set_yticks([-1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
ax.set_yticklabels([f"{t:.1f}" for t in [-1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0]],
                   fontsize=12, color=MUTED)
ax.tick_params(axis="both", length=0)
ax.grid(axis="y", color="#e5e7eb", linewidth=1.0, zorder=0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.margins(x=0.02)
# room under the axis for the year labels
ax.set_xlim(-0.6, len(BARS) - 0.4)

# source footer (no Realty Experts branding, per request)
fig.text(0.012, 0.012, "Source: U.S. Bureau of Economic Analysis",
         fontsize=10, color="#94a3b8", ha="left")

fig.subplots_adjust(left=0.06, right=0.975, top=0.84, bottom=0.16)
fig.savefig(OUT, dpi=150, facecolor="white")
plt.close(fig)
print("wrote", OUT)
