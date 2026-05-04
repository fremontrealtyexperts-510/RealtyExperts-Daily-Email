#!/usr/bin/env python3
"""Generate the U.S. Debt Held By The Public chart as a PNG.

Reproduces the CBO/Treasury historical + projected debt-to-GDP series
in the source navy/maroon palette with cream background and a 100% GDP
crossover line. Output: debt-vs-gdp-MMDDYY.png in the project root.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.lines import Line2D

# --- Data: debt held by the public as % of GDP (Treasury historical + CBO baseline) ---
historical = [
    (1940, 44), (1941, 42), (1942, 47), (1943, 70), (1944, 91), (1945, 104), (1946, 106),
    (1947, 92), (1948, 78), (1949, 75), (1950, 79),
    (1951, 65), (1952, 60), (1953, 56), (1954, 56), (1955, 56), (1956, 51), (1957, 47), (1958, 49), (1959, 46),
    (1960, 44), (1961, 43), (1962, 41), (1963, 40), (1964, 38), (1965, 36), (1966, 33), (1967, 31), (1968, 32), (1969, 28),
    (1970, 27), (1971, 27), (1972, 26), (1973, 25), (1974, 23), (1975, 24), (1976, 26), (1977, 26), (1978, 25), (1979, 25),
    (1980, 25), (1981, 25), (1982, 27), (1983, 32), (1984, 33), (1985, 35), (1986, 39), (1987, 39), (1988, 39), (1989, 39),
    (1990, 40), (1991, 44), (1992, 46), (1993, 48), (1994, 47), (1995, 48), (1996, 47), (1997, 44), (1998, 41), (1999, 38),
    (2000, 33), (2001, 31), (2002, 32), (2003, 34), (2004, 35), (2005, 35), (2006, 35), (2007, 35), (2008, 39),
    (2009, 52), (2010, 60), (2011, 65), (2012, 70), (2013, 71), (2014, 72), (2015, 72), (2016, 76), (2017, 75), (2018, 77),
    (2019, 79), (2020, 99), (2021, 96), (2022, 96), (2023, 97), (2024, 99), (2025, 99), (2026, 100),
]
projected = [
    (2026, 100), (2027, 102), (2028, 104), (2029, 105), (2030, 106),
    (2031, 108), (2032, 110), (2033, 112), (2034, 115), (2035, 119),
]

# Palette (matches the source aesthetic)
CREAM = "#f9f1de"
NAVY = "#1a2a4a"
MAROON = "#7a1a1a"
TEXT = "#1a2a4a"
GOLD_LABEL = "#7a6a3a"
SOURCE_GREY = "#5a5a4a"
GRID = "#d8c98a"
BORDER_BLUE = "#3478ff"


def build_chart(out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(15, 8.4), dpi=160)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    h_years = [y for y, _ in historical]
    h_vals = [v for _, v in historical]
    p_years = [y for y, _ in projected]
    p_vals = [v for _, v in projected]

    # Filled areas
    ax.fill_between(h_years, h_vals, 0, color=NAVY, linewidth=0)
    ax.fill_between(p_years, p_vals, 0, color=MAROON, linewidth=0)

    # 100% GDP crossover line
    ax.axhline(y=100, color="#5a5a4a", linewidth=1.2, linestyle=(0, (4, 4)), alpha=0.55, zorder=2)

    # Vertical separator at the historical/projected boundary
    boundary = projected[0][0]
    ax.axvline(x=boundary, color="#ffffff", linewidth=2.2, linestyle=(0, (5, 4)), zorder=4)

    # Axes range and ticks
    ax.set_xlim(1940, 2035)
    ax.set_ylim(0, 130)
    ax.set_xticks([1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020, 2030])
    ax.set_yticks([0, 30, 60, 90, 120])

    # Tick styling
    ax.tick_params(axis="x", colors=TEXT, labelsize=14, length=0, pad=10)
    ax.tick_params(axis="y", colors=GOLD_LABEL, labelsize=13, length=0, pad=8)

    # Y-axis "Percent of GDP" label
    ax.set_ylabel("Percent of GDP", color=GOLD_LABEL, fontsize=12, fontweight="bold", labelpad=12)

    # Hide the box / spines except a faint baseline
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GOLD_LABEL)
    ax.spines["bottom"].set_linewidth(0.8)

    # Subtle horizontal gridlines
    ax.yaxis.grid(True, color=GRID, linewidth=0.6, linestyle=(0, (2, 4)), alpha=0.6, zorder=1)
    ax.set_axisbelow(True)

    # Title
    ax.set_title(
        "U.S. Debt Held By The Public",
        color=TEXT, fontsize=30, fontweight="bold", pad=22, loc="center",
    )

    # In-area labels
    ax.text(
        1985, 18, "Historical Debt",
        color="#ffffff", fontsize=22, fontweight="bold", ha="center", va="center", zorder=5,
    )
    ax.text(
        2030.5, 78, "Projected\nDebt",
        color="#ffffff", fontsize=18, fontweight="bold", ha="center", va="center", zorder=5,
    )

    # Source citation
    fig.text(
        0.05, 0.025,
        "Source: CBO Long-Term Budget Outlook · Treasury Historical Tables",
        color=SOURCE_GREY, fontsize=10, ha="left",
    )

    # 100% GDP label inline near the crossover
    ax.text(
        1944, 102, "100% of GDP",
        color="#5a5a4a", fontsize=10, fontweight="bold", ha="left", va="bottom", alpha=0.85, zorder=5,
    )

    # Margins
    plt.subplots_adjust(left=0.07, right=0.97, top=0.88, bottom=0.10)

    # Save first (so canvas is finalized), then add the outer blue border via fig save trick
    fig.savefig(out_path, facecolor=CREAM, edgecolor=BORDER_BLUE, dpi=160)
    plt.close(fig)

    # Re-open and stamp a thicker border via Pillow (matplotlib edgecolor is thin)
    try:
        from PIL import Image, ImageDraw
        img = Image.open(out_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        w, h = img.size
        for offset in range(6):
            draw.rectangle([offset, offset, w - 1 - offset, h - 1 - offset], outline=BORDER_BLUE)
        img.save(out_path)
    except ImportError:
        pass


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: generate-debt-chart.py <output.png>")
        sys.exit(1)
    out = Path(sys.argv[1])
    build_chart(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
