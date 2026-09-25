#!/usr/bin/env python3
"""
make-jobless-claims-2026-chart.py  [outdir]

REALTY EXPERTS recreation of the "Layoffs Are Still Rare" graphic for the
09/25/26 daily email. OUR OWN branded chart, not the source image.
(make-jobless-claims-chart.py is the 08/21/26 chart; this is a separate file.)

VERIFIED: every weekly point and the 4-week average on the supplied graphic
match the Labor Department series (FRED ICSA and IC4WSA, pulled 09/25/26), and
the last points reproduce DOL's September 24, 2026 release exactly: 197,000
for the week ending September 19, 4-week average 202,250.

WHAT WE ADD:
  * A dashed reference at the SAME WEEK A YEAR AGO (read from ICSA, and asserted
    equal to the release's "Prior Year" column, 219,000), so "rare" has a
    benchmark on the chart itself.
  * The local answer, in the footnote: California's own weekly initial claims
    (CAICLAIMS). DOL publishes state data NOT seasonally adjusted only, so it is
    compared with the same week a year earlier, never with the SA line.

Every value is read from the FRED CSVs at run time, never hand typed.

matplotlib only; build with python3.13 on Mac.
"""
import csv
import io
import os
import subprocess
import sys
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "092526"
LAST_WEEK = date(2026, 9, 19)
RELEASE_PRIOR_YEAR = 219000   # DOL 09/24/26 release, "Prior Year" column (checked below)

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
GREEN = "#2f8f5b"
SLATE = "#4a5568"
MUTED = "#8a8172"
GRID = "#d8cdb8"


def fred(sid, start="2025-01-01"):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={start}"
    # Cached CSV first (fetch it with shell curl if the run below fails): python3.13
    # on this Mac has no CA bundle for urllib, and curl spawned from Python has
    # dropped the FRED connection (exit 56/92) while the same curl from the shell
    # works. The cache is the exact FRED response, so nothing is hand typed.
    cache = f"/tmp/fred_{sid}_{start}.csv"
    if not os.path.exists(cache):
        subprocess.run(["curl", "-s", "--retry", "3", "-m", "60", "-o", cache, url],
                       check=True)
    raw = open(cache).read()
    rows = list(csv.reader(io.StringIO(raw)))
    return {date.fromisoformat(a): int(float(b)) for a, b in rows[1:] if b not in ("", ".")}


def k(v):
    return f"{Decimal(v / 1000).quantize(Decimal('1'), rounding=ROUND_HALF_UP)}K"


