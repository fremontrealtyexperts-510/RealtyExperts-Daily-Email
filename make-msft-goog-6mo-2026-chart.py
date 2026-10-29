#!/usr/bin/env python3
"""
make-msft-goog-6mo-2026-chart.py  DATA_DIR  [outdir]

The 10/29/26 daily's stock chart. Harv attached the newsletter's "Microsoft Pulls
Away" graphic: MSFT and GOOG as percent change over the past 6 months, through
Oct. 28, end labels +25.1% and -7.3%, source Google Finance. Emits BOTH:

  msft-goog-102926.png      plain HB monogram    -> RE email + Agent Hub
  msft-goog-102926-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

No company logos: the graphic carried both trademarks, ours does not.

DATA_DIR holds (fetched Oct. 29, 2026, about 11:00 AM PT):
  msft-yahoo.json   MSFT, Yahoo chart API, interval 1d, Apr. 1, 2026 onward
  goog-yahoo.json   GOOG, same
  live-cnbc.json    CNBC quote service, MSFT|GOOG, 2:05 PM ET (11:05 AM PT)

=============================================================================
VERIFICATION 10/29/26
=============================================================================
* The graphic's base is the Apr. 29, 2026 close: MSFT 424.46 to 531.01 on
  Oct. 28 = up 25.10%, GOOG 347.31 to 321.89 = down 7.32%. Both labels hold
  (an Apr. 28 base gives MSFT +23.7%, which does not).
* Its early May GOOG spike is real: Apr. 30 close 381.94, up 9.97% in a day.
* Thursday: Alphabet's Q3 release (SEC 8-K, Exhibit 99.1, Oct. 28) shows
  revenue up 25% to $127.6B and Google Cloud up 103% to $30.7B, but EPS of
  $2.12 against $2.87 a year ago (an $8.7B loss on equity securities) and
  capital spending of $51.4B against $24.0B, so free cash flow was negative
  $9.1B. GOOG traded down 12.99% at 11:05 AM PT. Market Briefs' "Google saw
  its AI sales dip" is not in the release. Microsoft (8-K Ex. 99.1): Azure up
  48%, revenue $92.3B up 19%.

matplotlib; build with python3.13 on Mac.
"""
import json
import os
import sys
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "102926"

CREAM = "#fdf6e8"
INK = "#1f2933"
BLUE = "#2563eb"
ORANGE = "#d9643a"
GRID = "#d8cdb8"
MUTED = "#8a8172"
ZERO = "#b9ad93"
MINUS = "−"

BASE, END = date(2026, 4, 29), date(2026, 10, 28)
LIVE_DAY = datetime(2026, 10, 29)


def pct(a, b, places="0.01"):
    # round ONCE from the raw ratio
    return float(((Decimal(str(a)) / Decimal(str(b)) - 1) * 100).quantize(
        Decimal(places), rounding=ROUND_HALF_UP))


def signed(v, places=1):
    s = f"{abs(v):.{places}f}%"
    return ("+" if v >= 0 else MINUS) + s


def daily(fname):
    r = json.load(open(os.path.join(DATA, fname)))["chart"]["result"][0]
    et = ZoneInfo("America/New_York")
    s = {}
    for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]):
        if c is not None:
            s[datetime.fromtimestamp(t, et).date()] = round(c, 2)
    return s


def live():
    q = json.load(open(os.path.join(DATA, "live-cnbc.json")))["FormattedQuoteResult"]["FormattedQuote"]
    out = {}
    for x in q:
        out[x["symbol"]] = (float(x["last"].replace(",", "")),
                            float(x["previous_day_closing"].replace(",", "")),
                            x["change_pct"], x["last_time"])
    return out


def load():
    m, g = daily("msft-yahoo.json"), daily("goog-yahoo.json")
    assert (m[BASE], m[END]) == (424.46, 531.01), (m[BASE], m[END])
    assert (g[BASE], g[END]) == (347.31, 321.89), (g[BASE], g[END])
    assert pct(m[END], m[BASE], "0.1") == 25.1
    assert pct(g[END], g[BASE], "0.1") == -7.3
    assert pct(g[date(2026, 4, 30)], g[BASE]) == 9.97
    lv = live()
    # live prior close must be Wednesday's verified close, or the quote is stale
    assert lv["MSFT"][1] == m[END] and lv["GOOG"][1] == g[END], lv
    assert lv["GOOG"][3].startswith("2026-10-29T14:05"), lv["GOOG"][3]
    days = sorted(k for k in m if BASE <= k <= END)
    assert days == sorted(k for k in g if BASE <= k <= END)
    ms = [(k, pct(m[k], m[BASE])) for k in days]
    gs = [(k, pct(g[k], g[BASE])) for k in days]
    return ms, gs, lv, m, g


