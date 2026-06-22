#!/usr/bin/env python3
"""
make-mortgage-rates-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "U.S. Mortgage Rates — Share of
outstanding borrowers, by rate" graphic (source: National Mortgage Professional)
for the 06/22/26 daily email.

This is OUR OWN chart, not the source image: light RE-branded theme, a two-color
split that tells the lock-in story, and a "today's rate" marker. The data values
are faithful to the source.

  Share of outstanding borrowers, by current rate:
    Below 3% 20%  ·  3% to 4% 31.5%  ·  4% to 5% 18%  ·  5% to 6% 10%  ·  6%+ 21%

Story: ~70% of borrowers hold a rate under 5% — far below today's ~6.6% 30-year,
which is why so few homes come to market (the "lock-in effect").

matplotlib only. Run with python3.13 (the interpreter that has matplotlib on this Mac).
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "mortgage-rate-lockin-062226.png"

labels = ["Below 3%", "3% to 4%", "4% to 5%", "5% to 6%", "6%+"]
vals   = [20,          31.5,        18,          10,          21]

# Two-color split: UNDER 5% (cheap, locked-in money) vs 5%+ (at/above today's market)
TEAL      = "#0ea5e9"   # under-5% group
TEAL_DK   = "#0369a1"   # modal bar + under-5% value labels
ORANGE    = "#ea580c"   # RE-section orange — 6%+ (today's reality)
ORANGE_LT = "#fb923c"   # 5-6%
INK       = "#0f172a"
MUTED     = "#64748b"

# emphasize the modal 3-4% bar (deep teal) and the 6%+ bar (deep orange)
bar_colors = [TEAL, TEAL_DK, TEAL, ORANGE_LT, ORANGE]
lab_colors = [TEAL_DK, TEAL_DK, TEAL_DK, "#c2410c", "#c2410c"]

fig, ax = plt.subplots(figsize=(11.5, 6.4))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# light grouping bands behind the bars
ax.axvspan(-0.6, 2.5, color="#f0f9ff", zorder=0)   # under 5%
ax.axvspan(2.5, 4.6, color="#fff7ed", zorder=0)    # 5% and up

x = range(len(vals))
ax.bar(x, vals, width=0.72, color=bar_colors, zorder=3)

# value labels on each bar
for i, v in enumerate(vals):
    txt = f"{v:.1f}%" if v % 1 else f"{int(v)}%"
    ax.text(i, v + 0.7, txt, ha="center", va="bottom",
            fontsize=17, fontweight="bold", color=lab_colors[i], zorder=4)

# group "chip" labels that carry the headline stat
ax.text(1, 37.6, "≈ 70% locked in under 5%", ha="center", va="center",
        fontsize=12.5, fontweight="bold", color=TEAL_DK, zorder=5,
        bbox=dict(boxstyle="round,pad=0.55", fc="#e0f2fe", ec="none"))
ax.text(3.5, 37.6, "31% at 5% or higher", ha="center", va="center",
        fontsize=12.5, fontweight="bold", color="#c2410c", zorder=5,
        bbox=dict(boxstyle="round,pad=0.55", fc="#ffedd5", ec="none"))

# "today's rate" marker pointing at the left shoulder of the 6%+ bar
# (aimed off-center so the arrow never crosses the "21%" value label)
ax.annotate("Today's 30-yr ≈ 6.6%", xy=(3.72, 16.0), xytext=(3.92, 30.4),
            ha="center", va="bottom", fontsize=11, fontweight="bold", color="#9a3412",
            zorder=6,
            arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=2.2,
                            shrinkA=2, shrinkB=3, connectionstyle="arc3,rad=-0.18"),
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=ORANGE, lw=1.4))

# axes cosmetics — clean infographic look (no y-axis clutter)
ax.set_ylim(0, 41)
ax.set_xlim(-0.6, 4.6)
ax.set_xticks(list(x))
ax.set_xticklabels(labels, fontsize=14, fontweight="bold", color=INK)
ax.set_yticks([])
ax.tick_params(axis="x", length=0, pad=8)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#cbd5e1")

# titles
ax.set_title("U.S. Mortgage Rates", fontsize=27, fontweight="bold",
             color=INK, loc="left", pad=34)
ax.text(0.0, 1.055, "Share of outstanding borrowers, by current rate",
        transform=ax.transAxes, fontsize=13.5, color=MUTED, ha="left")

# source + branding footer
fig.text(0.012, 0.018,
         "Source: National Mortgage Professional   ·   "
         "Chart by REALTY EXPERTS®  ·  TeamRealtyExperts.com",
         fontsize=9.5, color="#94a3b8", ha="left")

fig.subplots_adjust(left=0.03, right=0.985, top=0.81, bottom=0.12)
fig.savefig(OUT, dpi=150, facecolor="white")
plt.close(fig)
print("wrote", OUT)
