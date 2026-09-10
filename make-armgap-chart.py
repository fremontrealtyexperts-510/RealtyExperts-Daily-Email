#!/usr/bin/env python3
"""
make-armgap-chart.py  [outdir]

Recreates the newsletter graphic "ARMs Now Cost A Full Point Less" for the
09/10/26 edition, plus the local answer (feedback-localize-national-studies).
Emits BOTH brand variants:

  armgap-091026.png      plain monogram    -> RE email + Agent Hub
  armgap-091026-hb.png   + wordmark        -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/10/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

All three supplied values match MBA's Weekly Applications Survey release of
September 9, 2026 (week ending September 4), read verbatim in the Browser pane
(mba.org returns 403 to curl and WebFetch):

  30-year fixed, conforming ($832,750 or less): 6.85% (from 6.79%), 0.67 points
  15-year fixed:                                6.17% (from 6.14%), 0.93 points
  5/1 ARM:                                      5.82% (from 5.94%), 0.84 points
  ARM share of applications: 8.5%, "the highest share since June"

Headline: 6.85 minus 5.82 is 1.03 points. TRUE for the conforming 30-year.

WHAT THE ORIGINAL LEAVES OUT, and why it matters here
------------------------------------------------------
Fremont's median on market list price (09/10/26 MLS export, live-inventory.json)
is $1,223,888. A 20% down loan on it is $979,110, ABOVE MBA's $832,750
conforming line, so the like for like fixed rate is MBA's JUMBO 30-year:
6.74% (from 6.76%), 0.63 points. The local gap is 0.92 points, not a full
point. Added as its own bar, same release, same week.

Right panel: principal and interest on that loan, 30 year amortization for
both (a 5/1 ARM amortizes over 30 years; only its rate is fixed for five).
Method check: the same formula gives $599.55 on $100,000 at 6% for 30 years,
the textbook value, asserted below before anything is drawn.

matplotlib only; build with python3.13 on Mac.
"""
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "091026"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
RUST = "#c8692f"
BLUE = "#2f6db5"
SLATE = "#8a9aa8"
GRID = "#d8cdb8"
MUTED = "#8a8172"

# label, rate %, colour (MBA release of 09/09/26, week ending 09/04/26)
RATES = [
    ("30-year fixed\nup to \\$832,750", Decimal("6.85"), CORAL),
    ("30-year fixed, jumbo\nabove \\$832,750", Decimal("6.74"), RUST),
    ("15-year fixed", Decimal("6.17"), SLATE),
    ("5/1 ARM", Decimal("5.82"), BLUE),
]
ARM = RATES[3][1]
JUMBO = RATES[1][1]

FREMONT_MEDIAN = Decimal("1223888")   # live-inventory.json, Fremont market.medianPrice, 09/10/26
DOWN = Decimal("0.20")


def payment(principal, annual_pct, years=30):
    r = Decimal(annual_pct) / Decimal(100) / Decimal(12)
    n = years * 12
    pay = Decimal(principal) * r / (1 - (1 + r) ** -n)
    return pay.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def dollars(x):
    return f"{Decimal(x).quantize(Decimal('1'), rounding=ROUND_HALF_UP):,}"


assert payment(100000, 6) == Decimal("599.55"), payment(100000, 6)

