#!/usr/bin/env python3
"""
make-btc-sixday-chart.py  [outdir]

Recreates the supplied graphic "Bitcoin's Six-Day Climb" for the 09/22/26
edition. Emits BOTH brand variants:

  btc-sixday-092226.png      plain monogram -> RE email + Agent Hub
  btc-sixday-092226-hb.png   + wordmark     -> harvrealtor.com / .net / app

NAME CHECK: make-bitcoin-2026-chart.py, make-btc-1month-chart.py and
make-btc-treasury-chart.py already exist; this name was free on 09/22/26.

=============================================================================
VERIFICATION 09/22/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

Series: Coin Metrics community API, asset btc, metric PriceUSD, daily. Coin
Metrics defines PriceUSD as the reference rate at 00:00 UTC the following day,
so each date's value is that UTC day's close. Pulled by script on 09/22/26 and
pasted in below by generator, not hand typed (CM_BTC).

  supplied graphic         Coin Metrics close
  Sept 15  $75,000         $75,650   (rounded on the graphic; the week's low)
  Sept 18  $80,000         $80,944   (rounded on the graphic)
  Sept 21  $85,863         $86,505   (graphic looks like an intraday print)

The supplied graphic drew three points joined by straight lines. The real
path is two jumps, not a ramp: flat near $76K Tuesday to Thursday, +5.97%
Friday, flat near $81K over the weekend, +6.54% Monday. All seven daily
closes are drawn so the shape is honest.

HEADLINE CLAIM "eight-month high" HOLDS, measured on closes: the last close
at or above Monday's $86,505 was January 28, 2026 ($89,178), so Monday is the
highest close since January 28, just under eight months. Drawn as a dashed
reference line.

MARKET BRIEFS CLAIM "nearly 35% jump in three months": June 22 close $63,924
to Monday is +35.3%. Right.

MOVING ENDPOINT (08/20 house pattern): crypto trades 24/7, so Tuesday is not
a close. The line stops at Monday's close; Tuesday is a separate dashed leg
to an open marker, a live CoinGecko price labeled with its time.

No MB pumpkin (their reader game), no MB logo. matplotlib only; python3.13.
"""
import os
import sys
from datetime import date, timedelta

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
SAND = "#e9dcc2"
GRID = "#d8cdb8"
MUTED = "#8a8172"
GREEN = "#2f855a"

