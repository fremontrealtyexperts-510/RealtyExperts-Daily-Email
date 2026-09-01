#!/usr/bin/env python3
"""
make-september-stocks-chart.py  [out.png]

Recreation of the "What September Did To Stocks" graphic Harv supplied for the
09/01/26 daily email.

✅ VERIFICATION PASSED, ALL ELEVEN NUMBERS. Every bar and the stated average
were recomputed from SPY monthly ADJUSTED closes (dividends reinvested), August
month-end to September month-end, which is the same basis the graphic cites:

  year   graphic     recomputed
  2016     0.0%        +0.01%
  2017    +2.0%        +2.01%
  2018    +0.6%        +0.59%
  2019    +1.9%        +1.95%
  2020    -3.7%        -3.74%
  2021    -4.7%        -4.66%
  2022    -9.2%        -9.24%
  2023    -4.7%        -4.74%
  2024    +2.1%        +2.10%
  2025    +3.6%        +3.56%
  average -1.2%        -1.22%

That is the first supplied graphic in four sessions where nothing had to be
corrected. The values are kept exactly as they are.

⚠️ SO WHY REDRAW IT AT ALL. Because the values are right and the FRAMING is not.
Market Briefs ran it under "September is historically the worst month for
stocks, with the S&P dropping 1.2% on average," which invites a reader to expect
a down September. The distribution says something different:

  • SIX of the ten were POSITIVE. Only four were negative.
  • The MEDIAN September was +0.30%, not -1.2%.
  • 2022 alone (-9.24%) supplies about three quarters of the negative mean.
    Drop that single year and the average of the other nine is -0.32%.
  • The two most recent Septembers, 2024 and 2025, were the second and first
    best in the whole window.

A mean of ten observations dragged by one nine point outlier is a fact about
2022, not a rule about Septembers. So this version keeps their bars and adds the
median line and the up/down count, which is the honest reading of the same data.
Same failure family as the 08/28 silver headline: every number true, the
impression wrong.

DATA: SPY monthly adjusted closes via Yahoo, pulled 09/01/26.

BRAND MARK: silver HB monogram, bottom right, no name text (Harv, 08/26/26).
matplotlib only; build with python3.13 on Mac.
"""
import sys
from statistics import median
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "september-stocks-090126.png"
LOGO = "hb-logo-mark.png"

# year, September total return in percent (SPY adjusted close, Aug end to Sep end)
ROWS = [
    (2016,  0.01), (2017,  2.01), (2018,  0.59), (2019,  1.95), (2020, -3.74),
    (2021, -4.66), (2022, -9.24), (2023, -4.74), (2024,  2.10), (2025,  3.56),
]
VALS = [v for _, v in ROWS]
MEAN = sum(VALS) / len(VALS)
MED = median(VALS)
UP = sum(1 for v in VALS if v > 0)
DOWN = sum(1 for v in VALS if v < 0)
EX22 = sum(v for y, v in ROWS if y != 2022) / (len(ROWS) - 1)

# The three claims the subtitle and annotations make, asserted rather than trusted:
assert abs(MEAN - (-1.22)) < 0.01, f"mean drifted: {MEAN}"
assert UP == 6 and DOWN == 4, f"up/down count changed: {UP}/{DOWN}"
assert MED > 0, "the median September was positive, which is the whole point"
assert EX22 > MEAN, "excluding 2022 must lift the average"

CREAM = "#fdf6e8"
INK   = "#1f2933"
GREEN = "#3f9d6d"
RED   = "#e2574c"
SLATE = "#4a5568"
GRID  = "#d8cdb8"
GOLD  = "#c9922e"


def add_logo(fig, path=LOGO, height=0.05, x=0.985, y=0.026, alpha=0.20):
    """Silver HB monogram, bottom right. Verbatim from make-rentbuy-chart.py."""
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

xs = list(range(len(ROWS)))
colors = [GREEN if v > 0 else RED for v in VALS]
ax.bar(xs, VALS, width=0.62, color=colors, zorder=3)

for x, (yr, v) in zip(xs, ROWS):
    off = 0.55 if v >= 0 else -0.55
    va = "bottom" if v >= 0 else "top"
    ax.text(x, v + off, f"{v:+.1f}%", ha="center", va=va, fontsize=13.5,
            fontweight="bold", color=GREEN if v > 0 else RED, zorder=5)

# The two lines that carry the correction.
ax.axhline(MEAN, color=RED, lw=1.6, ls=(0, (5, 4)), zorder=4)
ax.axhline(MED, color=GOLD, lw=1.6, ls=(0, (5, 4)), zorder=4)
ax.axhline(0, color=SLATE, lw=1.1, zorder=2)

ax.text(len(ROWS) - 0.35, MEAN - 0.30, f"average  {MEAN:.1f}%", ha="right", va="top",
        fontsize=12.5, fontweight="bold", color=RED, zorder=6)
# The median label cannot sit on the right: at +0.3% that is inside the 2025
# bar. The only clear span on this line is above the four negative years, so it
# goes there. (The average label at -1.2% IS clear on the right, because 2024
# and 2025 are positive.)
ax.text(5.0, MED + 0.35, f"median  {MED:+.1f}%", ha="center", va="bottom",
        fontsize=12.5, fontweight="bold", color=GOLD, zorder=6)

ax.annotate("one year supplies three quarters\nof that negative average",
            xy=(6, -9.24), xytext=(4.55, -6.6), ha="right", va="center",
            fontsize=11.5, color=SLATE, linespacing=1.45,
            arrowprops=dict(arrowstyle="-", color=SLATE, lw=1.0,
                            shrinkA=6, shrinkB=8, alpha=0.65))

ax.set_xticks(xs)
ax.set_xticklabels([f"'{str(y)[2:]}" for y, _ in ROWS], fontsize=14, fontweight="bold")
ax.set_ylim(-11.6, 6.2)
ax.set_yticks([-10, -5, 0, 5])
ax.yaxis.set_major_formatter(lambda v, p: f"{v:+.0f}%".replace("+0%", "0%"))
ax.grid(axis="y", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=12.5, colors=SLATE)
for lbl in ax.get_xticklabels():
    lbl.set_color(INK)

fig.text(0.046, 0.958, "September's bad reputation is mostly one year",
         fontsize=26.5, fontweight="bold", color=INK, va="top")
fig.text(0.046, 0.897,
         f"S&P 500 total return in September. The average is {MEAN:.1f}%, but {UP} of the "
         f"last 10 were positive and the median was {MED:+.1f}%.",
         fontsize=14, color=SLATE, va="top")

fig.text(0.008, 0.038,
         "Source: SPY monthly total returns, dividends reinvested, August close to September close.",
         fontsize=11, color=SLATE)
fig.text(0.008, 0.012,
         f"Excluding 2022 the average of the remaining nine Septembers is {EX22:.1f}%.",
         fontsize=11, color=SLATE)
add_logo(fig)

fig.subplots_adjust(left=0.075, right=0.978, top=0.805, bottom=0.115)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
print(f"  mean {MEAN:+.2f}%   median {MED:+.2f}%   up {UP} / down {DOWN}")
print(f"  average excluding 2022: {EX22:+.2f}%  (2022 alone = {-9.24/ (MEAN*len(ROWS)) * 100:.0f}% of the total drag)")
