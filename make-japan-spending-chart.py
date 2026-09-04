#!/usr/bin/env python3
"""
make-japan-spending-chart.py  [out.png]

Recreation of the "Japan's 8-Month Spending Slump" graphic Harv supplied for the
09/04/26 daily email.

✅ VERIFICATION 09/04/26. All EIGHT bars check out. Japan's Statistics Bureau
(Ministry of Internal Affairs and Communications) Family Income and Expenditure
Survey, two-or-more-person households, real year on year change:

    Dec 2025  -2.6%   Reuters                       ok
    Jan 2026  -1.0%   Reuters                       ok
    Feb 2026  -1.8%   Reuters                       ok
    Mar 2026  -2.9%   Reuters, Xinhua, Japan Times  ok
    Apr 2026  -0.5%   stat.go.jp, official table    ok
    May 2026  -0.4%   stat.go.jp, official table    ok
    Jun 2026  -3.3%   stat.go.jp, official table    ok
    Jul 2026  -3.6%   stat.go.jp, official summary  ok

Eight consecutive negative months, so the "8-month" claim is right too.

⚠️ VINTAGE NOTE, and the graphic got this RIGHT. The Statistics Bureau flags on
its own page that April, May and June 2026 were RETROACTIVELY REVISED, because
the CPI used to deflate nominal spending into real terms was rebased to 2025.
The supplied graphic carries the CURRENT revised values for those three months,
so its vintage is consistent. Worth knowing that Trading Economics still lists
May as -0.5%, which is either the pre-revision figure or a month shifted; the
Japanese source settles it at -0.4%. Secondary aggregators lag a rebasing.

⚠️ WHERE THE FRAMING FALLS SHORT: "slump" implies a steady slide, and the data
is not that. April and May were nearly flat, -0.5% and -0.4%, close to a
recovery. Then June and July broke down hard. Two facts the supplied chart holds
but does not say:
  1. July's -3.6% is the steepest drop since JANUARY 2024, when it fell 6.3%.
  2. Economists expected about -1.6% for July. The miss was two full points.
Both are on this build, because they are the reason the July bar matters.

BRAND MARK: silver HB monogram, bottom right, no name text (Harv, 08/26/26).
matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "japan-spending-090426.png"
LOGO = "hb-logo-mark.png"

DATA = [
    ("DEC\n'25", -2.6), ("JAN", -1.0), ("FEB", -1.8), ("MAR", -2.9),
    ("APR", -0.5), ("MAY", -0.4), ("JUN", -3.3), ("JUL", -3.6),
]
JULY_FORECAST = -1.6      # median economist forecast for July
PRIOR_WORST = ("Jan 2024", -6.3)

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
assert all(v < 0 for v in vals), "every month must be negative for an 8-month slump"

colors = [SAND] * len(DATA)
colors[-1] = DEEP          # July, the steepest in 30 months
colors[-2] = CORAL         # June

fig, ax = plt.subplots(figsize=(12.6, 7.0), dpi=170)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

ax.bar(xs, vals, width=0.62, color=colors, zorder=3)
for x, v in zip(xs, vals):
    ax.text(x, v - 0.16, f"{v}%", ha="center", va="top", fontsize=16,
            fontweight="bold", color=INK, zorder=5)

ax.axhline(0, color=SLATE, lw=1.6, zorder=4)

# ANNOTATION LAYOUT. First pass put all three of these inside the bar field and
# every one of them collided: the "nearly flat" note sat on the MAY bar, the
# forecast callout ran across the JUN bar and its own -0.4% label, and "steepest
# since Jan 2024" ran off the right edge. They now live in a clear column to the
# RIGHT of July, and the forecast marker is drawn beside the July bar, not
# through it. Caught by eyeballing the render.
ax.plot([7.38, 8.30], [JULY_FORECAST, JULY_FORECAST], color=SLATE, lw=2.0,
        ls=(0, (5, 3)), zorder=6)
ax.text(8.42, JULY_FORECAST, f"July forecast\n{JULY_FORECAST}%",
        fontsize=12, fontweight="bold", color=SLATE, ha="left", va="center", zorder=7)

ax.annotate(f"steepest since\n{PRIOR_WORST[0]}, when it\nfell {abs(PRIOR_WORST[1])}%",
            xy=(7.33, -3.52), xytext=(8.42, -3.15),
            fontsize=12, fontweight="bold", color=DEEP, ha="left", va="center",
            arrowprops=dict(arrowstyle="-|>", color=DEEP, lw=1.5), zorder=7)

ax.text(4.5, -1.62, "April and May were\nnearly flat, then it broke",
        ha="center", va="center", fontsize=12, color=SLATE, style="italic", zorder=6)

ax.set_xticks(xs)
ax.set_xticklabels(labels, fontsize=13.5, fontweight="bold")
ax.set_xlim(-0.65, 10.55)
ax.set_ylim(-4.5, 0.65)
ax.set_yticks([0, -1, -2, -3, -4])
ax.set_yticklabels(["0%", "-1%", "-2%", "-3%", "-4%"])
ax.grid(axis="y", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left", "bottom"):
    ax.spines[s].set_visible(False)
ax.tick_params(axis="both", length=0, labelsize=12.5, colors=SLATE)
for lbl in ax.get_xticklabels():
    lbl.set_color(INK)

fig.text(0.046, 0.958, "Japan's spending slump got worse, not better",
         fontsize=26, fontweight="bold", color=INK, va="top")
fig.text(0.046, 0.897,
         "Household spending, real change from a year earlier, eight straight negative months",
         fontsize=14, color=SLATE, va="top")

fig.text(0.008, 0.038,
         "Source: Japan Statistics Bureau, Ministry of Internal Affairs and Communications, "
         "Family Income and Expenditure Survey, two-or-more-person households.",
         fontsize=10.5, color=SLATE)
fig.text(0.008, 0.013,
         "April, May and June were retroactively revised by the Bureau after the consumer price "
         "index was rebased to 2025. The current revised values are shown.",
         fontsize=10.5, color=SLATE)
add_logo(fig)

fig.subplots_adjust(left=0.072, right=0.988, top=0.800, bottom=0.150)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
for lb, v in DATA:
    print(f"  {lb.replace(chr(10),' '):<8} {v:>5}%")
print(f"  July vs forecast: {vals[-1]} vs {JULY_FORECAST}  (miss of {abs(vals[-1]-JULY_FORECAST):.1f} pts)")
