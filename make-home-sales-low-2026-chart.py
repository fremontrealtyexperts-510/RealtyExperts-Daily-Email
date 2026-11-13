"""
make-home-sales-low-2026-chart.py  NAR_2023_TXT  NAR_2025_TXT  NAR_OCT26_HTML  MLS_2025_CSV  MLS_2026_CSV  [outdir]

The 11/13/26 daily's Real Estate chart. Harv supplied "Home Sales Sink to a 16-Year
Low" (U.S. existing home sales: 2021 6.12M, 2022 5.03M, 2023 4.09M, 2024 4.06M,
2025 4.06M, Oct. 2026 annual pace 3.75M). Rebuilt as OUR chart from NAR's own
tables, and kept local: a second panel compares homes in contract and on the
market on our own MLS board, Nov. 13, 2025 vs Nov. 13, 2026, from the saved
exports (same 21 column Paragon export, same status buckets as RE-Daily-1).

Emits BOTH:
  home-sales-low-111326.png      plain HB monogram    -> RE email + Agent Hub
  home-sales-low-111326-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

Inputs:
  NAR_2023_TXT   pdftotext -layout of nar.realtor/sites/default/files/documents/
                 ehs-04-2023-breakouts-of-single-family-condo-and-co-op-2023-05-18.pdf  (2021, 2022)
  NAR_2025_TXT   pdftotext -layout of nar.realtor/sites/default/files/2026-01/
                 ehs-12-2025-overview-2026-01-14.pdf                                     (2023, 2024, 2025)
  NAR_OCT26_HTML the Nov. 12, 2026 NAR release (October: 3.75 million SAAR)
  MLS_2025_CSV   "MLS_Defined_Spread_Sheet_4 - 111325 - 1055am.xlsx" from the Drive archive, as CSV
  MLS_2026_CSV   today's export (/tmp/mls-today.csv, sheet 111326)
  Listing level CSVs are inputs only; nothing but the counts is drawn or stored.

=============================================================================
VERIFICATION 11/13/26
=============================================================================
* NAR annual totals: 2021 6,120,000 and 2022 5,030,000 (2023 breakout table);
  2023 4,090,000, 2024 4,060,000 and 2025 4,060,000 (Dec. 2025 overview; the
  unrounded 2025 total is 4.061M). October 2026: 3.75 million SAAR, the lowest
  since August 2010 (NAR, Nov. 12, 2026). All six bars of the graphic match.
* Our board, the 14 cities present in both exports (Milpitas joined the export
  in January 2026): in contract (PEND) 838 -> 596, down 28.9%; on the market
  (ACTV, NEW, PCH, BOMK) 1,673 -> 1,715, up 2.5%.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import csv
import html
import os
import re
import sys
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

T23, T25, OCT, M25, M26 = sys.argv[1:6]
OUTDIR = sys.argv[6] if len(sys.argv) > 6 else "."
STAMP = "111326"

CREAM = "#fdf6e8"
INK = "#1f2933"
RED = "#c8102e"
SLATE = "#7d8a96"
SAND = "#c9bb9f"
GRID = "#e6dcc8"
MUTED = "#8a8172"

ACTIVE = {"ACTV", "PCH", "BOMK", "NEW"}     # RE-Daily-1's "Active/BOMK/PCH/New" bucket
PENDING = {"PEND"}                           # RE-Daily-1's "Pending" columns


def annual(txt, year):
    t = open(txt, encoding="utf-8").read()
    m = re.search(r"^\s*%d\s+([\d,]{9})\s" % year, t, flags=re.M)
    assert m, (txt, year)
    return int(m.group(1).replace(",", ""))


def load_us():
    vals = {2021: annual(T23, 2021), 2022: annual(T23, 2022),
            2023: annual(T25, 2023), 2024: annual(T25, 2024), 2025: annual(T25, 2025)}
    assert vals == {2021: 6120000, 2022: 5030000, 2023: 4090000, 2024: 4060000, 2025: 4060000}, vals
    t = open(OCT, encoding="utf-8", errors="ignore").read()
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>", " ", t, flags=re.S))))
    assert "decreased 5.5% to a seasonally adjusted annual rate of 3.75 million in October" in t
    assert "lowest level since August 2010" in t
    return vals, 3750000


def board(path):
    c = Counter()
    for r in csv.DictReader(open(path, encoding="utf-8")):
        c[(r["City"].strip().title(), r["Status"].strip())] += 1
    return c


def load_local():
    a, b = board(M25), board(M26)
    ca = {k[0] for k in a}
    cb = {k[0] for k in b}
    common = sorted(ca & cb)
    assert len(common) == 14 and cb - ca == {"Milpitas"} and not ca - cb, (common, cb - ca, ca - cb)
    tot = lambda c, st: sum(n for (city, s), n in c.items() if city in common and s in st)
    out = {"pend": (tot(a, PENDING), tot(b, PENDING)), "act": (tot(a, ACTIVE), tot(b, ACTIVE))}
    assert out == {"pend": (838, 596), "act": (1673, 1715)}, out
    return out


def pct(a, b):
    return (Decimal(b) / Decimal(a) - 1) * 100


def build():
    us, oct26 = load_us()
    loc = load_local()

    fig = plt.figure(figsize=(14.0, 7.8), dpi=100)
    fig.patch.set_facecolor(CREAM)

    # ---- left: United States -------------------------------------------------
    ax = fig.add_axes([0.045, 0.19, 0.555, 0.53])
    ax.set_facecolor(CREAM)
    labels = ["2021", "2022", "2023", "2024", "2025", "Oct. 2026"]
    vals = [us[y] / 1e6 for y in (2021, 2022, 2023, 2024, 2025)] + [oct26 / 1e6]
    cols = [SLATE] * 5 + [RED]
    ax.bar(range(6), vals, width=0.66, color=cols, zorder=3)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.12, f"{v:.2f}M", ha="center", va="bottom", fontsize=16, fontweight="bold",
                color=RED if i == 5 else INK)
        ax.text(i, -0.22, labels[i], ha="center", va="top", fontsize=14, color=RED if i == 5 else INK,
                fontweight="bold" if i == 5 else "normal")
    ax.text(5, -0.62, "annual pace", ha="center", va="top", fontsize=12, color=MUTED)
    ax.axhline(0, color=SAND, lw=1.4, zorder=1)
    ax.set_xlim(-0.6, 5.6)
    ax.set_ylim(-0.05, 7.0)
    ax.axis("off")
    fig.text(0.045, 0.775, "United States: existing home sales, millions", fontsize=15, fontweight="bold",
             color=INK, ha="left", va="bottom")

    # ---- right: our board ----------------------------------------------------
    bx = fig.add_axes([0.665, 0.19, 0.31, 0.53])
    bx.set_facecolor(CREAM)
    groups = [("In contract", loc["pend"]), ("On the market", loc["act"])]
    w = 0.36
    for g, (lab, (y25, y26)) in enumerate(groups):
        bx.bar(g - w / 2 - 0.02, y25, width=w, color=SAND, zorder=3)
        bx.bar(g + w / 2 + 0.02, y26, width=w, color=RED, zorder=3)
        bx.text(g - w / 2 - 0.02, y25 + 30, f"{y25:,}", ha="center", va="bottom", fontsize=14, color=MUTED,
                fontweight="bold")
        bx.text(g + w / 2 + 0.02, y26 + 30, f"{y26:,}", ha="center", va="bottom", fontsize=14,
                color=RED, fontweight="bold")
        p = pct(y25, y26).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        word = "down" if p < 0 else "up"
        bx.text(g, -45, lab, ha="center", va="top", fontsize=14, color=INK)
        bx.text(g, -150, f"{word} {abs(p)}%", ha="center", va="top", fontsize=13.5, fontweight="bold",
                color=RED if g == 0 else INK)
    bx.axhline(0, color=SAND, lw=1.4, zorder=1)
    bx.set_xlim(-0.62, 1.62)
    bx.set_ylim(-14.5, 2030)
    bx.axis("off")
    fig.text(0.665, 0.775, "Here: our 14 city board, a year apart", fontsize=15, fontweight="bold", color=INK,
             ha="left", va="bottom")
    fig.text(0.665, 0.745, "■", fontsize=13, color=SAND, ha="left", va="bottom")
    fig.text(0.680, 0.745, "Nov. 13, 2025", fontsize=12, color=MUTED, ha="left", va="bottom")
    fig.text(0.790, 0.745, "■", fontsize=13, color=RED, ha="left", va="bottom")
    fig.text(0.805, 0.745, "Nov. 13, 2026", fontsize=12, color=MUTED, ha="left", va="bottom")

    fig.text(0.035, 0.955, "Home Sales Sink to a 16-Year Low", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.897, "October's 3.75 million annual pace is the slowest since August 2010", fontsize=13.5,
             color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.055, "Source: National Association of Realtors (Oct. 2026 = seasonally adjusted annual rate). "
             "Our board: Bay East MLS exports for the 14 cities in both files", fontsize=10.2, color=MUTED,
             ha="left", va="bottom")
    fig.text(0.035, 0.025, "(Milpitas joined in 2026). In contract = pending; on the market = active, new, price "
             "change and back on market.", fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"home-sales-low-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
