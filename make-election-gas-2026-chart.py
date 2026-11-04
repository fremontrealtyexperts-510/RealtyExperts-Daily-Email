"""
make-election-gas-2026-chart.py  DATA_DIR  [outdir]

The 11/04/26 daily's economy chart. Harv attached the newsletter's "Election
Day Gas Hits a Record" graphic: U.S. average regular gasoline in Election Day
week, 2016 to 2026, EIA. Emits BOTH:

  election-gas-110426.png      plain HB monogram    -> RE email + Agent Hub
  election-gas-110426-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds EIA's weekly retail price tables (dnav LeafHandler HTML, f=w):
  NUS.html     emm_epmr_pte_nus_dpg    U.S. regular, all formulations ($/gal)
  Y05SF.html   emm_epmr_pte_y05sf_dpg  San Francisco regular, all formulations

=============================================================================
VERIFICATION 11/04/26
=============================================================================
* All six graphic bars hold at EIA's Monday survey of Election Day week:
  2016 2.233, 2018 2.753, 2020 2.112, 2022 3.796, 2024 3.069, 2026 4.153.
  (Market Briefs' $4.13 is GasBuddy's Election Day figure, a different survey.)
* "Record" holds in NOMINAL dollars against every federal Election Day back to
  EIA's first week (Aug. 1990); the prior high was 2022's $3.796. It does NOT
  hold after inflation: on CPI-U (Sept. 2026 = 336.940) 2012's $3.492 is about
  $5.11, 2010 about $4.32, 2022 about $4.30 and 2014 about $4.27. The subtitle
  says "not adjusted for inflation" and the footnote carries the 2012 number.
* ADDED under keep it local: EIA's San Francisco series (starts June 2000).
  2026 is its Election Day high too, $5.699 vs 2022's $5.260.
* Both 2026 prints are DOWN from the week before (U.S. 4.269, SF 5.856).

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import datetime
import html
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "110426"

CREAM = "#fdf6e8"
INK = "#1f2933"
ORANGE = "#e07a2e"
ORANGE_PALE = "#efbe93"
SLATE = "#3e5c76"
SLATE_PALE = "#a9b8c6"
GRID = "#d8cdb8"
MUTED = "#8a8172"
BAND = "#f6e6cc"

MON = {m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}


def parse(fname):
    """EIA dnav weekly table -> {date: price}."""
    t = open(os.path.join(DATA, fname), encoding="utf8", errors="ignore").read()
    out = {}
    for row in re.findall(r"<tr>(.*?)</tr>", t, re.S):
        ym = re.search(r"(\d{4})-([A-Z][a-z]{2})", row)
        if not ym:
            continue
        y = int(ym.group(1))
        cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
                 for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)][1:]
        for i in range(0, len(cells) - 1, 2):
            d, v = cells[i], cells[i + 1]
            if re.match(r"\d\d/\d\d$", d) and re.match(r"^\d+\.\d+$", v):
                mm, dd = map(int, d.split("/"))
                yy = y + 1 if (mm == 1 and MON[ym.group(2)] == 12) else y
                out[datetime.date(yy, mm, dd)] = float(v)
    return out


def election_monday(y):
    d = datetime.date(y, 11, 2)
    while d.weekday() != 1:          # first Tuesday on or after Nov. 2
        d += datetime.timedelta(days=1)
    return d - datetime.timedelta(days=1)


def r2(v):
    return float(Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def load():
    us, sf = parse("NUS.html"), parse("Y05SF.html")
    years = [2016, 2018, 2020, 2022, 2024, 2026]
    u = [us[election_monday(y)] for y in years]
    s = [sf[election_monday(y)] for y in years]
    assert [r2(v) for v in u] == [2.23, 2.75, 2.11, 3.80, 3.07, 4.15], u      # the supplied graphic
    assert [r2(v) for v in s] == [2.78, 3.71, 3.18, 5.26, 4.42, 5.70], s
    all_us = [us[election_monday(y)] for y in range(1990, 2027, 2)]
    all_sf = [sf[election_monday(y)] for y in range(2000, 2027, 2)]
    assert max(all_us) == u[-1] and sorted(all_us)[-2] == 3.796, all_us     # nominal record, prior 2022
    assert max(all_sf) == s[-1], all_sf
    # week before: both fell into Election Day
    assert us[datetime.date(2026, 10, 26)] == 4.269 and sf[datetime.date(2026, 10, 26)] == 5.856
    return years, u, s


def build():
    years, u, s = load()
    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.13, 0.895, 0.66])
    ax.set_facecolor(CREAM)

    w = 0.36
    n = len(years)
    ax.axvspan(n - 1 - 0.5, n - 1 + 0.5, color=BAND, zorder=0)
    for i in range(n):
        last = i == n - 1
        ax.bar(i - w / 2 - 0.01, u[i], width=w, color=ORANGE if last else ORANGE_PALE, zorder=3)
        ax.bar(i + w / 2 + 0.01, s[i], width=w, color=SLATE if last else SLATE_PALE, zorder=3)
        ax.text(i - w / 2 - 0.01, u[i] + 0.07, f"\\${r2(u[i]):.2f}", ha="center", va="bottom",
                fontsize=14.5 if last else 13, fontweight="bold", color=ORANGE if last else INK, zorder=5)
        ax.text(i + w / 2 + 0.01, s[i] + 0.07, f"\\${r2(s[i]):.2f}", ha="center", va="bottom",
                fontsize=14.5 if last else 13, fontweight="bold", color=SLATE if last else INK, zorder=5)

    ax.set_xticks(range(n))
    ax.set_xticklabels([str(y) for y in years], fontsize=15, color=INK)
    for lab in ax.get_xticklabels()[-1:]:
        lab.set_fontweight("bold")
    ax.set_xlim(-0.6, n - 0.4)
    ax.set_ylim(0, 6.6)
    ticks = [0, 2, 4, 6]
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"\\${v}" for v in ticks], fontsize=12.5, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=9)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    leg = ax.legend(handles=[Patch(color=ORANGE, label="U.S. average"), Patch(color=SLATE, label="San Francisco")],
                    loc="upper left", frameon=False, fontsize=13.5, handlelength=1.2, borderaxespad=0.2)
    for t in leg.get_texts():
        t.set_color(INK)

    fig.text(0.035, 0.955, "Election Day Gas Hits a Record, Here and Nationally", fontsize=26, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.895, "Price of a gallon of regular in Election Day week, EIA's Monday survey, not adjusted for inflation.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.06, "Highest of any Election Day in EIA's records (U.S. since 1990, San Francisco since 2000). "
             "After inflation, 2012's \\$3.49 would be about \\$5.11 today.", fontsize=11, color=INK, ha="left", va="bottom")
    fig.text(0.035, 0.025, "Source: U.S. Energy Information Administration, weekly retail gasoline prices, all formulations; "
             "inflation adjustment uses BLS CPI-U.", fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"election-gas-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
