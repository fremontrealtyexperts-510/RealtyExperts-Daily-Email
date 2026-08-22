#!/usr/bin/env python3
"""
make-walmart-chart.py  [out.png]

REALTY EXPERTS recreation of the "Walmart Stock Is Down 6.8% This Year" graphic
Harv supplied for the 08/21/26 daily email. OUR OWN branded chart: warm cream
ground, coral line with an area fill, the 2025 year end close as a dashed
baseline, and the latest settled close called out.

Story (Market Briefs, 08/21/26): Walmart beat on profit but posted its slowest
sales growth in six years and guided profits lower. The stock fell 9.15% on
August 20. It had used a $2.9B tariff refund to cut prices and win back
shoppers, and inflation may make those discounts short lived.

WHAT WAS VERIFIED:
  * The $111.41 baseline is CORRECT and is the 2025-12-31 close, the proper year
    to date base (the same trap that made the Moderna graphic look wrong on
    08/20: never test a YTD claim against January's first bar).
  * The graphic's $103.84 endpoint is the verified 2026-08-20 close, and
    103.84 / 111.41 - 1 = -6.79%, so its "down 6.8%" was right FOR THAT DAY.

⚠️ THE GRAPHIC WAS ALREADY A DAY STALE. It is captioned "Data through Aug 20,
2026" but this report ships on the evening of Friday 08/21, after the closing
bell. Friday's SETTLED close is $103.70, which puts the year to date at -6.92%.
This chart therefore runs through 08/21 and the title carries -6.9%, not the
-6.8% on the supplied art. Unlike the 08/20 Moderna and Bitcoin charts there is
no dashed "not settled" leg here, because the session is closed and every point
plotted is a real close.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "walmart-082126.png"

DATES = [
    "2025-12-31", "2026-01-02", "2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08",
    "2026-01-09", "2026-01-12", "2026-01-13", "2026-01-14", "2026-01-15", "2026-01-16",
    "2026-01-20", "2026-01-21", "2026-01-22", "2026-01-23", "2026-01-26", "2026-01-27",
    "2026-01-28", "2026-01-29", "2026-01-30", "2026-02-02", "2026-02-03", "2026-02-04",
    "2026-02-05", "2026-02-06", "2026-02-09", "2026-02-10", "2026-02-11", "2026-02-12",
    "2026-02-13", "2026-02-17", "2026-02-18", "2026-02-19", "2026-02-20", "2026-02-23",
    "2026-02-24", "2026-02-25", "2026-02-26", "2026-02-27", "2026-03-02", "2026-03-03",
    "2026-03-04", "2026-03-05", "2026-03-06", "2026-03-09", "2026-03-10", "2026-03-11",
    "2026-03-12", "2026-03-13", "2026-03-16", "2026-03-17", "2026-03-18", "2026-03-19",
    "2026-03-20", "2026-03-23", "2026-03-24", "2026-03-25", "2026-03-26", "2026-03-27",
    "2026-03-30", "2026-03-31", "2026-04-01", "2026-04-02", "2026-04-06", "2026-04-07",
    "2026-04-08", "2026-04-09", "2026-04-10", "2026-04-13", "2026-04-14", "2026-04-15",
    "2026-04-16", "2026-04-17", "2026-04-20", "2026-04-21", "2026-04-22", "2026-04-23",
    "2026-04-24", "2026-04-27", "2026-04-28", "2026-04-29", "2026-04-30", "2026-05-01",
    "2026-05-04", "2026-05-05", "2026-05-06", "2026-05-07", "2026-05-08", "2026-05-11",
    "2026-05-12", "2026-05-13", "2026-05-14", "2026-05-15", "2026-05-18", "2026-05-19",
    "2026-05-20", "2026-05-21", "2026-05-22", "2026-05-26", "2026-05-27", "2026-05-28",
    "2026-05-29", "2026-06-01", "2026-06-02", "2026-06-03", "2026-06-04", "2026-06-05",
    "2026-06-08", "2026-06-09", "2026-06-10", "2026-06-11", "2026-06-12", "2026-06-15",
    "2026-06-16", "2026-06-17", "2026-06-18", "2026-06-22", "2026-06-23", "2026-06-24",
    "2026-06-25", "2026-06-26", "2026-06-29", "2026-06-30", "2026-07-01", "2026-07-02",
    "2026-07-06", "2026-07-07", "2026-07-08", "2026-07-09", "2026-07-10", "2026-07-13",
    "2026-07-14", "2026-07-15", "2026-07-16", "2026-07-17", "2026-07-20", "2026-07-21",
    "2026-07-22", "2026-07-23", "2026-07-24", "2026-07-27", "2026-07-28", "2026-07-29",
    "2026-07-30", "2026-07-31", "2026-08-03", "2026-08-04", "2026-08-05", "2026-08-06",
    "2026-08-07", "2026-08-10", "2026-08-11", "2026-08-12", "2026-08-13", "2026-08-14",
    "2026-08-17", "2026-08-18", "2026-08-19", "2026-08-20", "2026-08-21",
]
CLOSES = [
    111.41, 112.76, 112.71, 114.34, 112.72, 113.07, 114.53, 117.97, 120.36, 120.04,
    119.20, 119.70, 118.71, 119.36, 117.83, 117.73, 117.64, 116.94, 116.57, 117.41,
    119.14, 124.06, 127.71, 128.00, 126.94, 131.18, 129.02, 126.70, 128.77, 133.64,
    133.89, 128.85, 126.62, 124.87, 122.99, 125.81, 126.75, 125.75, 124.42, 127.95,
    127.10, 127.91, 127.81, 123.31, 123.80, 124.34, 125.12, 123.49, 125.33, 126.52,
    125.99, 125.08, 121.98, 121.09, 119.02, 120.72, 122.05, 123.06, 122.18, 122.89,
    123.50, 124.28, 124.74, 125.79, 126.79, 122.49, 127.26, 129.13, 126.77, 124.57,
    125.05, 124.76, 124.82, 127.50, 127.92, 129.60, 129.98, 132.03, 129.92, 127.59,
    127.59, 128.01, 131.93, 131.60, 130.33, 130.79, 130.08, 130.20, 130.43, 127.59,
    130.35, 131.47, 132.46, 131.45, 133.34, 134.20, 130.85, 121.34, 120.27, 118.57,
    118.54, 118.90, 115.75, 114.60, 113.06, 116.89, 117.74, 118.88, 119.83, 118.88,
    120.59, 120.50, 121.04, 120.82, 121.03, 118.13, 117.18, 117.18, 119.42, 119.00,
    115.78, 115.69, 114.60, 113.26, 108.82, 111.84, 110.65, 111.54, 113.10, 112.21,
    113.90, 114.78, 113.70, 112.53, 114.95, 114.24, 112.20, 110.39, 109.33, 108.40,
    109.47, 111.74, 113.10, 114.22, 111.10, 111.20, 110.71, 111.55, 112.34, 112.07,
    111.85, 112.66, 113.26, 116.01, 115.72, 115.27, 114.33, 115.20, 114.30, 103.84,
    103.70,
]

BASE = 111.41          # 2025-12-31 close, the YTD base
LAST = CLOSES[-1]      # 2026-08-21 close
PRIOR = CLOSES[-2]     # 2026-08-20 close, the day of the 9.15% drop

assert abs(BASE - CLOSES[0]) < 0.01, "baseline must be the 2025 year end close"
assert DATES[-1] == "2026-08-21", "series must end at Friday's settled close"

INK    = "#12263f"
CORAL  = "#e2574c"
MUTED  = "#6b7280"
GROUND = "#fdf6e8"
GRID   = "#e7ddc9"
FILL   = "#f6c9c4"

xs = list(range(len(CLOSES)))
ytd = (LAST / BASE - 1) * 100

fig, ax = plt.subplots(figsize=(12.6, 6.8))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.fill_between(xs, BASE, CLOSES, color=FILL, alpha=0.5, zorder=2)
ax.plot(xs, CLOSES, color=CORAL, linewidth=2.4, zorder=3)

ax.axhline(BASE, color=MUTED, linewidth=1.3, linestyle=(0, (6, 5)), zorder=2)
ax.text(3, BASE - 0.9, "Started the year at $111.41", ha="left", va="top",
        fontsize=11.5, fontstyle="italic", color=MUTED, zorder=4)

ax.plot([xs[-1]], [LAST], "o", color=CORAL, markersize=9, zorder=5)
ax.annotate("$%.2f\n%.1f%% YTD" % (LAST, ytd),
            xy=(xs[-1], LAST), xytext=(xs[-1] - 4, LAST - 1.6),
            ha="right", va="top", fontsize=15, fontweight="bold",
            color=CORAL, zorder=5)

# the earnings drop that put it here
drop = len(CLOSES) - 2
ax.annotate("Fell 9.15% on Aug 20\nafter earnings",
            xy=(drop, PRIOR), xytext=(drop - 30, 123.5),
            ha="right", va="center", fontsize=11, color=MUTED, zorder=5,
            arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=1.1,
                            connectionstyle="angle,angleA=0,angleB=90,rad=4"))

ax.set_ylim(96, 138)
ax.set_xlim(-3, len(xs) + 3)
ax.set_yticks([100, 110, 120, 130])
ax.set_yticklabels(["$100", "$110", "$120", "$130"], fontsize=12, color=MUTED)

seen, ticks, labels = set(), [], []
for i, d in enumerate(DATES):
    mo = d[:7]
    if mo not in seen and d >= "2026-01-01":
        seen.add(mo); ticks.append(i)
        labels.append(["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG"][int(d[5:7]) - 1])
ax.set_xticks(ticks)
ax.set_xticklabels(labels, fontsize=12, color=MUTED)

ax.grid(axis="y", color=GRID, linewidth=1.1, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("Walmart Stock Is Down %.1f%% This Year" % abs(ytd), fontsize=25,
             fontweight="bold", color=INK, loc="left", pad=46)
ax.text(0.0, 1.045, "WMT share price, 2025 year end close through August 21, 2026",
        transform=ax.transAxes, fontsize=12.5, fontweight="bold", color=MUTED,
        ha="left")

fig.text(0.012, 0.014, "Source: Yahoo Finance, WMT daily closing prices. "
         "Year to date measured from the December 31, 2025 close of $111.41.",
         fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.075, right=0.985, top=0.80, bottom=0.115)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, "| bars:", len(CLOSES))
print("  base %.2f -> last %.2f = %+.2f%% YTD" % (BASE, LAST, ytd))
print("  Aug 20 close %.2f (graphic used this, -%.2f%% YTD)" % (PRIOR, abs((PRIOR/BASE-1)*100)))
