#!/usr/bin/env python3
"""
make-europe-inflation-chart.py  EU_DIR  [outdir]

Recreates the supplied graphic "Europe's Inflation Problem" for the 10/01/26
daily, adding August for each country and the U.S. and Bay Area for scale
(feedback-localize-national-studies).

  europe-inflation-100126.png      plain monogram -> RE email + Agent Hub
  europe-inflation-100126-hb.png   + wordmark     -> harvrealtor.com / .net / app

EU_DIR holds the primary releases saved with shell curl on 10/01/26:
  https___www.ine.es_dyngs_Prensa_en_adIPC0926.htm.html   INE flash, Sep 29
  https___www.istat.it_comunicato-stampa_prezzi-al-consumo-dati-provvisori-settembre-2026_.html
  insee_9056956.html                                      INSEE flash, Sep 30
  de_348.html  de_320.html                                Destatis 348 (Sep) and 320 (Aug)
  bls.json                                                BLS API, CUUR0000SA0 + CUURS49BSA0
Every value is matched against the release text at build time.

=============================================================================
VERIFICATION 10/01/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

  supplied   release (HICP, harmonised)          national CPI headline
  Spain 5.0  "HICP increases four tenths, to 5.0%"   4.9
  Italy 4.1  IPCA "+4,1% ... (da +3,2% ...)"           4.2
  France 3.4 IPCH "3,4 % en septembre 2026, apres +2,6 % en aout"   3.0
  Germany 3.3 "Harmonised index ... September 2026: +3.3%"          3.3

All four match, and all four are the HARMONISED index, the one the ECB's 2%
target is set on. The graphic never said so; in France and Italy the national
headline differs (3.0 and 4.2), so the chart says HICP outright. August is the
release's own prior month figure. Every country rose.

The U.S. and San Francisco area bars are CPI-U, a different index, so they sit
in a separate block with that label. August 2026 is the latest month for both
(the San Francisco series is bimonthly). Both round to 3.4%.

ECB deposit rate 2.50% after hikes on Jun 17 and Sep 16, 2026 (ECB press
release of Sep 10, 2026). Eurostat's euro area flash is due Oct 2.

matplotlib only; build with python3.13 on Mac.
"""
import html as htmllib
import json
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

EU = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "100126"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
SLATE = "#6f8296"
PALE = "#a7b3c0"
GRID = "#d8cdb8"
MUTED = "#8a8172"
GOLD = "#b07d12"


def flat(name):
    s = open(os.path.join(EU, name), encoding="utf-8", errors="ignore").read()
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
    return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", s)))


def one(x):
    return Decimal(x).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def europe():
    es = flat("https___www.ine.es_dyngs_Prensa_en_adIPC0926.htm.html")
    m = re.search(r"HICP increases four tenths, to (\d\.\d)%", es)
    es_sep = Decimal(m.group(1)); es_aug = es_sep - Decimal("0.4")

    it = flat("https___www.istat.it_comunicato-stampa_prezzi-al-consumo-dati-provvisori-settembre-2026_.html")
    m = re.search(r"\+(\d,\d)% su base annua \(da \+(\d,\d)% del mese precedente\)", it.split("armonizzato dei prezzi al consumo (IPCA)", 1)[1])
    it_sep, it_aug = (Decimal(g.replace(",", ".")) for g in m.groups())

    fr = flat("insee_9056956.html")
    m = re.search(r"augmenterait de (\d,\d) % en septembre 2026, après \+(\d,\d) % en août", fr)
    fr_sep, fr_aug = (Decimal(g.replace(",", ".")) for g in m.groups())

    de9 = flat("de_348.html"); de8 = flat("de_320.html")
    de_sep = Decimal(re.search(r"Harmonised index of consumer prices, September 2026: \+(\d\.\d)%", de9).group(1))
    de_aug = Decimal(re.search(r"Harmonised index of consumer prices, August 2026: \+(\d\.\d)%", de8).group(1))

    rows = [("Spain", es_sep, es_aug), ("Italy", it_sep, it_aug),
            ("France", fr_sep, fr_aug), ("Germany", de_sep, de_aug)]
    assert [(c, str(a), str(b)) for c, a, b in rows] == [
        ("Spain", "5.0", "4.6"), ("Italy", "4.1", "3.2"), ("France", "3.4", "2.6"), ("Germany", "3.3", "2.9")], rows
    return rows