def build():
    ms, gs, lv, m, g = load()
    m_end, g_end = ms[-1][1], gs[-1][1]
    m_live, g_live = pct(lv["MSFT"][0], m[BASE]), pct(lv["GOOG"][0], g[BASE])
    g_day = pct(lv["GOOG"][0], g[END])
    assert g_day == -12.99, g_day
    assert (round(m_live, 1), round(g_live, 1)) == (24.0, -19.4), (m_live, g_live)

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.07, 0.12, 0.70, 0.69])
    ax.set_facecolor(CREAM)

    def xs(series):
        return [datetime(k.year, k.month, k.day) for k, _ in series]

    ax.axhline(0, color=ZERO, lw=1.4, zorder=2)
    ax.plot(xs(ms), [v for _, v in ms], color=BLUE, lw=2.8, solid_joinstyle="round", zorder=4)
    ax.plot(xs(gs), [v for _, v in gs], color=ORANGE, lw=2.8, solid_joinstyle="round", zorder=4)

    # Wednesday close dots (the newsletter's frame)
    ex = xs(ms)[-1]
    ax.scatter([ex], [m_end], s=90, color=BLUE, edgecolor=CREAM, linewidth=2, zorder=6)
    ax.scatter([ex], [g_end], s=90, color=ORANGE, edgecolor=CREAM, linewidth=2, zorder=6)

    # Thursday intraday, dashed and hollow so it never reads as a close
    ax.plot([ex, LIVE_DAY], [m_end, m_live], color=BLUE, lw=2.2, ls=(0, (2, 2)), zorder=4)
    ax.plot([ex, LIVE_DAY], [g_end, g_live], color=ORANGE, lw=2.2, ls=(0, (2, 2)), zorder=4)
    ax.scatter([LIVE_DAY], [m_live], s=70, color=CREAM, edgecolor=BLUE, linewidth=2.2, zorder=7)
    ax.scatter([LIVE_DAY], [g_live], s=70, color=CREAM, edgecolor=ORANGE, linewidth=2.2, zorder=7)
    ax.annotate(f"Thursday, after earnings:\n{signed(g_day, 1)} on the day",
                xy=(LIVE_DAY, g_live), xytext=(-12, -8), textcoords="offset points",
                fontsize=12, fontweight="bold", color=ORANGE, ha="right", va="top")

    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
    # "May" takes no period; every other month here is abbreviated
    ax.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda v, _: (lambda d: d.strftime("%b") + ("" if d.month == 5 else "."))(mdates.num2date(v))))
    ax.set_xlim(datetime(2026, 4, 25), datetime(2026, 11, 3))
    ax.set_ylim(-25, 35)
    ticks = [-20, -10, 0, 10, 20, 30]
    ax.set_yticks(ticks)
    ax.set_yticklabels([("+" if v > 0 else (MINUS if v < 0 else "")) + f"{abs(v)}%" for v in ticks],
                       fontsize=12.5, color=MUTED)
    ax.tick_params(axis="x", labelsize=12.5, colors=MUTED)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # right hand stat column: the newsletter's frame first, Thursday underneath
    X = 0.80
    fig.text(X, 0.74, "Through Wednesday's close", fontsize=12.5, color=MUTED, ha="left", va="top")
    fig.text(X, 0.70, signed(m_end, 1), fontsize=30, fontweight="bold", color=BLUE, ha="left", va="top")
    fig.text(X, 0.635, "Microsoft", fontsize=13.5, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(X, 0.57, signed(g_end, 1), fontsize=30, fontweight="bold", color=ORANGE, ha="left", va="top")
    fig.text(X, 0.505, "Alphabet (Google)", fontsize=13.5, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(X, 0.40, "As of Thu. 11:05 AM PT", fontsize=12.5, color=MUTED, ha="left", va="top")
    fig.text(X, 0.36, f"Microsoft {signed(m_live, 1)}", fontsize=15, fontweight="bold", color=BLUE,
             ha="left", va="top")
    fig.text(X, 0.315, f"Alphabet {signed(g_live, 1)}", fontsize=15, fontweight="bold", color=ORANGE,
             ha="left", va="top")
    fig.text(X, 0.265, "dashed line, not a close", fontsize=11, color=MUTED, ha="left", va="top")

    fig.text(0.035, 0.955, "Microsoft Pulls Away", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.895,
             "Stock performance over the past 6 months: change from the Apr. 29 close, through Wednesday, Oct. 28.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035,
             "Source: Yahoo Finance daily closes (MSFT, GOOG), Apr. 29 to Oct. 28, 2026; Thursday intraday from CNBC at 11:05 AM PT.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"msft-goog-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
