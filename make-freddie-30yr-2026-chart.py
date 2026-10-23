#!/usr/bin/env python3
"""
make-freddie-30yr-2026-chart.py  DATA_DIR  [outdir]

The 10/23/26 daily's Real Estate chart. Harv attached the newsletter's
"Mortgage Rates Climb Past 7%" graphic: Freddie Mac average 30-year fixed,
2026, from a 6.09% start to a 7.40% end pill. Emits BOTH:

  freddie-30yr-102326.png      plain HB monogram    -> RE email + Agent Hub
  freddie-30yr-102326-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds pmms_history.csv, Freddie Mac's Primary Mortgage Market Survey
history (freddiemac.com/pmms/docs/PMMS_history.csv), fetched Oct. 23, 2026,
through the Oct. 22, 2026 release.

=============================================================================
VERIFICATION 10/23/26
=============================================================================
* The graphic's first point, 6.09%, is the Jan. 22 reading, NOT the start of
  2026 (Jan. 8 was 6.16%, Jan. 15 6.06%; Dec. 31, 2025 was 6.15%). Its 7.40%
  end is Oct. 8 AND Oct. 15. It is one week stale: Freddie's Oct. 22 release
  is 7.32%, the first weekly decline since Aug. 20.
* 2026 low 5.98% on Feb. 26. A year earlier (Oct. 23, 2025) 6.19%.
* Payment column: our five city median list price, $1,080,000 (live ledger
  Oct. 23, 2026), 20% down, 30-year principal and interest.

matplotlib; build with python3.13 on Mac.
"""
import csv
import os
import sys
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "102326"
MEDIAN = 1_080_000

CREAM = "#fdf6e8"
INK = "#1f2933"
RED = "#d6363c"
DEEP = "#a8232a"
FILL = "#f6d9cf"
GRID = "#d8cdb8"
MUTED = "#8a8172"
GREEN = "#2f7d4f"


