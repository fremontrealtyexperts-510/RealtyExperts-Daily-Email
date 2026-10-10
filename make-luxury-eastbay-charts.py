#!/usr/bin/env python3
"""
make-luxury-eastbay-charts.py  HIST_DIR  [outdir]

The 10/10/26 Saturday edition's luxury charts. Harv: luxury homes look like they
are booming in the Bay Area; make it the topic, illustrate it with bars and pies,
and make sure every number is correct and sourced. Built from OUR OWN saved MLS
exports (the dated MLS_Defined_Spread_Sheet_4 archive on Drive), so the counts
are on the same basis as the RE-Daily table.

  luxury-monthly-101026.png    paired bars: $2M+ homes for sale and in contract,
                               one snapshot near the 10th of each month
  luxury-where-101026.png      two donuts: where the $2M+ contracts are, a year
                               ago vs today (Tri-Valley, Tri-City, rest)
  luxury-bands-101026.png      bars: change in homes in contract by price band,
                               Oct. 9, 2025 to Oct. 10, 2026
  (each with its -hb twin via chart_brand.save_pair)

=============================================================================
SOURCE AND BASIS
=============================================================================

HIST_DIR holds one CSV per snapshot, named YYYY-MM-DD.csv, each a cell for cell
dump of that day's export (older days were .xlsx files converted with openpyxl).
The MLS data itself is never committed; only the counts below are.

* Columns are read by POSITION (Status 1, DOM 2, City 5, LP 7, BT 9). The
  10/09/25 file names its columns differently ("MLS #", "Sold Price") but the
  order is identical; asserted below.
* "In contract" = PEND + AC. "For sale" = ACTV + NEW + BOMK + PCH. Coming soon
  (CS) is excluded from every price figure (Bay East rules: coming soon homes may
  be counted, never described, and their prices are not used here).
* Price = list price (LP). The exports carry no closed sales.
* 14 cities: Milpitas joined the export in January 2026, so it is left out of
  every comparison (today it has 2 homes in contract and 7 for sale at $2M+).
* No export exists for Oct. 10, 2025; "a year ago" is Oct. 9, 2025. The Oct. 13,
  2025 file was checked as a second base and gives the same direction on every
  claim used in the copy (see the asserts).

Counts on 10/10/26 (generated from the CSVs, asserted below):
  $2M+ in contract, 14 cities: 87 (10/09/25), 89 (10/13/25), peak 120 (05/11/26),
  64 today. For sale: 191, 185, 215, 167.
  By area, in contract: Tri-Valley 60 -> 35, Tri-City 18 -> 23, rest 9 -> 6.
  Fremont 15 -> 18, Danville 23 -> 17.
  In contract by band: under $1M 453 -> 416, $1M to $1.5M 202 -> 163,
  $1.5M to $2M 126 -> 103, $2M to $3M 60 -> 49, $3M+ 27 -> 15.

matplotlib only; build with python3.13 on Mac.
"""
import csv
import glob
import math
import os
import sys
from collections import Counter
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

HIST = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "101026"

CREAM = "#fdf6e8"
INK = "#1f2933"
MUTED = "#8a8172"
GRID = "#d8cdb8"
CORAL = "#e2574c"
CORAL_D = "#b8432f"
BLUE = "#2f6f9f"
GOLD = "#b7862a"
SAND = "#e9d9b8"

SALE = {"ACTV", "NEW", "BOMK", "PCH"}
CONTRACT = {"PEND", "AC"}
TRI_VALLEY = {"DANVILLE", "PLEASANTON", "SAN RAMON", "DUBLIN", "LIVERMORE"}
TRI_CITY = {"FREMONT", "NEWARK", "UNION CITY"}
BANDS = [(0, 1_000_000, "Under\n\\$1M"), (1_000_000, 1_500_000, "\\$1M to\n\\$1.5M"),
         (1_500_000, 2_000_000, "\\$1.5M to\n\\$2M"), (2_000_000, 3_000_000, "\\$2M to\n\\$3M"),
         (3_000_000, 10 ** 12, "\\$3M\nand up")]
