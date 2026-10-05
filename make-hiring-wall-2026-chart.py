#!/usr/bin/env python3
"""
make-hiring-wall-2026-chart.py  DATA_DIR  [outdir]

The 10/05/26 daily's jobs chart (Economy section). Harv attached the newsletter
graphic "Hiring Hits a Wall" (U.S. monthly change in nonfarm payrolls, 2026, a
line ending at +29K in September). Rebuilt from BLS data, with a local panel
(feedback-localize-national-studies). Emits BOTH variants:

  hiring-2026-100526.png      plain HB monogram    -> RE email + Agent Hub
  hiring-2026-100526-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds two keyless BLS API v2 pulls made 10/05/26
(POST api.bls.gov/publicAPI/v2/timeseries/data/, startyear 2025, endyear 2026):
  bls-ces.json    CES0000000001         U.S. total nonfarm, thousands, SA
  bls-local.json  SMS06360840000000001  Oakland-Fremont-Berkeley metro division, SA
                  SMS06419400000000001  San Jose-Sunnyvale-Santa Clara metro area, SA
                  SMS06000000000000001  California, SA
Each is the raw API response; months are computed from the LEVELS (one vintage).

=============================================================================
VERIFICATION 10/05/26
=============================================================================
U.S. 2026 monthly changes: Jan +160, Feb -156, Mar +214, Apr +148, May +63,
Jun +31, Jul -10, Aug +133, Sep +29 (Aug and Sep preliminary). Every point
matches the supplied graphic, and they match the 10/03/26 pull behind
make-jobs-sept2026-chart.py. Dec 2025 to Sep 2026: 158,432 -> 159,044 =
+612K, an average of +68K a month.

Local panel, the same window for all four (Dec 2025 to Aug 2026, the latest
month published for states and metros; September arrives later in October):
  San Jose metro     1,165.0 -> 1,179.7   +14.7K   +1.26%
  California        18,062.5 -> 18,177.2  +114.7K  +0.64%
  United States    158,432   -> 159,015   +583K    +0.37%
  Oakland-Fremont-Berkeley 1,188.1 -> 1,188.6  +0.5K  +0.04%
The East Bay division fell in May (-2.9K) and June (-2.1K) and made it back in
July and August; it is essentially flat for the year.

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
STAMP = "100526"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
SLATE = "#6f8296"
PALE = "#a7b3c0"
GRID = "#d8cdb8"
MUTED = "#8a8172"
MINUS = "−"

US = "CES0000000001"
OAK, SJ, CA = "SMS06360840000000001", "SMS06419400000000001", "SMS06000000000000001"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]


def series(path):
    out = {}
    for s in json.load(open(path))["Results"]["series"]:
        out[s["seriesID"]] = {f'{x["year"]}-{x["period"][1:]}': Decimal(x["value"]) for x in s["data"]}
    return out


def k(v):
    v = int(v)
    return f"+{v}K" if v > 0 else (f"{MINUS}{abs(v)}K" if v < 0 else "0K")


def load():
    us = series(os.path.join(DATA, "bls-ces.json"))[US]
    loc = series(os.path.join(DATA, "bls-local.json"))
    keys = ["2025-12"] + [f"2026-{m:02d}" for m in range(1, 10)]
    chg = [int(us[keys[i]] - us[keys[i - 1]]) for i in range(1, len(keys))]
    assert chg == [160, -156, 214, 148, 63, 31, -10, 133, 29], chg
    ytd = us["2026-09"] - us["2025-12"]
    assert ytd == 612, ytd
    avg = ytd / 9
    assert avg.quantize(Decimal("1"), rounding=ROUND_HALF_UP) == 68, avg

    def window(ser):
        a, b = ser["2025-12"], ser["2026-08"]
        return b - a, (b / a - 1) * 100

    rows = [
        ("San Jose metro", *window(loc[SJ])),
        ("California", *window(loc[CA])),
        ("United States", *window(us)),
        ("Oakland, Fremont,\nBerkeley", *window(loc[OAK])),
    ]
    want = [("14.7", "1.26"), ("114.7", "0.64"), ("583", "0.37"), ("0.5", "0.04")]
    for (name, jobs, pct), (wj, wp) in zip(rows, want):
        assert jobs == Decimal(wj), (name, jobs)
        assert pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) == Decimal(wp), (name, pct)
    return chg, float(avg), rows


def jobs_label(name, jobs):
    n = int((jobs * 1000).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return f"+{n:,}"


def build():
    chg, avg, rows = load()
    print("U.S. 2026:", dict(zip(MONTHS, chg)), "avg", round(avg, 1))

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)

    # ---- left: the U.S. line ------------------------------------------------
    ax = fig.add_axes([0.075, 0.185, 0.555, 0.555])
    ax.set_facecolor(CREAM)
    x = list(range(len(chg)))
    ax.axhline(0, color=INK, lw=1.1, zorder=2)
    ax.axhline(avg, color=MUTED, lw=1.5, ls=(0, (6, 4)), zorder=2)
    # right end of the dashed line, past September, where the line never runs
    ax.text(len(chg) + 0.5, avg + 9, f"2026 average:\n+{round(avg)}K a month", fontsize=11,
            color=MUTED, ha="right", va="bottom", linespacing=1.15, zorder=6)
    ax.plot(x, chg, color=SLATE, lw=2.6, solid_joinstyle="round", zorder=3)
    lab_box = dict(boxstyle="square,pad=0.12", facecolor=CREAM, edgecolor="none")
    for i, v in enumerate(chg):
        last = i == len(chg) - 1
        ax.scatter([i], [v], s=95 if last else 46, color=CORAL if last else SLATE,
                   edgecolor=CREAM, linewidth=1.5 if last else 0, zorder=5)
        if last:
            continue
        # Apr, May and Jun sit on a falling stretch: centered labels would sit on the
        # incoming segment, so those three go just right of their point
        if MONTHS[i] in ("Apr", "May", "Jun"):
            ax.text(i + 0.12, v + 10, k(v), ha="left", va="bottom", fontsize=12,
                    fontweight="bold", color=INK, zorder=6, bbox=lab_box)
            continue
        up = v >= 0 and MONTHS[i] != "Jul"           # July sits just under zero: label below
        ax.text(i, v + (13 if up else -13), k(v), ha="center", va="bottom" if up else "top",
                fontsize=12, fontweight="bold", color=INK, zorder=6, bbox=lab_box)
    ax.annotate(k(chg[-1]), xy=(len(chg) - 1, chg[-1]), xytext=(18, 0), textcoords="offset points",
                fontsize=19, fontweight="bold", color="white", ha="left", va="center", zorder=7,
                bbox=dict(boxstyle="round,pad=0.35", facecolor=CORAL, edgecolor="none"))

    ax.set_xticks(x)
    ax.set_xticklabels(MONTHS, fontsize=12, color=MUTED)
    ax.get_xticklabels()[-1].set_color(DEEP)
    ax.get_xticklabels()[-1].set_fontweight("bold")
    yt = [-200, -100, 0, 100, 200]
    ax.set_yticks(yt)
    ax.set_yticklabels([k(v) for v in yt], fontsize=10.5, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.set_ylim(-215, 262)
    ax.set_xlim(-0.45, len(chg) + 0.55)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title("U.S. monthly change in payroll jobs, 2026", loc="left", fontsize=13,
                 fontweight="bold", color=INK, pad=14)

    # ---- right: the local panel ---------------------------------------------
    bx = fig.add_axes([0.745, 0.185, 0.20, 0.555])
    bx.set_facecolor(CREAM)
    names = [r[0] for r in rows]
    vals = [float(r[2]) for r in rows]
    ys = list(range(len(rows)))[::-1]
    cols = [SLATE, SLATE, SLATE, CORAL]
    bx.barh(ys, vals, height=0.56, color=cols, zorder=3)
    for yy, (name, jobs, pct), c in zip(ys, rows, cols):
        q = pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        bx.text(float(pct) + 0.04, yy + 0.07, f"+{q}%", ha="left", va="center", fontsize=13,
                fontweight="bold", color=DEEP if c == CORAL else INK, zorder=6)
        bx.text(float(pct) + 0.04, yy - 0.27, f"{jobs_label(name, jobs)} jobs", ha="left",
                va="center", fontsize=10.2, color=MUTED, zorder=6)
    bx.set_yticks(ys)
    bx.set_yticklabels(names, fontsize=11.5, color=INK, linespacing=1.1)
    bx.get_yticklabels()[-1].set_fontweight("bold")
    bx.get_yticklabels()[-1].set_color(DEEP)
    bx.set_xlim(0, 1.75)
    bx.set_ylim(-0.6, len(rows) - 0.35)
    bx.set_xticks([])
    bx.tick_params(axis="y", length=0, pad=8)
    bx.axvline(0, color=INK, lw=1.1, zorder=4)
    for sp in bx.spines.values():
        sp.set_visible(False)
    bx.set_title("Jobs added, Dec. to Aug.", loc="left", fontsize=13, fontweight="bold",
                 color=INK, pad=14, x=-0.62)

    fig.text(0.035, 0.955, "Hiring Is Stalling, and the East Bay Is Flat for the Year",
             fontsize=24, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.905, "Payroll jobs, seasonally adjusted",
             fontsize=13.5, color=MUTED, ha="left", va="top")

    fig.text(
        0.035, 0.083,
        "The U.S. has added 612,000 jobs this year through September. The Oakland, Fremont and Berkeley "
        "metro division added about 500 from December to August.",
        fontsize=10.8, color=DEEP, ha="left", va="bottom",
    )
    fig.text(0.035, 0.030,
             "Source: U.S. Bureau of Labor Statistics. U.S. data through September (released Oct. 2, 2026); "
             "state and metro data through August. Latest months preliminary.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"hiring-2026-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
