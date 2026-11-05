"""
make-korea-surplus-2026-chart.py  DATA_DIR  [outdir]

The 11/05/26 daily's Stocks chart, recreated from the newsletter graphic Harv
supplied ("South Korea's Surplus Hits a Record", Bank of Korea). Emits BOTH:

  korea-surplus-110526.png      plain HB monogram    -> RE email + Agent Hub
  korea-surplus-110526-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR/ca-history.json is the Bank of Korea ECOS series 301Y013 item 000000
(current account, monthly, millions of U.S. dollars), Jan 1980 to Sep 2026,
pulled 11/05/26 with the ECOS "sample" key ten rows at a time:
  https://ecos.bok.or.kr/api/StatisticSearch/sample/json/en/{a}/{b}/301Y013/M/198001/202609/000000
saved as a list of [YYYYMM, value].

=============================================================================
VERIFICATION 11/05/26
=============================================================================
* All nine supplied points match ECOS exactly at one decimal (13.3, 23.2, 37.9,
  28.3, 38.6, 49.7, 42.1, 46.1, 61.5 $B). The graphic was right.
* "Record" holds: September 2026 is the largest month in the whole series back
  to January 1980 (561 months). The next largest is June 2026.
* Added the 2025 comparison the graphic left out: Sep 2025 was $14.2B, so Sep
  2026 is 4.3x; Jan to Sep 2026 is $340.7B against $123.1B for ALL of 2025.
* Goods exports (ECOS 301Y013 item 110000) were $130,716.4M in Sep 2026, the
  newsletter's "$130.7B": verified, and quoted in the subtitle.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "110526"

CREAM = "#fdf6e8"
INK = "#1f2933"
SLATE = "#3e5c76"
SLATE_PALE = "#a9b8c6"
ORANGE = "#e07a2e"
GRID = "#d8cdb8"
MUTED = "#8a8172"
BAND = "#f6e6cc"
DOT = "#6b6257"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]


def b1(millions):
    return float((Decimal(str(millions)) / 1000).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def load():
    rows = json.load(open(os.path.join(DATA, "ca-history.json")))
    s = {t: v for t, v in rows}
    assert len(s) == 561 and min(s) == "198001" and max(s) == "202609", (len(s), min(s), max(s))
    y26 = [s["2026%02d" % m] for m in range(1, 10)]
    y25 = [s["2025%02d" % m] for m in range(1, 10)]
    assert [b1(v) for v in y26] == [13.3, 23.2, 37.9, 28.3, 38.6, 49.7, 42.1, 46.1, 61.5], y26   # supplied graphic
    assert max(s, key=s.get) == "202609"                                                          # all-time record
    assert sorted(s.values())[-2] == s["202606"]
    ytd26 = sum(y26)
    all25 = sum(s["2025%02d" % m] for m in range(1, 13))
    assert (b1(ytd26), b1(all25), b1(y25[-1])) == (340.7, 123.1, 14.2), (ytd26, all25, y25[-1])
    ratio = Decimal(str(y26[-1])) / Decimal(str(y25[-1]))
    assert ratio.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP) == Decimal("4.3"), ratio
    return [v / 1000 for v in y26], [v / 1000 for v in y25], b1(ytd26), b1(all25)


def build():
    y26, y25, ytd26, all25 = load()
    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.13, 0.66, 0.64])
    ax.set_facecolor(CREAM)

    n = len(y26)
    ax.axvspan(n - 1 - 0.5, n - 1 + 0.5, color=BAND, zorder=0)
    for i, v in enumerate(y26):
        last = i == n - 1
        ax.bar(i, v, width=0.62, color=ORANGE if last else SLATE_PALE, zorder=3)
        ax.text(i, v + 1.0, f"\\${b1(v * 1000):.1f}B", ha="center", va="bottom", fontsize=14.5 if last else 12.5,
                fontweight="bold", color=ORANGE if last else INK, zorder=5)
    ax.plot(range(n), y25, color=DOT, lw=1.4, ls=(0, (2, 2)), zorder=4)
    ax.scatter(range(n), y25, s=34, color=DOT, zorder=6)

    ax.set_xticks(range(n))
    ax.set_xticklabels(MONTHS, fontsize=14, color=INK)
    ax.get_xticklabels()[-1].set_fontweight("bold")
    ax.set_xlim(-0.6, n - 0.4)
    ax.set_ylim(0, 70)
    ticks = [0, 20, 40, 60]
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"\\${v}B" for v in ticks], fontsize=12.5, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=9)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    leg = ax.legend(handles=[Patch(color=SLATE_PALE, label="2026"),
                             Line2D([0], [0], color=DOT, lw=1.4, ls=(0, (2, 2)), marker="o", markersize=6,
                                    label="Same month, 2025")],
                    loc="upper left", frameon=False, fontsize=13.5, handlelength=1.8, borderaxespad=0.2)
    for t in leg.get_texts():
        t.set_color(INK)

    # side panel
    x0 = 0.775
    fig.text(x0, 0.715, "September 2026", fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(x0, 0.675, "\\$61.5B", fontsize=34, fontweight="bold", color=ORANGE, ha="left", va="top")
    fig.text(x0, 0.590, "the largest month on record\n(Bank of Korea data back to 1980)", fontsize=12.5, color=INK,
             ha="left", va="top", linespacing=1.35)
    fig.text(x0, 0.475, "4.3x September 2025", fontsize=17, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(x0, 0.430, "(\\$14.2B a year earlier)", fontsize=12.5, color=MUTED, ha="left", va="top")
    fig.text(x0, 0.335, f"\\${ytd26:.1f}B", fontsize=24, fontweight="bold", color=SLATE, ha="left", va="top")
    fig.text(x0, 0.275, "January to September 2026,\nvs. \\$" + f"{all25:.1f}B for all of 2025", fontsize=12.5,
             color=INK, ha="left", va="top", linespacing=1.35)

    fig.text(0.035, 0.955, "South Korea's Surplus Hits a Record", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.895, "Monthly current account surplus, U.S. dollars. Memory chip demand lifted goods exports to "
             "\\$130.7B in September.", fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.03, "Source: Bank of Korea, balance of payments (ECOS), monthly current account; "
             "September 2026 is preliminary.", fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"korea-surplus-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
