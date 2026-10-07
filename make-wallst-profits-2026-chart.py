#!/usr/bin/env python3
"""
make-wallst-profits-2026-chart.py  [outdir]

The 10/07/26 daily's Wall Street profits chart (Stocks section). Harv attached
the newsletter graphic "Wall Street Eyes a Record Year" (annual pretax profits
of NYSE member firms, 2020 to 2025 plus a projected 2026* bar of "$90B+",
"Source: NY State Comptroller, Oct. 2026"). Emits BOTH variants:

  wallst-profits-100726.png      plain HB monogram    -> RE email + Agent Hub
  wallst-profits-100726-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 10/07/26: every bar matched at the Comptroller (OSC), verbatim
=============================================================================
2020 to 2023, OSC press release of Oct. 2024 ("Wall Street's 2024 first half
profits ..."): "$50.9 billion in 2020 and $58.4 billion in 2021, before returning
to more typical levels in 2022 ($25.8 billion) and 2023 ($26.3 billion)."

2024 and 2025, OSC report "The Securities Industry in New York City", October
2026, Report 13-2027 (osc.ny.gov/files/reports/osdc/2026/pdf/
nyc-securities-industry-2026.pdf): "In 2024, profits grew to $49.9 billion, a 90
percent increase over the prior year" (49.9 / 1.90 = 26.3, consistent with the
2023 figure above) and "In 2025, industry profits soared to $65.1 billion, a
30.4 percent increase over 2024 ... surpassing the previous high of $61.4
billion in 2009."

2026: "Member firm profits for the first half of the year reached $45.9 billion,
an increase of 51.3 percent over the same period in 2025 and a record high for
any two-quarter period" and "If the growth rate in the first half continues
through the rest of the year, profits could soar into the range of $90 billion
in 2026." The supplied chart drew 2026 as one projected bar; ours splits it
into the $45.9 billion that is ACTUAL (first half) and the projected rest, so a
reader can see how much of the bar is a forecast.

Measure: pretax profits for broker/dealer operations of NYSE member firms
(nominal dollars). The report also notes the City's May forecast for 2026 was
$45.3 billion, already exceeded by the first half alone.

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
STAMP = "100726"

CREAM = "#fdf6e8"
INK = "#1f2933"
GREEN = "#2f855a"
CORAL = "#e2574c"
GOLD = "#c98a1b"
GRID = "#d8cdb8"
MUTED = "#8a8172"

PROFITS = [(2020, 50.9), (2021, 58.4), (2022, 25.8), (2023, 26.3), (2024, 49.9), (2025, 65.1)]
H1_2026 = 45.9
PACE_2026 = 90.0
PRIOR_RECORD_2009 = 61.4


def build():
    # internal consistency checks against the report's own percentages
    by = dict(PROFITS)
    assert abs((by[2025] / by[2024] - 1) * 100 - 30.4) < 0.2       # "a 30.4 percent increase"
    assert abs((by[2024] / by[2023] - 1) * 100 - 90) < 1          # "a 90 percent increase"
    assert max(by.values()) == by[2025] > PRIOR_RECORD_2009

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.13, 0.80, 0.66])
    ax.set_facecolor(CREAM)

    xs = list(range(len(PROFITS) + 1))
    w = 0.62
    for x, (yr, v) in zip(xs, PROFITS):
        col = GREEN if yr == 2025 else "#5b8f74"
        ax.bar(x, v, width=w, color=col, zorder=3)
        ax.text(x, v + 1.6, f"${v:.1f}B", fontsize=16, fontweight="bold", color=INK, ha="center",
                va="bottom", zorder=5)

    # 2026: actual first half (solid) + the projected rest (hatched, outlined)
    x26 = xs[-1]
    ax.bar(x26, H1_2026, width=w, color=GOLD, zorder=3)
    ax.bar(x26, PACE_2026 - H1_2026, bottom=H1_2026, width=w, facecolor=CREAM, edgecolor=GOLD,
           hatch="///", linewidth=2.0, zorder=3)
    ax.text(x26, PACE_2026 + 1.6, "$90B+", fontsize=19, fontweight="bold", color=GOLD, ha="center",
            va="bottom", zorder=5)
    ax.text(x26, H1_2026 / 2, f"${H1_2026:.1f}B\nfirst half,\nactual", fontsize=12, fontweight="bold",
            color="white", ha="center", va="center", linespacing=1.2, zorder=5)
    ax.text(x26, H1_2026 + (PACE_2026 - H1_2026) / 2, "if the\npace\nholds", fontsize=11.5,
            color=INK, ha="center", va="center", linespacing=1.15, zorder=5,
            bbox=dict(boxstyle="round,pad=0.25", facecolor=CREAM, edgecolor="none"))

    # the old record, so "record" has a reference
    # drawn only over 2022 to 2025, clear of the 2020 and 2021 value labels
    ax.hlines(PRIOR_RECORD_2009, 1.62, 5.0, color=MUTED, lw=1.3, ls=(0, (6, 4)), zorder=2)
    ax.text(1.7, PRIOR_RECORD_2009 + 1.2, "Previous record: $61.4B in 2009", fontsize=11.5, color=MUTED,
            ha="left", va="bottom", zorder=4)

    ax.set_xlim(-0.6, len(xs) - 0.4)
    ax.set_ylim(0, 100)
    ax.set_xticks(xs)
    ax.set_xticklabels([str(y) for y, _ in PROFITS] + ["2026"], fontsize=14, fontweight="bold", color=INK)
    ax.get_xticklabels()[-1].set_color(GOLD)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(["$0", "$25B", "$50B", "$75B", "$100B"], fontsize=11, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.035, 0.955, "Wall Street Is on Pace for a Record Year", fontsize=25, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.900, "Annual pretax profits of NYSE member firms (broker and dealer operations)",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.030,
             "Source: Office of the New York State Comptroller, securities industry reports (Oct. 2024 and "
             "Oct. 2026). 2026 projection is the Comptroller's.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"wallst-profits-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
