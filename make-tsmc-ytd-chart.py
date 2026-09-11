#!/usr/bin/env python3
"""
make-tsmc-ytd-chart.py  [outdir]

Recreates the newsletter graphic "TSMC Is Up 41% This Year" for the 09/11/26
edition. Emits BOTH brand variants:

  tsmc-ytd-091126.png      plain monogram    -> RE email + Agent Hub
  tsmc-ytd-091126-hb.png   + wordmark        -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/11/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

The supplied graphic plots TSM (NYSE) daily closes, year to date, "closed
Sept. 10 at $428.03", source Google Finance, headline "up 41% this year".

HEADLINE CHECKS. Yahoo Finance TSM daily bars: Dec 31, 2025 close $303.89,
Sep 10, 2026 close $428.03, so +40.85%, which rounds to 41%. The Sep 10 close
matches the graphic to the cent. 2026 high close $477.57 on Jun 30; 2026 low
close $316.50 on Mar 30; both match the graphic's peak and trough by eye.
No degenerate O=H=L=C bars and no gaps in the series.

FRAMING. The circulating version starts its line at the first January close,
so the baseline the 41% is measured from never appears. This version draws the
Dec 31 close as a dashed reference line, which SHOWS the 41%, and marks how far
the stock still sits below its June 30 high (-10.4%), which the headline leaves
out. Sep 11 is excluded: a live tick, not a close.

Data: Yahoo Finance chart API, TSM, interval 1d, Dec 31, 2025 to Sep 10, 2026.
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
STAMP = "091126"

CREAM = "#fdf6e8"
INK = "#1f2933"
GREEN = "#2f8f5b"
DEEP = "#1f6b43"
CORAL = "#e2574c"
SLATE = "#8a9aa8"
GRID = "#d8cdb8"
MUTED = "#8a8172"

# TSM (NYSE) daily closes via Yahoo Finance, Dec 31, 2025 to Sep 10, 2026.
CLOSES = [
    ("2025-12-31", 303.89), ("2026-01-02", 319.61), ("2026-01-05", 322.25), ("2026-01-06", 327.43), ("2026-01-07", 318.68),
    ("2026-01-08", 318.01), ("2026-01-09", 323.63), ("2026-01-12", 331.77), ("2026-01-13", 331.21), ("2026-01-14", 327.11),
    ("2026-01-15", 341.64), ("2026-01-16", 342.40), ("2026-01-20", 327.16), ("2026-01-21", 326.12), ("2026-01-22", 327.37),
    ("2026-01-23", 334.87), ("2026-01-26", 332.71), ("2026-01-27", 338.34), ("2026-01-28", 342.30), ("2026-01-29", 339.55),
    ("2026-01-30", 330.56), ("2026-02-02", 341.36), ("2026-02-03", 335.75), ("2026-02-04", 325.74), ("2026-02-05", 330.73),
    ("2026-02-06", 348.85), ("2026-02-09", 355.41), ("2026-02-10", 361.91), ("2026-02-11", 374.09), ("2026-02-12", 368.10),
    ("2026-02-13", 366.36), ("2026-02-17", 364.20), ("2026-02-18", 362.26), ("2026-02-19", 360.39), ("2026-02-20", 370.54),
    ("2026-02-23", 370.04), ("2026-02-24", 385.75), ("2026-02-25", 387.73), ("2026-02-26", 376.81), ("2026-02-27", 374.58),
    ("2026-03-02", 369.11), ("2026-03-03", 353.13), ("2026-03-04", 357.44), ("2026-03-05", 353.86), ("2026-03-06", 338.89),
    ("2026-03-09", 348.70), ("2026-03-10", 347.09), ("2026-03-11", 354.56), ("2026-03-12", 336.71), ("2026-03-13", 338.31),
    ("2026-03-16", 340.23), ("2026-03-17", 345.98), ("2026-03-18", 339.57), ("2026-03-19", 338.79), ("2026-03-20", 329.24),
    ("2026-03-23", 338.45), ("2026-03-24", 343.25), ("2026-03-25", 347.75), ("2026-03-26", 326.11), ("2026-03-27", 326.74),
    ("2026-03-30", 316.50), ("2026-03-31", 337.95), ("2026-04-01", 341.49), ("2026-04-02", 339.04), ("2026-04-06", 341.76),
    ("2026-04-07", 345.32), ("2026-04-08", 365.90), ("2026-04-09", 365.49), ("2026-04-10", 370.60), ("2026-04-13", 369.57),
    ("2026-04-14", 379.89), ("2026-04-15", 375.10), ("2026-04-16", 363.35), ("2026-04-17", 370.50), ("2026-04-20", 366.24),
    ("2026-04-21", 368.08), ("2026-04-22", 387.44), ("2026-04-23", 382.66), ("2026-04-24", 402.46), ("2026-04-27", 404.98),
    ("2026-04-28", 392.34), ("2026-04-29", 393.83), ("2026-04-30", 396.06), ("2026-05-01", 397.67), ("2026-05-04", 401.61),
    ("2026-05-05", 394.41), ("2026-05-06", 419.50), ("2026-05-07", 414.15), ("2026-05-08", 411.68), ("2026-05-11", 404.54),
    ("2026-05-12", 397.28), ("2026-05-13", 399.80), ("2026-05-14", 417.72), ("2026-05-15", 404.35), ("2026-05-18", 395.95),
    ("2026-05-19", 392.61), ("2026-05-20", 401.62), ("2026-05-21", 407.15), ("2026-05-22", 404.52), ("2026-05-26", 412.32),
    ("2026-05-27", 422.73), ("2026-05-28", 424.86), ("2026-05-29", 418.45), ("2026-06-01", 435.63), ("2026-06-02", 446.69),
    ("2026-06-03", 436.69), ("2026-06-04", 444.92), ("2026-06-05", 415.17), ("2026-06-08", 426.80), ("2026-06-09", 427.92),
    ("2026-06-10", 408.75), ("2026-06-11", 421.07), ("2026-06-12", 423.93), ("2026-06-15", 441.40), ("2026-06-16", 425.83),
    ("2026-06-17", 432.15), ("2026-06-18", 462.12), ("2026-06-22", 467.67), ("2026-06-23", 436.39), ("2026-06-24", 440.83),
    ("2026-06-25", 434.99), ("2026-06-26", 432.35), ("2026-06-29", 455.10), ("2026-06-30", 477.57), ("2026-07-01", 444.23),
    ("2026-07-02", 434.16), ("2026-07-06", 451.79), ("2026-07-07", 432.57), ("2026-07-08", 436.98), ("2026-07-09", 436.96),
    ("2026-07-10", 434.11), ("2026-07-13", 421.58), ("2026-07-14", 420.39), ("2026-07-15", 419.48), ("2026-07-16", 409.74),
    ("2026-07-17", 398.37), ("2026-07-20", 402.30), ("2026-07-21", 424.61), ("2026-07-22", 421.21), ("2026-07-23", 415.58),
    ("2026-07-24", 403.41), ("2026-07-27", 399.09), ("2026-07-28", 392.31), ("2026-07-29", 374.67), ("2026-07-30", 403.31),
    ("2026-07-31", 404.25), ("2026-08-03", 406.11), ("2026-08-04", 417.17), ("2026-08-05", 414.00), ("2026-08-06", 418.20),
    ("2026-08-07", 420.04), ("2026-08-10", 418.47), ("2026-08-11", 422.06), ("2026-08-12", 429.15), ("2026-08-13", 430.49),
    ("2026-08-14", 426.35), ("2026-08-17", 430.97), ("2026-08-18", 413.41), ("2026-08-19", 412.09), ("2026-08-20", 416.00),
    ("2026-08-21", 418.95), ("2026-08-24", 410.12), ("2026-08-25", 417.41), ("2026-08-26", 417.69), ("2026-08-27", 427.30),
    ("2026-08-28", 417.52), ("2026-08-31", 415.32), ("2026-09-01", 414.00), ("2026-09-02", 415.50), ("2026-09-03", 417.01),
    ("2026-09-04", 428.91), ("2026-09-08", 439.00), ("2026-09-09", 435.36), ("2026-09-10", 428.03),
]


def money(x, places="0.01"):
    return Decimal(str(x)).quantize(Decimal(places), rounding=ROUND_HALF_UP)


def build():
    ds = [date.fromisoformat(d) for d, _ in CLOSES]
    ps = [p for _, p in CLOSES]
    assert ds[0] == date(2025, 12, 31) and ds[-1] == date(2026, 9, 10)
    base, last_d, last_p = ps[0], ds[-1], ps[-1]
    assert money(last_p) == Decimal("428.03"), last_p
    ytd = money((Decimal(str(last_p)) / Decimal(str(base)) - 1) * 100, "0.1")
    hi_i = max(range(1, len(ps)), key=lambda i: ps[i])
    lo_i = min(range(1, len(ps)), key=lambda i: ps[i])
    off_hi = money((Decimal(str(last_p)) / Decimal(str(ps[hi_i])) - 1) * 100, "0.1")

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    ax.fill_between(ds, ps, base, color=GREEN, alpha=0.13, linewidth=0, zorder=1)
    ax.axhline(base, color=MUTED, linewidth=1.2, linestyle=(0, (6, 4)), zorder=2)
    ax.plot(ds, ps, color=GREEN, linewidth=2.5, zorder=3, solid_joinstyle="round")

    ax.text(date(2026, 1, 8), base - 6.5, f"Dec 31 close  \\${money(base)}",
            fontsize=11.5, color=MUTED, ha="left", va="top")

    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=range(1, 10)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.set_xlim(date(2025, 12, 24), date(2026, 11, 8))
    ax.set_ylim(270, 500)
    ax.set_yticks([300, 350, 400, 450])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"\\${v:.0f}"))
    ax.grid(axis="y", color=GRID, linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="both", length=0, labelsize=12.5, colors=SLATE)
    for lbl in ax.get_xticklabels():   # after tick_params, which resets colours
        lbl.set_color(INK)

    ax.scatter([ds[hi_i]], [ps[hi_i]], s=34, color=DEEP, zorder=5)
    ax.annotate(f"{ds[hi_i]:%b} {ds[hi_i].day} high  \\${money(ps[hi_i])}",
                xy=(ds[hi_i], ps[hi_i]), xytext=(date(2026, 4, 1), 490),
                fontsize=12, fontweight="bold", color=INK, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.0))
    ax.scatter([ds[lo_i]], [ps[lo_i]], s=34, color=CORAL, zorder=5)
    ax.annotate(f"{ds[lo_i]:%b} {ds[lo_i].day} low  \\${money(ps[lo_i])}",
                xy=(ds[lo_i], ps[lo_i]), xytext=(date(2026, 4, 20), 290),
                fontsize=12, fontweight="bold", color=INK, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.0))

    ax.scatter([last_d], [last_p], s=90, color=DEEP, edgecolor=CREAM, linewidth=1.5, zorder=6)
    ax.annotate(f"\\${money(last_p)}", xy=(last_d, last_p), xytext=(date(2026, 9, 20), last_p),
                fontsize=22, fontweight="bold", color="white", ha="left", va="center",
                bbox=dict(boxstyle="round,pad=0.32", fc=GREEN, ec="none"), zorder=7)
    ax.text(date(2026, 9, 20), last_p - 17,
            f"{last_d:%b} {last_d.day} close\n+{ytd}% this year\n{off_hi}% from the\n{ds[hi_i]:%b} {ds[hi_i].day} high",
            fontsize=11.5, color=INK, ha="left", va="top", linespacing=1.4)

    fig.text(0.045, 0.945, f"TSMC Is Up {money(ytd, '1')}% This Year",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888,
             "Taiwan Semiconductor (TSM, NYSE), daily closing price, December 31, 2025 to September 10, 2026",
             fontsize=14, color=MUTED, ha="left", va="top")

    fig.text(
        0.045, 0.118,
        "August revenue was a record NT\\$514.8 billion, up 53.3% from a year ago and the fourth straight monthly gain.\n"
        f"The stock is up {ytd}% on the year but still {str(off_hi).lstrip('-')}% below its June 30 high.",
        fontsize=11.5, color=DEEP, ha="left", va="bottom", linespacing=1.55,
    )
    fig.text(
        0.045, 0.040,
        "Source: TSM daily closing prices via Yahoo Finance; the dashed line is the December 31, 2025 close the year to date gain is measured from.\n"
        "Revenue: TSMC monthly revenue report, August 2026, consolidated, New Taiwan dollars.",
        fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5,
    )

    fig.subplots_adjust(left=0.075, right=0.975, top=0.80, bottom=0.235)
    return fig


if __name__ == "__main__":
    fig = build()
    save_pair(fig, os.path.join(OUTDIR, f"tsmc-ytd-{STAMP}.png"),
              logo=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hb-logo-mark.png"))
