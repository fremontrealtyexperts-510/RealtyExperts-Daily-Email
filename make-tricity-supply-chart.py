#!/usr/bin/env python3
"""
make-tricity-supply-chart.py  [outdir]

The flow behind the level: new listings arriving each month against the
standing for-sale inventory, Fremont plus Newark plus Union City combined,
January 2025 through August 2026. Built for the 09/20/26 Sunday edition.

  tricity-supply-092026.png      plain monogram -> RE email + Agent Hub
  tricity-supply-092026-hb.png   + wordmark     -> harvrealtor.com / .net / app

=============================================================================
SOURCE AND BASIS
=============================================================================

Two Zillow Research public CSVs, keyless, both 200 to plain curl on 09/20/26:

  .../public_csvs/invt_fs/City_invt_fs_uc_sfrcondo_sm_month.csv
  .../public_csvs/new_listings/City_new_listings_uc_sfrcondo_sm_month.csv

Same suffix on both files, `uc_sfrcondo_sm_month`, which is what makes the two
series safe to put on one chart: identical property scope (single family plus
condo), identical smoothing, identical monthly cadence, identical vintage.
Rows matched on RegionName + State 'CA' + CountyName 'Alameda County'.

WHY TWO AXES, AND THE HONEST VERSION OF THAT CHOICE. Bars are a monthly FLOW
(listings that arrived during the month) and the line is a monthly LEVEL (homes
standing on the market). They are different units and cannot share an axis
without inventing a comparison. Both axes therefore start at zero and each is
labelled with what it measures, so the reader is comparing SHAPE against shape.
No claim is made or implied that a bar height equals a line height.

WHAT IS NOT ON THIS CHART. The obvious third series, homes leaving the market,
is derivable as inv[m-1] + new[m] - inv[m], but Zillow's inventory is a
smoothed monthly average rather than a month end snapshot, so that identity
does not close cleanly and the residual would be an artefact of the smoothing
as much as of the market. Per the standing rule, a bar that cannot be sourced
gets dropped rather than estimated. The drain is described in the copy as an
inference from the two series that ARE plotted, and is not drawn as data.

ARITHMETIC. Both totals are January through August so the two years cover the
same eight months; comparing a partial 2026 against a full 2025 would be the
classic cropped window error. Percentages use Decimal with ROUND_HALF_UP.

Series generated straight from the CSVs, never hand typed.
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
SAND = "#c9b896"
DEEPSAND = "#a8906a"
GRID = "#d8cdb8"
MUTED = "#8a8172"

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
NEWL = {
    'Fremont':    [68, 104, 149, 173, 179, 169, 151, 132, 132, 127, 106, 75, 77, 100, 140, 162, 177, 166, 147, 137],
    'Newark':     [19, 29, 42, 47, 47, 40, 37, 34, 38, 37, 30, 20, 18, 26, 40, 49, 50, 48, 40, 40],
    'Union City': [22, 27, 38, 42, 45, 43, 40, 31, 30, 25, 27, 19, 20, 28, 39, 46, 44, 40, 35, 30],
}

TOT_INV = [sum(INV[c][i] for c in INV) for i in range(len(MONTHS))]
TOT_NEW = [sum(NEWL[c][i] for c in NEWL) for i in range(len(MONTHS))]

LABELS = ["Jan\n2025", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
          "Oct", "Nov", "Dec", "Jan\n2026", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug"]
X = list(range(len(MONTHS)))


def pct(a, b):
    return Decimal(str((a / b - 1) * 100)).quantize(Decimal("0.1"), ROUND_HALF_UP)


NEW_25 = sum(TOT_NEW[0:8])
NEW_26 = sum(TOT_NEW[12:20])
INV_AUG25, INV_AUG26 = TOT_INV[7], TOT_INV[19]
INV_JAN25, INV_JAN26 = TOT_INV[0], TOT_INV[12]

fig, ax = plt.subplots(figsize=(11.6, 6.9))
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

colors = [SAND] * 12 + [DEEPSAND] * 8
ax.bar(X, TOT_NEW, color=colors, width=0.66, zorder=3,
       label="New listings that month")
# Headroom to 780 is deliberate. Bars top out at 272 and the line at 626, so
# everything above 640 is empty on BOTH axes, which gives the callouts a band
# they can sit in without a series running through the text. The first render
# had the coral line crossing "1,699" and a minus sign, the exact vanishing
# minus the house rule warns about; the percentages are now spelled in words.
ax.set_ylim(0, 780)
ax.set_ylabel("New listings arriving each month", color=INK, fontsize=10.8,
              labelpad=9)
ax.grid(axis="y", color=GRID, lw=0.7, alpha=0.7)
ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_color(GRID)
ax.tick_params(colors=MUTED, labelsize=9.5, length=0)
for t in ax.get_xticklabels() + ax.get_yticklabels():
    t.set_color(INK)

ax2 = ax.twinx()
ax2.set_facecolor("none")
ax2.plot(X, TOT_INV, color=CORAL, lw=3.1, zorder=5, marker="o", ms=4.8,
         mfc=CREAM, mew=1.8, mec=CORAL, label="Homes standing for sale")
ax2.set_ylim(0, 780)
ax2.set_ylabel("Homes standing for sale", color=CORAL, fontsize=10.8,
               labelpad=11)
for s in ("top", "left", "bottom"):
    ax2.spines[s].set_visible(False)
ax2.spines["right"].set_color(GRID)
ax2.tick_params(colors=MUTED, labelsize=9.5, length=0)
for t in ax2.get_yticklabels():
    t.set_color(CORAL)

ax.set_xticks(X)
ax.set_xticklabels(LABELS, fontsize=9)
for t in ax.get_xticklabels():
    t.set_color(INK)
ax.set_xlim(-0.72, len(X) - 0.28)

# Year divider between Dec 2025 and Jan 2026.
ax.axvline(11.5, color=MUTED, lw=1.1, ls=(0, (4, 3)), alpha=0.6, zorder=2)

# Callouts live in the empty band above every series, keyed by colour to the
# thing they describe, and carry no arrows. An arrow to a bar has to cross the
# coral line, and the crossing is what put a line through the numbers before.
PEAK_25, PEAK_26 = max(TOT_INV[0:12]), max(TOT_INV[12:20])

ax2.text(0.6, 742,
         "The level ran higher all year",
         fontsize=11.6, fontweight="bold", color=CORAL, va="center")
ax2.text(0.6, 703,
         f"{PEAK_26} homes standing at the 2026 peak against {PEAK_25} in 2025, "
         f"and {INV_AUG26} in August against {INV_AUG25}",
         fontsize=10.4, color=INK, va="center")

ax2.text(0.6, 655,
         "The supply arriving barely moved",
         fontsize=11.6, fontweight="bold", color=DEEPSAND, va="center")
ax2.text(0.6, 617,
         f"{NEW_26:,} new listings January to August 2026 against "
         f"{NEW_25:,} over the same eight months of 2025, down "
         f"{abs(pct(NEW_26, NEW_25))}%",
         fontsize=10.4, color=INK, va="center")

lg = ax2.legend(
    handles=[ax.patches[13], ax2.lines[0]],
    labels=["New listings arriving that month (flow)",
            "Homes standing for sale (level)"],
    loc="upper right", bbox_to_anchor=(0.999, 0.999), frameon=False,
    fontsize=10.2, handlelength=1.8, ncol=1)
for t in lg.get_texts():
    t.set_color(INK)

fig.text(0.058, 0.955,
         "Same faucet, fuller tub",
         fontsize=21, fontweight="bold", color=INK, ha="left")
fig.text(0.058, 0.912,
         "Fremont, Newark and Union City combined. Bars count listings that "
         "arrived; the line counts homes still sitting there.",
         fontsize=11.5, color=MUTED, ha="left")

# Two short lines, not one long one: the full width version ran under the
# ghosted monogram in the bottom right corner.
fig.text(0.058, 0.043,
         "Zillow Research, for-sale inventory and new listings, both smoothed, "
         "single family and condo, monthly through August 2026.",
         fontsize=9.2, color=MUTED, ha="left")
fig.text(0.058, 0.014,
         "Two different units, so both axes start at zero and only the shapes "
         "are comparable.",
         fontsize=9.2, color=MUTED, ha="left")

fig.subplots_adjust(left=0.072, right=0.928, top=0.855, bottom=0.115)

out = os.path.join(OUTDIR, f"tricity-supply-{STAMP}.png")
save_pair(fig, out, logo=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "hb-logo-mark.png"))

print()
print("Checks:")
print(f"  new listings Jan-Aug   2025 {NEW_25:,}   2026 {NEW_26:,}   "
      f"{pct(NEW_26, NEW_25):+}%")
print(f"  inventory August       2025 {INV_AUG25:,}   2026 {INV_AUG26:,}   "
      f"{pct(INV_AUG26, INV_AUG25):+}%")
print(f"  inventory January      2025 {INV_JAN25:,}   2026 {INV_JAN26:,}   "
      f"{pct(INV_JAN26, INV_JAN25):+}%")
print(f"  peak level             2025 {max(TOT_INV[0:12]):,}   "
      f"2026 {max(TOT_INV[12:20]):,}")
