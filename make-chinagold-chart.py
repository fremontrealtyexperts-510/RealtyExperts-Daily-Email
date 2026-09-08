#!/usr/bin/env python3
"""
make-chinagold-chart.py  [outdir]

Recreates the Market Briefs graphic "China Can't Stop Buying Gold" for the
09/08/26 edition. Emits BOTH brand variants:

  chinagold-090826.png      plain HB monogram    -> RE email + Agent Hub
  chinagold-090826-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/08/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

Every bar in the supplied graphic VERIFIED, and the arithmetic closes from four
independent directions rather than one. Source is China's State Administration
of Foreign Exchange (SAFE), which publishes the reserve LEVEL in millions of
fine troy ounces; the monthly "add" is the first difference of that level.

  Q1 2026 end   2,313.46 t  = 74.379M oz
  Q2 2026 end   2,346.43 t  = 75.439M oz
  Jul 2026 end  76.08M oz
  Aug 2026 end  76.73M oz   = 2,386.6 t, matching the reported ~2,386.57 t record

  Mar add  = 74.379 - 74.220 = 159K            graphic says 160K  ✓
  Apr+May+Jun = 75.439 - 74.379 = 1,060K       graphic says 260+320+480 = 1,060K  ✓
              = 32.97 t, and Q2 tonnage moved 2,346.43 - 2,313.46 = 32.97 t  ✓ exact
  May alone, Kitco: 9.95 t = 319,900 oz        graphic says 320K  ✓
  Jul add  = 76.080 - 75.439 = 641K            graphic says 640K  ✓
  Aug add  = 76.730 - 76.080 = 650K            graphic says 650K  ✓

Streak cross check: Kitco has January 2026 as the 15th consecutive month and
February as the 16th. Feb + 6 = August = the 22nd, which is exactly what SAFE
and Market Briefs report. So month 1 of the streak is NOVEMBER 2024, not
October 2023. One secondary write up conflated the streak start with "biggest
monthly increase since October 2023", which is a SIZE comparison, not a streak
date. The two facts are unrelated and the copy must not merge them.

THE ONE THING THE SUPPLIED GRAPHIC GETS WRONG: ITS WINDOW
------------------------------------------------------------------
The original plots March through August only, and titles that ramp "China Can't
Stop Buying Gold". January and February 2026 are missing, and they are the two
months that matter most:

    Jan  +40K      Feb  +30K      Mar +160K  ...  Aug +650K

China very nearly DID stop, at 30,000 ounces in February, and then went up
every single month after it. Cutting the window at March hides the trough and
turns a 21 fold acceleration into a tidy 4 fold ramp. **Restoring the two
omitted months makes the graphic's own argument stronger, not weaker**, which is
why this is a correction and not a quibble. Same class as the 09/01 September
seasonality chart: the framing, not the arithmetic, was doing the lying.

Note the shape is NOT monotonic across the year. Jan 40 to Feb 30 is a DIP. The
honest claim is "grew every month since February", which is what the title says.

matplotlib only; build with python3.13 on Mac.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "090826"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
SLATE = "#8a9aa8"
GRID = "#d8cdb8"
MUTED = "#8a8172"
RESTORED = "#c9b896"   # the two months the original left out

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]
ADDS = [40, 30, 160, 260, 320, 480, 640, 650]   # thousands of troy ounces
OMITTED = {0, 1}   # Jan, Feb: absent from the supplied graphic


def build():
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    for i, v in enumerate(ADDS):
        last = i == len(ADDS) - 1
        if i in OMITTED:
            color, edge, hatch = RESTORED, MUTED, "///"
        elif last:
            color, edge, hatch = CORAL, DEEP, None
        else:
            color, edge, hatch = SLATE, "none", None
        ax.bar(i, v, width=0.64, color=color, edgecolor=edge,
               linewidth=1.3 if i in OMITTED else 0, hatch=hatch, zorder=3)
        ax.text(i, v + 12, f"{v}K", ha="center", va="bottom",
                fontsize=18 if last else 15, fontweight="bold",
                color=DEEP if last else (MUTED if i in OMITTED else INK), zorder=5)

    # Call out the trough the original cropped away. Text sits in the empty
    # upper left quadrant (every bar left of May is under 300K); the first
    # render put it at y=300 where it landed on the Mar and Apr value labels.
    ax.annotate(
        "January and February are missing\nfrom the original graphic. February\nwas the low point, at 30,000 ounces.",
        xy=(0.74, 42), xytext=(-0.30, 700),   # left of the centered "30K" label
        fontsize=12, color=MUTED, ha="left", va="top", linespacing=1.55,
        arrowprops=dict(arrowstyle="->", color=MUTED, linewidth=1.4,
                        connectionstyle="arc3,rad=-0.18", shrinkA=6, shrinkB=4),
        zorder=7,
    )

    ax.set_xticks(range(len(MONTHS)))
    ax.set_xticklabels(MONTHS, fontsize=15, fontweight="bold")
    for lbl, i in zip(ax.get_xticklabels(), range(len(MONTHS))):
        lbl.set_color(MUTED if i in OMITTED else INK)
    ax.set_ylim(0, 760)
    ax.set_yticks([0, 200, 400, 600])
    ax.set_yticklabels(["0", "200K", "400K", "600K"])
    ax.grid(axis="y", color=GRID, linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="both", length=0, labelsize=13, colors=SLATE)

    fig.text(0.045, 0.945, "China's Gold Buying Grew Every Month Since February",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888,
             "Troy ounces added to China's official gold reserves each month in 2026",
             fontsize=14.5, color=MUTED, ha="left", va="top")

    fig.text(
        0.045, 0.045,
        "Source: China State Administration of Foreign Exchange (SAFE), monthly change in official gold reserves. August 2026 was the\n"
        "22nd consecutive month of buying, a streak that began in November 2024, and took reserves to a record 76.73 million ounces.",
        fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5,
    )

    fig.subplots_adjust(left=0.085, right=0.965, top=0.815, bottom=0.185)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"chinagold-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