# Coin Metrics PriceUSD, daily close (00:00 UTC next day), Dec 25 2025 to Sept 21 2026.
CM_BTC = {
    "2025-12-25": 87231.30, "2025-12-26": 87334.81, "2025-12-27": 87695.42, "2025-12-28": 87747.65,
    "2025-12-29": 87133.51, "2025-12-30": 88428.49, "2025-12-31": 87516.98, "2026-01-01": 88684.22,
    "2026-01-02": 89940.18, "2026-01-03": 90598.13, "2026-01-04": 91359.76, "2026-01-05": 93948.58,
    "2026-01-06": 93574.29, "2026-01-07": 91208.96, "2026-01-08": 91096.92, "2026-01-09": 90539.60,
    "2026-01-10": 90406.14, "2026-01-11": 90717.21, "2026-01-12": 91141.15, "2026-01-13": 95304.50,
    "2026-01-14": 97043.99, "2026-01-15": 95546.14, "2026-01-16": 95489.13, "2026-01-17": 95106.98,
    "2026-01-18": 94261.33, "2026-01-19": 92526.24, "2026-01-20": 88236.56, "2026-01-21": 89599.36,
    "2026-01-22": 89395.70, "2026-01-23": 89439.77, "2026-01-24": 89185.04, "2026-01-25": 86445.67,
    "2026-01-26": 88337.45, "2026-01-27": 89260.38, "2026-01-28": 89177.79, "2026-01-29": 84520.40,
    "2026-01-30": 84017.03, "2026-01-31": 78702.39, "2026-02-01": 76911.05, "2026-02-02": 78716.60,
    "2026-02-03": 75684.77, "2026-02-04": 73095.19, "2026-02-05": 63494.69, "2026-02-06": 70647.70,
    "2026-02-07": 69166.26, "2026-02-08": 70522.59, "2026-02-09": 70244.10, "2026-02-10": 68688.79,
    "2026-02-11": 66989.72, "2026-02-12": 66221.54, "2026-02-13": 68860.84, "2026-02-14": 69798.08,
    "2026-02-15": 68629.96, "2026-02-16": 68747.44, "2026-02-17": 67471.05, "2026-02-18": 66380.71,
    "2026-02-19": 66932.35, "2026-02-20": 67977.31, "2026-02-21": 68020.67, "2026-02-22": 67550.02,
    "2026-02-23": 64689.91, "2026-02-24": 64123.75, "2026-02-25": 68038.52, "2026-02-26": 67519.26,
    "2026-02-27": 65864.14, "2026-02-28": 66965.64, "2026-03-01": 65733.52, "2026-03-02": 68922.62,
    "2026-03-03": 68431.17, "2026-03-04": 72667.46, "2026-03-05": 70987.43, "2026-03-06": 68226.71,
    "2026-03-07": 67315.55, "2026-03-08": 66202.70, "2026-03-09": 68528.54, "2026-03-10": 69891.82,
    "2026-03-11": 70298.58, "2026-03-12": 70538.11, "2026-03-13": 70930.01, "2026-03-14": 71136.22,
    "2026-03-15": 72712.15, "2026-03-16": 74723.96, "2026-03-17": 74086.01, "2026-03-18": 71253.96,
    "2026-03-19": 69948.90, "2026-03-20": 70510.42, "2026-03-21": 69707.29, "2026-03-22": 68018.15,
    "2026-03-23": 70726.21, "2026-03-24": 70610.02, "2026-03-25": 71281.30, "2026-03-26": 68722.97,
    "2026-03-27": 66214.17, "2026-03-28": 66351.07, "2026-03-29": 65966.75, "2026-03-30": 66651.23,
    "2026-03-31": 68214.87, "2026-04-01": 68116.82, "2026-04-02": 66908.32, "2026-04-03": 66891.74,
    "2026-04-04": 67295.13, "2026-04-05": 68921.81, "2026-04-06": 68742.91, "2026-04-07": 72057.12,
    "2026-04-08": 71085.06, "2026-04-09": 71788.68, "2026-04-10": 72945.07, "2026-04-11": 73119.11,
    "2026-04-12": 70685.37, "2026-04-13": 74632.75, "2026-04-14": 74173.51, "2026-04-15": 74761.96,
    "2026-04-16": 75095.74, "2026-04-17": 77114.48, "2026-04-18": 75792.06, "2026-04-19": 73905.20,
    "2026-04-20": 75814.15, "2026-04-21": 76107.44, "2026-04-22": 78317.74, "2026-04-23": 78233.68,
    "2026-04-24": 77444.27, "2026-04-25": 77624.71, "2026-04-26": 78538.77, "2026-04-27": 77256.30,
    "2026-04-28": 76295.53, "2026-04-29": 75795.01, "2026-04-30": 76299.62, "2026-05-01": 78132.64,
    "2026-05-02": 78712.54, "2026-05-03": 78649.17, "2026-05-04": 79826.11, "2026-05-05": 80936.75,
    "2026-05-06": 81364.62, "2026-05-07": 79989.00, "2026-05-08": 80179.69, "2026-05-09": 80663.63,
    "2026-05-10": 82256.78, "2026-05-11": 81714.74, "2026-05-12": 80525.56, "2026-05-13": 79291.91,
    "2026-05-14": 81175.83, "2026-05-15": 79063.41, "2026-05-16": 78164.50, "2026-05-17": 77497.70,
    "2026-05-18": 76975.91, "2026-05-19": 76807.46, "2026-05-20": 77408.17, "2026-05-21": 77595.39,
    "2026-05-22": 75567.54, "2026-05-23": 76619.87, "2026-05-24": 76950.99, "2026-05-25": 77244.57,
    "2026-05-26": 75816.04, "2026-05-27": 74268.78, "2026-05-28": 73500.53, "2026-05-29": 73322.90,
    "2026-05-30": 73731.48, "2026-05-31": 73599.56, "2026-06-01": 71328.73, "2026-06-02": 66540.69,
    "2026-06-03": 64232.58, "2026-06-04": 63639.25, "2026-06-05": 60907.61, "2026-06-06": 60771.61,
    "2026-06-07": 63158.25, "2026-06-08": 63109.62, "2026-06-09": 61640.46, "2026-06-10": 61435.08,
    "2026-06-11": 63475.32, "2026-06-12": 63475.64, "2026-06-13": 64423.54, "2026-06-14": 65615.33,
    "2026-06-15": 66222.59, "2026-06-16": 65638.14, "2026-06-17": 64400.73, "2026-06-18": 62835.22,
    "2026-06-19": 63307.28, "2026-06-20": 64220.54, "2026-06-21": 63365.44, "2026-06-22": 63923.57,
    "2026-06-23": 62593.35, "2026-06-24": 60908.19, "2026-06-25": 59863.42, "2026-06-26": 59961.51,
    "2026-06-27": 59955.57, "2026-06-28": 59516.67, "2026-06-29": 60175.46, "2026-06-30": 58525.08,
    "2026-07-01": 60065.60, "2026-07-02": 61438.19, "2026-07-03": 62564.61, "2026-07-04": 63090.41,
    "2026-07-05": 63619.88, "2026-07-06": 64063.06, "2026-07-07": 63458.12, "2026-07-08": 62214.04,
    "2026-07-09": 63189.39, "2026-07-10": 64118.62, "2026-07-11": 63892.71, "2026-07-12": 63752.27,
    "2026-07-13": 62126.53, "2026-07-14": 64934.44, "2026-07-15": 64765.06, "2026-07-16": 63780.14,
    "2026-07-17": 63915.92, "2026-07-18": 64777.66, "2026-07-19": 64653.05, "2026-07-20": 65181.92,
    "2026-07-21": 66403.10, "2026-07-22": 65983.19, "2026-07-23": 65094.41, "2026-07-24": 64100.11,
    "2026-07-25": 64331.33, "2026-07-26": 65328.79, "2026-07-27": 63718.24, "2026-07-28": 63728.45,
    "2026-07-29": 63904.64, "2026-07-30": 64827.57, "2026-07-31": 62875.18, "2026-08-01": 62751.88,
    "2026-08-02": 63445.68, "2026-08-03": 63460.05, "2026-08-04": 64161.47, "2026-08-05": 64610.31,
    "2026-08-06": 64212.27, "2026-08-07": 64869.17, "2026-08-08": 64906.96, "2026-08-09": 64864.93,
    "2026-08-10": 63907.75, "2026-08-11": 63547.44, "2026-08-12": 63359.40, "2026-08-13": 63395.01,
    "2026-08-14": 62924.70, "2026-08-15": 63034.43, "2026-08-16": 62818.41, "2026-08-17": 64434.14,
    "2026-08-18": 64696.18, "2026-08-19": 69267.83, "2026-08-20": 73070.93, "2026-08-21": 78359.17,
    "2026-08-22": 77020.13, "2026-08-23": 77593.03, "2026-08-24": 78894.50, "2026-08-25": 78601.40,
    "2026-08-26": 78955.04, "2026-08-27": 80297.40, "2026-08-28": 77716.59, "2026-08-29": 78243.93,
    "2026-08-30": 77689.19, "2026-08-31": 78533.89, "2026-09-01": 77407.70, "2026-09-02": 77188.70,
    "2026-09-03": 81243.24, "2026-09-04": 79681.56, "2026-09-05": 79817.32, "2026-09-06": 80319.97,
    "2026-09-07": 79073.02, "2026-09-08": 78445.68, "2026-09-09": 78207.48, "2026-09-10": 76675.77,
    "2026-09-11": 77176.82, "2026-09-12": 77252.41, "2026-09-13": 76759.26, "2026-09-14": 78278.79,
    "2026-09-15": 75650.43, "2026-09-16": 76082.38, "2026-09-17": 76386.90, "2026-09-18": 80944.16,
    "2026-09-19": 81262.35, "2026-09-20": 81194.74, "2026-09-21": 86505.30,
}

