#!/usr/bin/env python3
"""
make-oracle-coreweave-2026-chart.py  DATA_DIR  [outdir]

The 10/09/26 daily's AI stocks chart (Stocks section). Harv attached the
newsletter graphic "Oracle vs. CoreWeave in 2026" (year to date stock
performance through Oct. 8; CoreWeave +13.9%, Oracle -30.4%; "Source: Google
Finance, as of Oct. 8, 2026"). Emits BOTH:

  oracle-coreweave-100926.png      plain HB monogram    -> RE email + Agent Hub
  oracle-coreweave-100926-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds the raw Yahoo Finance chart API responses (daily bars,
Dec. 29, 2025 to Oct. 9, 2026): y_ORCL.json, y_CRWV.json, y_IXIC.json.
Every series is computed from the file, never hand typed.

=============================================================================
VERIFICATION 10/09/26
=============================================================================
Base = the Dec. 31, 2025 close (ORCL 194.91, CRWV 71.61, Nasdaq 23,241.99).
Oct. 8 closes: ORCL 135.69 = -30.38% (graphic -30.4%), CRWV 81.58 = +13.92%
(graphic +13.9%). Thursday's moves match the newsletter: ORCL -5.48%
(143.56 to 135.69), CRWV -7.77% (88.45 to 81.58). The graphic's shape checks
out: CoreWeave's 2026 high close is +92.7% on May 6 and its low -15.1% on
July 29; Oracle's high is +27.3% on June 1 and its low -41.0% on July 24.
The chart labels CoreWeave's high and Oracle's low (Oracle's high label
collided with the CoreWeave line in June, so it was left off).
No missing or degenerate (O=H=L=C) bars in the window.

Our addition: the Nasdaq Composite on the same basis, +17.0% through Oct. 8.
Both AI names trail the plain index this year, which the supplied graphic
does not show.

matplotlib; build with python3.13 on Mac.
"""
import json
import os
import sys
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "100926"
BASE_DAY = "2025-12-31"
END_DAY = "2026-10-08"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e05a47"
DEEP = "#b8432f"
BLUE = "#2b6cb0"
BLUE_D = "#1e4e8c"
SLATE = "#9a9081"
GRID = "#d8cdb8"
MUTED = "#8a8172"
MINUS = "−"


