#!/usr/bin/env python3
"""
make-ibond-rate-2026-chart.py  DATA_DIR  [outdir]

The 11/02/26 daily's Economy chart. Harv attached the newsletter's "I Bond Rate
Jumps to 5.51%" graphic: the rate on new Series I bonds, nine six-month issue
windows, Nov. 2022 to Nov. 2026. Emits BOTH:

  ibond-rate-110226.png      plain HB monogram    -> RE email + Agent Hub
  ibond-rate-110226-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds i-bond-rate-chart.txt: `pdftotext -layout` of TreasuryDirect's
i-bond-rate-chart.pdf ("SERIES I SAVINGS BOND INTEREST RATES EFFECTIVE NOVEMBER 1,
2026"), fetched Nov. 2, 2026.

=============================================================================
VERIFICATION 11/02/26
=============================================================================
* The rate at issue is each row's LAST column. All nine graphic points match it, and
  Treasury's fixed plus inflation formula on its history workbook rounds to the same
  nine values.
* "Highest since 2022-23" holds: nothing since the 6.89% window (Nov. 2022 to April
  2023) is above 5.51%. The next highest is 5.27% (Nov. 2023).
* Market Briefs' fixed rate claim holds: 1.40% is the highest since Nov. 2006, which
  was also 1.40%. May 2007 was 1.30%, as were Nov. 2023 and May 2024.
* TreasuryDirect page: 5.51% = 1.40% fixed + 2.04% semiannual inflation, for bonds
  issued Nov. 1, 2026 to April 30, 2027.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "110226"

CREAM = "#fdf6e8"
INK = "#1f2933"
BLUE = "#2563eb"
GREEN = "#16a34a"
GRID = "#d8cdb8"
MUTED = "#8a8172"

GRAPHIC = {"11/22": 6.89, "05/23": 4.30, "11/23": 5.27, "05/24": 4.28, "11/24": 3.11,
           "05/25": 3.98, "11/25": 4.03, "05/26": 4.26, "11/26": 5.51}
ROW = re.compile(r"^\s*(\d\d/\d\d)\s*-\s*\d\d/\d\d\s+(\d+\.\d\d)%\s+(.*)$")


def load():
    rows = []
    for line in open(os.path.join(DATA, "i-bond-rate-chart.txt")):
        m = ROW.match(line)
        if m:
            rates = re.findall(r"\d+\.\d\d", m.group(3))
            rows.append((m.group(1), float(m.group(2)), float(rates[-1])))
    assert rows[0][0] == "11/26", rows[0]
    at_issue = {k: v for k, _, v in rows}
    assert {k: at_issue[k] for k in GRAPHIC} == GRAPHIC, {k: at_issue[k] for k in GRAPHIC}
    # the headline: highest since the 6.89% window
    since = [v for k, _, v in rows[1:rows.index(next(r for r in rows if r[0] == "11/22"))]]
    assert max(since) == 5.27 and 5.51 > max(since) and at_issue["11/22"] > 5.51
    # the fixed rate claim: nothing since Nov. 2006 is above 1.40%
    fixed = [(k, f) for k, f, _ in rows]
    newest_equal = next(k for k, f in fixed[1:] if f >= 1.40)
    assert fixed[0] == ("11/26", 1.40) and newest_equal == "11/06", newest_equal
    return [(k, at_issue[k]) for k in GRAPHIC]


def build():
    pts = load()
    vals = [v for _, v in pts]
    labels = [f"{'Nov' if k[:2] == '11' else 'May'} '{k[3:]}" for k, _ in pts]
    xs = list(range(len(vals)))

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.05, 0.115, 0.755, 0.70])
    ax.set_facecolor(CREAM)

    ax.plot(xs[:-1], vals[:-1], color=BLUE, lw=3.0, solid_joinstyle="round", zorder=4)
    ax.plot(xs[-2:], vals[-2:], color=GREEN, lw=3.6, solid_capstyle="round", zorder=4)
    ax.scatter(xs[:-1], vals[:-1], s=64, color=BLUE, edgecolor=CREAM, linewidth=1.5, zorder=5)
    ax.scatter([xs[-1]], [vals[-1]], s=170, color=GREEN, edgecolor=CREAM, linewidth=2, zorder=6)

    # label sits on the open side of each turn: (dx, dy, ha, va)
    place = {0: (0, 15, "center", "bottom"), 1: (0, -17, "center", "top"), 2: (0, 15, "center", "bottom"),
             3: (12, 7, "left", "bottom"), 4: (0, -17, "center", "top"), 5: (0, 15, "center", "bottom"),
             6: (0, 15, "center", "bottom"), 7: (0, -17, "center", "top")}
    for i, (x, v) in enumerate(zip(xs[:-1], vals[:-1])):
        dx, dy, ha, va = place[i]
        ax.annotate(f"{v:.2f}%", xy=(x, v), xytext=(dx, dy), textcoords="offset points", fontsize=15,
                    fontweight="bold", color=INK, ha=ha, va=va)
    ax.annotate(f"{vals[-1]:.2f}%", xy=(xs[-1], vals[-1]), xytext=(0, 18), textcoords="offset points",
                fontsize=23, fontweight="bold", color=GREEN, ha="center", va="bottom")

    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=13.5, color=INK)
    ax.get_xticklabels()[-1].set_color(GREEN)
    ax.get_xticklabels()[-1].set_fontweight("bold")
    ax.set_xlim(-0.45, len(xs) - 0.55)
    ax.set_ylim(2.3, 7.6)
    ticks = [3, 4, 5, 6, 7]
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"{v}%" for v in ticks], fontsize=12.5, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=9)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    X = 0.83
    fig.text(X, 0.72, "Up from", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(X, 0.685, "4.26%", fontsize=26, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(X, 0.595, "Fixed part", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(X, 0.56, "1.40%", fontsize=26, fontweight="bold", color=GREEN, ha="left", va="top")
    fig.text(X, 0.49, "Highest since", fontsize=12, color=MUTED, ha="left", va="top")
    fig.text(X, 0.463, "Nov. 2006", fontsize=12, color=MUTED, ha="left", va="top")

    fig.text(0.035, 0.955, "I Bond Rate Jumps to 5.51%", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.895, "Rate on new Series I bonds, by six-month issue window. "
                           "Highest since the window that ended April 2023.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035, "Source: U.S. Treasury, TreasuryDirect Series I rate chart effective Nov. 1, 2026. "
                           "The Nov. 2026 rate covers bonds issued through April 30, 2027.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"ibond-rate-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
