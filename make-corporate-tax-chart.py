#!/usr/bin/env python3
"""
make-corporate-tax-chart.py  [out.png]

REALTY EXPERTS branded recreation of the "Corporate Tax Rates Around the World"
bar chart for the 07/06/26 daily email (Market Briefs "✌️ Moving out." — the
Ireland corporate-tax boom: three U.S. companies paid nearly half of Ireland's
corporate taxes; Ireland's 12.5% rate is far below the OECD average). OUR OWN
branded chart, not the source image.

Warm cream ground (Meridian paper), blue bars, the U.S. bar highlighted, and a
dashed OECD-average line at 24.2 with a callout. Source line only (no RE
authorship label, per Harv 06/29). Run with python3.13.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "corporate-tax-rates-070626.png"

# (country code, max corporate income tax rate %) — descending, selected OECD.
BARS = [
    ("FR", 36.1), ("CO", 35.0), ("DE", 30.1), ("AU", 30.0), ("US", 25.6),
    ("GB", 25.0), ("IT", 24.0), ("CH", 19.6), ("IE", 12.5), ("HU", 9.0),
]
OECD_AVG = 24.2

codes = [b[0] for b in BARS]
vals  = [b[1] for b in BARS]
x = list(range(len(BARS)))

BLUE     = "#3b82f6"   # standard bars (faithful to source blue)
BLUE_LT  = "#93c5fd"
US_HL    = "#B08C1E"   # highlight the U.S. bar (Meridian gold)
GOLD     = "#B08C1E"   # OECD-average line
GROUND   = "#FAF7F0"   # Meridian paper
INK      = "#2e2e2e"
MUTED    = "#8a8172"

fig, ax = plt.subplots(figsize=(12, 6.6))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

colors = [BLUE] * len(BARS)
colors[codes.index("US")] = US_HL  # U.S. stands out (the audience's country)
bars = ax.bar(x, vals, width=0.66, color=colors, zorder=3)

# value labels above each bar
for xi, v in zip(x, vals):
    ax.text(xi, v + 0.5, f"{v:.1f}", ha="center", va="bottom",
            fontsize=15, fontweight="bold", color=INK)

# OECD average dashed line + right-side callout
ax.axhline(OECD_AVG, color=GOLD, linestyle=(0, (6, 4)), linewidth=2.0, zorder=2)
ax.text(len(BARS) - 0.35, OECD_AVG + 0.9,
        f"OECD average\n(38 countries)  {OECD_AVG:.1f}",
        ha="right", va="bottom", fontsize=11.5, fontweight="bold", color=GOLD)

# titles
ax.set_title("Corporate Tax Rates Around the World", fontsize=23,
             fontweight="bold", color=INK, loc="center", pad=26)
ax.text(0.5, 1.015, "Maximum corporate income tax rate, selected OECD countries, 2025 (%)",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="center")

# axes cosmetics
ax.set_xticks(x)
ax.set_xticklabels(codes, fontsize=14, fontweight="bold", color=INK)
ax.set_ylim(0, 40)
ax.set_yticks([0, 10, 20, 30, 40])
ax.set_yticklabels(["0", "10", "20", "30", "40"], fontsize=12, color=MUTED)
ax.tick_params(axis="both", length=0)
ax.grid(axis="y", color="#e7ddc9", linewidth=1.0, zorder=0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#d8cbb0")
ax.set_xlim(-0.6, len(BARS) - 0.4)

fig.text(0.012, 0.012, "Source: OECD", fontsize=10, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.055, right=0.975, top=0.84, bottom=0.10)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT)
