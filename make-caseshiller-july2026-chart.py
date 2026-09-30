#!/usr/bin/env python3
"""
make-caseshiller-july2026-chart.py  RELEASE_HTML  [outdir]

Recreates the supplied graphic "Where Home Prices Are Still Rising" for the
09/30/26 daily as a LOCAL chart: S&P Cotality Case-Shiller metro home prices,
one year change to July 2026, every metro ranked, the San Francisco metro
highlighted (feedback-localize-national-studies).

  caseshiller-093026.png      plain monogram -> RE email + Agent Hub
  caseshiller-093026-hb.png   + wordmark     -> harvrealtor.com / .net / app

RELEASE_HTML is the S&P Dow Jones Indices press release of September 29, 2026
saved from PR Newswire with shell curl:
  https://www.prnewswire.com/news-releases/sp-cotality-case-shiller-index-reports-annual-gain-in-july-2026-302893034.html
Every bar is parsed from its "1-Year Change (%)" column at build time (FRED
was unreachable on 09/30/26, and the release is the primary source anyway).

=============================================================================
VERIFICATION 09/30/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

  supplied graphic          release Table 2
  Chicago     +6.9%         6.86
  New York    +5.8%         5.78
  Cleveland   +4.2%         4.22
  Denver      -1.1%         -1.09
  Las Vegas   -1.3%         -1.29
  Seattle     -1.6%         -1.57
  U.S. national +1.9%       1.93

All seven match, and the three up and three down it chose are the real top
three and bottom three. What it left out is the Bay Area: the graphic showed
six metros, none of them ours. San Francisco is 3.48, fifth of the 19 metros
with a July reading, so all 19 are drawn and ours is the highlighted bar.

Asserts pin the figures above, San Francisco 3.48, Composite-20 2.47, that
Detroit is blank (S&P published no July reading for it, citing recording
delays in Wayne County), and the two month over month figures in the
footnote: San Francisco -0.61 before seasonal adjustment (Table 2) and +0.40
after (Table 3).

The San Francisco index covers the San Francisco, Oakland, Fremont metro:
Alameda, Contra Costa, Marin, San Francisco and San Mateo counties.

matplotlib only; build with python3.13 on Mac.
"""
import html as htmllib
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

SRC = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "093026"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
SLATE = "#6f8296"
PALE = "#a7b3c0"
GRID = "#d8cdb8"
MUTED = "#8a8172"


