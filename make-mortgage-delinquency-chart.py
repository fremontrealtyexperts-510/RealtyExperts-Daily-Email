#!/usr/bin/env python3
"""
make-mortgage-delinquency-chart.py  [out.png]

REALTY EXPERTS branded recreation of the "Mortgage Delinquency Rates by Loan Type"
graphic for the 08/12/26 daily email (Market Briefs "Big swing." / the Pressure
Mounts On Mortgages story). OUR OWN branded chart, not the source image.

WHY THIS IS A SNAPSHOT AND NOT THE 20-YEAR LINE CHART. The supplied graphic drew
four quarterly series from Q1 2006 to Q1 2026. The MBA National Delinquency Survey
history is a paid subscription product, so those ~80 quarters per series cannot be
sourced. Rather than trace 320 points off a picture and present them as data, this
chart carries only what is verifiable at the primary source: the Q1 2026 rate for
each loan type plus its quarter-over-quarter move. That is also where the story
actually lives, since the FHA-to-conventional gap is the widest since 2021.

Every value below is quoted verbatim from the MBA Q1 2026 National Delinquency
Survey release (May 14, 2026), confirmed across two independent write-ups, and
internally consistent with MBA's own stated spreads (FHA sits "about 900 basis
points" above conventional: 11.88 - 2.75 = 9.13; VA "almost 225 basis points"
above conventional: 4.99 - 2.75 = 2.24).

Q1 2026 is the current vintage. The Q2 2026 survey had not been released as of
08/12/26.

Warm cream ground (Meridian paper), ranked horizontal bars, FHA carried in coral
because it is the story. No authorship label; footer carries the data source only.
Run python3.13.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "mortgage-delinquency-081226.png"

# (loan type, Q1 2026 rate %, quarter-over-quarter change in basis points, colour)
# Source: MBA National Delinquency Survey, Q1 2026, seasonally adjusted.
DATA = [
    ("FHA Loans",        11.88,  36, "#e8734a"),   # the story
    ("VA Loans",          4.99,  36, "#e0a83c"),
    ("All Loans",         4.44,  18, "#6b7f99"),
    ("Conventional",      2.75, -14, "#4a9d6b"),
]

GROUND = "#FAF7F0"   # Meridian paper
INK    = "#2e2e2e"
MUTED  = "#8a8172"
GRID   = "#ddd5c6"
UP     = "#c9532c"
DOWN   = "#2f7a4d"

labels = [d[0] for d in DATA]
vals   = [d[1] for d in DATA]
deltas = [d[2] for d in DATA]
colors = [d[3] for d in DATA]
y = list(range(len(DATA)))[::-1]   # barh draws bottom-up

fig, ax = plt.subplots(figsize=(12, 6.4))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.barh(y, vals, height=0.54, color=colors, zorder=3,
        edgecolor=GROUND, linewidth=1.5)

for yi, v, d, lab in zip(y, vals, deltas, labels):
    # loan type sits above the bar, left aligned at the axis
    ax.text(0.06, yi + 0.40, lab, fontsize=15.5, fontweight="bold",
            color=INK, ha="left", va="bottom", zorder=5)
    # rate at the end of the bar
    rate_txt = f"{v:.2f}%"
    ax.text(v + 0.16, yi, rate_txt, fontsize=17, fontweight="bold",
            color=INK, ha="left", va="center", zorder=5)
    # quarter-over-quarter move just after the rate; offset scales with the
    # width of the rate label so the two never collide on a two-digit rate
    arrow = "▲" if d > 0 else "▼"
    dc = UP if d > 0 else DOWN
    ax.text(v + 0.38 + 0.32 * len(rate_txt), yi, f"{arrow} {abs(d)} bps",
            fontsize=12.5, fontweight="bold", color=dc,
            ha="left", va="center", zorder=5)

# the spread callout: FHA vs conventional
ax.annotate("", xy=(11.88, 3.34), xytext=(2.75, 3.34),
            arrowprops=dict(arrowstyle="<->", color=MUTED, linewidth=1.5))
ax.text((11.88 + 2.75) / 2, 3.42,
        "913 bps gap, widest since 2021",
        fontsize=12.5, fontweight="bold", color=MUTED, ha="center", va="bottom")

for gx in [0, 2, 4, 6, 8, 10, 12]:
    ax.axvline(gx, color=GRID, linewidth=1.0, linestyle=(0, (5, 5)), zorder=1)

ax.set_title("Mortgage Delinquency Rates by Loan Type", fontsize=25,
             fontweight="bold", color=INK, loc="left", pad=40, x=-0.005)
ax.text(-0.005, 1.045,
        "Q1 2026, seasonally adjusted share of loans past due  ·  "
        "excludes loans in foreclosure",
        transform=ax.transAxes, fontsize=13.5, color=MUTED, ha="left")

ax.set_xlim(0, 16.6)
ax.set_ylim(-0.62, 3.92)
ax.set_xticks([0, 2, 4, 6, 8, 10, 12])
ax.set_xticklabels(["0%", "2%", "4%", "6%", "8%", "10%", "12%"])
ax.set_yticks([])
ax.tick_params(axis="x", labelsize=13.5, colors=MUTED, length=0)
for lbl in ax.get_xticklabels():
    lbl.set_fontweight("bold")
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.spines["bottom"].set_linewidth(1.4)

fig.text(0.045, 0.028,
         "Source: Mortgage Bankers Association National Delinquency Survey  ·  "
         "Q1 2026, released May 14, 2026",
         fontsize=11.5, color=MUTED, ha="left")

plt.subplots_adjust(left=0.045, right=0.985, top=0.80, bottom=0.135)
fig.savefig(OUT, dpi=170, facecolor=GROUND)
print("wrote", OUT)
for lab, v, d, _ in DATA:
    print("  %-14s %5.2f%%  (%+d bps QoQ)" % (lab, v, d))
print("  FHA - conventional gap: %.2f pts" % (11.88 - 2.75))
