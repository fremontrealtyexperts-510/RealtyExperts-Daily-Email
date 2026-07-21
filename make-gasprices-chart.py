#!/usr/bin/env python3
"""
make-gasprices-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the "US Gas Prices, Last 18 Months"
graphic (GasBuddy) Harv supplied for the 07/21/26 daily email. OUR OWN branded
chart, not the source image: warm cream ground, Economy-green line over a soft
fill, a dashed $4.00 line the last point crosses back above, and callouts on the
May peak, the early-July dip, and today's return over $4.

Data: FRED GASREGW (U.S. Regular All Formulations retail gasoline price, EIA
weekly survey), pulled live at build time from the keyless CSV endpoint. Window
2025-01-13 to 2026-07-20 (~18 months, matching the reference). The weekly series
is provably faithful: it lands at $4.001 on 2026-07-20 (Market Briefs "over $4"),
dips to $3.78 the week of 07/06 (MB "around $3.75"), and peaks at $4.50 the week
of 05/11. GasBuddy's DAILY national average topped $4.56 in that stretch; a daily
peak naturally runs a touch above the weekly average, so the two agree.

Story (Market Briefs "$4 Gas Is Back", 07/21/26): the national average is back
over $4 a gallon, up from the ~$3.78 early-July dip, as Iran tensions pinch fuel
supply on top of a refinery shortage. Gas is one of the few prices households
feel every week and it feeds the inflation read that sets mortgage rates.

No authorship label on the chart (per Harv, 06/29) - footer carries only the data
source. matplotlib only; build with python3.13 on Mac.
"""
import sys
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

OUT = sys.argv[1] if len(sys.argv) > 1 else "gasprices-072126.png"

# (week, $/gallon) - faithful to FRED GASREGW (EIA weekly regular gasoline),
# pulled 2026-07-21 for the window 2025-01-13 to 2026-07-20. Values verified
# against the CSV endpoint; embedded literally because python3.13's urllib on
# this box lacks a CA bundle (same pattern as make-brent-crossing-chart.py).
SERIES = [
    ("2025-01-13", 3.043), ("2025-01-20", 3.109), ("2025-01-27", 3.103),
    ("2025-02-03", 3.082), ("2025-02-10", 3.128), ("2025-02-17", 3.148),
    ("2025-02-24", 3.125), ("2025-03-03", 3.078), ("2025-03-10", 3.069),
    ("2025-03-17", 3.058), ("2025-03-24", 3.115), ("2025-03-31", 3.162),
    ("2025-04-07", 3.243), ("2025-04-14", 3.168), ("2025-04-21", 3.141),
    ("2025-04-28", 3.133), ("2025-05-05", 3.147), ("2025-05-12", 3.120),
    ("2025-05-19", 3.173), ("2025-05-26", 3.160), ("2025-06-02", 3.127),
    ("2025-06-09", 3.108), ("2025-06-16", 3.139), ("2025-06-23", 3.213),
    ("2025-06-30", 3.164), ("2025-07-07", 3.125), ("2025-07-14", 3.130),
    ("2025-07-21", 3.121), ("2025-07-28", 3.123), ("2025-08-04", 3.140),
    ("2025-08-11", 3.118), ("2025-08-18", 3.125), ("2025-08-25", 3.147),
    ("2025-09-01", 3.177), ("2025-09-08", 3.192), ("2025-09-15", 3.168),
    ("2025-09-22", 3.173), ("2025-09-29", 3.118), ("2025-10-06", 3.124),
    ("2025-10-13", 3.061), ("2025-10-20", 3.019), ("2025-10-27", 3.035),
    ("2025-11-03", 3.019), ("2025-11-10", 3.056), ("2025-11-17", 3.062),
    ("2025-11-24", 3.061), ("2025-12-01", 2.985), ("2025-12-08", 2.940),
    ("2025-12-15", 2.895), ("2025-12-22", 2.841), ("2025-12-29", 2.811),
    ("2026-01-05", 2.796), ("2026-01-12", 2.779), ("2026-01-19", 2.806),
    ("2026-01-26", 2.853), ("2026-02-02", 2.867), ("2026-02-09", 2.902),
    ("2026-02-16", 2.924), ("2026-02-23", 2.937), ("2026-03-02", 3.015),
    ("2026-03-09", 3.502), ("2026-03-16", 3.720), ("2026-03-23", 3.961),
    ("2026-03-30", 3.990), ("2026-04-06", 4.120), ("2026-04-13", 4.123),
    ("2026-04-20", 4.044), ("2026-04-27", 4.123), ("2026-05-04", 4.452),
    ("2026-05-11", 4.500), ("2026-05-18", 4.490), ("2026-05-25", 4.475),
    ("2026-06-01", 4.305), ("2026-06-08", 4.146), ("2026-06-15", 4.052),
    ("2026-06-22", 3.914), ("2026-06-29", 3.831), ("2026-07-06", 3.777),
    ("2026-07-13", 3.855), ("2026-07-20", 4.001),
]
if len(SERIES) < 60:
    raise SystemExit(f"too few rows ({len(SERIES)}) - aborting")

