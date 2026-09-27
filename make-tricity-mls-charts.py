#!/usr/bin/env python3
"""
make-tricity-mls-charts.py  HIST_DIR  [outdir]

Three Tri-City inventory charts for the 09/27/26 Sunday edition, built from OUR
OWN saved MLS exports rather than Zillow. Harv asked for bars or pies showing
Fremont, Newark and Union City inventory against last month, the start of the
year and last year.

  tricity-snapshots-092726.png   grouped bars, 4 snapshots per city
  tricity-monthly-092726.png     stacked bars, one late month export per month
  tricity-pricemix-092726.png    two donuts, price mix a year ago vs today
  (each with its -hb twin via chart_brand.save_pair)

=============================================================================
SOURCE AND BASIS
=============================================================================

HIST_DIR holds one CSV per snapshot, named MMDDYY.csv, each a verbatim dump of
the dated MLS_Defined_Spread_Sheet_4 export for that day (the same sheet
dump-mls-csv.js reads each morning; older days were .xlsx files converted
cell for cell). The earliest export on Drive is 10/07/2025, so "a year ago" is
that file, 51 weeks back, and the chart says so. The MLS data itself is never
committed; only these counts are.

BASIS: the five city ledger's own definition (generate-live-inventory.js):
live statuses ACTV, NEW, CS and BOMK, all property types. So every count here
is on the same basis as the ledger numbers printed in the report copy, and the
09/27 bar equals today's ledger city count. Pending (PEND), contingent (AC) and
price change (PCH) rows are excluded, as the ledger excludes them.

Every export from 10/07/2025 to today carries the same 21 column header and the
same status codes, verified at build time below (the script refuses to run if
a header differs). Milpitas joined the export in January; it is not on these
charts, so the city set is unaffected.

Counts on 09/27/26 (generated from the CSVs, printed by this script):
  snapshot       Fremont  Newark  Union City
  10/07/25         225      61       43
  01/02/26          88      27       20
  08/27/26         281      73       54
  09/27/26         257      88       67

matplotlib only; build with python3.13 on Mac.
"""
import csv
import math
import os
import sys
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

HIST = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "092726"
LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hb-logo-mark.png")

CREAM = "#fdf6e8"
INK = "#1f2933"
GRID = "#d8cdb8"
MUTED = "#8a8172"
# City hues validated with the dataviz palette checker on the cream surface
# (09/27/26): CVD separation 13.9, normal vision 25.4, all three 3:1 or better.
# The old coral and green pair failed protan separation at 5.9.
CITY_COLOR = {"FREMONT": "#e2574c", "NEWARK": "#2f6f9f", "UNION CITY": "#b7862a"}
CITIES = ["FREMONT", "NEWARK", "UNION CITY"]
NICE = {"FREMONT": "Fremont", "NEWARK": "Newark", "UNION CITY": "Union City"}
LIVE = {"ACTV", "NEW", "CS", "BOMK"}
HEADER = ("MLS No,Status,DOM,Address,Unit,City,Area,LP,SP,BT,SqFt,BR,Bth,PB,"
          "Gar,GarSp,YrBlt,Acres,Lot SqFt,HOA Fee,Freq").split(",")

# One export from the last week of each month (27th, or the nearest day with
# an export: 11/25 was the last before Thanksgiving, 12/23 the last before
# Christmas, 06/26 because there is no 06/27 file).
MONTHLY = [("102725", "Oct\n2025"), ("112525", "Nov"), ("122325", "Dec"),
           ("012726", "Jan\n2026"), ("022726", "Feb"), ("032726", "Mar"),
           ("042726", "Apr"), ("052726", "May"), ("062626", "Jun"),
           ("072726", "Jul"), ("082726", "Aug"), ("092726", "Sep")]
SNAPS = [("100725", "Oct 7\n2025"), ("010226", "Jan 2\n2026"),
         ("082726", "Aug 27\n2026"), ("092726", "Today\nSep 27")]


def load(stamp):
    path = os.path.join(HIST, f"{stamp}.csv")
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    if [h.strip() for h in rows[0]] != HEADER:
        raise SystemExit(f"{path}: header differs from the ledger layout")
    col = {h: i for i, h in enumerate(HEADER)}
    live = []
    for r in rows[1:]:
        city = r[col["City"]].strip().upper()
        st = r[col["Status"]].strip().upper()
        if city in CITIES and st in LIVE:
            live.append({"city": city, "lp": float(r[col["LP"]])})
    return live


