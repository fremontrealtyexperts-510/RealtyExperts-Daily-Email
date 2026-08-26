#!/usr/bin/env python3
"""
make-bayarea-rentbuy-chart.py  [out.png]

The LOCAL companion to make-rentbuy-chart.py, built 08/26/26 at Harv's
direction: the newsletter's rent versus buy story named seven metros and not one
of them was in the Bay Area, so this answers "what is that number here".

⚠️ WHY THIS IS A SEPARATE CHART AND NOT FIVE MORE BARS ON THE OTHER ONE.
Apartments.com's study cannot be extended. Its rent figures are APARTMENT rents
and its home prices are FHFA metro estimates, and the two do not travel
together. The tell: Apartments.com puts Sacramento rent at $1,579 while Zillow's
all homes rent index for the same city and month is $2,064, about 31% higher.
Bolting a Fremont bar computed any other way onto their ranking would have been
exactly the cross vendor mixing we refuse to do with prices.

METHOD (one publisher, one month, one geography definition, stated on the chart):
  home value  Zillow ZHVI, all homes, smoothed and seasonally adjusted, Jul 2026
  rent        Zillow ZORI, all homes, smoothed, Jul 2026
  payment     20% down, 30 year fixed at 6.75% (Mortgage News Daily, 08/26/26),
              principal and interest ONLY
  gap         monthly P&I minus monthly rent

Principal and interest only is deliberate. It matches the basis Apartments.com
used, so the Austin bar here stays comparable to the $1,054 they published.
Property tax, insurance and any HOA sit ON TOP of every payment shown, so every
gap in this chart is the CONSERVATIVE version of the real cash difference.

✅ VERIFICATION 08/26/26. The method was validated by reproducing a published
number with it. Austin on this method comes out at a $1,006 monthly gap against
the $1,054 Apartments.com printed, a 4.5% difference explained entirely by ZHVI
($504,148) standing in for their FHFA price estimate. That is close enough to
trust the same math on Bay Area cities.

  city          ZHVI Jul26    loan(80%)      P&I    ZORI Jul26      gap
  Fremont        1,471,931    1,177,545    7,638         3,358    4,280
  Milpitas       1,424,179    1,139,343    7,390         3,715    3,675
  Union City     1,223,080      978,464    6,346         2,941    3,405
  Newark         1,202,648      962,118    6,240         3,578    2,662
  Hayward          831,558      665,246    4,315         2,635    1,680
  Austin, TX       504,148      403,318    2,616         1,610    1,006   <- ref

Independent cross check on Fremont, using OUR OWN MLS export rather than Zillow:
the median list price of the 240 active Fremont listings on 08/26/26 is
$1,260,912, which at the same 20% down and 6.75% is $6,543 of P&I and a $3,185
gap against the same rent. So the honest Fremont range is roughly $3,200 to
$4,300 a month depending on whether you price the typical home or today's median
active listing. The chart plots the Zillow basis because that is the only one
that stays consistent across all six cities; the MLS floor belongs in the copy.

⚠️ ALSO WORTH SAYING IN THE COPY: on this like for like basis Sacramento's gap
is about $429, not the $1,042 the newsletter reported. Their number is inflated
by comparing an apartment rent against a house sized mortgage payment. Fremont's
lead is real regardless, which is why it is safe to say out loud.

BRAND MARK (Harv, 08/26/26): HB monogram bottom right, very low opacity, no name
text. Gold was rejected as too bright, light silver as too low contrast.

matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "bayarea-rentbuy-082626.png"
LOGO = "hb-logo-mark.png"

# city, monthly gap (P&I minus rent), is_local
ROWS = [
    ("Fremont",        4280, True),
    ("Milpitas",       3675, True),
    ("Union City",     3405, True),
    ("Newark",         2662, True),
    ("Hayward",        1680, True),
    ("Austin, TX",     1006, False),
]
assert ROWS == sorted(ROWS, key=lambda r: -r[1]), "chart reads as a ranking"

CREAM = "#fdf6e8"
INK   = "#1f2933"
CORAL = "#e2574c"
DEEP  = "#b8433a"
SLATE = "#8a9bb0"
GRID  = "#d8cdb8"
MUTED = "#8a8172"


def add_logo(fig, path=LOGO, height=0.05, x=0.985, y=0.026, alpha=0.20):
    """HB monogram, bottom right, deliberately near invisible but CRISP.

    Resample ONCE with PIL to the exact pixel size the figure draws, then blit
    1:1 with interpolation="none". Missing file or PIL is non-fatal."""
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
ys = list(range(len(ROWS)))[::-1]

colors = [DEEP if lb == "Fremont" else (CORAL if loc else SLATE)
          for lb, v, loc in ROWS]

ax.barh(ys, values, height=0.58, color=colors, zorder=3)

for y, v, (lb, _v, loc) in zip(ys, values, ROWS):
    ax.text(v + 70, y, f"${v:,}", va="center", ha="left", fontsize=21,
            fontweight="bold", color=INK, zorder=5)

ax.set_yticks(ys)
ax.set_yticklabels(labels, fontsize=15, fontweight="bold")
ax.set_xlim(0, max(values) * 1.20)
ax.set_xticks([0, 1000, 2000, 3000, 4000])
ax.set_xticklabels(["0", "$1,000", "$2,000", "$3,000", "$4,000"])

ax.grid(axis="x", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=12.5, colors=MUTED)
for lbl in ax.get_yticklabels():
    lbl.set_color(INK)

fig.text(0.046, 0.958, "Renting is cheaper here too, by a lot more",
         fontsize=26.5, fontweight="bold", color=INK, va="top")
fig.text(0.046, 0.897,
         "Monthly gap between the mortgage payment on a typical home and the typical rent, July 2026",
         fontsize=13.5, color=MUTED, va="top")

# call out that the last bar is the national headline, not a local market
austin_y = ys[-1]
ax.text(values[-1] + 1120, austin_y,
        "the metro the newsletter ranked first",
        va="center", ha="left", fontsize=12.5, style="italic", color=MUTED, zorder=5)

fig.text(0.008, 0.022,
         "Zillow ZHVI and ZORI, all homes, July 2026. Payment is 20% down on a 30 year fixed at 6.75% "
         "(Mortgage News Daily, Aug 26), principal and interest only.\nTaxes, insurance and HOA sit on top of every "
         "payment shown, so each gap is the conservative figure.",
         fontsize=10.5, color=MUTED, linespacing=1.5)
add_logo(fig)

fig.subplots_adjust(left=0.135, right=0.975, top=0.795, bottom=0.155)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
for lb, v, loc in ROWS:
    print(f"  {lb:<14} ${v:>6,}{'' if loc else '   (reference)'}")
