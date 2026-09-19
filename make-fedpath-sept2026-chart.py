#!/usr/bin/env python3
"""
make-fedpath-sept2026-chart.py  [outdir]

Recreation of the FOMC projections table Harv supplied for the 09/19/26 edition,
turned into the one line a homebuyer actually needs: where the Fed now thinks its
own rate is going, against where it thought in June. Emits BOTH variants:

  fedpath-091926.png      plain monogram  -> RE email + Agent Hub
  fedpath-091926-hb.png   + wordmark      -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/19/26
=============================================================================

Every number parsed from the Federal Reserve's own table, not from the
screenshot: federalreserve.gov/monetarypolicy/fomcprojtabl20260916.htm
(Summary of Economic Projections, September 16, 2026), median rows:

  Federal funds rate   2026 4.1  2027 4.1  2028 3.9  2029 3.6  longer run 3.2
  June projection      2026 3.8  2027 3.6  2028 3.4  2029  n/a longer run 3.1
  PCE inflation        2026 3.7  2027 2.3  2028 2.1  2029 2.0  longer run 2.0
  June projection      2026 3.6  2027 2.3  2028 2.0  2029 2.0
  Core PCE inflation   2026 3.4  2027 2.5  2028 2.2  2029 2.0
  Change in real GDP   2026 2.3  2027 2.4  2028 2.2  2029 2.1  longer run 2.0
  Unemployment rate    2026 4.1  2027 4.1  2028 4.1  2029 4.1  longer run 4.2

All match the supplied screenshot, including its three red boxes (the 2026
column, PCE and core PCE reaching 2.0 in 2029, and the fed funds row against
its June line). June carried no 2029 column, which is why that marker is absent
from the June series here rather than drawn at zero.

Context line on the chart comes from the September 16 statement and its
implementation note: the target range is 3.75% to 4.00%, effective September 17.
The midpoint of that range is 3.875%, which is what the 4.1 median for 2026 is
measured against: about one more quarter point increase before the year ends.

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
STAMP = "091926"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
MUTED = "#8a8172"
GRID = "#d8cdb8"
SLATE = "#9aa5b1"

LABELS = ["End of\n2026", "End of\n2027", "End of\n2028", "End of\n2029", "Longer\nrun"]
SEPT = [4.1, 4.1, 3.9, 3.6, 3.2]
JUNE = [3.8, 3.6, 3.4, None, 3.1]
NOW = 3.875  # midpoint of the current 3.75% to 4.00% target range

xs = list(range(5))
fig, ax = plt.subplots(figsize=(11.2, 6.3), dpi=115)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

ax.axhline(NOW, color=INK, linewidth=1.3, linestyle=(0, (5, 4)), zorder=3)
ax.text(4.42, NOW + 0.045, "where the Fed's rate sits today, 3.75% to 4.00%",
        fontsize=10.5, color=INK, ha="right", va="bottom")

# June carried no 2029 column, so its line STOPS at 2028 and its longer-run
# point stands alone. Joining them would draw a segment across a year the Fed
# never projected.
jx = [x for x, v in zip(xs, JUNE) if v is not None]
jv = [v for v in JUNE if v is not None]
ax.plot(jx[:3], jv[:3], color=SLATE, linewidth=2.6, marker="o", markersize=9,
        markerfacecolor=CREAM, markeredgewidth=2.2, zorder=4,
        label="What the Fed expected in June")
ax.plot(jx[3:], jv[3:], color=SLATE, linewidth=0, marker="o", markersize=9,
        markerfacecolor=CREAM, markeredgewidth=2.2, zorder=4)
ax.plot(xs, SEPT, color=CORAL, linewidth=3.0, marker="o", markersize=10,
        markerfacecolor=CREAM, markeredgecolor=CORAL, markeredgewidth=2.6,
        zorder=5, label="What the Fed expects now")

for x, v in zip(xs, SEPT):
    ax.text(x, v + 0.11, f"{v:.1f}%", ha="center", va="bottom", fontsize=14,
            fontweight="bold", color=DEEP)
for x, v in zip(jx, jv):
    ax.text(x, v - 0.13, f"{v:.1f}%", ha="center", va="top", fontsize=12,
            color="#6f7b87")

ax.set_xticks(xs)
ax.set_xticklabels(LABELS, fontsize=12.5, fontweight="bold", color=INK)
ax.tick_params(axis="x", length=0, pad=10)
ax.set_yticks([3.0, 3.5, 4.0, 4.5])
ax.set_yticklabels(["3.0%", "3.5%", "4.0%", "4.5%"], fontsize=11, color=MUTED)
ax.tick_params(axis="y", length=0, colors=MUTED)
ax.set_ylim(2.85, 4.62)
ax.set_xlim(-0.45, 4.45)
ax.grid(axis="y", color=GRID, linewidth=0.9, alpha=0.7, zorder=0)
ax.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(GRID)

ax.set_title("The Fed Raised Its Own Forecast", fontsize=25, fontweight="bold",
             color=INK, pad=32, loc="left", x=0)
ax.text(0, 1.045,
        "The typical Fed official's forecast for the federal funds rate, September against June",
        transform=ax.transAxes, fontsize=12.5, color=MUTED)

ax.legend(loc="lower left", frameon=False, fontsize=11.5,
          bbox_to_anchor=(0.005, 0.02))

fig.text(0.008, 0.028,
         "Source: Federal Reserve, Summary of Economic Projections, September 16, 2026 (median projections). June had no 2029 column.\n"
         "The same projections put inflation at 3.7% this year, which is why the rate path moved up.",
         fontsize=9.2, color=MUTED, ha="left", va="bottom", linespacing=1.5)

fig.subplots_adjust(left=0.068, right=0.985, top=0.845, bottom=0.185)

out = os.path.join(OUTDIR, f"fedpath-{STAMP}.png")
plain, branded = save_pair(fig, out, facecolor=CREAM)
print("wrote", plain)
print("wrote", branded)
