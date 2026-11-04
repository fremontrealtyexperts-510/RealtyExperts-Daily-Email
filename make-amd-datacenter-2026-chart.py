"""
make-amd-datacenter-2026-chart.py  DATA_DIR  [outdir]

The 11/04/26 daily's stock chart. Harv attached the newsletter's "AMD's Data
Center Sales Nearly Doubled" graphic: data center revenue by quarter, Q3 '25
through Q3 '26, "up 97% from a year ago". Emits BOTH:

  amd-datacenter-110426.png      plain HB monogram    -> RE email + Agent Hub
  amd-datacenter-110426-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds two Exhibit 99.1 earnings releases from SEC EDGAR (CIK 2488):
  q32026991.htm   Nov. 3, 2026 (0000002488-26-000188)  Q3'26, Q2'26, Q3'25 columns
  q12026991.htm   May 5, 2026  (0000002488-26-000072)  Q1'26, Q4'25, Q1'25 columns

=============================================================================
VERIFICATION 11/04/26
=============================================================================
* All five graphic points hold, read from the "Data Center Segment" rows of
  the segment tables, not typed: $4,341M, $5,380M, $5,775M, $6,718M, $8,546M
  -> 4.3, 5.4, 5.8, 6.7, 8.5. The Q4 '25 and Q2 '26 releases print the same
  figures in their own columns (checked by hand the same morning).
* "Up 97%": 8,546 / 4,341 = 1.9687, so +96.9%, which AMD's release rounds to
  97%. "Almost two thirds of AMD's revenue" (Market Briefs): 8,546 / 13,377 =
  63.9%. Both hold.
* The release was filed at 1:16 PM PT on Nov. 3, after the bell, so Tuesday's
  +3.65% close came BEFORE the report. Do not caption it as the reaction.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import html
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "110426"

CREAM = "#fdf6e8"
INK = "#1f2933"
GREEN = "#2f8f5b"
PALE = "#9cc9ad"
GRID = "#d8cdb8"
MUTED = "#8a8172"


def text_of(fname):
    b = open(os.path.join(DATA, fname), encoding="utf8", errors="ignore").read()
    b = re.sub(r"(?is)<(script|style).*?</\1>", "", b)
    b = re.sub(r"<[^>]+>", " ", b)
    return re.sub(r"\s+", " ", html.unescape(b))


def first_row(text, label, n):
    """First n dollar figures after the first occurrence of `label` (millions)."""
    i = text.index(label)
    vals = re.findall(r"\d[\d,]*", text[i + len(label): i + len(label) + 200])
    out = [int(v.replace(",", "")) for v in vals[:n]]
    assert len(out) == n, (label, vals)
    return out


def billions(m):
    return float((Decimal(m) / 1000).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def load():
    q3 = text_of("q32026991.htm")
    q1 = text_of("q12026991.htm")
    dc_q3 = first_row(q3, "Data Center Segment $", 3)      # Q3'26, Q2'26, Q3'25
    dc_q1 = first_row(q1, "Data Center Segment $", 3)      # Q1'26, Q4'25, Q1'25
    total = first_row(q3, "Total net revenue $", 3)        # Q3'26, Q2'26, Q3'25
    series = [dc_q3[2], dc_q1[1], dc_q1[0], dc_q3[1], dc_q3[0]]
    assert series == [4341, 5380, 5775, 6718, 8546], series
    assert [billions(m) for m in series] == [4.3, 5.4, 5.8, 6.7, 8.5]
    assert total[0] == 13377, total
    yoy = Decimal(series[-1]) / Decimal(series[0]) - 1
    assert yoy.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) == Decimal("0.97"), yoy
    share = Decimal(series[-1]) / Decimal(total[0])
    assert share.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) == Decimal("0.64"), share
    qoq = Decimal(series[-1]) / Decimal(series[-2]) - 1
    assert qoq.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) == Decimal("0.27"), qoq
    return series, total[0]


def build():
    series, total = load()
    labels = ["Q3 '25", "Q4 '25", "Q1 '26", "Q2 '26", "Q3 '26"]
    vals = [billions(m) for m in series]

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.115, 0.62, 0.70])
    ax.set_facecolor(CREAM)

    xs = range(len(vals))
    colors = [PALE] * (len(vals) - 1) + [GREEN]
    ax.bar(xs, vals, width=0.62, color=colors, zorder=3)
    for x, v in zip(xs, vals):
        ax.text(x, v + 0.18, f"\\${v:.1f}B", ha="center", va="bottom", fontsize=18, fontweight="bold",
                color=GREEN if x == len(vals) - 1 else INK, zorder=5)

    ax.set_xticks(list(xs))
    ax.set_xticklabels(labels, fontsize=14, color=INK)
    ax.set_xlim(-0.6, len(vals) - 0.4)
    ax.set_ylim(0, 10)
    ticks = [0, 2, 4, 6, 8]
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"\\${v}B" for v in ticks], fontsize=12.5, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=9)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # side panel: what the last bar means
    X = 0.735
    fig.text(X, 0.74, "Q3 '26", fontsize=14, color=MUTED, ha="left", va="top")
    fig.text(X, 0.69, "+97%", fontsize=34, fontweight="bold", color=GREEN, ha="left", va="top")
    fig.text(X, 0.60, "from a year earlier", fontsize=14, color=INK, ha="left", va="top")
    fig.text(X, 0.51, "+27%", fontsize=34, fontweight="bold", color=GREEN, ha="left", va="top")
    fig.text(X, 0.42, "from the quarter before", fontsize=14, color=INK, ha="left", va="top")
    fig.text(X, 0.33, "64%", fontsize=34, fontweight="bold", color=GREEN, ha="left", va="top")
    fig.text(X, 0.24, f"of AMD's \\${billions(total):.1f}B in sales", fontsize=14, color=INK, ha="left", va="top")

    fig.text(0.035, 0.955, "AMD's Data Center Sales Nearly Doubled", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.895, "AMD data center segment revenue by quarter, in billions of dollars.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035, "Source: AMD quarterly earnings releases (SEC 8-K, Exhibit 99.1), through Nov. 3, 2026.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"amd-datacenter-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
