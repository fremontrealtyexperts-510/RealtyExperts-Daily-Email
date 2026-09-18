#!/usr/bin/env python3
"""
make-portla-chinashare-chart.py  [outdir]

Recreation of the "China's Slide at the Port of LA" graphic Harv supplied for the
09/18/26 edition. Emits BOTH variants:

  portla-chinashare-091826.png      plain monogram  -> RE email + Agent Hub
  portla-chinashare-091826-hb.png   + wordmark      -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/18/26
=============================================================================

Series re-pulled from the source the graphic credits. VIZION's "Port of LA's
\$3.4B Budget and China's Import Decline" (published June 30, 2026) carries the
series and credits "Source: Port of Los Angeles, FreightWaves". Its own chart
data, read off the page, against the supplied graphic:

  year    supplied graphic   published series   verdict
  2020    61%                61%                match
  2021    58%                58%                match
  2022    56%                56%                match
  2023    54%                54%                match
  2024    about 53.5%        53.4%              corrected to 53.4%
  2025    about 53.5%        53.4%              corrected to 53.4%
  2026    40%                about 40%          match, but see below

Prose in the same piece: "In 2020, China accounted for 61% of the containerized
imports moving through Los Angeles. By 2025 that share had fallen to 53.4%. In
2026 it sits at approximately 40%."

★ THE 2026 POINT IS AN ESTIMATE, AND THE SUPPLIED GRAPHIC OVERSTATED IT. Its
footnote read "2026 share confirmed by Port of LA, Sept. 2026". Nothing found
supports a September confirmation: the series is from a June 30, 2026 article
and that article itself labels the year "2026E". Searches for a later Port of
Los Angeles statement of the China share returned nothing. So this chart labels
the point "2026 estimate", dashes the final segment, and the footnote gives the
June 30 publication date instead of a confirmation that does not exist.

★ NOT PLOTTED, on purpose: the same source's "2026E Total TEU: 9.30M". The 9.3M
figure FreightWaves reports is a FISCAL 2026-2027 forecast, while the chart's
other TEU values are calendar years, so the two bases do not belong on one line.
This chart carries share only, which is the story anyway.

Cross check from the port itself (portoflosangeles.org facts and figures, top
trading partners by value, calendar years): China/Hong Kong \$112B in 2023,
\$120B in 2024, \$82B in 2025. That is a 32% drop in value from 2024 to 2025,
which is a different basis (value, not TEU share) and so is quoted in the copy
rather than drawn here.

matplotlib only; build with python3.13 on Mac.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "091826"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
GRID = "#d8cdb8"
MUTED = "#8a8172"

YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026]
SHARE = [61.0, 58.0, 56.0, 54.0, 53.4, 53.4, 40.0]
LABELS = ["2020", "2021", "2022", "2023", "2024", "2025", "2026\nestimate"]

fig, ax = plt.subplots(figsize=(11.2, 6.3), dpi=115)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

xs = list(range(len(YEARS)))

# reported run 2020 to 2025, then the estimated final leg
ax.plot(xs[:6], SHARE[:6], color=CORAL, linewidth=3.0, zorder=4)
ax.plot(xs[5:], SHARE[5:], color=CORAL, linewidth=3.0, linestyle=(0, (6, 4)),
        zorder=4)
ax.fill_between(xs, SHARE, 36, color=CORAL, alpha=0.10, zorder=2)
ax.scatter(xs[:6], SHARE[:6], s=70, facecolor=CREAM, edgecolor=CORAL,
           linewidth=2.4, zorder=5)
ax.scatter([xs[6]], [SHARE[6]], s=90, facecolor=CREAM, edgecolor=DEEP,
           linewidth=2.6, zorder=5)

for x, v in zip(xs[1:6], SHARE[1:6]):
    ax.text(x, v + 1.6, f"{v:g}%", ha="center", va="bottom", fontsize=11.5,
            color=MUTED)

ax.annotate("61%", xy=(xs[0], SHARE[0]), xytext=(xs[0] + 0.12, SHARE[0] + 2.6),
            fontsize=17, fontweight="bold", color="#5c5346")
ax.annotate("about 40%", xy=(xs[6], SHARE[6]), xytext=(xs[6] - 0.62, SHARE[6] - 4.2),
            fontsize=17, fontweight="bold", color="#ffffff",
            bbox=dict(boxstyle="round,pad=0.45", facecolor=DEEP, edgecolor="none"))

ax.set_xticks(xs)
ax.set_xticklabels(LABELS, fontsize=12.5, fontweight="bold", color=INK)
ax.tick_params(axis="x", length=0, pad=8)
ax.set_yticks([40, 45, 50, 55, 60, 65])
ax.set_yticklabels(["40%", "45%", "50%", "55%", "60%", "65%"], fontsize=11,
                   color=MUTED)
ax.set_ylim(34, 67)
ax.set_xlim(-0.45, 6.45)
ax.grid(axis="y", color=GRID, linewidth=0.9, alpha=0.7, linestyle=(0, (4, 4)),
        zorder=0)
ax.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(GRID)

ax.set_title("China's Slide at the Port of LA", fontsize=25, fontweight="bold",
             color=INK, pad=32, loc="left", x=0)
ax.text(0, 1.045,
        "China's share of containerized imports through the Port of Los Angeles",
        transform=ax.transAxes, fontsize=13, color=MUTED)

fig.text(0.008, 0.028,
         "Source: Port of Los Angeles and FreightWaves data, compiled by VIZION, June 30, 2026. The 2026 share is that piece's\n"
         "estimate for the year, not a final or confirmed figure.",
         fontsize=9.2, color=MUTED, ha="left", va="bottom", linespacing=1.5)

fig.subplots_adjust(left=0.075, right=0.985, top=0.845, bottom=0.175)

out = os.path.join(OUTDIR, f"portla-chinashare-{STAMP}.png")
plain, branded = save_pair(fig, out, facecolor=CREAM)
print("wrote", plain)
print("wrote", branded)
