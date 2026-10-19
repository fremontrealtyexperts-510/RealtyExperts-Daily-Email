#!/usr/bin/env python3
"""
make-net-interest-2026-chart.py  MTS9_JSON  [outdir]

Recreation of "America's Interest Bill Tops $1 Trillion" graphic Harv supplied
for the 10/19/26 daily. Goes in the Economy section. Emits BOTH:

  net-interest-101926.png      plain HB monogram    -> RE email + Agent Hub
  net-interest-101926-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

MTS9_JSON is the Fiscal Data API pull of Monthly Treasury Statement Table 9 for
each Sept. 30 record date, FY2016 to FY2026 (fetched Oct. 19, 2026 1:35 PM PT):
  api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/mts/mts_table_9
  ?filter=record_date:in:(2016-09-30,...,2026-09-30)
Net interest = classification "Net Interest" (src line 31). Receipts = "Total"
src line 12. Values are current_fytd_rcpt_outly_amt (full fiscal year).

=============================================================================
VERIFICATION 10/19/26 (MTS vs the supplied graphic, $B)
=============================================================================
  FY   MTS      graphic        FY   MTS      graphic
  16   240.7    240 (241)      22   475.1    475
  17   262.8    263            23   659.2    659
  18   324.7    325            24   881.7    882
  19   375.6    375 (376)      25   970.4    971 (970)
  20   344.7    345            26  1051.8    1.05T
  21   352.3    352
Labels here are MTS rounded half up, so three differ from the graphic by $1B.
FY2026 net interest / receipts = 1051.8 / 5403.3 = 19.5% ("19% of revenue":
right). FY2016 = 7.4%. Average rate on total marketable debt (Fiscal Data
avg_interest_rates): 1.470% Sept. 2021, 3.518% Sept. 2026.

matplotlib; build with python3.13 on Mac, from this workspace (logo path).
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
STAMP = "101926"

CREAM = "#fdf6e8"
INK = "#1f2933"
ORANGE = "#e8833a"
DEEP = "#b8562a"
SOFT = "#e9b48c"
MUTED = "#8a8172"
GRID = "#d8cdb8"


def series():
    rows = json.load(open(SRC))["data"]
    out = {}
    for r in rows:
        y = int(r["record_fiscal_year"])
        amt = r["current_fytd_rcpt_outly_amt"]
        if amt in (None, "null", ""):
            continue
        if r["classification_desc"] == "Net Interest" and r["src_line_nbr"] == "31":
            out.setdefault(y, {})["ni"] = Decimal(amt) / Decimal(1e9)
        if r["classification_desc"] == "Total" and r["src_line_nbr"] == "12":
            out.setdefault(y, {})["rc"] = Decimal(amt) / Decimal(1e9)
    return out


def b(v):
    return v.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def build():
    s = series()
    years = list(range(2016, 2027))
    assert sorted(s) == years, sorted(s)
    ni = {y: s[y]["ni"] for y in years}
    share = {y: s[y]["ni"] / s[y]["rc"] * 100 for y in years}
    assert [int(b(ni[y])) for y in years] == [241, 263, 325, 376, 345, 352, 475, 659, 882, 970, 1052], \
        [b(ni[y]) for y in years]
    sh26 = share[2026].quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    sh16 = share[2016].quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    assert (str(sh26), str(sh16)) == ("19.5", "7.4"), (sh26, sh16)

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.05, 0.15, 0.90, 0.58])
    ax.set_facecolor(CREAM)

    for i, y in enumerate(years):
        last = y == 2026
        v = float(ni[y])
        ax.bar(i, v, width=0.68, color=ORANGE if last else SOFT, zorder=3)
        label = f"${ni[y] / 1000:.2f}T" if last else f"${b(ni[y])}B"
        ax.text(i, v + 22, label, fontsize=19 if last else 13.5, fontweight="bold",
                color=DEEP if last else INK, ha="center", va="bottom")
        ax.text(i, -60, f"FY{str(y)[2:]}", fontsize=13, fontweight="bold" if last else "normal",
                color=INK if last else MUTED, ha="center", va="top")

    ax.text(0, float(ni[2016]) + 95, f"{sh16}% of\nreceipts", fontsize=11.5, color=MUTED,
            ha="center", va="bottom", linespacing=1.15)
    ax.text(10, float(ni[2026]) + 118, f"{sh26}% of\nreceipts", fontsize=12.5, color=DEEP,
            fontweight="bold", ha="center", va="bottom", linespacing=1.15)

    ax.set_xlim(-0.6, 10.6)
    ax.set_ylim(0, 1360)
    ax.axis("off")

    fig.text(0.035, 0.955, "America's Interest Bill Tops $1 Trillion", fontsize=28,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.888, "Net interest on federal debt by fiscal year (October to September)",
             fontsize=14, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.838, "The average rate on Treasury's marketable debt is 3.52%, up from "
             "1.47% in September 2021.", fontsize=14.5, color=INK, ha="left", va="top")
    fig.text(0.035, 0.05, "Source: U.S. Treasury, Monthly Treasury Statement (Table 9) and "
             "average interest rates, via Fiscal Data.", fontsize=10.2, color=MUTED,
             ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"net-interest-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
