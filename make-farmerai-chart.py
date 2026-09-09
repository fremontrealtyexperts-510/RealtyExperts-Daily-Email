#!/usr/bin/env python3
"""
make-farmerai-chart.py  [outdir]

Recreates the Market Briefs graphic "Farmers Try AI, Few Pay For It" for the
09/09/26 edition. Emits BOTH brand variants:

  farmerai-090926.png      plain monogram   -> RE email + Agent Hub
  farmerai-090926-hb.png   + wordmark       -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/09/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

Source is McKinsey's Global Farmer Insights 2026, published Sept 8, 2026.
All three plotted values are RIGHT:

  17%  use generative AI in farm-related tasks
   6%  treat generative AI chatbots or AI search as a trusted purchasing input
   4%  pay for an AI tool

THREE CORRECTIONS TO THE SUPPLIED GRAPHIC
------------------------------------------------------------------
1. **The field window is wrong.** The original footer says "fielded April-July
   2026". Two independent write ups of the same report state verbatim that the
   survey "gathered responses from 5,500 farmers across 10 countries **between
   April and June**". Corrected here.

2. **The three bars are NOT a funnel, but descending bars read as one.** 17% to
   6% to 4% looks like use, then trust, then pay, each a subset of the last. It
   is not: "trust AI for buying decisions" is a separate survey question, not a
   step between using and paying. Meanwhile 4% "pay for an AI tool" IS a genuine
   subset of the 17% who use it, so the original draws the same people twice as
   two independent bars.

   Fixed by drawing the ONE real subset relationship as a stacked bar: of the
   17% who use generative AI, **12% use only free versions and 4% pay**. That
   is McKinsey's own split, and it delivers the headline ("few pay for it") by
   SHOWING it instead of asking the reader to infer it from two bars.
   ⚠️ 12 + 4 = 16, not 17. McKinsey attributes the gap to rounding, and the
   footnote says so rather than silently fudging a segment to make it total.

3. **6% is the fastest growing input, which the bar alone hides.** It is up
   from **1% in 2024**, the largest proportional gain of any purchasing input
   in the survey, though still a small base. A lone short bar reads as "nobody
   trusts AI"; the truth is "almost nobody did, and that is changing fastest".
   Same class as the 09/01 seasonality chart, where the level was true and the
   framing was the problem. Scale markers for the two inputs farmers DO trust
   (web search 18%, social media 9%) are drawn so 6% can be read against
   something.

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
STAMP = "090926"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
GREEN = "#2f8f5b"
PALEGREEN = "#a8d5bd"
SLATE = "#8a9aa8"
GRID = "#d8cdb8"
MUTED = "#8a8172"

FREE, PAID = 12, 4          # of the 17% who use generative AI
TRUST, TRUST_2024 = 6, 1    # trusted purchasing input
WEB, SOCIAL = 18, 9         # context: inputs farmers already trust


def build():
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    y_use, y_trust = 1.0, 0.0

    # Row 1: the one real subset relationship, drawn as a stack.
    ax.barh(y_use, FREE, height=0.42, color=PALEGREEN, zorder=3)
    ax.barh(y_use, PAID, height=0.42, left=FREE, color=GREEN, zorder=3)
    ax.text(FREE / 2, y_use, "12% free", ha="center", va="center",
            fontsize=13.5, fontweight="bold", color=INK, zorder=6)
    ax.text(FREE + PAID / 2, y_use, "4%\npaid", ha="center", va="center",
            fontsize=11.5, fontweight="bold", color="#ffffff",
            linespacing=1.25, zorder=6)
    ax.text(FREE + PAID + 0.6, y_use, "17%", ha="left", va="center",
            fontsize=22, fontweight="bold", color=INK, zorder=6)

    # Row 2: a separate question, with its own 2024 baseline.
    ax.barh(y_trust, TRUST, height=0.42, color=GREEN, zorder=3)
    ax.text(TRUST + 0.6, y_trust, "6%", ha="left", va="center",
            fontsize=22, fontweight="bold", color=INK, zorder=6)
    ax.plot([TRUST_2024, TRUST_2024], [y_trust - 0.27, y_trust + 0.27],
            color=DEEP, linewidth=2.4, zorder=7)
    ax.text(TRUST_2024 + 0.35, y_trust - 0.35, "1% in 2024",
            ha="left", va="top", fontsize=11.5, fontweight="bold", color=DEEP, zorder=7)

    # Scale markers: what farmers actually trust.
    for val, lab in ((WEB, "Web search 18%"), (SOCIAL, "Social media 9%")):
        ax.plot([val, val], [y_trust - 0.46, y_use + 0.46], color=MUTED,
                linestyle=(0, (3, 4)), linewidth=1.3, zorder=1)
        ax.text(val, y_use + 0.52, lab, ha="center", va="bottom",
                fontsize=11, color=MUTED, zorder=5)

    ax.set_yticks([y_use, y_trust])
    ax.set_yticklabels(["Use generative AI", "Trust AI for\nbuying decisions"],
                       fontsize=14.5, fontweight="bold")
    ax.set_ylim(-0.72, 1.86)
    ax.set_xlim(0, 22)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.grid(axis="x", color=GRID, linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="both", length=0, labelsize=13, colors=SLATE)
    for lbl in ax.get_yticklabels():   # after tick_params, which resets colours
        lbl.set_color(INK)

    fig.text(0.045, 0.945, "Farmers Are Trying AI, Mostly for Free",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888,
             "Share of farmers worldwide, 5,500 growers surveyed across 10 countries",
             fontsize=14, color=MUTED, ha="left", va="top")

    fig.text(
        0.045, 0.126,
        "Trust in AI for purchasing is the fastest growing input in the survey, up from 1% in 2024, but it starts from a very small base.\n"
        "Note the two rows answer different questions: paying is a subset of using, whereas trusting for purchases is asked separately.",
        fontsize=11.5, color=DEEP, ha="left", va="bottom", linespacing=1.55,
    )
    fig.text(
        0.045, 0.045,
        "Source: McKinsey Global Farmer Insights 2026, published September 8, 2026, fielded April to June 2026.\n"
        "The free and paid shares are McKinsey's own split and sum to 16% against a 17% total; the difference is rounding in the source.",
        fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5,
    )

    fig.subplots_adjust(left=0.185, right=0.965, top=0.815, bottom=0.265)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"farmerai-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
