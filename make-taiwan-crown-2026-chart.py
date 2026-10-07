#!/usr/bin/env python3
"""
make-taiwan-crown-2026-chart.py  DATA_DIR  [outdir]

The 10/07/26 daily's world markets chart (Stocks section). Harv attached the
newsletter graphic "World's Biggest Stock Markets" (total market value in US
dollars, "Bloomberg data, May 2026": U.S. $77.95T, China $15.61T, Japan $8.70T,
Hong Kong $7.25T, Taiwan $4.95T). Emits BOTH variants:

  taiwan-crown-100726.png      plain HB monogram    -> RE email + Agent Hub
  taiwan-crown-100726-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

=============================================================================
WHY THIS IS NOT A COPY OF THE SUPPLIED CHART (verification 10/07/26)
=============================================================================
Only ONE of the five bars could be sourced. Bloomberg's own story, syndicated
05/26/26 (BusinessMirror, The Wealth Advisor, UPI): "The island's market
capitalization climbed to $4.95 trillion as of Monday, according to data
compiled by Bloomberg", passing India's $4.92 trillion, making Taiwan the fifth
largest market "behind only the US, mainland China, Japan and Hong Kong". No
public source carries Bloomberg's U.S., China, Japan or Hong Kong totals, and
mixing in another vendor's market caps (WFE, exchange data) would be the cross
vendor splice we refuse to do. Per the standing rule, unsourceable bars drop.

The newsletter's actual story that morning was performance, not size: "Taiwan
just stole South Korea's crown as the world's hottest stock market. It beat
Korea by 23 percentage points last quarter." That IS fully sourceable from index
closes, so this chart shows the same five biggest markets (plus Korea and India,
the two Taiwan just passed) and how their benchmark indexes moved in 2026.

Index closes are CNBC ts-api daily bars (price index, local currency, no
dividends). Kospi spot checked against five closes printed in Korean press
(Asia Economy, FN News): Jul 10 7,475.94, Jul 13 6,806.93, Jul 28 6,023.66,
Aug 31 6,820.02, Sep 9 7,051.64; all five match the bars exactly. A search
summary that day claimed Kospi fell 18.8% in Q3; the closes say 19.33%.

  base = last 2025 close; mid = Jun 30, 2026; end = Sep 30, 2026
  Taiwan Taiex     28,963.60  46,125.91  47,940.13  H1 +59.3  YTD +65.5  Q3 +3.9
  South Korea Kospi 4,214.17   8,476.48   6,838.04  H1 +101.1 YTD +62.3  Q3 -19.3
  Japan Nikkei 225 50,339.48  70,062.32  66,753.72  H1 +39.2  YTD +32.6  Q3 -4.7
  U.S. S&P 500      6,845.50   7,499.36   7,651.54  H1 +9.6   YTD +11.8  Q3 +2.0
  Hong Kong HSI    25,630.54  22,881.02  24,613.27  H1 -10.7  YTD -4.0   Q3 +7.6
  China CSI 300     4,629.94   4,979.43   4,357.62  H1 +7.5   YTD -5.9   Q3 -12.5
  India Nifty 50   26,129.60  23,865.75  22,620.45  H1 -8.7   YTD -13.4  Q3 -5.2

Taiwan minus Korea in Q3: 3.93 - (-19.33) = 23.3 points, the newsletter's "23".
"The widest gap this century" was NOT verified and is not repeated.

matplotlib only; build with python3.13 on Mac.
"""
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "100726"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
GREEN = "#2f855a"
SLATE = "#6f8296"
GRID = "#d8cdb8"
MUTED = "#8a8172"
GOLD = "#c98a1b"
MINUS = "−"

MARKETS = [  # (symbol, label, index)
    (".TWII", "Taiwan", "Taiex"),
    (".KS11", "South Korea", "Kospi"),
    (".N225", "Japan", "Nikkei 225"),
    (".SPX", "United States", "S&P 500"),
    (".HSI", "Hong Kong", "Hang Seng"),
    (".CSI300", "China", "CSI 300"),
    (".NSEI", "India", "Nifty 50"),
]


def bars(name):
    return {b["tradeTime"][:8]: Decimal(b["close"])
            for b in json.load(open(os.path.join(DATA, name)))["barData"]["priceBars"]}


def last_on_or_before(series, day):
    k = max(d for d in series if d <= day)
    return k, series[k]


def pct(a, b):
    return (a / b - 1) * 100


def r1(d):
    return d.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def signed(d):
    q = r1(d)
    return f"+{q}%" if q > 0 else f"{MINUS}{abs(q)}%"


def load():
    rows = []
    for sym, label, idx in MARKETS:
        ye = bars(f"ye{sym}.json")
        q3 = bars(f"q3{sym}.json")
        _, base = last_on_or_before(ye, "20251231")
        dm, mid = last_on_or_before(q3, "20260630")
        de, end = last_on_or_before(q3, "20260930")
        assert dm == "20260630" and de == "20260930", (sym, dm, de)
        rows.append(dict(sym=sym, label=label, idx=idx, h1=pct(mid, base), ytd=pct(end, base),
                         q3=pct(end, mid)))
    by = {r["sym"]: r for r in rows}
    # the facts the copy leans on, asserted so a re-pull cannot drift silently
    assert (r1(by[".TWII"]["ytd"]), r1(by[".KS11"]["ytd"])) == (Decimal("65.5"), Decimal("62.3"))
    assert (r1(by[".TWII"]["h1"]), r1(by[".KS11"]["h1"])) == (Decimal("59.3"), Decimal("101.1"))
    assert (r1(by[".TWII"]["q3"]), r1(by[".KS11"]["q3"])) == (Decimal("3.9"), Decimal("-19.3"))
    assert r1(by[".TWII"]["q3"] - by[".KS11"]["q3"]) == Decimal("23.3")
    assert r1(by[".SPX"]["ytd"]) == Decimal("11.8") and r1(by[".NSEI"]["ytd"]) == Decimal("-13.4")
    rows.sort(key=lambda r: r["ytd"], reverse=True)
    assert [r["sym"] for r in rows] == [m[0] for m in MARKETS], [r["sym"] for r in rows]
    return rows


