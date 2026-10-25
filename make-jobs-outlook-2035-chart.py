#!/usr/bin/env python3
"""
make-jobs-outlook-2035-chart.py  DATA_DIR  [outdir]

The 10/25/26 (Sunday) daily's Economy chart. Market Briefs' "Brick by brick"
essay cites the government's ten year jobs forecast: 5.9 million new jobs,
office and admin work shedding 752,100, automation including AI the reason.
This charts that forecast from the source, every major job group, so the
reader sees where the trades and office work actually land.

Emits BOTH:
  jobs-outlook-2035-102526.png      plain HB monogram    -> RE email + Agent Hub
  jobs-outlook-2035-102526-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

=============================================================================
SOURCE
=============================================================================
DATA_DIR/bls-ep-2025-35-table-1-1.csv  BLS Employment Projections Table 1.1,
  "Employment by major occupational group, 2025 and projected 2035"
  (bls.gov/emp/tables/emp-by-major-occupational-group.htm, last modified
  Aug. 27, 2026), saved cell for cell from the live table on 10/25/26.
  Employment in thousands. Verified: the 22 groups sum to the 5,917.6 total,
  and every row's 2035 minus 2025 and percent agree with its printed change.
  BLS TED, Sept. 21, 2026: office and administrative support declines fastest
  (-4.0%) and sheds the most jobs (-752,100), with automation tools including
  AI named as the reason.

Skilled trades here = construction and extraction (47) plus installation,
maintenance, and repair (49).

matplotlib only; build with python3.13 on Mac, from the workspace so
hb-logo-mark.png resolves.
"""
import csv
import os
import sys
from decimal import Decimal

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "102526"

CREAM = "#fdf6e8"
INK = "#1f2933"
GRID = "#d8cdb8"
MUTED = "#8a8172"
ORANGE = "#e8833a"   # skilled trades
SLATE = "#3d4f63"    # computer and math
CORAL = "#e2574c"    # office and admin support
GREY = "#c4b9a3"     # everything else
MINUS = "−"     # a real minus sign; a hyphen can vanish at this size

SHORT = {
    "11-0000": "Management",
    "13-0000": "Business and financial",
    "15-0000": "Computer and math",
    "17-0000": "Architecture and engineering",
    "19-0000": "Life and social science",
    "21-0000": "Community and social service",
    "23-0000": "Legal",
    "25-0000": "Teaching and library",
    "27-0000": "Arts, design and media",
    "29-0000": "Healthcare practitioners",
    "31-0000": "Healthcare support",
    "33-0000": "Protective service",
    "35-0000": "Food prep and serving",
    "37-0000": "Building and grounds upkeep",
    "39-0000": "Personal care and service",
    "41-0000": "Sales",
    "43-0000": "Office and admin support",
    "45-0000": "Farming, fishing, forestry",
    "47-0000": "Construction and extraction",
    "49-0000": "Installation and repair",
    "51-0000": "Production",
    "53-0000": "Transportation and moving",
}
COLOR = {"43-0000": CORAL, "47-0000": ORANGE, "49-0000": ORANGE, "15-0000": SLATE}


def num(s):
    return Decimal(s.replace(",", ""))


def load():
    with open(os.path.join(DATA, "bls-ep-2025-35-table-1-1.csv"), newline="") as f:
        r = csv.reader(f)
        head = next(r)
        assert head[1] == "2025 National Employment Matrix code", head
        rows = {}
        for x in r:
            if len(x) < 7 or not x[1][:2].isdigit():
                continue
            rows[x[1]] = dict(title=x[0], e25=num(x[2]), e35=num(x[3]), chg=num(x[4]),
                              pct=num(x[5]))
    return rows


