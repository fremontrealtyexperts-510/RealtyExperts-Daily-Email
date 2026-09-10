#!/usr/bin/env python3
"""
make-oil100-chart.py  [outdir]

Recreates the newsletter graphic "Oil Is Back Above $100" for the 09/10/26
edition. Emits BOTH brand variants:

  oil100-091026.png      plain monogram    -> RE email + Agent Hub
  oil100-091026-hb.png   + wordmark        -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/10/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

The supplied graphic plots "Brent crude, average price per barrel", source EIA,
"September is month to date": Feb $71, Mar $103, Apr $117, May $107, Jun $85,
Jul $84, Aug $91, Sep $101.

FEBRUARY TO AUGUST ARE RIGHT. Averaging EIA's daily Europe Brent spot series
(RBRTE) month by month reproduces every label: 70.89, 103.13, 117.29, 107.14,
85.40, 83.76, 91.08.

SEPTEMBER IS NOT A MONTH TO DATE AVERAGE. EIA's spot table was last released
9/2/2026 (next release 9/10/2026) and carries exactly one September day,
Sept 1 at $96.02. No EIA September average of $101 exists yet. The ICE futures
September average (Sept 1 to 9, six settlements) is $96.87. The only $101 on
the board is the single Sept 9 futures settlement, $101.21. So the headline is
true of the PRICE, but the plotted point labels one day's price as a monthly
average, and that is exactly the claim the chart needed to SHOW.

INSTRUMENT. EIA's series is physical spot; our Economy card is locked to ICE
front month futures (reference-brent-locked-to-bz-f-futures). The two ran as
much as $14.83 apart on April's average (spot 117.29, futures 102.46), so EIA
monthly averages beside our futures card would print two different "Brent"
prices in one email. This version plots the futures contract we quote, daily,
which shows the crossing instead of asserting it.

Data: Yahoo Finance BZ=F daily bars, Feb 2 to Sep 9, 2026, checked for
degenerate O=H=L=C bars (none found). Sep 10 excluded: a live tick, not a
settlement. Month labels are computed below from the same series.

matplotlib only; build with python3.13 on Mac.
"""
import os
import sys
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "091026"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
OIL = "#d9822b"
SLATE = "#8a9aa8"
GRID = "#d8cdb8"
MUTED = "#8a8172"

