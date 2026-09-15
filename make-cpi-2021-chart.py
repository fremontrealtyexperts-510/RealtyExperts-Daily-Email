#!/usr/bin/env python3
"""
make-cpi-2021-chart.py  [outdir]

Recreates the CNBC chart "U.S. consumer price index, year-over-year % change,
Jan. 2021 to Aug. 2026" (Gabriel Cortes / CNBC) shown in the ClearValue Tax
video, for the 09/15/26 edition. (make-cpi-chart.py and make-cpi-energy-chart.py
are different charts.) Emits BOTH variants:

  cpi-2021-091526.png      plain monogram    -> RE email + Agent Hub
  cpi-2021-091526-hb.png   + wordmark        -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/15/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

BLS API (keyless v1), CUUR0000SA0 and CUUR0000SA0L1E, unadjusted, each month
over the same month a year earlier, Jan 2021 to Aug 2026. The CNBC chart's
visible anchors all check: all items peak 9.06% June 2022 (~9 on the chart),
core peak 6.63% Sept 2022, endpoints 3.4% and 2.4%.

October 2025 is MISSING from every CPI series (the shutdown gap; BLS returns
"-"). CNBC draws a continuous line through it; this rebuild breaks the line
there and labels the gap.

FRAMING. The video says inflation is "reaccelerating"; that is true of the
headline (2.4% in January to 4.2% in May, 3.4% now) and not of core, which at
2.446% is its lowest since March 2021 (1.65%). Fed 2% goal is a PCE target,
drawn as a yardstick.

matplotlib only; build with python3.13 on Mac.
"""
import os
import sys
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "091526"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
TEAL = "#2f7d6d"
SLATE = "#8a9aa8"
DEEP = "#b8433a"
GRID = "#e6dcc8"
MUTED = "#8a8172"

ALL = {"2021-01":1.4,"2021-02":1.676,"2021-03":2.62,"2021-04":4.16,"2021-05":4.993,"2021-06":5.391,"2021-07":5.365,"2021-08":5.251,"2021-09":5.39,"2021-10":6.222,"2021-11":6.809,"2021-12":7.036,"2022-01":7.48,"2022-02":7.871,"2022-03":8.542,"2022-04":8.259,"2022-05":8.582,"2022-06":9.06,"2022-07":8.525,"2022-08":8.263,"2022-09":8.202,"2022-10":7.745,"2022-11":7.11,"2022-12":6.454,"2023-01":6.41,"2023-02":6.036,"2023-03":4.985,"2023-04":4.93,"2023-05":4.048,"2023-06":2.969,"2023-07":3.178,"2023-08":3.665,"2023-09":3.7,"2023-10":3.241,"2023-11":3.137,"2023-12":3.352,"2024-01":3.091,"2024-02":3.153,"2024-03":3.477,"2024-04":3.357,"2024-05":3.269,"2024-06":2.971,"2024-07":2.895,"2024-08":2.531,"2024-09":2.441,"2024-10":2.598,"2024-11":2.749,"2024-12":2.888,"2025-01":3.0,"2025-02":2.822,"2025-03":2.391,"2025-04":2.311,"2025-05":2.355,"2025-06":2.669,"2025-07":2.705,"2025-08":2.916,"2025-09":3.013,"2025-11":2.735,"2025-12":2.677,"2026-01":2.386,"2026-02":2.414,"2026-03":3.256,"2026-04":3.811,"2026-05":4.249,"2026-06":3.531,"2026-07":3.365,"2026-08":3.397}
CORE = {"2021-01":1.41,"2021-02":1.283,"2021-03":1.646,"2021-04":2.961,"2021-05":3.798,"2021-06":4.475,"2021-07":4.275,"2021-08":4.0,"2021-09":4.025,"2021-10":4.563,"2021-11":4.929,"2021-12":5.453,"2022-01":6.021,"2022-02":6.414,"2022-03":6.474,"2022-04":6.161,"2022-05":6.022,"2022-06":5.917,"2022-07":5.911,"2022-08":6.322,"2022-09":6.631,"2022-10":6.284,"2022-11":5.958,"2022-12":5.708,"2023-01":5.583,"2023-02":5.538,"2023-03":5.59,"2023-04":5.519,"2023-05":5.33,"2023-06":4.829,"2023-07":4.653,"2023-08":4.349,"2023-09":4.147,"2023-10":4.031,"2023-11":4.007,"2023-12":3.93,"2024-01":3.862,"2024-02":3.752,"2024-03":3.801,"2024-04":3.61,"2024-05":3.419,"2024-06":3.267,"2024-07":3.171,"2024-08":3.197,"2024-09":3.311,"2024-10":3.333,"2024-11":3.319,"2024-12":3.238,"2025-01":3.258,"2025-02":3.117,"2025-03":2.789,"2025-04":2.779,"2025-05":2.787,"2025-06":2.934,"2025-07":3.059,"2025-08":3.11,"2025-09":3.019,"2025-11":2.633,"2025-12":2.639,"2026-01":2.504,"2026-02":2.457,"2026-03":2.595,"2026-04":2.75,"2026-05":2.851,"2026-06":2.594,"2026-07":2.478,"2026-08":2.446}


