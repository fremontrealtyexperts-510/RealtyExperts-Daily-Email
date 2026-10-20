#!/usr/bin/env python3
"""
make-newhomes-contract-2026-chart.py  HIST_DIR  [outdir]

The 10/20/26 daily's LOCAL companion to make-builder-confidence-2026-chart.py.
NAHB's index is national (plus a West regional average), so per the KEEP IT
LOCAL rule this asks the same question of our own MLS export: are buyers
signing on new construction here as readily as they were in the spring?

Emits BOTH:
  newhomes-contract-102026.png      plain HB monogram    -> RE email + Agent Hub
  newhomes-contract-102026-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

=============================================================================
SOURCE AND BASIS
=============================================================================
HIST_DIR holds verbatim CSV dumps of the dated MLS_Defined_Spread_Sheet_4
exports nearest the 20th of each month in 2026 (June 18, since there is no
June 19 to 21 export), pulled from the Drive archive with the service account
(older files are real .xlsx, converted cell for cell with openpyxl). The
listing level CSVs are never committed; only the counts asserted below.

  New construction  = YrBlt 2025 or 2026 (built this year or last; the MLS
                      export has no separate new construction flag).
  For sale          = ACTV, NEW, CS, BOMK, PCH (the ledger's live basis).
  In contract       = PEND (same basis as make-incontract-yoy-chart.py).
  Share in contract = in contract / (for sale + in contract).
  Cities            = all 15 in the export (Milpitas is present all year).

Counts generated from the files on 10/20/26:
            new: for sale / in contract     resale: for sale / in contract
  Jan 20          75 / 43                       1,132 / 457
  Jun 18          96 / 48                       2,154 / 805
  Oct 20         109 / 31                       1,953 / 679
Year apart check (copy only, 14 cities without Milpitas): new homes in
contract 45 on Oct. 20, 2025 (built 2024 or 2025) vs 25 now; for sale 99 vs 100.

matplotlib only; build with python3.13 on Mac.
"""
import csv
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

HIST = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "102026"

CREAM = "#fdf6e8"
INK = "#1f2933"
GRID = "#e4d9c4"
MUTED = "#8a8172"
CORAL = "#e2574c"     # new construction
BLUE = "#2f6f9f"      # resale
LIVE = {"ACTV", "NEW", "CS", "BOMK", "PCH"}
HEADER = ("MLS No,Status,DOM,Address,Unit,City,Area,LP,SP,BT,SqFt,BR,Bth,PB,"
          "Gar,GarSp,YrBlt,Acres,Lot SqFt,HOA Fee,Freq").split(",")
SNAPS = [("Jan", "012026"), ("Feb", "022026"), ("Mar", "032026"), ("Apr", "042026"),
         ("May", "052026"), ("Jun", "061826"), ("Jul", "072026"), ("Aug", "082026"),
         ("Sep", "092026"), ("Oct", "102026")]
NOTICE = ("Based on information from the Bay East Association of REALTORS® (Bay East MLS) "
          "as of Jan. 20 to Oct. 20, 2026; not verified by broker or MLS.")