AP_MONTHS = ["Jan.", "Feb.", "March", "April", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."]
EXPECT_HDR = ["Status", "DOM", "Address", "Unit", "City", "Area", "LP"]


def pct(a, b):
    return Decimal(b - a) / Decimal(a) * 100


def r0(x):
    return int(Decimal(x).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def load(path):
    rows = list(csv.reader(open(path)))
    hdr = rows[0]
    assert hdr[1:8] == EXPECT_HDR, (path, hdr[:9])
    assert hdr[9] == "BT", (path, hdr[9])
    out = []
    for x in rows[1:]:
        x = x + [""] * (21 - len(x))
        city = x[5].strip().upper()
        if city == "MILPITAS":
            continue
        try:
            lp = float(str(x[7]).replace("$", "").replace(",", ""))
        except ValueError:
            lp = None
        out.append((x[1].strip(), city, lp))
    return out


def lux(rows, statuses, lo=2_000_000):
    return [r for r in rows if r[0] in statuses and r[2] is not None and r[2] >= lo]


def snapshots():
    files = sorted(glob.glob(os.path.join(HIST, "20*.csv")))
    snaps = {}
    for f in files:
        d = date.fromisoformat(os.path.basename(f)[:10])
        snaps[d] = load(f)
    return snaps


def chart_monthly(snaps):
    days = [d for d in sorted(snaps) if d != date(2025, 10, 13)]          # one per month
    assert len(days) == 13 and days[0] == date(2025, 10, 9) and days[-1] == date(2026, 10, 10)
    ctr = [len(lux(snaps[d], CONTRACT)) for d in days]
    sale = [len(lux(snaps[d], SALE)) for d in days]
    assert ctr == [87, 89, 46, 47, 70, 73, 88, 120, 87, 82, 82, 65, 64], ctr
    assert sale == [191, 140, 110, 62, 92, 148, 198, 215, 214, 206, 196, 166, 167], sale
    b13 = date(2025, 10, 13)
    assert len(lux(snaps[b13], CONTRACT)) == 89 and len(lux(snaps[b13], SALE)) == 185
    peak = max(range(len(ctr)), key=lambda i: ctr[i])
    down_yr = abs(r0(pct(ctr[0], ctr[-1])))                 # 26
    down_pk = abs(r0(pct(ctr[peak], ctr[-1])))              # 47
    assert (down_yr, down_pk) == (26, 47)

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.06, 0.15, 0.91, 0.62])
    ax.set_facecolor(CREAM)
    x = list(range(len(days)))
    w = 0.38
    ax.bar([i - w / 2 for i in x], sale, width=w, color=SAND, edgecolor="none", zorder=3, label="For sale")
    ax.bar([i + w / 2 for i in x], ctr, width=w, color=CORAL, edgecolor="none", zorder=3, label="In contract")
    for i, v in enumerate(ctr):
        ax.text(i + w / 2, v + 3, f"{v}", ha="center", va="bottom", fontsize=11.5, fontweight="bold",
                color=CORAL_D if i in (peak, len(ctr) - 1, 0) else INK, zorder=4)
    for i, v in enumerate(sale):
        ax.text(i - w / 2, v + 3, f"{v}", ha="center", va="bottom", fontsize=10, color=MUTED, zorder=4)

    ax.annotate(f"Spring peak: {ctr[peak]} in contract", xy=(peak + w / 2, ctr[peak] + 14),
                xytext=(peak + 0.2, 262), fontsize=13, fontweight="bold", color=CORAL_D,
                ha="center", va="bottom", arrowprops=dict(arrowstyle="-", color=CORAL_D, lw=1.2))
    ax.text(len(ctr) - 1 + w / 2, 262, f"Today: {ctr[-1]}, down {down_yr}% on the year\nand {down_pk}% from May",
            fontsize=13, fontweight="bold", color=CORAL_D, ha="right", va="bottom", linespacing=1.3)

    labels = []
    for i, d in enumerate(days):
        m = AP_MONTHS[d.month - 1]
        labels.append(f"{m}\n{d.year}" if i in (0, 3, len(days) - 1) else m)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11.5, color=MUTED)
    ax.set_xlim(-0.7, len(days) - 0.3)
    ax.set_ylim(0, 300)
    ax.set_yticks([0, 50, 100, 150, 200, 250])
    ax.set_yticklabels(["0", "50", "100", "150", "200", "250"], fontsize=11, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    leg = ax.legend(loc="upper left", bbox_to_anchor=(0.0, 1.0), frameon=False, fontsize=12, ncol=2,
                    handlelength=1.2, columnspacing=1.4)
    for t in leg.get_texts():
        t.set_color(INK)

    fig.text(0.035, 0.955, "East Bay Luxury Had Its Spring", fontsize=26, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.895,
             "Homes listed at \\$2 million or more across our 14 city MLS table, "
             "one snapshot near the 10th of each month",
             fontsize=13.2, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.030,
             "Source: our daily MLS exports, Oct. 9, 2025 to Oct. 10, 2026. List prices, all property types; "
             "in contract = pending and contingent;\ncoming soon excluded. Milpitas left out (it joined the export "
             "in January).",
             fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.4)
    return fig


def area_counts(rows):
    c = Counter()
    for st, city, lp in lux(rows, CONTRACT):
        c["Tri-Valley" if city in TRI_VALLEY else "Tri-City" if city in TRI_CITY else "Rest of the table"] += 1
    return c


def chart_where(snaps):
    a, b = snaps[date(2025, 10, 9)], snaps[date(2026, 10, 10)]
    ca, cb = area_counts(a), area_counts(b)
    assert (ca["Tri-Valley"], ca["Tri-City"], ca["Rest of the table"]) == (60, 18, 9), ca
    assert (cb["Tri-Valley"], cb["Tri-City"], cb["Rest of the table"]) == (35, 23, 6), cb
    c13 = area_counts(snaps[date(2025, 10, 13)])
    # same direction on the second base: Tri-Valley share down, Tri-City share up
    assert c13["Tri-Valley"] / sum(c13.values()) > cb["Tri-Valley"] / sum(cb.values())
    assert c13["Tri-City"] / sum(c13.values()) < cb["Tri-City"] / sum(cb.values())
    city = lambda rows, n: sum(1 for r in lux(rows, CONTRACT) if r[1] == n)
    fa, fb, da, db = city(a, "FREMONT"), city(b, "FREMONT"), city(a, "DANVILLE"), city(b, "DANVILLE")
    pa, pb = city(a, "PLEASANTON"), city(b, "PLEASANTON")
    assert (fa, fb, da, db, pa, pb) == (15, 18, 23, 17, 16, 5)
    s13 = snaps[date(2025, 10, 13)]
    assert (city(s13, "FREMONT"), city(s13, "DANVILLE"), city(s13, "PLEASANTON")) == (20, 23, 15)
    today = Counter(r[1] for r in lux(b, CONTRACT))
    assert today.most_common(1)[0] == ("FREMONT", 18)          # Fremont leads the table today

    order = ["Tri-Valley", "Tri-City", "Rest of the table"]
    cols = [BLUE, CORAL, GOLD]
    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    for k, (cnt, when, sub) in enumerate(((ca, "A year ago", "Oct. 9, 2025"), (cb, "Today", "Oct. 10, 2026"))):
        ax = fig.add_axes([0.04 + k * 0.40, 0.12, 0.40, 0.62])
        ax.set_facecolor(CREAM)
        vals = [cnt[o] for o in order]
        tot = sum(vals)
        wedges, _ = ax.pie(vals, colors=cols, startangle=90, counterclock=False,
                           wedgeprops=dict(width=0.36, edgecolor=CREAM, linewidth=2.5))
        ax.text(0, 0.08, f"{tot}", ha="center", va="center", fontsize=34, fontweight="bold", color=INK)
        ax.text(0, -0.17, "\\$2M+ homes\nin contract", ha="center", va="center", fontsize=12, color=MUTED,
                linespacing=1.2)
        ang = 90
        for v, col in zip(vals, cols):
            share = v / tot * 360
            mid = math.radians(ang - share / 2)
            ang -= share
            r = 0.82
            pc = r0(Decimal(v) / Decimal(tot) * 100)
            ax.text(r * math.cos(mid), r * math.sin(mid), f"{v}\n{pc}%", ha="center", va="center",
                    fontsize=12.5, fontweight="bold", color="white", linespacing=1.1)
        ax.text(0, 1.30, when, ha="center", va="bottom", fontsize=17, fontweight="bold", color=INK)
        ax.text(0, 1.14, sub, ha="center", va="bottom", fontsize=12, color=MUTED)
        ax.set_aspect("equal")
    # legend + read
    lx = 0.835
    for i, (o, col) in enumerate(zip(order, cols)):
        y = 0.70 - i * 0.075
        fig.patches.append(matplotlib.patches.FancyBboxPatch((lx, y - 0.012), 0.018, 0.03,
                           boxstyle="round,pad=0.002", transform=fig.transFigure, facecolor=col,
                           edgecolor="none"))
        fig.text(lx + 0.027, y + 0.003, o, fontsize=13, color=INK, va="center")
    fig.text(lx, 0.405, "Tri-Valley: Danville,\nPleasanton, San Ramon,\nDublin, Livermore\n\n"
             "Tri-City: Fremont,\nNewark, Union City",
             fontsize=10.8, color=MUTED, va="top", linespacing=1.3)
    fig.text(lx, 0.235, f"Fremont now leads\nthe table with {fb}.\nDanville: {da} to {db}.\nPleasanton: {pa} to {pb}.",
             fontsize=11.5, color=CORAL_D, fontweight="bold", va="top", linespacing=1.35)

    fig.text(0.035, 0.955, "Where the \\$2M+ Buyers Are Signing", fontsize=26, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.895,
             "Homes listed at \\$2 million or more that are in contract, by area, across our 14 city MLS table",
             fontsize=13.2, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.030,
             "Source: our daily MLS exports of Oct. 9, 2025 and Oct. 10, 2026. List prices; pending and contingent; "
             "all property types. Rest: Oakland, Hayward, Castro Valley and others.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


def band_counts(rows):
    c = Counter()
    for st, city, lp in rows:
        if st in CONTRACT and lp is not None:
            for lo, hi, n in BANDS:
                if lo <= lp < hi:
                    c[n] += 1
    return [c[n] for _, _, n in BANDS]


def chart_bands(snaps):
    a = band_counts(snaps[date(2025, 10, 9)])
    b = band_counts(snaps[date(2026, 10, 10)])
    a13 = band_counts(snaps[date(2025, 10, 13)])
    assert a == [453, 202, 126, 60, 27] and b == [416, 163, 103, 49, 15], (a, b)
    assert all(y < x for x, y in zip(a13, b))                  # every band down on the second base too
    ch = [pct(x, y) for x, y in zip(a, b)]
    assert [r0(v) for v in ch] == [-8, -19, -18, -18, -44], ch

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.06, 0.17, 0.91, 0.58])
    ax.set_facecolor(CREAM)
    x = list(range(len(BANDS)))
    cols = [SAND, SAND, SAND, CORAL, CORAL_D]
    ax.bar(x, [float(v) for v in ch], width=0.6, color=cols, zorder=3)
    for i, (v, p, q) in enumerate(zip(ch, a, b)):
        ax.text(i, float(v) - 2.2, f"\u2212{abs(r0(v))}%", ha="center", va="top", fontsize=20,
                fontweight="bold", color=CORAL_D if i >= 3 else INK, zorder=4)
        ax.text(i, float(v) - 9.0, f"{p} to {q}", ha="center", va="top", fontsize=12, color=MUTED, zorder=4)
    ax.axhline(0, color=INK, lw=1.1, alpha=0.6, zorder=2)
    ax.set_xticks(x)
    ax.set_xticklabels([n for _, _, n in BANDS], fontsize=13, color=INK)
    ax.xaxis.set_ticks_position("top")
    ax.set_ylim(-62, 2)
    ax.set_yticks([])
    ax.tick_params(axis="both", length=0, pad=10)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.035, 0.955, "Contracts Fell Most at the Very Top", fontsize=26, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.895,
             "Change in homes in contract by list price, Oct. 9, 2025 to Oct. 10, 2026, across our 14 city MLS table",
             fontsize=13.2, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.030,
             "Source: our daily MLS exports. In contract = pending and contingent; all property types. "
             "Milpitas left out (joined in January).",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    snaps = snapshots()
    for name, fn in (("luxury-monthly", chart_monthly), ("luxury-where", chart_where), ("luxury-bands", chart_bands)):
        fig = fn(snaps)
        save_pair(fig, os.path.join(OUTDIR, f"{name}-{STAMP}.png"), facecolor=CREAM)
        plt.close(fig)
