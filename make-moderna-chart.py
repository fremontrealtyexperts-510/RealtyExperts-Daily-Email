#!/usr/bin/env python3
"""
make-moderna-chart.py  [out.png]

REALTY EXPERTS recreation of the "Moderna's 491% Year" graphic Harv supplied for
the 08/20/26 daily email. OUR OWN branded chart: warm cream ground, coral line
with an area fill, the year-end baseline as a dashed reference, and the runup
called out.

Story (Market Briefs, 08/20/26): Moderna's and Merck's experimental melanoma
vaccine kept the cancer from returning in a late stage trial. MRNA rose 176.97%
on August 19 and added roughly $60B of market value in a single day.

WHAT WAS VERIFIED, and one thing the supplied graphic got right that looked wrong
at first glance:

  * The $29.49 baseline is CORRECT. It is the 2025-12-31 close, the proper year
    to date base. An early check against the first 2026 bar (2026-01-02, $30.86)
    made the graphic look wrong by about 26 points of return. It was not: YTD is
    measured from the prior year end close, not the first trading day.
    174.38 / 29.49 - 1 = +491.3%, matching the supplied graphic exactly.
  * The $174.38 endpoint is the VERIFIED 2026-08-19 close (Yahoo Finance daily).
  * MB's +176.97% one day move reconciles: 62.96 on 08/18 to 174.38 on 08/19.

⚠️ THE ENDPOINT WAS ALREADY BEING OVERTAKEN WHEN THIS WAS BUILT. The supplied
graphic is a picture of Wednesday's close. By midday Thursday 08/20 MRNA had
given back a large part of the spike, trading near $131.77 while the market was
still open. That live tick is NOT charted as a close (never chart an unsettled
tick, see make-meta-chart.py). It is drawn as a separate dashed leg to an open
marker and labeled as midday and not settled, the same treatment used for the
Cisco earnings reaction on 08/13. The line itself ends at the last settled close.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "moderna-082026.png"

# Yahoo Finance daily closes. First entry is the 2025 year end close (the YTD base).
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
    "2026-08-17", "2026-08-18", "2026-08-19",
]
CLOSES = [
    29.49, 30.86, 32.17, 35.66, 35.89, 33.86, 34.30, 33.84, 39.60, 40.58,
    39.36, 41.83, 43.00, 49.81, 51.87, 48.71, 47.99, 45.45, 45.30, 46.86,
    44.07, 42.55, 42.20, 42.77, 40.87, 41.01, 41.95, 41.99, 40.51, 40.11,
    42.23, 43.93, 46.60, 49.70, 49.87, 50.29, 50.52, 51.37, 51.71, 53.57,
    52.85, 49.83, 57.80, 53.83, 52.52, 55.74, 54.98, 55.97, 53.39, 52.56,
    53.31, 53.93, 52.40, 52.37, 51.38, 51.28, 51.34, 53.54, 53.57, 49.56,
    48.23, 50.80, 50.03, 49.20, 48.77, 50.11, 52.10, 51.28, 50.96, 50.68,
    52.84, 54.26, 54.68, 53.72, 54.59, 54.23, 55.60, 52.85, 50.73, 48.70,
    47.14, 45.72, 45.94, 45.37, 47.30, 46.71, 48.79, 48.54, 54.35, 52.88,
    53.27, 50.42, 50.03, 49.04, 48.11, 45.72, 48.12, 47.26, 46.88, 47.03,
    47.61, 47.57, 47.19, 46.06, 45.64, 49.06, 51.59, 47.44, 47.60, 47.73,
    45.99, 49.64, 49.91, 52.13, 55.40, 61.80, 63.96, 59.35, 61.00, 60.42,
    59.75, 67.27, 69.70, 70.03, 72.50, 79.76, 81.80, 79.77, 73.80, 76.56,
    68.27, 67.01, 67.44, 68.28, 63.15, 61.82, 59.49, 59.66, 58.07, 57.02,
    54.07, 55.63, 55.81, 54.49, 57.92, 54.82, 55.14, 56.99, 56.26, 53.86,
    59.17, 59.81, 60.57, 63.67, 63.65, 63.32, 64.46, 62.96, 174.38,
]

BASE = 29.49          # 2025-12-31 close
LAST = CLOSES[-1]     # 2026-08-19 close, the last SETTLED session
LIVE = 131.77         # 2026-08-20 midday, market open, NOT a close
LIVE_LABEL = "Aug 20 midday\n$131.77, not settled"

assert abs(BASE - CLOSES[0]) < 0.01, "baseline must be the 2025 year end close"
assert abs(LAST - 174.38) < 0.01, "endpoint must be the verified 08/19 close"
assert DATES[-1] == "2026-08-19", "series must end at the last settled session"

INK    = "#12263f"
CORAL  = "#e2574c"
MUTED  = "#6b7280"
GROUND = "#fdf6e8"
GRID   = "#e7ddc9"
FILL   = "#f6c9c4"

xs = list(range(len(CLOSES)))

fig, ax = plt.subplots(figsize=(12.6, 6.8))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.fill_between(xs, BASE, CLOSES, color=FILL, alpha=0.55, zorder=2)
ax.plot(xs, CLOSES, color=CORAL, linewidth=2.4, zorder=3)

# where the year started
ax.axhline(BASE, color=MUTED, linewidth=1.3, linestyle=(0, (6, 5)), zorder=2)
ax.text(1, BASE - 11, "Started the year at $29.49", ha="left", va="top",
        fontsize=11.5, fontstyle="italic", color=MUTED, zorder=4)

# the settled endpoint
ax.plot([xs[-1]], [LAST], "o", color=CORAL, markersize=9, zorder=5)
ax.annotate("$174.38  ·  +491% YTD\nAug 19 close",
            xy=(xs[-1], LAST), xytext=(xs[-1] - 12, LAST + 6),
            ha="right", va="bottom", fontsize=14, fontweight="bold",
            color=CORAL, zorder=5)

# the pullback already under way while this was built
ax.plot([xs[-1], xs[-1] + 5], [LAST, LIVE], color=MUTED, linewidth=1.8,
        linestyle=(0, (4, 3)), zorder=4)
ax.plot([xs[-1] + 5], [LIVE], "o", markersize=9, zorder=5,
        markerfacecolor=GROUND, markeredgecolor=MUTED, markeredgewidth=1.8)
# xlim carries extra right margin so this label cannot run off the canvas
# (it was clipped on the first render; only eyeballing the PNG showed it)
ax.annotate(LIVE_LABEL, xy=(xs[-1] + 5, LIVE), xytext=(xs[-1] + 8, LIVE - 4),
            ha="left", va="top", fontsize=11, color=MUTED, zorder=5)

ax.set_xlim(-3, len(xs) + 46)
ax.set_ylim(0, 205)
ax.set_yticks([0, 50, 100, 150, 200])
ax.set_yticklabels(["$0", "$50", "$100", "$150", "$200"], fontsize=12, color=MUTED)

# month ticks
seen, ticks, labels = set(), [], []
for i, d in enumerate(DATES):
    mo = d[:7]
    if mo not in seen and d >= "2026-01-01":
        seen.add(mo)
        ticks.append(i)
        labels.append(["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG"][int(d[5:7]) - 1])
ax.set_xticks(ticks)
ax.set_xticklabels(labels, fontsize=12, color=MUTED)

ax.grid(axis="y", color=GRID, linewidth=1.1, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("Moderna's 491% Year", fontsize=25, fontweight="bold",
             color=INK, loc="left", pad=46)
ax.text(0.0, 1.045, "MRNA share price, 2025 year end close through August 19, 2026",
        transform=ax.transAxes, fontsize=12.5, fontweight="bold", color=MUTED,
        ha="left")

fig.text(0.012, 0.014, "Source: Yahoo Finance, MRNA daily closing prices. "
         "Year to date measured from the December 31, 2025 close of $29.49.",
         fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.075, right=0.985, top=0.80, bottom=0.115)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, "| bars:", len(CLOSES))
print("  base %.2f -> last %.2f = %+.1f%% YTD" % (BASE, LAST, (LAST / BASE - 1) * 100))
print("  one day 08/18 %.2f -> 08/19 %.2f = %+.2f%%" % (CLOSES[-2], LAST, (LAST / CLOSES[-2] - 1) * 100))
print("  live 08/20 midday %.2f = %+.1f%% YTD (NOT charted as a close)" % (LIVE, (LIVE / BASE - 1) * 100))
