#!/usr/bin/env python3
"""
make-bayarea-paychecks-2026-chart.py  DATA_DIR  [outdir]

The 10/25/26 (Sunday) daily's Real Estate chart, the LOCAL answer to Market
Briefs' "Brick by brick" essay (AI is shifting work back to the trades; it
opens with "for decades, plumbers and electricians could buy a home and raise
a family"). No supplied graphic. This tests that line on our own market: what
the median Bay Area tradesperson and office worker earn, against the income it
takes to buy our five city median list price at today's rate.

Emits BOTH:
  paychecks-vs-home-102526.png      plain HB monogram    -> RE email + Agent Hub
  paychecks-vs-home-102526-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

=============================================================================
SOURCES AND METHOD
=============================================================================
DATA_DIR/oews-41860.json  BLS API v1 response for OEWS May 2025, area 0041860
  (San Francisco-Oakland-Fremont, CA metro), all industries, series
  OEUM0041860000000<SOC>13 (annual median wage) and ...01 (employment).
  Cross checked on 10/25/26 against data.bls.gov/oes/#/area/0041860/2025:
  electricians $92,830, software developers $186,640, office clerks $52,000,
  all occupations $74,260, identical.

DATA_DIR/live-inventory-102526.json  generate-live-inventory.js output for the
  102526 export: all.market.medianPrice = the five city (Fremont, Hayward,
  Milpitas, Newark, Union City) median list price of homes on the market.

Income needed = C.A.R.'s Traditional Housing Affordability Index method:
  20% down, 30-year fixed, taxes and insurance at 1.38% of price a year,
  payment (PITI) rounded to $10, income = payment x 12 / 0.30, to $100.
  VALIDATED 10/25/26 by reproducing C.A.R.'s published Q2 2026 rows at their
  6.54% composite rate (car.org/marketdata/data/haitraditional):
    CA SFH       $916,750   -> $5,710 / $228,400   (published $5,710 / $228,400)
    Alameda    $1,350,000   -> $8,410 / $336,400   (published $8,410 / $336,400)
    Santa Clara $2,050,000  -> $12,770 / $510,800  (published $12,770 / $510,800)
  asserted below, then applied at Mortgage News Daily's 7.33% (Oct. 23).

matplotlib only; build with python3.13 on Mac, from the workspace so
hb-logo-mark.png resolves.
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
STAMP = "102526"
RATE = 7.33          # MND 30-year, Oct. 23, 2026 (no weekend update)

CREAM = "#fdf6e8"
INK = "#1f2933"
GRID = "#d8cdb8"
MUTED = "#8a8172"
ORANGE = "#e8833a"   # skilled trades
SLATE = "#3d4f63"    # office and tech
GREY = "#b3a891"     # all jobs
CORAL = "#e2574c"    # income needed

# SOC code -> (label, group)
OCC = {
    "151252": ("Software developers", "office"),
    "472111": ("Electricians", "trade"),
    "472031": ("Carpenters", "trade"),
    "499021": ("HVAC mechanics", "trade"),
    "472152": ("Plumbers and pipefitters", "trade"),
    "000000": ("All jobs", "all"),
    "472061": ("Construction laborers", "trade"),
    "433031": ("Bookkeeping clerks", "office"),
    "514121": ("Welders", "trade"),
    "436014": ("Administrative assistants", "office"),
    "434051": ("Customer service reps", "office"),
    "439061": ("General office clerks", "office"),
}
COLOR = {"trade": ORANGE, "office": SLATE, "all": GREY}


def half_up(x, step):
    return int((Decimal(str(x)) / Decimal(step)).quantize(Decimal("1"), ROUND_HALF_UP)) * step


def pi_payment(loan, rate):
    r = rate / 100 / 12
    return loan * r / (1 - (1 + r) ** -360)


def car_income(price, rate):
    """C.A.R. HAI: (PITI to $10, minimum qualifying income to $100)."""
    piti = pi_payment(0.8 * price, rate) + price * 0.0138 / 12
    pay = half_up(piti, 10)
    return pay, half_up(pay * 12 / 0.30, 100)


def load_wages():
    d = json.load(open(os.path.join(DATA, "oews-41860.json")))
    assert d["status"] == "REQUEST_SUCCEEDED", d["status"]
    out = {}
    for s in d["Results"]["series"]:
        sid = s["seriesID"]
        assert sid.startswith("OEUM0041860000000"), sid
        soc, dtype = sid[17:23], sid[23:25]
        (pt,) = [x for x in s["data"] if x["year"] == "2025"]
        out.setdefault(soc, {})[dtype] = int(pt["value"])
    return out


def build():
    # 1. the method reproduces C.A.R.'s published Q2 2026 rows exactly
    assert car_income(916750, 6.54) == (5710, 228400)
    assert car_income(1350000, 6.54) == (8410, 336400)
    assert car_income(2050000, 6.54) == (12770, 510800)

    li = json.load(open(os.path.join(DATA, "live-inventory-102526.json")))
    assert li["date"] == "10/25/26", li["date"]
    price = li["all"]["market"]["medianPrice"]
    assert price == 1077000 and li["all"]["market"]["count"] == 616, li["all"]["market"]
    pay, need = car_income(price, RATE)
    assert (pay, need) == (7160, 286400), (pay, need)

    wages = load_wages()
    rows = [(OCC[soc][0], OCC[soc][1], wages[soc]["13"], wages[soc]["01"]) for soc in OCC]
    expected = {"Software developers": 186640, "Electricians": 92830, "Carpenters": 89200,
                "HVAC mechanics": 78490, "Plumbers and pipefitters": 77880, "All jobs": 74260,
                "Construction laborers": 72610, "Bookkeeping clerks": 65530, "Welders": 64320,
                "Administrative assistants": 62110, "Customer service reps": 57830,
                "General office clerks": 52000}
    assert {r[0]: r[2] for r in rows} == expected, rows
    rows.sort(key=lambda r: -r[2])
    assert [r[0] for r in rows] == list(expected), [r[0] for r in rows]
    # the copy's claims: no median paycheck shown clears the bar; the needed income
    # is about three times an electrician's; a developer earns about two thirds
    assert all(w < need for _, _, w, _ in rows)
    assert 2.95 < need / expected["Electricians"] < 3.15
    assert 0.62 < expected["Software developers"] / need < 0.68

    fig = plt.figure(figsize=(14.0, 8.8), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.205, 0.165, 0.615, 0.60])
    ax.set_facecolor(CREAM)

    n = len(rows)
    ys = list(range(n))[::-1]
    for y, (label, grp, w, _) in zip(ys, rows):
        c = COLOR[grp]
        ax.barh(y, w, height=0.64, color=c, zorder=3)
        ax.text(w + 3500, y, f"${w:,}", va="center", ha="left", fontsize=12.5,
                fontweight="bold", color=c, zorder=5)
        share = half_up(w / need * 100, 1)
        fig.text(0.905, 0.165 + 0.60 * (y + 0.5) / n, f"{share}%", ha="center",
                 va="center", fontsize=13, fontweight="bold" if grp != "all" else "normal",
                 color=INK if grp != "all" else MUTED)

    ax.axvline(need, color=CORAL, lw=2.6, ls=(0, (5, 3)), zorder=4)
    # below the top bar's label, in the open space right of the shorter bars
    ax.text(need - 4000, n - 1.55, f"Income needed\n${need:,} a year", ha="right",
            va="top", fontsize=13.5, fontweight="bold", color=CORAL, zorder=6,
            linespacing=1.25)
    ax.text(need - 4000, n - 2.95, f"to buy ${price:,} with 20% down\nat {RATE}%, "
            f"about ${pay:,} a month\nwith taxes and insurance", ha="right", va="top",
            fontsize=11.5, color=INK, zorder=6, linespacing=1.3)

    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows], fontsize=13, color=INK)
    for tick, (_, grp, _, _) in zip(ax.get_yticklabels(), rows):
        if grp == "all":
            tick.set_color(MUTED)
    ax.set_xlim(0, 300000)
    ax.set_ylim(-0.6, n - 0.4)
    ax.set_xticks([0, 50000, 100000, 150000, 200000, 250000, 300000])
    ax.set_xticklabels(["$0", "$50K", "$100K", "$150K", "$200K", "$250K", "$300K"],
                       fontsize=12, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=7)
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.905, 0.79, "Share of the\nincome needed", ha="center", va="bottom",
             fontsize=11.5, color=MUTED, linespacing=1.2)

    # legend chips
    fig.text(0.035, 0.815, "■", color=ORANGE, fontsize=18, ha="left", va="center")
    fig.text(0.053, 0.815, "Skilled trades", color=INK, fontsize=13.5, ha="left", va="center")
    fig.text(0.165, 0.815, "■", color=SLATE, fontsize=18, ha="left", va="center")
    fig.text(0.183, 0.815, "Office and tech", color=INK, fontsize=13.5, ha="left", va="center")
    fig.text(0.305, 0.815, "■", color=GREY, fontsize=18, ha="left", va="center")
    fig.text(0.323, 0.815, "All jobs", color=INK, fontsize=13.5, ha="left", va="center")

    title = fig.text(0.035, 0.955, "One Median Paycheck Won't Buy the Median Home",
                     fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.897, "Median yearly pay by job in the Bay Area against the income needed "
             f"to buy our five city median list price of ${price:,}", fontsize=14, color=MUTED,
             ha="left", va="top")
    fig.text(0.035, 0.035,
             "Source: BLS Occupational Employment and Wage Statistics, May 2025, San Francisco, "
             "Oakland and Fremont metro, annual median wages. Income needed uses the C.A.R.\n"
             f"affordability method (20% down, 30-year fixed at {RATE}% from Mortgage News Daily "
             "Oct. 23, taxes and insurance at 1.38% of price a year, payment at 30% of gross\n"
             "income) on the median list price of homes on the market in Fremont, Hayward, "
             "Milpitas, Newark and Union City, our Bay East MLS export of Oct. 25, 2026.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.45)

    # the -hb wordmark sits top right: the title must end well before it
    fig.canvas.draw()
    bb = title.get_window_extent(renderer=fig.canvas.get_renderer())
    assert bb.x1 < 0.84 * fig.get_size_inches()[0] * fig.dpi, bb.x1
    return fig, rows, price, pay, need


if __name__ == "__main__":
    fig, rows, price, pay, need = build()
    out = os.path.join(OUTDIR, f"paychecks-vs-home-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    print(f"five city median ${price:,}: payment ${pay:,}/mo, income needed ${need:,}")
    for label, grp, w, emp in rows:
        print(f"  {label:26s} {grp:6s} ${w:>8,}  {w / need * 100:5.1f}%  ({emp:,} jobs)")
    print("wrote", out)