def counts(stamp):
    c = Counter(x["city"] for x in load(stamp))
    return {k: c.get(k, 0) for k in CITIES}


def pct(a, b):
    """Percent change b -> a, half up, never half to even."""
    return Decimal(str((a / b - 1) * 100)).quantize(Decimal("1"), ROUND_HALF_UP)


def signed(d):
    # Spelled out, never a bare minus that can vanish at small sizes.
    return f"up {d}%" if d > 0 else (f"down {abs(d)}%" if d < 0 else "flat")


def style(ax):
    ax.set_facecolor(CREAM)
    ax.grid(axis="y", color=GRID, lw=0.7, alpha=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9.5, length=0)
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_color(INK)


def ramp(hex_color, n):
    """Light to full strength in one hue: the old snapshots fade, today is solid."""
    import matplotlib.colors as mc
    base = mc.to_rgb(hex_color)
    cream = mc.to_rgb(CREAM)
    out = []
    for i in range(n):
        t = 0.28 + 0.72 * (i / (n - 1))
        out.append(tuple(cream[j] + (base[j] - cream[j]) * t for j in range(3)))
    return out


SNAP = {s: counts(s) for s, _ in SNAPS}
MON = {s: counts(s) for s, _ in MONTHLY}
assert SNAP["092726"] == MON["092726"]

# ================================================================ chart 1
fig, axes = plt.subplots(1, 3, figsize=(11.6, 7.4), sharey=True,
                         gridspec_kw=dict(wspace=0.10))
fig.patch.set_facecolor(CREAM)
YMAX = 330
for ax, city in zip(axes, CITIES):
    style(ax)
    vals = [SNAP[s][city] for s, _ in SNAPS]
    cols = ramp(CITY_COLOR[city], len(vals))
    x = range(len(vals))
    ax.bar(x, vals, width=0.74, color=cols, edgecolor=CREAM, linewidth=2,
           zorder=3)
    for i, v in enumerate(vals):
        last = i == len(vals) - 1
        ax.text(i, v + 6, f"{v}", ha="center", va="bottom", color=INK,
                fontsize=13 if last else 11.5,
                fontweight="bold" if last else "normal")
    ax.set_xticks(list(x))
    ax.set_xticklabels([l for _, l in SNAPS], fontsize=9.2)
    for t in ax.get_xticklabels():
        t.set_color(INK)
    ax.get_xticklabels()[-1].set_fontweight("bold")
    ax.set_ylim(0, YMAX)
    ax.set_xlim(-0.6, len(vals) - 0.4)
    ax.set_title(NICE[city].upper(), loc="left", fontsize=13.5,
                 fontweight="bold", color=CITY_COLOR[city], pad=10)
    now, mo, jan, yr = vals[3], vals[2], vals[1], vals[0]
    ax.text(0.0, -0.165,
            f"vs a month ago: {signed(pct(now, mo))}\n"
            f"vs a year ago: {signed(pct(now, yr))}",
            transform=ax.transAxes, fontsize=10.6, color=INK, va="top",
            linespacing=1.5)
axes[0].set_ylabel("Homes for sale", color=INK, fontsize=10.5, labelpad=8)

fig.text(0.062, 0.955, "Fremont eased; Newark and Union City kept building",
         fontsize=18.5, fontweight="bold", color=INK, ha="left")
fig.text(0.062, 0.915,
         "Homes for sale a year ago, at New Year, a month ago and today. Same scale in every panel.",
         fontsize=11.4, color=MUTED, ha="left")
fig.text(0.062, 0.035,
         "Source: our daily MLS export. Active, new, back on market and coming soon; all property types.\n"
         "Oct 7, 2025 is the earliest saved export, 51 weeks before today. Jan 2 is the holiday low.",
         fontsize=9.0, color=MUTED, ha="left", linespacing=1.45)
fig.subplots_adjust(left=0.075, right=0.975, top=0.835, bottom=0.265)
save_pair(fig, os.path.join(OUTDIR, f"tricity-snapshots-{STAMP}.png"), logo=LOGO)
plt.close(fig)

