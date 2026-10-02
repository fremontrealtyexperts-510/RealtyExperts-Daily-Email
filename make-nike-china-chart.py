#!/usr/bin/env python3
"""
make-nike-china-chart.py  EX991_TXT  [outdir]

Recreates the supplied graphic "Nike's China Problem" for the 10/02/26 daily
(Stocks section), adding each region's dollar revenue and the reported change.

  nike-china-100226.png      plain monogram -> RE email + Agent Hub
  nike-china-100226-hb.png   + wordmark     -> harvrealtor.com / .net / app

EX991_TXT is the text of NIKE, Inc.'s Form 8-K Exhibit 99.1 (fiscal 2027 first
quarter results, filed October 1, 2026), with table cells separated by " | ":
  https://www.sec.gov/Archives/edgar/data/320187/000032018726000184/q1fy27exhibit991er.htm
Every bar and label is parsed from its DIVISIONAL REVENUES table at build time.

=============================================================================
VERIFICATION 10/02/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

  supplied graphic       Nike table, % change excluding currency changes
  Greater China -26%     -26   (reported -22; $1,180M from $1,512M)
  EMEA           -5%     -5    (reported -5;  $3,176M from $3,331M)
  APLA            0%     0     (reported -2;  $1,463M from $1,490M)
  North America  +2%     2     (reported 2;   $5,127M from $5,020M)

All four match Nike's printed currency-neutral whole numbers; nothing was
rounded. Nike prints whole percents only, so the chart does too, and it never
mixes a one decimal reported figure with the integer currency-neutral ones.
What the graphic left out: the dollars. Greater China ($1.18 billion) is now
smaller than APLA ($1.46 billion); a year ago it was larger. That comparison is
ours, from Nike's table.

The quarter is the three months ended August 31, 2026 (June to August).
Total NIKE, Inc. revenue $11,213M vs $11,720M: down 4% reported, 5% currency
neutral (asserted from the TOTAL row).

matplotlib only; build with python3.13 on Mac.
"""
import os
import re
import sys

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
GREEN = "#2f855a"
GRID = "#d8cdb8"
MUTED = "#8a8172"

REGIONS = [("North America", "North America"),
           ("Europe, Middle East & Africa", "EMEA"),
           ("Greater China", "Greater China"),
           ("Asia Pacific & Latin America", "APLA")]


def _num(s):
    return int(s.replace(",", "").replace("(", "-").replace(")", ""))


def load():
    lines = [l.strip() for l in open(SRC, encoding="utf-8", errors="ignore")]
    start = lines.index("DIVISIONAL REVENUES")
    assert "% Change Excluding Currency Changes" in lines[start + 2], lines[start + 2]
    assert "8/31/2026 | 8/31/2025" in lines[start + 4], lines[start + 4]
    rows, current = {}, None
    for l in lines[start + 5:start + 40]:
        if l in [g for g, _ in REGIONS]:
            current = l
            continue
        if current and l.startswith("Total |"):
            c = [x.strip() for x in l.split("|")]
            # Total | 5,127 | 5,020 | 2 | % | 2 | %
            vals = [x for x in c[1:] if x not in ("$", "%", "")]
            now, prior, rep, cn = (_num(v) for v in vals[:4])
            rows[current] = dict(now=now, prior=prior, rep=rep, cn=cn)
            current = None
        if l.startswith("TOTAL NIKE, INC. REVENUES"):
            vals = [x.strip() for x in l.split("|")[1:] if x.strip() not in ("$", "%", "")]
            rows["TOTAL"] = dict(now=_num(vals[0]), prior=_num(vals[1]), rep=_num(vals[2]), cn=_num(vals[3]))
            break
    assert len(rows) == 5, rows.keys()
    expect = {"North America": (5127, 5020, 2, 2), "Europe, Middle East & Africa": (3176, 3331, -5, -5),
              "Greater China": (1180, 1512, -22, -26), "Asia Pacific & Latin America": (1463, 1490, -2, 0),
              "TOTAL": (11213, 11720, -4, -5)}
    for k, v in expect.items():
        r = rows[k]
        assert (r["now"], r["prior"], r["rep"], r["cn"]) == v, (k, r)
    return rows


def money(m):
    return f"\\${m / 1000:.2f}B"   # escaped: matplotlib reads a $ pair as math


def build():
    rows = load()
    order = sorted(REGIONS, key=lambda g: rows[g[0]]["cn"])          # most negative first
    assert [s for _, s in order] == ["Greater China", "EMEA", "APLA", "North America"], order
    print("regions:", [(s, rows[g]) for g, s in order])

    fig, ax = plt.subplots(figsize=(12.8, 7.6), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    h = 0.58
    for i, (g, short) in enumerate(order):
        r = rows[g]
        v = r["cn"]
        col = CORAL if v < 0 else (GREEN if v > 0 else SLATE)
        china = short == "Greater China"
        if v != 0:
            ax.barh(i, v, height=h, color=col, zorder=3)
        else:
            ax.plot([0, 0], [i - h / 2, i + h / 2], color=SLATE, lw=5, solid_capstyle="butt", zorder=4)
        lab = "flat" if v == 0 else (f"+{v}%" if v > 0 else f"−{abs(v)}%")
        if v < 0:
            ax.text(v - 0.6, i, lab, ha="right", va="center", fontsize=19 if china else 16,
                    fontweight="bold", color=DEEP, zorder=5)
        else:
            ax.text(max(v, 0) + 0.6, i, lab, ha="left", va="center", fontsize=16,
                    fontweight="bold", color=GREEN if v > 0 else INK, zorder=5)
        # region name and dollars on the right of the zero line
        ax.text(8.0, i - 0.13, short, ha="left", va="center", fontsize=15.5,
                fontweight="bold" if china else "normal", color=INK)
        rep = "" if r["rep"] == v else f", {('+' if r['rep'] > 0 else chr(0x2212))}{abs(r['rep'])}% in dollars"
        ax.text(8.0, i + 0.22, f"{money(r['now'])}, from {money(r['prior'])}{rep}",
                ha="left", va="center", fontsize=11.2, color=MUTED)

    ax.axvline(0, color=INK, lw=1.1, zorder=4)
    ax.set_xlim(-33, 27)
    ax.set_ylim(len(order) - 0.45, -0.7)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)

    t = rows["TOTAL"]
    fig.text(0.045, 0.955, "Nike's China Problem", fontsize=26, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.895,
             "Revenue change by region from a year earlier, currency-neutral, quarter ended August 31, 2026",
             fontsize=14, color=MUTED, ha="left", va="top")
    fig.text(
        0.045, 0.092,
        f"Greater China, at {money(rows['Greater China']['now'])}, is now smaller than APLA at "
        f"{money(rows['Asia Pacific & Latin America']['now'])}; a year ago it was larger.\n"
        f"Total revenue was {money(t['now'])}, down {abs(t['rep'])}% in dollars and {abs(t['cn'])}% currency-neutral. "
        "Currency-neutral strips out exchange rate moves.",
        fontsize=11.2, color=DEEP, ha="left", va="bottom", linespacing=1.55,
    )
    fig.text(0.045, 0.034,
             "Source: NIKE, Inc. fiscal 2027 first quarter results, Form 8-K filed October 1, 2026 "
             "(divisional revenues, NIKE Brand). APLA = Asia Pacific and Latin America.",
             fontsize=10.5, color=MUTED, ha="left", va="bottom")
    fig.subplots_adjust(left=0.045, right=0.97, top=0.83, bottom=0.19)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"nike-china-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
