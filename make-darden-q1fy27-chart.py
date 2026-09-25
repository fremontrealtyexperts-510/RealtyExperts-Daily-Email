#!/usr/bin/env python3
"""
make-darden-q1fy27-chart.py  [outdir] [release.htm]

REALTY EXPERTS recreation of the "LongHorn Sizzles, Olive Garden Cools" graphic
for the 09/25/26 daily email. OUR OWN branded chart, not the source image.

VERIFIED AGAINST THE PRIMARY SOURCE: Darden's fiscal 2027 first quarter release,
SEC Form 8-K Exhibit 99.1, September 24, 2026. All five supplied bars match the
release's FISCAL CALENDAR column exactly (LongHorn 6.2%, Other Business 3.8%,
Consolidated 3.1%, Fine Dining 1.6%, Olive Garden 1.1%).

WHAT WE ADD, and why:
  * The release prints a second basis. Fiscal 2026 had 53 weeks, so the fiscal
    calendar compares June 1 to August 30, 2026 against May 26 to August 24,
    2025, a week offset. Darden also publishes a COMPARABLE calendar column
    (LongHorn 6.8%, Olive Garden 1.0%, Fine Dining 1.0%, Other 4.5%, total
    3.2%). The bars stay on the fiscal basis Darden headlines; the footnote
    carries the other column so neither is hidden.
  * Each segment's Q1 sales under its name. Olive Garden is the biggest brand by
    far, which is why its 1.1% weighs on the total more than LongHorn's 6.2%.
  * Other Business excludes Bahama Breeze (being closed or converted), per the
    release's footnote.

Every value is parsed from the release at run time, never hand typed.

matplotlib only; build with python3.13 on Mac.
"""
import html
import os
import re
import sys
import urllib.request
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
SRC = sys.argv[2] if len(sys.argv) > 2 else "/tmp/darden-q1fy27.htm"
URL = ("https://www.sec.gov/Archives/edgar/data/940944/000094094426000032/"
       "exhibit991-q1fy27.htm")
STAMP = "092526"

CREAM = "#fdf6e8"
INK = "#1f2933"
RUST = "#c8692f"
DEEP = "#b8433a"
SLATE = "#4a5568"
MUTED = "#8a8172"
GRID = "#d8cdb8"

SEGMENTS = ["Olive Garden", "LongHorn Steakhouse", "Fine Dining", "Other Business"]
TOTAL = "Consolidated Darden"


def text():
    if not os.path.exists(SRC):
        req = urllib.request.Request(URL, headers={
            "User-Agent": "Harv Balu research harvrealtor@outlook.com"})
        with urllib.request.urlopen(req, timeout=60) as r:
            open(SRC, "wb").write(r.read())
    b = open(SRC, encoding="utf-8", errors="ignore").read()
    b = re.sub(r"(?is)<(script|style).*?</\1>", "", b)
    b = re.sub(r"(?i)</td>", " | ", b)
    t = html.unescape(re.sub(r"<[^>]+>", " ", b))
    return re.sub(r"\s+", " ", t)


def parse(t):
    comps, sales = {}, {}
    for name in [TOTAL] + SEGMENTS:
        # same-restaurant sales table: name (footnote digit optional) | fiscal | comparable
        m = re.search(re.escape(name) + r"\s*1?\s*\|\s*(-?\d+\.\d)%\s*\|\s*(-?\d+\.\d)%", t)
        assert m, f"no same-restaurant row for {name}"
        comps[name] = (Decimal(m.group(1)), Decimal(m.group(2)))
        m = re.search(re.escape(name) + r"\s*\|[\s|]*\$([\d,]+\.\d)\s*\|[\s|]*\$([\d,]+\.\d)", t)
        assert m, f"no sales row for {name}"
        sales[name] = Decimal(m.group(1).replace(",", ""))
    # the headline sentence must agree with the table
    m = re.search(r"Blended same-restaurant sales\s*1?\s*for the quarter increased "
                  r"(\d+\.\d)% on a fiscal calendar basis", t)
    assert m and Decimal(m.group(1)) == comps[TOTAL][0], "headline vs table mismatch"
    return comps, sales


def money(m):
    if m >= 1000:
        b = (m / 1000).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"${b}B"
    return f"${m.quantize(Decimal('1'), rounding=ROUND_HALF_UP)}M"


def build(comps, sales):
    names = sorted([TOTAL] + SEGMENTS, key=lambda n: comps[n][0], reverse=True)
    label = {TOTAL: "Darden overall", "LongHorn Steakhouse": "LongHorn Steakhouse",
             "Other Business": "Other brands", "Fine Dining": "Fine Dining",
             "Olive Garden": "Olive Garden"}
    top = max(float(comps[n][0]) for n in names)

    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    fig.text(0.062, 0.925, "LongHorn Carries Darden's Quarter",
             fontsize=30, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.062, 0.858,
             "Same-restaurant sales growth by segment, first quarter of fiscal 2027 "
             "(June 1 to August 30, 2026)",
             fontsize=14.5, color=MUTED, ha="left", va="top")

    ax = fig.add_axes((0.33, 0.2, 0.6, 0.58))
    ax.set_facecolor(CREAM)
    ys = list(range(len(names)))[::-1]
    ax.set_xlim(0, top * 1.22)
    ax.set_ylim(-0.6, len(names) - 0.4)
    for y, n in zip(ys, names):
        v = float(comps[n][0])
        is_total = n == TOTAL
        color = SLATE if is_total else (DEEP if n == "LongHorn Steakhouse" else RUST)
        ax.barh(y, v, height=0.56, color=color, zorder=3)
        ax.text(v + top * 0.02, y, f"{comps[n][0]}%", va="center", ha="left",
                fontsize=22, fontweight="bold", color=color)
        sub = ("all brands" if is_total else "Q1 sales") + f" {money(sales[n])}"
        fig_y = ax.transData.transform((0, y))[1] / fig.bbox.height
        fig.text(0.062, fig_y + 0.013, label[n], fontsize=17, fontweight="bold",
                 color=SLATE if is_total else INK, ha="left", va="center")
        fig.text(0.062, fig_y - 0.027, sub, fontsize=12, color=MUTED,
                 ha="left", va="center")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ("top", "right", "bottom"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(GRID)

    c = {n: comps[n][1] for n in names}
    fig.text(0.062, 0.128,
             "Fiscal calendar basis, as Darden headlines it. On its comparable calendar "
             f"basis: LongHorn {c['LongHorn Steakhouse']}%, other brands "
             f"{c['Other Business']}%, overall {c[TOTAL]}%,",
             fontsize=11.5, color=MUTED, ha="left", va="top")
    fig.text(0.062, 0.093,
             f"Fine Dining {c['Fine Dining']}%, Olive Garden {c['Olive Garden']}%. "
             "Other brands excludes Bahama Breeze, which is being closed or converted.",
             fontsize=11.5, color=MUTED, ha="left", va="top")
    fig.text(0.062, 0.035,
             "Source: Darden Restaurants fiscal 2027 first quarter results, "
             "SEC Form 8-K Exhibit 99.1, September 24, 2026.",
             fontsize=10.5, color=MUTED, ha="left", va="bottom")
    return fig, names


if __name__ == "__main__":
    comps, sales = parse(text())
    fig, names = build(comps, sales)
    for n in names:
        print(f"  {n:22s} fiscal {comps[n][0]}%  comparable {comps[n][1]}%  "
              f"sales ${sales[n]}M")
    save_pair(fig, os.path.join(OUTDIR, f"darden-q1fy27-{STAMP}.png"),
              facecolor=CREAM)
