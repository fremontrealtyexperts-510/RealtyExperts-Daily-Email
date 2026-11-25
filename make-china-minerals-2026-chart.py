#!/usr/bin/env python3
"""
make-china-minerals-2026-chart.py  USGS_TXT_DIR  [outdir]

The 11/25/26 daily's Economy chart. Harv supplied "China's Grip On Key Minerals"
(Bloomberg, Nov. 24, 2026; USGS): share of world production in 2025, gallium
(low purity) 99%, graphite (natural) 80%, antimony (mined) 36%.

A supplied graphic is a design brief, not a data source. Checked against the
USGS Mineral Commodity Summaries 2026 (February 2026), one page per mineral:
  https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-gallium.pdf   (and -graphite, -antimony)
USGS_TXT_DIR holds gallium.txt, graphite.txt, antimony.txt made with
`pdftotext -layout`. Every 2025 tonnage below is asserted to sit on its
country's line (or the next line, where USGS's "e" footnote wraps it) in those
files, and each world total is asserted against USGS's rounded total.

  * Gallium: China 900,000 kg of 909,000 kg = 99.0%. USGS text: "China accounted
    for 99%". Correct.
  * Graphite: China 1,400,000 t of the 1,752,880 t the country rows add to = 79.9%,
    so the graphic's 80% is right on USGS's own table. USGS's narrative says
    "an estimated 82%"; the footer says so.
  * Antimony: China 40,000 t of 110,720 t = 36.1%. Correct. Russia (32,000) and
    Tajikistan (22,000) are next, which the graphic left out; they are drawn.

Emits BOTH:
  china-minerals-112526.png      plain HB monogram    -> RE email + Agent Hub
  china-minerals-112526-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app
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

SRC = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "112526"

CREAM = "#fdf6e8"
INK = "#1f2933"
MUTED = "#8a8172"
CORAL = "#e2574c"
TEAL = "#2a8c82"
TEAL2 = "#7fb8b0"
SAND = "#e2d7bf"

# 2025e column, USGS MCS 2026. (country, tonnage string exactly as USGS prints it)
DATA = {
    "gallium": dict(unit="kg", world="900,000", rows=[("China", "900,000"), ("Japan", "3,000"), ("Russia", "6,000")]),
    "graphite": dict(unit="t", world="1,800,000", rows=[
        ("Austria", "200"), ("Brazil", "65,000"), ("Canada", "8,000"), ("China", "1,400,000"), ("Germany", "140"),
        ("India", "17,000"), ("Korea, North", "8,000"), ("Korea, Republic of", "500"), ("Madagascar", "80,000"),
        ("Mexico", "740"), ("Mozambique", "60,000"), ("Norway", "6,600"), ("Russia", "25,000"), ("Sri Lanka", "3,200"),
        ("Tanzania", "75,000"), ("Turkey", "2,200"), ("Ukraine", "800"), ("Vietnam", "500")]),
    "antimony": dict(unit="t", world="110,000", rows=[
        ("Australia", "1,300"), ("Bolivia", "5,000"), ("Burma", "4,500"), ("China", "40,000"), ("Guatemala", "50"),
        ("Iran", "90"), ("Kazakhstan", "800"), ("Kyrgyzstan", "700"), ("Laos", "200"), ("Mexico", "600"),
        ("Pakistan", "260"), ("Russia", "32,000"), ("Tajikistan", "22,000"), ("Turkey", "3,000"), ("Vietnam", "220")]),
}
EXPECT = {"gallium": "99.0", "graphite": "79.9", "antimony": "36.1"}   # China's share, printed precision


def r(x, p="0.1"):
    return Decimal(x).quantize(Decimal(p), ROUND_HALF_UP)


def n(s):
    return Decimal(s.replace(",", ""))


def verify(name, spec):
    lines = open(os.path.join(SRC, f"{name}.txt")).read().splitlines()
    i0 = next(i for i, l in enumerate(lines) if re.search(r"World .*Production", l))
    i1 = next(i for i in range(i0, len(lines)) if "2025e" in lines[i])     # the table's column header
    block = lines[i1 + 1:]
    for country, val in spec["rows"]:
        j = next(i for i, l in enumerate(block) if re.match(r"\s*" + re.escape(country) + r"(e\b|\b)", l))
        near = " ".join(block[j:j + 3])          # USGS's "e" footnote can push the numbers onto the next line
        assert re.search(r"(?<![\d,])\d?" + re.escape(val) + r"(?![\d,])", near), (name, country, val, near)
    wt = next(l for l in block if "World total" in l)
    assert spec["world"] in wt, (name, wt)


def shares(spec):
    tot = sum(n(v) for _, v in spec["rows"])
    return {c: n(v) / tot * 100 for c, v in spec["rows"]}, tot


def build():
    S = {}
    for name, spec in DATA.items():
        verify(name, spec)
        sh, tot = shares(spec)
        assert str(r(sh["China"])) == EXPECT[name], (name, sh["China"])
        S[name] = (sh, tot)
        print(name, "total", tot, "China", r(sh["China"], "0.01"),
              sorted(((c, str(r(v))) for c, v in sh.items()), key=lambda kv: -Decimal(kv[1]))[:4])
    assert r(S["antimony"][0]["Russia"] + S["antimony"][0]["Tajikistan"]) == Decimal("48.8")   # "nearly half"
    assert S["antimony"][1] == 110720 and S["graphite"][1] == 1752880 and S["gallium"][1] == 909000

    rows = [
        ("Gallium", "low purity", "chips, LEDs, lasers", "gallium", [("Russia", None), ("Japan", None)],
         "Russia and Japan make the other 1%"),
        ("Graphite", "natural", "batteries, brake linings, steel", "graphite", [("Madagascar", TEAL), ("Tanzania", TEAL2)],
         "Next: Madagascar {Madagascar}%, Tanzania {Tanzania}%"),
        ("Antimony", "mined", "flame retardants, ammunition", "antimony", [("Russia", TEAL), ("Tajikistan", TEAL2)],
         "Russia and Tajikistan together mine nearly half"),
    ]

    fig = plt.figure(figsize=(14.0, 7.9), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.20, 0.17, 0.755, 0.62])
    ax.set_facecolor(CREAM)
    H = 0.52
    for k, (title, kind, use, key, nexts, note) in enumerate(rows):
        y = 2 - k
        sh = S[key][0]
        c = float(sh["China"])
        ax.barh(y, 100, height=H, color=SAND, zorder=2)
        ax.barh(y, c, height=H, color=CORAL, zorder=3)
        left = c
        for country, col in nexts:
            if col is None:
                continue
            w = float(sh[country])
            ax.barh(y, w, left=left, height=H, color=col, zorder=3)
            left += w
        ax.text(c - 1.2, y, f"{r(sh['China'], '1')}%", ha="right", va="center", fontsize=30, fontweight="bold",
                color=CREAM, zorder=5)
        if key == "antimony":
            for country, col in nexts:
                w = float(sh[country]); x0 = c + sum(float(sh[cc]) for cc, _ in nexts[:[cc for cc, _ in nexts].index(country)])
                ax.text(x0 + w / 2, y, f"{country}\n{r(sh[country], '1')}%", ha="center", va="center", fontsize=12.5,
                        fontweight="bold", color=CREAM if col == TEAL else INK, linespacing=1.2, zorder=5)
        vals = {cc: r(v, "1") for cc, v in sh.items()}
        ax.text(0, y - H / 2 - 0.08, note.format(**vals), ha="left", va="top", fontsize=12, color=MUTED)
        fig.text(0.185, 0.17 + 0.62 * ((y + 0.5) / 3) + 0.035, title, ha="right", va="center", fontsize=21,
                 fontweight="bold", color=INK)
        fig.text(0.185, 0.17 + 0.62 * ((y + 0.5) / 3) - 0.012, kind, ha="right", va="center", fontsize=13.5,
                 color=MUTED)
        fig.text(0.185, 0.17 + 0.62 * ((y + 0.5) / 3) - 0.050, use, ha="right", va="center", fontsize=11.5,
                 color=TEAL, style="italic")
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.75, 2.5)
    ax.axis("off")

    fig.text(0.035, 0.955, "China's Grip on Key Minerals", fontsize=26, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.897, "China's share of world production in 2025, with the next largest producers",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.62, 0.897, "■ China", fontsize=13.5, color=CORAL, ha="left", va="top", fontweight="bold")
    fig.text(0.70, 0.897, "■ Next largest", fontsize=13.5, color=TEAL, ha="left", va="top", fontweight="bold")
    fig.text(0.825, 0.897, "■ Rest of world", fontsize=13.5, color="#b8a98a", ha="left", va="top", fontweight="bold")
    fig.text(0.035, 0.022,
             "Shares are China's tonnage over the sum of USGS's 2025 country estimates (USGS's text puts graphite at 82%). "
             "China's ban on U.S.-bound gallium, germanium\nand antimony stays suspended through Jan. 27, 2027. "
             "Source: U.S. Geological Survey, Mineral Commodity Summaries 2026.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.45)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"china-minerals-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    print("wrote", out)
