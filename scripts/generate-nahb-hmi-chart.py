#!/usr/bin/env python3
"""Generate the NAHB Housing Market Index chart as a PNG.

Rebuilds Market Briefs' 12-month bar chart in the source navy/sky palette.
Values are read from labeled bars in the published NAHB Housing Market Index.

Output: nahb-hmi-MMDDYY.png in the project root.
"""

from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt

NAVY = "#163d63"
SKY = "#7ec3e5"
WHITE = "#ffffff"
GRID = "#2f5478"
SUBTLE = "#9ab4cc"
BORDER = "#1e90ff"

MONTHS = ["Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
          "Jan", "Feb", "Mar", "Apr", "May"]
VALUES = [32, 33, 32, 32, 37, 38, 39, 37, 37, 38, 34, 37]


def build_chart(out_path: Path):
    fig, ax = plt.subplots(figsize=(12.5, 7.0), dpi=200)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    fig.text(0.5, 0.91, "NAHB Housing Market Index",
             ha="center", color=WHITE, fontsize=32, fontweight="bold")

    bars = ax.bar(MONTHS, VALUES, color=SKY, width=0.62,
                  edgecolor="none", zorder=3)

    for bar, v in zip(bars, VALUES):
        ax.text(bar.get_x() + bar.get_width() / 2,
                v + 0.35, f"{v}", ha="center", va="bottom",
                color=WHITE, fontsize=15, fontweight="bold")

    ax.set_ylim(29.5, 40.8)
    ax.set_yticks([30, 32, 34, 36, 38, 40])
    ax.set_yticklabels([str(t) for t in [30, 32, 34, 36, 38, 40]],
                       color=WHITE, fontsize=12)

    ax.tick_params(axis="x", colors=WHITE, length=0, pad=8)
    ax.tick_params(axis="y", colors=WHITE, length=0)
    for label in ax.get_xticklabels():
        label.set_fontsize(13)
        label.set_fontweight("bold")

    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.spines["bottom"].set_linewidth(0.8)

    ax.yaxis.grid(True, color=GRID, linestyle="--", linewidth=0.7, alpha=0.7)
    ax.set_axisbelow(True)

    fig.text(0.06, 0.045,
             "Source: National Association of Home Builders (NAHB)",
             ha="left", color=SUBTLE, fontsize=10.5)

    rect = plt.Rectangle((0, 0), 1, 1, transform=fig.transFigure,
                         fill=False, edgecolor=BORDER, linewidth=4.5)
    fig.patches.append(rect)

    plt.subplots_adjust(left=0.07, right=0.96, top=0.83, bottom=0.13)
    plt.savefig(out_path, facecolor=NAVY, edgecolor="none", dpi=200)
    plt.close()


def main():
    today = datetime.now().strftime("%m%d%y")
    out = Path(__file__).resolve().parent.parent / f"nahb-hmi-{today}.png"
    build_chart(out)
    print(f"Wrote {out}")
    print(f"Latest: May 2026 = {VALUES[-1]} (Apr: {VALUES[-2]}, +{VALUES[-1] - VALUES[-2]})")


if __name__ == "__main__":
    main()
