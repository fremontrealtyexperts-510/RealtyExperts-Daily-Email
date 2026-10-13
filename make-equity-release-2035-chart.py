#!/usr/bin/env python3
"""
make-equity-release-2035-chart.py  DATA_DIR  [outdir]

The 10/13/26 daily's home equity chart. Harv attached the newsletter graphic
"Home Equity Cash-Outs Set To Triple" (two bars, "Global annual equity release
volume, in U.S. dollars": TODAY 2025 to 26 $20B, 2035 projected $60B, ~3X;
"Source: EPPARG & EY via HousingWire (Oct. 2026); converted from euros at
~$1.15/EUR"). Emits BOTH:

  equity-release-101326.png      plain HB monogram    -> RE email + Agent Hub
  equity-release-101326-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds survey.txt (pdftotext -layout of EY's "Global Equity Release
Survey 2026" for EPPARG, epparg.org/wp-content/uploads/2026/10/
Global_ERM_Survey-2026-FINAL.pdf, published Oct. 12, 2026) and ecb.xml (the ECB
euro reference rates, eurofxref-daily.xml, Oct. 13, 2026). Both fetched Oct. 13,
2026 about 10:40 AM PT.

=============================================================================
VERIFICATION 10/13/26
=============================================================================
The survey's page 12 table is in EUROS: "Current annual volumes (EUR bn)"
Total (Global) 17.7, "Predicted annual volumes in 10 years (EUR bn)" 52.1,
across 14 markets, and the country columns sum exactly to both totals. Market
Briefs printed "$17.7B" and "$52.1B" (wrong currency; EPPARG's own press
release carries the same "$"). The graphic's $20B/$60B used ~$1.15; at the ECB
rate on Oct. 13 (1.1188) it is $19.8B today and $58.3B in 2035, 2.94 times.
Three label fixes: it is 14 surveyed markets, not "global"; the products are
lifetime (reverse) mortgages and home reversions, NOT cash-out refinances; and
it is annual new volume, a flow, not outstanding balances. HousingWire swapped
the U.S. and Europe columns in its copy; the U.S. is the largest market,
EUR 7.7bn now and 21.5bn in 2035, taken here from EY's table, not HousingWire.

Our addition: the by-country panel, so the U.S. share is visible.

matplotlib; build with python3.13 on Mac.
"""
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "101326"

CREAM = "#fdf6e8"
INK = "#1f2933"
ORANGE = "#ea580c"
ORANGE_D = "#b8460a"
TAN = "#d9c7a7"
TAN_D = "#8a7a5c"
GRID = "#d8cdb8"
MUTED = "#8a8172"

COLS = ["Australia", "Canada", "France", "Germany", "Hong Kong", "Italy", "Ireland",
        "Netherlands", "Norway", "Poland", "Spain", "Sweden", "U.K.", "U.S.",
        "Total (Europe)", "Total (Global)"]
SHOW = ["U.S.", "U.K.", "Canada", "Italy", "Netherlands", "Spain", "Australia", "France"]


def num(tok):
    return Decimal("0") if tok == "<0.1" else Decimal(tok)


