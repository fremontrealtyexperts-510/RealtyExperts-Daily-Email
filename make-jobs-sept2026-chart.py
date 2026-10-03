#!/usr/bin/env python3
"""
make-jobs-sept2026-chart.py  BLS_SERIES_JSON  [outdir]

The 10/03/26 daily's first jobs chart (Economy section). No newsletter on
Saturday; Harv asked for the September 2026 Employment Situation (released
Friday, October 2, 2026) written up briefly with bar charts. Emits BOTH brand
variants:

  jobs-monthly-100326.png      plain HB monogram    -> RE email + Agent Hub
  jobs-monthly-100326-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

BLS_SERIES_JSON maps series id -> {"YYYY-MM": "value"}, pulled from the keyless
BLS API (POST api.bls.gov/publicAPI/v2/timeseries/data/) on 10/03/26:
  CES0000000001  total nonfarm, all employees, thousands, SA
  CES9091000001  federal government, thousands, SA
  LNS14000000    unemployment rate, SA (October 2025 is "-": the 2025 lapse
                 in appropriations; BLS never published it)
  CES0500000003  average hourly earnings, total private, SA

=============================================================================
VERIFICATION 10/03/26
=============================================================================

Monthly changes are computed from the LEVELS in one API pull (one vintage):
  Oct 25 -140, Nov +41, Dec -17, Jan 26 +160, Feb -156, Mar +214, Apr +148,
  May +63, Jun +31, Jul -10, Aug +133, Sep +29 (preliminary).
Each matches the release text read on bls.gov (Browser pane, 10/03/26):
"+29,000"; "July was revised down by 31,000, from +21,000 to -10,000, and the
change for August was revised down by 29,000, from +162,000 to +133,000 ...
combined is 60,000 lower"; "an average monthly gain of 45,000 over the prior
12 months" (Sep 2025 to Aug 2026: 543 / 12 = 45.25).

The two dashed outlines are the PREVIOUSLY PUBLISHED values (+21 and +162),
taken from that release sentence because the API serves only the current
vintage. "Previously reported", not "first reported": +21 was July's SECOND
estimate (the 09/07/26 note records an earlier +23K print).

October 2025: federal employment -166 (CES9091000001), total private +13,
so the dip is labeled "federal job cuts". February 2026 (-156) was broad
private weakness with no verified single cause, so it carries no label.

Unemployment 4.2% (Aug 4.1%); hourly pay $37.81, +3.0% over 12 months.

matplotlib only; build with python3.13 on Mac.
"""
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

SRC = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "100326"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
SLATE = "#6f8296"
PALE = "#a7b3c0"
GRID = "#d8cdb8"
MUTED = "#8a8172"

TOTAL, FED, UR, AHE = "CES0000000001", "CES9091000001", "LNS14000000", "CES0500000003"
MONTHS = ["2025-09", "2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03",
          "2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09"]
LABELS = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]
PREVIOUS = {"Jul": 21, "Aug": 162}          # BLS release text, 10/02/26
MINUS = "−"                            # a hyphen minus can vanish at small sizes


def k(v):
    v = int(v)
    return f"+{v}K" if v > 0 else (f"{MINUS}{abs(v)}K" if v < 0 else "0K")


def load():
    d = {s: {m: Decimal(v) for m, v in ser.items()} for s, ser in json.load(open(SRC)).items()}
    t = d[TOTAL]
    chg = [t[MONTHS[i]] - t[MONTHS[i - 1]] for i in range(1, len(MONTHS))]
    assert [int(c) for c in chg] == [-140, 41, -17, 160, -156, 214, 148, 63, 31, -10, 133, 29], chg
    prior12 = (t["2026-08"] - t["2025-08"]) / 12
    assert prior12.quantize(Decimal("1"), rounding=ROUND_HALF_UP) == 45, prior12
    # revisions: the release's "combined is 60,000 lower"
    assert (PREVIOUS["Jul"] - int(chg[9])) + (PREVIOUS["Aug"] - int(chg[10])) == 60
    fed_oct = d[FED]["2025-10"] - d[FED]["2025-09"]
    assert fed_oct == -166, fed_oct
    assert d[UR]["2026-09"] == Decimal("4.2") and d[UR]["2026-08"] == Decimal("4.1")
    ahe = (d[AHE]["2026-09"] / d[AHE]["2025-09"] - 1) * 100
    assert ahe.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP) == Decimal("3.0"), ahe
    return [int(c) for c in chg], float(prior12)


