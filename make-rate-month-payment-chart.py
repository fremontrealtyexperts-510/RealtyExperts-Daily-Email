#!/usr/bin/env python3
"""
make-rate-month-payment-chart.py  DATA_DIR  [outdir]

The 10/09/26 daily's mortgage rate chart (Real Estate section). Harv attached
the newsletter graphic "Mortgage Rates Jump to 7.5%" (MND 30-year fixed, daily,
Sep. 8 to Oct. 8, 2026; 6.89% to 7.50%; "Source: Mortgage News Daily rate
index, as of Oct. 8, 2026") and asked for something new on a story the report
has told many times, without going overboard. Our twist: the same line, read
in dollars, as the monthly payment on the five city median home. Emits BOTH:

  rate-month-payment-100926.png      plain HB monogram    -> RE email + Agent Hub
  rate-month-payment-100926-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds mnd.html, the saved page mortgagenewsdaily.com/mortgage-rates/mnd
(fetched Oct. 9, 2026 8:41 AM PT). Its history table carries the 30-year daily
index for Sept. 9 to Oct. 8; Sept. 8 comes from the same page's "1 month"
change (+0.61 from 7.50%), and matches our own 09/09/26 report (6.89%).

=============================================================================
VERIFICATION 10/09/26
=============================================================================
Every point on the supplied line matches MND's table: 6.89, 6.97, 7.07, 7.12,
7.17, 7.22, 7.24, 7.19, 7.20, 7.19, 7.17, 7.26, 7.45, 7.43, 7.50, 7.58, 7.60,
7.54, 7.57, 7.61, 7.56, 7.59, 7.50. The supplied title says rates "jump" to
7.5%; Thursday's 7.50% was a 0.09 point DROP from 7.59%, MND's biggest one day
drop in three months. The month high is 7.61% on Oct. 5, which is also MND's
52 week high.

Payment: principal and interest, 30-year fixed, 20% down, on $1,075,000, the
median list price of the 615 homes on the market across Fremont, Hayward,
Milpitas, Newark and Union City in our Oct. 9 MLS export (live-inventory.json
all.market.medianPrice). Loan $860,000: 6.89% = $5,658, 7.50% = $6,013, a
difference of $355 a month. Put the other way: the Sept. 8 payment
($5,658.21) borrows $809,224 at 7.50%, about $51,000 (5.9%) less than $860,000.

matplotlib; build with python3.13 on Mac.
"""
import os
import re
import sys
from datetime import date
from decimal import Decimal, ROUND_HALF_UP, getcontext

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

getcontext().prec = 40

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "100926"
MEDIAN = Decimal("1075000")      # five city on market median list price, Oct. 9 export
DOWN = Decimal("0.20")

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e05a47"
DEEP = "#b8432f"
BLUE = "#2b6cb0"
BLUE_D = "#1e4e8c"
GRID = "#d8cdb8"
MUTED = "#8a8172"

