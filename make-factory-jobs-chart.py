#!/usr/bin/env python3
"""
make-factory-jobs-chart.py  BLS_SERIES_JSON  [outdir]

The 10/02/26 daily's factory chart (Economy section). Harv supplied an ISM
Manufacturing PMI graphic ("9 Straight Months Of Factory Growth"). ISM's
published terms prohibit charts or time series derived from its PMI content
without written permission, so this chart tells the same story from public
domain BLS data instead, and makes it local (feedback-localize-national-studies):

  factory-jobs-100226.png      plain monogram -> RE email + Agent Hub
  factory-jobs-100226-hb.png   + wordmark     -> harvrealtor.com / .net / app

BLS_SERIES_JSON maps series id -> {"YYYY-MM": "value"} for these BLS series,
pulled from the keyless API (api.bls.gov/publicAPI/v2) on 10/02/26:
  CES3000000001         U.S. manufacturing, all employees, thousands, SA
  CEU3000000001         same, not seasonally adjusted
  SMU06000003000000001  California manufacturing, NSA
  SMU06419403000000001  San Jose-Sunnyvale-Santa Clara MSA manufacturing, NSA
  SMU06360843000000001  Oakland-Fremont-Berkeley Metropolitan Division
                        (Alameda and Contra Costa counties) manufacturing, NSA
Area names confirmed on data.bls.gov/timeseries/<id> on 10/02/26.

=============================================================================
VERIFICATION 10/02/26
=============================================================================

Left panel, U.S. SA, matches the ISM window (Oct 2025 to Sep 2026): low of
12,580 in December, 12,652 in September (+72 since December), gains in each
of the last four months (+13, +20, +15, +9). September is from this morning's
Employment Situation, preliminary.

Right panel, August 2026 vs August 2025, all not seasonally adjusted (the only
fair way to compare a metro with the nation; metro data run a month behind):
San Jose +1.4% (131.4 vs 129.6), U.S. +0.3% (12,712 vs 12,672), California
-1.2% (1,213.8 vs 1,228.3), Oakland-Fremont -5.5% (93.3 vs 98.7).
Oakland-Fremont peaked at 113.5 in September 2022; 93.3 is the lowest August
since 2016 (92.2). Every figure is asserted below from the file.

matplotlib only; build with python3.13 on Mac.
"""
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

SRC = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "100226"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
SLATE = "#6f8296"
PALE = "#a7b3c0"
BLUE = "#2b6cb0"
GRID = "#d8cdb8"
MUTED = "#8a8172"

US_SA, US_NSA, CA = "CES3000000001", "CEU3000000001", "SMU06000003000000001"
SJ, EB = "SMU06419403000000001", "SMU06360843000000001"
MONTHS = ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03",
          "2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09"]
LABELS = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]


def one(x):
    return Decimal(x).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def load():
    d = {k: {m: Decimal(v) for m, v in s.items()} for k, s in json.load(open(SRC)).items()}
    us = [d[US_SA][m] for m in MONTHS]
    assert us == [Decimal(x) for x in (12603, 12593, 12580, 12582, 12583, 12598, 12597, 12595,
                                       12608, 12628, 12643, 12652)], us
    yoy = {}
    for k in (SJ, US_NSA, CA, EB):
        a, b = d[k]["2026-08"], d[k]["2025-08"]
        yoy[k] = (a, b, one((a / b - 1) * 100))
    assert [str(yoy[k][2]) for k in (SJ, US_NSA, CA, EB)] == ["1.4", "0.3", "-1.2", "-5.5"], yoy
    eb = d[EB]
    peak = max(eb.items(), key=lambda kv: kv[1])
    assert peak == ("2022-09", Decimal("113.5")), peak
    augs = {int(m[:4]): v for m, v in eb.items() if m.endswith("-08")}
    lower = [y for y, v in augs.items() if v < augs[2026]]
    assert lower == [2016] and augs[2016] == Decimal("92.2"), (lower, augs)
    return us, yoy, peak


