#!/usr/bin/env python3
"""
make-meta-capex-chart.py  DATA_DIR  [outdir]

Meta's capital spending by year, recreated for the 09/28/26 daily from Harv's
supplied "Meta's AI Bill Keeps Climbing" graphic (2025 $70B, then 2026 to 2028
"estimates" of $140B, $197B and $215B, source "Bloomberg, company filings and
analyst estimates").

  meta-capex-092826.png      plain monogram -> RE email + Agent Hub
  meta-capex-092826-hb.png   + wordmark     -> harvrealtor.com / .net / app

=============================================================================
WHAT CHANGED FROM THE SUPPLIED GRAPHIC, AND WHY
=============================================================================

1. ONE DEFINITION. Meta reports and guides "capital expenditures, including
   principal payments on finance leases". The graphic's $70B for 2025 is the
   narrower cash flow line, purchases of property and equipment ($69.691B).
   On Meta's own definition 2025 was $72.22B, which is the basis its 2026
   guidance uses, so every bar here is on that one basis.
2. 2026 IS META'S OWN RANGE, not a point estimate: $130B to $145B, from the
   July 29, 2026 earnings release (narrowed from $125B to $145B in April,
   raised from $115B to $135B in January). The first half actually spent,
   Q1 $19.84B + Q2 $31.08B, is drawn solid inside it.
3. 2027 AND 2028 ARE DROPPED. They are sell side consensus figures from a
   Bloomberg terminal, which cannot be checked at a primary source, and the
   published estimates for 2027 disagree with each other by tens of billions
   depending on the date and the compiler. Meta has not guided past 2026.
   (feedback-verify-supplied-chart-values-before-recreating: drop any bar you
   cannot source.)

DATA_DIR must hold, fetched with shell curl on 09/28/26 (python3.13 cannot
reach SEC over SSL on this Mac):
  meta-capex.json     data.sec.gov companyconcept us-gaap
                      PaymentsToAcquirePropertyPlantAndEquipment, CIK 1326801
  meta-finlease.json  same for FinanceLeasePrincipalPayments
  meta-q4.txt, meta-q1.txt, meta-q2.txt  text of the Exhibit 99.1 earnings
                      releases filed 01/28, 04/29 and 07/29/26
Every number on the chart is parsed from those files at build time.

matplotlib only; build with python3.13 on Mac.
"""
import json
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "092826"
LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hb-logo-mark.png")

CREAM = "#fdf6e8"
INK = "#1f2933"
GRID = "#d8cdb8"
MUTED = "#8a8172"
BLUE = "#2f6f9f"
BLUE_LIGHT = "#b9d0e3"


def fy(path):
    d = json.load(open(os.path.join(DATA, path)))
    out = {}
    for u in sorted(d["units"]["USD"], key=lambda u: u["filed"]):
        if u.get("fp") == "FY" and u["form"] == "10-K" and u["start"][5:] == "01-01" \
                and u["end"][5:] == "12-31" and u["end"][:4] == u["start"][:4]:
            out[int(u["end"][:4])] = u["val"]   # later filings overwrite: newest vintage wins
    return out


ppe, lease = fy("meta-capex.json"), fy("meta-finlease.json")
YEARS = [2023, 2024, 2025]
ACTUAL = {y: (ppe[y] + lease[y]) / 1e9 for y in YEARS}


def text(q):
    return open(os.path.join(DATA, f"meta-{q}.txt")).read()


def guide(q):
    m = re.search(r"capital expenditures, including principal payments on finance leases, "
                  r"to be in the range of \$(\d+)-(\d+) billion", text(q))
    return int(m.group(1)), int(m.group(2))


def quarter(q):
    m = re.search(r"Capital expenditures, including principal payments on finance leases, "
                  r"were \$([\d.]+) billion", text(q))
    return float(m.group(1))


LO, HI = guide("q2")
H1 = quarter("q1") + quarter("q2")
# Meta's own printed full year 2025 figure must equal the sum we built.
fy25 = re.search(r"were \$[\d.]+ billion and \$([\d.]+) billion for the fourth quarter and full "
                 r"year 2025", text("q4"))
assert abs(float(fy25.group(1)) - ACTUAL[2025]) < 0.01, (fy25.group(1), ACTUAL[2025])
assert (LO, HI) == (130, 145), (LO, HI)


def b(x):
    return f"${Decimal(str(x)).quantize(Decimal('0.1'), ROUND_HALF_UP)}B"


