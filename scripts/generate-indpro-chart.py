#!/usr/bin/env python3
"""Generate the U.S. Industrial Production chart as a PNG.

Reproduces Market Briefs' Apr 2021 - Apr 2026 INDPRO chart in the source
brown/orange palette. Pulls data directly from FRED.

Output: indpro-MMDDYY.png in the project root.
"""

import csv
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BROWN_BG = "#3d2614"
PANEL = "#3d2614"
ORANGE = "#f08a25"
ORANGE_LIGHT = "#fdb877"
WHITE = "#ffffff"
GRID = "#5a3d27"
SUBTLE = "#a08070"
BORDER = "#1e90ff"


def fetch_indpro(start="2021-04-01", end="2026-04-01"):
    cache = Path("/tmp/indpro.csv")
    if cache.exists():
        text = cache.read_text()
    else:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id=INDPRO&cosd={start}&coed={end}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            text = r.read().decode()
        cache.write_text(text)
    rows = list(csv.reader(text.splitlines()))[1:]
    return [(datetime.strptime(d, "%Y-%m-%d"), float(v)) for d, v in rows if v not in ("", ".")]


def build_chart(out_path: Path):
    data = fetch_indpro()
    dates = [d for d, _ in data]
    vals = [v for _, v in data]
    last_d, last_v = dates[-1], vals[-1]

    fig, ax = plt.subplots(figsize=(12.5, 7.2), dpi=200)
    fig.patch.set_facecolor(BROWN_BG)
    ax.set_facecolor(PANEL)

    fig.text(0.5, 0.91, "U.S. Industrial Production",
             ha="center", color=WHITE, fontsize=32, fontweight="bold")
    fig.text(0.5, 0.855,
             "Total Index, Seasonally Adjusted (2017 = 100)   ·   Apr 2021 – Apr 2026",
             ha="center", color=SUBTLE, fontsize=13)

    ax.plot(dates, vals, color=ORANGE, linewidth=2.6, solid_capstyle="round")

    ax.scatter([last_d], [last_v], s=80, color=WHITE, edgecolors=ORANGE,
               linewidths=2.5, zorder=5)

    label_text = f"{last_v:.2f}"
    label_x = mdates.date2num(last_d) - 80
    label_y = last_v + 0.18
    bbox = dict(boxstyle="round,pad=0.5", fc=ORANGE_LIGHT, ec="none")
    ax.text(label_x, label_y, label_text, fontsize=18, fontweight="bold",
            color="#5a2a05", bbox=bbox, ha="right", va="center",
            zorder=6)

    ax.set_ylim(97.8, 103.2)
    ax.set_yticks([98, 99, 100, 101, 102, 103])
    ax.set_yticklabels([f"{int(t)}" for t in [98, 99, 100, 101, 102, 103]],
                       color=WHITE, fontsize=12)

    years = [datetime(y, 1, 1) for y in range(2021, 2027)]
    ax.set_xticks(years)
    ax.set_xticklabels([str(y.year) for y in years], color=WHITE, fontsize=13)
    ax.set_xlim(datetime(2021, 1, 1), datetime(2026, 8, 1))

    for spine in ("top", "right", "bottom", "left"):
        ax.spines[spine].set_color(GRID)
        ax.spines[spine].set_linewidth(0.8)

    ax.tick_params(axis="both", colors=WHITE, length=0)
    ax.yaxis.grid(True, color=GRID, linestyle="--", linewidth=0.7, alpha=0.7)
    ax.set_axisbelow(True)

    fig.text(0.5, 0.045,
             "Source: Board of Governors of the Federal Reserve System (US) via FRED®",
             ha="center", color=SUBTLE, fontsize=10.5)

    rect = plt.Rectangle((0, 0), 1, 1, transform=fig.transFigure,
                         fill=False, edgecolor=BORDER, linewidth=4.5)
    fig.patches.append(rect)

    plt.subplots_adjust(left=0.07, right=0.96, top=0.78, bottom=0.13)
    plt.savefig(out_path, facecolor=BROWN_BG, edgecolor="none", dpi=200)
    plt.close()
    return last_d, last_v


def main():
    today = datetime.now().strftime("%m%d%y")
    out = Path(__file__).resolve().parent.parent / f"indpro-{today}.png"
    last_d, last_v = build_chart(out)
    print(f"Wrote {out}")
    print(f"Latest: {last_d.strftime('%b %Y')} = {last_v:.4f}")


if __name__ == "__main__":
    main()
