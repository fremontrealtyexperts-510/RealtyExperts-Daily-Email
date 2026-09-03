#!/usr/bin/env python3
"""
make-adp-2026-chart.py  [out.png]

Recreation of the "Private Hiring Keeps Cooling" graphic Harv supplied for the
09/03/26 daily email.

⚠️ NAME NOTE: `make-adp-chart.py` ALREADY EXISTS (the 08/06/26 build, a 12 month
window ending July). This is a separate file on purpose. Do not merge them and do
not reuse that name. See session-2026-08-18 for the day a reused filename silently
clobbered an older chart.

✅ VERIFICATION 09/03/26. Every one of the eight months was re-pulled from the
ADP National Employment Report series on FRED (`ADPMNUSNERSA`, total nonfarm
private employment, seasonally adjusted) and differenced month over month, the
same method the 08/06 build used. The method validates against the headline: the
August diff is 132,803,000 - 132,765,000 = +38,000, which is exactly the +38K ADP
published this morning.

⚠️ THREE OF THE EIGHT BARS ARE STALE. The supplied graphic mixes vintages. Its
July bar is the REVISED 46K (its own footnote says so) and its August bar is
today's fresh print, but February, April and June are still ADP's ORIGINAL
first-release numbers, which have since been revised:

    month   supplied   current vintage   delta
    Jan         11            11           ok
    Feb         63            66           +3   stale
    Mar         61            61           ok
    Apr        109           105           -4   stale
    May        122           122           ok
    Jun         98            95           -3   stale
    Jul         46            46           ok   (revised, and the graphic says so)
    Aug         38            38           ok

That is the 08/27 Core PCE failure again: a chart where every number was once
true, strung across several vintages. This build plots ONE vintage, the current
one, and the deltas are disclosed in the caption.

⚠️ AND THE TITLE OVERREACHES. "Private hiring keeps cooling" is true of the last
four months (122 -> 95 -> 46 -> 38) but not of the year: January printed 11K,
which is the WEAKEST month on the chart, well below August's 38K. The 2026 shape
is a hump, not a slide. So the cooling call is framed to the stretch it actually
describes, May onward, and January is left visible rather than explained away.

Context for the copy, not the chart: 38K missed the ~47K consensus, and the
government's payroll report lands Friday with consensus near 53K and 4.1%
unemployment.

BRAND MARK: silver HB monogram, bottom right, no name text (Harv, 08/26/26).
matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "adp-2026-090326.png"
LOGO = "hb-logo-mark.png"

# month, current-vintage MoM change in thousands (FRED ADPMNUSNERSA differenced)
DATA = [
    ("JAN",  11), ("FEB",  66), ("MAR",  61), ("APR", 105),
    ("MAY", 122), ("JUN",  95), ("JUL",  46), ("AUG",  38),
]
SUPPLIED = {"JAN": 11, "FEB": 63, "MAR": 61, "APR": 109,
            "MAY": 122, "JUN": 98, "JUL": 46, "AUG": 38}

CREAM = "#fdf6e8"
INK   = "#1f2933"
CORAL = "#e2574c"
DEEP  = "#b8433a"
SLATE = "#4a5568"
SAND  = "#c9b896"
GRID  = "#d8cdb8"
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

labels = [d[0] for d in DATA]
vals = [d[1] for d in DATA]
xs = list(range(len(DATA)))

# The last four months are the cooling run the headline is actually about.
colors = [SAND] * len(DATA)
for i in range(4, len(DATA)):
    colors[i] = CORAL
colors[-1] = DEEP

fig, ax = plt.subplots(figsize=(12.6, 7.0), dpi=170)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

ax.bar(xs, vals, width=0.62, color=colors, zorder=3)
for x, v in zip(xs, vals):
    ax.text(x, v + 3.0, f"{v}K", ha="center", va="bottom", fontsize=16.5,
            fontweight="bold", color=INK, zorder=5)

# bracket the stretch the "cooling" claim actually covers
ax.annotate("", xy=(4, 141), xytext=(7, 141),
            arrowprops=dict(arrowstyle="-", color=DEEP, lw=1.8), zorder=6)
ax.text(5.5, 145, "the cooling run: 122K to 38K", ha="center", va="bottom",
        fontsize=13.5, fontweight="bold", color=DEEP, zorder=6)
# Sits HIGH, above every bar top, so it cannot land on the February column.
# The first placement (x=0.35, y=62) printed straight across the Feb bar.
ax.annotate("January, at 11K, was the\nweakest month of the year",
            xy=(-0.16, 7), xytext=(-0.32, 108),
            fontsize=12.5, color=SLATE, ha="left", va="center",
            arrowprops=dict(arrowstyle="-|>", color=SLATE, lw=1.4), zorder=6)

ax.set_xticks(xs)
ax.set_xticklabels(labels, fontsize=14, fontweight="bold")
ax.set_ylim(0, 170)
ax.set_yticks([0, 50, 100, 150])
ax.set_yticklabels(["0", "50K", "100K", "150K"])
ax.grid(axis="y", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=12.5, colors=SLATE)
for lbl in ax.get_xticklabels():
    lbl.set_color(INK)

fig.text(0.046, 0.958, "Private hiring cooled again in August",
         fontsize=26.5, fontweight="bold", color=INK, va="top")
fig.text(0.046, 0.897,
         "U.S. private-sector jobs added each month in 2026, seasonally adjusted",
         fontsize=14, color=SLATE, va="top")

# TWO lines. As one line this ran off the right edge of the figure.
fig.text(0.008, 0.038,
         "Source: ADP National Employment Report via FRED, current vintage, differenced month over month.",
         fontsize=10.5, color=SLATE)
fig.text(0.008, 0.013,
         "The graphic circulating this morning carried ADP's original Feb, Apr and Jun prints "
         "(63K, 109K, 98K), since revised to 66K, 105K and 95K.",
         fontsize=10.5, color=SLATE)
add_logo(fig)

fig.subplots_adjust(left=0.072, right=0.988, top=0.800, bottom=0.135)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
for m, v in DATA:
    s = SUPPLIED[m]
    flag = "ok" if s == v else f"STALE (graphic said {s}K)"
    print(f"  {m}  {v:>4}K   {flag}")
