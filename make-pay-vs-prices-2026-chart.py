"""
make-pay-vs-prices-2026-chart.py  DATA_DIR  [outdir]

The 11/07/26 daily's Real Estate chart. Harv supplied a screenshot of a Business
Insider chart (Juliana Kaplan/BI, "Year-over-year change in earnings", source
BLS), 3.1% in October 2026. Recreated as OUR chart from BLS, with consumer
prices added beside pay because that comparison is what a buyer's budget feels.

Emits BOTH:
  pay-vs-prices-110726.png      plain HB monogram    -> RE email + Agent Hub
  pay-vs-prices-110726-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds raw BLS Public Data API v1 responses pulled 11/07/26:
  bls-2020-2021.json  and  bls-2022-2026.json
  CES0500000003  average hourly earnings, all private employees, SA
  CUUR0000SA0    CPI-U, all items, U.S. city average, NSA (the headline YoY basis)

=============================================================================
VERIFICATION 11/07/26
=============================================================================
* Pay YoY = AHE / AHE a year earlier - 1. October 2026 3.12% (BLS: 3.1%),
  peak 5.89% March 2022 (the screenshot's ~5.9% top), asserted.
* CPI YoY September 2026 3.74% (BLS 3.7%), asserted. October 2026 CPI is not
  out yet. October 2025 CPI was never collected ("Data unavailable due to the
  2025 lapse in appropriations"), so the CPI line has a one month gap there.
* Prices have outrun pay in each of the six latest CPI months, April to
  September 2026, and the last month before that with prices ahead was April
  2023 (both asserted).

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "110726"

CREAM = "#fdf6e8"
INK = "#1f2933"
NAVY = "#2b4c7e"
ORANGE = "#ea580c"
GRID = "#e6dcc8"
MUTED = "#8a8172"
AXIS = "#8a7f6a"
SHADE = "#f6d9c4"


def load():
    S = {}
    for f in ("bls-2020-2021.json", "bls-2022-2026.json"):
        d = json.load(open(os.path.join(DATA, f)))
        assert d["status"] == "REQUEST_SUCCEEDED", (f, d["status"])
        for s in d["Results"]["series"]:
            for r in s["data"]:
                if r["period"] != "M13" and r["value"] != "-":
                    S.setdefault(s["seriesID"], {})[(int(r["year"]), int(r["period"][1:]))] = float(r["value"])

    def yoy(sid, y, m):
        a, b = S[sid].get((y, m)), S[sid].get((y - 1, m))
        return (a / b - 1) * 100 if a and b else None

    months = [(y, m) for y in range(2022, 2027) for m in range(1, 13) if (y, m) <= (2026, 10)]
    pay = [yoy("CES0500000003", y, m) for y, m in months]
    cpi = [yoy("CUUR0000SA0", y, m) for y, m in months]
    i = {k: n for n, k in enumerate(months)}
    assert round(pay[i[(2026, 10)]], 1) == 3.1 and round(max(pay), 2) == 5.89, (pay[-1], max(pay))
    assert round(cpi[i[(2026, 9)]], 1) == 3.7, cpi[i[(2026, 9)]]
    assert cpi[i[(2025, 10)]] is None and cpi[i[(2026, 10)]] is None
    ahead = [k for k in months if cpi[i[k]] is not None and cpi[i[k]] > pay[i[k]]]
    assert ahead[-6:] == [(2026, m) for m in range(4, 10)], ahead[-6:]
    assert ahead[-7] == (2023, 4), ahead[-7]
    return months, pay, cpi


def build():
    months, pay, cpi = load()
    x = list(range(len(months)))
    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.17, 0.89, 0.60])
    ax.set_facecolor(CREAM)

    a0 = months.index((2026, 4))
    ax.axvspan(a0 - 0.5, months.index((2026, 9)) + 0.5, color=SHADE, alpha=0.55, zorder=0, lw=0)
    for yv in (2, 4, 6, 8):
        ax.axhline(yv, color=GRID, lw=1, zorder=1)
        ax.text(-1.0, yv, f"{yv}%", ha="right", va="center", fontsize=11, color=MUTED)
    ax.plot(x, pay, color=NAVY, lw=3.2, zorder=4, solid_capstyle="round")
    xs = [a for a, v in zip(x, cpi) if v is not None]
    # draw CPI in runs so the October 2025 gap stays a gap
    run = []
    for a, v in zip(x, cpi):
        if v is None:
            if run:
                ax.plot(*zip(*run), color=ORANGE, lw=3.2, zorder=3, solid_capstyle="round")
            run = []
        else:
            run.append((a, v))
    if run:
        ax.plot(*zip(*run), color=ORANGE, lw=3.2, zorder=3, solid_capstyle="round")

    for n, (y, m) in enumerate(months):
        if m == 1:
            ax.text(n, 0.85, str(y), ha="left", va="top", fontsize=13, color=INK, fontweight="bold")
            ax.plot([n, n], [1.15, 1.35], color=AXIS, lw=1.2)
    ax.set_xlim(-1.5, len(months) + 6.5)
    ax.set_ylim(0.6, 9.6)
    ax.axis("off")

    # end labels
    ax.text(x[-1] + 0.8, pay[-1] - 0.05, "Pay +3.1%\n(October)", ha="left", va="top", fontsize=13,
            fontweight="bold", color=NAVY, linespacing=1.1)
    lc = months.index((2026, 9))
    ax.text(lc + 1.8, cpi[lc] + 0.12, "Prices +3.7%\n(September)", ha="left", va="bottom", fontsize=13,
            fontweight="bold", color=ORANGE, linespacing=1.1)
    ax.text(a0 + 2.5, 8.9, "Prices ahead\nof pay since April", ha="center", va="top", fontsize=12,
            color="#9a4a1c", linespacing=1.15)
    ax.text(months.index((2022, 6)) + 0.6, 9.2, "Prices", ha="left", va="bottom", fontsize=12.5,
            color=ORANGE, fontweight="bold")
    ax.text(months.index((2022, 3)), 6.15, "Pay", ha="center", va="bottom", fontsize=12.5, color=NAVY,
            fontweight="bold")

    fig.text(0.035, 0.955, "Prices Are Rising Faster Than Paychecks Again", fontsize=26, fontweight="bold",
             color=INK, ha="left", va="top")
    fig.text(0.035, 0.897, "Change from a year earlier: average hourly pay vs. consumer prices, 2022 to 2026",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.03, "Source: U.S. Bureau of Labor Statistics. Pay: average hourly earnings, all private "
             "employees (SA). Prices: CPI-U, all items. No CPI for October 2025 (not collected).",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"pay-vs-prices-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