# Tuesday 09/22 live print, CoinGecko simple/price. NOT a close.
LIVE = 86428
LIVE_TIME = "8:43 AM PT"

START, END = date(2026, 9, 15), date(2026, 9, 21)
days = [START + timedelta(n) for n in range((END - START).days + 1)]
vals = [CM_BTC[d.isoformat()] for d in days]

# Guards: the series must end at the last complete UTC day, and the claims
# on the chart must be true of the data.
assert max(CM_BTC) == END.isoformat(), "series must end at Monday's close"
low = min(vals)
assert vals[0] == low, "Sept 15 must be the low of the window"
higher = [d for d, v in CM_BTC.items() if d < END.isoformat() and v >= vals[-1]]
LAST_HIGHER = max(higher)
assert LAST_HIGHER == "2026-01-28", LAST_HIGHER
REF = CM_BTC[LAST_HIGHER]
six_day = (vals[-1] / vals[0] - 1) * 100
fri = (vals[3] / vals[2] - 1) * 100
mon = (vals[6] / vals[5] - 1) * 100
three_mo = (vals[-1] / CM_BTC["2026-06-22"] - 1) * 100
assert 14 < six_day < 15 and 5.5 < fri < 6.5 and 6 < mon < 7, (six_day, fri, mon)
assert 34.5 < three_mo < 36, three_mo

