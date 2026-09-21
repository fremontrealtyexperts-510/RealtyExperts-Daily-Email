#!/usr/bin/env python3
"""
make-boj-rate-chart.py  [outdir]

Recreates the supplied graphic "Japan Just Hiked To A 31-Year High" (Bank of
Japan policy rate, Jan 2024 to Sept 18, 2026) for the 09/21/26 edition. Emits
BOTH brand variants:

  boj-rate-092126.png      plain monogram -> RE email + Agent Hub
  boj-rate-092126-hb.png   + wordmark     -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/21/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

Every step was read out of the Bank of Japan's own statement for that meeting
(boj.or.jp/en/mopo/mpmdeci/state_YYYY/ and mpr_YYYY/), by extracting the
sentence "encourage the uncollateralized overnight call rate to remain at
around X percent" from each document:

  decided      effective    target            vote       document
  2024-03-19   2024-03-21   0 to 0.1 percent   7-2        state_2024/k240319a.htm
  2024-07-31   2024-08-01   0.25 percent       7-2        state_2024/k240731a.htm
  2025-01-24   2025-01-27   0.5 percent        8-1        state_2025/k250124a.htm
  2025-12-19   2025-12-22   0.75 percent       unanimous  state_2025/k251219a.htm
  2026-06-16   2026-06-17   1.0 percent        7-1        mpr_2026/k260616a.pdf
  2026-09-18   2026-09-24   1.25 percent       7-2        mpr_2026/k260918a.pdf

Before March 2024 the short term policy rate was minus 0.1 percent.

VALUES: all seven levels on the supplied graphic are RIGHT, and so are the
step positions by eye.

FRAMING, three fixes:
  1. The graphic labels March 2024 "0.1%". The BOJ's target was a RANGE,
     "around 0 to 0.1 percent". This version shades that band and says so.
  2. "Sixth hike since exiting negative rates" miscounts by one. The exit in
     March 2024 was itself the first increase, so September is the sixth
     increase COUNTING the exit, or the fifth after it. This version says
     "six increases, starting with the exit".
  3. The graphic stamps the last step "Sept 18, 2026", the decision date. The
     increase takes EFFECT on September 24, because September 21, 22 and 23
     are all Japanese holidays in 2026. On the day this runs the rate in
     force is still 1.0 percent. Steps are drawn at decision dates, which is
     what the headline refers to, and the footer names the effective date.

HEADLINE: "31-year high" is RIGHT. OECD immediate rates, call money, Japan
(FRED IRSTCI01JPM156N, monthly average) was last at or above 1.25 percent in
June 1995 at 1.279 percent, then 0.947 in July 1995. 2026 less 1995 is 31.
Market Briefs' "highest since 1995" agrees.

House style: warm cream ground, coral line, no authorship label, footer is the
data source only. matplotlib only; build with python3.13 on Mac.
"""
import os
import sys
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "092126"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8392f"
SAND = "#e9dcc2"
GRID = "#d8cdb8"
MUTED = "#8a8172"
MINUS = "−"   # a real minus sign; a hyphen is too easy to lose next to a line

START = date(2024, 1, 1)
END = date(2026, 9, 30)

# (decision date, level drawn, label). March 2024 is drawn at the top of its
# 0 to 0.1 range, with the range itself shaded underneath.
STEPS = [
    (START,             -0.10, f"{MINUS}0.1%"),
    (date(2024, 3, 19),  0.10, "0 to 0.1%"),
    (date(2024, 7, 31),  0.25, "0.25%"),
    (date(2025, 1, 24),  0.50, "0.5%"),
    (date(2025, 12, 19), 0.75, "0.75%"),
    (date(2026, 6, 16),  1.00, "1.0%"),
    (date(2026, 9, 18),  1.25, "1.25%"),
]

xs = [d for d, _, _ in STEPS] + [END]
ys = [v for _, v, _ in STEPS] + [STEPS[-1][1]]

fig, ax = plt.subplots(figsize=(11.6, 6.7))
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

ax.axhline(0, color=MUTED, lw=1.2, alpha=0.8, zorder=2)
ax.grid(axis="y", color=GRID, lw=0.7, alpha=0.75)
ax.set_axisbelow(True)

