"""
make-markets-week-2026-chart.py  WK_DIR  MLS_110626_CSV  MLS_111326_CSV  INVENTORY_HISTORY_JSON  [outdir]

The 11/15/26 Sunday daily's Stocks chart. Harv supplied Market Briefs' "Markets This
Week" scoreboard (Nov. 9 to 13, 2026, Friday close, weekly change) and asked for it to be
checked and regenerated where wrong. Rebuilt as OUR scoreboard from primary sources, with
the three wrong tiles corrected and a fourth row added for our own MLS board (keep it local).

Emits BOTH:
  markets-week-111526.png      plain HB monogram    -> RE email + Agent Hub
  markets-week-111526-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

WK_DIR holds the raw pulls (scratchpad wk/):
  yh-GSPC.json yh-DJI.json yh-IXIC.json yh-GCF.json yh-BZF.json   Yahoo chart API, interval=1d
  cnbc.json (@GC.1 @SI.1 @LCO.1)  cnbc-idx.json (.SPX .DJI .IXIC)   CNBC restQuote, Sunday = Friday's settle/close
  tsy-202611.csv   home.treasury.gov daily yield curve, November 2026
  mnd.html         mortgagenewsdaily.com/mortgage-rates/mnd (daily index table)
  btc10.json       CoinGecko bitcoin market_chart days=10 (hourly)
The two MLS CSVs are the Drive archive exports "MLS_Defined_Spread_Sheet_4 - 110626" and
"... -111326" (inputs only; nothing listing level is drawn or stored).

=============================================================================
VERIFICATION 11/15/26 (Friday Nov. 13 vs Friday Nov. 6)
=============================================================================
Matched the supplied graphic: S&P 500 7,561.67 (+2.51%), Dow 52,347.55 (+2.07%), Nasdaq
25,136.27 (+2.27%), Brent $95.84 (-2.52%, ICE January both Fridays, no roll), 10-Year 5.15%
(+0.29). Index closes identical on Yahoo and CNBC; the Nov. 6 bases equal what our own
Nov. 7 report printed.
CORRECTED:
* Gold: graphic $3,884 (-4.58%). COMEX December settlement $3,886.30 vs $4,074.90 = -4.63%.
* 30-year mortgage: graphic 7.11% (-0.07) is Freddie Mac's weekly survey (Nov. 12). The
  report's rate source, Mortgage News Daily, closed Friday at 7.50%, up 0.33 from 7.17%.
* Bitcoin: graphic $69,556 (-8.41%) matches Friday morning, not a close. At 4 PM ET (the
  stock close) CoinGecko had $68,823.10 vs $75,800.57 a week earlier = -9.21%; Coinbase's
  4 PM ET hourly opens agree within 0.05%.
LOCAL ROW (our MLS board, Friday to Friday): board wide listings 2,464 -> 2,419; in contract
631 -> 622; five city ledger 628 -> 623 (inventory-history.json); Fremont median on market
list price $1,299,000 -> $1,279,000 (generate-live-inventory.js method, equal to both days'
published copy).

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import csv
import json
import os
import re
import sys
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

WK, M06, M13, HIST = sys.argv[1:5]
OUTDIR = sys.argv[5] if len(sys.argv) > 5 else "."
STAMP = "111526"
ET = ZoneInfo("America/New_York")
D0, D1 = "2026-11-06", "2026-11-13"

CREAM = "#fdf6e8"
CARD = "#f6ecd6"
LOCAL = "#efe3c8"
INK = "#1f2933"
MUTED = "#8a8172"
GREEN = "#2f7d4f"
RED = "#c8102e"
GOLD = "#a8792a"


def q2(x):
    return Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def yahoo(name):
    r = json.load(open(os.path.join(WK, name)))["chart"]["result"][0]
    out = {}
    for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]):
        if c is not None:
            out[datetime.fromtimestamp(t, ET).strftime("%Y-%m-%d")] = q2(str(c))
    return out[D0], out[D1]


def cnbc(name):
    return {q["symbol"]: q for q in json.load(open(os.path.join(WK, name)))["FormattedQuoteResult"]["FormattedQuote"]}


def pct(a, b):
    return ((Decimal(b) / Decimal(a) - 1) * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def load_markets():
    idx = cnbc("cnbc-idx.json")
    tiles = []
    for name, f, sym, prior in (("S&P 500", "yh-GSPC.json", ".SPX", "7376.86"),
                                ("Dow", "yh-DJI.json", ".DJI", "51285.73"),
                                ("Nasdaq", "yh-IXIC.json", ".IXIC", "24579.43")):
        a, b = yahoo(f)
        assert a == Decimal(prior), (name, a)                      # = our Nov. 7 report
        assert q2(idx[sym]["last"].replace(",", "")) == b, (name, idx[sym]["last"], b)   # Yahoo = CNBC
        tiles.append((name, "{:,.2f}".format(b), pct(a, b), "pct"))
    assert [t[2] for t in tiles] == [Decimal("2.51"), Decimal("2.07"), Decimal("2.27")], tiles

    met = cnbc("cnbc.json")
    g0, g1 = yahoo("yh-GCF.json")
    assert met["@GC.1"]["settleDate"] == D1 and Decimal(met["@GC.1"]["settlePrice"]) == g1 == Decimal("3886.30")
    assert g0 == Decimal("4074.90")                                # = our Nov. 7 report (COMEX Dec settle)
    gold = ("Gold (COMEX)", "${:,.2f}".format(g1), pct(g0, g1), "pct")
    assert gold[2] == Decimal("-4.63"), gold

    b0, b1 = yahoo("yh-BZF.json")
    assert "Jan'27" in met["@LCO.1"]["name"] and Decimal(met["@LCO.1"]["settlePrice"]) == b1 == Decimal("95.84")
    assert b0 == Decimal("98.32")                                  # = our Nov. 7 report
    brent = ("Brent crude", "${:,.2f}".format(b1), pct(b0, b1), "pct")
    assert brent[2] == Decimal("-2.52"), brent

    rows = list(csv.reader(open(os.path.join(WK, "tsy-202611.csv"))))
    i10 = [h.strip('"') for h in rows[0]].index("10 Yr")
    tsy = {r[0]: Decimal(r[i10]) for r in rows[1:]}
    t0, t1 = tsy["11/06/2026"], tsy["11/13/2026"]
    assert (t0, t1) == (Decimal("4.86"), Decimal("5.15"))
    ten = ("10-Year Treasury", "{}%".format(t1), t1 - t0, "pts")

    m = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", open(os.path.join(WK, "mnd.html"), encoding="utf-8",
                                                          errors="ignore").read()))
    mnd = dict(re.findall(r"(\d{1,2}/\d{1,2}/\d{4})\s+([\d.]+)%", m))
    r0, r1 = Decimal(mnd["11/6/2026"]), Decimal(mnd["11/13/2026"])
    assert (r0, r1) == (Decimal("7.17"), Decimal("7.50"))
    mort = ("30-year mortgage (MND)", "{}%".format(r1), r1 - r0, "pts")

    px = json.load(open(os.path.join(WK, "btc10.json")))["prices"]
    def at4(day):
        tgt = datetime.fromisoformat(day + "T16:00:00").replace(tzinfo=ET).timestamp() * 1000
        p = min(px, key=lambda v: abs(v[0] - tgt))
        assert abs(p[0] - tgt) <= 5 * 60 * 1000, (day, p)        # an on-the-hour point, not a nearby one
        return Decimal(str(p[1]))
    c0, c1 = at4(D0), at4(D1)
    btc = ("Bitcoin (4 PM ET)", "${:,.0f}".format(c1.quantize(Decimal("1"), rounding=ROUND_HALF_UP)), pct(c0, c1), "pct")
    assert btc[1] == "$68,823" and btc[2] == Decimal("-9.21"), btc
    return tiles + [gold], [brent, ten, mort, btc]


def board(path):
    act, pend, frem = 0, 0, []
    for r in csv.DictReader(open(path, encoding="utf-8")):
        st = r["Status"].strip().upper()
        if st in ("ACTV", "PCH", "BOMK", "NEW"):
            act += 1
        elif st == "PEND":
            pend += 1
        # generate-live-inventory.js market median: PCH folded into ACTV, ACTV/NEW/BOMK, price gates, address
        if r["City"].strip().upper() == "FREMONT" and st in ("ACTV", "PCH", "NEW", "BOMK"):
            try:
                lp = float(str(r["LP"]).replace(",", "").replace("$", ""))
            except ValueError:
                continue
            if r["Address"].strip() and 50000 <= lp <= 20000000:
                frem.append(lp)
    s = sorted(frem)
    n = len(s)
    med = s[n // 2] if n % 2 else round((s[n // 2 - 1] + s[n // 2]) / 2)
    return act + pend, pend, int(med)


def load_local():
    b0, p0, f0 = board(M06)
    b1, p1, f1 = board(M13)
    assert (b0, p0, f0) == (2464, 631, 1299000), (b0, p0, f0)     # = Nov. 6 report copy (board, Fremont median)
    assert (b1, p1, f1) == (2419, 622, 1279000), (b1, p1, f1)     # = Nov. 13 report copy
    hist = {r["date"]: sum(c["total"] for c in r["cities"].values()) for r in json.load(open(HIST))["series"]}
    l0, l1 = hist[D0], hist[D1]
    assert (l0, l1) == (628, 623), (l0, l1)
    return [("Board wide listings", "{:,}".format(b1), b1 - b0, "count"),
            ("In contract", "{:,}".format(p1), p1 - p0, "count"),
            ("Five city live ledger", "{:,}".format(l1), l1 - l0, "count"),
            ("Fremont median list", "${:,}".format(f1), f1 - f0, "money")]


def change_text(v, kind):
    up = v > 0
    arrow = "▲" if up else ("▼" if v < 0 else "●")
    mag = abs(v)
    if kind == "pct":
        body = "{}%".format(mag)
    elif kind == "pts":
        body = "{} pts".format(mag)
    elif kind == "money":
        body = "${:,}".format(mag)
    else:
        body = "{:,}".format(mag)
    sign = "+" if up else ("−" if v < 0 else "")
    return "{} {}{}".format(arrow, sign, body), (GREEN if up else (RED if v < 0 else MUTED))


def build():
    row1, row2 = load_markets()
    row3 = load_local()
    fig = plt.figure(figsize=(14.0, 8.6), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1400)
    ax.set_ylim(860, 0)
    ax.axis("off")

    ax.text(50, 52, "Markets This Week", fontsize=30, fontweight="bold", color=INK, ha="left", va="center")
    ax.text(50, 98, "Friday close, Nov. 13, 2026, and the change from Friday, Nov. 6", fontsize=14.5, color=MUTED,
            ha="left", va="center")

    x0, w, gap = 50, 315, 13
    def tile(i, y, h, label, value, delta, kind, bg):
        x = x0 + i * (w + gap)
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=14", facecolor=bg,
                                    edgecolor="none", zorder=1))
        ax.text(x + w / 2, y + 30, label.upper(), fontsize=12.5, color=MUTED, ha="center", va="center",
                fontweight="bold")
        ax.text(x + w / 2, y + 78, value, fontsize=29 if len(value) < 11 else 26, color=INK, ha="center",
                va="center", fontweight="bold")
        txt, col = change_text(delta, kind)
        ax.text(x + w / 2, y + 126, txt, fontsize=16, color=col, ha="center", va="center", fontweight="bold")

    for i, t in enumerate(row1):
        tile(i, 130, 160, *t, CARD)
    for i, t in enumerate(row2):
        tile(i, 305, 160, *t, CARD)
    ax.plot([50, 1350], [500, 500], color="#d9c9a6", lw=1.4)
    ax.text(50, 530, "HERE: OUR 15 CITY MLS BOARD, FRIDAY TO FRIDAY", fontsize=13, color=GOLD, ha="left",
            va="center", fontweight="bold")
    for i, t in enumerate(row3):
        tile(i, 555, 160, *t, LOCAL)

    ax.text(50, 770, "Sources: index closes from Yahoo Finance, matching CNBC; COMEX December gold and ICE January "
            "Brent settlements via CNBC; U.S. Treasury daily yield curve;", fontsize=10.6, color=MUTED, ha="left",
            va="center")
    ax.text(50, 795, "Mortgage News Daily 30-year index (Freddie Mac's Nov. 12 weekly survey: 7.11%); CoinGecko "
            "bitcoin at 4 PM ET; Bay East MLS exports, Nov. 6 and Nov. 13, 2026.", fontsize=10.6, color=MUTED,
            ha="left", va="center")
    ax.text(50, 820, "Treasury and mortgage changes are in percentage points. Five city ledger: Fremont, Hayward, "
            "Milpitas, Newark and Union City.", fontsize=10.6, color=MUTED, ha="left", va="center")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"markets-week-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