fig, ax = plt.subplots(figsize=(11.6, 7.2))
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)
ax.grid(axis="y", color=GRID, lw=0.7, alpha=0.7)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(colors=MUTED, labelsize=10, length=0)

W = 0.62
xs = list(range(len(YEARS) + 1))
for x, y in zip(xs, YEARS):
    ax.bar(x, ACTUAL[y], width=W, color=BLUE, edgecolor=CREAM, linewidth=2, zorder=3)
    ax.text(x, ACTUAL[y] + 3.5, b(ACTUAL[y]), ha="center", va="bottom", fontsize=15,
            fontweight="bold", color=INK)

# 2026: the guided range as a light band, the first half actually spent as solid.
x6 = xs[-1]
ax.add_patch(Rectangle((x6 - W / 2, 0), W, HI, facecolor=BLUE_LIGHT, edgecolor="none",
                       alpha=0.55, zorder=2))
ax.add_patch(Rectangle((x6 - W / 2, LO), W, HI - LO, facecolor="none", edgecolor=BLUE,
                       lw=1.6, ls=(0, (4, 3)), zorder=4))
ax.bar(x6, H1, width=W, color=BLUE, edgecolor=CREAM, linewidth=2, zorder=3)
ax.text(x6, HI + 3.5, f"\\${LO}B to \\${HI}B", ha="center", va="bottom", fontsize=15,
        fontweight="bold", color=INK)
ax.text(x6, HI + 15.5, "Meta's guidance", ha="center", va="bottom", fontsize=10.5,
        color=MUTED)
ax.text(x6, H1 / 2, f"{b(H1)}\nspent\nJan to Jun", ha="center", va="center",
        fontsize=10.5, color=CREAM, fontweight="bold", linespacing=1.25, zorder=5)

up25 = (ACTUAL[2025] / ACTUAL[2024] - 1) * 100
lo26 = (LO / ACTUAL[2025] - 1) * 100
hi26 = (HI / ACTUAL[2025] - 1) * 100
q = lambda v: Decimal(str(v)).quantize(Decimal("1"), ROUND_HALF_UP)
ax.text(xs[2], ACTUAL[2025] + 14, f"up {q(up25)}% on 2024", ha="center", va="bottom",
        fontsize=10.5, color=MUTED)
ax.text(x6, (H1 + LO) / 2 + 6, f"up {q(lo26)}% to {q(hi26)}%\non 2025", ha="center",
        va="center", fontsize=11, color=BLUE, fontweight="bold", linespacing=1.3, zorder=5)

ax.set_xticks(xs)
ax.set_xticklabels([str(y) for y in YEARS] + ["2026"], fontsize=13, fontweight="bold")
for t in ax.get_xticklabels():
    t.set_color(INK)
ax.set_ylim(0, 185)
ax.set_xlim(-0.6, len(xs) - 0.4)
ax.set_yticks([0, 50, 100, 150])
ax.set_yticklabels(["$0", "$50B", "$100B", "$150B"], fontsize=10)
for t in ax.get_yticklabels():
    t.set_color(MUTED)

fig.text(0.062, 0.955, "Meta's AI bill keeps climbing", fontsize=21, fontweight="bold",
         color=INK, ha="left")
fig.text(0.062, 0.913,
         "Capital spending each year, including finance lease payments. 2026 is Meta's own range.",
         fontsize=11.4, color=MUTED, ha="left")
fig.text(0.062, 0.035,
         "Source: Meta Platforms Form 10-K for 2025 and earnings releases of January 28, April 29 and July 29, 2026.\n"
         "Analyst estimates for 2027 and 2028 are not shown; Meta has not guided past 2026.",
         fontsize=9.0, color=MUTED, ha="left", linespacing=1.45)
fig.subplots_adjust(left=0.075, right=0.975, top=0.86, bottom=0.14)
save_pair(fig, os.path.join(OUTDIR, f"meta-capex-{STAMP}.png"), logo=LOGO)

print("\nChecks:")
for y in YEARS:
    print(f"  {y}: PP&E {ppe[y]/1e9:.3f} + finance lease {lease[y]/1e9:.3f} = {ACTUAL[y]:.3f}")
print(f"  2026 guidance ${LO}B to ${HI}B; H1 spent {H1:.2f}")
print(f"  2025 vs 2024 up {up25:.1f}%; 2026 range vs 2025 up {lo26:.1f}% to {hi26:.1f}%")