def build():
    chg, avg = load()
    print("monthly:", dict(zip(LABELS, chg)), "prior 12 avg:", round(avg, 2))

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.215, 0.895, 0.565])
    ax.set_facecolor(CREAM)

    x = list(range(len(chg)))
    W = 0.62
    lab_box = dict(boxstyle="square,pad=0.12", facecolor=CREAM, edgecolor="none")

    # previously reported, drawn first so the revised bar sits on top
    for name, prev in PREVIOUS.items():
        i = LABELS.index(name)
        ax.add_patch(Rectangle((i - W / 2, 0), W, prev, facecolor="none", edgecolor=DEEP,
                               lw=1.8, ls=(0, (4, 3)), zorder=2))
        ax.text(i, prev + 5, f"was {k(prev)}", ha="center", va="bottom", fontsize=11,
                color=DEEP, zorder=6, bbox=lab_box)

    for i, v in enumerate(chg):
        sep = i == len(chg) - 1
        col = CORAL if sep else (SLATE if v >= 0 else PALE)
        ax.bar(i, v, width=W, color=col, zorder=3)
        size, weight, tcol = (17, "bold", DEEP) if sep else (12.5, "bold", INK)
        if v >= 0:
            yy, va = v + 5, "bottom"
            if LABELS[i] == "Aug":                 # inside the dashed outline
                yy = v + 4
        else:
            yy, va = v - 5, "top"
        # the cream box masks the average line where it runs through a label,
        # and the dashed outline's edges where August's label is wider than its bar
        ax.text(i, yy, k(v), ha="center", va=va, fontsize=size, fontweight=weight,
                color=tcol, zorder=6, bbox=lab_box)
    ax.text(0, chg[0] - 25, "federal\njob cuts", ha="center", va="top", fontsize=10.2,
            color=MUTED, linespacing=1.15, zorder=6)

    ax.axhline(avg, color=MUTED, lw=1.5, ls=(0, (6, 4)), zorder=4)
    ax.axhline(0, color=INK, lw=1.1, zorder=5)

    ax.set_xticks(x)
    ax.set_xticklabels(LABELS, fontsize=12, color=MUTED)
    ax.get_xticklabels()[-1].set_color(DEEP)
    ax.get_xticklabels()[-1].set_fontweight("bold")
    ax.tick_params(axis="x", length=0, pad=8)
    yt = [-150, -100, -50, 0, 50, 100, 150, 200]
    ax.set_yticks(yt)
    ax.set_yticklabels([k(v) for v in yt], fontsize=10.5, color=MUTED)
    ax.tick_params(axis="y", length=0)
    ax.set_ylim(-215, 252)
    ax.set_xlim(-0.6, len(chg) - 0.4)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.text(0, -0.125, "2025", transform=ax.get_xaxis_transform(), ha="center", fontsize=10, color=MUTED)
    ax.text(3, -0.125, "2026", transform=ax.get_xaxis_transform(), ha="center", fontsize=10, color=MUTED)

    fig.text(0.035, 0.955, "Hiring Slowed to 29,000 in September",
             fontsize=24, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.905, "Monthly change in U.S. payroll jobs, seasonally adjusted",
             fontsize=13.5, color=MUTED, ha="left", va="top")

    # legend row
    handles = [
        Rectangle((0, 0), 1, 1, facecolor="none", edgecolor=DEEP, lw=1.8, ls=(0, (4, 3))),
        Line2D([0], [0], color=MUTED, lw=1.5, ls=(0, (6, 4))),
    ]
    fig.legend(handles, ["Previously reported, before Friday's revisions",
                         f"Average for the 12 months before September: +{round(avg)}K"],
               loc="upper left", bbox_to_anchor=(0.03, 0.872), ncol=2, frameon=False,
               fontsize=11.5, handlelength=2.6, columnspacing=2.2, labelcolor=INK)

    fig.text(
        0.035, 0.085,
        f"July and August were revised down by a combined 60,000. The unemployment rate rose to 4.2% "
        f"from 4.1%, and average hourly pay was 3.0% higher than a year earlier.",
        fontsize=10.8, color=DEEP, ha="left", va="bottom",
    )
    fig.text(0.035, 0.030,
             "Source: U.S. Bureau of Labor Statistics, The Employment Situation for September 2026, "
             "released October 2, 2026. September is preliminary.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"jobs-monthly-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
