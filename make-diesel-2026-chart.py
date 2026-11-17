"""
make-diesel-2026-chart.py  EIA_US_HTML  EIA_CA_HTML  [outdir]

The 11/17/26 daily's Economy chart. Harv supplied "Diesel Is Off Its Record
High" (U.S. average retail diesel, weekly 2026: $3.48 Jan. 5, record $6.53
Sep. 21, $6.13 Nov. 9; EIA through Nov. 9). Rebuilt as OUR chart from EIA's
own weekly series, extended one week to EIA's Nov. 16 release (the week Market
Briefs wrote about: just under $6), and KEPT LOCAL with California's weekly
average on the same axis.

Emits BOTH:
  diesel-111726.png      plain HB monogram    -> RE email + Agent Hub
  diesel-111726-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

EIA_US_HTML = eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=EMD_EPD2D_PTE_NUS_DPG&f=W
EIA_CA_HTML = eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=EMD_EPD2D_PTE_SCA_DPG&f=W
(No. 2 diesel retail prices, dollars per gallon, weekly, Mondays.)

=============================================================================
VERIFICATION 11/17/26
=============================================================================
* The supplied graphic's three labels equal EIA's U.S. series: Jan. 5 3.477
  ($3.48), Sep. 21 6.529 ($6.53), Nov. 9 6.127 ($6.13).
* Sep. 21's 6.529 is the highest in the series, which starts Mar. 21, 1994
  (1,705 weeks), so "record" holds. California's high is the same week, 8.246.
* Nov. 16: U.S. 5.937, the first week under $6 since Sep. 7 (5.967), as Market
  Briefs said ("just under $6 ... first time since early September").
  California 7.733, 1.796 above the U.S.
* A year earlier (Nov. 17, 2025): U.S. 3.868, California 4.996.
* Money rounded half up with Decimal.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import html
import os
import re
import sys
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

US_SRC, CA_SRC = sys.argv[1], sys.argv[2]
OUTDIR = sys.argv[3] if len(sys.argv) > 3 else "."
STAMP = "111726"

CREAM = "#fdf6e8"
INK = "#1f2933"
ORANGE = "#d9771f"
BRICK = "#9b3a24"
GRID = "#e6dcc8"
MUTED = "#8a8172"

MON = {m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}


def parse(path):
    """EIA LeafHandler weekly table: a 'YYYY-Mon' cell, then (MM/DD, value) pairs."""
    t = open(path, errors="ignore").read()
    out = {}
    for row in re.findall(r"(?is)<tr>(.*?)</tr>", t):
        cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"(?is)<td[^>]*>(.*?)</td>", row)]
        if not cells:
            continue
        m = re.match(r"(\d{4})-(\w{3})$", cells[0])
        if not m:
            continue
        yr, rest = int(m.group(1)), cells[1:]
        for i in range(0, len(rest) - 1, 2):
            d, v = rest[i], rest[i + 1]
            if not re.match(r"\d\d/\d\d$", d) or not v:
                continue
            mm, dd = map(int, d.split("/"))
            y = yr + 1 if (mm == 1 and MON[m.group(2)] == 12) else yr
            out[date(y, mm, dd)] = Decimal(v)
    return out


def c2(x):
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def load():
    us, ca = parse(US_SRC), parse(CA_SRC)
    D = date
    # the supplied graphic, label for label
    assert (c2(us[D(2026, 1, 5)]), c2(us[D(2026, 9, 21)]), c2(us[D(2026, 11, 9)])) == \
        (Decimal("3.48"), Decimal("6.53"), Decimal("6.13"))
    assert min(us) == D(1994, 3, 21) and max(us.values()) == us[D(2026, 9, 21)] == Decimal("6.529")
    assert max(ca.values()) == ca[D(2026, 9, 21)] == Decimal("8.246")
    last = max(us)
    assert last == D(2026, 11, 16) and us[last] == Decimal("5.937") and ca[last] == Decimal("7.733"), last
    under = sorted(d for d in us if d < last and us[d] < 6)
    assert under[-1] == D(2026, 9, 7) and us[under[-1]] == Decimal("5.967"), under[-1]
    assert (us[D(2025, 11, 17)], ca[D(2025, 11, 17)]) == (Decimal("3.868"), Decimal("4.996"))
    weeks = sorted(d for d in us if D(2026, 1, 5) <= d <= last)
    assert len(weeks) == 46 and all(d in ca for d in weeks), len(weeks)
    return weeks, [float(us[d]) for d in weeks], [float(ca[d]) for d in weeks]


def build():
    weeks, us, ca = load()
    fig = plt.figure(figsize=(14.0, 7.8), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.13, 0.76, 0.68])
    ax.set_facecolor(CREAM)

    for g in range(3, 10):
        ax.axhline(g, color=GRID, lw=1, zorder=1, ls=(0, (4, 4)))
        ax.text(weeks[0] - (weeks[1] - weeks[0]) * 1.2, g, f"\\${g}", ha="right", va="center", fontsize=13,
                color=MUTED)
    ax.fill_between(weeks, 3, us, color=ORANGE, alpha=0.10, lw=0, zorder=2)
    ax.plot(weeks, ca, color=BRICK, lw=3.0, zorder=4)
    ax.plot(weeks, us, color=ORANGE, lw=3.4, zorder=5)

    # start
    ax.plot([weeks[0]], [us[0]], marker="o", ms=10, color=ORANGE, zorder=6)
    ax.text(weeks[0], us[0] - 0.42, "\\$3.48  Jan. 5", fontsize=13, fontweight="bold", color=INK, ha="left",
            va="center")
    # records, same week for both
    i = weeks.index(date(2026, 9, 21))
    wk = weeks[1] - weeks[0]
    # U.S. label sits right of its point, in the empty band between the two lines (CA runs 8.1 to 8.2,
    # U.S. 6.2 to 6.4 from Sep. 28 on); centered above it, the CA line crossed it in late August.
    for y, color, lab, dx, ha in ((us[i], ORANGE, "\\$6.53 U.S. record, Sept. 21", 0.9, "left"),
                                  (ca[i], BRICK, "\\$8.25 California record", 0, "center")):
        ax.plot([weeks[i]], [y], marker="o", ms=11, color=CREAM, mec=color, mew=3, zorder=7)
        ax.text(weeks[i] + wk * dx, y + 0.36, lab, fontsize=13, fontweight="bold", color=color, ha=ha,
                va="center")

    end = weeks[-1]
    ax.plot([end], [us[-1]], marker="o", ms=12, color=ORANGE, zorder=7)
    ax.plot([end], [ca[-1]], marker="o", ms=12, color=BRICK, zorder=7)
    lx = end + (weeks[1] - weeks[0]) * 1.1
    ax.text(lx, ca[-1] + 0.12, "\\$7.73", fontsize=26, fontweight="bold", color=BRICK, ha="left", va="center")
    ax.text(lx, ca[-1] - 0.42, "California", fontsize=13, color=INK, ha="left", va="center")
    ax.text(lx, us[-1] + 0.12, "\\$5.94", fontsize=26, fontweight="bold", color=ORANGE, ha="left", va="center")
    ax.text(lx, us[-1] - 0.42, "U.S. average\nNov. 16", fontsize=13, color=INK, ha="left", va="top",
            linespacing=1.15)

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.tick_params(axis="x", length=0, labelsize=13, pad=8)
    for t in ax.get_xticklabels():
        t.set_color(INK)
    ax.yaxis.set_visible(False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlim(weeks[0] - (weeks[1] - weeks[0]) * 0.6, end + (weeks[1] - weeks[0]) * 0.6)
    ax.set_ylim(2.8, 9.15)

    fig.text(0.035, 0.955, "Diesel Is Off Its Record High", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.897, "Average retail price of diesel, dollars per gallon, weekly, 2026. "
             "The U.S. average slipped under \\$6 for the first time since early September.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.03, "Source: U.S. Energy Information Administration, No. 2 diesel retail prices, "
             "U.S. and California, weekly through Nov. 16, 2026.", fontsize=10.2, color=MUTED, ha="left",
             va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"diesel-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
