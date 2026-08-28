#!/usr/bin/env python3
"""
make-localrent-chart.py  [out.png]

Built for the 08/28/26 daily email, to answer a national headline locally.

THE HEADLINE (verified at the primary source): Apartment List's National Rent
Report for August 2026 says the national median rent rose 0.1% this month to
$1,390, the first August increase in four years, with their vacancy index down
to 7.1%, its first decline since late 2021. Rents are down 0.8% year over year.
Market Briefs ran this story on 08/28 and reported it correctly.

WHY THIS CHART EXISTS: $1,390 describes nobody in our five cities. Standing
instruction (Harv, 08/26/26): when a national study lands with no Bay Area
market in it, build the chart that gives the LOCAL answer.

⚠️ METHOD NOTE, THE WHOLE POINT OF WHICH IS NOT TO CHEAT:
Apartment List's $1,390 and the numbers on this chart are DIFFERENT SERIES and
are NOT comparable. Apartment List measures new leases signed on its own
platform; Zillow's ZORI measures asking rents across all home types. Their
national figures differ by nearly $600 for that reason alone. So this chart does
NOT extend Apartment List's series and does NOT plot their number. Every bar
here, the five cities AND the United States reference bar, comes from ONE
series, ZORI, so the local-versus-national comparison on this chart is internally
honest. The Apartment List figure stays in the copy, attributed to Apartment
List, and is never set beside these bars.

ENDPOINT: ZORI's latest published month is JULY 2026. Apartment List's headline
is AUGUST. The chart is labeled July and the copy says so. Do not imply this
chart shows the August move.

DATA (Zillow Observed Rent Index, smoothed, all home types, July 2026, pulled
from files.zillowstatic.com public CSVs on 08/28/26):

  city            Jul-2026   Jul-2025    YoY
  Milpitas          $3,715     $3,429   +8.4%
  Newark            $3,578     $3,458   +3.5%
  Fremont           $3,358     $3,199   +5.0%
  Union City        $2,941     $2,818   +4.3%
  Hayward           $2,635     $2,560   +3.0%
  United States     $1,962     $1,918   +2.3%

Every one of our five cities is growing faster than the nation, and the cheapest
of them costs 34% more than the national figure.

BRAND MARK: silver HB monogram, bottom right, no name text (Harv, 08/26/26).
matplotlib only; build with python3.13 on Mac.
"""
import sys
from decimal import Decimal, ROUND_HALF_UP
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "localrent-082826.png"
LOGO = "hb-logo-mark.png"

# city, typical asking rent Jul-2026 (ZORI), year-over-year percent change
ROWS = [
    ("Milpitas",       3715,  8.4),
    ("Newark",         3578,  3.5),
    ("Fremont",        3358,  5.0),
    ("Union City",     2941,  4.3),
    ("Hayward",        2635,  3.0),
    ("United States",  1962,  2.3),
]
assert ROWS == sorted(ROWS, key=lambda r: -r[1]), "chart reads as a ranking by rent"
assert ROWS[-1][0] == "United States", "the national bar anchors the bottom"
# The claim the subtitle makes, asserted rather than trusted:
assert all(r[2] > ROWS[-1][2] for r in ROWS[:-1]), "every local city outgrew the nation"

CREAM = "#fdf6e8"
INK   = "#1f2933"
CORAL = "#e2574c"
DEEP  = "#b8433a"
SLATE = "#4a5568"
GRID  = "#d8cdb8"
MUTED = "#9aa5b1"


def add_logo(fig, path=LOGO, height=0.05, x=0.985, y=0.026, alpha=0.20):
    """Silver HB monogram, bottom right corner, deliberately near invisible.

    Copied verbatim from make-rentbuy-chart.py, which Harv approved 08/26/26.
    Sharpness comes from resampling ONCE with PIL to the exact pixel size the
    figure draws at, then blitting 1:1. Missing file or PIL is non-fatal."""
    try:
        from PIL import Image
        import numpy as np
        src = Image.open(path).convert("RGBA")
    except (FileNotFoundError, OSError, ImportError):
        print(f"WARN: {path} unavailable, chart rendered without the brand mark")
        return False
    fw, fh = fig.get_size_inches()
    px_h = max(1, int(round(height * fh * fig.dpi)))
    px_w = max(1, int(round(src.width * px_h / src.height)))
    src = src.resize((px_w, px_h), Image.LANCZOS)
    w = px_w / (fw * fig.dpi)
    ax = fig.add_axes((x - w, y, w, height), zorder=10)
    ax.imshow(np.asarray(src), interpolation="none", alpha=alpha)
    ax.axis("off")
    return True


fig, ax = plt.subplots(figsize=(12.6, 7.0), dpi=170)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

labels = [r[0] for r in ROWS]
values = [r[1] for r in ROWS]
yoys   = [r[2] for r in ROWS]
ys = list(range(len(ROWS) - 1, -1, -1))

# Fremont is the focus city so it steps forward; the nation is the reference
# bar and is deliberately drained of colour so it reads as a benchmark, not a
# peer.
colors = []
for lb in labels:
    if lb == "Fremont":
        colors.append(DEEP)
    elif lb == "United States":
        colors.append(MUTED)
    else:
        colors.append(CORAL)
ax.barh(ys, values, height=0.58, color=colors, zorder=3)

for y, v, g in zip(ys, values, yoys):
    ax.text(v + 45, y, f"\\${v:,}", va="center", ha="left", fontsize=17,
            fontweight="bold", color=INK, zorder=5)
    ax.text(v + 640, y, f"+{g:.1f}% yr/yr", va="center", ha="left", fontsize=13,
            color=SLATE, zorder=5)

ax.set_yticks(ys)
ax.set_yticklabels(labels, fontsize=14.5, fontweight="bold")
# Headroom for the dollar label plus the year-over-year label to its right.
# 5,150 keeps Milpitas's "+8.4% yr/yr" clear of the right edge (at 4,850 it
# collided with it) and the last x tick at 4,000 clear of the brand mark.
ax.set_xlim(0, 5150)
ax.set_xticks([0, 1000, 2000, 3000, 4000])
ax.set_xticklabels(["0", "\\$1,000", "\\$2,000", "\\$3,000", "\\$4,000"])
ax.set_ylim(-0.75, len(ROWS) - 0.25)

ax.grid(axis="x", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=12.5, colors=SLATE)
for lbl in ax.get_yticklabels():
    lbl.set_color(INK)

fig.text(0.046, 0.958, "The national rent story is not our rent story",
         fontsize=26.5, fontweight="bold", color=INK, va="top")
fig.text(0.046, 0.897,
         "Typical asking rent, July 2026. Every one of our five cities is rising "
         "faster than the nation.",
         fontsize=14, color=SLATE, va="top")

# Two lines: as one line this ran off the right edge of the figure.
fig.text(0.008, 0.038,
         "Source: Zillow Observed Rent Index, smoothed, all home types, July 2026.",
         fontsize=11, color=SLATE)
fig.text(0.008, 0.012,
         "The United States bar comes from that same index, so every bar is measured the same way.",
         fontsize=11, color=SLATE)
add_logo(fig)

fig.subplots_adjust(left=0.145, right=0.988, top=0.805, bottom=0.115)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
nat = ROWS[-1][1]
for lb, v, g in ROWS:
    prem = "" if lb == "United States" else f"  {Decimal(str(v / nat * 100 - 100)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)}% above US"
    print(f"  {lb:<15} ${v:>6,}  +{g:.1f}%{prem}")