def split(series):
    """Two runs, before and after the missing October 2025."""
    ks = sorted(series)
    a = [k for k in ks if k < "2025-10"]
    b = [k for k in ks if k > "2025-10"]
    to = lambda k: datetime.strptime(k + "-15", "%Y-%m-%d")
    return ([to(k) for k in a], [series[k] for k in a]), ([to(k) for k in b], [series[k] for k in b])


def build():
    assert "2025-10" not in ALL and "2025-10" not in CORE
    assert max(ALL.items(), key=lambda kv: kv[1]) == ("2022-06", 9.06)
    assert max(CORE.items(), key=lambda kv: kv[1]) == ("2022-09", 6.631)
    assert (round(ALL["2026-08"], 1), round(CORE["2026-08"], 1)) == (3.4, 2.4)
    earlier_lower = [k for k, v in CORE.items() if v < CORE["2026-08"] and k < "2026-08"]
    assert max(earlier_lower) == "2021-03"

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    for series, col, ls in ((ALL, CORAL, "-"), (CORE, TEAL, "-")):
        for xs, ys in split(series):
            ax.plot(xs, ys, color=col, linewidth=2.8, linestyle=ls, zorder=3)
    gap = datetime(2025, 10, 15)
    ax.axvspan(datetime(2025, 9, 25), datetime(2025, 11, 5), color=SLATE, alpha=0.18, linewidth=0)
    ax.text(gap, 6.0, "Oct 2025:\nno data\n(shutdown)", fontsize=10.5, color=MUTED,
            ha="center", va="bottom", linespacing=1.3)

    ax.axhline(2.0, color=SLATE, linewidth=1.2, linestyle=(0, (6, 5)), zorder=2)
    # Placed where both lines sit well above 2% (early 2021 lines ran through it).
    ax.text(datetime(2023, 9, 1), 1.85, "Fed's 2% goal (a PCE target, shown for scale)",
            fontsize=10.5, color=MUTED, ha="left", va="top", fontweight="bold")

    ax.annotate("9.1% peak\nJune 2022", xy=(datetime(2022, 6, 15), 9.06),
                xytext=(datetime(2022, 11, 1), 9.15), fontsize=12, color=CORAL,
                fontweight="bold", ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=CORAL, lw=1))
    ax.annotate("Core peak 6.6%\nSept 2022", xy=(datetime(2022, 9, 15), 6.631),
                xytext=(datetime(2023, 3, 1), 7.35), fontsize=12, color=TEAL,
                fontweight="bold", ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=TEAL, lw=1))
    ax.annotate("4.2% in May", xy=(datetime(2026, 5, 15), 4.249),
                xytext=(datetime(2025, 12, 1), 5.05), fontsize=11.5, color=CORAL,
                ha="center", va="center", arrowprops=dict(arrowstyle="-", color=CORAL, lw=1))

    end = datetime(2026, 8, 15)
    for v, col in ((ALL["2026-08"], CORAL), (CORE["2026-08"], TEAL)):
        ax.scatter([end], [v], s=60, color=col, zorder=4)
        ax.text(datetime(2026, 10, 5), v, f"{v:.1f}%", fontsize=17, fontweight="bold",
                color=col, ha="left", va="center")

    ax.set_xlim(datetime(2020, 12, 1), datetime(2027, 2, 15))
    ax.set_ylim(0.8, 9.8)
    ax.set_yticks(range(1, 10))
    ax.set_yticklabels([f"{i}%" for i in range(1, 10)], fontsize=12, color=MUTED)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.tick_params(length=0, labelsize=12.5, colors=MUTED)
    ax.yaxis.grid(True, color=GRID, linewidth=1, zorder=0)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)

    # Kept short: the longer title ran under the -hb corner lockup.
    fig.text(0.045, 0.945, "Inflation Turned Back Up. Core Barely Moved.",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888, "U.S. consumer prices, 12 month % change, January 2021 to August 2026",
             fontsize=14, color=MUTED, ha="left", va="top")
    fig.text(0.045, 0.838, "▬", fontsize=16, color=CORAL, ha="left", va="center")
    fig.text(0.068, 0.838, "All items", fontsize=12.5, color=INK, ha="left", va="center", fontweight="bold")
    fig.text(0.160, 0.838, "▬", fontsize=16, color=TEAL, ha="left", va="center")
    fig.text(0.183, 0.838, "Core (excluding food and energy)", fontsize=12.5, color=INK,
             ha="left", va="center", fontweight="bold")

    fig.text(0.045, 0.100,
             "Headline inflation went from 2.4% in January to 4.2% in May and sits at 3.4%. Core is 2.4%, its lowest since March 2021.",
             fontsize=11.5, color=DEEP, ha="left", va="bottom")
    fig.text(0.045, 0.030,
             "Source: U.S. Bureau of Labor Statistics, Consumer Price Index, unadjusted 12 month changes, data through August 2026\n"
             "(released September 11, 2026). October 2025 was not collected during the federal shutdown.",
             fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5)

    fig.subplots_adjust(left=0.065, right=0.975, top=0.80, bottom=0.21)
    return fig


if __name__ == "__main__":
    fig = build()
    save_pair(fig, os.path.join(OUTDIR, f"cpi-2021-{STAMP}.png"),
              logo=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hb-logo-mark.png"))
