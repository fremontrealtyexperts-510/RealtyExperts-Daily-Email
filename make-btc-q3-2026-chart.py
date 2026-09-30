#!/usr/bin/env python3
"""
make-btc-q3-2026-chart.py  COINMETRICS_JSON  LIVE_JSON  [outdir]

Recreates the supplied graphic "Bitcoin's Best Quarter Since 2024" for the
09/30/26 edition. Emits BOTH brand variants:

  btc-quarter-093026.png      plain monogram -> RE email + Agent Hub
  btc-quarter-093026-hb.png   + wordmark     -> harvrealtor.com / .net / app

NAME CHECK: make-bitcoin-2026-chart.py, make-btc-1month-chart.py,
make-btc-sixday-chart.py and make-btc-treasury-chart.py already exist; this
name was free on 09/30/26.

INPUTS (nothing is hand typed, every number is computed from the files):
  COINMETRICS_JSON  the Coin Metrics community API response, pulled with curl:
      https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=btc
        &metrics=PriceUSD&frequency=1d&start_time=2023-12-25&page_size=10000
      PriceUSD is the reference rate at 00:00 UTC the following day, so each
      date's value is that UTC day's close (5:00 PM PT).
  LIVE_JSON         {"price": 83507.61, "time_pt": "7:45 AM PT", "source": "Coinbase"}

=============================================================================
VERIFICATION 09/30/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

  supplied graphic             Coin Metrics close     Coinbase close
  Jun 30   about $58.5K        $58,525                $58,524
  Jul 31   about $63K          $62,875                $62,826
  Aug 31   about $78.5K        $78,534                $78,563
  "peak"   about $84.7K        $86,505 (Sept 21)      $86,595   <- graphic is low
  Sep 29   $82,985             $83,675                $83,638   <- an intraday print

The supplied graphic joined five points; its September high sits about $1,800
under the real one, and its last point is a Tuesday intraday price, not the
close. All 92 daily closes are drawn here.

TITLE CLAIM "best quarter since 2024" HOLDS and is drawn, not asserted: the
right panel shows every quarter back to Q4 2024 (+47.6%), the last better one.
It is true whether tonight's close lands above or below that, because Q4 2024
and Q1 2024 are both in 2024.

THE HALF THE GRAPHIC LEFT OUT: the quarter follows three straight losing
quarters, so Tuesday's close is still about a third below the October 2025
record close and below where 2026 began. Both are printed on the chart.

MOVING ENDPOINT (08/20 house pattern): the quarter ends at 00:00 UTC October 1,
5:00 PM PT on 09/30, so the line stops at Tuesday's close, the last settled
day. The live price goes in the footer with its time; a dashed live leg is
drawn only when the live price is 1% or more away from that close.

matplotlib only; build with python3.13 on Mac.
"""
import json
import os
import sys
from datetime import date, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

SRC, LIVE_SRC = sys.argv[1], sys.argv[2]
OUTDIR = sys.argv[3] if len(sys.argv) > 3 else "."
STAMP = "093026"

CREAM = "#fdf6e8"
INK = "#1f2933"
ORANGE = "#cc7410"
DEEP = "#9a5508"
SLATE = "#6f8296"
PALE = "#a7b3c0"
SAND = "#f1dfbf"
GRID = "#d8cdb8"
MUTED = "#8a8172"

MINUS = "−"


def load():
    rows = json.load(open(SRC))["data"]
    px = {r["time"][:10]: float(r["PriceUSD"]) for r in rows}
    assert len(px) > 900, len(px)
    return px


def pct(a, b):
    return (b / a - 1) * 100


def signed(v, nd=1):
    return f"+{v:.{nd}f}%" if v >= 0 else f"{MINUS}{abs(v):.{nd}f}%"


px = load()
live = json.load(open(LIVE_SRC))

Q_START, Q_LAST = date(2026, 6, 30), date(2026, 9, 29)
assert max(px) == Q_LAST.isoformat(), f"series must end at Tuesday's close, got {max(px)}"
days = [Q_START + timedelta(n) for n in range((Q_LAST - Q_START).days + 1)]
vals = [px[d.isoformat()] for d in days]
assert len(vals) == 92

# Quarter ends (UTC day closes) back to the end of Q3 2024.
ENDS = ["2024-09-30", "2024-12-31", "2025-03-31", "2025-06-30", "2025-09-30",
        "2025-12-31", "2026-03-31", "2026-06-30"]
NAMES = ["Q4\n2024", "Q1\n2025", "Q2\n2025", "Q3\n2025", "Q4\n2025", "Q1\n2026", "Q2\n2026", "Q3\n2026"]
qret = [pct(px[ENDS[i]], px[ENDS[i + 1]]) for i in range(len(ENDS) - 1)]
q3 = pct(px["2026-06-30"], vals[-1])
qret.append(q3)

