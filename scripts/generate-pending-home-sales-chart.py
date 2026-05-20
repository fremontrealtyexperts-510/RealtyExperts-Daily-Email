#!/usr/bin/env python3
"""Generate U.S. Pending Home Sales chart as PNG (matches MB style).

12-month NAR Pending Home Sales Index, line with shaded fill,
navy/sky-blue palette.

Output: pending-home-sales-MMDDYY.png in the project root.
"""

from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

NAVY = "#163d63"
SKY = "#7ec3e5"
SKY_FILL = "#3d6b97"
WHITE = "#ffffff"
GRID = "#2f5478"
SUBTLE = "#9ab4cc"
BORDER = "#1e90ff"

MONTHS = ["May'25", "Jun'25", "Jul'25", "Aug'25", "Sep'25", "Oct'25",
          "Nov'25", "Dec'25", "Jan'26", "Feb'26", "Mar'26", "Apr'26"]
VALUES = [73.3, 72.7, 72.8, 74.7, 74.4, 75.6, 77.2, 71.5, 70.8, 72.6, 73.8, 74.8]


def build_chart(out_path: Path):
    fig, ax = plt.subplots(figsize=(12.5, 7.0), dpi=200)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    fig.text(0.5, 0.91, "U.S. PENDING HOME SALES",
             ha="center", color=WHITE, fontsize=30, fontweight="bold")
    fig.text(0.5, 0.855, "Monthly Index   ·   May '25 – April '26",
             ha="center", color=SUBTLE, fontsize=13)

    x = list(range(len(MONTHS)))
    ax.fill_between(x, VALUES, 69.5, color=SKY_FILL, alpha=0.45, zorder=2)
    ax.plot(x, VALUES, color=SKY, linewidth=2.8, marker="o",
            markersize=8, markerfacecolor=SKY, markeredgecolor=SKY, zorder=3)

    for i, v in enumerate(VALUES):
        offset = 1.0 if v < 76 else -1.4
        ax.text(i, v + offset, f"{v}", ha="center", va="center",
                color=WHITE, fontsize=14, fontweight="bold", zorder=4)

    ax.set_xticks(x)
    labels = [m.replace("'", "\n'") for m in MONTHS]
    ax.set_xticklabels(labels, color=WHITE, fontsize=12, fontweight="bold")

    ax.set_ylim(69, 80)
    ax.set_yticks([70, 72, 74, 76, 78, 80])
    ax.set_yticklabels([str(int(t)) for t in [70, 72, 74, 76, 78, 80]],
                       color=WHITE, fontsize=12)

    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.spines["bottom"].set_linewidth(0.8)

    ax.tick_params(axis="both", colors=WHITE, length=0, pad=6)
    ax.yaxis.grid(True, color=GRID, linestyle="--", linewidth=0.7, alpha=0.7)
    ax.set_axisbelow(True)

    fig.text(0.06, 0.045, "Source: National Association of Realtors",
             ha="left", color=SUBTLE, fontsize=10.5)

    rect = plt.Rectangle((0, 0), 1, 1, transform=fig.transFigure,
                         fill=False, edgecolor=BORDER, linewidth=4.5)
    fig.patches.append(rect)

    plt.subplots_adjust(left=0.07, right=0.96, top=0.78, bottom=0.13)
    plt.savefig(out_path, facecolor=NAVY, edgecolor="none", dpi=200)
    plt.close()


def main():
    today = datetime.now().strftime("%m%d%y")
    out = Path(__file__).resolve().parent.parent / f"pending-home-sales-{today}.png"
    build_chart(out)
    print(f"Wrote {out}")
    print(f"Latest: Apr 2026 = {VALUES[-1]} (Mar: {VALUES[-2]}, +{VALUES[-1] - VALUES[-2]:.1f})")


if __name__ == "__main__":
    main()
