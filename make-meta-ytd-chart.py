#!/usr/bin/env python3
"""
make-meta-ytd-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the Meta Platforms year-to-date graphic Harv
supplied for the 07/30/26 daily email. OUR OWN branded chart, not the source
image: warm cream ground, a coral price line with a soft fill, the February peak
and the April low both flagged, and the closing price called out in a pill.

Story tie-in (Market Briefs, 07/30/26): Meta reported earnings and shares dipped
more than 10% at one point in after hours trading after the company said its AI
investments are draining free cash flow. The year to date path lands in the
Stocks section.

Data: Meta Platforms (META) 2026 year-to-date price path, transcribed faithfully
from the Google Finance source graphic Harv provided. Weekly closes through the
July 29, 2026 close of $585.61, down 11.28% ($74.48) from the $660.09 open.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "meta-ytd-073026.png"

# Weekly closes, Jan 2 through Jul 29 2026, transcribed from the source graphic.
PRICES = [
    660.09, 634.0, 608.0, 636.0,          # Jan (early dip, then recovery)
    672.0, 740.0, 690.0, 667.0,           # Feb (spike to the year high, then fade)
    650.0, 633.0, 641.0, 648.0,           # Mar (flat drift)
    638.0, 645.0, 603.0, 580.0,           # Apr (slide begins)
    527.0, 668.0, 694.0, 678.0,           # late Apr low, then the May snapback
    652.0, 613.0, 607.0, 620.0,           # Jun (give back)
    632.0, 572.0, 660.0, 694.0,           # Jul (dip, then the run to the month high)
    585.61,                               # Jul 29 close, post earnings
]
START = PRICES[0]
END = PRICES[-1]
YTD_PCT = -11.28
YTD_DOL = -74.48

PEAK_I = PRICES.index(max(PRICES))   # February high, $740
LOW_I = PRICES.index(min(PRICES))    # late April low, $527

# month boundaries for tick placement (index of the first week of each month)
MONTH_TICKS = [(0, "JAN"), (4, "FEB"), (8, "MAR"), (12, "APR"),
               (16, "MAY"), (20, "JUN"), (24, "JUL")]

CORAL   = "#ef5350"
CORAL_D = "#c62828"
INK     = "#12263f"
MUTED   = "#6b7280"
GROUND  = "#fdf6e8"   # warm cream (house style)
GRID    = "#e7ddc9"

FLOOR = 480           # baseline for the area fill

x = list(range(len(PRICES)))

fig, ax = plt.subplots(figsize=(12, 6.4))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.plot(x, PRICES, color=CORAL, linewidth=2.8, zorder=4, solid_capstyle="round")
ax.fill_between(x, PRICES, FLOOR, color=CORAL, alpha=0.13, zorder=2)

# opening level reference, so the year to date loss reads visually
ax.axhline(START, color="#b9ad93", linewidth=1.4, linestyle=(0, (4, 4)), zorder=3)
ax.text(8.8, START + 6, f"Opened the year at ${START:,.2f}",
        fontsize=11, color="#8a8172", ha="left", zorder=5)

# February peak callout
ax.plot([PEAK_I], [PRICES[PEAK_I]], "o", color=CORAL_D, markersize=7, zorder=5)
ax.annotate(f"Feb high  ${PRICES[PEAK_I]:,.0f}",
            xy=(PEAK_I, PRICES[PEAK_I]), xytext=(PEAK_I - 3.5, PRICES[PEAK_I] + 12),
            fontsize=12, fontweight="bold", color=CORAL_D, zorder=6)

# April low callout
ax.plot([LOW_I], [PRICES[LOW_I]], "o", color=CORAL_D, markersize=7, zorder=5)
ax.annotate(f"Apr low  ${PRICES[LOW_I]:,.0f}",
            xy=(LOW_I, PRICES[LOW_I]), xytext=(LOW_I - 1.6, PRICES[LOW_I] - 26),
            fontsize=12, fontweight="bold", color=CORAL_D, zorder=6)

# closing price pill
ax.plot([x[-1]], [END], "o", color=CORAL_D, markersize=8, zorder=6)
ax.annotate(f"${END:,.2f}", xy=(x[-1], END), xytext=(x[-1] + 0.7, END),
            fontsize=15, fontweight="bold", color="white", va="center",
            zorder=7,
            bbox=dict(boxstyle="round,pad=0.42", facecolor=CORAL_D,
                      edgecolor="none"))

ax.set_xlim(-0.6, len(PRICES) + 3.4)
ax.set_ylim(FLOOR, 790)
ax.set_yticks([500, 550, 600, 650, 700, 750])
ax.set_yticklabels(["500", "550", "600", "650", "700", "750"],
                   fontsize=12, color=MUTED)
ax.set_xticks([i for i, _ in MONTH_TICKS])
ax.set_xticklabels([m for _, m in MONTH_TICKS], fontsize=12.5,
                   fontweight="bold", color=MUTED)
ax.grid(axis="y", color=GRID, linewidth=1.1, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("Meta Is Down 11% In 2026", fontsize=25, fontweight="bold",
             color=INK, loc="left", pad=30)
ax.text(0.0, 1.045, "META share price, year to date",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="left")
ax.text(1.0, 1.045, f"{YTD_PCT:.2f}%  (${YTD_DOL:,.2f})  YEAR TO DATE",
        transform=ax.transAxes, fontsize=14.5, fontweight="bold",
        color=CORAL_D, ha="right")

fig.text(0.012, 0.014, "Source: Google Finance. Close of July 29, 2026.",
         fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.062, right=0.985, top=0.82, bottom=0.085)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT,
      f"| weeks: {len(PRICES)} | start ${START:,.2f} | end ${END:,.2f} | YTD {YTD_PCT:.2f}%")
