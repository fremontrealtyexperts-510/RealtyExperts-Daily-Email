#!/usr/bin/env python3
"""
make-consumer-sentiment-2026-chart.py  DATA_DIR  [outdir]

The 10/12/26 daily's consumer sentiment chart. Harv attached the newsletter
graphic "Consumer Mood Sinks Again" (University of Michigan Consumer Sentiment
Index, 2026: 56.4, 56.6, 53.3, 49.8, 44.8 "RECORD LOW", 49.5, 55.2, 51.7, 48.1,
and October 46.3 dashed as preliminary). Emits BOTH:

  consumer-sentiment-101226.png      plain HB monogram    -> RE email + Agent Hub
  consumer-sentiment-101226-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds tbmics.csv (sca.isr.umich.edu/files/tbmics.csv, the official
monthly table) and umich-home.html (sca.isr.umich.edu, the October preliminary
release), both fetched Oct. 12, 2026 about 8:00 AM PT.

=============================================================================
VERIFICATION 10/12/26
=============================================================================
Every supplied point matches UMich: Jan to Sept from tbmics.csv (also FRED
UMCSENT through August), October preliminary 46.3 from the release page
(down 1.8 points from 48.1; final due Oct. 23). "Record low" is right: May
2026's 44.8 is the lowest in the table, which runs back to 1952. Our addition:
the low before 2026 was 50.0 (June 2022), and four 2026 months have now come
in below it (April 49.8, May 44.8, June 49.5, September 48.1), plus October's
preliminary 46.3, which would be the second lowest on record if it holds.

matplotlib; build with python3.13 on Mac.
"""
import csv
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
STAMP = "101226"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e05a47"
DEEP = "#b8432f"
BLUE = "#2b6cb0"
BLUE_D = "#1e4e8c"
GRID = "#d8cdb8"
MUTED = "#8a8172"
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]
SHORT = ["Jan.", "Feb.", "March", "April", "May", "June", "July", "Aug.", "Sept.", "Oct."]


def load():
    rows = list(csv.reader(open(os.path.join(DATA, "tbmics.csv"))))[1:]
    allv = [(r[0], int(r[1]), float(r[2])) for r in rows if len(r) > 2 and r[2].strip()]
    y26 = {m: v for m, y, v in allv if y == 2026}
    vals = [y26[m] for m in MONTHS[:9]]
    assert vals == [56.4, 56.6, 53.3, 49.8, 44.8, 49.5, 55.2, 51.7, 48.1], vals

    page = re.sub(r"<[^>]+>", " ", open(os.path.join(DATA, "umich-home.html"), errors="ignore").read())
    page = re.sub(r"\s+", " ", page)
    m = re.search(r"Preliminary Results for October 2026 .*?Index of Consumer Sentiment ([0-9.]+) ([0-9.]+)", page)
    octp, sep = float(m.group(1)), float(m.group(2))
    assert (octp, sep) == (46.3, 48.1), (octp, sep)

    low = min(allv, key=lambda r: r[2])
    assert low == ("May", 2026, 44.8), low
    before = min((r for r in allv if r[1] < 2026), key=lambda r: r[2])
    assert before == ("June", 2022, 50.0), before
    under = [r for r in allv if r[2] < before[2]]
    assert sorted(r[0] for r in under) == ["April", "June", "May", "September"]
    assert sorted(v for _, _, v in allv)[1] > octp      # Oct prelim would be 2nd lowest ever
    assert allv[0][1] == 1952
    return vals, octp, before


def build():
    vals, octp, before = load()
    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.06, 0.16, 0.86, 0.62])
    ax.set_facecolor(CREAM)

    x = list(range(9))
    ax.axhline(before[2], color=MUTED, lw=1.3, ls=(0, (5, 4)), zorder=1)
    ax.text(9.45, before[2] + 0.25, f"Lowest before 2026: {before[2]:.1f}\n(June 2022)", fontsize=11.5,
            color=MUTED, ha="right", va="bottom", linespacing=1.25)
    ax.fill_between([-0.4, 9.6], 40, before[2], color="#f6e1da", lw=0, zorder=0)

    ax.plot(x, vals, color=BLUE, lw=3.2, solid_joinstyle="round", zorder=4)
    ax.plot([8, 9], [vals[-1], octp], color=CORAL, lw=3.0, ls=(0, (3, 2.2)), zorder=4)
    ax.scatter(x, vals, s=60, color=BLUE, edgecolor=CREAM, linewidth=1.5, zorder=5)
    for i, v in enumerate(vals):
        if i == 4:
            continue
        below = v < before[2]
        # label placement keeps clear of the line: below on the falling legs, beside the turns
        dx, dy, ha, va = {2: (0, -16, "center", "top"), 3: (0, -16, "center", "top"),
                          5: (12, -4, "left", "top"), 7: (10, 6, "left", "bottom")}.get(
                              i, (0, 12, "center", "bottom"))
        ax.annotate(f"{v:.1f}", xy=(i, v), xytext=(dx, dy), textcoords="offset points",
                    fontsize=14, fontweight="bold", color=DEEP if below else INK, ha=ha, va=va)
    ax.scatter([4], [vals[4]], s=130, color=DEEP, edgecolor=CREAM, linewidth=2, zorder=6)
    ax.annotate(f"{vals[4]:.1f}\nRecord low", xy=(4, vals[4]), xytext=(0, -16), textcoords="offset points",
                fontsize=14, fontweight="bold", color=DEEP, ha="center", va="top", linespacing=1.2)
    ax.scatter([9], [octp], s=130, color=CORAL, edgecolor=CREAM, linewidth=2, zorder=6)
    ax.annotate(f"{octp:.1f}", xy=(9, octp), xytext=(0, -18), textcoords="offset points",
                fontsize=18, fontweight="bold", color="white", ha="center", va="top", zorder=7,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=CORAL, edgecolor="none"))
    ax.text(9, octp - 3.05, "preliminary", fontsize=11.5, color=DEEP, ha="center", va="top")

    ax.text(5.55, 40.7, "Shaded: below every reading before 2026.\nFour months this year so far, and\n"
            "October's preliminary 46.3 would rank\nsecond lowest on record.",
            fontsize=12, color=DEEP, ha="left", va="bottom", linespacing=1.3)

    ax.set_xticks(list(range(10)))
    ax.set_xticklabels(SHORT, fontsize=13, color=MUTED)
    ax.set_xlim(-0.4, 9.6)
    ax.set_ylim(40, 61)
    ax.set_yticks([40, 45, 50, 55, 60])
    ax.set_yticklabels(["40", "45", "50", "55", "60"], fontsize=12, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.035, 0.955, "Consumer Mood Sinks Again", fontsize=26, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.895, "University of Michigan index of consumer sentiment, monthly, 2026",
             fontsize=13.2, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.065, "Source: University of Michigan Surveys of Consumers, records back to 1952. "
             "October is the preliminary reading, released Oct. 9, 2026; the final is due Oct. 23.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"consumer-sentiment-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
