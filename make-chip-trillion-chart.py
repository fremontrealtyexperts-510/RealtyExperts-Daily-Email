#!/usr/bin/env python3
"""
make-chip-trillion-chart.py  [outdir]

Recreates the supplied graphic "AMD Joins The $1 Trillion Chip Club" for the
09/22/26 edition. Emits BOTH brand variants:

  chip-trillion-092226.png      plain monogram -> RE email + Agent Hub
  chip-trillion-092226-hb.png   + wordmark     -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/22/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

Market value is computed here, not transcribed: the September 21, 2026 closing
price (Nasdaq historical quotes API) times the shares outstanding on each
company's latest SEC cover page (EDGAR dei:EntityCommonStockSharesOutstanding).
Every input is in DATA below, pulled by script on 09/22/26, never hand typed.

  supplied graphic      computed at the 9/21 close
  Nvidia    $5.4T       $5.48T   (graphic is about the 9/18 close, $5.36T)
  Broadcom  $1.65T      $1.73T   (graphic matches the 9/17 close, $1.66T)
  Micron    $1.2T       $1.18T   right, rounded
  AMD       $1.0T       $1.00T   right: $1.0048T, needs $612.57 a share

So two of the four bars on the supplied graphic were a session or two stale.
Rebuilt on one consistent close for all four.

HEADLINE CLAIM ("every U.S. chipmaker worth $1 trillion or more") HOLDS.
The next largest U.S. chipmaker at the same close is Intel, about $0.61T
(drawn as a hollow "next in line" bar). Qualcomm about $0.20T, Texas
Instruments about $0.25T; Marvell, Analog Devices and the equipment makers
are all far below. TSMC (Taiwan) and Arm (U.K.) are not U.S. companies.

AMD STORY NUMBERS: +9.95% on Monday ($559.82 to $615.52) and +187% this year
from the 2025 final close of $214.16 (YTD base is the PRIOR YEAR'S LAST
CLOSE, per the 08/20 rule). Market Briefs said "around 180%". Its "16th most
valuable public company in the world" was not verified and is not used.

House style: warm cream ground, ranked horizontal bars, coral for the new
member. No company logos (trademarks). matplotlib only; python3.13 on Mac.
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
STAMP = "092226"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8392f"
SLATE = "#5b6b7a"
SAND = "#e9dcc2"
GRID = "#d8cdb8"
MUTED = "#8a8172"

# (name, ticker, close 9/21, close 9/18, shares outstanding, as of, filing)
DATA = [
    ("Nvidia", "NVDA", 227.38, 222.27, 24100000000, "2026-08-21", "10-Q filed 2026-08-26"),
    ("Broadcom", "AVGO", 362.66, 357.61, 4773629865, "2026-08-28", "10-Q filed 2026-09-10"),
    ("Micron", "MU", 1043.96, 1015.8, 1129393151, "2026-06-17", "10-Q filed 2026-06-25"),
    ("AMD", "AMD", 615.52, 559.82, 1632475042, "2026-07-29", "10-Q filed 2026-08-05"),
    ("Intel", "INTC", 121.78, 108.6, 5044000000, "2026-07-17", "10-Q filed 2026-07-24"),
]
AMD_2025_CLOSE = 214.16   # 12/31/2025 close, Nasdaq historical


def tn(close, shares):
    """Market value in trillions, exact decimal arithmetic."""
    return Decimal(str(close)) * Decimal(shares) / Decimal(10 ** 12)


def fmt_t(v):
    return f"${v.quantize(Decimal('0.01'), ROUND_HALF_UP)}T"


rows = [(n, t, tn(c, s), c, p) for n, t, c, p, s, _, _ in DATA]
club = [r for r in rows if r[2] >= 1]
outside = [r for r in rows if r[2] < 1]
club.sort(key=lambda r: r[2], reverse=True)

# Guards: the chart must say what the headline says.
assert [r[1] for r in club] == ["NVDA", "AVGO", "MU", "AMD"], club
assert club[-1][1] == "AMD" and Decimal("1.00") <= club[-1][2] < Decimal("1.01")
assert all(r[2] < Decimal("0.7") for r in outside)
amd = club[-1]
amd_day = (amd[3] / amd[4] - 1) * 100
amd_ytd = (amd[3] / AMD_2025_CLOSE - 1) * 100
assert round(amd_day, 2) == 9.95, amd_day
assert 186 < amd_ytd < 188, amd_ytd

order = club + outside                 # Intel last, as the hollow bar
y = list(range(len(order)))[::-1]

fig, ax = plt.subplots(figsize=(11.6, 6.7))
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

for yi, (name, tick, val, _, _) in zip(y, order):
    v = float(val)
    if tick == "AMD":
        ax.barh(yi, v, height=0.62, color=DEEP, zorder=3)
    elif val < 1:
        ax.barh(yi, v, height=0.62, facecolor=CREAM, edgecolor=MUTED,
                linewidth=1.6, linestyle=(0, (4, 3)), zorder=3)
    else:
        ax.barh(yi, v, height=0.62, color=SLATE, zorder=3)

    label = fmt_t(val)
    color = DEEP if tick == "AMD" else (MUTED if val < 1 else INK)
    # Intel's label lands on the $1T line (first render); a cream box masks
    # the dashes behind it so the figure reads cleanly.
    box = (dict(boxstyle="square,pad=0.18", fc=CREAM, ec="none")
           if val < 1 else None)
    ax.text(v + 0.07, yi, label, va="center", ha="left", bbox=box, zorder=4,
            fontsize=17 if val >= 1 else 13.5, fontweight="bold", color=color)

# Company names in the left margin, as tick labels.
ax.set_yticks(y)
ax.set_yticklabels([r[0] for r in order])
for lab, r in zip(ax.get_yticklabels(), order):
    lab.set_fontweight("bold")
    lab.set_fontsize(15 if r[2] >= 1 else 12.5)
    lab.set_color(DEEP if r[1] == "AMD" else (MUTED if r[2] < 1 else INK))

# The $1 trillion line that defines the club.
ax.axvline(1.0, color=MUTED, lw=1.4, ls=(0, (5, 4)), zorder=2)
ax.text(1.0, y[0] + 0.52, "$1 trillion", ha="center", va="bottom",
        fontsize=11, color=MUTED, fontweight="bold")

# The story, in the empty space right of the short bars.
amd_y = y[order.index(amd)]
ax.text(1.72, amd_y + 0.06,
        f"Newest member. Up {amd_day:.2f}% Monday", fontsize=12.5,
        fontweight="bold", color=INK, ha="left", va="bottom")
ax.text(1.72, amd_y - 0.06,
        f"and about {amd_ytd:.0f}% this year.", fontsize=12.5,
        color=INK, ha="left", va="top")
intel_y = y[-1]
ax.text(float(outside[0][2]) + 0.72, intel_y, "Next largest U.S. chipmaker",
        fontsize=11, color=MUTED, ha="left", va="center")

ax.set_xlim(0, 6.3)
ax.set_ylim(-0.7, len(order) - 0.2)
ax.set_xticks([])
for s in ("top", "right", "bottom"):
    ax.spines[s].set_visible(False)
ax.spines["left"].set_color(GRID)
ax.tick_params(axis="y", length=0, pad=10)

fig.text(0.035, 0.935, "AMD joins the $1 trillion chip club",
         fontsize=22, fontweight="bold", color=INK, ha="left")
fig.text(0.035, 0.888,
         "Market value of every U.S. chipmaker worth $1 trillion or more, "
         "at the September 21, 2026 close.",
         fontsize=11.6, color=MUTED, ha="left")

fig.text(0.035, 0.043,
         "Market value = September 21 closing price (Nasdaq) times shares "
         "outstanding on each company's latest SEC filing.",
         fontsize=9.2, color=MUTED, ha="left")
fig.text(0.035, 0.016,
         "Sources: Nasdaq historical quotes; SEC EDGAR 10-Q cover pages.",
         fontsize=9.2, color=MUTED, ha="left")

fig.subplots_adjust(left=0.13, right=0.975, top=0.83, bottom=0.11)

out = os.path.join(OUTDIR, f"chip-trillion-{STAMP}.png")
save_pair(fig, out, logo=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "hb-logo-mark.png"))

print()
print("Checks:")
for name, tick, val, c, p in order:
    print(f"  {tick:5} {fmt_t(val):>7}  close {c:>9,.2f}  prev {p:>9,.2f}")
print(f"  AMD day {amd_day:+.2f}%  ytd {amd_ytd:+.1f}%  $1T at "
      f"${10**12 / DATA[3][4]:,.2f}")
