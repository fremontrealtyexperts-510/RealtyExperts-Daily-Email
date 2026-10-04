#!/usr/bin/env python3
"""
make-hoa-dues-charts.py  TODAY_CSV  YEAR_AGO_CSV  [outdir]

The 10/04/26 Sunday daily's two HOA charts (Real Estate section). Market Briefs
("Worth the squeeze", hello@grow.briefs.co) led with HOA fees; Harv asked for our
own bar and pie charts on LOCAL dues, last year vs now, useful to agents, buyers
and sellers. Built from our own dated MLS exports, never a vendor chart:

  hoa-dues-100426.png / -hb.png   median dues by city and type, the U.S. median for
                                  scale, and the borrowing power dues cost at 7.57%
  hoa-mix-100426.png  / -hb.png   condo dues bands, October 7, 2025 vs today (donuts)

TODAY_CSV     /tmp/mls-today.csv from dump-mls-csv.js (MLS_Defined_Spread_Sheet_4 - 100426)
YEAR_AGO_CSV  the earliest saved export, MLS_Defined_Spread_Sheet_4-100725-1215pm, pulled
              with a scratchpad copy of dump-mls-csv.js (reference-mls-export-archive-on-drive)
Listing level CSVs are NEVER committed (public repo); this script reads them and
draws aggregates only, and asserts every printed figure.

=============================================================================
BASIS AND VERIFICATION 10/04/26
=============================================================================
Every listing in the export (active, new, back on market, price change, coming
soon and in contract). Dues are the "HOA Fee" column with Freq "M" (monthly); the
few A/Q/S rows are converted only for the all-homes figure, and blank-frequency
rows are left out because their basis is unknown.

Condo medians today (n): Fremont $611.50 -> shown $612 (86), Hayward $558 (55),
Newark $555 (25), Milpitas $505 (38), Union City $395 (15); five cities $550 (219).
Townhomes five cities $380 (114). Detached homes with an HOA: 137 of 544, median
$161 (160.5 rounded half up). All homes with dues, five cities: $395 (466 with a known frequency).
U.S. median for 2025, all listings with nonzero dues: $135 (Realtor.com,
"Homeowners Associations Continue to Grow in Prevalence, Price in 2025",
Joel Berner, January 27, 2026; its methodology counts only nonzero dues, the same
basis as ours).

Year ago, Fremont, Hayward, Newark and Union City only (Milpitas joined the export
in January 2026): condos n=167, median $549, bands 11/62/66/28 (under $300,
$300 to $499, $500 to $699, $700+); today n=181, median $560, bands 11/49/84/37.
Share at $500 or more: 56.3% -> 66.9%.

Borrowing power: 30-year fixed at Mortgage News Daily's 7.57% (10/02/26 reading),
payment factor 0.00704014 per dollar: $200 -> $28,409, $400 -> $56,817,
$550 -> $78,123, $700 -> $99,430, shown to the nearest $100.

matplotlib only; build with python3.13 on Mac.
"""
import csv
import os
import statistics as st
import sys
from decimal import Decimal, ROUND_HALF_UP, getcontext

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

TODAY_CSV, YEAR_CSV = sys.argv[1], sys.argv[2]
OUTDIR = sys.argv[3] if len(sys.argv) > 3 else "."
STAMP = "100426"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
BLUE = "#2f6f9f"
GOLD = "#b7862a"
SLATE = "#6f8296"
PALE = "#a7b3c0"
GRID = "#d8cdb8"
MUTED = "#8a8172"
RAMP = ["#d6e4f0", "#9dbfdc", "#4f87b6", "#1f4e79"]     # ordered bands: one hue, light to dark

FIVE = ["FREMONT", "HAYWARD", "NEWARK", "MILPITAS", "UNION CITY"]
FOUR = ["FREMONT", "HAYWARD", "NEWARK", "UNION CITY"]
BANDS = [(0, 300, r"Under \$300"), (300, 500, r"\$300 to \$499"),
         (500, 700, r"\$500 to \$699"), (700, 10 ** 9, r"\$700 or more")]
