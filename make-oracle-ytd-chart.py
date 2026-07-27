#!/usr/bin/env python3
"""
make-oracle-ytd-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the Oracle "Down 41% In 2026" graphic Harv
supplied for the 07/27/26 daily email. OUR OWN branded chart, not the source
image: warm cream ground, a coral price line with a soft fill, the June melt-up
peak flagged, and the closing price called out in a rounded pill.

Story tie-in (Market Briefs, 07/27/26): Oracle landed a roughly $7B, 10-year
Pentagon software contract, which experts read as steady revenue while the
company takes on debt to build AI data centers. The market has been unkind all
the same, so the year-to-date path lands in the Stocks section.

Data: Oracle (ORCL) 2026 year-to-date price path, transcribed faithfully from the
Google Finance source graphic Harv provided. Weekly closes through the July 24,
2026 close of $114.99, a 41.0% year-to-date decline from roughly $195.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "oracle-ytd-072726.png"

# Weekly closes, Jan 2 through Jul 24 2026, transcribed from the source graphic.
PRICES = [
    195.0, 193.0, 190.5, 191.0,          # Jan
    186.0, 172.0, 141.0, 157.5,          # Feb (sharp early-Feb drop, then bounce)
    155.0, 150.0, 163.5, 157.0,          # Mar (mid-month local peak)
    148.0, 141.0, 136.5, 134.5,          # Apr (year low)
    142.0, 155.0, 170.0, 184.0,          # May (rally begins)
    190.0, 194.0, 250.0, 243.0,          # Jun (melt-up to the mid-month peak)
    245.0, 228.0, 221.0, 205.0,          # early Jul
    200.0, 172.0, 140.0, 114.99,         # late Jul collapse into the close
]
END = PRICES[-1]
YTD = -41.00

# month boundaries for tick placement (index of the first week of each month)
MONTH_TICKS = [(0, "JAN"), (4, "FEB"), (8, "MAR"), (12, "APR"),
               (16, "MAY"), (20, "JUN"), (24, "JUL")]

CORAL   = "#ef5350"
CORAL_D = "#c62828"
INK     = "#12263f"
MUTED   = "#6b7280"
GROUND  = "#fdf6e8"   # warm cream (house style)
GRID    = "#e7ddc9"

x = list(range(len(PRICES)))

fig, ax = plt.subplots(figsize=(12, 6.4))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.plot(x, PRICES, color=CORAL, linewidth=2.8, zorder=4, solid_capstyle="round")
ax.fill_between(x, PRICES, 100, color=CORAL, alpha=0.13, zorder=2)

# peak callout
peak_i = PRICES.index(max(PRICES))
ax.plot([peak_i], [PRICES[peak_i]], "o", color=CORAL_D, markersize=7, zorder=5)
ax.annotate(f"June peak  ${PRICES[peak_i]:,.0f}",
            xy=(peak_i, PRICES[peak_i]), xytext=(peak_i - 5.6, PRICES[peak_i] + 6),
            fontsize=12, fontweight="bold", color=CORAL_D, zorder=6)

# closing price pill
ax.plot([x[-1]], [END], "o", color=CORAL_D, markersize=8, zorder=6)
ax.annotate(f"${END:,.2f}", xy=(x[-1], END), xytext=(x[-1] + 0.7, END),
            fontsize=15, fontweight="bold", color="white", va="center",
            zorder=7,
            bbox=dict(boxstyle="round,pad=0.42", facecolor=CORAL_D,
                      edgecolor="none"))

ax.set_xlim(-0.6, len(PRICES) + 3.6)
ax.set_ylim(100, 268)
ax.set_yticks([100, 150, 200, 250])
ax.set_yticklabels(["100", "150", "200", "250"], fontsize=12, color=MUTED)
ax.set_xticks([i for i, _ in MONTH_TICKS])
ax.set_xticklabels([m for _, m in MONTH_TICKS], fontsize=12.5,
                   fontweight="bold", color=MUTED)
ax.grid(axis="y", color=GRID, linewidth=1.1, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("Oracle Is Down 41% In 2026", fontsize=25, fontweight="bold",
             color=INK, loc="left", pad=30)
ax.text(0.0, 1.045, "ORCL share price, year to date",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="left")
ax.text(1.0, 1.045, f"{YTD:.2f}%  YEAR TO DATE",
        transform=ax.transAxes, fontsize=14.5, fontweight="bold",
        color=CORAL_D, ha="right")

fig.text(0.012, 0.014, "Source: Google Finance. Close of July 24, 2026.",
         fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.062, right=0.985, top=0.82, bottom=0.085)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, f"| weeks: {len(PRICES)} | end ${END:,.2f} | YTD {YTD:.2f}%")
