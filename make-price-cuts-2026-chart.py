#!/usr/bin/env python3
"""
make-price-cuts-2026-chart.py  HIST_DIR  [outdir]

The 10/24/26 (Saturday) daily's Real Estate chart. No newsletter and no
supplied graphic; rates sat at 7.33% (MND) and the Fed meets Oct. 27 to 28.
This asks the buyer's question with OUR OWN data: how many sellers are
cutting their asking price, and has that changed over the year?

Emits BOTH:
  price-cuts-102426.png      plain HB monogram    -> RE email + Agent Hub
  price-cuts-102426-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

=============================================================================
SOURCE AND BASIS
=============================================================================
HIST_DIR holds 13 verbatim dumps of the dated MLS_Defined_Spread_Sheet_4
exports nearest the 24th of each month, Oct. 24, 2025 to Oct. 24, 2026
(older ones are real .xlsx on Drive, converted cell for cell with openpyxl;
June on are Google Sheets read with UNFORMATTED_VALUE). The listing level
CSVs are never committed; only the counts below.

For each pair of consecutive exports (a, b), a listing counts when it is
  on the market at b   = ACTV, NEW, BOMK, PCH (coming soon excluded: it is
                         not yet open to offers), and
  for sale at a        = ACTV, NEW, CS, BOMK, PCH, same MLS number.
It is a CUT when its list price at b is lower than at a.

  Four cities = Fremont, Hayward, Newark, Union City (continuous all year).
  Board       = the 14 cities present in every export. Milpitas joined the
                export in January 2026, so it is left out of both series.

Shares generated from the files on 10/24/26 (asserted below):
  window end    four cities         board (14)
  Nov 24, 2025   68 / 262  26.0%    295 / 1,027  28.7%
  Dec 24, 2025   30 / 186  16.1%    143 /   698  20.5%
  Jan 23, 2026   31 / 149  20.8%    110 /   517  21.3%
  Feb 23, 2026   44 / 155  28.4%    171 /   577  29.6%
  Mar 24, 2026   73 / 185  39.5%    234 /   693  33.8%
  Apr 24, 2026   80 / 214  37.4%    278 /   786  35.4%
  May 26, 2026   99 / 277  35.7%    335 /   958  35.0%
  Jun 24, 2026  116 / 300  38.7%    357 / 1,030  34.7%
  Jul 24, 2026  101 / 304  33.2%    362 / 1,049  34.5%
  Aug 24, 2026  101 / 295  34.2%    337 /   997  33.8%
  Sep 24, 2026  114 / 282  40.4%    370 /   968  38.2%
  Oct 24, 2026  105 / 308  34.1%    368 / 1,075  34.2%

matplotlib only; build with python3.13 on Mac, from the workspace so
hb-logo-mark.png resolves.
"""
import csv
import os
import statistics
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

HIST = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "102426"

CREAM = "#fdf6e8"
INK = "#1f2933"
GRID = "#d8cdb8"
MUTED = "#8a8172"
ORANGE = "#e8833a"   # four city bars
CORAL = "#e2574c"    # latest month
SLATE = "#3d4f63"    # board line

FOR_SALE = {"ACTV", "NEW", "CS", "BOMK", "PCH"}
ON_MARKET = {"ACTV", "NEW", "BOMK", "PCH"}
FOUR = {"FREMONT", "HAYWARD", "NEWARK", "UNION CITY"}
HEADER = ("MLS No,Status,DOM,Address,Unit,City,Area,LP,SP,BT,SqFt,BR,Bth,PB,"
          "Gar,GarSp,YrBlt,Acres,Lot SqFt,HOA Fee,Freq").split(",")
# (file tag, axis label)
DATES = [("102425", None), ("112425", "Nov 24\n2025"), ("122425", "Dec 24\n2025"),
         ("012326", "Jan 23\n2026"), ("022326", "Feb 23"), ("032426", "Mar 24"),
         ("042426", "Apr 24"), ("052626", "May 26"), ("062426", "Jun 24"),
         ("072426", "Jul 24"), ("082426", "Aug 24"), ("092426", "Sep 24"),
         ("102426", "Oct 24\n2026")]


def load(tag):
    with open(os.path.join(HIST, f"{tag}.csv"), newline="") as f:
        r = csv.reader(f)
        head = [h.strip() for h in next(r)]
        assert head == HEADER, (tag, head)
        out = {}
        for x in r:
            row = dict(zip(HEADER, x))
            out[row["MLS No"].strip().split(".")[0]] = row
    return out


