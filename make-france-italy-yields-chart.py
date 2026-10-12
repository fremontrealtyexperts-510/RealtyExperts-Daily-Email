#!/usr/bin/env python3
"""
make-france-italy-yields-chart.py  DATA_DIR  [outdir]

The 10/12/26 daily's Economy chart. Harv attached the newsletter graphic
"France Now Pays More Than Italy" (10-year government bond yields, Oct. 9,
2026: France 4.85%, Italy 4.57%, Spain 4.09%, Germany 3.45%; "Source:
Bloomberg, Trading Economics (Oct. 9, 2026 closes)"). Emits BOTH:

  france-italy-yields-101226.png      plain HB monogram    -> RE email + Agent Hub
  france-italy-yields-101226-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds CNBC daily bars (ts-api.cnbc.com harmony bars, 1D, fetched
Oct. 12, 2026 7:55 AM PT): FR10Y-FR, IT10Y-IT, ES10Y-ES, DE10Y-DE (.json for
2024 onward, -long.json for 1999 to 2023).

=============================================================================
VERIFICATION 10/12/26
=============================================================================
CNBC Friday Oct. 9 closes: France 4.8599, Italy 4.5954, Spain 4.1080, Germany
3.4857. The supplied bars are 1 to 4 basis points lower (vendor close times
differ); the order and the story hold. CNBC's bars carry a stray Saturday
stub (Oct. 10) for European bonds: weekday bars only are used.
"Now" needs a footnote: France first closed above Italy on Oct. 7, 2025 and
has closed above every day since Aug. 4, 2026. What is new is the SIZE of the
gap: +0.28 points Oct. 8 is the widest in CNBC data back to Jan. 1999, Oct. 9
(+0.26) the second widest. France's 10-year is the highest since July 2002;
France over Germany 1.37 points, the widest (before Sept. 2026) since May 2012.
U.S. reference bar: Treasury daily yield curve 10-year, Oct. 9, 5.24%.

matplotlib; build with python3.13 on Mac.
"""
import json
import os
import sys
from datetime import date, datetime

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["path.simplify"] = False    # ~700 dense points: simplification shaved the final peak
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "101226"
DAY = "20261009"
US10 = 5.24            # Treasury daily yield curve, Oct. 9, 2026

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e05a47"
DEEP = "#b8432f"
BLUE = "#2b6cb0"
BLUE_D = "#1e4e8c"
BLUES = ["#4f83bf", "#6b98cb", "#86acd6"]
SLATE = "#8a95a3"
GRID = "#d8cdb8"
MUTED = "#8a8172"


def bars(sym):
    out = {}
    for f in (f"{sym}-long.json", f"{sym}.json"):
        p = os.path.join(DATA, f)
        if not os.path.exists(p):
            continue
        for b in json.load(open(p))["barData"]["priceBars"]:
            d = b["tradeTime"][:8]
            if datetime.strptime(d, "%Y%m%d").weekday() < 5:      # drop weekend stubs
                out[d] = float(b["close"])
    return out


