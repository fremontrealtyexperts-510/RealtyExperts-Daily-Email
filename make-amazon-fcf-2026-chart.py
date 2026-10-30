#!/usr/bin/env python3
"""
make-amazon-fcf-2026-chart.py  DATA_DIR  [outdir]

The 10/30/26 daily's stock chart. Harv attached the newsletter's "Amazon's Cash
Flow Goes Negative" graphic: trailing 12-month free cash flow, seven bars,
Q1 '25 through Q3 '26. Emits BOTH:

  amazon-fcf-103026.png      plain HB monogram    -> RE email + Agent Hub
  amazon-fcf-103026-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds the Exhibit 99.1 earnings releases from SEC EDGAR:
  amzn-q3.htm          Oct. 29, 2026 (0001018724-26-000038)
  pr-2026-07-30.htm    July 30, 2026 (0001018724-26-000024)

=============================================================================
VERIFICATION 10/30/26
=============================================================================
* Every series is read from the releases' "Free cash flow -- TTM" rows, not
  typed. All seven graphic bars hold: 25.9, 18.2, 14.8, 11.2, 1.2, -7.6, -42.4.
* The graphic's TITLE is the one thing changed. "Cash Flow" went up, not
  negative: operating cash flow rose 29% to $168.3B. FREE cash flow is what
  turned negative, so the title says that.
* Q3 2026 TTM: operating cash flow $168,300M less net purchases of property and
  equipment $210,657M = -$42,357M. The net purchases rose $94.8B year over year,
  which the release says "primarily reflects investments in artificial
  intelligence". The AI attribution is for that INCREASE, not the whole $210.7B.
* The first negative reading was Q2 '26. This chart's point is the size of the
  drop since, $34.8B in one quarter.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
import html
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "103026"

CREAM = "#fdf6e8"
INK = "#1f2933"
BLUE = "#2563eb"
CORAL = "#d9643a"
GRID = "#d8cdb8"
MUTED = "#8a8172"
ZERO = "#6b6252"
MINUS = "−"


def text_of(fname):
    b = open(os.path.join(DATA, fname), encoding="utf8", errors="ignore").read()
    b = re.sub(r"(?is)<(script|style).*?</\1>", "", b)
    b = re.sub(r"(?i)</tr>", "\n", b)
    b = re.sub(r"<[^>]+>", " ", b)
    return re.sub(r"[ \t ]+", " ", html.unescape(b))


def row(text, label):
    """The six quarterly figures on the row that starts with `label`, in millions."""
    for line in text.split("\n"):
        if line.strip().startswith(label):
            vals = re.findall(r"\(?\d[\d,]*\)?", line[line.index(label) + len(label):].replace("(1)", ""))
            out = []
            for v in vals[:6]:
                n = int(re.sub(r"[(),]", "", v))
                out.append(-n if v.startswith("(") else n)
            assert len(out) == 6, (label, vals)
            return out
    raise SystemExit(f"row not found: {label}")


def billions(m):
    return float((Decimal(m) / 1000).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def money(v):
    return (MINUS if v < 0 else "") + f"\\${abs(v):.1f}B"


def load():
    oct_pr, jul_pr = text_of("amzn-q3.htm"), text_of("pr-2026-07-30.htm")
    fcf_new = row(oct_pr, "Free cash flow -- TTM")          # Q2 25 .. Q3 26
    fcf_old = row(jul_pr, "Free cash flow -- TTM")          # Q1 25 .. Q2 26
    assert fcf_old[1:] == fcf_new[:5], (fcf_old, fcf_new)   # the two releases agree
    series = [fcf_old[0]] + fcf_new
    assert [billions(m) for m in series] == [25.9, 18.2, 14.8, 11.2, 1.2, -7.6, -42.4], series
    ocf = row(oct_pr, "Operating cash flow -- trailing twelve months (TTM)")[-1]
    capex = row(oct_pr, "Purchases of property and equipment, net of proceeds from sales and incentives -- TTM")
    assert (ocf, capex[-1]) == (168300, 210657), (ocf, capex)
    assert ocf - capex[-1] == series[-1]
    assert capex[-1] - capex[1] == 94754, capex          # the "$94.8 billion" in the release
    return series, ocf, capex[-1], capex[-1] - capex[1]


def build():
    series, ocf, capex, up = load()
    labels = ["Q1 '25", "Q2 '25", "Q3 '25", "Q4 '25", "Q1 '26", "Q2 '26", "Q3 '26"]
    vals = [billions(m) for m in series]

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.115, 0.895, 0.70])
    ax.set_facecolor(CREAM)

    xs = range(len(vals))
    ax.bar(xs, vals, width=0.62, color=[BLUE if v >= 0 else CORAL for v in vals], zorder=3)
    ax.axhline(0, color=ZERO, lw=1.5, zorder=4)
    for x, v in zip(xs, vals):
        ax.text(x, v + (1.3 if v >= 0 else -1.5), money(v), ha="center", va="bottom" if v >= 0 else "top",
                fontsize=17, fontweight="bold", color=INK if v >= 0 else CORAL, zorder=5)

    ax.set_xticks(list(xs))
    ax.set_xticklabels(labels, fontsize=13.5, color=INK)
    ax.set_xlim(-0.6, len(vals) - 0.4)
    ax.set_ylim(-52, 34)
    ticks = [-40, -20, 0, 20]
    ax.set_yticks(ticks)
    ax.set_yticklabels([(MINUS if v < 0 else "") + f"\\${abs(v)}B" for v in ticks], fontsize=12.5, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=9)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # the arithmetic behind the last bar, in the empty space under the blue bars
    X, Y = 0.115, 0.375
    box = dict(facecolor=CREAM, edgecolor="none", pad=3)
    fig.text(X, Y, "The last 12 months", fontsize=13, color=MUTED, ha="left", va="top", bbox=box)
    fig.text(X, Y - 0.042, money(billions(ocf)), fontsize=18, fontweight="bold", color=BLUE, ha="left", va="top", bbox=box)
    fig.text(X + 0.105, Y - 0.048, "cash from operations, up 29%", fontsize=13.5, color=INK, ha="left", va="top", bbox=box)
    fig.text(X, Y - 0.10, money(billions(capex)), fontsize=18, fontweight="bold", color=CORAL, ha="left", va="top", bbox=box)
    fig.text(X + 0.105, Y - 0.106, f"spent on property and equipment,", fontsize=13.5, color=INK, ha="left", va="top", bbox=box)
    fig.text(X + 0.105, Y - 0.138, f"up {money(billions(up))} from a year ago, mainly AI", fontsize=13.5, color=INK,
             ha="left", va="top", bbox=box)

    fig.text(0.035, 0.955, "Amazon's Free Cash Flow Goes Negative", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.895, "Trailing 12-month free cash flow, in billions of dollars.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035, "Source: Amazon quarterly earnings releases (SEC 8-K, Exhibit 99.1), through Oct. 29, 2026.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"amazon-fcf-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