def window(a, b, cities):
    both = cut = 0
    drops = []
    for k, rb in b.items():
        city = rb["City"].upper()
        if rb["Status"] not in ON_MARKET or city == "MILPITAS":
            continue
        if cities and city not in cities:
            continue
        ra = a.get(k)
        if not ra or ra["Status"] not in FOR_SALE:
            continue
        la, lb = float(ra["LP"]), float(rb["LP"])
        both += 1
        if lb < la - 1:
            cut += 1
            drops.append((la - lb) / la * 100)
    return both, cut, drops


def pct(n, d):
    return Decimal(n * 100) / Decimal(d)


def r1(x):
    return x.quantize(Decimal("0.1"), ROUND_HALF_UP)


def build():
    exports = {tag: load(tag) for tag, _ in DATES}
    rows = []
    for (ta, _), (tb, label) in zip(DATES, DATES[1:]):
        four = window(exports[ta], exports[tb], FOUR)
        board = window(exports[ta], exports[tb], None)
        rows.append((label, four, board))

    four_cuts = [(f[1], f[0]) for _, f, _ in rows]
    board_cuts = [(b[1], b[0]) for _, _, b in rows]
    assert four_cuts == [(68, 262), (30, 186), (31, 149), (44, 155), (73, 185), (80, 214),
                         (99, 277), (116, 300), (101, 304), (101, 295), (114, 282),
                         (105, 308)], four_cuts
    assert board_cuts[0] == (295, 1027) and board_cuts[-1] == (368, 1075), board_cuts
    # the copy's claims: a third or more of four city listings cut in every month
    # since March, and last fall's months ran lower
    shares = [pct(c, n) for c, n in four_cuts]
    assert all(s >= 33 for s in shares[4:]), shares
    assert all(s < 30 for s in shares[:4]), shares

    fig = plt.figure(figsize=(14.0, 8.4), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.07, 0.17, 0.90, 0.60])
    ax.set_facecolor(CREAM)

    xs = list(range(len(rows)))
    bshare = [float(pct(c, n)) for _, _, (n, c, _) in rows]
    for i, (label, (n, c, _), _) in enumerate(rows):
        s = pct(c, n)
        color = CORAL if i == len(rows) - 1 else ORANGE
        ax.bar(i, float(s), width=0.66, color=color, zorder=3)
        ax.text(i, float(s) / 2, f"{c} of\n{n}", ha="center", va="center", fontsize=10.5,
                color="white", fontweight="bold", zorder=5, linespacing=1.15)
        # one row of labels above every bar and the board line, so the
        # dashed line never runs behind a number
        ax.text(i, 44.0, f"{r1(s)}%", ha="center", va="bottom",
                fontsize=13.5, fontweight="bold", color=color, zorder=7)

    ax.plot(xs, bshare, color=SLATE, lw=2.2, ls=(0, (4, 3)), marker="o", ms=6.5,
            zorder=6)

    ax.set_xticks(xs)
    ax.set_xticklabels([lab for lab, _, _ in rows], fontsize=12, color=INK)
    ax.set_xlim(-0.6, len(rows) - 0.4)
    ax.set_ylim(0, 50)
    ax.set_yticks([0, 10, 20, 30, 40, 50])
    ax.set_yticklabels(["0", "10%", "20%", "30%", "40%", "50%"], fontsize=12, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=6)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # legend chips
    fig.text(0.07, 0.815, "■", color=ORANGE, fontsize=18, ha="left", va="center")
    fig.text(0.088, 0.815, "Fremont, Hayward, Newark and Union City", color=INK,
             fontsize=13.5, ha="left", va="center")
    fig.text(0.43, 0.815, "- -●- -", color=SLATE, fontsize=13.5, ha="left", va="center",
             fontweight="bold")
    fig.text(0.478, 0.815, "Board wide, 14 cities", color=INK, fontsize=13.5,
             ha="left", va="center")

    fig.text(0.035, 0.955, "Since March, About One in Three Sellers Cut Their Price",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.897, "Share of homes on the market that lowered their asking price "
             "in the month before each date", fontsize=14, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035,
             "Source: our daily Bay East MLS export nearest the 24th of each month, all property "
             "types. A home counts when it was for sale at both exports and on the market\n"
             "(active, new, back on market or price change) at the second; coming soon is excluded. "
             "Milpitas joined the export in January 2026 and is not included.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.45)
    return fig, rows


if __name__ == "__main__":
    fig, rows = build()
    out = os.path.join(OUTDIR, f"price-cuts-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    for label, (n, c, d), (bn, bc, bd) in rows:
        print(f"{label.replace(chr(10), ' '):14s} four {c:4d}/{n:4d} {r1(pct(c, n))}%  "
              f"median cut {statistics.median(d):.1f}%   board {bc:4d}/{bn:5d} {r1(pct(bc, bn))}%")
    print("wrote", out)
