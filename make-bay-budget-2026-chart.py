#!/usr/bin/env python3
"""
make-bay-budget-2026-chart.py  DATA_DIR  [outdir]

The local companion to make-housing-food-share-2026-chart.py for the 11/02/26 daily,
per Harv's standing rule that a national study with no Bay Area market in it gets a
local chart. BLS publishes metro areas on a two-year basis, so this is a separate
chart and not a bar added to the 2025 donut. Emits BOTH:

  bay-budget-110226.png      plain HB monogram    -> RE email + Agent Hub
  bay-budget-110226-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds two BLS Consumer Expenditure tables, 2023-2024, released Dec. 2025 and
still the latest metro data on Nov. 2, 2026:
  cu-region-2023-2024.xlsx     Table 1800, all consumer units and the West
  cu-msa-west-2023-2024.xlsx   Table 3033, San Francisco metro

=============================================================================
VERIFICATION 11/02/26
=============================================================================
* One publisher, one survey, one period on the chart. The 2025 national release is
  NOT mixed in: U.S. 46.1% here is 2023-2024, against 46.9% for 2025 on the donut.
* Method check against a published number: the same division on the 2025 U.S. figures
  reproduces BLS's printed 33.9%.
* Table 3033's West column (91,079 total, 31,353 housing, 11,560 food) equals Table
  1800's West mean, so the two tables agree.
* "San Francisco" is the BLS San Francisco-Oakland-Hayward metro: Alameda, Contra
  Costa, Marin, San Francisco and San Mateo counties.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import os
import sys
import warnings
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

warnings.filterwarnings("ignore")

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "110226"

CREAM = "#fdf6e8"
INK = "#1f2933"
ORANGE = "#ea580c"
BLUE = "#2563eb"
SLATE = "#a39a8a"
TRACK = "#efe6d2"
MUTED = "#8a8172"


def share(a, b):
    # round ONCE from the raw ratio
    return float((Decimal(int(a)) * 100 / Decimal(int(b))).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def rows(name):
    ws = openpyxl.load_workbook(os.path.join(DATA, name), data_only=True).worksheets[0]
    return [[(" ".join(c.split()) if isinstance(c, str) else c) for c in r] for r in ws.iter_rows(values_only=True)]


def table_1800():
    # each item is a label row, then Mean, SE and RSE rows
    rs = rows("cu-region-2023-2024.xlsx")
    assert rs[2][1] == "All consumer units" and rs[2][5] == "West", rs[2]
    out = {}
    for i, r in enumerate(rs):
        if r[0] in ("Average annual expenditures", "Food", "Housing") and r[0] not in out:
            assert rs[i + 1][0] == "Mean"
            out[r[0]] = (rs[i + 1][1], rs[i + 1][5])
    return out


def table_3033():
    rs = rows("cu-msa-west-2023-2024.xlsx")
    hdr = [str(c).replace("\n", " ") for c in rs[2]]
    sf = hdr.index("San Francisco")
    out = {}
    for r in rs:
        if r[0] in ("Average annual expenditures", "Food", "Housing") and r[0] not in out:
            out[r[0]] = (r[1], r[sf])
    return out


def load():
    a, m = table_1800(), table_3033()
    assert {k: v[1] for k, v in a.items()} == {k: v[0] for k, v in m.items()}, (a, m)
    assert (a["Average annual expenditures"][0], a["Housing"][0], a["Food"][0]) == (77907, 25853, 10077)
    assert (m["Average annual expenditures"][1], m["Housing"][1], m["Food"][1]) == (117578, 42517, 14677)
    assert share(27790, 81905) == 33.9
    out = []
    for name, tot, hs, fd in (("United States", a["Average annual expenditures"][0], a["Housing"][0], a["Food"][0]),
                              ("The West", a["Average annual expenditures"][1], a["Housing"][1], a["Food"][1]),
                              ("San Francisco metro", m["Average annual expenditures"][1], m["Housing"][1], m["Food"][1])):
        out.append(dict(name=name, housing=int(hs), hs=share(hs, tot), fs=share(fd, tot), both=share(hs + fd, tot)))
    assert [o["both"] for o in out] == [46.1, 47.1, 48.6], out
    assert [o["hs"] for o in out] == [33.2, 34.4, 36.2], out
    return out


def build():
    data = load()
    order = list(reversed(data))
    ys = list(range(len(order)))

    fig = plt.figure(figsize=(14.0, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)

    left = fig.add_axes([0.195, 0.125, 0.335, 0.60])
    right = fig.add_axes([0.585, 0.125, 0.385, 0.60])
    for ax in (left, right):
        ax.set_facecolor(CREAM)
        ax.set_yticks(ys)
        ax.tick_params(axis="both", length=0)
        ax.set_xticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_ylim(-0.6, 2.6)

    left.set_yticklabels([d["name"] for d in order], fontsize=15, color=INK)
    left.get_yticklabels()[0].set_fontweight("bold")
    right.set_yticklabels([])

    for y, d in zip(ys, order):
        here = d["name"].startswith("San")
        left.barh(y, d["housing"], height=0.56, color=ORANGE if here else SLATE, zorder=3)
        left.text(d["housing"] + 900, y, f"\\${d['housing']:,}", fontsize=17, fontweight="bold",
                  color=ORANGE if here else INK, va="center", ha="left")
        right.barh(y, 100, height=0.56, color=TRACK, zorder=2)
        right.barh(y, d["hs"], height=0.56, color=ORANGE if here else SLATE, zorder=3)
        right.barh(y, d["fs"], left=d["hs"], height=0.56, color=BLUE, zorder=3)
        right.text(d["hs"] / 2, y, f"{d['hs']:.1f}%", fontsize=14, fontweight="bold", color="white",
                   va="center", ha="center", zorder=4)
        right.text(d["hs"] + d["fs"] / 2, y, f"{d['fs']:.1f}%", fontsize=12.5, fontweight="bold", color="white",
                   va="center", ha="center", zorder=4)
        right.text(d["hs"] + d["fs"] + 3, y, f"{d['both']:.1f}%", fontsize=19, fontweight="bold",
                   color=ORANGE if here else INK, va="center", ha="left", zorder=4)
    left.set_xlim(0, 56000)
    right.set_xlim(0, 100)

    fig.text(0.195, 0.77, "Housing, dollars a year", fontsize=14, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.585, 0.77, "Housing + food, share of all spending", fontsize=14, fontweight="bold", color=INK,
             ha="left", va="top")

    fig.text(0.035, 0.955, "Housing Takes More of the Budget Here", fontsize=26, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.885, "Average household, 2023 and 2024 combined, the latest metro data from the Bureau of Labor "
                           "Statistics.", fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035, "Source: U.S. Bureau of Labor Statistics, Consumer Expenditure Surveys 2023-2024, Tables "
                           "1800 and 3033. San Francisco metro includes Alameda County.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"bay-budget-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