def build():
    us, yoy, peak = load()
    print("US SA:", [str(v) for v in us])
    print("YoY Aug:", {k: (str(a), str(b), str(c)) for k, (a, b, c) in yoy.items()})

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)

    # ---- left: U.S. factory jobs, SA ------------------------------------
    ax = fig.add_axes([0.075, 0.25, 0.42, 0.48])
    ax.set_facecolor(CREAM)
    x = list(range(len(us)))
    y = [float(v) / 1000 for v in us]                      # millions
    ax.plot(x, y, color=BLUE, lw=3, zorder=3, solid_capstyle="round")
    ax.scatter(x, y, s=28, color=BLUE, zorder=4)
    lo = us.index(min(us))
    ax.scatter([lo], [y[lo]], s=90, facecolor=CREAM, edgecolor=BLUE, lw=2.5, zorder=5)
    ax.text(lo, y[lo] - 0.0075, f"{int(us[lo]):,},000", ha="center", va="top", fontsize=11.5, color=INK)
    ax.text(lo, y[lo] - 0.0135, "December low", ha="center", va="top", fontsize=10, color=MUTED)
    ax.scatter([x[-1]], [y[-1]], s=90, color=BLUE, zorder=5)
    ax.text(x[-1] - 0.2, y[-1] + 0.006, f"{int(us[-1]):,},000", ha="right", va="bottom",
            fontsize=12.5, fontweight="bold", color=INK)
    ax.text(x[-1] - 0.2, y[-1] + 0.0145, f"+{int(us[-1] - us[lo]):,},000 since December",
            ha="right", va="bottom", fontsize=10.5, color=BLUE)
    ax.set_xticks(x)
    ax.set_xticklabels(LABELS, fontsize=11, color=MUTED)
    ax.tick_params(axis="x", length=0)
    yt = [12.56, 12.58, 12.60, 12.62, 12.64, 12.66]
    ax.set_yticks(yt)
    ax.set_yticklabels([f"{v:.2f}M" for v in yt], fontsize=10.5, color=MUTED)
    ax.tick_params(axis="y", length=0)
    ax.set_ylim(12.555, 12.685)
    ax.set_xlim(-0.5, len(us) - 0.4)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)))
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.text(0, -0.115, "2025", transform=ax.get_xaxis_transform(), ha="left", fontsize=10, color=MUTED)
    ax.text(3, -0.115, "2026", transform=ax.get_xaxis_transform(), ha="left", fontsize=10, color=MUTED)
    fig.text(0.035, 0.82, "U.S. factory jobs are rising again",
             fontsize=13.5, fontweight="bold", color=INK, ha="left", va="bottom")
    fig.text(0.035, 0.80, "Manufacturing employment, seasonally adjusted, through September",
             fontsize=11.5, color=MUTED, ha="left", va="top")

    # ---- right: August vs a year earlier, NSA ----------------------------
    bx = fig.add_axes([0.70, 0.25, 0.27, 0.48])
    bx.set_facecolor(CREAM)
    rows = [(SJ, "San Jose metro"), (US_NSA, "United States"), (CA, "California"), (EB, "Oakland-Fremont area")]
    for i, (k, name) in enumerate(rows):
        a, b, p = yoy[k]
        here = k == EB
        col = CORAL if here else (SLATE if p >= 0 else PALE)
        bx.barh(i, float(p), height=0.6, color=col, zorder=3)
        lab = f"+{p}%" if p >= 0 else f"−{abs(p)}%"
        if p >= 0:
            bx.text(float(p) + 0.15, i, lab, ha="left", va="center", fontsize=13, fontweight="bold", color=INK)
        elif here:   # long bar: label inside its end so it cannot touch the name column
            bx.text(float(p) + 0.18, i, lab, ha="left", va="center", fontsize=14,
                    fontweight="bold", color="white", zorder=5)
        else:
            bx.text(float(p) - 0.15, i, lab, ha="right", va="center", fontsize=13,
                    fontweight="bold", color=INK)
        nx = -6.4
        bx.text(nx, i - 0.12, name, ha="right", va="center", fontsize=12.5,
                fontweight="bold" if here else "normal", color=DEEP if here else INK)
        jobs = f"{int(a * 1000):,} jobs" if k not in (US_NSA,) else f"{float(a) / 1000:.2f} million jobs"
        bx.text(nx, i + 0.25, jobs, ha="right", va="center", fontsize=9.8, color=MUTED)
    bx.axvline(0, color=INK, lw=1.0, zorder=4)
    bx.set_xlim(-6.6, 2.6)
    bx.set_ylim(len(rows) - 0.4, -0.6)
    bx.axis("off")
    fig.text(0.535, 0.82, "Locally, two directions",
             fontsize=13.5, fontweight="bold", color=INK, ha="left", va="bottom")
    fig.text(0.535, 0.80, "Factory jobs, August 2026 vs a year earlier",
             fontsize=11.5, color=MUTED, ha="left", va="top")

    fig.text(0.035, 0.955, "Factories Are Hiring Again, Just Not in the East Bay",
             fontsize=24, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.905,
             "U.S. factory jobs rose for a fourth straight month in September; San Jose gained, Oakland-Fremont did not",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(
        0.035, 0.085,
        f"The Oakland-Fremont area (Alameda and Contra Costa counties) had {int(peak[1] * 1000):,} factory jobs at its "
        f"September 2022 peak; August's {int(yoy[EB][0] * 1000):,} is the lowest for an August since 2016.\n"
        "Right panel figures are not seasonally adjusted and run a month behind the national count. "
        "September U.S. figures are preliminary.",
        fontsize=10.6, color=DEEP, ha="left", va="bottom", linespacing=1.55,
    )
    fig.text(0.035, 0.030,
             "Source: U.S. Bureau of Labor Statistics, Current Employment Statistics (national, state and metro), "
             "released October 2, 2026 and earlier.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"factory-jobs-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
