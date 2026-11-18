#!/usr/bin/env python3
"""
make-political-ads-2026-chart.py  SRC_DIR  [outdir]

The 11/18/26 daily's Economy chart: our recreation of the supplied graphic
"Midterm Ad Spending Breaks Records" (total U.S. political ad spending by
election cycle, AdImpact: 2022 $8.90B, 2024 $11.20B, 2026 $12.06B), plus the
LOCAL piece: California led every state at $1.32B.

Emits BOTH:
  political-ads-111826.png      plain HB monogram    -> RE email + Agent Hub
  political-ads-111826-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

SOURCE AND VERIFICATION (AdImpact figures, read from the saved articles)
  cnbc.html  CNBC, Nov. 17, 2026: "Political advertisers spent a record $12.06
             billion during the 2025-26 elections, making it the first time a
             midterm cycle outspent a presidential cycle, according to ... AdImpact"
  wrap.html  TheWrap: "the $11.20 billion recorded during the 2023-24 cycle" and
             "Political advertising totaled $8.9 billion during the 2022 cycle,
             according to AdImpact"
  ce.html    Campaigns & Elections: "finished 8 percent above 2024 levels";
             "California and Texas ... surpassed the $1 billion mark ... at $1.32
             billion and $1.13 billion respectively"
Note: AdImpact's own Dec. 2024 cycle review said $11.1B for 2024; its current
figure is $11.20B, and 12.06 / 11.20 = +7.7%, matching "8 percent". Not
adjusted for inflation. Neutral by design: no party split, no candidates.

matplotlib only; build with python3.13 on Mac.
"""
import html
import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

SRC = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "111826"

CREAM = "#fdf6e8"
INK = "#1f2933"
GRID = "#e4d9c4"
MUTED = "#8a8172"
CORAL = "#e2574c"
SLATE = "#9aa9b8"
GREEN = "#2f7d4f"
LOCAL = "#efe3c8"


def text(name):
    s = open(os.path.join(SRC, name), encoding="utf-8", errors="ignore").read()
    s = re.sub(r"(?s)<(script|style).*?</\1>", " ", s)
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"\s+", " ", s).replace("–", "-").replace("’", "'")


def load():
    cnbc, wrap, ce = text("cnbc.html"), text("wrap.html"), text("ce.html")
    m26 = re.search(r"spent a record \$(\d+\.\d+) billion during the 2025-26 elections", cnbc)
    m24 = re.search(r"the \$(\d+\.\d+) billion recorded during the 2023-24 cycle", wrap)
    m22 = re.search(r"totaled \$(\d+\.\d+) billion during the 2022 cycle, according to AdImpact", wrap)
    mca = re.search(r"California and Texas - surpassed the \$1 billion mark for ad spending in a single cycle, "
                    r"at \$(\d+\.\d+) billion and \$(\d+\.\d+) billion", ce)
    assert m26 and m24 and m22 and mca, (m26, m24, m22, mca)
    assert "first time a midterm cycle outspent a presidential cycle" in cnbc
    assert "8 percent above 2024 levels" in ce
    v = {"2022": float(m22.group(1)), "2024": float(m24.group(1)), "2026": float(m26.group(1)),
         "ca": float(mca.group(1)), "tx": float(mca.group(2))}
    # the supplied graphic: $8.90B, $11.20B, $12.06B
    assert (v["2022"], v["2024"], v["2026"]) == (8.9, 11.2, 12.06), v
    assert round(100 * (v["2026"] / v["2024"] - 1)) == 8
    return v


def build():
    v = load()
    fig = plt.figure(figsize=(14.0, 8.6), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.05, 0.14, 0.58, 0.66])
    ax.set_facecolor(CREAM)
    labels = ["2022\nMidterm", "2024\nPresidential", "2026\nMidterm"]
    vals = [v["2022"], v["2024"], v["2026"]]
    cols = [SLATE, SLATE, CORAL]
    bars = ax.bar(range(3), vals, width=0.62, color=cols, zorder=3)
    for i, (b, val) in enumerate(zip(bars, vals)):
        ax.text(b.get_x() + b.get_width() / 2, val + 0.25, f"${val:.2f}B",
                ha="center", va="bottom", fontsize=24 if i == 2 else 20, fontweight="bold",
                color=CORAL if i == 2 else INK)
    up = 100 * (vals[2] / vals[1] - 1)
    ax.text(2, vals[2] / 2, f"+{up:.0f}%\nvs 2024", ha="center", va="center", fontsize=15,
            fontweight="bold", color="white")
    ax.set_xticks(range(3))
    ax.set_xticklabels(labels, fontsize=15, fontweight="bold", color=INK)
    ax.set_ylim(0, 14.2)
    ax.set_yticks([0, 4, 8, 12])
    ax.set_yticklabels(["$0", "$4B", "$8B", "$12B"])
    ax.tick_params(axis="y", labelsize=12, colors=MUTED, length=0)
    ax.tick_params(axis="x", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=1.0, zorder=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.035, 0.955, "Political Ad Spending Sets a Midterm Record", fontsize=27,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895, "Total U.S. political advertising by election cycle. 2026 is the first midterm "
             "to top a presidential cycle.", fontsize=13.5, color=MUTED, ha="left", va="top")

    # LOCAL panel
    fig.add_artist(FancyBboxPatch((0.675, 0.20), 0.29, 0.56, boxstyle="round,pad=0.004,rounding_size=0.015",
                                  transform=fig.transFigure, facecolor=LOCAL, edgecolor="none", zorder=0))
    fig.text(0.695, 0.725, "HERE: CALIFORNIA, 2025 TO 2026", fontsize=13, fontweight="bold",
             color=GREEN, ha="left", va="top")
    fig.text(0.695, 0.655, f"${v['ca']:.2f}B", fontsize=46, fontweight="bold", color=GREEN,
             ha="left", va="top")
    fig.text(0.695, 0.505, "Most of any state, and the first\nstate ever to pass $1 billion\nin a single cycle.",
             fontsize=14, color=INK, ha="left", va="top", linespacing=1.4)
    fig.text(0.695, 0.335, f"Next: Texas ${v['tx']:.2f}B", fontsize=14, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.695, 0.275, f"California was {100 * v['ca'] / v['2026']:.0f}% of the U.S. total.",
             fontsize=12.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.03,
             "Source: AdImpact, as reported by CNBC (Nov. 17, 2026), TheWrap and Campaigns & Elections. Not adjusted "
             "for inflation.\nAdImpact's December 2024 review put 2024 at \\$11.1B; its current figure is \\$11.20B.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.45)
    return fig, v


if __name__ == "__main__":
    fig, v = build()
    out = os.path.join(OUTDIR, f"political-ads-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    print(v)
