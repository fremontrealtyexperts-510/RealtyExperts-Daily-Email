#!/usr/bin/env python3
"""
make-brent-roundtrip-chart.py  DATA_DIR  [outdir]

Recreates the newsletter graphic "Oil's Wild Round Trip Is Back On" for the
09/29/26 daily. Emits BOTH brand variants:

  brent-roundtrip-092926.png      plain monogram -> RE email + Agent Hub
  brent-roundtrip-092926-hb.png   + wordmark     -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/29/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

The supplied graphic plots "Brent crude, average price per barrel, 2026":
Jan $67, Feb $71, Mar $103, Apr $117, May $107, Jun $85, Jul $84, Aug $91,
then Sep $106. Footer: "U.S. EIA Short-Term Energy Outlook; Sept. figure is
Sept. 28 spot (Trading Economics)".

JANUARY TO AUGUST ARE RIGHT, ON THEIR OWN BASIS. EIA's monthly Europe Brent
spot series (RBRTE, release of 9/23/2026) prints 66.60, 70.89, 103.13, 117.29,
107.14, 85.40, 83.76, 91.08, and averaging EIA's daily spot series month by
month reproduces every one.

SEPTEMBER IS A DIFFERENT INSTRUMENT. $106 is one day's FUTURES price (the ICE
November contract settled $105.28 on Sept 28; Trading Economics quotes the
front month). On the graphic's own spot basis September is far higher: EIA's
daily spot averaged $112.96 for Sept 1 to 22, its latest data. So the graphic
joins eight physical spot averages to one futures print.

INSTRUMENT CHOSEN. Same call as make-oil100-chart.py on 09/10/26: our Economy
card is locked to ICE front month futures
(reference-brent-locked-to-bz-f-futures), so this chart plots that contract,
every month on one basis. Monthly averages are computed below from the daily
settlements; each month also gets a bar from its lowest to its highest daily
settlement, which is the "wild" part the title promises. A continuous daily
line is deliberately NOT drawn: in 2026's steep backwardation the front month
series jumps at each contract roll (Mar 31 $118.35 to Apr 1 $101.16 is the May
to June roll, not a $17 crash), and a line would present those as moves.

On this basis the peak month is MAY ($104.09), not April. April was the spot
peak because physical cargoes ran $14.83 over futures that month.

DATA_DIR must hold, fetched with shell curl on 09/29/26:
  bzf-2026.json    Yahoo chart API, BZ=F daily, 2026-01-01 to 2026-09-29
  bzx26-2026.json  Yahoo chart API, BZX26.NYM (November) daily, same window
  rbrte-d.xls      EIA daily Europe Brent spot, www.eia.gov/dnav/pet/hist_xls/RBRTEd.xls
Every number on the chart is computed from those files at build time. The
Sept 29 bar is excluded (a live tick, and BZ=F had already spliced it into the
December contract); every September day used is checked against BZX26.

matplotlib (+ pandas/xlrd for the EIA file); build with python3.13 on Mac.
"""
import json
import os
import sys
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "092926"
LAST = date(2026, 9, 28)           # last settled session used

CREAM = "#fdf6e8"
INK = "#1f2933"
DEEP = "#b8433a"
OIL = "#d9822b"
RANGE = "#efcfa6"
SLATE = "#8a9aa8"
GRID = "#d8cdb8"
MUTED = "#8a8172"


def money(x, places="0.01"):
    return Decimal(str(x)).quantize(Decimal(places), rounding=ROUND_HALF_UP)