def build():
    rows = load()
    total = rows.pop("00-0000")
    assert set(rows) == set(SHORT), sorted(rows)
    assert total["chg"] == Decimal("5917.6") and total["pct"] == Decimal("3.5"), total
    assert sum(v["chg"] for v in rows.values()) == total["chg"]
    for code, v in rows.items():
        assert abs((v["e35"] - v["e25"]) - v["chg"]) <= Decimal("0.15"), code
        assert abs(v["chg"] / v["e25"] * 100 - v["pct"]) <= Decimal("0.06"), code
    off = rows["43-0000"]
    assert off["chg"] == Decimal("-752.1") and off["pct"] == Decimal("-4.0"), off
    # the copy's claims: office support loses the most jobs and declines the
    # fastest; the two trades groups add about as many as it loses; computer
    # and math grows faster than the average; health care is almost a third
    assert min(rows.values(), key=lambda v: v["chg"]) is off
    assert min(rows.values(), key=lambda v: v["pct"]) is off
    trades = rows["47-0000"]["chg"] + rows["49-0000"]["chg"]
    assert trades == Decimal("738.4"), trades
    assert rows["15-0000"]["pct"] > total["pct"]
    health = rows["29-0000"]["chg"] + rows["31-0000"]["chg"]
    assert Decimal("0.30") < health / total["chg"] < Decimal("0.334"), health

    order = sorted(rows, key=lambda c: rows[c]["chg"])     # bottom to top
    fig = plt.figure(figsize=(14.0, 10.0), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.255, 0.12, 0.70, 0.685])
    ax.set_facecolor(CREAM)

    for y, code in enumerate(order):
        v = rows[code]
        jobs = int(v["chg"] * 1000)
        c = COLOR.get(code, GREY)
        ax.barh(y, jobs, height=0.68, color=c, zorder=3)
        txt = f"+{jobs:,}" if jobs > 0 else f"{MINUS}{-jobs:,}"
        bold = code in COLOR
        if jobs >= 0:
            ax.text(jobs + 12000, y, txt, va="center", ha="left", fontsize=11.5,
                    color=c if bold else MUTED, fontweight="bold" if bold else "normal",
                    zorder=5)
        else:
            ax.text(jobs - 12000, y, txt, va="center", ha="right", fontsize=11.5,
                    color=c if bold else MUTED, fontweight="bold" if bold else "normal",
                    zorder=5)

    ax.axvline(0, color=INK, lw=1.1, zorder=4)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([SHORT[c] for c in order], fontsize=12.5, color=INK)
    for tick, code in zip(ax.get_yticklabels(), order):
        if code in COLOR:
            tick.set_fontweight("bold")
            tick.set_color(COLOR[code])
    ax.set_xlim(-1000000, 1300000)
    ax.set_ylim(-0.6, len(order) - 0.4)
    ticks = [-750000, -500000, -250000, 0, 250000, 500000, 750000, 1000000, 1250000]
    ax.set_xticks(ticks)
    def tick(t):
        if t == 0:
            return "0"
        if t >= 1000000:
            return f"+{t / 1e6:g}M"
        return f"+{t // 1000}K" if t > 0 else f"{MINUS}{-t // 1000}K"
    ax.set_xticklabels([tick(t) for t in ticks], fontsize=11.5, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=6)
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    tjobs = int(total["chg"] * 1000)
    ax.text(1250000, 4.2, f"All jobs: +{tjobs:,}\n(+{total['pct']}%)", ha="right", va="center",
            fontsize=13.5, fontweight="bold", color=INK, linespacing=1.3, zorder=6)
    ax.text(1250000, 1.6, f"Trades add +{int(trades * 1000):,}\nOffice support loses "
            f"{MINUS}{-int(off['chg'] * 1000):,}", ha="right", va="center", fontsize=12.5,
            color=INK, linespacing=1.35, zorder=6)

    # legend chips
    fig.text(0.035, 0.835, "■", color=CORAL, fontsize=18, ha="left", va="center")
    fig.text(0.053, 0.835, "Office and admin support", color=INK, fontsize=13.5, ha="left",
             va="center")
    fig.text(0.245, 0.835, "■", color=ORANGE, fontsize=18, ha="left", va="center")
    fig.text(0.263, 0.835, "Skilled trades", color=INK, fontsize=13.5, ha="left", va="center")
    fig.text(0.375, 0.835, "■", color=SLATE, fontsize=18, ha="left", va="center")
    fig.text(0.393, 0.835, "Computer and math", color=INK, fontsize=13.5, ha="left",
             va="center")
    fig.text(0.535, 0.835, "■", color=GREY, fontsize=18, ha="left", va="center")
    fig.text(0.553, 0.835, "Everything else", color=INK, fontsize=13.5, ha="left", va="center")

    title = fig.text(0.035, 0.962, "Where the Jobs Are Headed by 2035", fontsize=25,
                     fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.910, "Projected change in U.S. employment by job group, 2025 to 2035",
             fontsize=14, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.03,
             "Source: U.S. Bureau of Labor Statistics, Employment Projections 2025 to 2035, Table 1.1 "
             "(employment by major occupational group). Skilled trades = construction and\n"
             "extraction plus installation, maintenance and repair occupations. BLS ties the office "
             "and admin decline partly to automation tools, including AI.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.45)

    fig.canvas.draw()
    bb = title.get_window_extent(renderer=fig.canvas.get_renderer())
    assert bb.x1 < 0.84 * fig.get_size_inches()[0] * fig.dpi, bb.x1
    return fig, rows, order, total, trades


if __name__ == "__main__":
    fig, rows, order, total, trades = build()
    out = os.path.join(OUTDIR, f"jobs-outlook-2035-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    for code in reversed(order):
        v = rows[code]
        print(f"  {SHORT[code]:30s} {int(v['chg'] * 1000):>+10,}  {v['pct']:>+5}%")
    print(f"  total {int(total['chg'] * 1000):+,} ({total['pct']}%), trades {int(trades * 1000):+,}")
    print("wrote", out)
