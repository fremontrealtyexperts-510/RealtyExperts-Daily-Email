#!/usr/bin/env python3
"""
make-caseshiller-sept2026-chart.py  RELEASE_HTML  BLS_CPI_JSON  [outdir]

The 11/25/26 daily's Real Estate chart. Market Briefs ran "Inflation 16, Homes 0":
home prices up 2.1% in September, inflation 3.7%, homes down after inflation 16
months running. Checked at the primary source, the S&P Dow Jones Indices release
of Nov. 24, 2026 (press.spglobal.com, saved with curl):
  "The S&P Cotality Case-Shiller National Home Price Index rose 2.1% year over
   year in September ... Consumer prices rose 3.7% year over year in September
   ... marking the 16th consecutive month in which U.S. home prices declined in
   real terms."  All three MB figures are right.

KEEP IT LOCAL: every metro is drawn, ranked, against INFLATION, with the San
Francisco metro (Alameda, Contra Costa, Marin, San Francisco, San Mateo; NOT
Milpitas, which is Santa Clara County) highlighted. The inflation line is BLS
CPI-U, U.S. city average, not seasonally adjusted (CUUR0000SA0), September 2026
over September 2025 = 3.738%, computed from BLS_CPI_JSON (keyless v1 API:
api.bls.gov/publicAPI/v1/timeseries/data/CUUR0000SA0). San Francisco is +3.73%,
so it matches inflation to the rounding and misses it by 0.01 point; four metros
beat it (Chicago, New York, Miami, Cleveland). The chart says exactly that.

Bars are parsed from Table 2's "1-Year Change (%)" column at build time; the
asserts pin the release's figures. Detroit has no September reading (S&P cites
Wayne County recording delays).

  caseshiller-112526.png      plain monogram -> RE email + Agent Hub
  caseshiller-112526-hb.png   + wordmark     -> harvrealtor.com / .net / app
"""
import json
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
CPI = sys.argv[2]
OUTDIR = sys.argv[3] if len(sys.argv) > 3 else "."
STAMP = "112526"

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
    assert rows["Chicago"] == Decimal("6.87") and rows["New York"] == Decimal("5.76")
    assert rows["Miami"] == Decimal("4.57") and rows["Cleveland"] == Decimal("3.98")
    assert rows["Seattle"] == Decimal("-1.88") and rows["Denver"] == Decimal("-0.99") and rows["Dallas"] == Decimal("-0.90")
    assert rows["San Francisco"] == Decimal("3.73")
    assert rows["U.S. National"] == Decimal("2.09") and rows["Composite-20"] == Decimal("2.56")
    assert sf_nsa == Decimal("0.29") and sf_sa == Decimal("0.86"), (sf_nsa, sf_sa)
    return rows, sf_nsa, sf_sa


def cpi_yoy():
    d = json.load(open(CPI))["Results"]["series"][0]["data"]
    v = {(r["year"], r["period"]): Decimal(r["value"]) for r in d if r["value"].replace(".", "").isdigit()}
    y = (v[("2026", "M09")] / v[("2025", "M09")] - 1) * 100
    assert y.quantize(Decimal("0.001")) == Decimal("3.738"), y
    return y


def one(x):
    return Decimal(x).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def build():
    rows, sf_nsa, sf_sa = load()
    cpi = cpi_yoy()
    nat = rows["U.S. National"]
    metros = sorted(((k, v) for k, v in rows.items()
                     if v is not None and not k.startswith(("Composite", "U.S."))), key=lambda kv: -kv[1])
    assert len(metros) == 19
    rank = [k for k, _ in metros].index("San Francisco") + 1
    beat = [k for k, v in metros if v > cpi]
    assert beat == ["Chicago", "New York", "Miami", "Cleveland"], beat
    assert rank == 5 and rows["San Francisco"] < cpi and one(rows["San Francisco"]) == one(cpi), (rank, cpi)
    print("metros:", [(k, str(v)) for k, v in metros])
    print("San Francisco rank", rank, "| CPI", cpi.quantize(Decimal("0.001")), "| national", nat)

    fig, ax = plt.subplots(figsize=(12.8, 8.8), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    h = 0.66
    for i, (name, v) in enumerate(metros):
        sf = name == "San Francisco"
        col = CORAL if sf else (SLATE if v > cpi else (PALE if v >= 0 else "#c9d1da"))
        ax.barh(i, float(v), height=h, color=col, zorder=3)
        label = (f"+{v}%" if sf else f"+{one(v)}%") if v >= 0 else f"−{abs(one(v))}%"
        if v >= 0:
            ax.text(float(v) + 0.10, i, label, ha="left", va="center", fontsize=13 if sf else 11.5,
                    fontweight="bold" if sf else "normal", color=DEEP if sf else INK, zorder=5,
                    bbox=dict(boxstyle="square,pad=0.12", fc=CREAM, ec="none"))
            ax.text(-0.12, i, "San Francisco metro" if sf else name, ha="right", va="center",
                    fontsize=13 if sf else 12, fontweight="bold" if sf else "normal",
                    color=DEEP if sf else INK, zorder=5)
        else:
            ax.text(float(v) - 0.10, i, label, ha="right", va="center", fontsize=11.5, color=INK, zorder=5)
            ax.text(0.12, i, name, ha="left", va="center", fontsize=12, color=INK, zorder=5)

    ax.axvline(0, color=INK, lw=1.0, zorder=4)
    ax.axvline(float(cpi), color=DEEP, lw=1.6, linestyle=(0, (5, 4)), zorder=2)
    ax.text(float(cpi) + 0.08, len(metros) - 0.35, f"Inflation\n+{cpi.quantize(Decimal('0.01'))}%", ha="left",
            va="bottom", fontsize=11.5, color=DEEP, fontweight="bold", linespacing=1.3)
    ax.axvline(float(nat), color=MUTED, lw=1.1, linestyle=(0, (2, 3)), zorder=2)
    ax.text(float(nat) + 0.08, len(metros) - 0.35, f"U.S. home prices\n+{one(nat)}%", ha="left", va="bottom",
            fontsize=11, color=MUTED, linespacing=1.3)

    ax.set_ylim(len(metros) - 0.4, -0.7)
    ax.set_xlim(-3.4, 8.0)
    ax.set_yticks([])
    ax.set_xticks([])
    for sp in ("top", "right", "left", "bottom"):
        ax.spines[sp].set_visible(False)

    fig.text(0.045, 0.957, "Home Prices vs. Inflation: Four Metros Beat It",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.910,
             "S&P Cotality Case-Shiller home prices, change from a year earlier, September 2026, against consumer prices",
             fontsize=14, color=MUTED, ha="left", va="top")
    fig.text(
        0.045, 0.092,
        f"The San Francisco metro (Alameda, Contra Costa, Marin, San Francisco, San Mateo) rose {rows['San Francisco']}% against "
        f"inflation of {cpi.quantize(Decimal('0.01'))}%,\neven to the rounding, and ranks {rank} of {len(metros)}. "
        f"Nationally, prices have trailed inflation 16 months in a row, says S&P.",
        fontsize=11.2, color=DEEP, ha="left", va="bottom", linespacing=1.55,
    )
    fig.text(0.045, 0.034,
             "Sources: S&P Dow Jones Indices and Cotality, release of Nov. 24, 2026; BLS CPI-U, U.S. city average. Detroit: no September reading.",
             fontsize=10.5, color=MUTED, ha="left", va="bottom")

    fig.subplots_adjust(left=0.045, right=0.97, top=0.855, bottom=0.17)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"caseshiller-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