def us():
    d = json.load(open(os.path.join(EU, "bls.json")))
    out = {}
    for s in d["Results"]["series"]:
        v = {(r["year"], r["period"]): Decimal(r["value"]) for r in s["data"]
             if re.fullmatch(r"\d+\.\d+", r["value"])}   # SF is bimonthly; odd months are "-"
        out[s["seriesID"]] = one((v[("2026", "M08")] / v[("2025", "M08")] - 1) * 100)
    assert out == {"CUUR0000SA0": Decimal("3.4"), "CUURS49BSA0": Decimal("3.4")}, out
    return [("United States", out["CUUR0000SA0"]), ("San Francisco area", out["CUURS49BSA0"])]


def build():
    rows = europe()
    usrows = us()
    print("europe:", [(c, str(a), str(b)) for c, a, b in rows], "| us:", [(c, str(v)) for c, v in usrows])

    fig, ax = plt.subplots(figsize=(12.8, 8.0), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)
    h = 0.62
    ys = [0, 1, 2, 3]
    for y, (c, sep, aug) in zip(ys, rows):
        ax.barh(y, float(sep), height=h, color=CORAL, zorder=3)
        ax.plot([float(aug)] * 2, [y - h / 2 - 0.06, y + h / 2 + 0.06], color=INK, lw=2.4, zorder=5)
        ax.text(float(sep) + 0.08, y, f"{one(sep)}%", ha="left", va="center", fontsize=17,
                fontweight="bold", color=DEEP, zorder=5)
        ax.text(float(sep) + 0.72, y, f"from {one(aug)}% in August", ha="left", va="center",
                fontsize=11.5, color=MUTED, zorder=5)
        ax.text(-0.1, y, c, ha="right", va="center", fontsize=16, color=INK)

    ax.text(0.06, 4.05, "For scale: consumer price index (CPI-U), August 2026", ha="left", va="center",
            fontsize=10.5, color=MUTED, style="italic", zorder=6,
            bbox=dict(boxstyle="square,pad=0.2", fc=CREAM, ec="none"))
    for y, (c, v) in zip((4.65, 5.45), usrows):
        ax.barh(y, float(v), height=0.5, color=SLATE, zorder=3)
        ax.text(float(v) + 0.08, y, f"{one(v)}%", ha="left", va="center", fontsize=14,
                fontweight="bold", color=INK, zorder=5)
        ax.text(-0.1, y, c, ha="right", va="center", fontsize=13.5, color=INK)

    ax.axvline(2.0, color=GOLD, lw=2.0, ls=(0, (4, 3)), zorder=4)
    ax.text(2.0, -0.62, "ECB target: 2%", ha="center", va="bottom", fontsize=12.5,
            fontweight="bold", color=GOLD, zorder=6,
            bbox=dict(boxstyle="square,pad=0.25", fc=CREAM, ec="none"))
    ax.axvline(0, color=INK, lw=1.0, zorder=4)
    ax.set_xlim(0, 7.4)
    ax.set_ylim(5.85, -0.85)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.045, 0.955, "Europe's Inflation Jumped in September",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.902,
             "Harmonised (HICP) annual inflation, September 2026 flash estimates; black tick marks August",
             fontsize=14, color=MUTED, ha="left", va="top")
    fig.text(
        0.045, 0.090,
        "All four rose from August. The ECB has raised its deposit rate twice this year, to 2.50%. "
        "The euro area figure is due Friday, October 2.\n"
        "National headlines differ in France (3.0%) and Italy (4.2%), which lead with their own CPI. "
        "U.S. and San Francisco area bars are CPI-U, a different index.",
        fontsize=11, color=DEEP, ha="left", va="bottom", linespacing=1.55,
    )
    fig.text(0.045, 0.034,
             "Sources: INE, Istat, INSEE, Destatis flash estimates of September 29 and 30, 2026; "
             "U.S. Bureau of Labor Statistics (not seasonally adjusted).",
             fontsize=10.5, color=MUTED, ha="left", va="bottom")
    fig.subplots_adjust(left=0.22, right=0.97, top=0.84, bottom=0.18)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"europe-inflation-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
