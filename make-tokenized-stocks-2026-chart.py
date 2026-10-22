#!/usr/bin/env python3
"""
make-tokenized-stocks-2026-chart.py  DATA_DIR  [outdir]

The 10/22/26 daily's crypto chart. Harv attached the newsletter's "Tokenized
Stocks Take Off" graphic: monthly trading volume on Robinhood Chain, 2026,
July $526M, August $2.21B, September $11.31B, "21x since July", source CNBC.
Emits BOTH:

  tokenized-stocks-102226.png      plain HB monogram    -> RE email + Agent Hub
  tokenized-stocks-102226-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds bitwise-staking-report-oct2026.txt, pdftotext -layout of
static.bitwiseinvestments.com/Research/Bitwise-Staking-Report-Q4-2026.pdf
(released Oct. 20, 2026; titled "Q4 2026" but its data covers Q3), fetched
Oct. 22, 2026. Every number on the chart is parsed from that text.

=============================================================================
VERIFICATION 10/22/26
=============================================================================
* CNBC (Tanaya Macheel, Oct. 21, 2026) cites "the latest quarterly staking
  report by Bitwise Asset Management, published Tuesday" for all three bars.
  The report's own sentence carries the same three numbers, and they are DEX
  volume in Robinhood Stock Tokens (data: Bitwise, Allium), not all Robinhood
  Chain activity.
* 526 + 2,210 + 11,310 = 14,046, the report's $14.05 billion Q3 total.
* September / July = 21.5x by month. The report's "over 22x" is AVERAGE DAILY
  volume ($17.0M July, 30 days in Sept.: $377.1M), so both hold.
* Context from the same page: 96 Stock Tokens in circulation at the end of
  July, 193 at the end of August, stable in September; priced value at least
  $160.8 million at Sept. 30.

matplotlib; build with python3.13 on Mac.
"""
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
STAMP = "102226"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e9846b"
GREEN = "#2f7d4f"
GRID = "#d8cdb8"
MUTED = "#8a8172"


def millions(num, unit):
    v = Decimal(num)
    return v * 1000 if unit == "billion" else v


def load():
    txt = re.sub(r"\s+", " ", open(os.path.join(DATA, "bitwise-staking-report-oct2026.txt")).read())
    m = re.search(r"Volume rose from \$([\d.]+) (million|billion) in July to \$([\d.]+) (million|billion) "
                  r"in August before reaching \$([\d.]+) (million|billion) during September", txt)
    assert m, "Bitwise volume sentence not found"
    jul = millions(m.group(1), m.group(2))
    aug = millions(m.group(3), m.group(4))
    sep = millions(m.group(5), m.group(6))
    assert (jul, aug, sep) == (Decimal("526"), Decimal("2210"), Decimal("11310")), (jul, aug, sep)

    q = re.search(r"Stock Tokens generated \$([\d.]+) billion in DEX volume between July 1 and September 30", txt)
    total = Decimal(q.group(1)) * 1000
    assert abs((jul + aug + sep) - total) <= 5, (jul + aug + sep, total)

    c = re.search(r"increased from (\d+) at the end of July to (\d+) at the end of August", txt)
    tokens = (int(c.group(1)), int(c.group(2)))
    assert tokens == (96, 193), tokens

    v = re.search(r"\$([\d.]+) million by the end of the reporting period", txt)
    held = Decimal(v.group(1))
    assert held == Decimal("160.8"), held
    return jul, aug, sep, total, tokens, held


def label(mn):
    return f"${mn:,.0f}M" if mn < 1000 else f"${mn / 1000:.2f}B"


def build():
    jul, aug, sep, total, tokens, held = load()
    mult = (sep / jul).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    assert mult == Decimal("21.5"), mult

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.065, 0.13, 0.70, 0.66])
    ax.set_facecolor(CREAM)

    names = ["July", "August", "September"]
    vals = [float(jul) / 1000, float(aug) / 1000, float(sep) / 1000]
    cols = [CORAL, CORAL, GREEN]
    ax.bar(range(3), vals, width=0.58, color=cols, zorder=3)
    for i, mn in enumerate([jul, aug, sep]):
        ax.text(i, vals[i] + 0.25, label(mn), ha="center", va="bottom",
                fontsize=22 if i == 2 else 18, fontweight="bold",
                color=GREEN if i == 2 else INK, zorder=4)

    ax.set_xticks(range(3))
    ax.set_xticklabels(names, fontsize=14, color=INK)
    ax.get_xticklabels()[2].set_fontweight("bold")
    ax.set_xlim(-0.6, 2.6)
    ax.set_ylim(0, 13.2)
    ax.set_yticks([0, 3, 6, 9, 12])
    ax.set_yticklabels(["$0", "$3B", "$6B", "$9B", "$12B"], fontsize=12.5, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.axhline(0, color="#b9ad93", lw=1.2, zorder=4)

    # multiple pill, upper left in the empty space over July and August
    ax.text(0.0, 10.6, f"  {mult}x July's volume  ", ha="left", va="center", fontsize=16,
            fontweight="bold", color="white", zorder=5,
            bbox=dict(boxstyle="round,pad=0.5", facecolor=GREEN, edgecolor="none"))

    # right hand stat column
    fig.text(0.80, 0.70, "Third quarter total", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(0.80, 0.665, f"${total / 1000:.2f}B", fontsize=27, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.80, 0.55, "Stock Tokens in circulation", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(0.80, 0.515, f"{tokens[0]} → {tokens[1]}", fontsize=27, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.80, 0.445, "end of July to end of Aug.", fontsize=11.5, color=MUTED,
             ha="left", va="top")
    fig.text(0.80, 0.37, "Value of the tokens", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(0.80, 0.335, f"${held:.1f}M", fontsize=27, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.80, 0.265, "at least, priced at Sept. 30", fontsize=11.5, color=MUTED,
             ha="left", va="top")

    fig.text(0.035, 0.955, "Tokenized Stock Trading Took Off", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895,
             "Monthly trading volume in Robinhood Stock Tokens on decentralized exchanges on Robinhood Chain, 2026.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035,
             "Source: Bitwise Asset Management staking report, released Oct. 20, 2026 (data: Bitwise, Allium), as reported by CNBC. "
             "Volume is turnover, not money invested.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"tokenized-stocks-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