def year_built(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def counts(path):
    with open(path, newline="") as f:
        r = csv.reader(f)
        head = next(r)
        assert head == HEADER, (path, head)
        rows = [dict(zip(HEADER, x)) for x in r]
    cities = {x["City"].strip().upper() for x in rows}
    assert len(cities) == 15 and "MILPITAS" in cities, (path, sorted(cities))
    new = [x for x in rows if year_built(x["YrBlt"]) >= 2025]
    old = [x for x in rows if year_built(x["YrBlt"]) < 2025]
    c = lambda sel, st: sum(1 for x in sel if x["Status"] in st)
    return dict(new_sale=c(new, LIVE), new_pend=c(new, {"PEND"}),
                old_sale=c(old, LIVE), old_pend=c(old, {"PEND"}))


def share(pend, sale):
    return Decimal(pend) / Decimal(pend + sale) * 100


def pct(d):
    return int(d.quantize(Decimal("1"), ROUND_HALF_UP))


def build():
    data = [counts(os.path.join(HIST, f"{stamp}.csv")) for _, stamp in SNAPS]
    assert (data[0]["new_sale"], data[0]["new_pend"]) == (75, 43), data[0]
    assert (data[5]["new_sale"], data[5]["new_pend"]) == (96, 48), data[5]
    assert (data[-1]["new_sale"], data[-1]["new_pend"]) == (109, 31), data[-1]
    assert (data[-1]["old_sale"], data[-1]["old_pend"]) == (1953, 679), data[-1]
    new = [share(d["new_pend"], d["new_sale"]) for d in data]
    old = [share(d["old_pend"], d["old_sale"]) for d in data]
    # the story the copy tells: new outsold resale every month through June; since
    # July new ran 21% to 28% and trailed resale in three of four months (August
    # was the exception, 27.9% vs 26.1%), and it trails now
    assert all(n > o for n, o in zip(new[:6], old[:6])), (new, old)
    assert min(new[:6]) > 32 and max(new[6:]) < Decimal("28.5"), new
    assert [n < o for n, o in zip(new[6:], old[6:])] == [True, False, True, True], (new, old)

    x = list(range(len(SNAPS)))
    nf = [float(v) for v in new]
    of = [float(v) for v in old]

    fig = plt.figure(figsize=(14.0, 8.4), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.06, 0.17, 0.90, 0.62])
    ax.set_facecolor(CREAM)

    # where new construction fell behind resale
    ax.fill_between(x[5:], nf[5:], of[5:], where=[n < o for n, o in zip(nf[5:], of[5:])],
                    interpolate=True, color=CORAL, alpha=0.10, lw=0, zorder=1)

    ax.plot(x, of, color=BLUE, lw=2.8, marker="o", ms=7, zorder=4)
    ax.plot(x, nf, color=CORAL, lw=3.6, marker="o", ms=9, zorder=5)
    for i in x:
        hi_new = nf[i] >= of[i]
        for vals, color, is_new in ((nf, CORAL, True), (of, BLUE, False)):
            above = (is_new == hi_new)
            ax.text(i, vals[i] + (0.75 if above else -0.75), f"{pct(new[i] if is_new else old[i])}%",
                    fontsize=14 if is_new else 12.5, fontweight="bold", color=color,
                    ha="center", va="bottom" if above else "top", zorder=6)

    ax.text(0.9, 39.3, "January to June: new homes outsold resale every month",
            fontsize=13, color=INK, ha="left", va="center", style="italic")
    ax.text(7.5, 15.4, "Since July: below resale in three of four months",
            fontsize=13, color=CORAL, fontweight="bold", ha="center", va="center",
            style="italic")

    last = data[-1]
    first = data[0]
    ax.text(x[-1] + 0.12, 33.6,
            f"October: {last['new_pend']} of {last['new_pend'] + last['new_sale']}\n"
            f"new homes in contract.\n{last['new_sale']} for sale, up from\n"
            f"{first['new_sale']} in January.",
            fontsize=12, color=INK, ha="right", va="top", linespacing=1.35,
            bbox=dict(boxstyle="round,pad=0.45", facecolor="white", edgecolor=GRID))

    ax.set_xlim(-0.4, len(SNAPS) - 0.6)
    ax.set_ylim(13, 41)
    ax.set_xticks(x)
    ax.set_xticklabels([m for m, _ in SNAPS], fontsize=14, fontweight="bold", color=INK)
    ax.set_yticks([15, 20, 25, 30, 35, 40])
    ax.set_yticklabels([f"{v}%" for v in (15, 20, 25, 30, 35, 40)])
    ax.tick_params(axis="y", labelsize=12, colors=MUTED, length=0)
    ax.tick_params(axis="x", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=1.0, zorder=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    from matplotlib.lines import Line2D
    fig.add_artist(Line2D([0.060, 0.076, 0.092], [0.835] * 3, color=CORAL, lw=3.6,
                          marker="o", ms=8, markevery=[1], transform=fig.transFigure))
    fig.text(0.100, 0.835, "New construction (built 2025 or 2026)", color=INK,
             fontsize=13.5, ha="left", va="center")
    fig.add_artist(Line2D([0.400, 0.416, 0.432], [0.835] * 3, color=BLUE, lw=2.8,
                          marker="o", ms=6.5, markevery=[1], transform=fig.transFigure))
    fig.text(0.440, 0.835, "Resale (older homes)", color=INK, fontsize=13.5,
             ha="left", va="center")

    fig.text(0.035, 0.955, "New Homes Are Selling Slower Here, Too", fontsize=27,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.893,
             "Share of listings in contract, 15 East Bay cities on our MLS export, 2026. "
             "Snapshot near the 20th of each month.",
             fontsize=13.2, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.030,
             "Source: our daily Bay East MLS export, Jan. 20, Feb. 20, Mar. 20, Apr. 20, May 20, "
             "June 18, July 20, Aug. 20, Sept. 20 and Oct. 20, 2026, all property types.\n"
             "In contract = pending. For sale = active, new, coming soon, back on market and price "
             "change. New construction = year built 2025 or 2026.\n" + NOTICE,
             fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.45)
    return fig, data, new, old


if __name__ == "__main__":
    fig, data, new, old = build()
    out = os.path.join(OUTDIR, f"newhomes-contract-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    for (m, _), d, n, o in zip(SNAPS, data, new, old):
        print(f"{m}  new {d['new_sale']:>3} sale {d['new_pend']:>3} pend {float(n):5.1f}%   "
              f"resale {d['old_sale']:>5,} sale {d['old_pend']:>4} pend {float(o):5.1f}%")