def build():
    fr, it, es, de = bars("FR10Y-FR"), bars("IT10Y-IT"), bars("ES10Y-ES"), bars("DE10Y-DE")
    lvl = {"France": fr[DAY], "Italy": it[DAY], "Spain": es[DAY], "Germany": de[DAY]}
    assert [round(v, 2) for v in lvl.values()] == [4.86, 4.60, 4.11, 3.49], lvl

    days = sorted(d for d in set(fr) & set(it) if d <= DAY)
    gap = {d: (fr[d] - it[d]) * 100 for d in days}
    first = next(d for d in days if gap[d] > 0)
    assert first == "20251007", first
    widest = max(days, key=lambda d: gap[d])
    assert (widest, round(gap[widest], 1)) == ("20261008", 27.7)
    assert round(gap[DAY], 1) == 26.4
    since = [d for d in days if d >= "20260804"]
    assert all(gap[d] > 0 for d in since)
    assert max(d for d in fr if fr[d] >= fr[DAY] and d < "20260901") == "20020730"
    assert days[0] < "19990201"

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)

    # ---- left: the four yields, plus the U.S. for comparison
    ax = fig.add_axes([0.105, 0.17, 0.34, 0.60])
    ax.set_facecolor(CREAM)
    names = ["France", "Italy", "Spain", "Germany"]
    ys = [5.3, 4.2, 3.1, 2.0]
    cols = [CORAL] + BLUES
    for n, y, c in zip(names, ys, cols):
        v = lvl[n]
        ax.barh(y, v, height=0.78, color=c, zorder=3)
        ax.text(v - 0.08, y, f"{v:.2f}%", ha="right", va="center", fontsize=19,
                fontweight="bold", color="white", zorder=4)
        ax.text(-0.12, y, n, ha="right", va="center", fontsize=16, fontweight="bold",
                color=DEEP if n == "France" else INK)
    ax.plot([-1.2, 5.6], [1.15, 1.15], color=GRID, lw=1.2, clip_on=False)
    ax.barh(0.45, US10, height=0.6, color=SLATE, zorder=3)
    ax.text(US10 - 0.08, 0.45, f"{US10:.2f}%", ha="right", va="center", fontsize=15,
            fontweight="bold", color="white", zorder=4)
    ax.text(-0.12, 0.45, "U.S.", ha="right", va="center", fontsize=14, fontweight="bold", color=INK)
    ax.text(0.0, -0.25, "For comparison: the U.S. 10-Year Treasury", ha="left", va="top",
            fontsize=11.5, color=MUTED)
    ax.set_xlim(0, 5.6)
    ax.set_ylim(-0.6, 5.85)
    ax.axis("off")
    fig.text(0.035, 0.79, "10-year yields, Friday, Oct. 9", fontsize=14, fontweight="bold",
             color=INK, ha="left", va="bottom")

    # ---- right: France minus Italy, since 2024
    bx = fig.add_axes([0.56, 0.17, 0.38, 0.60])
    bx.set_facecolor(CREAM)
    rd = [d for d in days if d >= "20240101"]
    x = [datetime.strptime(d, "%Y%m%d").date() for d in rd]
    y = [gap[d] / 100 for d in rd]
    bx.axhline(0, color=INK, lw=1.0, zorder=2)
    bx.fill_between(x, y, 0, where=[v > 0 for v in y], color="#f3c2b8", lw=0, zorder=1, interpolate=True)
    bx.plot(x, y, color=BLUE, lw=1.8, zorder=3, snap=False, solid_joinstyle="miter")
    fx = datetime.strptime(first, "%Y%m%d").date()
    bx.scatter([fx], [gap[first] / 100], s=50, color=CREAM, edgecolor=DEEP, linewidth=2, zorder=5)
    bx.annotate("First time above:\nOct. 7, 2025", xy=(fx, gap[first] / 100),
                xytext=(date(2024, 9, 1), 0.22), fontsize=11.5, color=DEEP, ha="left", va="center",
                linespacing=1.25, arrowprops=dict(arrowstyle="-", color=DEEP, lw=1))
    lx = datetime.strptime(DAY, "%Y%m%d").date()
    bx.scatter([lx], [gap[DAY] / 100], s=36, color=CORAL, edgecolor=CREAM, linewidth=1.6, zorder=6)
    bx.annotate(f"+{gap[DAY] / 100:.2f}\nOct. 9", xy=(lx, gap[DAY] / 100), xytext=(8, -4),
                textcoords="offset points", fontsize=13, fontweight="bold", color=DEEP,
                ha="left", va="top", linespacing=1.15)
    bx.text(date(2024, 1, 15), -1.32, "Italy paid more", fontsize=12, color=BLUE_D, ha="left", va="bottom")
    bx.text(date(2025, 11, 20), 0.36, "France pays more", fontsize=12, color=DEEP, ha="right", va="bottom")
    bx.set_xlim(date(2024, 1, 1), date(2026, 12, 20))
    bx.set_ylim(-1.35, 0.5)
    bx.set_yticks([-1.25, -1.0, -0.75, -0.5, -0.25, 0, 0.25])
    bx.set_yticklabels(["\u22121.25", "\u22121.00", "\u22120.75", "\u22120.50", "\u22120.25", "0", "+0.25"], fontsize=11, color=MUTED)
    bx.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    bx.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    for t in bx.get_xticklabels():
        t.set_fontsize(11)
        t.set_color(MUTED)
    bx.tick_params(axis="both", length=0, pad=6)
    bx.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    bx.set_axisbelow(True)
    for sp in bx.spines.values():
        sp.set_visible(False)
    fig.text(0.56, 0.79, "France minus Italy, percentage points", fontsize=14, fontweight="bold",
             color=INK, ha="left", va="bottom")

    fig.text(0.035, 0.955, "France Now Pays More to Borrow Than Italy", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895, "10-year government bond yields. Thursday's gap of 0.28 points was the "
             "widest in data back to 1999, and Friday's the second widest.",
             fontsize=13.2, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.065, "Sources: CNBC daily closing yields, Jan. 1999 to Oct. 9, 2026 (weekdays); "
             "U.S. Treasury daily yield curve, Oct. 9, 2026.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"france-italy-yields-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