fig, ax = plt.subplots(figsize=(11.6, 6.7))
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)
ax.grid(axis="y", color=GRID, lw=0.7, alpha=0.75)
ax.set_axisbelow(True)

x = list(range(len(days)))
YLO, YHI = 72500, 91500
ax.fill_between(x, vals, YLO, color=SAND, alpha=0.55, lw=0, zorder=1)
ax.plot(x, vals, color=CORAL, lw=3.4, zorder=4, solid_capstyle="round")
for xi, v in zip(x, vals):
    ax.plot(xi, v, "o", ms=7.5, mfc=CREAM, mec=CORAL, mew=2.2, zorder=5)
ax.plot(x[-1], vals[-1], "o", ms=12, mfc=DEEP, mec=CREAM, mew=2.2, zorder=6)

# Tuesday live leg, dashed, open marker.
xl = len(days)
ax.plot([x[-1], xl], [vals[-1], LIVE], color=CORAL, lw=2.2,
        ls=(0, (4, 3)), zorder=3)
ax.plot(xl, LIVE, "o", ms=10, mfc=CREAM, mec=DEEP, mew=2.2, zorder=6)
ax.annotate(f"${LIVE:,.0f}", (xl, LIVE), xytext=(0, -20),
            textcoords="offset points", ha="center", va="top",
            fontsize=12.5, fontweight="bold", color=DEEP)
ax.annotate(f"live {LIVE_TIME},\nnot a close", (xl, LIVE), xytext=(0, -40),
            textcoords="offset points", ha="center", va="top",
            fontsize=9.8, color=MUTED, linespacing=1.15)

# Point labels.
ax.annotate(f"${vals[0]:,.0f}", (x[0], vals[0]), xytext=(0, -20),
            textcoords="offset points", ha="center", va="top",
            fontsize=15, fontweight="bold", color=INK)