def yahoo_closes(path):
    """{date: (close, degenerate)}; degenerate = O=H=L=C, a bar Yahoo filled in."""
    r = json.load(open(path))["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    out = {}
    for t, o, h, l, c in zip(r["timestamp"], q["open"], q["high"], q["low"], q["close"]):
        if c is None:
            continue
        d = datetime.fromtimestamp(t, timezone.utc).date()
        out[d] = (c, o == h == l == c)
    return out


def load():
    bz = yahoo_closes(os.path.join(DATA, "bzf-2026.json"))
    nov_raw = yahoo_closes(os.path.join(DATA, "bzx26-2026.json"))
    s = {}
    for d, (p, degenerate) in bz.items():
        if date(2026, 1, 1) <= d <= LAST:
            assert not degenerate, f"degenerate BZ=F bar {d}"
            s[d] = p
    nov = {d: p for d, (p, _) in nov_raw.items()}
    # September: every day must be the November contract to the cent, on a real bar.
    for d, p in s.items():
        if d.month == 9:
            assert not nov_raw[d][1], f"degenerate Nov bar {d}"
            assert abs(p - nov[d]) < 0.005, f"BZ=F spliced on {d}: {p} vs Nov {nov[d]}"
    assert money(s[LAST]) == Decimal("105.28"), s[LAST]

    import pandas as pd
    e = pd.read_excel(os.path.join(DATA, "rbrte-d.xls"), sheet_name="Data 1", skiprows=2)
    e.columns = ["date", "px"]
    spot = {pd.Timestamp(d).date(): float(p) for d, p in zip(e["date"], e["px"])
            if pd.notna(p) and pd.Timestamp(d).year == 2026}
    return s, nov, spot


def build():
    s, nov, spot = load()
    months = list(range(1, 10))
    avg, lo, hi, n = {}, {}, {}, {}
    for m in months:
        v = [p for d, p in s.items() if d.month == m]
        avg[m], lo[m], hi[m], n[m] = sum(v) / len(v), min(v), max(v), len(v)

    # EIA spot monthly means must reproduce EIA's published monthly series.
    spot_avg = {m: sum(p for d, p in spot.items() if d.month == m) /
                sum(1 for d in spot if d.month == m) for m in months}
    for m, pub in zip(range(1, 9), [66.60, 70.89, 103.13, 117.29, 107.14, 85.40, 83.76, 91.08]):
        assert money(spot_avg[m]) == money(pub), (m, spot_avg[m], pub)
    # Same-day comparison for September (days both series print).
    both = sorted(d for d in spot if d.month == 9 and d in nov)
    sep_spot = sum(spot[d] for d in both) / len(both)
    sep_fut = sum(nov[d] for d in both) / len(both)
    last_spot_day = max(d for d in spot if d.month == 9)

    peak = max(months, key=lambda m: avg[m])
    trough = min((6, 7, 8), key=lambda m: avg[m])
    print("monthly futures averages:", {m: str(money(avg[m])) for m in months})
    print(f"peak month {peak} {money(avg[peak])}, summer trough {trough} {money(avg[trough])}")
    print(f"Sept spot vs Nov futures on {len(both)} shared days to {both[-1]}: "
          f"{money(sep_spot)} vs {money(sep_fut)}")

    def xpos(m):
        if m == 9:   # centre of the days actually covered
            return date(2026, 9, 1) + (LAST - date(2026, 9, 1)) / 2
        return date(2026, m, 15)

    xs = [xpos(m) for m in months]
    ys = [avg[m] for m in months]

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    # Monthly low to high range bars.
    for m, x in zip(months, xs):
        x0 = mdates.date2num(x) - 6.5
        ax.add_patch(FancyBboxPatch((x0, lo[m]), 13, hi[m] - lo[m],
                                    boxstyle="round,pad=0,rounding_size=3.2",
                                    mutation_aspect=0.35,
                                    fc=RANGE, ec="none", alpha=0.85, zorder=1))

    ax.plot(xs, ys, color=OIL, linewidth=3.2, zorder=3, solid_joinstyle="round")
    ax.scatter(xs, ys, s=70, color=OIL, edgecolor=CREAM, linewidth=1.6, zorder=4)

    # Value labels on every monthly average.
    for m, x, y in zip(months, xs, ys):
        if m in (peak, 9):
            continue
        dy = 3.2 if m not in (6, 7) else -3.4
        ax.text(x, y + dy, f"\\${money(y, '1')}", ha="center",
                va="bottom" if dy > 0 else "top", fontsize=13, fontweight="bold",
                color=INK, zorder=5)

    ax.annotate(f"\\${money(avg[peak], '1')}", xy=(xs[peak - 1], avg[peak]),
                xytext=(0, 34), textcoords="offset points", ha="center", va="center",
                fontsize=19, fontweight="bold", color="white", zorder=6,
                bbox=dict(boxstyle="round,pad=0.32", fc=OIL, ec="none"),
                arrowprops=dict(arrowstyle="-", color=OIL, lw=1.4))
    ax.text(mdates.date2num(xs[peak - 1]) + 15.5, avg[peak] + 8.4,
            f"{date(2026, peak, 1):%B} average,\nthe year's high",
            ha="left", va="center", fontsize=11, color=MUTED, linespacing=1.35)

    ax.annotate(f"\\${money(avg[9], '1')}", xy=(xs[8], avg[9]),
                xytext=(0, 34), textcoords="offset points", ha="center", va="center",
                fontsize=19, fontweight="bold", color=INK, zorder=6,
                bbox=dict(boxstyle="round,pad=0.32", fc="white", ec=OIL, lw=1.6),
                arrowprops=dict(arrowstyle="-", color=OIL, lw=1.4))
    ax.text(xs[8], lo[9] - 2.0, f"Sept. 1 to {LAST.day}\naverage so far",
            ha="center", va="top", fontsize=10.5, color=MUTED, linespacing=1.3)
    # Monday's settle, the price on our Economy card, as its own marker.
    ax.scatter([LAST], [s[LAST]], s=80, marker="D", color=DEEP, edgecolor=CREAM,
               linewidth=1.4, zorder=6)
    ax.text(mdates.date2num(LAST) + 4.5, s[LAST], f"Monday's\nsettle\n\\${money(s[LAST])}",
            ha="left", va="center", fontsize=11, color=DEEP, fontweight="bold", linespacing=1.3)

    ax.text(xs[trough - 1], lo[trough] - 2.2, "summer\nlow", ha="center", va="top",
            fontsize=10.5, color=MUTED, linespacing=1.3)

    ax.set_xlim(date(2025, 12, 24), date(2026, 10, 30))
    ax.set_ylim(52, 128)
    ax.set_yticks([60, 80, 100, 120])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"\\${v:.0f}"))
    ax.set_xticks([mdates.date2num(x) for x in xs])
    ax.set_xticklabels([f"{date(2026, m, 1):%b}" for m in months], fontsize=13)
    ax.grid(axis="y", color=GRID, linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="both", length=0, labelsize=12.5, colors=SLATE)
    for lbl in ax.get_xticklabels():   # after tick_params, which resets colours
        lbl.set_color(INK)

    fig.text(0.045, 0.945, "Oil's Wild Round Trip Is Back On",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888,
             "Brent crude, ICE front month futures, 2026: monthly average settlement per barrel.\n"
             "Shaded bars run from each month's lowest daily settlement to its highest.",
             fontsize=13.5, color=MUTED, ha="left", va="top", linespacing=1.45)

    fig.text(
        0.045, 0.112,
        f"The version circulating today mixes two instruments: EIA's physical spot averages for January to August, then one day's\n"
        f"futures price (\\$106) for September. Spot ran far above futures this month, \\${money(sep_spot)} against \\${money(sep_fut)} "
        f"on average for Sept. 1 to {both[-1].day}.",
        fontsize=11.2, color=DEEP, ha="left", va="bottom", linespacing=1.55,
    )
    fig.text(
        0.045, 0.040,
        "Source: ICE Futures Europe via Yahoo Finance, Brent front month daily settlements (BZ=F; the November contract for September).\n"
        f"U.S. EIA Europe Brent spot price (RBRTE) for the comparison, data through Sept. {last_spot_day.day}.",
        fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5,
    )

    fig.subplots_adjust(left=0.075, right=0.965, top=0.79, bottom=0.235)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"brent-roundtrip-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