def _cells(row):
    cells = [re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", c))).strip()
             for c in re.findall(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", row)]
    return [c for c in cells if c]


def _num(cell):
    return Decimal(cell.replace("%", "").strip())


def load():
    s = open(SRC, encoding="utf-8", errors="ignore").read()
    rows, sf_nsa, sf_sa = {}, None, None
    for t in re.findall(r"(?is)<table.*?</table>", s):
        trs = [_cells(r) for r in re.findall(r"(?is)<tr.*?</tr>", t)]
        if "1-Year Change" in t:                      # Table 2
            for cells in trs:
                if len(cells) == 5 and cells[0] != "Metropolitan Area":
                    rows[cells[0]] = None if cells[4] == "--" else _num(cells[4])
                    if cells[0] == "San Francisco":
                        sf_nsa = _num(cells[2])        # July / June, not seasonally adjusted
        elif any(c[:3] == ["Metropolitan Area", "NSA", "SA"] for c in trs):   # Table 3
            for cells in trs:
                if len(cells) == 5 and cells[0] == "San Francisco":
                    assert _num(cells[1]) == sf_nsa, cells   # same NSA figure in both tables
                    sf_sa = _num(cells[2])             # July / June, seasonally adjusted
    assert len(rows) == 23, len(rows)
    assert rows["Detroit"] is None
    assert rows["Chicago"] == Decimal("6.86") and rows["New York"] == Decimal("5.78")
    assert rows["Cleveland"] == Decimal("4.22") and rows["Denver"] == Decimal("-1.09")
    assert rows["Las Vegas"] == Decimal("-1.29")
    assert rows["Seattle"] == Decimal("-1.57") and rows["San Francisco"] == Decimal("3.48")
    assert rows["U.S. National"] == Decimal("1.93") and rows["Composite-20"] == Decimal("2.47")
    assert sf_nsa == Decimal("-0.61") and sf_sa == Decimal("0.40"), (sf_nsa, sf_sa)
    return rows, sf_nsa, sf_sa


def one(x):
    return Decimal(x).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def build():
    rows, sf_nsa, sf_sa = load()
    nat = rows["U.S. National"]
    metros = sorted(((k, v) for k, v in rows.items()
                     if v is not None and not k.startswith(("Composite", "U.S."))), key=lambda kv: -kv[1])
    assert len(metros) == 19
    rank = [k for k, _ in metros].index("San Francisco") + 1
    assert [k for k, _ in metros[:3]] == ["Chicago", "New York", "Cleveland"], metros[:3]
    assert [k for k, _ in metros[-3:]] == ["Denver", "Las Vegas", "Seattle"], metros[-3:]
    assert rank == 5, rank
    print("metros:", [(k, str(v)) for k, v in metros])
    print("San Francisco rank", rank, "of", len(metros), "| national", nat)

    fig, ax = plt.subplots(figsize=(12.8, 8.8), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    h = 0.66
    for i, (name, v) in enumerate(metros):
        sf = name == "San Francisco"
        col = CORAL if sf else (SLATE if v >= 0 else PALE)
        ax.barh(i, float(v), height=h, color=col, zorder=3)
        label = f"+{one(v)}%" if v >= 0 else f"−{abs(one(v))}%"
        if v >= 0:
            ax.text(float(v) + 0.10, i, label, ha="left", va="center", fontsize=13 if sf else 11.5,
                    fontweight="bold" if sf else "normal", color=DEEP if sf else INK, zorder=5,
                    bbox=dict(boxstyle="square,pad=0.12", fc=CREAM, ec="none"))   # the national line runs behind some labels
            ax.text(-0.12, i, "San Francisco metro" if sf else name, ha="right", va="center",
                    fontsize=13 if sf else 12, fontweight="bold" if sf else "normal",
                    color=DEEP if sf else INK, zorder=5)
        else:
            ax.text(float(v) - 0.10, i, label, ha="right", va="center", fontsize=11.5, color=INK, zorder=5)
            ax.text(0.12, i, name, ha="left", va="center", fontsize=12, color=INK, zorder=5)

    ax.axvline(0, color=INK, lw=1.0, zorder=4)
    ax.axvline(float(nat), color=DEEP, lw=1.3, linestyle=(0, (5, 4)), zorder=2)
    ax.text(float(nat) + 0.08, len(metros) - 0.35, f"U.S. national\n+{one(nat)}%", ha="left", va="bottom",
            fontsize=11, color=DEEP, linespacing=1.3)

    ax.set_ylim(len(metros) - 0.4, -0.7)
    ax.set_xlim(-3.4, 8.0)
    ax.set_yticks([])
    ax.set_xticks([])
    for sp in ("top", "right", "left", "bottom"):
        ax.spines[sp].set_visible(False)

    fig.text(0.045, 0.957, "Home Prices by Metro: The Bay Area Ranks Fifth",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.910,
             "S&P Cotality Case-Shiller home price index, change from a year earlier, July 2026",
             fontsize=14, color=MUTED, ha="left", va="top")
    fig.text(
        0.045, 0.092,
        "The San Francisco metro index covers Alameda, Contra Costa, Marin, San Francisco and San Mateo counties. "
        f"It ranks number {rank} of {len(metros)} for the year.\n"
        f"From June it fell {abs(one(sf_nsa))}% before seasonal adjustment and rose {one(sf_sa)}% after. "
        "Detroit has no July reading; S&P cited recording delays.",
        fontsize=11.2, color=DEEP, ha="left", va="bottom", linespacing=1.55,
    )
    fig.text(0.045, 0.034,
             "Source: S&P Dow Jones Indices and Cotality, S&P Cotality Case-Shiller Indices release of September 29, 2026 (not seasonally adjusted).",
             fontsize=10.5, color=MUTED, ha="left", va="bottom")

    fig.subplots_adjust(left=0.045, right=0.97, top=0.855, bottom=0.17)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"caseshiller-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
