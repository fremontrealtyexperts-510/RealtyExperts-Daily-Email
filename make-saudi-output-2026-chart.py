#!/usr/bin/env python3
"""
make-saudi-output-2026-chart.py  [outdir]

The 10/14/26 daily's oil chart. Harv attached the newsletter graphic "Saudi Oil
Output Bounces Back" (Saudi crude production in 2026, million b/d: Jan 10.1,
Feb 10.9, Mar 7.0, Apr 6.3, May 6.6, Jun 7.1, Jul 8.1, Aug 6.2, Sep 8.37,
"Iran war begins" between Feb and Mar; "Source: OPEC Monthly Oil Market Reports
(Saudi-reported production), JODI"). Emits BOTH:

  saudi-output-101426.png      plain HB monogram    -> RE email + Agent Hub
  saudi-output-101426-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 10/14/26 (opec.org PDFs answer 403 to scripts; reports via press)
=============================================================================
Basis: what Saudi Arabia itself reported to OPEC ("direct communication").
* Sep 8.372, Aug 6.238: "Crude Oil Production in Saudi Arabia increased to 8372
  BBL/D/1K in September from 6238 BBL/D/1K in August of 2026" (Trading
  Economics); Times Kuwait: "Riyadh informed OPEC that its output had reached
  8.372 million bpd, compared with 6.238 million bpd in August". August was
  reported as the lowest since 1990.
* Jul 8.2, Jun 7.1: WorldOil / Bloomberg, Aug. 12, 2026: "The kingdom told the
  group it pumped 8.2 MMbpd of crude in July, up from 7.1 MMbpd in the previous
  month". The graphic's 8.1 for July does NOT match the figure as reported, and
  no revision was found, so the chart uses 8.2.
* Apr 6.3: Enterprise, May 14, 2026: "The Kingdom reported an output of a
  little over 6.3 mn bbl / d last month, according to Opec's monthly report",
  down 651k from March, "the lowest monthly output in 36 years".
* Mar 6.967, Feb 10.882: OPEC data via Trading Economics' April item.
* Jan 10.086: OPEC's February report via SHANA (rounds to the graphic's 10.1).
* May: NOT FOUND on the Saudi reported basis. The 6.912 in press coverage of the
  June report is OPEC's secondary sources estimate, a different measure, so the
  graphic's 6.6 is left out and the line is dotted across May.
* War marker: Kpler via AFP, Iran "was attacked by the United States and Israel
  on February 28". Labeled neutrally.

matplotlib; build with python3.13 on Mac.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "101426"

MONTHS = ["Jan.", "Feb.", "March", "April", "May", "June", "July", "Aug.", "Sept."]
# million b/d, Saudi reported to OPEC; None = not found on this basis
VALS = [10.086, 10.882, 6.967, 6.316, None, 7.1, 8.2, 6.238, 8.372]

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e05a47"
DEEP = "#b8432f"
ORANGE = "#d9822b"
ORANGE_BG = "#f6e3cc"
GRID = "#d8cdb8"
MUTED = "#8a8172"


def build():
    assert round((VALS[8] / VALS[7] - 1) * 100) == 34          # "jumped by a third"
    assert min(v for v in VALS if v) == VALS[7]                  # August is the low

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.06, 0.13, 0.88, 0.66])
    ax.set_facecolor(CREAM)

    pts = [(i, v) for i, v in enumerate(VALS) if v is not None]
    # solid segments between consecutive known months, dotted across the May gap
    for (i0, v0), (i1, v1) in zip(pts, pts[1:]):
        ls = "-" if i1 - i0 == 1 else (0, (2, 2.5))
        ax.plot([i0, i1], [v0, v1], color=ORANGE, lw=3.2, ls=ls, solid_capstyle="round", zorder=4)
    xs = [i for i, _ in pts]
    ys = [v for _, v in pts]
    ax.fill_between(xs, 5.0, ys, color=ORANGE_BG, lw=0, zorder=1)
    ax.scatter(xs[:-1], ys[:-1], s=70, color=ORANGE, edgecolor=CREAM, linewidth=1.8, zorder=5)

    above = {0, 1, 5, 6}
    for i, v in pts[:-1]:
        lab = f"{v:.1f}"
        if i in above:
            ax.annotate(lab, xy=(i, v), xytext=(0, 13), textcoords="offset points", fontsize=16,
                        fontweight="bold", color=INK, ha="center", va="bottom")
        else:
            ax.annotate(lab, xy=(i, v), xytext=(0, -14), textcoords="offset points", fontsize=16,
                        fontweight="bold", color=INK, ha="center", va="top")
    ax.annotate("lowest since 1990", xy=(7, VALS[7]), xytext=(0, -38), textcoords="offset points",
                fontsize=11.5, color=DEEP, ha="center", va="top")
    ax.text(4, 6.15, "May: Saudi\nfigure not\npublished", fontsize=11, color=MUTED, ha="center",
            va="top", linespacing=1.2)

    ax.scatter([8], [VALS[8]], s=150, color=DEEP, edgecolor=CREAM, linewidth=2, zorder=6)
    ax.annotate("8.37M, up a third", xy=(8, VALS[8]), xytext=(0, 16), textcoords="offset points", fontsize=16,
                fontweight="bold", color="white", ha="right", va="bottom", zorder=7,
                bbox=dict(boxstyle="round,pad=0.35", facecolor=DEEP, edgecolor="none"))

    ax.axvline(1.93, color=MUTED, lw=1.4, ls=(0, (4, 3)), zorder=2)
    ax.text(2.0, 11.55, "Conflict with Iran begins, Feb. 28", fontsize=12.5, color=MUTED,
            ha="left", va="center")

    ax.set_xticks(range(9))
    ax.set_xticklabels(MONTHS, fontsize=13, color=MUTED)
    ax.set_xlim(-0.45, 8.45)
    ax.set_ylim(5.0, 11.9)
    ax.set_yticks([6, 8, 10])
    ax.set_yticklabels(["6M", "8M", "10M"], fontsize=12, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.035, 0.955, "Saudi Oil Output Bounces Back", fontsize=26, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.895, "Crude production Saudi Arabia reported to OPEC, 2026, million barrels a day.",
             fontsize=13.2, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035, "Source: OPEC Monthly Oil Market Reports (production reported by Saudi Arabia), "
             "as published Feb. to Oct. 2026; May not available on that basis.", fontsize=10.2,
             color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"saudi-output-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