def payment(price, rate):
    loan = Decimal(price) * Decimal("0.8")
    m = Decimal(str(rate)) / Decimal(1200)
    p = loan * m / (1 - (1 + m) ** -360)
    return int(p.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def load():
    s = {}
    for r in csv.DictReader(open(os.path.join(DATA, "pmms_history.csv"))):
        if r["pmms30"].strip():
            s[datetime.strptime(r["date"], "%m/%d/%Y").date()] = float(r["pmms30"])
    ser = sorted((k, v) for k, v in s.items() if date(2025, 12, 31) <= k <= date(2026, 10, 22))
    assert ser[0] == (date(2025, 12, 31), 6.15) and ser[-1] == (date(2026, 10, 22), 7.32), (ser[0], ser[-1])
    assert s[date(2026, 1, 22)] == 6.09 and s[date(2026, 10, 15)] == 7.40 == s[date(2026, 10, 8)]
    y26 = [t for t in ser if t[0].year == 2026]
    lo = min(y26, key=lambda t: t[1])
    assert lo == (date(2026, 2, 26), 5.98), lo
    assert s[date(2025, 10, 23)] == 6.19
    # last weekly decline before Oct. 22
    prev = [(a, b) for a, b in zip(ser, ser[1:]) if b[1] < a[1] and b[0] < date(2026, 10, 22)]
    assert prev[-1][1][0] == date(2026, 8, 20), prev[-1]
    return ser, lo, s[date(2025, 10, 23)]


def build():
    ser, lo, yr_ago = load()
    xs = [datetime(k.year, k.month, k.day) for k, _ in ser]
    ys = [v for _, v in ser]
    start, last = ys[0], ys[-1]
    pay_now, pay_low = payment(MEDIAN, last), payment(MEDIAN, lo[1])
    assert (pay_now, pay_low) == (5935, 5169), (pay_now, pay_low)

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.065, 0.12, 0.72, 0.69])
    ax.set_facecolor(CREAM)

    FLOOR = 5.75
    ax.fill_between(xs, FLOOR, ys, color=FILL, lw=0, zorder=1, alpha=0.85)
    ax.plot(xs, ys, color=RED, lw=2.8, solid_joinstyle="round", zorder=4)
    ax.axhline(7.0, color="#b9ad93", lw=1.3, ls=(0, (4, 4)), zorder=2)
    ax.text(datetime(2026, 1, 3), 7.03, "7%", fontsize=12, color=MUTED, va="bottom")

    ax.scatter([xs[0]], [start], s=70, color=CREAM, edgecolor=RED, linewidth=2.2, zorder=5)
    ax.annotate(f"Dec. 31: {start:.2f}%", xy=(xs[0], start), xytext=(4, 16),
                textcoords="offset points", fontsize=13, fontweight="bold", color=INK, ha="left")

    lx = datetime(lo[0].year, lo[0].month, lo[0].day)
    ax.scatter([lx], [lo[1]], s=55, color=DEEP, edgecolor=CREAM, linewidth=1.5, zorder=5)
    ax.annotate(f"2026 low: {lo[1]:.2f}%\n(Feb. 26)", xy=(lx, lo[1]), xytext=(0, -14),
                textcoords="offset points", fontsize=12, color=DEEP, ha="center", va="top")

    px = datetime(2026, 10, 15)
    ax.annotate("Peak 7.40%\n(Oct. 8 and 15)", xy=(px, 7.40), xytext=(-14, 10),
                textcoords="offset points", fontsize=12, color=INK, ha="right", va="bottom")

    fx = xs[-1]
    ax.scatter([fx], [last], s=130, color=DEEP, edgecolor=CREAM, linewidth=2, zorder=7)
    ax.annotate(f"Oct. 22: {last:.2f}%", xy=(fx, last), xytext=(-6, -34), textcoords="offset points",
                fontsize=16, fontweight="bold", color="white", ha="right", va="top", zorder=8,
                bbox=dict(boxstyle="round,pad=0.38", facecolor=DEEP, edgecolor="none"))

    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b."))
    ax.set_xlim(datetime(2025, 12, 24), datetime(2026, 10, 31))
    ax.set_ylim(FLOOR, 7.72)
    ax.set_yticks([6.0, 6.5, 7.0, 7.5])
    ax.set_yticklabels(["6.0%", "6.5%", "7.0%", "7.5%"], fontsize=12.5, color=MUTED)
    ax.tick_params(axis="x", labelsize=12.5, colors=MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.815, 0.70, "A year ago", fontsize=13, color=MUTED, ha="left", va="top")
    fig.text(0.815, 0.665, f"{yr_ago:.2f}%", fontsize=27, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.815, 0.55, "Payment on our\nfive city median*", fontsize=13, color=MUTED, ha="left",
             va="top", linespacing=1.3)
    fig.text(0.815, 0.47, f"${pay_now:,}", fontsize=27, fontweight="bold", color=DEEP, ha="left", va="top")
    fig.text(0.815, 0.405, f"at {last:.2f}%", fontsize=11.5, color=MUTED, ha="left", va="top")
    fig.text(0.815, 0.355, f"${pay_low:,}", fontsize=22, fontweight="bold", color=GREEN, ha="left", va="top")
    fig.text(0.815, 0.30, f"at February's {lo[1]:.2f}%", fontsize=11.5, color=MUTED, ha="left", va="top")

    fig.text(0.035, 0.955, "Mortgage Rates Topped 7.4%, Then Eased", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895, "Freddie Mac average 30-year fixed rate, weekly, Dec. 31, 2025 through Oct. 22, 2026.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035,
             "Source: Freddie Mac Primary Mortgage Market Survey. *$1,080,000 median list price across Fremont, "
             "Hayward, Milpitas, Newark and Union City, 20% down, principal and interest.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"freddie-30yr-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