# The claims printed on the chart must be true of the data.
assert 42.5 < q3 < 43.5, q3
assert qret[0] > q3 > max(qret[1:-1]), qret            # best since Q4 2024, and Q4 2024 was better
assert all(v < 0 for v in qret[4:7]), qret[4:7]         # three straight losing quarters
peak_i = max(range(len(vals)), key=lambda i: vals[i])
assert days[peak_i] == date(2026, 9, 21), days[peak_i]
ath_day = max(px, key=px.get)
assert ath_day == "2025-10-06", ath_day
from_ath = pct(px[ath_day], vals[-1])
ytd = pct(px["2025-12-31"], vals[-1])
assert -34 < from_ath < -32 and -5 < ytd < -4, (from_ath, ytd)
jul = pct(px["2026-06-30"], px["2026-07-31"])
aug = pct(px["2026-07-31"], px["2026-08-31"])
sep = pct(px["2026-08-31"], vals[-1])
live_gap = pct(vals[-1], live["price"])

fig = plt.figure(figsize=(12.8, 7.6), dpi=100)
fig.patch.set_facecolor(CREAM)

# ---------------------------------------------------------------- left: price
ax = fig.add_axes((0.070, 0.235, 0.530, 0.555))
ax.set_facecolor(CREAM)
x = list(range(len(days)))
YLO, YHI = 52000, 93000
ax.grid(axis="y", color=GRID, lw=0.7, alpha=0.75)
ax.set_axisbelow(True)
ax.fill_between(x, vals, YLO, color=SAND, alpha=0.60, lw=0, zorder=1)
ax.plot(x, vals, color=ORANGE, lw=2.8, zorder=4, solid_capstyle="round", solid_joinstyle="round")

# Month boundaries and what each month contributed.
bounds = [0, 31, 62, 91]          # Jun 30, Jul 31, Aug 31, Sep 29
for b in bounds[1:3]:
    ax.plot([b, b], [YLO, vals[b]], color=GRID, lw=1.0, zorder=2)
for (a, b), label in zip(zip(bounds[:-1], bounds[1:]),
                         (f"July {signed(jul)}", f"August {signed(aug)}", f"September {signed(sep)}")):
    ax.text((a + b) / 2, YLO + 1050, label, ha="center", va="bottom", fontsize=11.5,
            color=INK, fontweight="bold", zorder=5)

ax.plot(x[0], vals[0], "o", ms=8.5, mfc=CREAM, mec=ORANGE, mew=2.3, zorder=6)
ax.plot(x[peak_i], vals[peak_i], "o", ms=8.5, mfc=CREAM, mec=ORANGE, mew=2.3, zorder=6)
ax.plot(x[-1], vals[-1], "o", ms=11.5, mfc=DEEP, mec=CREAM, mew=2.0, zorder=7)

# The line climbs up and right from the first point, so its label goes below,
# on one line (the first render put "$58,525" straight across the line).
t0 = ax.annotate(f"${vals[0]:,.0f}", (x[0], vals[0]), xytext=(11, -19), textcoords="offset points",
                 ha="left", va="baseline", fontsize=14.5, fontweight="bold", color=INK, zorder=6)
fig.canvas.draw()
w0 = t0.get_window_extent(renderer=fig.canvas.get_renderer()).width * 72.0 / fig.dpi
ax.annotate("June 30 close", (x[0], vals[0]), xytext=(11 + w0 + 6, -19), textcoords="offset points",
            ha="left", va="baseline", fontsize=10.5, color=MUTED, zorder=6)
ax.annotate(f"${vals[peak_i]:,.0f}", (x[peak_i], vals[peak_i]), xytext=(-10, 22), textcoords="offset points",
            ha="right", va="bottom", fontsize=14.5, fontweight="bold", color=INK)
ax.annotate("September 21, the quarter's high close", (x[peak_i], vals[peak_i]), xytext=(-10, 8),
            textcoords="offset points", ha="right", va="bottom", fontsize=10.5, color=MUTED)
ax.annotate(f"${vals[-1]:,.0f}", (x[-1], vals[-1]), xytext=(12, -2), textcoords="offset points",
            ha="left", va="bottom", fontsize=17, fontweight="bold", color=DEEP)
ax.annotate("Tuesday close", (x[-1], vals[-1]), xytext=(12, -6), textcoords="offset points",
            ha="left", va="top", fontsize=10.5, color=MUTED)

XMAX = 107
if abs(live_gap) >= 1.0:          # only worth drawing when the market has left the close
    xl = len(days)
    ax.plot([x[-1], xl + 3], [vals[-1], live["price"]], color=ORANGE, lw=2.0, ls=(0, (4, 3)), zorder=3)
    ax.plot(xl + 3, live["price"], "o", ms=9, mfc=CREAM, mec=DEEP, mew=2.0, zorder=6)
    ax.annotate(f"${live['price']:,.0f} live,\nnot a close", (xl + 3, live["price"]), xytext=(9, 0),
                textcoords="offset points", ha="left", va="center", fontsize=10, color=MUTED, linespacing=1.2)