# ICE Brent front month daily settlements (Yahoo BZ=F), Feb 2 to Sep 9, 2026.
SETTLES = [
    ("2026-02-02", 66.30), ("2026-02-03", 67.33), ("2026-02-04", 69.46), ("2026-02-05", 67.55), ("2026-02-06", 68.05),
    ("2026-02-09", 69.04), ("2026-02-10", 68.80), ("2026-02-11", 69.40), ("2026-02-12", 67.52), ("2026-02-13", 67.75),
    ("2026-02-17", 67.42), ("2026-02-18", 70.35), ("2026-02-19", 71.66), ("2026-02-20", 71.76), ("2026-02-23", 71.49),
    ("2026-02-24", 70.77), ("2026-02-25", 70.85), ("2026-02-26", 70.75), ("2026-02-27", 72.48), ("2026-03-02", 77.74),
    ("2026-03-03", 81.40), ("2026-03-04", 81.40), ("2026-03-05", 85.41), ("2026-03-06", 92.69), ("2026-03-09", 98.96),
    ("2026-03-10", 87.80), ("2026-03-11", 91.98), ("2026-03-12", 100.46), ("2026-03-13", 103.14), ("2026-03-16", 100.21),
    ("2026-03-17", 103.42), ("2026-03-18", 107.38), ("2026-03-19", 108.65), ("2026-03-20", 112.19), ("2026-03-23", 99.94),
    ("2026-03-24", 104.49), ("2026-03-25", 102.22), ("2026-03-26", 108.01), ("2026-03-27", 112.57), ("2026-03-30", 112.78),
    ("2026-03-31", 118.35), ("2026-04-01", 101.16), ("2026-04-02", 109.03), ("2026-04-06", 109.77), ("2026-04-07", 109.27),
    ("2026-04-08", 94.75), ("2026-04-09", 95.92), ("2026-04-10", 95.20), ("2026-04-13", 99.36), ("2026-04-14", 94.79),
    ("2026-04-15", 94.93), ("2026-04-16", 99.39), ("2026-04-17", 90.38), ("2026-04-20", 95.48), ("2026-04-21", 98.48),
    ("2026-04-22", 101.91), ("2026-04-23", 105.07), ("2026-04-24", 105.33), ("2026-04-27", 108.23), ("2026-04-28", 111.26),
    ("2026-04-29", 118.03), ("2026-04-30", 114.01), ("2026-05-01", 108.17), ("2026-05-04", 114.44), ("2026-05-05", 109.87),
    ("2026-05-06", 101.27), ("2026-05-07", 100.06), ("2026-05-08", 101.29), ("2026-05-11", 104.21), ("2026-05-12", 107.77),
    ("2026-05-13", 105.63), ("2026-05-14", 105.72), ("2026-05-15", 109.26), ("2026-05-18", 112.10), ("2026-05-19", 111.28),
    ("2026-05-20", 105.02), ("2026-05-21", 102.58), ("2026-05-22", 103.54), ("2026-05-26", 99.58), ("2026-05-27", 94.29),
    ("2026-05-28", 93.71), ("2026-05-29", 92.05), ("2026-06-01", 94.98), ("2026-06-02", 96.00), ("2026-06-03", 97.81),
    ("2026-06-04", 95.03), ("2026-06-05", 93.09), ("2026-06-08", 94.25), ("2026-06-09", 91.45), ("2026-06-10", 93.10),
    ("2026-06-11", 90.38), ("2026-06-12", 87.33), ("2026-06-15", 83.17), ("2026-06-16", 78.96), ("2026-06-17", 79.55),
    ("2026-06-18", 79.85), ("2026-06-22", 77.90), ("2026-06-23", 77.08), ("2026-06-24", 73.74), ("2026-06-25", 75.26),
    ("2026-06-26", 71.99), ("2026-06-29", 73.15), ("2026-06-30", 72.92), ("2026-07-01", 71.57), ("2026-07-02", 71.80),
    ("2026-07-06", 71.99), ("2026-07-07", 74.16), ("2026-07-08", 78.02), ("2026-07-09", 76.30), ("2026-07-10", 76.01),
    ("2026-07-13", 83.30), ("2026-07-14", 84.73), ("2026-07-15", 84.95), ("2026-07-16", 84.23), ("2026-07-17", 88.10),
    ("2026-07-20", 89.22), ("2026-07-21", 91.01), ("2026-07-22", 94.07), ("2026-07-23", 100.69), ("2026-07-24", 96.78),
    ("2026-07-27", 88.36), ("2026-07-28", 84.09), ("2026-07-29", 90.74), ("2026-07-30", 89.03), ("2026-07-31", 90.12),
    ("2026-08-03", 83.77), ("2026-08-04", 79.36), ("2026-08-05", 79.45), ("2026-08-06", 82.49), ("2026-08-07", 83.55),
    ("2026-08-10", 87.72), ("2026-08-11", 88.91), ("2026-08-12", 88.98), ("2026-08-13", 87.07), ("2026-08-14", 88.52),
    ("2026-08-17", 90.87), ("2026-08-18", 91.02), ("2026-08-19", 91.62), ("2026-08-20", 93.78), ("2026-08-21", 94.39),
    ("2026-08-24", 92.17), ("2026-08-25", 88.58), ("2026-08-26", 87.84), ("2026-08-27", 89.70), ("2026-08-28", 89.31),
    ("2026-08-31", 90.49), ("2026-09-01", 94.65), ("2026-09-02", 95.63), ("2026-09-03", 95.52), ("2026-09-04", 96.28),
    ("2026-09-08", 97.92), ("2026-09-09", 101.21),
]


def money(x, places="0.01"):
    return Decimal(str(x)).quantize(Decimal(places), rounding=ROUND_HALF_UP)