def build():
    rows = load()
    for r in rows:
        print(f'{r["label"]:14} H1 {r["h1"]:+7.2f}  YTD {r["ytd"]:+7.2f}  Q3 {r["q3"]:+7.2f}')

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.205, 0.145, 0.62, 0.64])
    ax.set_facecolor(CREAM)

    n = len(rows)
    ys = list(range(n))[::-1]
    xmin, xmax = -32, 115
    for y, r in zip(ys, rows):
        h1, ytd = float(r["h1"]), float(r["ytd"])
        hot = r["sym"] in (".TWII", ".KS11")
        col = (GREEN if r["sym"] == ".TWII" else CORAL) if hot else SLATE
        if hot:
            ax.axhspan(y - 0.42, y + 0.42, color="#f3e6cc", lw=0, zorder=0)
        if abs(ytd - h1) >= 6:
            ax.annotate("", xy=(ytd, y), xytext=(h1, y),
                        arrowprops=dict(arrowstyle="-|>,head_length=0.7,head_width=0.35", color=col,
                                        lw=2.6 if hot else 1.8, shrinkA=6, shrinkB=7), zorder=3)
        else:  # too short for a head; a plain connector reads cleaner
            ax.plot([h1, ytd], [y, y], color=col, lw=2.6 if hot else 1.8, zorder=3)
        ax.scatter([h1], [y], s=90, facecolor=CREAM, edgecolor=col, linewidth=2.0, zorder=4)
        ax.scatter([ytd], [y], s=150 if hot else 110, color=col, edgecolor=CREAM, linewidth=1.5, zorder=5)
        # labels: midyear value beside the hollow dot, Sept. value bold beside the solid dot
        left_first = ytd < h1
        off = 2.6
        ax.text(h1, y + 0.33, signed(r["h1"]), fontsize=10.5,
                color=MUTED, ha="center", va="center", zorder=6)
        ax.text(ytd + (-off if left_first else off), y, signed(r["ytd"]), fontsize=14 if hot else 12.5,
                fontweight="bold", color=col, ha="right" if left_first else "left", va="center", zorder=6)
        # country + index at the left margin
        ax.text(xmin - 3, y + 0.12, r["label"], fontsize=14, fontweight="bold" if hot else "normal",
                color=INK, ha="right", va="center")
        ax.text(xmin - 3, y - 0.24, r["idx"], fontsize=10.5, color=MUTED, ha="right", va="center")

    ax.axvline(0, color=MUTED, lw=1.2, zorder=1)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-0.7, n - 0.3)
    ax.set_yticks([])
    xt = [-20, 0, 20, 40, 60, 80, 100]
    ax.set_xticks(xt)
    ax.set_xticklabels([f"{MINUS}20%" if v < 0 else (f"+{v}%" if v > 0 else "0") for v in xt],
                       fontsize=11, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="x", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # the story, in the empty right margin
    tw = [r for r in rows if r["sym"] == ".TWII"][0]
    kr = [r for r in rows if r["sym"] == ".KS11"][0]
    fig.text(0.845, 0.700, "Last quarter", fontsize=12.5, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.845, 0.660, f"Taiwan  {signed(tw['q3'])}", fontsize=13, color=GREEN, fontweight="bold",
             ha="left", va="top")
    fig.text(0.845, 0.622, f"Korea  {signed(kr['q3'])}", fontsize=13, color=CORAL, fontweight="bold",
             ha="left", va="top")
    fig.text(0.845, 0.578, "A 23 point swing\nthat flipped the lead", fontsize=11, color=MUTED,
             ha="left", va="top", linespacing=1.25)

    # legend for the two dots
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], ls="none", marker="o", markersize=10, markerfacecolor=CREAM,
                      markeredgecolor=SLATE, markeredgewidth=2.0),
               Line2D([], [], ls="none", marker="o", markersize=11, markerfacecolor=SLATE,
                      markeredgecolor=CREAM)]
    leg = fig.legend(handles, ["June 30", "Sept. 30"], loc="upper left", bbox_to_anchor=(0.838, 0.435),
                     frameon=False, fontsize=11.5, handletextpad=0.5, labelspacing=0.8)
    for t in leg.get_texts():
        t.set_color(MUTED)

    fig.text(0.035, 0.955, "Taiwan Takes Korea's Crown", fontsize=25, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.900,
             "Benchmark index change in 2026, at midyear and at the end of September. The world's five biggest\n"
             "stock markets, plus South Korea and India, the two Taiwan has passed this year.",
             fontsize=13, color=MUTED, ha="left", va="top", linespacing=1.3)
    fig.text(0.035, 0.030,
             "Source: CNBC daily index closes (price only, local currency). Change measured from each "
             "index's last 2025 close.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"taiwan-crown-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
