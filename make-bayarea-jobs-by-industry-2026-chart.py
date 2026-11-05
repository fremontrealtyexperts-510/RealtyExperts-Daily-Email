"""
make-bayarea-jobs-by-industry-2026-chart.py  DATA_DIR  [outdir]

The 11/05/26 daily's Economy chart. Harv supplied a newsletter graphic of ADP's
October private payrolls by industry ("Where October's 86,000 Jobs Came From").
NOT recreated: ADP's data license (license.txt inside ADP_NER_history.zip)
says "No commercial reproduction, use or re-use of any kind may be made of the
Information without the prior written consent of ADP". Same handling as ISM and
S&P Global PMIs: ADP's headline numbers go in the copy with attribution, and
the story is charted from public BLS data, kept local.

Emits BOTH:
  bayarea-jobs-by-industry-110526.png      plain HB monogram    -> RE email + Agent Hub
  bayarea-jobs-by-industry-110526-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR/metro.json is the BLS public API v1 response (POST, startyear 2025,
endyear 2026) for State and Metro Area CES, not seasonally adjusted, thousands:
  SMU06 36084 <industry> 01  Oakland-Fremont-Berkeley division (Alameda + Contra Costa)
  SMU06 41940 <industry> 01  San Jose-Sunnyvale-Santa Clara metro (Santa Clara + San Benito)
industries 05000000 total private, 15000000 mining logging construction,
30000000 ... 80000000 the private supersectors.

=============================================================================
VERIFICATION 11/05/26
=============================================================================
* Change is Sept 2025 to Sept 2026 because the series are NOT seasonally
  adjusted; a month to month change would be mostly seasonal. Sept 2026 is
  preliminary (BLS footnote P).
* The nine supersector changes sum EXACTLY to each area's total private change,
  asserted in Decimal: East Bay -5.7K, San Jose +19.9K.
* Fremont, Hayward, Newark and Union City are in the Oakland-Fremont-Berkeley
  division; Milpitas is in the San Jose metro.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import json
import os
import sys
from decimal import Decimal

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "110526"

CREAM = "#fdf6e8"
INK = "#1f2933"
GREEN = "#2e8b57"
RED = "#d1495b"
GRID = "#d8cdb8"
MUTED = "#8a8172"
AXIS = "#8a7f6a"

AREAS = [("36084", "East Bay", "Oakland-Fremont-Berkeley (Alameda + Contra Costa)", "Fremont, Hayward, Newark, Union City"),
         ("41940", "South Bay", "San Jose metro (Santa Clara + San Benito)", "Milpitas")]
IND = [("65000000", "Education & health"), ("70000000", "Leisure & hospitality"),
       ("40000000", "Trade, transport & utilities"), ("80000000", "Other services"),
       ("15000000", "Construction & mining"), ("60000000", "Professional & business"),
       ("55000000", "Financial activities"), ("30000000", "Manufacturing"), ("50000000", "Information")]


def load():
    d = json.load(open(os.path.join(DATA, "metro.json")))
    assert d["status"] == "REQUEST_SUCCEEDED"
    ser = {}
    for s in d["Results"]["series"]:
        rows = {(x["year"], x["period"]): x for x in s["data"]}
        a, b = rows[("2025", "M09")], rows[("2026", "M09")]
        assert any(f.get("code") == "P" for f in b["footnotes"] if f), s["seriesID"]   # preliminary, say so
        ser[s["seriesID"]] = Decimal(b["value"]) - Decimal(a["value"])
    out = {}
    for code, *_ in AREAS:
        ch = [ser["SMU06%s%s01" % (code, i)] for i, _ in IND]
        tot = ser["SMU06%s0500000001" % code]
        assert sum(ch) == tot, (code, sum(ch), tot)
        out[code] = (ch, tot)
    assert out["36084"][1] == Decimal("-5.7") and out["41940"][1] == Decimal("19.9"), out
    assert out["41940"][0][0] == Decimal("11.1") and out["36084"][0][0] == Decimal("5.1")   # health leads both
    return out


def jobs(k):
    v = int(k * 1000)
    return ("+" if v > 0 else "−" if v < 0 else "") + f"{abs(v):,}"


def build():
    data = load()
    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    n = len(IND)
    lim = 13.5
    for j, (code, short, long_, towns) in enumerate(AREAS):
        ch, tot = data[code]
        left = 0.255 + j * 0.375
        ax = fig.add_axes([left, 0.13, 0.33, 0.60])
        ax.set_facecolor(CREAM)
        for i, v in enumerate(ch):
            y = n - 1 - i
            fv = float(v)
            ax.barh(y, fv, height=0.64, color=GREEN if fv > 0 else RED, zorder=3)
            if fv >= 0:
                ax.text(fv + 0.35, y, jobs(v), va="center", ha="left", fontsize=12.5, fontweight="bold",
                        color=GREEN if fv > 0 else MUTED)
            else:
                ax.text(fv - 0.35, y, jobs(v), va="center", ha="right", fontsize=12.5, fontweight="bold", color=RED)
        ax.axvline(0, color=AXIS, lw=1.4, zorder=4)
        ax.set_xlim(-lim + 4.5, lim)
        ax.set_ylim(-0.6, n - 0.4)
        ax.axis("off")
        fig.text(left, 0.825, short, fontsize=17, fontweight="bold", color=INK, ha="left", va="bottom")
        fig.text(left, 0.800, long_, fontsize=10.8, color=MUTED, ha="left", va="bottom")
        fig.text(left, 0.765, f"Total private jobs {jobs(tot)}", fontsize=13.5, fontweight="bold",
                 color=GREEN if tot > 0 else RED, ha="left", va="bottom")
        fig.text(left, 0.742, f"includes {towns}", fontsize=10.5, color=MUTED, ha="left", va="bottom", style="italic")
        if j == 0:
            for i, (_, name) in enumerate(IND):
                y = n - 1 - i
                yy = 0.13 + 0.60 * (y + 0.6) / (n + 0.2)      # ylim spans n + 0.2
                fig.text(0.235, yy, name, fontsize=13, color=INK, ha="right", va="center")

    fig.text(0.035, 0.955, "Where the Bay Area's Private Jobs Came From", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.897, "Change in private sector jobs by industry, September 2025 to September 2026",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.03, "Source: U.S. Bureau of Labor Statistics, Current Employment Statistics, State and Metro Area, "
             "not seasonally adjusted; September 2026 is preliminary.", fontsize=10.2, color=MUTED, ha="left",
             va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"bayarea-jobs-by-industry-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