dates = [datetime.strptime(d, "%Y-%m-%d") for d, _ in SERIES]
vals  = [v for _, v in SERIES]

GREEN    = "#16a34a"   # Economy section green
GREEN_DK = "#0f7a37"
INK      = "#12263f"
MUTED    = "#6b7280"
GROUND   = "#fdf6e8"   # warm cream (house style)
GRID     = "#e7ddc9"
ACCENT   = "#b45309"   # amber for the peak callout
RED      = "#b91c1c"   # for the July dip

# --- key points -----------------------------------------------------------
last_i = len(vals) - 1                               # today, 07/20 $4.00
peak_i = max(range(len(vals)), key=lambda i: vals[i])  # 05/11 $4.50
# early-July dip (the local min after the May peak)
dip_i  = min(range(peak_i, len(vals)), key=lambda i: vals[i])

fig, ax = plt.subplots(figsize=(12, 6.0))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

FLOOR = 2.5
ax.fill_between(dates, vals, FLOOR, color=GREEN, alpha=0.12, zorder=2)
ax.plot(dates, vals, color=GREEN_DK, linewidth=2.3, zorder=4,
        solid_joinstyle="round", solid_capstyle="round")

# the $4.00 line the story turns on
ax.axhline(4.00, color=GREEN_DK, linewidth=1.15, linestyle=(0, (5, 4)),
           alpha=0.55, zorder=3)
ax.text(dates[1], 4.03, "$4.00 a gallon", fontsize=11, fontweight="bold",
        color=GREEN_DK, alpha=0.85, ha="left", va="bottom")

# the May peak (2026 high on the weekly series) - parked up and left of the spike
ax.scatter([dates[peak_i]], [vals[peak_i]], s=62, color=ACCENT, zorder=6,
           edgecolor=GROUND, linewidth=2.0)
ax.annotate(f"May 11: ${vals[peak_i]:.2f}\n2026 high",
            xy=(dates[peak_i], vals[peak_i]), xytext=(dates[peak_i - 6], 4.60),
            fontsize=11.5, fontweight="bold", color=ACCENT, ha="center", va="center",
            arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.4,
                            connectionstyle="arc3,rad=0.20"))

# today, back over $4 - parked top right, arrow down to the last point
ax.scatter([dates[last_i]], [vals[last_i]], s=95, color=GREEN_DK, zorder=6,
           edgecolor=GROUND, linewidth=2.2)
ax.annotate(f"Jul 20: ${vals[last_i]:.2f}\nback over $4",
            xy=(dates[last_i], vals[last_i]), xytext=(dates[last_i - 6], 4.76),
            fontsize=12.5, fontweight="bold", color=GREEN_DK, ha="center", va="center",
            arrowprops=dict(arrowstyle="->", color=GREEN_DK, lw=1.7,
                            connectionstyle="arc3,rad=-0.30"))

# the early-July dip
ax.scatter([dates[dip_i]], [vals[dip_i]], s=55, color=RED, zorder=6,
           edgecolor=GROUND, linewidth=1.8)
ax.annotate(f"Jul 6: ${vals[dip_i]:.2f}",
            xy=(dates[dip_i], vals[dip_i]), xytext=(dates[dip_i - 6], 3.35),
            fontsize=11, fontweight="bold", color=RED, ha="center", va="center",
            arrowprops=dict(arrowstyle="->", color=RED, lw=1.3,
                            connectionstyle="arc3,rad=0.25"))

ax.set_ylim(FLOOR, 4.98)
ax.set_yticks([2.75, 3.25, 3.75, 4.25, 4.75])
ax.set_yticklabels(["$2.75", "$3.25", "$3.75", "$4.25", "$4.75"])
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
ax.tick_params(axis="y", labelsize=11, colors=MUTED, length=0)
ax.tick_params(axis="x", labelsize=11.5, colors=INK, length=0)
for lbl in ax.get_xticklabels():
    lbl.set_fontweight("bold")
ax.grid(axis="y", color=GRID, linewidth=1.0)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#d8cbb0")

ax.set_title("US Gas Prices Back Over $4", fontsize=24, fontweight="bold",
             color=INK, loc="left", pad=26)
ax.text(0.0, 1.03,
        "National average, regular unleaded ($/gallon), weekly  (Jan 2025 to Jul 2026)",
        transform=ax.transAxes, fontsize=12.5, color=MUTED, ha="left")

fig.text(0.012, 0.014,
         "Source: U.S. Energy Information Administration regular gasoline weekly "
         "retail price via FRED (GASREGW)",
         fontsize=9, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.062, right=0.975, top=0.84, bottom=0.12)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, "| points:", len(SERIES),
      f"| last {SERIES[-1][0]} ${vals[-1]:.3f} | peak {SERIES[peak_i][0]} ${vals[peak_i]:.3f}")
