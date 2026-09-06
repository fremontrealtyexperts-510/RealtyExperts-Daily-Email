#!/usr/bin/env python3
"""
make-car-listprice-chart.py  [out.png]

Sunday 09/06/26 edition, companion to make-car-speed-chart.py.

The statewide story this week is a market losing steam: closed sales, pendings
and new listings all fell week over week, and C.A.R.'s inventory replenishment
rate sits at 0.59. The obvious buyer question that follows is "so can I
negotiate". This chart answers it for the Bay with C.A.R.'s own numbers.

WHAT IS PLOTTED. Not the raw sales-to-list ratio, which would compress a 99.3
to 108.2 spread against a zero baseline into eight bars of nearly equal length.
Instead the DEVIATION from the asking price in percentage points, diverging from
a zero line that means "sold for exactly what it was listed at". A California
home sold 0.7 points BELOW asking in July. Every Bay Area city in the set sold
AT or ABOVE it.

  California   99.3%  ->  -0.7
  Fremont     100.7%  ->  +0.7
  Hayward     101.4%  ->  +1.4
  Milpitas    100.9%  ->  +0.9
  Newark      100.0%  ->   0.0
  Union City  100.0%  ->   0.0
  San Jose    100.0%  ->   0.0
  Oakland     108.2%  ->  +8.2

⚠️ OAKLAND IS NOT AN ERROR AND MUST BE EXPLAINED, NOT QUIETLY DROPPED. 108.2%
is real and it is a pricing convention, not a hotter market: Oakland listing
agents routinely publish a deliberately low asking price to manufacture a
bidding war, so the ratio measures the size of the underpricing as much as the
demand. Its own C.A.R. letter shows Oakland at 17 days, the SLOWEST in this set,
which is the tell. The chart says so on its face so nobody reads it as
"Oakland is the most competitive city here". Sourced but caveated beats dropped.

BASIS: identical to the speed chart. C.A.R., July 2026, existing single family.
Statewide 99.3% from the July 2026 Home Sales and Price Report (which also gives
July 2025 at 98.5%); city values read off each city's own C.A.R. letter PDF.

⚠️ Do NOT chart the weekly dashboard's 41.4% "share of actives reduced" against
these. That figure is weekly and all property types, and C.A.R.'s monthly
release does not publish a statewide equivalent, so there is no honest statewide
counterpart to the city letters' price-cut shares. It belongs in the copy alone.

BRAND MARK: HB monogram bottom right, no name text (Harv, 08/26/26).
matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "car-listprice-090626.png"
LOGO = "hb-logo-mark.png"

# label, sales-to-list ratio (percent), role
ROWS = [
    ("Oakland",    108.2, "nearby"),
    ("Hayward",    101.4, "ledger"),
    ("Milpitas",   100.9, "ledger"),
    ("Fremont",    100.7, "fremont"),
    ("Newark",     100.0, "ledger"),
    ("San Jose",   100.0, "nearby"),
    ("Union City", 100.0, "ledger"),
    ("California",  99.3, "state"),
]
assert ROWS == sorted(ROWS, key=lambda r: -r[1]), "chart must read as a ranking"

CREAM = "#fdf6e8"
INK   = "#1f2933"
CORAL = "#e2574c"
DEEP  = "#b8433a"
TAN   = "#d9a05b"
SLATE = "#8a9bb0"
GRID  = "#d8cdb8"
MUTED = "#8a8172"

FILL = {"state": SLATE, "fremont": DEEP, "ledger": CORAL, "nearby": TAN}


def add_logo(fig, path=LOGO, height=0.05, x=0.985, y=0.026, alpha=0.20):
    """HB monogram, bottom right, deliberately near invisible but CRISP."""
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


fig, ax = plt.subplots(figsize=(12.6, 7.2), dpi=170)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

labels = [r[0] for r in ROWS]
devs = [round(r[1] - 100.0, 1) for r in ROWS]
ys = list(range(len(ROWS)))[::-1]
colors = [FILL[r[2]] for r in ROWS]

ax.barh(ys, devs, height=0.60, color=colors, zorder=3)

for y, d, (lb, ratio, role) in zip(ys, devs, ROWS):
    if abs(d) < 0.05:                       # exactly at asking, no bar to sit on
        ax.text(0.16, y, "sold at the asking price", va="center", ha="left",
                fontsize=14.5, fontweight="bold", color=INK, zorder=5)
    else:
        off = 0.16 if d > 0 else -0.16
        ax.text(d + off, y, f"{d:+.1f} pts", va="center",
                ha="left" if d > 0 else "right", fontsize=19,
                fontweight="bold", color=INK, zorder=5)

# zero line means "sold for exactly the asking price"
ax.axvline(0, color=INK, lw=1.6, zorder=4)

ax.text(4.15, 2.55,
        "Oakland lists low on purpose to\nstart a bidding war. At 17 days it is\n"
        "also the slowest city here, so read\nthis as a pricing habit, not heat.",
        va="center", ha="left", fontsize=11.5, style="italic",
        color=MUTED, linespacing=1.6, zorder=5)

ax.set_yticks(ys)
ax.set_yticklabels(labels, fontsize=15.5, fontweight="bold")
ax.set_xlim(-2.6, 10.4)
ax.set_xticks([-2, 0, 2, 4, 6, 8, 10])
ax.set_xticklabels(["-2", "asking\nprice", "+2", "+4", "+6", "+8", "+10"])
ax.grid(axis="x", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=12, colors=MUTED)
for lbl in ax.get_yticklabels():
    lbl.set_color(INK)

fig.text(0.046, 0.962, "California sells below asking. The Bay does not.",
         fontsize=24, fontweight="bold", color=INK, va="top")
fig.text(0.046, 0.905,
         "How far the typical sale landed above or below its list price, July 2026, existing single family homes",
         fontsize=13.5, color=MUTED, va="top")
fig.text(0.046, 0.856,
         "Slate bar is the statewide figure. Tan bars are neighboring cities shown for context.",
         fontsize=11.5, color=MUTED, style="italic", va="top")

fig.text(0.008, 0.020,
         "California Association of REALTORS®. Statewide sales-price-to-list-price ratio was 99.3% in July 2026, up from "
         "98.5% a year earlier;\ncity ratios from C.A.R.'s July 2026 city market reports.",
         fontsize=10.5, color=MUTED, linespacing=1.5)
add_logo(fig)

fig.subplots_adjust(left=0.135, right=0.975, top=0.775, bottom=0.150)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
for (lb, ratio, role), d in zip(ROWS, devs):
    print(f"  {lb:<12} {ratio:>6.1f}%  -> {d:+.1f} pts   ({role})")