# ================================================================ chart 2
fig, ax = plt.subplots(figsize=(11.6, 7.2))
fig.patch.set_facecolor(CREAM)
style(ax)
x = list(range(len(MONTHLY)))
bottom = [0] * len(x)
for city in CITIES:
    vals = [MON[s][city] for s, _ in MONTHLY]
    ax.bar(x, vals, bottom=bottom, width=0.72, color=CITY_COLOR[city],
           edgecolor=CREAM, linewidth=2, zorder=3, label=NICE[city])
    # Direct label the segments of the newest bar only.
    ax.text(x[-1] + 0.46, bottom[-1] + vals[-1] / 2, f"{NICE[city]} {vals[-1]}",
            ha="left", va="center", fontsize=10.2, color=INK)
    bottom = [b + v for b, v in zip(bottom, vals)]
for i, tot in enumerate(bottom):
    last = i == len(bottom) - 1
    ax.text(i, tot + 7, f"{tot}", ha="center", va="bottom", color=INK,
            fontsize=12.5 if last else 10.8,
            fontweight="bold" if last else "normal")
ax.set_xticks(x)
ax.set_xticklabels([l for _, l in MONTHLY], fontsize=9.6)
for t in ax.get_xticklabels():
    t.set_color(INK)
ax.set_xlim(-0.6, len(x) + 1.15)
ax.set_ylim(0, 520)
ax.set_ylabel("Homes for sale, three cities combined", color=INK, fontsize=10.5,
              labelpad=8)
leg = ax.legend(loc="upper left", frameon=False, ncol=3, fontsize=10.5,
                handlelength=1.1, handleheight=1.1, bbox_to_anchor=(0.0, 1.02))
for t in leg.get_texts():
    t.set_color(INK)

peak_i = max(range(len(bottom)), key=lambda i: bottom[i])
low_i = min(range(len(bottom)), key=lambda i: bottom[i])
fig.text(0.062, 0.955, "A year of Tri-City inventory, month by month",
         fontsize=19, fontweight="bold", color=INK, ha="left")
fig.text(0.062, 0.915,
         f"Fremont, Newark and Union City stacked. Low of {bottom[low_i]} in "
         f"{MONTHLY[low_i][1].split(chr(10))[0]}, peak of {bottom[peak_i]} in "
         f"{MONTHLY[peak_i][1].split(chr(10))[0]}, {bottom[-1]} today.",
         fontsize=11.4, color=MUTED, ha="left")
fig.text(0.062, 0.035,
         "Source: our daily MLS export from the last week of each month (the 27th, or the nearest export day).\n"
         "Active, new, back on market and coming soon; all property types.",
         fontsize=9.0, color=MUTED, ha="left", linespacing=1.45)
fig.subplots_adjust(left=0.075, right=0.975, top=0.86, bottom=0.14)
save_pair(fig, os.path.join(OUTDIR, f"tricity-monthly-{STAMP}.png"), logo=LOGO)
plt.close(fig)

# ================================================================ chart 3
BANDS = [(r"Under \$1M", 0, 1_000_000), (r"\$1M to \$1.5M", 1_000_000, 1_500_000),
         (r"\$1.5M to \$2M", 1_500_000, 2_000_000), (r"\$2M and up", 2_000_000, 1e12)]
# Ordered price bands are a magnitude, so one hue light to dark.
BAND_COLOR = ["#cfe5d3", "#8cc39a", "#3f8f5b", "#1d5a36"]


def mix(stamp):
    rows = load(stamp)
    return [sum(1 for r in rows if lo <= r["lp"] < hi) for _, lo, hi in BANDS]


A, B = mix("100725"), mix("092726")
assert sum(A) == sum(SNAP["100725"].values()) and sum(B) == sum(SNAP["092726"].values())

