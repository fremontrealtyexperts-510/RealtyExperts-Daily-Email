#!/usr/bin/env python3
"""Generate Average U.S. Monthly Rent chart as PNG (matches MB style).

11-year annual bar chart, Apartment List / Zillow Observed Rent Index,
navy/sky-blue palette.

Output: avg-monthly-rent-MMDDYY.png in the project root.
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

YEARS = list(range(2016, 2027))
VALUES = [1029, 1068, 1109, 1149, 1185, 1265, 1341, 1448, 1535, 1650, 1698]


def build_chart(out_path: Path):
    fig, ax = plt.subplots(figsize=(12.5, 7.0), dpi=200)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    fig.text(0.5, 0.91, "Average U.S. Monthly Rent",
             ha="center", color=WHITE, fontsize=32, fontweight="bold")
    fig.text(0.5, 0.855, "2016 — 2026",
             ha="center", color=SUBTLE, fontsize=13)

    bars = ax.bar([str(y) for y in YEARS], VALUES, color=SKY, width=0.62,
                  edgecolor="none", zorder=3)

    for bar, v in zip(bars, VALUES):
        ax.text(bar.get_x() + bar.get_width() / 2,
                v + 25, f"${v:,}", ha="center", va="bottom",
                color=WHITE, fontsize=13, fontweight="bold")

    ax.set_ylim(0, 1900)
    ax.set_yticks([])
    ax.set_xticks(range(len(YEARS)))
    ax.set_xticklabels([str(y) for y in YEARS],
                       color=WHITE, fontsize=13, fontweight="bold")

    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.spines["bottom"].set_linewidth(0.8)

    ax.tick_params(axis="x", colors=WHITE, length=0, pad=8)
    ax.set_axisbelow(True)

    fig.text(0.06, 0.045,
             "Source: Apartment List / Zillow Observed Rent Index",
             ha="left", color=SUBTLE, fontsize=10.5)

    rect = plt.Rectangle((0, 0), 1, 1, transform=fig.transFigure,
                         fill=False, edgecolor=BORDER, linewidth=4.5)
    fig.patches.append(rect)

    plt.subplots_adjust(left=0.04, right=0.97, top=0.78, bottom=0.13)
    plt.savefig(out_path, facecolor=NAVY, edgecolor="none", dpi=200)
    plt.close()


def main():
    today = datetime.now().strftime("%m%d%y")
    out = Path(__file__).resolve().parent.parent / f"avg-monthly-rent-{today}.png"
    build_chart(out)
    print(f"Wrote {out}")
    print(f"2016: ${VALUES[0]:,}  →  2026: ${VALUES[-1]:,}  "
          f"(+{(VALUES[-1] - VALUES[0]) / VALUES[0] * 100:.1f}% over 10 years)")


if __name__ == "__main__":
    main()