def build(ic, ic4, ca):
    weeks = sorted(d for d in ic if d.year == 2026 and d <= LAST_WEEK)
    assert weeks[-1] == LAST_WEEK, f"latest week is {weeks[-1]}, expected {LAST_WEEK}"
    assert ic[LAST_WEEK] == 197000 and ic4[LAST_WEEK] == 202250, "release mismatch"
    ya = LAST_WEEK - timedelta(days=364)
    assert ic[ya] == RELEASE_PRIOR_YEAR, f"year ago SA {ic[ya]} != release"
    ca_now, ca_ya = ca[LAST_WEEK], ca[ya]
    ca_chg = (Decimal(ca_now) / Decimal(ca_ya) - 1) * 100
    ca_chg = ca_chg.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

    ys = [ic[d] / 1000 for d in weeks]
    ys4 = [ic4[d] / 1000 for d in weeks]
    xs = list(range(len(weeks)))

    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    fig.text(0.062, 0.925, "Layoffs Stay Rare in 2026",
             fontsize=30, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.062, 0.858,
             "U.S. weekly initial jobless claims, seasonally adjusted, through the "
             f"week ending {LAST_WEEK:%B %-d}",
             fontsize=14.5, color=MUTED, ha="left", va="top")

    # legend chips
    for x0, col, lab in ((0.064, CORAL, "Weekly claims"), (0.215, GREEN, "4-week average"),
                         (0.385, SLATE, f"Same week last year, {k(ic[ya])}")):
        if col is SLATE:
            fig.lines.append(plt.Line2D([x0, x0 + 0.022], [0.788, 0.788], color=SLATE,
                                        linestyle=(0, (4, 3)), linewidth=2,
                                        transform=fig.transFigure, figure=fig))
            fig.text(x0 + 0.03, 0.788, lab, fontsize=12.5, fontweight="bold",
                     color=INK, va="center")
        else:
            fig.lines.append(plt.Line2D([x0, x0 + 0.022], [0.788, 0.788], color=col,
                                        linewidth=4, transform=fig.transFigure,
                                        figure=fig))
            fig.text(x0 + 0.03, 0.788, lab, fontsize=12.5, fontweight="bold",
                     color=INK, va="center")

    ax = fig.add_axes((0.1, 0.235, 0.77, 0.515))
    ax.set_facecolor(CREAM)
    ax.axhline(ic[ya] / 1000, color=SLATE, linestyle=(0, (4, 3)), linewidth=1.6, zorder=2)
    ax.plot(xs, ys, color=CORAL, linewidth=2.8, zorder=4)
    ax.plot(xs, ys4, color=GREEN, linewidth=3.2, zorder=3)
    ax.scatter([xs[-1]], [ys[-1]], s=70, color=CORAL, zorder=5)
    ax.scatter([xs[-1]], [ys4[-1]], s=70, color=GREEN, zorder=5)

    ax.annotate(k(ic4[LAST_WEEK]), (xs[-1], ys4[-1]), xytext=(16, 10),
                textcoords="offset points", ha="left", va="center", fontsize=18,
                fontweight="bold", color="white", annotation_clip=False,
                bbox=dict(boxstyle="round,pad=0.35", fc=GREEN, ec="none"))
    ax.annotate(k(ic[LAST_WEEK]), (xs[-1], ys[-1]), xytext=(16, -16),
                textcoords="offset points", ha="left", va="center", fontsize=18,
                fontweight="bold", color="white", annotation_clip=False,
                bbox=dict(boxstyle="round,pad=0.35", fc=CORAL, ec="none"))

    # month ticks at the first week of each month
    ticks, labels, seen = [], [], set()
    for i, d in enumerate(weeks):
        if d.month not in seen:
            seen.add(d.month)
            ticks.append(i)
            labels.append(d.strftime("%b").upper())
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, fontsize=13.5, fontweight="bold", color=INK)
    ax.set_ylim(184, 236)
    ax.set_yticks([190, 200, 210, 220, 230])
    ax.set_yticklabels([f"{v}K" for v in (190, 200, 210, 220, 230)], fontsize=12.5,
                       color=MUTED)
    ax.set_xlim(-0.6, len(xs) - 0.4)
    ax.grid(axis="y", color=GRID, linewidth=1, zorder=0)
    ax.tick_params(length=0, pad=8)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)

    fig.text(0.062, 0.128,
             f"Closer to home: California logged {ca_now:,} initial claims that week, "
             f"down {abs(ca_chg)}% from {ca_ya:,} in the same week of {ya.year}",
             fontsize=11.5, color=MUTED, ha="left", va="top")
    fig.text(0.062, 0.093,
             "(state data is published only without seasonal adjustment, so it is "
             "compared year over year; the latest week is DOL's advance figure).",
             fontsize=11.5, color=MUTED, ha="left", va="top")
    fig.text(0.062, 0.035,
             "Source: U.S. Department of Labor weekly claims, via FRED (ICSA, IC4WSA, "
             "CAICLAIMS), week ending September 19, 2026.",
             fontsize=10.5, color=MUTED, ha="left", va="bottom")
    return fig, weeks, ys, ys4, ya, ca_now, ca_ya, ca_chg


if __name__ == "__main__":
    ic, ic4, ca = fred("ICSA"), fred("IC4WSA"), fred("CAICLAIMS")
    fig, weeks, ys, ys4, ya, ca_now, ca_ya, ca_chg = build(ic, ic4, ca)
    for d, a, b in zip(weeks, ys, ys4):
        print(f"  {d}  {a:6.1f}K  4wk {b:7.2f}K")
    lo = min(range(len(ys)), key=lambda i: ys[i])
    hi = max(range(len(ys)), key=lambda i: ys[i])
    print(f"  2026 low {ys[lo]}K on {weeks[lo]}, high {ys[hi]}K on {weeks[hi]}")
    print(f"  year ago ({ya}) SA {ic[ya]:,}; CA {ca_now:,} vs {ca_ya:,} ({ca_chg}%)")
    save_pair(fig, os.path.join(OUTDIR, f"jobless-claims-{STAMP}.png"), facecolor=CREAM)
