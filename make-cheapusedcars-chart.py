#!/usr/bin/env python3
"""
make-cheapusedcars-chart.py  [out.png]

Recreation of the "Cheap Used Cars Are Vanishing" graphic Harv supplied for the
09/02/26 daily email, EXPANDED.

✅ VERIFICATION 09/02/26. The supplied card shows two bars, "share of used-car
sales priced under $20,000": Q2 2019 = 55.2%, Q2 2026 = 32%, sourced to Edmunds.
Both values trace to the Edmunds Q2 2026 used vehicle report. Three independent
write ups of that release agree:

    Auto Remarketing   55.2% (Q2 2019) -> 31.8% (Q2 2026)
    Autobody News      55.2% (Q2 2019) -> 31.8% (Q2 2026)
    Epoch Times        "55 percent"    -> "nearly 32 percent"

So the supplied 32% is a rounding of 31.8%, not an error. This chart uses the
precise 31.8%.

⚠️ WHY IT IS REDRAWN ANYWAY. Two accurate bars are a headline, not an argument.
They say the cheap car is disappearing without showing what replaced it. The
same Edmunds release carries the number that actually bites, and it is the one
a household budget feels: what a fixed budget now buys. Same money, much older
car, far more miles.

    budget            Q2 2019                    Q2 2026
    $10,000-$15,000   4.7 yrs,  58,250 miles     8.7 yrs,  98,222 miles
    $15,000-$20,000   3.4 yrs,  41,851 miles     6.0 yrs,  71,192 miles

Both bands are carried by all three write ups above, so both are safe to plot.

DROPPED: the $5,000-$10,000 band (8.1 -> 10.7 years). Only ONE of the three
sources printed it and no second source confirms it, so it does not get a bar.
Standing rule: drop any bar you cannot source twice.

Context that belongs in the copy, not the chart: Edmunds also put the average
transaction price of a THREE YEAR OLD used vehicle at $32,461 in Q2 2026, a Q2
record. Market Briefs ran a related item this morning quoting a $27,028 average
used listing price for July, about 29% above July 2019; that is a different
series (all listings, one month) and is not mixed into this chart.

BRAND MARK: silver HB monogram, bottom right, no name text (Harv, 08/26/26).
matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "cheapusedcars-090226.png"
LOGO = "hb-logo-mark.png"

SHARE = [("Q2 2019", 55.2), ("Q2 2026", 31.8)]

# budget band, (2019 age, 2019 miles), (2026 age, 2026 miles)
BANDS = [
    ("\\$10,000 to \\$15,000", (4.7, 58250), (8.7, 98222)),
    ("\\$15,000 to \\$20,000", (3.4, 41851), (6.0, 71192)),
]

CREAM = "#fdf6e8"
INK   = "#1f2933"
CORAL = "#e2574c"
DEEP  = "#b8433a"
SLATE = "#4a5568"
SAND  = "#c9b896"
GRID  = "#d8cdb8"


def add_logo(fig, path=LOGO, height=0.05, x=0.985, y=0.026, alpha=0.20):
    """Silver HB monogram, bottom right corner, deliberately near invisible."""
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


fig, (axL, axR) = plt.subplots(
    1, 2, figsize=(13.6, 7.2), dpi=170, gridspec_kw={"width_ratios": [1, 1.45]})
fig.patch.set_facecolor(CREAM)
for a in (axL, axR):
    a.set_facecolor(CREAM)

# ---------------------------------------------------------------- left panel
labels = [s[0] for s in SHARE]
vals = [s[1] for s in SHARE]
xs = [0, 1]
axL.bar(xs, vals, width=0.52, color=[SAND, DEEP], zorder=3)
for x, v in zip(xs, vals):
    axL.text(x, v + 1.6, f"{v}%", ha="center", va="bottom", fontsize=27,
             fontweight="bold", color=INK, zorder=5)
axL.set_xticks(xs)
axL.set_xticklabels(labels, fontsize=15, fontweight="bold")
axL.set_ylim(0, 68)
axL.set_yticks([0, 20, 40, 60])
axL.set_yticklabels(["0", "20%", "40%", "60%"])
axL.grid(axis="y", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
axL.set_axisbelow(True)
axL.set_title("Share of used-car sales under \\$20,000",
              fontsize=14.5, fontweight="bold", color=INK, pad=14)

# ---------------------------------------------------------------- right panel
ys, tick_pos, tick_lab = [], [], []
h = 0.34
for i, (band, y19, y26) in enumerate(BANDS):
    base = (len(BANDS) - 1 - i) * 1.25
    axR.barh(base + h / 2 + 0.02, y19[0], height=h, color=SAND, zorder=3)
    axR.barh(base - h / 2 - 0.02, y26[0], height=h, color=DEEP, zorder=3)
    axR.text(y19[0] + 0.14, base + h / 2 + 0.02,
             f"{y19[0]} yrs  ·  {y19[1]:,} mi", va="center", ha="left",
             fontsize=12.5, fontweight="bold", color=SLATE, zorder=5)
    axR.text(y26[0] + 0.14, base - h / 2 - 0.02,
             f"{y26[0]} yrs  ·  {y26[1]:,} mi", va="center", ha="left",
             fontsize=12.5, fontweight="bold", color=INK, zorder=5)
    tick_pos.append(base)
    tick_lab.append(band)

axR.set_yticks(tick_pos)
axR.set_yticklabels(tick_lab, fontsize=14.5, fontweight="bold")
axR.set_xlim(0, 14.2)
axR.set_xticks([0, 2, 4, 6, 8, 10])
axR.set_xticklabels(["0", "2", "4", "6", "8", "10 yrs"])
axR.set_ylim(-0.85, (len(BANDS) - 1) * 1.25 + 0.85)
axR.grid(axis="x", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
axR.set_axisbelow(True)
axR.set_title("What that budget buys: age and miles",
              fontsize=14.5, fontweight="bold", color=INK, pad=14)

for a in (axL, axR):
    for s in ("top", "right", "left"):
        a.spines[s].set_visible(False)
    a.spines["bottom"].set_color(GRID)
    a.tick_params(axis="both", length=0, labelsize=12.5, colors=SLATE)
    for lbl in a.get_yticklabels() + a.get_xticklabels():
        lbl.set_color(INK if lbl.get_fontweight() == "bold" else SLATE)

# Legend lives in the header, NOT in the axes. An in-axes legend at lower right
# sat directly on top of the "8" and "10 yrs" tick labels; caught by eyeballing
# the render, not by any assert.
from matplotlib.patches import Patch
fig.legend(handles=[Patch(facecolor=SAND, label="Q2 2019"),
                    Patch(facecolor=DEEP, label="Q2 2026")],
           loc="upper right", frameon=False, fontsize=13.5, ncol=2,
           bbox_to_anchor=(0.986, 0.985), handlelength=1.5, columnspacing=1.6)

fig.text(0.036, 0.960, "Cheap used cars are vanishing",
         fontsize=27, fontweight="bold", color=INK, va="top")
fig.text(0.036, 0.902,
         "The same budget now buys a car four years older with 40,000 more miles",
         fontsize=14, color=SLATE, va="top")

fig.text(0.008, 0.022,
         "Source: Edmunds Q2 2026 used vehicle report. Shares are of all used-vehicle "
         "sales; age and mileage are averages within each price band.",
         fontsize=11, color=SLATE)
add_logo(fig)

fig.subplots_adjust(left=0.075, right=0.985, top=0.775, bottom=0.115, wspace=0.42)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
print(f"  share under \\$20k: {SHARE[0][1]}% ({SHARE[0][0]}) -> {SHARE[1][1]}% ({SHARE[1][0]})")
for band, y19, y26 in BANDS:
    print(f"  {band:<22} {y19[0]} yrs/{y19[1]:,} mi -> {y26[0]} yrs/{y26[1]:,} mi")
