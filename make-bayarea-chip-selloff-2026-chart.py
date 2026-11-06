"""
make-bayarea-chip-selloff-2026-chart.py  DATA_DIR  [outdir]

The 11/06/26 daily's Stocks chart. Harv: "Mainly, it's just a stock, what
happened. It was heavily in red." Thursday, November 5, 2026 was the worst day
for the S&P 500 and Nasdaq since April 2025 and the worst for the Philadelphia
semiconductor index since March 16, 2020, led by AI chip and data center
stocks. Kept local: ten chip and hardware companies headquartered in the Bay
Area (city from each company's SEC EDGAR business address), with the four
benchmarks underneath for scale.

Emits BOTH:
  bayarea-chip-selloff-110626.png      plain HB monogram    -> RE email + Agent Hub
  bayarea-chip-selloff-110626-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds the Nasdaq.com historical API responses
(api.nasdaq.com/api/quote/<T>/historical?assetclass=stocks|index) for the ten
tickers plus SOX and COMP, and spx_dji.json for the S&P 500 and Dow (Nasdaq's
API does not carry them).

=============================================================================
VERIFICATION 11/06/26
=============================================================================
* Every Wednesday and Thursday close matched across Nasdaq.com, Yahoo daily
  bars and CNBC's previous close (Thursday). Index moves match the AP wrap:
  S&P 500 down 334.89 to 7,353.73, Dow down 1,833.06 to 51,523.06, Nasdaq down
  1,421.52 to 24,315.00 (asserted below).
* "Worst since": computed from Yahoo daily closes. S&P 500 -4.36% and Nasdaq
  -5.52% are the worst since April 3-4, 2025; SOX -12.25% is the worst since
  -15.90% on March 16, 2020.
* HQ cities (EDGAR submissions JSON, business address): Lam Research 4650
  Cushing Blvd FREMONT; KLA One Technology Dr MILPITAS; Sandisk 951 SanDisk Dr
  MILPITAS; Western Digital 5601 Great Oaks Pkwy SAN JOSE; Super Micro 980 Rock
  Ave SAN JOSE; Nvidia, AMD, Intel, Applied Materials SANTA CLARA; Broadcom
  3421 Hillview Ave PALO ALTO.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
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
STAMP = "110626"
WED, THU = "11/04/2026", "11/05/2026"

CREAM = "#fdf6e8"
INK = "#1f2933"
RED = "#d1495b"
CORAL = "#ea580c"   # orange, the Real Estate accent: our own market
SLATE = "#7c8b99"
GRID = "#e6dcc8"
MUTED = "#8a8172"
AXIS = "#8a7f6a"

COMPANIES = [("SNDK", "Sandisk", "Milpitas"), ("WDC", "Western Digital", "San Jose"),
             ("AMD", "AMD", "Santa Clara"), ("LRCX", "Lam Research", "Fremont"),
             ("AMAT", "Applied Materials", "Santa Clara"), ("KLAC", "KLA", "Milpitas"),
             ("AVGO", "Broadcom", "Palo Alto"), ("INTC", "Intel", "Santa Clara"),
             ("NVDA", "Nvidia", "Santa Clara"), ("SMCI", "Super Micro", "San Jose")]
BENCH = [("SOX", "Philadelphia Semiconductor Index"), ("COMP", "Nasdaq Composite"),
         ("SPX", "S&P 500"), ("DJI", "Dow Jones Industrial Average")]
TRI_CITY = {"Fremont", "Milpitas"}          # our own market, drawn in coral

# printed precision, asserted against the copy
EXPECT = {"SNDK": "-22.3", "WDC": "-17.4", "AMD": "-17.3", "LRCX": "-16.4", "AMAT": "-13.6", "KLAC": "-13.3",
          "AVGO": "-10.4", "INTC": "-10.3", "NVDA": "-9.3", "SMCI": "-8.5",
          "SOX": "-12.2", "COMP": "-5.5", "SPX": "-4.4", "DJI": "-3.4"}


def nasdaq_closes(t):
    d = json.load(open(os.path.join(DATA, f"{t}.json")))
    rows = {r["date"]: Decimal(r["close"].replace("$", "").replace(",", "")) for r in d["data"]["tradesTable"]["rows"]}
    return rows[WED], rows[THU]


def pct(a, b):
    return (b / a - 1) * 100


def one(x):
    return x.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def load():
    out = {}
    for t, *_ in COMPANIES:
        out[t] = nasdaq_closes(t)
    for t in ("SOX", "COMP"):
        out[t] = nasdaq_closes(t)
    sd = json.load(open(os.path.join(DATA, "spx_dji.json")))
    for t in ("SPX", "DJI"):
        out[t] = (Decimal(sd[t][WED]), Decimal(sd[t][THU]))
    # AP wrap point changes
    assert out["SPX"][0] - out["SPX"][1] == Decimal("334.89"), out["SPX"]
    assert out["DJI"][0] - out["DJI"][1] == Decimal("1833.06"), out["DJI"]
    assert out["COMP"][0] - out["COMP"][1] == Decimal("1421.51"), out["COMP"]   # AP printed 1,421.52 from unrounded closes
    ch = {t: pct(*v) for t, v in out.items()}
    for t, e in EXPECT.items():
        assert str(one(ch[t])) == e, (t, ch[t], e)
    # ranked steepest first, as drawn
    vals = [ch[t] for t, *_ in COMPANIES]
    assert vals == sorted(vals), vals
    return ch


def build():
    ch = load()
    fig = plt.figure(figsize=(14.0, 10.4), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.335, 0.085, 0.60, 0.735])
    ax.set_facecolor(CREAM)

    rows = []
    for t, name, city in COMPANIES:
        rows.append((t, name, city, CORAL if city in TRI_CITY else RED, True))
    rows.append(None)                                   # gap
    for t, name in BENCH:
        rows.append((t, name, None, SLATE, False))

    n = len(rows)
    for i, r in enumerate(rows):
        y = n - 1 - i
        if r is None:
            continue
        t, name, city, color, bold = r
        v = float(ch[t])
        ax.barh(y, v, height=0.66, color=color, zorder=3)
        ax.text(v - 0.35, y, f"−{abs(one(ch[t]))}%", va="center", ha="right", fontsize=13.5,
                fontweight="bold", color=color if color != SLATE else "#5b6875")
        label_y = 0.085 + 0.735 * (y + 0.6) / (n + 0.2)
        if city:
            fig.text(0.318, label_y + 0.0095, name, fontsize=13.5, fontweight="bold", color=INK, ha="right",
                     va="center")
            fig.text(0.318, label_y - 0.0115, city, fontsize=11, color=CORAL if city in TRI_CITY else MUTED,
                     ha="right", va="center", fontweight="bold" if city in TRI_CITY else "normal")
        else:
            fig.text(0.318, label_y, name, fontsize=12.5, color="#5b6875", ha="right", va="center")
    ax.axvline(0, color=AXIS, lw=1.4, zorder=4)
    for x in (-5, -10, -15, -20):
        ax.axvline(x, color=GRID, lw=1, zorder=1)
        ax.text(x, -0.95, f"−{abs(x)}%", ha="center", va="top", fontsize=10.5, color=MUTED)
    ax.set_xlim(-26.5, 0.6)
    ax.set_ylim(-0.6, n - 0.4)
    ax.axis("off")

    gap_y = 0.085 + 0.735 * (n - 1 - len(COMPANIES) + 0.6) / (n + 0.2)
    fig.text(0.318, gap_y, "BENCHMARKS", fontsize=10.5, color=MUTED, ha="right", va="center", fontweight="bold")

    fig.text(0.035, 0.962, "Thursday's Chip Rout Hit Close to Home", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.912, "Stock price change on Thursday, November 5, 2026, Bay Area chip and hardware companies "
             "by headquarters city", fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.881, "Worst day for the S&P 500 and Nasdaq since April 2025; worst for the chip index "
             "since March 2020", fontsize=13.5, color=INK, ha="left", va="top")
    fig.text(0.035, 0.022, "Orange: headquartered in Fremont and Milpitas. Source: Nasdaq.com closing prices, "
             "November 4 and 5, 2026; headquarters from each company's SEC filings.", fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"bayarea-chip-selloff-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
