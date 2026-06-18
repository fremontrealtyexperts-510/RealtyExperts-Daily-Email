#!/usr/bin/env python3
"""
make-fedfunds-chart.py  [out.png]

Recreates the Market Briefs "The Fed's Interest Rate" chart for the 06/17/26
daily email (Fed-decision day). Same data story + labeled anchors as the source
graphic (2019 ~2.4% bump, the 2020 COVID crash to ~0, the 2023-24 5.33% peak,
and 3.63% now) — only the styling is our own (clean light theme, RE blue, RE
branding). Series: Federal Funds Effective Rate, monthly, Jan 2016 - Jun 2026
(FRED: FEDFUNDS).

Run with python3.13 (the interpreter that has matplotlib on this Mac).
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = sys.argv[1] if len(sys.argv) > 1 else "fed-funds-rate-061726.png"

# Federal Funds Effective Rate, monthly, Jan 2016 -> Jun 2026 (FRED FEDFUNDS).
SERIES_BY_YEAR = {
    2016: [0.34, 0.38, 0.36, 0.37, 0.37, 0.38, 0.39, 0.40, 0.40, 0.40, 0.41, 0.54],
    2017: [0.65, 0.66, 0.79, 0.90, 0.91, 1.04, 1.15, 1.16, 1.15, 1.15, 1.16, 1.30],
    2018: [1.41, 1.42, 1.51, 1.69, 1.70, 1.82, 1.91, 1.91, 1.95, 2.19, 2.20, 2.27],
    2019: [2.40, 2.40, 2.41, 2.42, 2.39, 2.38, 2.40, 2.13, 2.04, 1.83, 1.55, 1.55],
    2020: [1.55, 1.58, 0.65, 0.05, 0.05, 0.08, 0.09, 0.10, 0.09, 0.09, 0.09, 0.09],
    2021: [0.08, 0.08, 0.07, 0.07, 0.06, 0.08, 0.10, 0.09, 0.08, 0.08, 0.08, 0.08],
    2022: [0.08, 0.08, 0.20, 0.33, 0.77, 1.21, 1.68, 2.33, 2.56, 3.08, 3.78, 4.10],
    2023: [4.33, 4.57, 4.65, 4.83, 5.06, 5.08, 5.12, 5.33, 5.33, 5.33, 5.33, 5.33],
    2024: [5.33, 5.33, 5.33, 5.33, 5.33, 5.33, 5.33, 5.13, 4.83, 4.64, 4.48, 4.33],
    2025: [4.33, 4.33, 4.33, 4.33, 4.33, 4.33, 4.20, 4.10, 3.95, 3.83, 3.72, 3.66],
    2026: [3.65, 3.64, 3.63, 3.63, 3.63, 3.63],  # Jan-Jun 2026
}

xs, ys = [], []
for yr in sorted(SERIES_BY_YEAR):
    for m, v in enumerate(SERIES_BY_YEAR[yr]):
        xs.append(yr + m / 12.0)
        ys.append(v)

BLUE = "#2563eb"
INK = "#0f172a"
MUTED = "#64748b"
GOLD = "#a8852e"
GRID = "#e2e8f0"
BG = "#fdf8ef"   # faint warm cream — premium feel, still our own clean theme

fig, ax = plt.subplots(figsize=(12, 6.3))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# area fill + line
ax.fill_between(xs, ys, color=BLUE, alpha=0.10, zorder=2)
ax.plot(xs, ys, color=BLUE, linewidth=3.4, solid_capstyle="round",
        solid_joinstyle="round", zorder=3)

# --- peak marker (5.33%, first reached Aug 2023) ---
peak_x = 2023 + 7 / 12.0
ax.scatter([peak_x], [5.33], s=70, color=BLUE, zorder=5,
           edgecolor="white", linewidth=1.5)
ax.text(peak_x + 0.06, 5.93, "2023–24 PEAK", fontsize=12.5,
        fontweight="bold", color=GOLD, ha="left", va="bottom")
ax.text(peak_x + 0.06, 5.40, "5.33%", fontsize=20, fontweight="bold",
        color=INK, ha="left", va="bottom")

# --- current marker (3.63%) ---
cx, cy = xs[-1], ys[-1]
ax.scatter([cx], [cy], s=80, color=BLUE, zorder=6,
           edgecolor="white", linewidth=1.6)
ax.annotate("3.63%", xy=(cx, cy), xytext=(cx + 0.30, cy),
            fontsize=20, fontweight="bold", color="white", va="center", ha="left",
            bbox=dict(boxstyle="round,pad=0.45", fc=BLUE, ec="none"), zorder=7)

# axes
ax.set_xlim(2015.85, 2027.9)
ax.set_ylim(0, 6.25)
ax.set_yticks([0, 1, 2, 3, 4, 5, 6])
ax.set_yticklabels([f"{v}%" for v in [0, 1, 2, 3, 4, 5, 6]],
                   fontsize=13, fontweight="bold", color=MUTED)
ax.set_xticks(list(range(2016, 2027)))
ax.set_xticklabels([str(y) for y in range(2016, 2027)],
                   fontsize=13, fontweight="bold", color=INK)
ax.tick_params(axis="both", length=0)
ax.grid(axis="y", color=GRID, linewidth=1.0, linestyle=(0, (1, 3)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#1f2937")
ax.spines["bottom"].set_linewidth(1.4)

# titles
ax.set_title("The Fed's Interest Rate", fontsize=30, fontweight="bold",
             color=INK, loc="left", pad=34)
ax.text(0.0, 1.055, "Federal Funds Effective Rate  •  2016–2026",
        transform=ax.transAxes, fontsize=14.5, color=GOLD, ha="left", fontweight="bold")

# source + branding footer
fig.text(0.012, 0.015,
         "Source: Federal Reserve (FRED, FEDFUNDS)  •  "
         "REALTY EXPERTS® · TeamRealtyExperts.com",
         fontsize=9.5, color="#94a3b8", ha="left")

fig.subplots_adjust(left=0.062, right=0.965, top=0.80, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor=BG)
plt.close(fig)
print("wrote", OUT)
