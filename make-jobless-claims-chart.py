#!/usr/bin/env python3
"""
make-jobless-claims-chart.py  [out.png]

REALTY EXPERTS recreation of the "US Jobless Claims Keep Hovering Near Lows"
graphic Harv supplied for the 08/21/26 daily email. OUR OWN branded chart: warm
cream ground, coral line with an area fill, the latest week called out.

Story (Market Briefs, 08/21/26): "Initial claims slipped to around 200,000, down
about 6,000 from the prior week."

⚠️ THE SUPPLIED GRAPHIC'S HEADLINE NUMBER IS WRONG. It prints 202K. The Labor
Department's own release for the week ending August 15 (embargoed to 8:30am ET
Thursday, August 20, 2026) puts advance seasonally adjusted initial claims at
206,000, a decrease of 6,000 from the previous week's REVISED 212,000. MB's
"down about 6,000" is right; its "around 200,000" is loose; the graphic's 202K
matches neither the advance figure nor any recent week. This chart uses 206,000.

DATA PROVENANCE, and why it is not FRED. FRED and ALFRED were both unreachable
from this host on build day (connection failures, not 5xx), so the series was
rebuilt from the PRIMARY source: DOL's weekly UI claims press releases at
oui.doleta.gov/press/YYYY/MMDDYY.pdf. Each release tabulates three weeks of
seasonally adjusted initial claims, so a year of Thursdays was fetched and, for
each week ending date, the value from the LATEST release naming it was kept, so
every point is the most revised figure available. The last three points
reproduce the published table exactly: Aug 15 = 206,000, Aug 8 = 212,000,
Aug 1 = 200,000.

⚠️ FIVE WEEKS ARE GENUINELY MISSING and are NOT interpolated. No release exists
at the press archive for the weeks ending 2025-09-27 through 2025-10-25 (those
Thursdays return 404 while their neighbours return 200). Rather than invent
points, the line BREAKS across that span and the gap is labeled. Never draw a
bar you cannot source.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "jobless-082126.png"

DATES = [
    "2025-07-26", "2025-08-02", "2025-08-09", "2025-08-16", "2025-08-23", "2025-08-30",
    "2025-09-06", "2025-09-13", "2025-09-20", "2025-11-01", "2025-11-08", "2025-11-15",
    "2025-11-22", "2025-11-29", "2025-12-06", "2025-12-13", "2025-12-20", "2025-12-27",
    "2026-01-03", "2026-01-10", "2026-01-17", "2026-01-24", "2026-01-31", "2026-02-07",
    "2026-02-14", "2026-02-21", "2026-02-28", "2026-03-07", "2026-03-14", "2026-03-21",
    "2026-03-28", "2026-04-04", "2026-04-11", "2026-04-18", "2026-04-25", "2026-05-02",
    "2026-05-09", "2026-05-16", "2026-05-23", "2026-05-30", "2026-06-06", "2026-06-13",
    "2026-06-20", "2026-06-27", "2026-07-04", "2026-07-11", "2026-07-18", "2026-07-25",
    "2026-08-01", "2026-08-08", "2026-08-15",
]
CLAIMS = [
    219000, 227000, 224000, 234000, 229000, 236000, 264000, 232000,
    218000, 229000, 228000, 222000, 217000, 192000, 237000, 224000,
    215000, 200000, 207000, 199000, 210000, 209000, 232000, 229000,
    208000, 213000, 214000, 213000, 205000, 211000, 203000, 218000,
    208000, 215000, 190000, 199000, 212000, 210000, 212000, 225000,
    230000, 227000, 216000, 217000, 217000, 209000, 189000, 198000,
    200000, 212000, 206000,
]

LAST = CLAIMS[-1]
PRIOR_YEAR = 233000     # comparable week a year earlier, per the same release

assert DATES[-1] == "2026-08-15", "series must end at the latest published week"
assert LAST == 206000, "endpoint must be the DOL advance SA figure, not the graphic's 202K"

INK    = "#12263f"
CORAL  = "#e2574c"
MUTED  = "#6b7280"
GROUND = "#fdf6e8"
GRID   = "#e7ddc9"
FILL   = "#f6c9c4"

d = [datetime.date.fromisoformat(x) for x in DATES]

# split into contiguous runs so the unpublished weeks leave a real gap
runs, cur = [], [0]
for i in range(1, len(d)):
    if (d[i] - d[i - 1]).days > 7:
        runs.append(cur); cur = [i]
    else:
        cur.append(i)
runs.append(cur)

fig, ax = plt.subplots(figsize=(12.6, 6.8))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

floor = 175000
for r in runs:
    xs = [d[i] for i in r]; ys = [CLAIMS[i] for i in r]
    ax.fill_between(xs, floor, ys, color=FILL, alpha=0.5, zorder=2)
    ax.plot(xs, ys, color=CORAL, linewidth=2.2, zorder=3)

# label the hole rather than papering over it
gap_a, gap_b = d[runs[0][-1]], d[runs[1][0]]
mid = gap_a + (gap_b - gap_a) / 2
ax.axvspan(gap_a, gap_b, color="#efe6d2", alpha=0.65, zorder=1)
ax.text(mid, 251000, "no weekly release\npublished", ha="center", va="center",
        fontsize=10.5, fontstyle="italic", color=MUTED, zorder=4)

ax.plot([d[-1]], [LAST], "o", color=CORAL, markersize=9, zorder=5)
ax.annotate("206,000\nweek ending Aug 15",
            xy=(d[-1], LAST),
            xytext=(d[-1] - datetime.timedelta(days=26), 224500),
            ha="right", va="center", fontsize=14, fontweight="bold", color=CORAL,
            zorder=5, arrowprops=dict(arrowstyle="-", color=CORAL, linewidth=1.1))

ax.axhline(PRIOR_YEAR, color=MUTED, linewidth=1.3, linestyle=(0, (6, 5)), zorder=2)
ax.text(d[1], PRIOR_YEAR + 2200, "Same week a year earlier  233,000",
        ha="left", va="bottom", fontsize=11, fontstyle="italic", color=MUTED, zorder=4)

ax.set_ylim(floor, 278000)
ax.set_yticks([180000, 200000, 220000, 240000, 260000])
ax.set_yticklabels(["180K", "200K", "220K", "240K", "260K"], fontsize=12, color=MUTED)

ticks = [x for x in d if x.day <= 7 and x.month in (9, 11, 1, 3, 5, 7)]
ax.set_xticks(ticks)
ax.set_xticklabels([t.strftime("%b %Y").upper() for t in ticks], fontsize=11.5, color=MUTED)

ax.grid(axis="y", color=GRID, linewidth=1.1, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("US Jobless Claims Keep Hovering Near Lows", fontsize=25,
             fontweight="bold", color=INK, loc="left", pad=46)
ax.text(0.0, 1.045, "Weekly initial claims, seasonally adjusted",
        transform=ax.transAxes, fontsize=12.5, fontweight="bold", color=MUTED,
        ha="left")

fig.text(0.012, 0.014, "Source: U.S. Department of Labor, weekly unemployment "
         "insurance claims releases (advance and revised seasonally adjusted "
         "initial claims).", fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.075, right=0.985, top=0.80, bottom=0.115)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, "| weeks:", len(CLAIMS), "| runs:", len(runs))
print("  span", DATES[0], "->", DATES[-1])
print("  last three:", list(zip(DATES[-3:], CLAIMS[-3:])))
print("  min", min(CLAIMS), "max", max(CLAIMS), "| gap weeks not drawn:",
      (d[runs[1][0]] - d[runs[0][-1]]).days // 7 - 1)
