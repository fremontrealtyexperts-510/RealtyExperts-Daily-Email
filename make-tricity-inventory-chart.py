#!/usr/bin/env python3
"""
make-tricity-inventory-chart.py  [outdir]

Tri-City for-sale inventory month by month, January 2025 through August 2026.
Built for the 09/20/26 Sunday edition, where Harv asked for a dive into how
Fremont, Newark and Union City inventory has been flowing month to month.

  tricity-inventory-092026.png      plain monogram -> RE email + Agent Hub
  tricity-inventory-092026-hb.png   + wordmark     -> harvrealtor.com / .net / app

=============================================================================
SOURCE AND BASIS (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

No supplied graphic here, this is ours from scratch. Series come from Zillow
Research public CSVs, keyless, 200 to plain curl on 09/20/26:

  https://files.zillowstatic.com/research/public_csvs/invt_fs/
      City_invt_fs_uc_sfrcondo_sm_month.csv

City rows matched on RegionName + State == 'CA' + CountyName == 'Alameda
County', so no same named city in another state can leak in. Month columns
start at index 8.

BASIS: for-sale inventory, smoothed, single family plus condo, monthly. Every
city on this chart is on that one basis, so the three lines are comparable to
each other. It is NOT the same basis as the MLS board counts printed elsewhere
in the report, which are all property types including townhome and duet and
count BOMK and PCH status. The two must never be set against each other, per
the 09/06 basis mismatch lesson. The chart says which basis it is on.

ENDPOINT: Zillow lags a month. The newest column on 09/20/26 is 2026-08-31, so
the line stops at August 2026 and the subtitle says so rather than implying it
runs to today.

VALUES: the series are generated straight out of the CSV, never hand typed,
after a 49 of 80 hand typing error on 09/19. Regenerate with:

  python3 - <<'EOF'
  import csv
  r=list(csv.reader(open('zinv.csv'))); hdr=r[0]
  for row in r[1:]:
      if row[2] in ('Fremont','Newark','Union City') and row[5]=='CA' \
         and row[7]=='Alameda County':
          print(row[2], row[8:][-20:])
  EOF

SCALE: Fremont carries roughly four times the inventory of either neighbour, so
a single axis would flatten Newark and Union City into a crease at the bottom.
Two panels, each with its own axis, keeps every shape readable. The panels are
NOT a common scale and the chart does not pretend they are, so the comparison
the reader is invited to make is shape against shape, not height against height.

matplotlib only; build with python3.13 on Mac.
"""
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "092026"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
GREEN = "#2f8f5b"
ORANGE = "#e08b2f"
GRID = "#d8cdb8"
MUTED = "#8a8172"

# Zillow for-sale inventory, smoothed, SFR + condo, Alameda County cities.
# Generated from City_invt_fs_uc_sfrcondo_sm_month.csv on 2026-09-20.
MONTHS = [
    '2025-01-31', '2025-02-28', '2025-03-31', '2025-04-30', '2025-05-31',
    '2025-06-30', '2025-07-31', '2025-08-31', '2025-09-30', '2025-10-31',
    '2025-11-30', '2025-12-31', '2026-01-31', '2026-02-28', '2026-03-31',
    '2026-04-30', '2026-05-31', '2026-06-30', '2026-07-31', '2026-08-31',
]
INV = {
    'Fremont':    [150, 184, 250, 317, 362, 381, 386, 368, 361, 345, 309, 254, 216, 230, 282, 338, 381, 398, 394, 383],
    'Newark':     [50, 57, 72, 90, 103, 108, 106, 102, 101, 99, 88, 70, 57, 58, 74, 97, 114, 121, 117, 113],
    'Union City': [51, 54, 66, 78, 90, 98, 100, 93, 86, 74, 69, 56, 50, 53, 70, 88, 103, 107, 104, 93],
}