# The March to July 2024 target was a range, not a point.
ax.fill_between([date(2024, 3, 19), date(2024, 7, 31)], 0, 0.10,
                color=SAND, alpha=0.95, zorder=1, lw=0)

ax.step(xs, ys, where="post", color=CORAL, lw=3.2, zorder=4,
        solid_joinstyle="miter")

for d, v, _ in STEPS[1:-1]:
    ax.plot(d, v, "o", ms=8, mfc=CREAM, mec=CORAL, mew=2.2, zorder=5)
ax.plot(STEPS[-1][0], STEPS[-1][1], "o", ms=12, mfc=DEEP, mec=CREAM,
        mew=2.2, zorder=6)

# Step labels. Placed above each new level and to the right of the riser, so
# no label sits on the line itself.
LABEL_OFFSETS = {
    "0 to 0.1%": (6, 12),
    "0.25%": (6, 12),
    "0.5%": (6, 12),
    "0.75%": (6, 12),
    "1.0%": (6, 12),
}
for d, v, lab in STEPS[1:-1]:
    dx, dy = LABEL_OFFSETS[lab]
    ax.annotate(lab, (d, v), xytext=(dx, dy), textcoords="offset points",
                ha="left", va="bottom", fontsize=12, fontweight="bold",
                color=INK)

ax.annotate(STEPS[0][2], (START, -0.10), xytext=(10, -22),
            textcoords="offset points", ha="left", va="center",
            fontsize=12, fontweight="bold", color=DEEP)

ax.annotate("1.25%", (STEPS[-1][0], 1.25), xytext=(-12, 16),
            textcoords="offset points", ha="right", va="bottom",
            fontsize=21, fontweight="bold", color=DEEP)

# No in-band caption: the band is only 0.1 tall, so any text inside it sits on
# the line (first render). The "0 to 0.1%" label already says it is a range.

ax.text(date(2024, 1, 20), 1.42,
        "Highest since 1995",
        fontsize=13.5, fontweight="bold", color=INK, ha="left", va="center")
ax.text(date(2024, 1, 20), 1.30,
        "Japan's overnight rate last averaged 1.25% or more in June 1995.",
        fontsize=10.6, color=INK, ha="left", va="center")

ax.set_xlim(date(2023, 12, 1), date(2026, 10, 31))
ax.set_ylim(-0.30, 1.55)
ax.set_yticks([0, 0.5, 1.0, 1.5])
ax.set_yticklabels(["0%", "0.5%", "1.0%", "1.5%"])
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=(4, 7, 10)))

for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_color(GRID)
# tick_params resets label colours, so recolour after it.
ax.tick_params(axis="both", colors=MUTED, labelsize=11, length=0)
ax.tick_params(axis="x", which="minor", length=4, color=GRID)
for t in ax.get_xticklabels() + ax.get_yticklabels():
    t.set_color(INK)
for t in ax.get_xticklabels():
    t.set_fontweight("bold")

fig.text(0.062, 0.948, "Japan just raised rates to a 31-year high",
         fontsize=21, fontweight="bold", color=INK, ha="left")
fig.text(0.062, 0.905,
         "Bank of Japan policy rate target since January 2024. Six increases, "
         "starting with the exit from negative rates.",
         fontsize=11.4, color=MUTED, ha="left")

fig.text(0.062, 0.043,
         "Bank of Japan statements on monetary policy, March 2024 to September "
         "2026; OECD call rate via FRED for the 1995 comparison.",
         fontsize=9.2, color=MUTED, ha="left")
fig.text(0.062, 0.016,
         "Steps drawn at decision dates. The September increase takes effect "
         "September 24, after three Japanese holidays.",
         fontsize=9.2, color=MUTED, ha="left")

fig.subplots_adjust(left=0.075, right=0.975, top=0.855, bottom=0.12)

out = os.path.join(OUTDIR, f"boj-rate-{STAMP}.png")
save_pair(fig, out, logo=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "hb-logo-mark.png"))

print()
print("Checks:")
for d, v, lab in STEPS:
    print(f"  {d.isoformat()}  {v:+.2f}  {lab}")