AP_MONTHS = ["Jan.", "Feb.", "March", "April", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."]


def ap(d):
    return f"{AP_MONTHS[d.month - 1]} {d.day}"


def factor(rate):
    r = rate / Decimal(1200)
    return r / (1 - (1 + r) ** -360)


def payment(rate, exact=False):
    p = MEDIAN * (1 - DOWN) * factor(rate)
    return p if exact else p.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def load():
    t = open(os.path.join(DATA, "mnd.html"), errors="ignore").read()
    rows = re.findall(r'<tr>\s*<td>(\d+)/(\d+)/(\d{4})</td>(.*?)</tr>', t, re.S)
    ser = []
    for m, d, y, body in rows:
        vals = re.findall(r'class="text-center rate" title="([0-9.]+)%"', body)
        ser.append((date(int(y), int(m), int(d)), Decimal(vals[0])))
    ser.sort()
    # Sept. 8 from the page's own 1 month change on the 30-year row
    summ = re.sub(r"<[^>]+>", " ", t)
    summ = re.sub(r"\s+", " ", summ)
    m = re.search(r"30 Yr\. Fixed ([0-9.]+)% ([+\-&#x2B;0-9.]+)% ([+\-&#x2B;0-9.]+)% ([+\-&#x2B;0-9.]+)%", summ)
    cur, one_month = Decimal(m.group(1)), Decimal(m.group(4).replace("&#x2B;", ""))
    assert ser[-1] == (date(2026, 10, 8), cur), (ser[-1], cur)
    assert ser[0][0] == date(2026, 9, 9), ser[0]
    ser.insert(0, (date(2026, 9, 8), cur - one_month))

    want = ["6.89", "6.97", "7.07", "7.12", "7.17", "7.22", "7.24", "7.19", "7.20", "7.19", "7.17",
            "7.26", "7.45", "7.43", "7.50", "7.58", "7.60", "7.54", "7.57", "7.61", "7.56", "7.59", "7.50"]
    assert [str(v) for _, v in ser] == want, [str(v) for _, v in ser]
    return ser


def build():
    ser = load()
    x = list(range(len(ser)))
    y = [float(v) for _, v in ser]
    d0, r0 = ser[0]
    d1, r1 = ser[-1]
    p0, p1 = payment(r0), payment(r1)
    assert (p0, p1) == (Decimal("5658"), Decimal("6013")), (p0, p1)
    # the Sept. 8 payment, borrowed at today's rate
    less = MEDIAN * (1 - DOWN) - payment(r0, exact=True) / factor(r1)
    assert Decimal("50500") < less < Decimal("51000"), less          # 50,776
    less_k = int((less / 1000).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    hi = max(range(len(ser)), key=lambda i: ser[i][1])
    assert ser[hi] == (date(2026, 10, 5), Decimal("7.61"))

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.17, 0.80, 0.62])
    ax.set_facecolor(CREAM)

    ax.fill_between(x, y, 6.6, color="#d3e2f2", alpha=0.75, lw=0, zorder=1)
    ax.plot(x, y, color=BLUE, lw=3.2, solid_joinstyle="round", zorder=4)

    # start
    ax.scatter([0], [y[0]], s=130, color=CREAM, edgecolor=BLUE, linewidth=2.6, zorder=6)
    ax.annotate(f"{r0}%", xy=(0, y[0]), xytext=(14, -2), textcoords="offset points",
                fontsize=22, fontweight="bold", color=BLUE_D, ha="left", va="top", zorder=7)
    ax.annotate(f"${p0:,} a month", xy=(0, y[0]), xytext=(15, -38), textcoords="offset points",
                fontsize=14, color=INK, ha="left", va="top", zorder=7)

    # month high
    ax.scatter([hi], [y[hi]], s=60, color=BLUE, edgecolor=CREAM, linewidth=1.5, zorder=6)
    ax.annotate(f"High: {ser[hi][1]}%, {ap(ser[hi][0])}", xy=(hi, y[hi]), xytext=(0, 12),
                textcoords="offset points", fontsize=12, color=BLUE_D, ha="center", va="bottom", zorder=7)

    # end
    ax.scatter([x[-1]], [y[-1]], s=150, color=CORAL, edgecolor=CREAM, linewidth=2, zorder=7)
    ax.annotate(f"{r1}%", xy=(x[-1], y[-1]), xytext=(16, 0), textcoords="offset points",
                fontsize=22, fontweight="bold", color="white", ha="left", va="center", zorder=8,
                bbox=dict(boxstyle="round,pad=0.32", facecolor=CORAL, edgecolor="none"))
    ax.annotate(f"${p1:,} a month", xy=(x[-1], y[-1]), xytext=(18, -34), textcoords="offset points",
                fontsize=14, color=INK, ha="left", va="top", zorder=8)

    # the takeaway, in the open space under the line
    ax.text(12.9, 6.98, f"+${p1 - p0:,} a month", fontsize=30, fontweight="bold", color=DEEP,
            ha="left", va="bottom", zorder=7)
    ax.text(12.95, 6.955, f"for the same home in four weeks. Put another\n"
            f"way, the Sept. 8 payment of ${p0:,} now\nborrows about ${less_k},000 less.",
            fontsize=13.5, color=INK, ha="left", va="top", linespacing=1.3, zorder=7)

    ticks = [i for i, (d, _) in enumerate(ser) if d.weekday() == 1]     # Tuesdays, as on the source
    ax.set_xticks(ticks)
    ax.set_xticklabels([ap(ser[i][0]) for i in ticks], fontsize=12, color=MUTED)
    ax.set_xlim(-0.8, len(ser) + 2.6)
    ax.set_ylim(6.6, 7.8)
    ax.set_yticks([6.75, 7.0, 7.25, 7.5, 7.75])
    ax.set_yticklabels(["6.75%", "7.00%", "7.25%", "7.50%", "7.75%"], fontsize=11.5, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.035, 0.955, "A Month of Mortgage Rates, in Dollars", fontsize=26, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.895,
             "30-year fixed rate, daily, Sept. 8 to Oct. 8, 2026, and the monthly payment "
             "on the five city median home",
             fontsize=13.2, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.070,
             f"Payment: principal and interest on ${MEDIAN:,}, the median list price of homes on the market in "
             "Fremont, Hayward, Milpitas, Newark and Union City\n(our Oct. 9 MLS export), with 20% down. "
             "Source: Mortgage News Daily daily rate index, as of Oct. 8, 2026.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.4)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"rate-month-payment-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
