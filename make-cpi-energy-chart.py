#!/usr/bin/env python3
"""
make-cpi-energy-chart.py  [outdir]

Recreates the newsletter graphic "Energy Is Doing The Damage, Not Everything
Else" for the 09/14/26 edition. (make-cpi-chart.py is an older, different
chart; this is a new file on purpose so neither clobbers the other.) Emits
BOTH variants:

  cpi-energy-091426.png      plain monogram    -> RE email + Agent Hub
  cpi-energy-091426-hb.png   + wordmark        -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/14/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

The supplied graphic: 12 month % change, Jan to Aug 2026.
  Headline 2.4 2.4 3.3 3.8 4.2 3.5 3.4 3.4
  Core     2.5 2.5 2.6 2.8 2.9 2.6 2.5 2.4
Source BLS, CPI report released Sept. 11, 2026.

ALL SIXTEEN POINTS ARE RIGHT. BLS API (keyless v1), unadjusted index levels,
2026 month over same 2025 month:
  CUUR0000SA0     2.386 2.414 3.256 3.811 4.249 3.531 3.365 3.397
  CUUR0000SA0L1E  2.504 2.457 2.595 2.750 2.851 2.594 2.478 2.446
(October 2025 is missing from every CPI series, the shutdown gap; it does not
touch any Jan to Aug 2026 comparison.) The release (8:30 a.m. ET Friday,
September 11, 2026) prints 3.4 and 2.4 verbatim.

Energy CUUR0000SA0E is up 16.3% on the year (peak 23.5% in May); gasoline
27.4%; fuel oil 52.0%; shelter 3.0%.

FRAMING. The headline is true of the 12 month lines: the gap between them is
energy, and core is at its lowest reading of the year. What the original
leaves out: core is still above 2%, and on the MONTH core rose 0.3% (SA) in
August, its biggest monthly gain since April's 0.4%. The Fed's 2% goal is for
PCE, not CPI, so it is labeled as a yardstick. The rebuild shades the gap,
names it, and adds the August detail.

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
STAMP = "091426"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
TEAL = "#2f7d6d"
ORANGE = "#d9822b"
DEEP = "#b8433a"
SLATE = "#8a9aa8"
GRID = "#e6dcc8"
MUTED = "#8a8172"

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG"]
HEADLINE = [2.386, 2.414, 3.256, 3.811, 4.249, 3.531, 3.365, 3.397]
CORE = [2.504, 2.457, 2.595, 2.750, 2.851, 2.594, 2.478, 2.446]


def build():
    assert [f"{v:.1f}" for v in HEADLINE] == ["2.4", "2.4", "3.3", "3.8", "4.2", "3.5", "3.4", "3.4"]
    assert [f"{v:.1f}" for v in CORE][:3] + [f"{v:.1f}" for v in CORE][4:] == \
        ["2.5", "2.5", "2.6", "2.9", "2.6", "2.5", "2.4"]

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    xs = list(range(len(MONTHS)))
    ax.fill_between(xs, CORE, HEADLINE, where=[h >= c for h, c in zip(HEADLINE, CORE)],
                    interpolate=True, color=ORANGE, alpha=0.16, zorder=1, linewidth=0)
    ax.plot(xs, HEADLINE, color=CORAL, linewidth=3.6, zorder=3, solid_capstyle="round")
    ax.plot(xs, CORE, color=TEAL, linewidth=3.6, zorder=3, solid_capstyle="round")
    ax.scatter([7, 7], [HEADLINE[-1], CORE[-1]], s=70, color=[CORAL, TEAL], zorder=4)

    # Fed yardstick
    ax.axhline(2.0, color=SLATE, linewidth=1.3, linestyle=(0, (6, 5)), zorder=2)
    ax.text(0.0, 2.05, "FED'S 2% GOAL (a PCE target, shown for scale)",
            fontsize=10.5, color=MUTED, ha="left", va="bottom", fontweight="bold")

    # Endpoint labels
    for y, col in ((HEADLINE[-1], CORAL), (CORE[-1], TEAL)):
        ax.text(7.28, y, f"{y:.1f}%", fontsize=19, fontweight="bold", color="white",
                ha="left", va="center",
                bbox=dict(boxstyle="round,pad=0.35", fc=col, ec="none"))

    # Peak
    ax.annotate("May peak 4.2%", xy=(4, HEADLINE[4]), xytext=(4.35, 4.42),
                fontsize=12, color=CORAL, fontweight="bold", ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=CORAL, lw=1.1))

    # Name the gap
    ax.text(3.62, 3.33, "The gap is energy:\nup 16.3% in a year", fontsize=12.5,
            color="#9a5a1c", ha="center", va="center", linespacing=1.4, fontweight="bold")

    # August detail
    ax.text(0.0, 4.47,
            "August alone (seasonally adjusted)\n"
            "All items +0.4%    Core +0.3%\n"
            "Energy +2.1%    Gasoline +3.9%\n"
            "Core's 0.3% was its biggest\nmonthly rise since April.",
            fontsize=11.5, color=INK, ha="left", va="top", linespacing=1.5,
            bbox=dict(boxstyle="round,pad=0.6", fc="#f6e7cf", ec="#d8cdb8"))

    ax.set_xlim(-0.25, 7.95)
    ax.set_ylim(1.8, 4.6)
    ax.set_xticks(xs)
    ax.set_xticklabels(MONTHS, fontsize=12.5, fontweight="bold", color=MUTED)
    ax.set_yticks([2.0, 2.5, 3.0, 3.5, 4.0, 4.5])
    ax.set_yticklabels(["2.0%", "2.5%", "3.0%", "3.5%", "4.0%", "4.5%"], fontsize=12, color=MUTED)
    ax.tick_params(length=0)
    ax.yaxis.grid(True, color=GRID, linewidth=1, zorder=0)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)

    fig.text(0.045, 0.945, "Energy Is Driving Inflation. Core Is Still Above 2%.",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888, "U.S. consumer prices, 12 month % change, January to August 2026",
             fontsize=14, color=MUTED, ha="left", va="top")
    # legend
    fig.text(0.045, 0.838, "▬", fontsize=16, color=CORAL, ha="left", va="center")
    fig.text(0.068, 0.838, "Headline CPI", fontsize=12.5, color=INK, ha="left", va="center", fontweight="bold")
    fig.text(0.185, 0.838, "▬", fontsize=16, color=TEAL, ha="left", va="center")
    fig.text(0.208, 0.838, "Core CPI (excluding food and energy)", fontsize=12.5, color=INK,
             ha="left", va="center", fontweight="bold")

    fig.text(
        0.045, 0.098,
        "Core is at its lowest reading of the year, but still above 2%, and the Fed meets Wednesday with a hike priced in.",
        fontsize=11.5, color=DEEP, ha="left", va="bottom",
    )
    fig.text(
        0.045, 0.030,
        "Source: U.S. Bureau of Labor Statistics, Consumer Price Index for August 2026, released September 11, 2026. 12 month changes are\n"
        "unadjusted; August monthly changes are seasonally adjusted. The Fed's 2% target applies to PCE inflation and is shown for scale.",
        fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5,
    )

    fig.subplots_adjust(left=0.07, right=0.975, top=0.80, bottom=0.21)
    return fig


if __name__ == "__main__":
    fig = build()
    save_pair(fig, os.path.join(OUTDIR, f"cpi-energy-{STAMP}.png"),
              logo=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hb-logo-mark.png"))