LOAN = (FREMONT_MEDIAN * (1 - DOWN)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
PAY_FIX = payment(LOAN, JUMBO)
PAY_ARM = payment(LOAN, ARM)
DIFF = PAY_FIX - PAY_ARM
FIVE_YR = (DIFF * 60 / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * 100   # nearest $100


def build():
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)

    # Left: the four MBA rates
    axl = fig.add_axes((0.205, 0.285, 0.395, 0.435))
    axl.set_facecolor(CREAM)
    ys = list(range(len(RATES)))[::-1]
    for y, (lab, rate, col) in zip(ys, RATES):
        axl.barh(y, float(rate), height=0.62, color=col, zorder=3)
        axl.text(float(rate) + 0.12, y, f"{rate}%", ha="left", va="center",
                 fontsize=17, fontweight="bold", color=col if col != SLATE else INK, zorder=5)
        if lab.startswith("30-year"):   # inside the bar: outside, it collides with the value label
            axl.text(float(rate) - 0.18, y, f"{rate - ARM} points above the ARM", ha="right", va="center",
                     fontsize=11, fontweight="bold", color="white", zorder=5)
    axl.set_yticks(ys)
    axl.set_yticklabels([r[0] for r in RATES], fontsize=12.5, fontweight="bold", linespacing=1.3)
    axl.set_xlim(0, 9.4)
    axl.set_ylim(-0.6, len(RATES) - 0.4)
    axl.set_xticks([])
    for s in ("top", "right", "bottom"):
        axl.spines[s].set_visible(False)
    axl.spines["left"].set_color(GRID)
    axl.tick_params(axis="y", length=0, colors=SLATE)
    for lbl in axl.get_yticklabels():   # after tick_params, which resets colours
        lbl.set_color(INK)
    axl.text(0, 1.10, "National average rates", transform=axl.transAxes,
             fontsize=14, fontweight="bold", color=INK, ha="left", va="bottom")
    axl.text(0, 1.03, "MBA survey, 80% loan to value", transform=axl.transAxes,
             fontsize=11, color=MUTED, ha="left", va="bottom")

    # Right: what the local gap is worth
    axr = fig.add_axes((0.705, 0.285, 0.255, 0.435))
    axr.set_facecolor(CREAM)
    pays = [PAY_FIX, PAY_ARM]
    cols = [RUST, BLUE]
    for x, (p, col) in enumerate(zip(pays, cols)):
        axr.bar(x, float(p), width=0.58, color=col, zorder=3)
        axr.text(x, float(p) - 260, f"\\${dollars(p)}", ha="center", va="top",
                 fontsize=15, fontweight="bold", color="white", zorder=5)
    axr.plot([-0.29, 1.29], [float(PAY_FIX)] * 2, color=MUTED, linewidth=1.0,
             linestyle=(0, (4, 3)), zorder=4)
    axr.bar(1, float(DIFF), bottom=float(PAY_ARM), width=0.58, color=BLUE, alpha=0.16,
            edgecolor=BLUE, linewidth=1.0, linestyle=(0, (3, 2)), zorder=3)   # the saving, drawn
    axr.text(1, float(PAY_FIX) + 170, f"\\${dollars(DIFF)} less\na month", ha="center", va="bottom",
             fontsize=13, fontweight="bold", color=BLUE, linespacing=1.25, zorder=5)
    axr.set_xticks([0, 1])
    axr.set_xticklabels([f"30-year jumbo\n{JUMBO}%", f"5/1 ARM\n{ARM}%"],
                        fontsize=12, fontweight="bold", linespacing=1.3)
    axr.set_xlim(-0.6, 1.6)
    axr.set_ylim(0, float(PAY_FIX) * 1.30)
    axr.set_yticks([])
    for s in ("top", "right", "left"):
        axr.spines[s].set_visible(False)
    axr.spines["bottom"].set_color(GRID)
    axr.tick_params(axis="x", length=0, colors=SLATE)
    for lbl in axr.get_xticklabels():
        lbl.set_color(INK)
    axr.text(-0.08, 1.10, "On a typical Fremont loan", transform=axr.transAxes,
             fontsize=14, fontweight="bold", color=INK, ha="left", va="bottom")
    axr.text(-0.08, 1.03, f"Principal and interest on \\${dollars(LOAN)}", transform=axr.transAxes,
             fontsize=11, color=MUTED, ha="left", va="bottom")

    fig.text(0.045, 0.945, "ARMs Now Cost a Full Point Less",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888,
             "Average contract rates, week ending September 4, 2026, and what the gap is worth in Fremont",
             fontsize=14, color=MUTED, ha="left", va="top")

    fig.text(
        0.045, 0.118,
        f"At Fremont prices the loan is jumbo, where the fixed rate is {JUMBO}%, so the local gap is {JUMBO - ARM} points: about \\${dollars(DIFF)} a month,\n"
        f"roughly \\${dollars(FIVE_YR)} over the five years the ARM rate is locked. After that it adjusts every year with the market.",
        fontsize=11.5, color=DEEP, ha="left", va="bottom", linespacing=1.55,
    )
    fig.text(
        0.045, 0.040,
        "Source: Mortgage Bankers Association Weekly Applications Survey, released September 9, 2026. Points: 0.67 (30-year), 0.63 (jumbo), 0.93 (15-year),\n"
        f"0.84 (ARM). Loan is 20% down on Fremont's \\${dollars(FREMONT_MEDIAN)} median list price, September 10 MLS. Principal and interest only, 30 year amortization.",
        fontsize=10.5, color=MUTED, ha="left", va="bottom", linespacing=1.5,
    )
    return fig


if __name__ == "__main__":
    print(f"loan ${dollars(LOAN)}  fixed {JUMBO}% ${PAY_FIX}  arm {ARM}% ${PAY_ARM}  diff ${DIFF}  5yr ${FIVE_YR}")
    print(f"conforming check: 6.85% -> ${payment(LOAN, Decimal('6.85'))}")
    fig = build()
    out = os.path.join(OUTDIR, f"armgap-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
