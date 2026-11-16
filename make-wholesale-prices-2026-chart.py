"""
make-wholesale-prices-2026-chart.py  BLS_JSON  [outdir]

The 11/16/26 daily's Economy chart. Harv supplied "Wholesale Inflation Near a
4-Year High" (PPI final demand, change from a year earlier, NSA, Oct. 2025 2.8%
to Oct. 2026 6.5%). Rebuilt as OUR chart from the BLS series, plus a housing
line the graphic did not carry: inputs to residential construction (goods),
i.e. what home builders pay for materials.

Emits BOTH:
  wholesale-prices-111626.png      plain HB monogram    -> RE email + Agent Hub
  wholesale-prices-111626-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

BLS_JSON = BLS API v1 POST {"seriesid":["WPUFD4","WPUIP2311001"],"startyear":"2020","endyear":"2026"}

=============================================================================
VERIFICATION 11/16/26
=============================================================================
* All 13 points of the supplied graphic equal the year-over-year change of
  WPUFD4 (PPI final demand, NSA) rounded to one decimal: 2.8, 3.1, 3.1, 3.1,
  3.4, 4.3, 5.7, 5.9, 5.6, 4.9, 5.5, 6.3, 6.5. Oct. 2026 index 160.248 vs
  150.439 = +6.52%.
* The last month at or above 6.52% was Nov. 2022 (7.4%), so "near a 4-year
  high" holds (3 years 11 months).
* WPUIP2311001 (inputs to residential construction, goods, NSA): Oct. 2026
  355.005 vs 323.182 = +9.85%, also the fastest since Nov. 2022 (11.8%).
  Both series started the window at 2.8% (Oct. 2025: 2.84% and 2.82%).
* July to October 2026 carry BLS's "P" (preliminary) footnote.

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

SRC = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "111626"

CREAM = "#fdf6e8"
INK = "#1f2933"
RED = "#c8102e"
ORANGE = "#d9771f"
GRID = "#e6dcc8"
MUTED = "#8a8172"

MONTHS = [("2025", "M10"), ("2025", "M11"), ("2025", "M12")] + [("2026", "M%02d" % m) for m in range(1, 11)]
GRAPHIC = ["2.8", "3.1", "3.1", "3.1", "3.4", "4.3", "5.7", "5.9", "5.6", "4.9", "5.5", "6.3", "6.5"]


def q1(x):
    return x.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def load():
    d = json.load(open(SRC))
    assert d["status"] == "REQUEST_SUCCEEDED", d["status"]
    out = {}
    for s in d["Results"]["series"]:
        idx = {(r["year"], r["period"]): Decimal(r["value"]) for r in s["data"]
               if r["period"] != "M13" and r["value"] != "-"}
        prelim = {(r["year"], r["period"]) for r in s["data"]
                  if any((f or {}).get("code") == "P" for f in r.get("footnotes", []))}
        yoy = {k: (v / idx[(str(int(k[0]) - 1), k[1])] - 1) * 100
               for k, v in idx.items() if (str(int(k[0]) - 1), k[1]) in idx}
        out[s["seriesID"]] = (idx, yoy, prelim)
    fd_idx, fd, fd_p = out["WPUFD4"]
    rc_idx, rc, rc_p = out["WPUIP2311001"]
    # the supplied graphic, point for point
    assert [str(q1(fd[k])) for k in MONTHS] == GRAPHIC, [str(q1(fd[k])) for k in MONTHS]
    assert (fd_idx[("2026", "M10")], fd_idx[("2025", "M10")]) == (Decimal("160.248"), Decimal("150.439"))
    assert (rc_idx[("2026", "M10")], rc_idx[("2025", "M10")]) == (Decimal("355.005"), Decimal("323.182"))
    assert str(q1(rc[("2026", "M10")])) == "9.8", rc[("2026", "M10")]
    for yo in (fd, rc):   # last month at or above today's pace = Nov. 2022
        last = yo[("2026", "M10")]
        before = sorted(k for k in yo if k < ("2026", "M10") and yo[k] >= last)
        assert before[-1] == ("2022", "M11"), before[-1]
    assert str(q1(fd[("2022", "M11")])) == "7.4" and str(q1(rc[("2022", "M11")])) == "11.8"
    assert {("2026", "M%02d" % m) for m in (7, 8, 9, 10)} <= fd_p & rc_p, (fd_p, rc_p)
    return [float(fd[k]) for k in MONTHS], [float(rc[k]) for k in MONTHS]


def build():
    fd, rc = load()
    xs = list(range(len(MONTHS)))
    fig = plt.figure(figsize=(14.0, 7.8), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.15, 0.70, 0.66])
    ax.set_facecolor(CREAM)

    for g in (2, 4, 6, 8, 10):
        ax.axhline(g, color=GRID, lw=1, zorder=1, ls=(0, (4, 4)))
        ax.text(-0.35, g, f"{g}%", ha="right", va="center", fontsize=13, color=MUTED)
    ax.fill_between(xs, 2, fd, color=RED, alpha=0.07, lw=0, zorder=2)
    ax.plot(xs, rc, color=ORANGE, lw=3.0, zorder=4)
    ax.plot(xs, fd, color=RED, lw=3.0, zorder=5)
    ax.plot([0], [fd[0]], marker="o", ms=10, color=INK, zorder=6)
    ax.text(-0.05, 3.75, "Both 2.8%\nin Oct. 2025", fontsize=12.5, color=INK, ha="left", va="bottom",
            linespacing=1.15)

    end = xs[-1]
    ax.plot([end], [rc[-1]], marker="o", ms=12, color=ORANGE, zorder=7)
    ax.plot([end], [fd[-1]], marker="o", ms=12, color=RED, zorder=7)
    lx = end + 0.45
    ax.text(lx, rc[-1] + 0.05, "9.8%", fontsize=26, fontweight="bold", color=ORANGE, ha="left", va="center")
    ax.text(lx, rc[-1] - 0.85, "Materials for\nhome building", fontsize=12.5, color=INK, ha="left", va="center",
            linespacing=1.15)
    ax.text(lx, fd[-1] + 0.05, "6.5%", fontsize=26, fontweight="bold", color=RED, ha="left", va="center")
    ax.text(lx, fd[-1] - 0.85, "All wholesale prices\n(final demand)", fontsize=12.5, color=INK, ha="left",
            va="center", linespacing=1.15)

    labels = ["Oct\n2025", "Nov", "Dec", "Jan\n2026", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"]
    ax.set_xticks(xs)
    ax.set_xticklabels(labels)
    ax.tick_params(axis="x", length=0, labelsize=13, pad=8)
    for t in ax.get_xticklabels():
        t.set_color(INK)
    ax.yaxis.set_visible(False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlim(-0.4, len(xs) - 0.6)
    ax.set_ylim(1.6, 10.9)
    ax.set_clip_on(False)

    fig.text(0.035, 0.955, "Wholesale Prices Near a 4-Year High", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.897, "Producer Price Index, change from a year earlier, not seasonally adjusted. "
             "Both lines are the fastest since November 2022.", fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.03, "Source: U.S. Bureau of Labor Statistics, PPI final demand and inputs to residential "
             "construction (goods); July to October 2026 are preliminary.", fontsize=10.2, color=MUTED,
             ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"wholesale-prices-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
