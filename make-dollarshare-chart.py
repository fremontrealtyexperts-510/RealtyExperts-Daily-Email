#!/usr/bin/env python3
"""
make-dollarshare-chart.py  [outdir]

Recreates the Market Briefs graphic "The Dollar Loses Ground" for the 09/08/26
edition. Emits BOTH brand variants:

  dollarshare-090826.png      plain HB monogram    -> RE email + Agent Hub
  dollarshare-090826-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/08/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

All FOUR values verified against the cited primary source, the New York Fed's
Liberty Street Economics post "Are Central Banks Moving Out of Dollar Assets?"
(Goldberg, Hannaoui and Parthasarathy, September 2, 2026):

  "The dollar's share of global official foreign exchange reserves fell from
   64 percent in 2015 to 56 percent in 2025."
  "From 2015 to 2019, the dollar share fell by 3 percentage points."   -> 2019 = 61%
  "From 2019 to 2023, the decline moderated to 2 percentage points."  -> 2023 = 59%

  Check: 3 + 2 + 3 = 8, and 64 - 8 = 56. The four points close exactly.

⚠️ METHOD NOTE ON HOW THIS WAS VERIFIED. A first summarizing fetch of the same
post confidently returned "2023: 58%". The post states NO standalone 2023
figure at all; 59% is derived from its two stated declines. A second, narrower
fetch asking for verbatim sentences exposed the invention. **A summarizer will
hand back a number its source never printed.** Ask for the quote, not the value.
This also means the graphic's 59% is RIGHT and my first pass was wrong.

Separately, do not mix this series with IMF COFER's headline "allocated
reserves" share, which is a different denominator and prints 56.77% for Q4 2025.
The NY Fed basis is global OFFICIAL reserves. Both are correct; they are not
interchangeable, and the graphic cites the NY Fed, so the NY Fed basis is used
throughout. Same discipline as the Brent futures-versus-spot lock.

TWO THINGS THE SUPPLIED GRAPHIC GETS WRONG, both fixed here
------------------------------------------------------------------
1. UNEVEN YEAR GAPS DRAWN EVENLY. The original spaces 2015, 2019, 2023 and 2025
   at equal widths, but the first two gaps are FOUR years and the last is TWO.
   Drawn honestly on a real time axis the picture changes materially:

       2015 to 2019   -3 pp over 4 yr  = -0.75 pp/yr
       2019 to 2023   -2 pp over 4 yr  = -0.50 pp/yr
       2023 to 2025   -3 pp over 2 yr  = -1.50 pp/yr   <- twice as fast as either

   The even spacing flattens the recent stretch into "more of the same" when it
   is in fact the steepest part of the whole decade. This is the 09/04 error
   (unequal gaps rendered evenly) and it is fixed with a true numeric x axis.

2. THE CHART ARGUES THE OPPOSITE OF ITS OWN SOURCE. Titled "The Dollar Loses
   Ground" and sourced to the NY Fed, whose actual finding is that the aggregate
   decline is NOT a broad move out of dollars: "roughly equal numbers of
   countries increased and decreased their dollar holdings" in both sub periods,
   and the aggregate is driven by a handful of large holders (China and Russia
   in 2015 to 2019; China, Russia, Mexico and Morocco in 2019 to 2023). Among
   countries with complete data only Brazil and Hong Kong showed meaningful
   reductions. A falling average that hides a flat distribution is the 09/01
   September seasonality trap. The caveat is put ON the chart, not left to the
   caption, because the line alone tells a story the research contradicts.

matplotlib only; build with python3.13 on Mac.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

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

# NY Fed Liberty Street Economics, September 2, 2026. True years, true spacing.
YEARS = [2015, 2019, 2023, 2025]
SHARE = [64, 61, 59, 56]


def build():
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    ax.plot(YEARS, SHARE, color=CORAL, linewidth=3.2, zorder=4,
            solid_capstyle="round")
    ax.scatter(YEARS, SHARE, s=130, color=CORAL, edgecolor=CREAM,
               linewidth=2.5, zorder=5)

    for x, v in zip(YEARS, SHARE):
        ax.text(x, v + 0.42, f"{v}%", ha="center", va="bottom",
                fontsize=21, fontweight="bold", color=INK, zorder=6)

    # Per-segment pace. The whole point of using a real time axis.
    # The steep segment's label goes ABOVE its line and its explanatory note
    # BELOW, so no leader is needed. The first render used an arrow and it ran
    # straight through the "-1.50 pp/yr" text.
    for (x0, v0), (x1, v1) in zip(zip(YEARS, SHARE), zip(YEARS[1:], SHARE[1:])):
        pace = (v1 - v0) / (x1 - x0)
        steep = abs(pace) > 1.0
        # Steep label is nudged right as well as up: at +0.55 the plotted line
        # clipped the minus sign and the label read as "1.50" at full size.
        ax.text((x0 + x1) / 2 + (0.42 if steep else 0),
                (v0 + v1) / 2 + (0.95 if steep else -0.75),
                f"{pace:.2f} pp/yr", ha="center",
                va="bottom" if steep else "top",
                fontsize=12.5, fontweight="bold" if steep else "normal",
                color=DEEP if steep else MUTED, zorder=6)

    ax.text(
        2024.0, 55.5,
        "Same 3 point drop as 2015 to 2019,\nbut in half the time",
        fontsize=12, color=DEEP, ha="center", va="top",
        linespacing=1.5, zorder=7,
    )

    ax.set_xlim(2014.2, 2025.9)
    ax.set_xticks(YEARS)
    ax.set_xticklabels([str(y) for y in YEARS], fontsize=15, fontweight="bold")
    ax.set_ylim(53.4, 66.4)
    ax.set_yticks([54, 56, 58, 60, 62, 64])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.grid(axis="y", color=GRID, linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="both", length=0, labelsize=13, colors=SLATE)
    for lbl in ax.get_xticklabels():
        lbl.set_color(INK)

    fig.text(0.045, 0.945, "The Dollar's Reserve Share Fell 8 Points in a Decade",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888,
             "U.S. dollar share of global official foreign exchange reserves, plotted on a true time axis",
             fontsize=14.5, color=MUTED, ha="left", va="top")

    # The source's own conclusion, which the line by itself contradicts.
    fig.text(
        0.045, 0.128,
        "But the same research finds this is not the world leaving the dollar: roughly equal numbers of countries RAISED and lowered their\n"
        "dollar holdings, and the aggregate drop traces to a few large holders (China, Russia, and later Mexico and Morocco).",
        fontsize=11.5, color=DEEP, ha="left", va="bottom", linespacing=1.55,
    )
    fig.text(
        0.045, 0.045,
        "Source: Federal Reserve Bank of New York, Liberty Street Economics, “Are Central Banks Moving Out of Dollar Assets?”, September 2, 2026.\n"
        "2019 and 2023 are derived from the post's stated declines of 3 and 2 percentage points. Not the same series as IMF COFER allocated reserves.",
        fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5,
    )

    fig.subplots_adjust(left=0.075, right=0.965, top=0.815, bottom=0.265)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"dollarshare-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