LABELS = ["Jan\n2025", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
          "Oct", "Nov", "Dec", "Jan\n2026", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug"]
JAN25, JAN26 = 0, 12
X = list(range(len(MONTHS)))


def pct(a, b):
    """Percent change b -> a, half up, never half to even."""
    return Decimal(str((a / b - 1) * 100)).quantize(Decimal("0.1"), ROUND_HALF_UP)


def style(ax):
    ax.set_facecolor(CREAM)
    ax.grid(axis="y", color=GRID, lw=0.7, alpha=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    # tick_params resets label colours, so recolour AFTER it every time.
    ax.tick_params(colors=MUTED, labelsize=9.5, length=0)
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_color(INK)


def january_bands(ax):
    """Mark the two winter troughs, which is where the story lives."""
    for j in (JAN25, JAN26):
        ax.axvline(j, color=MUTED, lw=1.0, ls=(0, (3, 3)), alpha=0.55, zorder=1)


fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(11.6, 8.5), sharex=True,
    gridspec_kw=dict(height_ratios=[1.28, 1], hspace=0.16))
fig.patch.set_facecolor(CREAM)

# ---------------------------------------------------------------- Fremont
style(ax1)
january_bands(ax1)
ax1.plot(X, INV["Fremont"], color=CORAL, lw=3.0, zorder=4,
         marker="o", ms=4.6, mfc=CREAM, mew=1.7, mec=CORAL)
ax1.set_ylim(0, 470)
ax1.set_ylabel("Homes for sale", color=INK, fontsize=10.5, labelpad=8)
ax1.text(0.006, 1.055, "FREMONT", transform=ax1.transAxes, fontsize=13,
         fontweight="bold", color=CORAL)

for j, note in ((JAN25, "150"), (JAN26, "216")):
    ax1.annotate(note, (j, INV["Fremont"][j]), xytext=(0, -20),
                 textcoords="offset points", ha="center", fontsize=11.5,
                 fontweight="bold", color=CORAL)
ax1.annotate("386", (6, 386), xytext=(0, 12), textcoords="offset points",
             ha="center", fontsize=10.5, color=MUTED)
ax1.annotate("398", (17, 398), xytext=(0, 12), textcoords="offset points",
             ha="center", fontsize=10.5, color=MUTED)

ax1.annotate(
    "The winter floor rose 44%.\nThe summer ceiling barely moved.",
    xy=(JAN26, 216), xytext=(13.5, 92),
    fontsize=10.8, color=INK, va="center",
    arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.3,
                    shrinkA=4, shrinkB=6,
                    connectionstyle="arc3,rad=-0.18"))

# ------------------------------------------------- Newark and Union City
style(ax2)
january_bands(ax2)
ax2.plot(X, INV["Newark"], color=GREEN, lw=2.7, zorder=4,
         marker="o", ms=4.2, mfc=CREAM, mew=1.6, mec=GREEN, label="Newark")
ax2.plot(X, INV["Union City"], color=ORANGE, lw=2.7, zorder=3,
         marker="s", ms=4.0, mfc=CREAM, mew=1.6, mec=ORANGE, label="Union City")
ax2.set_ylim(0, 152)
ax2.set_ylabel("Homes for sale", color=INK, fontsize=10.5, labelpad=8)

ax2.text(0.006, 1.075, "NEWARK", transform=ax2.transAxes, fontsize=13,
         fontweight="bold", color=GREEN)
ax2.text(0.148, 1.075, "and", transform=ax2.transAxes, fontsize=11,
         color=MUTED)
ax2.text(0.205, 1.075, "UNION CITY", transform=ax2.transAxes, fontsize=13,
         fontweight="bold", color=ORANGE)

ax2.annotate("50", (JAN25, 50), xytext=(-2, -19), textcoords="offset points",
             ha="center", fontsize=10.5, fontweight="bold", color=GREEN)
ax2.annotate("57", (JAN26, 57), xytext=(-2, 11), textcoords="offset points",
             ha="center", fontsize=10.5, fontweight="bold", color=GREEN)
ax2.annotate("51", (JAN25, 51), xytext=(14, 4), textcoords="offset points",
             ha="center", fontsize=10.5, fontweight="bold", color=ORANGE)
ax2.annotate("50", (JAN26, 50), xytext=(15, -13), textcoords="offset points",
             ha="center", fontsize=10.5, fontweight="bold", color=ORANGE)

ax2.annotate(
    "Union City started 2026 exactly where it started 2025,\n"
    "and is the one city with no inventory build.",
    xy=(19, 93), xytext=(9.4, 22),
    fontsize=10.5, color=INK, va="center",
    arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.3,
                    shrinkA=4, shrinkB=6,
                    connectionstyle="arc3,rad=0.16"))

ax2.set_xticks(X)
ax2.set_xticklabels(LABELS, fontsize=9)
for t in ax2.get_xticklabels():
    t.set_color(INK)
ax2.set_xlim(-0.6, len(X) - 0.4)

# ------------------------------------------------------------ titles
fig.text(0.062, 0.963,
         "Where the inventory actually went",
         fontsize=21, fontweight="bold", color=INK, ha="left")
fig.text(0.062, 0.929,
         "Homes for sale each month, January 2025 through August 2026. "
         "Each panel has its own scale.",
         fontsize=11.6, color=MUTED, ha="left")

fig.text(0.062, 0.022,
         "Zillow Research, for-sale inventory, smoothed, single family and condo, "
         "monthly through August 2026. Not the same basis as the MLS board counts.",
         fontsize=9.2, color=MUTED, ha="left")

fig.subplots_adjust(left=0.078, right=0.975, top=0.878, bottom=0.085)

out = os.path.join(OUTDIR, f"tricity-inventory-{STAMP}.png")
save_pair(fig, out, logo=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "hb-logo-mark.png"))

print()
print("Checks:")
for c in INV:
    print(f"  {c:<11} Jan25 {INV[c][JAN25]:>3} -> Jan26 {INV[c][JAN26]:>3} "
          f"({pct(INV[c][JAN26], INV[c][JAN25]):>+5}%)   "
          f"Aug25 {INV[c][7]:>3} -> Aug26 {INV[c][19]:>3} "
          f"({pct(INV[c][19], INV[c][7]):>+5}%)")
