#!/usr/bin/env python3
"""
make-anthropic-prospectus-chart.py  DATA_DIR  [outdir]

Anthropic's 2025 results from its draft IPO prospectus, as a waterfall from
revenue to net loss, for the 09/29/26 daily. Harv supplied two screenshots of
the Reuters exclusive (Sept 28, 2026, Echo Wang) and asked for a graph.

  anthropic-prospectus-092926.png      plain monogram -> RE email + Agent Hub
  anthropic-prospectus-092926-hb.png   + wordmark     -> harvrealtor.com / .net / app

DISCLOSURE: this chart is about Anthropic, the company that makes Claude, which
is the assistant that built it. Same standard as every other chart here, same
precedent as make-anthropic-runrate-chart.py (09/04/26): Harv is told about the
conflict in the run summary so he can decide whether to keep it.

=============================================================================
SOURCES AND VERIFICATION, 09/29/26
=============================================================================

THE FILING IS NOT PUBLIC. Anthropic submitted its draft S-1 confidentially on
June 1, 2026; EDGAR has no Anthropic registration statement as of this build.
Every figure is Reuters' reporting of the draft it saw, so the chart says so.

Parsed at build time from the syndicated Reuters text (DATA_DIR/reuters.html,
the Euronext copy of the main story, body identical across five copies):
  "net loss of $42 billion in 2025"
  "Revenue grew 12-fold in 2025 to nearly $4.6 billion"
  "$7.33 billion on compute and infrastructure ... more than half of its
   $12.65 billion in total operating expenses"
  "a roughly $34 billion accounting charge that reflected an increase in the
   estimated value of financing that could eventually turn into Anthropic
   shares, rather than money the company spent running its business"
  "$518 billion"
and from the $518B follow-up (DATA_DIR/reuters518.html):
  "at least $518 billion over a decade ... about 80% of that sum is
   non-cancelable or requires payment regardless of usage"

The operating loss, $8.06B in 2025 against $2.98B in 2024, is from the Reuters
summary bullets in Harv's screenshot (the syndicated body says "more than $8
billion"); six outlets citing Reuters print the same two numbers. It closes
the waterfall: $12.65B of operating expenses less $8.06B of operating loss is
$4.59B of revenue, which is Reuters' "nearly $4.6 billion". The non-cash charge
is drawn as the net loss less the operating loss ($33.94B, Reuters' "roughly
$34 billion"), so the bars sum exactly to the reported $42B.

matplotlib only; build with python3.13 on Mac.
"""
import html as htmllib
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "092926"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
BLUE = "#2f6db5"
SLATE = "#8a9aa8"
GRID = "#d8cdb8"
MUTED = "#8a8172"
PALE = "#f3c9c3"

# Reuters summary bullets (Harv's screenshot): operating loss 2025 and 2024.
OP_LOSS_2025 = Decimal("8.06")
OP_LOSS_2024 = Decimal("2.98")


def text_of(path):
    s = open(path, encoding="utf-8", errors="ignore").read()
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", s)
    t = htmllib.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"\s+", " ", t)


def grab(pattern, text):
    m = re.search(pattern, text)
    assert m, f"not found in source: {pattern}"
    return Decimal(m.group(1))


def load():
    t = text_of(os.path.join(DATA, "reuters.html"))
    v = {
        "net_loss": grab(r"net loss of \$(\d+) billion in 2025", t),
        "revenue_approx": grab(r"Revenue grew 12-fold in 2025 to nearly \$([\d.]+) billion", t),
        "compute": grab(r"spent \$([\d.]+) billion on compute and infrastructure", t),
        "opex": grab(r"\$([\d.]+) billion in total operating expenses", t),
        "charge_approx": grab(r"roughly \$(\d+) billion accounting charge", t),
        "commitments": grab(r"\$(\d+) billion on cloud, computing and infrastructure obligations", t),
    }
    t2 = text_of(os.path.join(DATA, "reuters518.html"))
    assert grab(r"at least \$(\d+) billion over a decade", t2) == v["commitments"]
    v["noncancel_pct"] = grab(r"about (\d+)% of that sum is non-cancelable", t2)

    v["revenue"] = v["opex"] - OP_LOSS_2025
    v["other"] = v["opex"] - v["compute"]
    v["charge"] = v["net_loss"] - OP_LOSS_2025
    # Internal consistency with Reuters' own rounding.
    assert abs(v["revenue"] - v["revenue_approx"]) <= Decimal("0.05"), v["revenue"]
    assert v["revenue"] <= v["revenue_approx"]                      # "nearly"
    assert abs(v["charge"] - v["charge_approx"]) < 1, v["charge"]   # "roughly"
    assert v["compute"] > v["opex"] / 2                             # "more than half"
    print({k: str(x) for k, x in v.items()})
    return v


def b(x, places="0.01"):
    return Decimal(str(x)).quantize(Decimal(places), rounding=ROUND_HALF_UP)