RATE = Decimal("7.57")
NOTICE = ("Based on information from the Bay East Association of REALTORS® (Bay East MLS) "
          "as of {asof}; not verified by broker or MLS.")


def load(path):
    rows = list(csv.reader(open(path, encoding="utf-8")))
    hi = next(i for i, r in enumerate(rows) if "Status" in r and "City" in r)
    h = rows[hi]
    # rows drop trailing empty cells (HOA Fee, Freq): pad before zip
    return [dict(zip(h, [c.strip() for c in r] + [""] * (len(h) - len(r)))) for r in rows[hi + 1:]]


def num(x):
    try:
        return float(str(x).replace(",", "").replace("$", ""))
    except ValueError:
        return None


def monthly_m(d):
    f = num(d["HOA Fee"])
    return f if d["Freq"] == "M" and f and f > 0 else None


def monthly_any(d):
    f = num(d["HOA Fee"])
    if not f or f <= 0:
        return None
    return {"M": f, "A": f / 12, "Q": f / 3, "S": f / 6}.get(d["Freq"])


def med(xs):
    return Decimal(str(st.median(xs))).quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def fees(D, bts, cities):
    return [monthly_m(d) for d in D if d["BT"] in bts and d["City"] in cities and monthly_m(d)]


def band_counts(xs):
    return [sum(1 for x in xs if lo <= x < hi) for lo, hi, _ in BANDS]


def largest_remainder(counts):
    n = sum(counts)
    raw = [Decimal(c) * 100 / n for c in counts]
    fl = [int(r) for r in raw]
    order = sorted(range(len(raw)), key=lambda i: raw[i] - fl[i], reverse=True)
    for i in order[: 100 - sum(fl)]:
        fl[i] += 1
    return fl