ax.annotate("last week's low", (x[0], vals[0]), xytext=(0, -40),
            textcoords="offset points", ha="center", va="top",
            fontsize=10.5, color=MUTED)
ax.annotate(f"${vals[3]:,.0f}", (x[3], vals[3]), xytext=(-8, 14),
            textcoords="offset points", ha="right", va="bottom",
            fontsize=15, fontweight="bold", color=INK)
ax.annotate(f"${vals[6]:,.0f}", (x[6], vals[6]), xytext=(-14, 12),
            textcoords="offset points", ha="right", va="bottom",
            fontsize=20, fontweight="bold", color=DEEP)

# The two jumps that make the climb. Both labels sit below and right of
# their segment; at the segment midpoint the first render put the Friday
# label on the line.
for x0, y0, y1, pct, day in ((2, vals[2], vals[3], fri, "Friday"),
                             (5, vals[5], vals[6], mon, "Monday")):
    xt = x0 + 0.62
    line_at = y0 + (y1 - y0) * 0.62
    yt = (y0 + y1) / 2 - 900
    assert line_at - yt > 1100, (day, line_at, yt)   # clear of the line
    ax.text(xt, yt, f"+{pct:.1f}%\n{day}", ha="left", va="center",
            fontsize=11.5, fontweight="bold", color=GREEN, linespacing=1.1)

# What "eight-month high" is measured against.
ax.axhline(REF, color=MUTED, lw=1.3, ls=(0, (5, 4)), zorder=2)
ax.text(-0.15, REF + 350,
        f"January 28 close, ${REF:,.0f}: the last time Bitcoin closed higher",
        ha="left", va="bottom", fontsize=10.8, color=MUTED, fontweight="bold")

labels = [d.strftime("%a\n%b %-d") for d in days] + ["Tue\nSep 22"]
ax.set_xticks(list(range(len(days) + 1)))
ax.set_xticklabels(labels)
ax.set_xlim(-0.45, len(days) + 0.45)
ax.set_ylim(YLO, YHI)
yt = [75000, 80000, 85000, 90000]
ax.set_yticks(yt)
ax.set_yticklabels([f"${v // 1000}K" for v in yt])

for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_color(GRID)
ax.tick_params(axis="both", colors=MUTED, labelsize=11, length=0)
for t in ax.get_xticklabels() + ax.get_yticklabels():
    t.set_color(INK)
for t in ax.get_xticklabels():
    t.set_fontweight("bold")
ax.get_xticklabels()[-1].set_color(MUTED)

fig.text(0.062, 0.935, "Bitcoin's six-day climb", fontsize=22,
         fontweight="bold", color=INK, ha="left")
fig.text(0.062, 0.888,
         f"Daily close, September 15 to 21, 2026. Up {six_day:.1f}% from last "
         "week's low to Monday, the highest close since January 28.",
         fontsize=11.4, color=MUTED, ha="left")

fig.text(0.062, 0.043,
         "Source: Coin Metrics reference rate, daily close at 00:00 UTC. "
         "Tuesday's point is a live CoinGecko price, not a close.",
         fontsize=9.2, color=MUTED, ha="left")

fig.subplots_adjust(left=0.085, right=0.975, top=0.84, bottom=0.15)

out = os.path.join(OUTDIR, f"btc-sixday-{STAMP}.png")
save_pair(fig, out, logo=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "hb-logo-mark.png"))

print()
print("Checks:")
for d, v in zip(days, vals):
    print(f"  {d.isoformat()} {d.strftime('%a')}  ${v:,.2f}")
print(f"  six day {six_day:+.2f}%  Fri {fri:+.2f}%  Mon {mon:+.2f}%  "
      f"3 month {three_mo:+.1f}%  last higher {LAST_HIGHER} ${REF:,.0f}")
print(f"  live {LIVE_TIME} ${LIVE:,}  vs Monday close {(LIVE / vals[-1] - 1) * 100:+.2f}%")
