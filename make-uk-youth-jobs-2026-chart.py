#!/usr/bin/env python3
"""
make-uk-youth-jobs-2026-chart.py  DATA_DIR  [outdir]

The 10/23/26 daily's Economy chart. Harv attached the newsletter's "Young Brits
Losing Top-Paying Jobs" graphic: drop in payrolled workers aged 18 to 24 since
the end of 2022, Tech -30%, Tech + Finance -22%, Finance -10%, source "UK
Payroll Data via Bloomberg". Emits BOTH:

  uk-youth-jobs-102326.png      plain HB monogram    -> RE email + Agent Hub
  uk-youth-jobs-102326-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds hmrc-payrolled-industry-age-dec2025.xlsx, HMRC's "Payrolled
employments in the UK by nationality, industry, age and sex, from July 2014 to
December 2025" (released April 14, 2026; .ods converted with soffice), sheets
2 (all industries), 13 (information and communication), 14 (finance and
insurance). Every bar is computed from it.

=============================================================================
VERIFICATION 10/23/26
=============================================================================
* Bloomberg (Oct. 22, 2026) reported a Boston Consulting Group analysis of
  official payroll data. HMRC's PAYE RTI table reproduces it exactly, 18 to 24,
  December 2022 to December 2025 (non-seasonally adjusted, same month so no
  seasonal gap):
    information and communication 121,900 -> 85,300   -30.0%
    finance and insurance          85,600 -> 77,300    -9.7%
    the two combined              207,500 -> 162,600  -21.6%  (BCG: about 45,000
                                                             lost, to about 163,000)
    all industries              3,762,500 -> 3,755,700  -0.2%  (added here)
* "Tech" on the graphic is SIC section J, information and communication, which
  also covers publishing, broadcasting and telecoms; the chart says so.
* These are payrolled employments (jobs), not people.

matplotlib + openpyxl; build with python3.13 on Mac.
"""
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "102326"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e0614a"
SOFT = "#efa08f"
GREY = "#b9ad93"
GRID = "#d8cdb8"
MUTED = "#8a8172"


def pct(a, b):
    return float(((Decimal(b) / Decimal(a) - 1) * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def series(ws):
    rows = list(ws.iter_rows(values_only=True))
    hdr = rows[2]
    if "Total:\n 18 to 24" in hdr:
        t = hdr.index("Total:\n 18 to 24")
        get = lambda r: r[t]
    else:
        f, m = hdr.index("Total:\nFemale:\n18 to 24"), hdr.index("Total:\nMale:\n18 to 24")
        get = lambda r: r[f] + r[m]
    return rows[0][0], {r[0]: get(r) for r in rows[3:] if isinstance(r[0], str) and r[0][-4:].isdigit()}


def load():
    wb = openpyxl.load_workbook(os.path.join(DATA, "hmrc-payrolled-industry-age-dec2025.xlsx"),
                                read_only=True, data_only=True)
    out = {}
    for sheet, key, must in (("2", "all", "nationality and age"),
                             ("13", "tech", "information and communication"),
                             ("14", "fin", "finance and insurance")):
        title, s = series(wb[sheet])
        assert must in title, title
        out[key] = (s["December 2022"], s["December 2025"])
    assert out["tech"] == (121900, 85300), out["tech"]
    assert out["fin"] == (85600, 77300), out["fin"]
    assert out["all"] == (3762500, 3755700), out["all"]
    out["both"] = (out["tech"][0] + out["fin"][0], out["tech"][1] + out["fin"][1])
    return out


def build():
    d = load()
    bars = [
        ("Information and\ncommunication (tech)", pct(*d["tech"]), CORAL),
        ("Tech and finance\ncombined", pct(*d["both"]), CORAL),
        ("Finance and\ninsurance", pct(*d["fin"]), SOFT),
        ("All jobs, ages 18 to 24", pct(*d["all"]), GREY),
    ]
    assert [b[1] for b in bars] == [-30.0, -21.6, -9.7, -0.2], [b[1] for b in bars]
    counts = [d["tech"], d["both"], d["fin"], d["all"]]

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.25, 0.14, 0.50, 0.66])
    ax.set_facecolor(CREAM)

    ys = list(range(len(bars)))[::-1]
    for y, (name, v, col), (a, b) in zip(ys, bars, counts):
        ax.barh(y, abs(v), height=0.62, color=col, zorder=3)
        ax.text(abs(v) + 0.6, y + 0.07, f"−{abs(v):.1f}%", va="center", ha="left",
                fontsize=24, fontweight="bold", color=col if col != GREY else MUTED, zorder=4)
        ax.text(abs(v) + 0.6, y - 0.26, f"{a:,} to {b:,} jobs", va="center", ha="left",
                fontsize=11.5, color=MUTED, zorder=4)
        ax.text(-0.8, y, name, va="center", ha="right", fontsize=14.5, fontweight="bold", color=INK)

    ax.set_xlim(0, 41)
    ax.set_ylim(-0.6, len(bars) - 0.4)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.79, 0.70, "Young people's jobs", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(0.79, 0.665, "overall: flat", fontsize=22, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.79, 0.58, "The squeeze is in the\nbest paid fields, not\nthe whole job market.",
             fontsize=12.5, color=MUTED, ha="left", va="top", linespacing=1.4)
    fig.text(0.79, 0.43, "Jobs lost in tech\nand finance", fontsize=13, color=MUTED, ha="left", va="top",
             linespacing=1.3)
    fig.text(0.79, 0.355, f"{d['both'][0] - d['both'][1]:,}", fontsize=27, fontweight="bold",
             color=CORAL, ha="left", va="top")

    fig.text(0.035, 0.955, "Young Brits Are Losing Tech and Finance Jobs", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895,
             "Change in UK payrolled jobs held by 18 to 24 year olds, December 2022 to December 2025.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035,
             "Source: HM Revenue and Customs, payrolled employments by industry and age (PAYE Real Time Information),\n"
             "released April 2026. The analysis was first reported by Bloomberg, from Boston Consulting Group.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"uk-youth-jobs-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
