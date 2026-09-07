#!/usr/bin/env python3
"""
make-augpayrolls-chart.py  [outdir]

Recreates the Market Briefs graphic "August Hiring Tripled What Wall Street
Expected" for the 09/07/26 (Labor Day) edition. Emits BOTH brand variants:

  augpayrolls-090726.png      plain HB monogram    -> RE email + Agent Hub
  augpayrolls-090726-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/07/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

Re-pulled from the BLS public API v1 (keyless POST, no key required):
    POST https://api.bls.gov/publicAPI/v1/timeseries/data/
    CES0000000001, total nonfarm employment, seasonally adjusted, levels in
    thousands. Month over month change computed from the levels, not traced
    off the supplied image.

    Jun 2026  158,892 - 158,861 = +31K   matches the graphic
    Jul 2026  158,913 - 158,892 = +21K   matches the graphic
    Aug 2026  159,075 - 158,913 = +162K  matches the graphic

ALL THREE BLS BARS REPRODUCE EXACTLY. The fourth bar, the +53K forecast, is
NOT a BLS series and cannot be diffed against one: it is an economist survey
consensus. Market Briefs prints 53,000 and the supplied graphic prints +53K,
and the 09/05/26 edition verified the same figure, so 53K is what we plot. It
is labeled "Wall Street forecast" and drawn hollow, never as a measured value.

⚠️ ONE VINTAGE, STATED. June and July are the CURRENTLY REVISED figures, which
is what BLS serves today and what the graphic used. Some write ups of this same
report quote July at +23K, an earlier print. Mixing an original print with a
revised one inside a single chart is the 09/03 ADP error and the 08/27 seven
vintage error. Every bar here comes from one API pull on 09/07/26.

CONTEXT VERIFIED BUT DELIBERATELY NOT CHARTED
------------------------------------------------------------------
  Unemployment rate held at 4.1% in August (BLS LNS14000000, Jul 4.1, Aug 4.1).
  Confirms the Market Briefs line "unemployment held steady at 4.1%".

  Fed hike odds: 49.4% the day BEFORE the report, 58.4% AFTER (CME FedWatch,
  verified 09/05/26 from the source transcript). Market Briefs today prints
  "60%". These are market implied probabilities from fed funds futures, NOT a
  forecast and NOT a Fed statement, so the copy says so. ⚠️ Do NOT reach for
  the Forbes 66% of Aug 31 to describe this move: that is a different date and
  it produced a wrong-direction claim on 09/05 that nearly shipped.

The headline word "tripled": 162 / 53 = 3.06x, so "three times the forecast" is
accurate and we keep it.

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
STAMP = "090726"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
SLATE = "#8a9aa8"
GRID = "#d8cdb8"
MUTED = "#8a8172"

# (label, value in thousands, kind)
ROWS = [
    ("June",            31,  "actual"),
    ("July",            21,  "actual"),
    ("Aug. forecast",   53,  "forecast"),
    ("Aug. actual",    162,  "headline"),
]


def build():
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    # invert_yaxis() below puts y=0 at the top, so plain ascending order keeps
    # ROWS reading top to bottom as written: June, July, forecast, actual.
    ys = list(range(len(ROWS)))

    for y, (label, val, kind) in zip(ys, ROWS):
        if kind == "forecast":
            ax.barh(y, val, height=0.58, facecolor="none", edgecolor=CORAL,
                    linewidth=2.0, linestyle=(0, (5, 3)), zorder=3)
            vcolor, vsize = CORAL, 17
        elif kind == "headline":
            ax.barh(y, val, height=0.58, color=CORAL, zorder=3)
            vcolor, vsize = DEEP, 22
        else:
            ax.barh(y, val, height=0.58, color=SLATE, zorder=3)
            vcolor, vsize = INK, 17

        ax.text(val + 3.2, y, f"+{val}K", ha="left", va="center",
                fontsize=vsize, fontweight="bold", color=vcolor, zorder=5)

    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in ROWS], fontsize=15.5, fontweight="bold")
    for lbl, (_, _, kind) in zip(ax.get_yticklabels(), ROWS):
        lbl.set_color(CORAL if kind == "forecast" else INK)

    ax.set_xlim(0, 190)
    ax.set_xticks([0, 50, 100, 150])
    ax.set_xticklabels(["0", "50K", "100K", "150K"])
    ax.grid(axis="x", color=GRID, linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="both", length=0, labelsize=13, colors=SLATE)
    ax.invert_yaxis()

    fig.text(0.045, 0.945, "August Hiring Came in Triple the Forecast",
             fontsize=26, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888,
             "Change in U.S. nonfarm payrolls, seasonally adjusted",
             fontsize=14.5, color=MUTED, ha="left", va="top")

    fig.text(
        0.045, 0.045,
        "June, July and August: U.S. Bureau of Labor Statistics, August 2026 Employment Situation, released September 4, 2026.\n"
        "June and July are the currently revised figures. The forecast bar is the economist survey consensus, not a BLS series.",
        fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5,
    )

    fig.subplots_adjust(left=0.155, right=0.965, top=0.815, bottom=0.185)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"augpayrolls-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
