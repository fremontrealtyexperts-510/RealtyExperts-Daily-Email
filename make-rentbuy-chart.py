#!/usr/bin/env python3
"""
make-rentbuy-chart.py  [out.png]

Recreation of the "Renting Is Cheaper Than Buying" graphic Harv supplied for the
08/26/26 daily email.

✅ VERIFICATION DONE 08/26/26. Every one of the seven values was read off the
primary source, Apartments.com's "Cities Where Renting Is More Affordable Than
Buying in 2026" (Katherine Chavous, published July 24, 2026), and each stated
gap was independently checked against that city's own printed mortgage and rent:

  city                mortgage      rent    stated gap   mortgage - rent
  Austin, TX           $2,475     $1,421      $1,054        $1,054  ok
  Sacramento, CA       $2,621     $1,579      $1,042        $1,042  ok
  Denver, CO           $2,518     $1,633        $885          $885  ok
  Portland, OR         $2,404     $1,551        $853          $853  ok
  Baltimore, MD        $2,254     $1,527        $727          $727  ok
  Salt Lake City, UT   $2,106     $1,428        $678          $678  ok
  Orlando, FL          $1,967     $1,590        $377          $377  ok

All seven internally consistent, all seven match the supplied graphic. Method,
in the publisher's words: average monthly rent from 2026 Apartments.com rent
data against the city median monthly mortgage payment estimated by the FHFA,
ranked by the difference.

Two cautions that belong in the copy, not the chart:
  1. The study is dated JULY 24, 2026. The newsletter ran it on August 26 as
     though it were fresh. It is a month old.
  2. It compares an APARTMENT rent against a house sized mortgage payment, so it
     measures monthly cash out the door, not equivalent housing.

Do not trust a search summary here. Mid verification, web results returned
Denver "$1,070", Portland "$970" and Salt Lake City "$1,100" for this same
study. All three are wrong, bled in from unrelated articles, and each would have
outranked Austin and broken the ranking. The page itself settled it.

BRAND MARK (standing instruction, Harv, 08/26/26): recreations carry the SILVER
HB monogram in the bottom right corner, at very low opacity, instead of the
words "Created by Harv Balu". REVERSES the 08/25 credit-line rule, which itself
reversed the 06/29 source-only-footer rule. No name text. The gold version was
rejected as too bright: this is a signature, not a badge.

matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "rentbuy-082626.png"
LOGO = "hb-logo-mark.png"

# city, monthly saving renting vs the median mortgage payment
ROWS = [
    ("Austin, TX",      1054),
    ("Sacramento, CA",  1042),
    ("Denver, CO",       885),
    ("Portland, OR",     853),
    ("Baltimore, MD",    727),
    ("Salt Lake City",   678),
    ("Orlando, FL",      377),
]
assert ROWS == sorted(ROWS, key=lambda r: -r[1]), "chart reads as a ranking"

CREAM = "#fdf6e8"
INK   = "#1f2933"
CORAL = "#e2574c"
DEEP  = "#b8433a"
SLATE = "#4a5568"
SAND  = "#c9b896"
GRID  = "#d8cdb8"
MUTED = "#8a8172"


def add_logo(fig, path=LOGO, height=0.05, x=0.985, y=0.026, alpha=0.20):
    """Silver HB monogram, bottom right corner, deliberately near invisible.

    Harv, 08/26/26: "the logo is not the main thing here, almost transparent as
    possible, just barely visible", then "make the logo a bit small", then "not
    clear or sharp". So: small, faint, but CRISP.

    Sharpness comes from resampling ONCE, with PIL, to the exact pixel size the
    figure will draw at, then blitting 1:1 with interpolation="none". Letting
    matplotlib rescale a 500px hairline master down to ~60px softens the strokes
    to mush. There is no vector master for this monogram, so this is as sharp as
    it gets. Missing file or missing PIL is non-fatal."""
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
ys = list(range(len(ROWS) - 1, -1, -1))

# Sacramento carries the local read for a Bay Area audience, so it is the one
# bar that steps forward. Everything else stays in the base coral.
colors = [DEEP if lb.endswith("CA") else CORAL for lb in labels]
ax.barh(ys, values, height=0.58, color=colors, zorder=3)

for y, v in zip(ys, values):
    ax.text(v + 14, y, f"\\${v:,}", va="center", ha="left", fontsize=17,
            fontweight="bold", color=INK, zorder=5)

ax.set_yticks(ys)
ax.set_yticklabels(labels, fontsize=14.5, fontweight="bold")
# Last tick stops at $1,000: a $1,250 label collides with the brand mark in the
# bottom right corner. Caught by eyeballing the render, not by any assert.
ax.set_xlim(0, 1235)
ax.set_xticks([0, 250, 500, 750, 1000])
ax.set_xticklabels(["0", "\\$250", "\\$500", "\\$750", "\\$1,000"])
ax.set_ylim(-0.75, len(ROWS) - 0.25)

ax.grid(axis="x", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=12.5, colors=SLATE)
for lbl in ax.get_yticklabels():
    lbl.set_color(INK)

fig.text(0.046, 0.958, "Renting is cheaper than buying",
         fontsize=26.5, fontweight="bold", color=INK, va="top")
fig.text(0.046, 0.897,
         "What a renter saves each month against the median mortgage payment, 2026",
         fontsize=14, color=SLATE, va="top")

fig.text(0.008, 0.022,
         "Sources: Apartments.com 2026 rent data; median mortgage payments estimated by "
         "the FHFA. Study published July 24, 2026.",
         fontsize=11, color=SLATE)
add_logo(fig)

fig.subplots_adjust(left=0.165, right=0.988, top=0.805, bottom=0.115)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
for lb, v in ROWS:
    print(f"  {lb:<16} ${v:>6,}")