def loan_for(payment):
    getcontext().prec = 40
    r = RATE / 100 / 12
    factor = r / (1 - (1 + r) ** -360)
    return int((Decimal(payment) / factor / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * 100)


def stats():
    T, Y = load(TODAY_CSV), load(YEAR_CSV)
    city = {c: fees(T, {"CO"}, {c}) for c in FIVE}
    cmed = {c: med(v) for c, v in city.items()}
    assert {c: (int(cmed[c]), len(city[c])) for c in FIVE} == {
        "FREMONT": (612, 86), "HAYWARD": (558, 55), "NEWARK": (555, 25),
        "MILPITAS": (505, 38), "UNION CITY": (395, 15)}, cmed
    co5, th5 = fees(T, {"CO"}, set(FIVE)), fees(T, {"TH"}, set(FIVE))
    assert (int(med(co5)), len(co5), int(med(th5)), len(th5)) == (550, 219, 380, 114)
    de = [d for d in T if d["BT"] == "DE" and d["City"] in FIVE]
    de_dues = [monthly_any(d) for d in de if monthly_any(d)]
    de_with = sum(1 for d in de if (num(d["HOA Fee"]) or 0) > 0)
    assert (de_with, len(de), int(med(de_dues))) == (137, 544, 161)   # 160.5, half up
    allh = [monthly_any(d) for d in T if d["City"] in FIVE and monthly_any(d)]
    assert (int(med(allh)), len(allh)) == (395, 466)

    y4, t4 = fees(Y, {"CO"}, set(FOUR)), fees(T, {"CO"}, set(FOUR))
    yb, tb = band_counts(y4), band_counts(t4)
    assert (len(y4), int(med(y4)), yb) == (167, 549, [11, 62, 66, 28]), (len(y4), med(y4), yb)
    assert (len(t4), int(med(t4)), tb) == (181, 560, [11, 49, 84, 37]), (len(t4), med(t4), tb)
    return dict(cmed=cmed, n=len(co5), co5=int(med(co5)), th5=int(med(th5)), de=int(med(de_dues)),
                allh=int(med(allh)), y4=(len(y4), int(med(y4)), yb), t4=(len(t4), int(med(t4)), tb))


def money(v):
    return r"\$" + f"{v:,}"


def dues_chart(s):
    fig = plt.figure(figsize=(14.0, 8.4), dpi=100)
    fig.patch.set_facecolor(CREAM)

    # ---- left: median monthly dues -------------------------------------------
    ax = fig.add_axes([0.255, 0.19, 0.30, 0.575])
    ax.set_facecolor(CREAM)
    rows = [("Condos", None, None, None)]
    for c in ["FREMONT", "HAYWARD", "NEWARK", "MILPITAS", "UNION CITY"]:
        rows.append((c.title(), int(s["cmed"][c]), BLUE, False))
    rows += [("All five cities", None, None, None),
             ("Townhomes", s["th5"], GOLD, False),
             ("Single family homes with an HOA", s["de"], SLATE, False),
             ("All homes with dues", s["allh"], CORAL, True),
             ("United States, 2025", None, None, None),
             ("All homes with dues", 135, PALE, True)]
    y = 0.0
    for name, v, col, bold in rows:
        if v is None:                       # group header
            y += 0.35 if y else 0
            ax.text(-292, y, name, ha="left", va="center", fontsize=12.5, fontweight="bold", color=MUTED)
            y += 0.95
            continue
        ax.barh(y, v, height=0.68, color=col, zorder=3)
        ax.text(v + 10, y, money(v), ha="left", va="center", fontsize=13,
                fontweight="bold", color=DEEP if col == CORAL else INK, zorder=5)
        ax.text(-14, y, name, ha="right", va="center", fontsize=12.2,
                fontweight="bold" if bold else "normal", color=INK)
        y += 1.0
    ax.axvline(0, color=INK, lw=1.0, zorder=4)
    ax.set_xlim(0, 760)
    ax.set_ylim(y - 0.3, -0.7)
    ax.axis("off")
    fig.text(0.035, 0.80, "Median monthly HOA dues", fontsize=13.2, fontweight="bold",
             color=INK, ha="left", va="bottom")
    fig.text(0.035, 0.785, "Homes listed today, by city and home type", fontsize=11.5,
             color=MUTED, ha="left", va="top")

    # ---- right: borrowing power -------------------------------------------------
    bx = fig.add_axes([0.765, 0.265, 0.20, 0.42])
    bx.set_facecolor(CREAM)
    pay = [200, 400, s["co5"], 700]
    loans = [loan_for(p) for p in pay]
    assert loans == [28400, 56800, 78100, 99400], loans
    for i, (p, l) in enumerate(zip(pay, loans)):
        hot = p == s["co5"]
        bx.barh(i, l, height=0.62, color=CORAL if hot else SLATE, zorder=3)
        bx.text(l + 1500, i, money(l), ha="left", va="center", fontsize=13, fontweight="bold",
                color=DEEP if hot else INK, zorder=5)
        lab = money(p) + " a month" + ("\nthe median condo" if hot else "")
        bx.text(-3000, i, lab, ha="right", va="center", fontsize=12, linespacing=1.25,
                fontweight="bold" if hot else "normal", color=DEEP if hot else INK)
    bx.axvline(0, color=INK, lw=1.0, zorder=4)
    bx.set_xlim(0, 128000)
    bx.set_ylim(len(pay) - 0.4, -0.6)
    bx.axis("off")
    fig.text(0.615, 0.80, "What dues cost in borrowing power", fontsize=13.2, fontweight="bold",
             color=INK, ha="left", va="bottom")
    fig.text(0.615, 0.785, "Loan the same monthly money would carry at 7.57%", fontsize=11.5,
             color=MUTED, ha="left", va="top")

    fig.text(0.035, 0.955, "HOA Dues Here Run Nearly Three Times the U.S. Median",
             fontsize=24, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.905, "Fremont, Hayward, Milpitas, Newark and Union City, October 4, 2026",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.100,
             "Borrowing power: 30-year fixed at Mortgage News Daily's 7.57%, principal and interest. "
             "Newark and Union City condo medians rest on fewer than 30 listings.",
             fontsize=10.6, color=DEEP, ha="left", va="bottom")
    fig.text(0.035, 0.062,
             "Sources: our MLS export of October 4, 2026; U.S. median for 2025 from Realtor.com, "
             "published January 27, 2026.",
             fontsize=9.6, color=MUTED, ha="left", va="bottom")
    fig.text(0.035, 0.030, NOTICE.format(asof="October 4, 2026"),
             fontsize=9.6, color=MUTED, ha="left", va="bottom")
    return fig


def mix_chart(s):
    fig = plt.figure(figsize=(14.0, 8.0), dpi=100)
    fig.patch.set_facecolor(CREAM)
    panels = [("October 7, 2025", s["y4"], 0.06), ("October 4, 2026", s["t4"], 0.53)]
    shares = []
    for title, (n, m, counts), x0 in panels:
        ax = fig.add_axes([x0, 0.215, 0.40, 0.57])
        ax.set_facecolor(CREAM)
        pct = largest_remainder(counts)
        hi = pct[2] + pct[3]
        shares.append(hi)
        wedges, _ = ax.pie(counts, colors=RAMP, startangle=90, counterclock=False,
                           wedgeprops=dict(width=0.36, edgecolor=CREAM, linewidth=2.5))
        for w, p in zip(wedges, pct):
            ang = (w.theta2 + w.theta1) / 2.0
            import math
            r = 1.17
            xx, yy = r * math.cos(math.radians(ang)), r * math.sin(math.radians(ang))
            ax.text(xx, yy, f"{p}%", ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
        ax.text(0, 0.10, f"{hi}%", ha="center", va="center", fontsize=34, fontweight="bold", color=BLUE)
        ax.text(0, -0.22, r"at \$500 or more", ha="center", va="center", fontsize=12.5, color=INK)
        ax.set_aspect("equal")
        ax.set_xlim(-1.45, 1.45)
        ax.set_ylim(-1.38, 1.38)
        ax.text(0, 1.47, title, ha="center", va="bottom", fontsize=15, fontweight="bold", color=INK)
        ax.text(0, -1.47, f"{n} condos listed, median {money(m)} a month", ha="center", va="top",
                fontsize=12, color=MUTED)
    assert shares == [56, 67], shares
    fig.legend([Patch(facecolor=c, edgecolor="none") for c in RAMP], [b[2] for b in BANDS],
               loc="lower center", bbox_to_anchor=(0.5, 0.105), ncol=4, frameon=False,
               fontsize=12, handlelength=1.6, columnspacing=2.4, labelcolor=INK)
    fig.text(0.035, 0.955, r"Two in Three Condos Now Carry Dues of \$500 or More",
             fontsize=24, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.905, "Condos listed in Fremont, Hayward, Newark and Union City, by monthly HOA dues",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.062,
             "Sources: our MLS exports of October 7, 2025 and October 4, 2026. Milpitas joined the export in "
             "January 2026, so it is left out.",
             fontsize=9.6, color=MUTED, ha="left", va="bottom")
    fig.text(0.035, 0.030, NOTICE.format(asof="October 7, 2025 and October 4, 2026"),
             fontsize=9.6, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    s = stats()
    print({k: (v if k != "cmed" else {c: int(x) for c, x in v.items()}) for k, v in s.items()})
    for name, build in (("hoa-dues", dues_chart), ("hoa-mix", mix_chart)):
        fig = build(s)
        save_pair(fig, os.path.join(OUTDIR, f"{name}-{STAMP}.png"), facecolor=CREAM)
        plt.close(fig)
