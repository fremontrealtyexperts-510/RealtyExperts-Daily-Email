#!/usr/bin/env python3
"""
make-labordaygas-chart.py  [outdir]

Recreates the Market Briefs graphic "Most Expensive Labor Day At The Pump Ever"
for the 09/07/26 (Labor Day) edition. Emits BOTH brand variants:

  labordaygas-090726.png      plain HB monogram      -> RE email + Agent Hub
  labordaygas-090726-hb.png   monogram + wordmark    -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/07/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

The supplied graphic's FIVE VALUES ALL VERIFIED EXACTLY against the primary
source, the GasBuddy press release of September 1, 2026,
https://www.gasbuddy.com/newsroom/pressrelease/2026/09/01/1173 , which prints
its own "5 Years of Average Labor Day Gas Prices" list:

    2022 $3.79   2023 $3.77   2024 $3.29   2025 $3.16   2026 $4.03 (projected)

Cross check: the release says 2026 is "87 cents higher than in 2025", and
4.03 - 3.16 = 0.87 exactly. The series is internally consistent.

TWO THINGS THE SUPPLIED GRAPHIC GETS WRONG, both fixed here
------------------------------------------------------------------
1. THE CHART DOES NOT SHOW ITS OWN HEADLINE. It is titled "Most Expensive
   Labor Day At The Pump Ever" but plots only 2022 to 2026, and the record it
   claims to break is NOT in that window. GasBuddy's release names the prior
   record explicitly: $3.83/gal in 2012. In the supplied graphic the tallest
   historical bar is 2022 at $3.79, so a reader can only take "ever" on faith.
   We draw the 2012 record as a labeled reference line, so the claim is VISIBLE
   rather than merely asserted.

   ⚠️ Deliberately a LINE and not a sixth bar. 2012 to 2022 is a ten year gap;
   drawing it as an adjacent bar would render an uneven time axis evenly, which
   is the 09/04 Anthropic-graphic error (unequal gaps drawn evenly). A reference
   line carries the level without implying adjacency.

2. THE PROJECTION HAS ALREADY BEEN OVERTAKEN. $4.03 is a FORECAST published
   Sept 1, six days before the holiday it forecasts. Labor Day is today, so the
   actual is knowable: AAA's national average this morning is $4.1505, twelve
   cents ABOVE the projection. Same pattern as the 08/20 Moderna and BTC
   endpoints that were stale by build time. We keep the GasBuddy bar (it is the
   graphic's series) and annotate the realized AAA print beside it.

   ⚠️ SOURCE SEPARATION IS DELIBERATE. AAA and GasBuddy survey differently and
   do not agree year to year: AAA puts Labor Day 2025 at $3.19 and the 2012
   record at $3.82, against GasBuddy's $3.16 and $3.83. Those are methodology
   gaps, not errors. So the BARS AND THE REFERENCE LINE ARE 100% GASBUDDY, and
   the single AAA number is drawn in a different colour, labeled "AAA", and
   sourced separately in the footer. Never let the two series share a mark.
   This is the same discipline the Brent lock exists to enforce (two instruments
   wearing one name, reference-brent-locked-to-bz-f-futures.md).

Local note carried in the report copy, not on this chart: California's average
today is $5.8602 (AAA), $1.71 above the national number. Charting it would need
a y-axis to $6 and would flatten the national series this chart is about.

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
STAMP = "090726"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
SLATE = "#8a9aa8"
GRID = "#d8cdb8"
MUTED = "#8a8172"
GREEN = "#2f8f5b"

# GasBuddy press release, September 1, 2026. Single source for every bar.
YEARS = ["2022", "2023", "2024", "2025", "2026"]
PRICES = [3.79, 3.77, 3.29, 3.16, 4.03]
PROJECTED = 4  # index of the forecast bar

GB_RECORD_2012 = 3.83     # GasBuddy: previous record, 2012
AAA_ACTUAL = 4.1505       # AAA national average, 9/7/26. DIFFERENT SOURCE.


def build():
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    xs = range(len(YEARS))
    for i, (x, v) in enumerate(zip(xs, PRICES)):
        is_proj = i == PROJECTED
        ax.bar(
            x, v, width=0.62,
            color=CORAL if is_proj else SLATE,
            edgecolor=DEEP if is_proj else "none",
            linewidth=1.6 if is_proj else 0,
            hatch="///" if is_proj else None,
            zorder=3,
        )
        # The projected bar carries its value INSIDE. Above it belongs to the
        # AAA marker, and stacking both there collided on the first render.
        if is_proj:
            ax.text(x, v - 0.10, f"${v:.2f}", ha="center", va="top",
                    fontsize=20, fontweight="bold", color="#ffffff", zorder=6)
        else:
            ax.text(x, v + 0.06, f"${v:.2f}", ha="center", va="bottom",
                    fontsize=17, fontweight="bold", color=INK, zorder=5)

    # 2012 record: the level the headline claims to beat, absent from the original.
    # Labeled at the RIGHT margin, the only band clear of every bar value label.
    # Drawn with plot(), not axhline(), so it STOPS short of its own label
    # instead of running behind the text.
    ax.plot([-0.50, len(YEARS) - 0.56], [GB_RECORD_2012, GB_RECORD_2012],
            color=MUTED, linestyle=(0, (6, 4)), linewidth=1.7, zorder=2)
    ax.text(
        len(YEARS) - 0.46, GB_RECORD_2012,
        "  Previous record\n  $3.83 in 2012",
        fontsize=12.5, color=MUTED, fontweight="bold",
        ha="left", va="center", linespacing=1.5, zorder=5,
    )

    # AAA's realized print. Separate source, so a separate colour and its own label.
    ax.plot([PROJECTED - 0.36, PROJECTED + 0.36], [AAA_ACTUAL, AAA_ACTUAL],
            color=GREEN, linewidth=3.0, solid_capstyle="butt", zorder=6)
    ax.text(
        PROJECTED, AAA_ACTUAL + 0.14,
        "Actual today: $4.15\n(AAA national average)",
        fontsize=12.5, color=GREEN, fontweight="bold",
        ha="center", va="bottom", linespacing=1.45, zorder=7,
    )

    ax.set_xticks(list(xs))
    ax.set_xticklabels(
        [y if i != PROJECTED else f"{y}\nprojected" for i, y in enumerate(YEARS)],
        fontsize=15, fontweight="bold",
    )
    ax.set_xlim(-0.62, len(YEARS) + 0.62)  # right margin holds the record label
    ax.set_ylim(0, 4.95)
    ax.set_yticks([0, 1, 2, 3, 4])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:.0f}"))
    ax.grid(axis="y", color=GRID, linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="both", length=0, labelsize=13, colors=SLATE)
    for lbl in ax.get_xticklabels():
        lbl.set_color(INK)

    fig.text(0.045, 0.945, "The Priciest Labor Day at the Pump on Record",
             fontsize=26, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888,
             "U.S. average price for a gallon of regular gasoline on Labor Day",
             fontsize=14.5, color=MUTED, ha="left", va="top")

    fig.text(
        0.045, 0.045,
        "Bars and the 2012 record line: GasBuddy Labor Day forecast, September 1, 2026. The 2026 bar is GasBuddy's projection.\n"
        "Actual today: AAA national average, September 7, 2026. AAA and GasBuddy survey differently and are shown separately.",
        fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5,
    )

    fig.subplots_adjust(left=0.075, right=0.965, top=0.815, bottom=0.185)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"labordaygas-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
