#!/usr/bin/env python3
"""
make-nvidia-buyback-chart.py  BARS_JSON  [outdir]

Recreates the newsletter graphic "Nvidia Just Blew Past The Buyback Record"
("Largest single U.S. share buyback authorizations, in billions": Nvidia 2026
$150B, Apple 2024 $110B, Chevron 2023 $75B, Alphabet 2024 $70B, Microsoft 2024
$60B; source "NVIDIA, Bloomberg, company filings, Sept. 2026") for the 09/29/26
daily.

  nvidia-buyback-092926.png      plain monogram -> RE email + Agent Hub
  nvidia-buyback-092926-hb.png   + wordmark     -> harvrealtor.com / .net / app

BARS_JSON holds the verified bars, each checked against the company's own
press release or SEC filing on 09/29/26 (see the "verified" field and URL of
each entry), plus the title, subtitle, footnote and source lines. The chart
draws ONE bar per company, its largest single authorization, so the subtitle
says "by each company": Apple alone has authorized $90B or more in several
years, and a list of every authorization would be mostly Apple.

matplotlib only; build with python3.13 on Mac.
"""
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

CFG = json.load(open(sys.argv[1]))
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "092926"

CREAM = "#fdf6e8"
INK = "#1f2933"
GREEN = "#4f8a10"
SLATE = "#7d8fa3"
GRID = "#d8cdb8"
MUTED = "#8a8172"
DEEP = "#b8433a"


def esc(text):
    """Config text is plain; escape $ so matplotlib does not read it as mathtext."""
    return text.replace("$", r"\$")


def build():
    bars = CFG["bars"]
    for bar in bars:
        assert bar.get("verified"), f"unverified bar: {bar}"
    bars = sorted(bars, key=lambda b: -b["amount"])
    top = bars[0]

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    n = len(bars)
    h = 0.58
    xmax = top["amount"] * 1.30
    for i, bar in enumerate(bars):
        col = GREEN if bar is top else SLATE
        ax.add_patch(FancyBboxPatch((0, i - h / 2), bar["amount"], h,
                                    boxstyle="round,pad=0,rounding_size=0.12",
                                    mutation_aspect=1 / 18, fc=col, ec="none", zorder=3))
        amt = Decimal(str(bar["amount"])).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        ax.text(bar["amount"] + xmax * 0.012, i, f"\\${amt}B", ha="left", va="center",
                fontsize=22 if bar is top else 19, fontweight="bold",
                color=GREEN if bar is top else INK, zorder=5)
        if bar.get("note"):
            ax.text(bar["amount"] + xmax * 0.012, i + 0.34, esc(bar["note"]), ha="left", va="center",
                    fontsize=10.5, color=MUTED, zorder=5)

    ax.set_ylim(n - 0.45, -0.55)
    ax.set_xlim(0, xmax)
    ax.set_yticks(range(n))
    ax.set_yticklabels([""] * n)
    for i, bar in enumerate(bars):
        ax.text(-xmax * 0.02, i - 0.10, esc(bar["company"]), ha="right", va="center", fontsize=17,
                fontweight="bold", color=INK, transform=ax.transData)
        ax.text(-xmax * 0.02, i + 0.22, esc(bar["when"]), ha="right", va="center", fontsize=12,
                color=MUTED, transform=ax.transData)
    ax.set_xticks([])
    for sp in ("top", "right", "left", "bottom"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="both", length=0)

    fig.text(0.045, 0.945, esc(CFG["title"]), fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888, esc(CFG["subtitle"]), fontsize=14, color=MUTED, ha="left", va="top")
    fig.text(0.045, 0.112, esc(CFG["footnote"]), fontsize=11.2, color=DEEP, ha="left", va="bottom", linespacing=1.55)
    fig.text(0.045, 0.040, esc(CFG["source"]), fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5)

    fig.subplots_adjust(left=0.215, right=0.975, top=0.81, bottom=0.25)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"nvidia-buyback-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