fig, axes = plt.subplots(1, 2, figsize=(11.6, 7.6))
fig.patch.set_facecolor(CREAM)
for ax, vals, title in ((axes[0], A, "Oct 7, 2025"), (axes[1], B, "Today, Sep 27, 2026")):
    ax.set_facecolor(CREAM)
    tot = sum(vals)
    wedges, _ = ax.pie(vals, colors=BAND_COLOR, startangle=90, counterclock=False,
                       wedgeprops=dict(width=0.40, edgecolor=CREAM, linewidth=2.5))
    for bi, (w, v) in enumerate(zip(wedges, vals)):
        ang = math.radians((w.theta1 + w.theta2) / 2)
        r = 0.80
        share = Decimal(str(v / tot * 100)).quantize(Decimal("1"), ROUND_HALF_UP)
        dark = bi >= 2
        ax.text(r * math.cos(ang), r * math.sin(ang), f"{share}%",
                ha="center", va="center", fontsize=12, fontweight="bold",
                color=CREAM if dark else INK)
    ax.text(0, 0.07, f"{tot}", ha="center", va="center", fontsize=26,
            fontweight="bold", color=INK)
    ax.text(0, -0.17, "homes", ha="center", va="center", fontsize=11, color=MUTED)
    ax.set_title(title, fontsize=13.5, fontweight="bold", color=INK, pad=4)
    ax.set_aspect("equal")

# Change table under the donuts, one row per band.
rows_txt = []
for (name, _, _), a, b in zip(BANDS, A, B):
    rows_txt.append((name, a, b, pct(b, a)))
y0 = 0.225
fig.text(0.215, y0 + 0.042, "Price band", fontsize=10, color=MUTED, ha="left")
fig.text(0.52, y0 + 0.042, "A year ago", fontsize=10, color=MUTED, ha="right")
fig.text(0.63, y0 + 0.042, "Today", fontsize=10, color=MUTED, ha="right")
fig.text(0.76, y0 + 0.042, "Change", fontsize=10, color=MUTED, ha="right")
for i, (name, a, b, d) in enumerate(rows_txt):
    y = y0 - i * 0.036
    fig.patches.append(plt.Rectangle((0.19, y - 0.004), 0.016, 0.022,
                                     transform=fig.transFigure,
                                     color=BAND_COLOR[i], zorder=5))
    bold = "bold" if i == 1 else "normal"
    fig.text(0.215, y, name, fontsize=11, color=INK, ha="left", fontweight=bold)
    fig.text(0.52, y, f"{a}", fontsize=11, color=INK, ha="right")
    fig.text(0.63, y, f"{b}", fontsize=11, color=INK, ha="right", fontweight=bold)
    fig.text(0.76, y, signed(d), fontsize=11, color=INK, ha="right", fontweight=bold)

fig.text(0.062, 0.955, "Where the new Tri-City inventory is priced",
         fontsize=19, fontweight="bold", color=INK, ha="left")
fig.text(0.062, 0.915,
         "Fremont, Newark and Union City by list price. The growth is almost all in one band.",
         fontsize=11.4, color=MUTED, ha="left")
fig.text(0.062, 0.035,
         "Source: our daily MLS export. Active, new, back on market and coming soon; all property types.\n"
         "Oct 7, 2025 is the earliest saved export, 51 weeks before today.",
         fontsize=9.0, color=MUTED, ha="left", linespacing=1.45)
fig.subplots_adjust(left=0.04, right=0.96, top=0.86, bottom=0.34, wspace=0.08)
save_pair(fig, os.path.join(OUTDIR, f"tricity-pricemix-{STAMP}.png"), logo=LOGO)
plt.close(fig)

# ================================================================ checks
print("\nSnapshots (ledger basis):")
for s, lab in SNAPS:
    print(f"  {s}  " + "  ".join(f"{NICE[c]} {SNAP[s][c]:>3}" for c in CITIES)
          + f"  total {sum(SNAP[s].values())}")
print("Monthly totals:", [(s, sum(MON[s].values())) for s, _ in MONTHLY])
print("Price mix a year ago:", dict(zip([b[0] for b in BANDS], A)), sum(A))
print("Price mix today:     ", dict(zip([b[0] for b in BANDS], B)), sum(B))
for c in CITIES:
    n, m, j, y = (SNAP[s][c] for s in ("092726", "082726", "010226", "100725"))
    print(f"  {NICE[c]:<11} MoM {signed(pct(n, m))}, since Jan 2 {signed(pct(n, j))}, YoY {signed(pct(n, y))}")
