#!/usr/bin/env python3
"""
make-jobs-hiring-sept2026-chart.py  BLS_SERIES_JSON  [outdir]

The 10/03/26 daily's second jobs chart (Economy section): who did the hiring
over the past year nationally, and how the Bay Area compares
(feedback-localize-national-studies). Emits BOTH brand variants:

  jobs-hiring-100326.png      plain HB monogram    -> RE email + Agent Hub
  jobs-hiring-100326-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

BLS_SERIES_JSON is the same keyless BLS API pull (10/03/26) used by
make-jobs-sept2026-chart.py. Series used here:
  national, SA, thousands (left panel, September 2025 to September 2026):
    CES0000000001 total nonfarm          CES6562000001 health care + social assistance
    CES6000000001 prof. + business svcs  CES2000000001 construction
    CES7000000001 leisure + hospitality  CES3000000001 manufacturing
    CES5500000001 financial activities   CES5000000001 information
    CES9000000001 government
    not shown (seven smaller supersectors): CES1000000001 mining and logging,
    CES4142000001 wholesale, CES4200000001 retail, CES4300000001 transportation
    and warehousing, CES4422000001 utilities, CES6561000001 private education,
    CES8000000001 other services
  local, NOT seasonally adjusted, thousands (right panel, August 2026 vs
  August 2025; metro data run a month behind the national release):
    SMU06419400000000001  San Jose-Sunnyvale-Santa Clara MSA
    SMU06418840000000001  San Francisco-San Mateo-Redwood City Metropolitan
                          Division (name confirmed on data.bls.gov 10/03/26)
    SMU06000000000000001  California
    CEU0000000001         United States
    SMU06360840000000001  Oakland-Fremont-Berkeley Metropolitan Division
                          (Alameda and Contra Costa counties)

=============================================================================
VERIFICATION 10/03/26 (every printed number is asserted below)
=============================================================================

Left: all industries +496; health care and social assistance +520.4, MORE
than the whole economy, so everything else combined was slightly negative.
Professional and business services +123, construction +109, leisure and
hospitality +62, manufacturing +40; financial activities -107, information
-120, government -216. The seven not shown sum to +85.4. Supersectors sum to
496.8 against the separately estimated total of 496 (rounding; no residual
bar is drawn, so nothing has to reconcile on the chart).

Right (August vs August, NSA): San Jose +1.6% (1,180.8 vs 1,162.3), San
Francisco and San Mateo +1.1% (1,131.4 vs 1,119.5), California +0.7%
(18,103.8 vs 17,982.3), U.S. +0.3% (158,905 vs 158,424), Oakland-Fremont
+0.2% (1,184.1 vs 1,182.3). Percentages rounded half up with Decimal.

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
STAMP = "100326"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
SLATE = "#6f8296"
PALE = "#a7b3c0"
GRID = "#d8cdb8"
MUTED = "#8a8172"
MINUS = "−"

INDUSTRIES = [  # (series, label)
    ("CES6562000001", "Health care and social assistance"),
    ("CES6000000001", "Professional and business services"),
    ("CES2000000001", "Construction"),
    ("CES7000000001", "Leisure and hospitality"),
    ("CES3000000001", "Manufacturing"),
    ("CES5500000001", "Financial activities"),
    ("CES5000000001", "Information"),
    ("CES9000000001", "Government"),
]
NOT_SHOWN = ["CES1000000001", "CES4142000001", "CES4200000001", "CES4300000001",
             "CES4422000001", "CES6561000001", "CES8000000001"]
AREAS = [  # (series, name, sub)
    ("SMU06419400000000001", "San Jose metro", None),
    ("SMU06418840000000001", "San Francisco and San Mateo", None),
    ("SMU06000000000000001", "California", None),
    ("CEU0000000001", "United States", None),
    ("SMU06360840000000001", "Oakland-Fremont area", "Alameda and Contra Costa"),
]
HOME = "SMU06360840000000001"


def r0(x):
    return int(Decimal(x).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def r1(x):
    return Decimal(x).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def kfmt(v):
    return f"+{v}K" if v >= 0 else f"{MINUS}{abs(v)}K"


def load():
    d = {s: {m: Decimal(v) for m, v in ser.items()} for s, ser in json.load(open(SRC)).items()}
    yr = lambda s: d[s]["2026-09"] - d[s]["2025-09"]
    total = yr("CES0000000001")
    rows = [(lab, yr(s)) for s, lab in INDUSTRIES]
    assert total == 496, total
    assert [r0(v) for _, v in rows] == [520, 123, 109, 62, 40, -107, -120, -216], rows
    assert rows[0][1] > total                       # health care beat the whole economy
    rest = sum(yr(s) for s in NOT_SHOWN)
    assert r0(rest) == 85, rest
    areas = []
    for s, name, sub in AREAS:
        a, b = d[s]["2026-08"], d[s]["2025-08"]
        areas.append((s, name, sub, a, r1((a / b - 1) * 100)))
    assert [str(p) for *_, p in areas] == ["1.6", "1.1", "0.7", "0.3", "0.2"], areas
    return total, rows, rest, areas


def jobs_label(s, a):
    if s in ("SMU06000000000000001", "CEU0000000001"):
        return f"{float(a) / 1000:.1f} million jobs"
    return f"{int(a * 1000):,} jobs"


def build():
    total, rows, rest, areas = load()
    print("total", total, "rows", [(l, str(v)) for l, v in rows], "not shown", rest)
    print("areas", [(n, str(a), str(p)) for _, n, _, a, p in areas])

    fig = plt.figure(figsize=(14.0, 8.4), dpi=100)
    fig.patch.set_facecolor(CREAM)

    # ---- left: U.S. by industry, 12 months ---------------------------------
    ax = fig.add_axes([0.272, 0.17, 0.285, 0.585])
    ax.set_facecolor(CREAM)
    ys = [0] + [i + 1.35 for i in range(len(rows))]
    vals = [int(total)] + [r0(v) for _, v in rows]
    names = ["All industries"] + [lab for lab, _ in rows]
    for j, (y, v, nm) in enumerate(zip(ys, vals, names)):
        col = INK if j == 0 else (CORAL if j == 1 else (SLATE if v >= 0 else PALE))
        ax.barh(y, v, height=0.66, color=col, zorder=3)
        bold = j in (0, 1)
        if v >= 0:
            ax.text(v + 10, y, kfmt(v), ha="left", va="center", fontsize=13 if bold else 12,
                    fontweight="bold", color=DEEP if j == 1 else INK, zorder=5)
        else:     # across the zero line: the bar end is too close to the name column
            ax.text(10, y, kfmt(v), ha="left", va="center", fontsize=12,
                    fontweight="bold", color=INK, zorder=5)
        ax.text(-262, y, nm, ha="right", va="center", fontsize=12.2,
                fontweight="bold" if bold else "normal", color=DEEP if j == 1 else INK)
    ax.axhline(0.68, xmin=0.0, xmax=1.0, color=GRID, lw=1.0)
    ax.axvline(0, color=INK, lw=1.0, zorder=4)
    ax.set_xlim(-250, 640)
    ax.set_ylim(ys[-1] + 0.6, -0.6)
    ax.axis("off")
    fig.text(0.035, 0.80, "U.S. jobs added or lost, September 2025 to September 2026",
             fontsize=13.2, fontweight="bold", color=INK, ha="left", va="bottom")
    fig.text(0.035, 0.785, "By industry, seasonally adjusted",
             fontsize=11.5, color=MUTED, ha="left", va="top")

    # ---- right: Bay Area, August vs August, NSA ----------------------------
    bx = fig.add_axes([0.80, 0.17, 0.165, 0.585])
    bx.set_facecolor(CREAM)
    ys2 = [i * 1.35 for i in range(len(areas))]
    for y, (s, name, sub, a, p) in zip(ys2, areas):
        home = s == HOME
        bx.barh(y, float(p), height=0.62, color=CORAL if home else SLATE, zorder=3)
        bx.text(float(p) + 0.05, y, f"+{p}%", ha="left", va="center", fontsize=13,
                fontweight="bold", color=DEEP if home else INK, zorder=5)
        bx.text(-0.12, y - 0.18, name, ha="right", va="center", fontsize=12.2,
                fontweight="bold" if home else "normal", color=DEEP if home else INK)
        bx.text(-0.12, y + 0.26, sub if sub else jobs_label(s, a), ha="right", va="center",
                fontsize=10, color=DEEP if home else MUTED)
    bx.axvline(0, color=INK, lw=1.0, zorder=4)
    bx.set_xlim(0, 2.25)
    bx.set_ylim(ys2[-1] + 0.75, -0.75)
    bx.axis("off")
    fig.text(0.60, 0.80, "Bay Area jobs vs a year earlier",
             fontsize=13.2, fontweight="bold", color=INK, ha="left", va="bottom")
    fig.text(0.60, 0.785, "August 2026, the latest local count",
             fontsize=11.5, color=MUTED, ha="left", va="top")

    fig.text(0.035, 0.955, "Who Is Still Hiring",
             fontsize=24, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.905,
             "Health care added more jobs over the past year than the U.S. economy did overall. "
             "Locally, San Jose led and the East Bay was flat.",
             fontsize=13.2, color=MUTED, ha="left", va="top")
    fig.text(
        0.035, 0.085,
        f"Seven smaller industries, together +{r0(rest)}K, are not shown. Bay Area figures are not seasonally "
        f"adjusted and run a month behind the national count.",
        fontsize=10.8, color=DEEP, ha="left", va="bottom",
    )
    fig.text(0.035, 0.030,
             "Source: U.S. Bureau of Labor Statistics, Current Employment Statistics, national through "
             "September 2026 and state and metro through August 2026.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"jobs-hiring-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
