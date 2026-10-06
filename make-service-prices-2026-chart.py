#!/usr/bin/env python3
"""
make-service-prices-2026-chart.py  DATA_DIR  [outdir]

The 10/06/26 daily's services inflation chart (Economy section). Harv attached the
newsletter graphic "Service Prices Spike" (the ISM services prices paid index,
Sep 2025 to Sep 2026, 74.0 in September). That chart is NOT recreated: ISM's release
license forbids charts, tables or time series derived from its PMI content
(reference-ism-pmi-license-no-derived-charts). The ISM numbers go in the copy only.
This chart tells the same story from public domain BLS data, with a Bay Area panel
(feedback-localize-national-studies). Emits BOTH variants:

  service-prices-100626.png      plain HB monogram    -> RE email + Agent Hub
  service-prices-100626-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds the raw keyless BLS API v2 response pulled 10/06/26
(POST api.bls.gov/publicAPI/v2/timeseries/data/, startyear 2021, endyear 2026):
  bls-cpi.json   WPUFD4       PPI final demand services, not seasonally adjusted
                 CUUR0000SAS  CPI-U services, U.S. city average, NSA
                 CUURS49BSAS  CPI-U services, San Francisco-Oakland-Hayward, NSA
                              (bimonthly, even months; Alameda, Contra Costa, Marin,
                              San Francisco and San Mateo counties)
Every percent is computed here from the index LEVELS (one vintage), 12-month change.

=============================================================================
VERIFICATION 10/06/26
=============================================================================
PPI final demand services, change from a year earlier:
  Sep 25 3.0, Oct 2.8, Nov 3.1, Dec 3.1, Jan 26 3.1, Feb 3.4, Mar 4.3, Apr 5.7,
  May 5.9, Jun 5.6, Jul 4.8, Aug 5.4. May's 5.9% was the highest since December
  2022 (6.4%); every month from Jan 2023 to Apr 2026 was below it. PPI is revised
  four months after first publication, so May to August are still preliminary.
CPI services, August vs a year earlier:
  San Francisco area  2.8% (Aug 2025) -> 3.8% (Aug 2026)
  U.S. city average   3.8% (Aug 2025) -> 3.1% (Aug 2026)
Cross-check: BLS's own August 2026 San Francisco release prints all items +3.4%
and all items less food and energy +3.0%; the same pull computes 3.39 and 3.0.
ISM (text only, never charted): prices index 74 in September from 72.6, the highest
since July 2022 (74.5); Services PMI 54.9 (PR Newswire, Oct. 5, 2026).

matplotlib only; build with python3.13 on Mac.
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
STAMP = "100626"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
SLATE = "#6f8296"
PALE = "#a7b3c0"
GRID = "#d8cdb8"
MUTED = "#8a8172"

PPI, US, SF = "WPUFD4", "CUUR0000SAS", "CUURS49BSAS"
WINDOW = [(2025, m) for m in range(9, 13)] + [(2026, m) for m in range(1, 9)]
TICKS = ["Sep '25", "Oct", "Nov", "Dec", "Jan '26", "Feb", "Mar", "Apr", "May", "Jun",
         "Jul", "Aug '26"]


def levels(path):
    # CPI has no October 2025 (the shutdown); BLS sends "-" for that month
    out = {}
    for s in json.load(open(path))["Results"]["series"]:
        out[s["seriesID"]] = {
            (int(x["year"]), int(x["period"][1:])): Decimal(x["value"])
            for x in s["data"] if x["period"].startswith("M") and x["period"] != "M13"
            and x["value"].replace(".", "", 1).isdigit()
        }
    return out


def yoy(ser, y, m):
    return (ser[(y, m)] / ser[(y - 1, m)] - 1) * 100


def r1(d):
    return d.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def load():
    lv = levels(os.path.join(DATA, "bls-cpi.json"))
    ppi = [yoy(lv[PPI], y, m) for y, m in WINDOW]
    got = [str(r1(v)) for v in ppi]
    assert got == ["3.0", "2.8", "3.1", "3.1", "3.1", "3.4", "4.3", "5.7", "5.9", "5.6",
                   "4.8", "5.4"], got

    # "May's 5.9% was the highest since December 2022": every month from Jan 2023 to
    # Apr 2026 sits below May, and December 2022 sits above it
    may = yoy(lv[PPI], 2026, 5)
    between = [(y, m) for y in (2023, 2024, 2025, 2026) for m in range(1, 13)
               if (2023, 1) <= (y, m) <= (2026, 4)]
    assert all(yoy(lv[PPI], y, m) < may for y, m in between)
    assert yoy(lv[PPI], 2022, 12) >= may

    panel = [
        ("Bay Area*", yoy(lv[SF], 2025, 8), yoy(lv[SF], 2026, 8)),
        ("United States", yoy(lv[US], 2025, 8), yoy(lv[US], 2026, 8)),
    ]
    want = [("2.8", "3.8"), ("3.8", "3.1")]
    for (name, a, b), (wa, wb) in zip(panel, want):
        assert (str(r1(a)), str(r1(b))) == (wa, wb), (name, a, b)
    return [float(v) for v in ppi], [str(r1(v)) for v in ppi], panel


def build():
    ppi, lab, panel = load()
    print("PPI services y/y:", dict(zip(TICKS, lab)))
    print("CPI services Aug/Aug:", [(n, str(r1(a)), str(r1(b))) for n, a, b in panel])

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)

    # ---- left: U.S. producer prices for services ------------------------------
    ax = fig.add_axes([0.06, 0.205, 0.585, 0.56])
    ax.set_facecolor(CREAM)
    x = list(range(len(ppi)))
    ax.fill_between(x, ppi, 2.0, color=SLATE, alpha=0.10, lw=0, zorder=1)
    ax.plot(x, ppi, color=SLATE, lw=2.8, solid_joinstyle="round", zorder=3)
    lo = ppi.index(min(ppi))
    hi = ppi.index(max(ppi))
    last = len(ppi) - 1
    box = dict(boxstyle="square,pad=0.12", facecolor=CREAM, edgecolor="none")
    for i, v in enumerate(ppi):
        if i == last:
            ax.scatter([i], [v], s=110, color=CORAL, edgecolor=CREAM, linewidth=1.6, zorder=6)
            continue
        if i == lo:
            ax.scatter([i], [v], s=70, color=CREAM, edgecolor=SLATE, linewidth=2.2, zorder=6)
        else:
            ax.scatter([i], [v], s=40, color=SLATE, zorder=5)
        weight = "bold" if i in (lo, hi) else "normal"
        # Feb, Mar and Jun sit on steep stretches where a centered label touches a segment:
        # Feb goes below right (under the climb), Mar above left, Jun below left
        if TICKS[i] == "Feb":
            ax.text(i + 0.12, v - 0.10, f"{lab[i]}%", ha="left", va="top", fontsize=12.5,
                    fontweight=weight, color=INK, zorder=7, bbox=box)
            continue
        if TICKS[i] == "Mar":
            ax.text(i - 0.13, v + 0.06, f"{lab[i]}%", ha="right", va="bottom", fontsize=12.5,
                    fontweight=weight, color=INK, zorder=7, bbox=box)
            continue
        if TICKS[i] == "Jun":
            ax.text(i - 0.10, v - 0.10, f"{lab[i]}%", ha="right", va="top", fontsize=12.5,
                    fontweight=weight, color=INK, zorder=7, bbox=box)
            continue
        # labels above the line, except the low and the July dip, which sit below
        below = i in (lo, 10)
        off = -0.20 if below else 0.17
        ax.text(i, v + off, f"{lab[i]}%", ha="center", va="top" if below else "bottom",
                fontsize=12.5, fontweight=weight, color=INK, zorder=7, bbox=box)
    ax.annotate(f"{lab[last]}%", xy=(last, ppi[last]), xytext=(0, 26), textcoords="offset points",
                fontsize=20, fontweight="bold", color="white", ha="center", va="bottom", zorder=8,
                bbox=dict(boxstyle="round,pad=0.35", facecolor=CORAL, edgecolor="none"))
    ax.text(hi, ppi[hi] + 0.62, "fastest since\nDec. 2022", ha="center", va="bottom",
            fontsize=10.5, color=MUTED, linespacing=1.1, zorder=7)

    ax.set_xticks(x)
    ax.set_xticklabels(TICKS, fontsize=12, color=MUTED)
    ax.get_xticklabels()[-1].set_color(DEEP)
    ax.get_xticklabels()[-1].set_fontweight("bold")
    yt = [2, 3, 4, 5, 6, 7]
    ax.set_yticks(yt)
    ax.set_yticklabels([f"{v}%" for v in yt], fontsize=11, color=MUTED)
    ax.set_ylim(2.0, 7.45)
    ax.set_xlim(-0.5, last + 0.6)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title("What U.S. service businesses charge (producer prices)", loc="left",
                 fontsize=13, fontweight="bold", color=INK, pad=14)

    # ---- right: consumer prices for services, Bay Area vs U.S. ---------------
    bx = fig.add_axes([0.745, 0.205, 0.215, 0.56])
    bx.set_facecolor(CREAM)
    ys = [1.0, 0.0]
    for yy, (name, a, b) in zip(ys, panel):
        a_f, b_f = float(a), float(b)
        rising = b_f > a_f
        col = CORAL if rising else SLATE
        bx.annotate("", xy=(b_f, yy), xytext=(a_f, yy), zorder=3,
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=3.2, mutation_scale=22,
                                    shrinkA=7, shrinkB=9))
        bx.scatter([a_f], [yy], s=95, color=CREAM, edgecolor=PALE, linewidth=2.4, zorder=5)
        bx.scatter([b_f], [yy], s=120, color=col, edgecolor=CREAM, linewidth=1.5, zorder=6)
        bx.text(a_f, yy - 0.2, f"{r1(a)}%", ha="center", va="top", fontsize=11.5,
                color=MUTED, zorder=7)
        bx.text(b_f, yy + 0.2, f"{r1(b)}%", ha="center", va="bottom", fontsize=17,
                fontweight="bold", color=DEEP if rising else INK, zorder=7)
    bx.set_yticks(ys)
    bx.set_yticklabels([p[0] for p in panel], fontsize=12.5, color=INK)
    bx.get_yticklabels()[0].set_fontweight("bold")
    bx.get_yticklabels()[0].set_color(DEEP)
    bx.set_xlim(2.4, 4.2)
    bx.set_ylim(-0.75, 1.75)
    bx.set_xticks([])
    bx.tick_params(axis="y", length=0, pad=10)
    for sp in bx.spines.values():
        sp.set_visible(False)
    bx.set_title("What consumers pay for services", loc="left", fontsize=13,
                 fontweight="bold", color=INK, pad=14, x=-0.42)
    # legend for the two dots, under the panel title
    bx.scatter([2.55], [-0.62], s=60, color=CREAM, edgecolor=PALE, linewidth=2.0, zorder=5,
               clip_on=False)
    bx.text(2.65, -0.62, "Aug. 2025", ha="left", va="center", fontsize=10.5, color=MUTED)
    bx.scatter([3.42], [-0.62], s=70, color=SLATE, edgecolor=CREAM, linewidth=1.2, zorder=5,
               clip_on=False)
    bx.text(3.52, -0.62, "Aug. 2026", ha="left", va="center", fontsize=10.5, color=MUTED)

    fig.text(0.035, 0.955, "Service Prices Are Heating Up, and Faster in the Bay Area",
             fontsize=23, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.905, "Change in prices from a year earlier, not seasonally adjusted",
             fontsize=13.5, color=MUTED, ha="left", va="top")

    fig.text(
        0.035, 0.098,
        "Service businesses raised prices 5.4% over the year to August, up from 3.0% a year earlier. "
        "Bay Area consumer prices for services rose 3.8%, the U.S. 3.1%.",
        fontsize=11.2, color=DEEP, ha="left", va="bottom",
    )
    fig.text(0.035, 0.030,
             "Source: U.S. Bureau of Labor Statistics, Producer Price Index (final demand services) and "
             "Consumer Price Index (services), data through August 2026;\nproducer prices for May to "
             "August are preliminary. *San Francisco, Oakland, Hayward area: Alameda, Contra Costa, "
             "Marin, San Francisco and San Mateo counties.",
             fontsize=9.8, color=MUTED, ha="left", va="bottom", linespacing=1.3)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"service-prices-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
