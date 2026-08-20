#!/usr/bin/env python3
"""
make-btc-1month-chart.py  [out.png]

REALTY EXPERTS recreation of the "Bitcoin Rips to a One-Month High" graphic Harv
supplied for the 08/20/26 daily email. OUR OWN branded chart: warm cream ground,
coral line with an area fill, the prior one month high as a dashed reference.

⚠️ NAME CHECK: make-bitcoin-2026-chart.py ALREADY EXISTS in this repo from an
earlier run. This file is deliberately named differently so it cannot clobber it
(see the 08/18 make-gdp-chart.py incident).

Data: VERIFIED against Yahoo Finance BTC-USD daily closes, not traced off the
supplied graphic. The supplied version was built on TradingView and printed
$69,661 with a one day gain of 7.48%, or $4,847. Yahoo's completed UTC daily bar
for the same session is $69,266, a gain of 7.09% over the $64,681 close on
08/18. The roughly $400 gap is a normal aggregation difference between crypto
data providers, not an error in either. Our numbers are Yahoo throughout so the
series and the percentages sit on one basis.

⚠️ THE SUPPLIED HEADLINE WAS ALREADY STALE WHEN THIS WAS BUILT. The graphic is
captioned "1 month through Aug 20, 2026" but its value is Wednesday's level. By
midday Thursday 08/20 Bitcoin had run FURTHER, to about $72,781, which is a new
and higher one month high. Crypto trades 24/7, so the 08/20 bar is still in
progress: it is NOT drawn as a completed daily close. It is a separate dashed
leg to an open marker, labeled as midday and in progress, the same treatment
given the Moderna chart the same morning.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "btc-082026.png"

# Yahoo Finance BTC-USD daily closes, completed UTC days only.
DATES = [
    "2026-07-20", "2026-07-21", "2026-07-22", "2026-07-23", "2026-07-24", "2026-07-25",
    "2026-07-26", "2026-07-27", "2026-07-28", "2026-07-29", "2026-07-30", "2026-07-31",
    "2026-08-01", "2026-08-02", "2026-08-03", "2026-08-04", "2026-08-05", "2026-08-06",
    "2026-08-07", "2026-08-08", "2026-08-09", "2026-08-10", "2026-08-11", "2026-08-12",
    "2026-08-13", "2026-08-14", "2026-08-15", "2026-08-16", "2026-08-17", "2026-08-18",
    "2026-08-19",
]
CLOSES = [
    65230, 66505, 66101, 65045, 64098, 64312, 65340, 63725,
    63871, 63908, 64725, 62814, 62763, 63482, 63461, 64056,
    64598, 64262, 64880, 64905, 64845, 63911, 63552, 63402,
    63402, 62976, 63024, 62819, 64506, 64681, 69266,
]

LAST = CLOSES[-1]      # 2026-08-19, last completed daily bar
PREV = CLOSES[-2]      # 2026-08-18
LIVE = 72781           # 2026-08-20 midday, day still in progress
PRIOR_HIGH = max(CLOSES[:-1])

assert DATES[-1] == "2026-08-19", "series must end at the last completed bar"
assert LAST > PRIOR_HIGH, "the 08/19 close should be the one month high"

INK    = "#12263f"
CORAL  = "#e2574c"
MUTED  = "#6b7280"
GROUND = "#fdf6e8"
GRID   = "#e7ddc9"
FILL   = "#f6c9c4"

xs = list(range(len(CLOSES)))
floor = 60000

fig, ax = plt.subplots(figsize=(12.6, 6.8))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.fill_between(xs, floor, CLOSES, color=FILL, alpha=0.55, zorder=2)
ax.plot(xs, CLOSES, color=CORAL, linewidth=2.4, zorder=3)

# the high it had to clear
ax.axhline(PRIOR_HIGH, color=MUTED, linewidth=1.3, linestyle=(0, (6, 5)), zorder=2)
ax.text(0.4, PRIOR_HIGH + 260, "Previous one month high  $%s" % f"{PRIOR_HIGH:,}",
        ha="left", va="bottom", fontsize=11, fontstyle="italic", color=MUTED, zorder=4)

ax.plot([xs[-1]], [LAST], "o", color=CORAL, markersize=9, zorder=5)
ax.annotate("$%s\nAug 19 close, +7.1%% on the day" % f"{LAST:,}",
            xy=(xs[-1], LAST), xytext=(xs[-1] - 1.1, LAST + 900),
            ha="right", va="bottom", fontsize=14, fontweight="bold",
            color=CORAL, zorder=5)

# it kept going while this was built
ax.plot([xs[-1], xs[-1] + 1.6], [LAST, LIVE], color=MUTED, linewidth=1.8,
        linestyle=(0, (4, 3)), zorder=4)
ax.plot([xs[-1] + 1.6], [LIVE], "o", markersize=9, zorder=5,
        markerfacecolor=GROUND, markeredgecolor=MUTED, markeredgewidth=1.8)
ax.annotate("Aug 20 midday\n$%s, still moving" % f"{LIVE:,}",
            xy=(xs[-1] + 1.6, LIVE), xytext=(xs[-1] + 2.4, LIVE + 150),
            ha="left", va="center", fontsize=11, color=MUTED, zorder=5)

ax.set_xlim(-1, len(xs) + 9)
ax.set_ylim(floor, 76000)
ax.set_yticks([62000, 65000, 68000, 71000, 74000])
ax.set_yticklabels(["$62K", "$65K", "$68K", "$71K", "$74K"], fontsize=12, color=MUTED)

ticks = [i for i, d in enumerate(DATES) if d in
         ("2026-07-20", "2026-07-27", "2026-08-03", "2026-08-10", "2026-08-17")]
ax.set_xticks(ticks)
ax.set_xticklabels(["Jul 20", "Jul 27", "Aug 3", "Aug 10", "Aug 17"],
                   fontsize=12, color=MUTED)

ax.grid(axis="y", color=GRID, linewidth=1.1, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("Bitcoin Rips to a One-Month High", fontsize=25, fontweight="bold",
             color=INK, loc="left", pad=46)
ax.text(0.0, 1.045, "BTC/USD daily closes, July 20 to August 19, 2026",
        transform=ax.transAxes, fontsize=12.5, fontweight="bold", color=MUTED,
        ha="left")

fig.text(0.012, 0.014, "Source: Yahoo Finance, BTC-USD daily closing prices "
         "(completed UTC days).", fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.078, right=0.985, top=0.80, bottom=0.115)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, "| bars:", len(CLOSES))
print("  one month %s -> %s = %+.2f%%" % (CLOSES[0], LAST, (LAST / CLOSES[0] - 1) * 100))
print("  one day   %s -> %s = %+.2f%%" % (PREV, LAST, (LAST / PREV - 1) * 100))
print("  prior 1mo high %s | live 08/20 %s (NOT a completed bar)" % (PRIOR_HIGH, LIVE))