def build():
    v = load()
    rev, comp, other = float(v["revenue"]), float(v["compute"]), float(v["other"])
    op, charge, net = float(OP_LOSS_2025), float(v["charge"]), float(v["net_loss"])

    # Horizontal waterfall, top to bottom: (label, left, right, colour, value text, kind)
    steps = [
        ("Revenue", 0.0, rev, BLUE, f"+\\${b(rev, '0.1')}B", "flow"),
        ("Compute and infrastructure", rev - comp, rev, CORAL, f"\u2212\\${b(comp)}B", "flow"),
        ("Other operating costs", rev - comp - other, rev - comp, CORAL, f"\u2212\\${b(other)}B", "flow"),
        ("Operating loss", -op, 0.0, INK, f"\u2212\\${b(op)}B", "total"),
        ("Accounting charge on financing\n(not cash spent)", -op - charge, -op, PALE,
         f"about \u2212\\${b(charge, '1')}B", "flow"),
        ("Net loss", -net, 0.0, INK, f"\u2212\\${b(net, '1')}B", "total"),
    ]

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    h = 0.62
    running = [rev, rev - comp, rev - comp - other, -op, -op - charge, -net]
    for i, (lbl, left, right, col, txt, kind) in enumerate(steps):
        hatch = "////" if col == PALE else None
        ax.add_patch(Rectangle((left, i - h / 2), right - left, h, fc=col,
                               ec=DEEP if hatch else "none", lw=1.0 if hatch else 0,
                               hatch=hatch, zorder=3))
        if i < len(steps) - 1:   # dotted connector at the running total
            x = running[i]
            ax.plot([x, x], [i + h / 2, i + 1 - h / 2], color=MUTED, lw=1.0,
                    linestyle=(0, (3, 3)), zorder=2)
        if right - left > 20:     # long bar: label inside
            ax.text((left + right) / 2, i, txt, ha="center", va="center", fontsize=16,
                    fontweight="bold", color="white" if col == INK else DEEP, zorder=5,
                    bbox=None if col == INK else dict(boxstyle="round,pad=0.25", fc=CREAM, ec="none"))
        elif lbl == "Revenue":
            ax.text(right + 0.7, i, txt, ha="left", va="center", fontsize=16,
                    fontweight="bold", color=BLUE, zorder=5)
        else:
            ax.text(left - 0.7, i, txt, ha="right", va="center", fontsize=16,
                    fontweight="bold", color=INK if col == INK else DEEP, zorder=5)

    ax.text(rev + 10.6, 0, "up 12 fold from 2024", ha="left", va="center",
            fontsize=11, color=MUTED)
    ax.text(1.0, 3, f"2024: \u2212\\${b(OP_LOSS_2024)}B", ha="left", va="center",
            fontsize=11.5, color=MUTED)

    ax.text(2.6, 4.5,
            f"Still ahead: at least\n\\${v['commitments']} billion for computing\ncapacity over about a decade,\n"
            f"about {v['noncancel_pct']}% of it non-cancelable",
            ha="left", va="center", fontsize=12.5, color=INK, linespacing=1.45,
            bbox=dict(boxstyle="round,pad=0.6", fc="white", ec=GRID, lw=1.2))

    ax.axvline(0, color=INK, lw=1.1, zorder=4)
    ax.set_ylim(len(steps) - 0.45, -0.55)
    ax.set_xlim(-46, 27)
    ax.set_yticks(range(len(steps)))
    ax.set_yticklabels([s[0] for s in steps], fontsize=13, linespacing=1.3)
    ax.set_xticks([-40, -30, -20, -10, 0, 10])
    ax.xaxis.set_major_formatter(FuncFormatter(
        lambda x, _: f"\\${x:.0f}B" if x >= 0 else f"\u2212\\${-x:.0f}B"))
    ax.grid(axis="x", color=GRID, linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left", "bottom"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="both", length=0, labelsize=12, colors=SLATE)
    for lbl in ax.get_yticklabels():   # after tick_params, which resets colours
        lbl.set_color(INK)
    for lbl, (_, _, _, col, _, kind) in zip(ax.get_yticklabels(), steps):
        if kind == "total":
            lbl.set_fontweight("bold")

    fig.text(0.045, 0.945, "Anthropic's \\$42 Billion Loss, Broken Down",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888,
             "2025 results from the company's draft IPO prospectus, as reported by Reuters",
             fontsize=14, color=MUTED, ha="left", va="top")

    fig.text(
        0.045, 0.112,
        "The prospectus was filed confidentially and is not yet public. Reuters says the accounting charge reflected a higher estimated\n"
        "value of financing that could turn into shares, rather than money spent running the business. Other operating costs are total\n"
        f"operating expenses (\\${v['opex']}B) less compute.",
        fontsize=10.8, color=DEEP, ha="left", va="bottom", linespacing=1.5,
    )
    fig.text(
        0.045, 0.040,
        "Source: Reuters, September 28 and 29, 2026, reporting Anthropic's draft registration statement.",
        fontsize=10.5, color=MUTED, ha="left", va="bottom",
    )

    fig.subplots_adjust(left=0.265, right=0.975, top=0.82, bottom=0.265)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"anthropic-prospectus-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