def build():
    ds = [date.fromisoformat(d) for d, _ in SETTLES]
    ps = [p for _, p in SETTLES]
    last_d, last_p = ds[-1], ps[-1]
    peak_i = max(range(len(ps)), key=lambda i: ps[i])
    summer = [i for i, d in enumerate(ds) if date(2026, 6, 1) <= d <= date(2026, 8, 31)]
    low_i = min(summer, key=lambda i: ps[i])
    prior_above = [i for i, d in enumerate(ds) if d < last_d and ps[i] > 100][-1]

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    ax.fill_between(ds, ps, 100, where=[p > 100 for p in ps], interpolate=True,
                    color=CORAL, alpha=0.17, linewidth=0, zorder=1)
    ax.axhline(100, color=DEEP, linewidth=1.3, linestyle=(0, (6, 4)), zorder=2)
    ax.plot(ds, ps, color=OIL, linewidth=2.6, zorder=3, solid_joinstyle="round")

    # Month labels: name plus that month's average settlement.
    ticks, labels = [], []
    for m in range(2, 10):
        vals = [p for d, p in zip(ds, ps) if d.month == m]
        avg = money(sum(vals) / len(vals), "0.1")
        if m == 9:
            ticks.append(mdates.date2num(date(2026, 9, 6)))
            labels.append(f"Sep\navg \\${avg}\nso far")   # 3 lines: 2 would collide with Aug
        else:
            ticks.append(mdates.date2num(date(2026, m, 15)))
            labels.append(f"{date(2026, m, 1):%b}\navg \\${avg}")
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, fontsize=12, linespacing=1.35)

    ax.set_xlim(date(2026, 2, 1), date(2026, 10, 24))
    ax.set_ylim(60, 128)
    ax.set_yticks([60, 80, 100, 120])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"\\${v:.0f}"))
    ax.grid(axis="y", color=GRID, linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="both", length=0, labelsize=12.5, colors=SLATE)
    for lbl in ax.get_xticklabels():   # after tick_params, which resets colours
        lbl.set_color(INK)
    for lbl in ax.get_yticklabels():
        if lbl.get_text().endswith("100"):
            lbl.set_color(DEEP)
            lbl.set_fontweight("bold")

    # Callouts
    ax.annotate(f"{ds[peak_i]:%b} {ds[peak_i].day} peak  \\${money(ps[peak_i])}",
                xy=(ds[peak_i], ps[peak_i]), xytext=(date(2026, 4, 22), 124.5),
                fontsize=12, fontweight="bold", color=INK, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.0))
    ax.annotate(f"{ds[low_i]:%b} {ds[low_i].day} low  \\${money(ps[low_i])}",
                xy=(ds[low_i], ps[low_i]), xytext=(date(2026, 7, 14), 64.5),
                fontsize=12, fontweight="bold", color=INK, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.0))
    ax.scatter([ds[prior_above]], [ps[prior_above]], s=28, color=DEEP, zorder=5)
    ax.annotate(f"{ds[prior_above]:%b} {ds[prior_above].day}  \\${money(ps[prior_above])}",
                xy=(ds[prior_above], ps[prior_above]), xytext=(date(2026, 7, 8), 108.5),
                fontsize=11, color=MUTED, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.9))

    ax.scatter([last_d], [last_p], s=90, color=DEEP, edgecolor=CREAM, linewidth=1.5, zorder=6)
    ax.annotate(f"\\${money(last_p)}", xy=(last_d, last_p), xytext=(date(2026, 9, 17), last_p),
                fontsize=22, fontweight="bold", color="white", ha="left", va="center",
                bbox=dict(boxstyle="round,pad=0.32", fc=OIL, ec="none"), zorder=7)
    ax.text(date(2026, 9, 17), last_p - 6.0,
            f"{last_d:%b} {last_d.day} settle, first\nclose above \\$100\nsince {ds[prior_above]:%b} {ds[prior_above].day}",
            fontsize=11.5, color=INK, ha="left", va="top", linespacing=1.4)

    fig.text(0.045, 0.945, "Oil Is Back Above \\$100",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888,
             "Brent crude, ICE front month futures, daily settlement per barrel, February 2 to September 9, 2026",
             fontsize=14, color=MUTED, ha="left", va="top")

    sep_avg = money(sum(p for d, p in zip(ds, ps) if d.month == 9) / sum(1 for d in ds if d.month == 9))
    fig.text(
        0.045, 0.118,
        f"The price is back above \\$100, but September's average is not yet: \\${sep_avg} for September 1 to 9. The version circulating today\n"
        "plots \\$101 as September's month to date average. That is one day's price; EIA's spot series has published only September 1 (\\$96.02).",
        fontsize=11.5, color=DEEP, ha="left", va="bottom", linespacing=1.55,
    )
    fig.text(
        0.045, 0.040,
        "Source: ICE Futures Europe, Brent front month daily settlements via Yahoo Finance (BZ=F). Month labels are average settlements.\n"
        "EIA physical spot, used in the circulating version, ran above futures this spring, by \\$14.83 on April's average.",
        fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5,
    )

    fig.subplots_adjust(left=0.075, right=0.965, top=0.815, bottom=0.275)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"oil100-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