def r1(x):
    return Decimal(str(x)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def pct(x):
    v = r1(x)
    return f"+{v}%" if v > 0 else f"{MINUS}{abs(v)}%"


AP_MONTHS = ["Jan.", "Feb.", "March", "April", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."]


def ap(d):
    return f"{AP_MONTHS[d.month - 1]} {d.day}"


def load(name):
    d = json.load(open(os.path.join(DATA, name)))["chart"]["result"][0]
    q = d["indicators"]["quote"][0]
    bars = {}
    for t, o, h, l, c in zip(d["timestamp"], q["open"], q["high"], q["low"], q["close"]):
        day = datetime.fromtimestamp(t, ZoneInfo("America/New_York")).strftime("%Y-%m-%d")
        assert c is not None, (name, day)
        assert not (o == h == l == c), ("degenerate bar", name, day)
        bars[day] = Decimal(str(c))
    base = bars[BASE_DAY]
    days = sorted(k for k in bars if "2026-01-01" <= k <= END_DAY)
    ser = [(date.fromisoformat(k), (bars[k] / base - 1) * 100) for k in days]
    return bars, ser


def build():
    orcl_b, orcl = load("y_ORCL.json")
    crwv_b, crwv = load("y_CRWV.json")
    _, ixic = load("y_IXIC.json")

    # the supplied graphic's headline numbers
    assert r1(orcl[-1][1]) == Decimal("-30.4"), orcl[-1]
    assert r1(crwv[-1][1]) == Decimal("13.9"), crwv[-1]
    # Thursday's moves as printed by the newsletter
    assert (orcl_b[END_DAY] / orcl_b["2026-10-07"] - 1) * 100 < Decimal("-5.47")
    assert (crwv_b[END_DAY] / crwv_b["2026-10-07"] - 1) * 100 < Decimal("-7.76")
    assert len(orcl) == len(crwv) == len(ixic)

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.13, 0.75, 0.66])
    ax.set_facecolor(CREAM)

    def xs(s):
        return [d for d, _ in s]

    def ys(s):
        return [float(v) for _, v in s]

    ax.axhline(0, color=INK, lw=1.1, alpha=0.55, zorder=2)
    ax.plot(xs(ixic), ys(ixic), color=SLATE, lw=2.0, ls=(0, (4, 3)), zorder=3)
    ax.plot(xs(crwv), ys(crwv), color=BLUE, lw=2.6, solid_joinstyle="round", zorder=4)
    ax.plot(xs(orcl), ys(orcl), color=CORAL, lw=2.6, solid_joinstyle="round", zorder=5)

    end = orcl[-1][0]
    for s, col in ((crwv, BLUE), (orcl, CORAL)):
        ax.scatter([end], [float(s[-1][1])], s=90, color=col, edgecolor=CREAM, linewidth=1.8, zorder=7)
    ax.scatter([end], [float(ixic[-1][1])], s=50, color=SLATE, edgecolor=CREAM, linewidth=1.5, zorder=6)

    # CoreWeave's high and Oracle's low, quietly, in open space
    cpk = max(crwv, key=lambda p: p[1])
    ax.annotate(f"CoreWeave's high: {pct(cpk[1])}, {ap(cpk[0])}",
                xy=(cpk[0], float(cpk[1])), xytext=(10, 2), textcoords="offset points",
                fontsize=12, color=BLUE_D, ha="left", va="center", zorder=8)
    olo = min(orcl, key=lambda p: p[1])
    ax.annotate(f"Oracle's low: {pct(olo[1])}, {ap(olo[0])}",
                xy=(olo[0], float(olo[1])), xytext=(0, -9), textcoords="offset points",
                fontsize=12, color=DEEP, ha="center", va="top", zorder=8)

    # end labels in the right margin
    lab_x = 1.012
    def endlab(y_data, text, sub, col, dy=0):
        y_ax = ax.transLimits.transform((mdates.date2num(end), y_data))[1]
        ax.text(lab_x, y_ax + dy, text, transform=ax.transAxes, fontsize=20, fontweight="bold",
                color=col, ha="left", va="center", clip_on=False)
        ax.text(lab_x, y_ax + dy - 0.055, sub, transform=ax.transAxes, fontsize=12.5,
                color=col, ha="left", va="center", clip_on=False)

    ax.set_xlim(date(2026, 1, 1), date(2026, 10, 14))
    ax.set_ylim(-50, 100)
    fig.canvas.draw()
    endlab(float(crwv[-1][1]), pct(crwv[-1][1]), "CoreWeave", BLUE, dy=0.0)
    endlab(float(ixic[-1][1]), pct(ixic[-1][1]), "Nasdaq", SLATE, dy=0.09)
    endlab(float(orcl[-1][1]), pct(orcl[-1][1]), "Oracle", CORAL)

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.set_yticks([-50, -25, 0, 25, 50, 75, 100])
    ax.set_yticklabels([f"{MINUS}50%", f"{MINUS}25%", "0%", "+25%", "+50%", "+75%", "+100%"],
                       fontsize=11.5, color=MUTED)
    for lab in ax.get_xticklabels():
        lab.set_fontsize(12)
        lab.set_color(MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.035, 0.955, "Oracle vs. CoreWeave in 2026", fontsize=26, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.895,
             "Year to date stock performance through the Oct. 8 close, with the Nasdaq Composite "
             "(dashed) for reference",
             fontsize=13.2, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.030,
             "Source: Yahoo Finance daily closes, Dec. 31, 2025 to Oct. 8, 2026. "
             "Price change only, dividends not included.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"oracle-coreweave-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