def load():
    txt = open(os.path.join(DATA, "survey.txt"), errors="ignore").read()
    head = txt.index("Predicted")
    pred_line = [l for l in txt[head:head + 2000].splitlines() if l.strip().startswith("2.8")][0]
    cur_i = txt.index("Current annual", head)
    cur_line = [l for l in txt[cur_i:cur_i + 1500].splitlines() if l.strip().startswith("1.2")][0]
    pred = pred_line.split()                # Hong Kong is "Not stated": 15 numbers
    cur = cur_line.split()                  # 16 numbers
    assert len(cur) == 16 and len(pred) == 15, (cur, pred)
    pred = pred[:4] + ["0"] + pred[4:]      # Hong Kong 2035 not stated, counted as 0 in EY's total
    now = {c: num(v) for c, v in zip(COLS, cur)}
    later = {c: num(v) for c, v in zip(COLS, pred)}
    assert (now["Total (Global)"], later["Total (Global)"]) == (Decimal("17.7"), Decimal("52.1"))
    assert (now["U.S."], later["U.S."]) == (Decimal("7.7"), Decimal("21.5"))
    countries = COLS[:14]
    assert sum(now[c] for c in countries) == Decimal("17.7")       # Poland "<0.1" taken as 0
    assert sum(later[c] for c in countries) == Decimal("52.1")

    ecb = open(os.path.join(DATA, "ecb.xml")).read()
    assert "time='2026-10-13'" in ecb
    fx = Decimal(re.search(r"currency='USD' rate='([0-9.]+)'", ecb).group(1))
    assert fx == Decimal("1.1188"), fx
    usd = lambda e: float((e * fx).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
    tot = (usd(now["Total (Global)"]), usd(later["Total (Global)"]))
    assert tot == (19.8, 58.3), tot
    rows = [(c, usd(now[c]), usd(later[c])) for c in SHOW]
    others = [c for c in countries if c not in SHOW]
    rows.append(("Six others", usd(sum(now[c] for c in others)), usd(sum(later[c] for c in others))))
    assert rows[0] == ("U.S.", 8.6, 24.1), rows[0]
    mult = later["Total (Global)"] / now["Total (Global)"]
    return tot, rows, float(mult), float(fx)


def build():
    tot, rows, mult, fx = load()
    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)

    # left: the two totals
    ax = fig.add_axes([0.05, 0.17, 0.30, 0.60])
    ax.set_facecolor(CREAM)
    ax.bar([0, 1], tot, width=0.62, color=[TAN, ORANGE], zorder=3)
    for i, v in enumerate(tot):
        ax.text(i, v + 1.2, f"${v:.1f}B", fontsize=24, fontweight="bold",
                color=TAN_D if i == 0 else ORANGE_D, ha="center", va="bottom")
    ax.text(0.5, 33, f"{mult:.1f}x", fontsize=17, fontweight="bold", color="white", ha="center",
            va="center", bbox=dict(boxstyle="round,pad=0.45", facecolor=INK, edgecolor="none"))
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Today\n(2025/26)", "2035\nforecast"], fontsize=13.5, color=INK, linespacing=1.3)
    ax.set_xlim(-0.55, 1.55)
    ax.set_ylim(0, 68)
    ax.set_yticks([])
    ax.tick_params(axis="x", length=0, pad=8)
    for sp in ["top", "right", "left"]:
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    fig.text(0.05, 0.80, "All 14 markets surveyed", fontsize=14, fontweight="bold", color=INK,
             ha="left", va="bottom")

    # right: by country, today vs 2035
    bx = fig.add_axes([0.50, 0.17, 0.44, 0.60])
    bx.set_facecolor(CREAM)
    n = len(rows)
    ys = list(range(n))[::-1]
    h = 0.36
    for y, (name, a, b) in zip(ys, rows):
        us = name == "U.S."
        bx.barh(y + h / 2, b, height=h, color=ORANGE if us else "#f0a46f", zorder=3)
        bx.barh(y - h / 2, a, height=h, color=TAN, zorder=3)
        bx.text(b + 0.35, y + h / 2, f"${b:.1f}B", fontsize=12.5, fontweight="bold",
                color=ORANGE_D, ha="left", va="center")
        bx.text(a + 0.35, y - h / 2, f"${a:.1f}B", fontsize=11, color=TAN_D, ha="left", va="center")
    bx.set_yticks(ys)
    bx.set_yticklabels([r[0] for r in rows], fontsize=13)
    for lab in bx.get_yticklabels():
        lab.set_color(ORANGE_D if lab.get_text() == "U.S." else INK)
        if lab.get_text() == "U.S.":
            lab.set_fontweight("bold")
    bx.set_xlim(0, 28.5)
    bx.set_ylim(-0.7, n - 0.3)
    bx.set_xticks([])
    bx.tick_params(axis="y", length=0, pad=8)
    for sp in bx.spines.values():
        sp.set_visible(False)
    fig.text(0.50, 0.80, "By country", fontsize=14, fontweight="bold", color=INK, ha="left", va="bottom")
    fig.text(0.605, 0.80, "■", fontsize=14, color=TAN, ha="left", va="bottom")
    fig.text(0.62, 0.80, "today", fontsize=12.5, color=TAN_D, ha="left", va="bottom")
    fig.text(0.67, 0.80, "■", fontsize=14, color=ORANGE, ha="left", va="bottom")
    fig.text(0.685, 0.80, "2035 forecast", fontsize=12.5, color=ORANGE_D, ha="left", va="bottom")

    fig.text(0.035, 0.955, "Reverse Mortgage Cash Set To Nearly Triple By 2035", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895, "Home equity released each year through reverse mortgages and home "
             "reversions, in billions of U.S. dollars", fontsize=13.2, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035, "Source: EY Global Equity Release Survey 2026 for EPPARG (Oct. 12, 2026), reported in euros "
             "(\u20ac17.7 billion today, \u20ac52.1 billion in 2035) and\nconverted at the ECB reference rate of "
             f"${fx:.4f} on Oct. 13, 2026. Six others: Germany, Hong Kong, Ireland, Norway, Poland and Sweden "
             "(Hong Kong gave no 2035 forecast).",
             fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.4)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"equity-release-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
