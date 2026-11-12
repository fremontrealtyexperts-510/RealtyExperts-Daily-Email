"""
make-condo-sellers-buyers-2026-chart.py  REDFIN_HTML  [outdir]

The 11/12/26 daily's Real Estate chart. Harv supplied "Condo Sellers Outnumber
Buyers" (% more condo sellers than buyers, September 2026: San Antonio 459%,
Houston 322%, Miami 274%, Austin 258%, Phoenix 255%, U.S. overall 123%).
Rebuilt as OUR chart from Redfin's own metro table, and kept local: the same
table carries the three Bay Area metros, so they are drawn underneath on the
identical method and month (one publisher, one month, one measure).

Emits BOTH:
  condo-sellers-buyers-111226.png      plain HB monogram    -> RE email + Agent Hub
  condo-sellers-buyers-111226-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

REDFIN_HTML is the saved page https://www.redfin.com/news/condo-fall-2026/
("For Every Condo Buyer in the U.S., There Are More Than Two Sellers", published
Nov. 9, 2026), whose "Metro-Level Summary for Condos, September 2026" table lists
the 50 most populous metros with buyers, sellers and the percent gap.

=============================================================================
VERIFICATION 11/12/26
=============================================================================
* Table: San Antonio 458.5% (104 buyers, 583 sellers), Houston 321.6%, Miami
  273.6%, Austin 257.6%, Phoenix 254.6%; next is Nashville 253.3%. All five
  bars of the supplied graphic match after rounding half up, in the same order.
* U.S. 123% is stated in the article text ("123% more condo sellers than buyers
  nationwide in September ... the largest gap in records dating back to 2013",
  up from 95.5% a year earlier).
* Bay Area: Oakland metro (Alameda and Contra Costa counties) 69.1%, 725 buyers
  and 1,226 sellers; San Jose 64.6%, 428 and 704; San Francisco 6.3%, 908 and
  965, which Redfin calls balanced (within 10%).
* Buyers and sellers are Redfin estimates printed as whole numbers, so the percent
  recomputed from them can drift (San Antonio 460.6 vs 458.5); asserted within 2.5
  points to catch a misread column. The chart draws Redfin's printed percent.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import html
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

SRC = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "111226"

CREAM = "#fdf6e8"
INK = "#1f2933"
RED = "#c8102e"
SLATE = "#7d8a96"
SAND = "#b9a888"
GRID = "#e6dcc8"
MUTED = "#8a8172"

TOP = ["San Antonio, TX", "Houston, TX", "Miami, FL", "Austin, TX", "Phoenix, AZ"]
BAY = [("Oakland, CA", "Oakland metro"), ("San Jose, CA", "San Jose metro"),
       ("San Francisco, CA", "San Francisco metro")]
US = Decimal("123")


def load():
    t = open(SRC, encoding="utf-8", errors="ignore").read()
    assert "Metro-Level Summary for Condos, September 2026" in re.sub(r"\s+", " ", html.unescape(
        re.sub(r"<[^>]+>", " ", t)))
    txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>", " ", t, flags=re.S))))
    assert "There were 123% more condo sellers than buyers nationwide in September" in txt
    rows = {}
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", t, flags=re.S):
        c = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", x))).strip()
             for x in re.findall(r"<td[^>]*>(.*?)</td>", r, flags=re.S)]
        if len(c) == 5 and c[2].endswith("%"):
            pct, buyers, sellers = Decimal(c[2][:-1]), int(c[3]), int(c[4])
            # buyers and sellers are Redfin ESTIMATES printed as whole numbers, so the percent recomputed from
            # them drifts from the printed one (San Antonio, 104 buyers: 460.6 vs 458.5). This guards against a
            # misread column, not rounding: the two must agree within 2.5 points. The chart draws the PRINTED %.
            calc = (Decimal(sellers) / Decimal(buyers) - 1) * 100
            assert abs(calc - pct) <= Decimal("2.5"), (c, calc)
            rows[c[0]] = (pct, buyers, sellers, c[1])
    assert len(rows) == 50, len(rows)
    ranked = sorted(rows, key=lambda k: rows[k][0], reverse=True)
    assert ranked[:5] == TOP, ranked[:6]
    got = [int(rows[k][0].quantize(Decimal("1"), rounding=ROUND_HALF_UP)) for k in TOP]
    assert got == [459, 322, 274, 258, 255], got
    return rows


def r0(p):
    return int(p.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def build():
    rows = load()
    items = [(k.split(",")[0], rows[k][0], SLATE, None) for k in TOP]
    items.append(("U.S. overall", US, INK, None))
    for k, lab in BAY:
        pct, b, s, power = rows[k]
        note = f"{s:,} sellers, {b:,} buyers" + ("  (balanced)" if power.startswith("Balanced") else "")
        items.append((lab, pct, RED, note))

    fig = plt.figure(figsize=(14.0, 7.8), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.235, 0.10, 0.70, 0.70])
    ax.set_facecolor(CREAM)
    ys = [0, 1, 2, 3, 4, 5.35, 6.7, 7.7, 8.7]
    for (lab, pct, col, note), y in zip(items, ys):
        v = float(pct)
        ax.barh(y, v, height=0.68, color=col, zorder=3)
        ax.text(-8, y, lab, ha="right", va="center", fontsize=15, color=col if col == RED else INK,
                fontweight="bold")
        ax.text(v + 6, y, f"{r0(pct)}%", ha="left", va="center", fontsize=16, fontweight="bold",
                color=col if col != SLATE else "#4f5b66")
        if note:
            ax.text(128, y, note, ha="left", va="center", fontsize=12.5, color=MUTED)
    for y in (4.675, 6.025):
        ax.axhline(y, color=GRID, lw=1.4, zorder=1)
    ax.set_xlim(0, 520)
    ax.set_ylim(9.3, -0.6)
    ax.axis("off")

    fig.text(0.035, 0.955, "Condo Sellers Outnumber Buyers, Far Less So Here", fontsize=26, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.897, "% more condo sellers than buyers, September 2026: the widest gaps among the 50 largest "
             "metros, the U.S., and the Bay Area", fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.03, "Source: Redfin, Metro-Level Summary for Condos, September 2026 (published Nov. 9, 2026). "
             "Oakland metro = Alameda and Contra Costa counties.", fontsize=10.2, color=MUTED, ha="left",
             va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"condo-sellers-buyers-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