ax.set_xlim(-2.5, XMAX)
ax.set_ylim(YLO, YHI)
ax.set_xticks(bounds)
ax.set_xticklabels(["Jun 30", "Jul 31", "Aug 31", "Sep 29"])
yt = [60000, 70000, 80000, 90000]
ax.set_yticks(yt)
ax.set_yticklabels([f"${v // 1000}K" for v in yt])
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=11)
for t in ax.get_xticklabels() + ax.get_yticklabels():
    t.set_color(INK)

# ------------------------------------------------------- right: every quarter
bx = fig.add_axes((0.655, 0.235, 0.325, 0.555))
bx.set_facecolor(CREAM)
xs = list(range(len(qret)))
for i, v in enumerate(qret):
    hero = i == len(qret) - 1
    bx.bar(i, v, width=0.64, color=ORANGE if hero else (SLATE if v >= 0 else PALE), zorder=3)
    bx.text(i, v + (2.2 if v >= 0 else -2.2), signed(v, 0 if not hero else 0),
            ha="center", va="bottom" if v >= 0 else "top",
            fontsize=13.5 if hero else 9.6, fontweight="bold" if hero or i == 0 else "normal",
            color=DEEP if hero else INK, zorder=5)
bx.axhline(0, color=INK, lw=1.0, zorder=4)
# What "best since 2024" is measured against.
bx.text(0, qret[0] + 8.2, "the last\nbetter quarter", ha="center", va="bottom", fontsize=9.2,
        color=MUTED, linespacing=1.2, zorder=5)
bx.set_xlim(-0.75, len(qret) - 0.4)
bx.set_ylim(-34, 66)
bx.set_xticks(xs)
bx.set_xticklabels(NAMES, fontsize=9.6, linespacing=1.25)
bx.set_yticks([])
for s in ("top", "right", "left", "bottom"):
    bx.spines[s].set_visible(False)
bx.tick_params(axis="x", length=0, pad=6)
for i, t in enumerate(bx.get_xticklabels()):
    t.set_color(DEEP if i == len(qret) - 1 else INK)
    if i == len(qret) - 1:
        t.set_fontweight("bold")

# ----------------------------------------------------------------- the words
fig.text(0.045, 0.945, "Bitcoin's Best Quarter Since 2024", fontsize=25, fontweight="bold",
         color=INK, ha="left", va="top")
fig.text(0.045, 0.893,
         f"Up {q3:.0f}% since June 30 with one day left in the quarter, after three straight losing quarters",
         fontsize=13.5, color=MUTED, ha="left", va="top")
fig.text(0.070, 0.812, "DAILY CLOSE, JUNE 30 TO SEPTEMBER 29, 2026", fontsize=9.6, fontweight="bold",
         color=MUTED, ha="left", va="bottom")
fig.text(0.655, 0.812, "CHANGE BY QUARTER (Q3 2026 THROUGH TUESDAY)", fontsize=9.6, fontweight="bold", color=MUTED,
         ha="left", va="bottom")

fig.text(0.045, 0.098,
         f"Still a partial recovery: Tuesday's close is {abs(from_ath):.0f}% below the record close of "
         f"${px[ath_day]:,.0f} set October 6, 2025, and {abs(ytd):.0f}% below where 2026 began.",
         fontsize=11.4, color=DEEP, ha="left", va="bottom")
fig.text(0.045, 0.040,
         "Source: Coin Metrics reference rate, daily close at 00:00 UTC (5 PM PT). Q3 2026 runs through "
         f"Tuesday's close; {live['source']} showed ${live['price']:,.0f} at {live['time_pt']} Wednesday.",
         fontsize=9.8, color=MUTED, ha="left", va="bottom")

out = os.path.join(OUTDIR, f"btc-quarter-{STAMP}.png")
save_pair(fig, out, logo=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hb-logo-mark.png"),
          facecolor=CREAM)
plt.close(fig)

print()
print("Checks:")
print(f"  Jun 30 ${vals[0]:,.2f}  peak {days[peak_i]} ${vals[peak_i]:,.2f}  Sep 29 ${vals[-1]:,.2f}")
print(f"  Q3 to date {q3:+.2f}%  July {jul:+.2f}%  August {aug:+.2f}%  September {sep:+.2f}%")
print("  quarters:", ", ".join(f"{n.replace(chr(10), ' ')} {v:+.1f}%" for n, v in zip(NAMES, qret)))
print(f"  record close {ath_day} ${px[ath_day]:,.2f} ({from_ath:+.1f}%)  2026 start ${px['2025-12-31']:,.2f} ({ytd:+.1f}%)")
print(f"  live {live['time_pt']} ${live['price']:,.2f} ({live_gap:+.2f}% vs Tuesday close), leg drawn: {abs(live_gap) >= 1.0}")
