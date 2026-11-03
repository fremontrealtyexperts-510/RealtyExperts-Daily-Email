#!/usr/bin/env python3
"""
make-binance-outflow-2026-chart.py  [outdir]

The 11/03/26 daily's Crypto chart. Harv attached the newsletter's "Users Rush Out
of Binance After Hack" graphic: three bars for the first window after withdrawals
reopened on Nov. 1. Emits BOTH:

  binance-outflow-110326.png      plain HB monogram    -> RE email + Agent Hub
  binance-outflow-110326-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 11/03/26
=============================================================================
* All three bars match Binance's own figures as CNBC quotes them from Binance's
  post on X ("Binance said it recorded $3.64 billion in net outflows after reopening
  withdrawals on Sunday"): $4.65 billion withdrawn and $1.01 billion deposited
  "between 6 a.m. and 3:30 p.m. UTC on Nov. 1". CNBC, published Nov. 1, 2026 7:11 PM
  EST, updated Nov. 2 12:09 AM EST. The graphic credits The Block as well; CNBC
  quotes Binance directly, so Binance via CNBC is the cited source here.
* The window is 9.5 hours. In Pacific time it ran 11 PM Saturday, Oct. 31 (PDT) to
  7:30 AM Sunday, Nov. 1 (PST); clocks fell back at 2 AM that night.
* Added context the graphic left out, same CNBC piece: the net outflow was 2.1% of
  Binance's $171 billion in total assets, the hack was a record $6.3 billion, and
  Binance says it has covered about 95% of the impacted amount, up from 90%.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "110326"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2725b"
GREEN = "#16a34a"
RED = "#dc2626"
GRID = "#d8cdb8"
MUTED = "#8a8172"

# billions of dollars, Binance via CNBC
WITHDRAWN, DEPOSITED, NET = 4.65, 1.01, 3.64
ASSETS, HACK, COVERED = 171, 6.3, 95


def build():
    assert round(WITHDRAWN - DEPOSITED, 2) == NET, (WITHDRAWN, DEPOSITED, NET)
    share = round(100 * NET / ASSETS, 1)
    assert share == 2.1, share

    rows = [("Withdrawn", WITHDRAWN, CORAL), ("Deposited", DEPOSITED, GREEN), ("Net outflow", NET, RED)]

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.20, 0.17, 0.49, 0.62])
    ax.set_facecolor(CREAM)

    ys = [2, 1, 0]
    for y, (label, v, color) in zip(ys, rows):
        ax.barh(y, v, height=0.62, color=color, zorder=3)
        ax.text(v + 0.10, y, f"${v:.2f}B", fontsize=30, fontweight="bold", color=color,
                ha="left", va="center", zorder=4)
        fig.text(0.035, 0.17 + 0.62 * (y + 0.5) / 3, label, fontsize=19, fontweight="bold",
                 color=INK, ha="left", va="center")

    ax.set_ylim(-0.5, 2.5)
    ax.set_xlim(0, WITHDRAWN * 1.36)
    ax.set_yticks([])
    ax.set_xticks([0, 1, 2, 3, 4, 5])
    ax.set_xticklabels(["$0", "$1B", "$2B", "$3B", "$4B", "$5B"], fontsize=12, color=MUTED)
    ax.tick_params(axis="x", length=0, pad=8)
    ax.grid(axis="x", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    X = 0.755
    fig.text(X, 0.75, "Net outflow was", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(X, 0.715, f"{share:.1f}%", fontsize=30, fontweight="bold", color=RED, ha="left", va="top")
    fig.text(X, 0.635, f"of Binance's ${ASSETS}B", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(X, 0.605, "in total assets", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(X, 0.515, "Stolen last week", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(X, 0.48, f"${HACK}B", fontsize=30, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(X, 0.39, "Binance says covered", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(X, 0.355, f"about {COVERED}%", fontsize=30, fontweight="bold", color=GREEN, ha="left", va="top")

    fig.text(0.035, 0.955, "Users Rush Out of Binance After the Hack", fontsize=27, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.893, "Crypto flows in the first 9.5 hours after withdrawals reopened, "
                           "11 PM Oct. 31 to 7:30 AM Nov. 1 (PT)",
             fontsize=14, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035, "Source: Binance, via CNBC (Nov. 1, 2026). Net outflow is withdrawals less deposits. "
                           "Total assets as of Oct. 28.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"binance-outflow-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
