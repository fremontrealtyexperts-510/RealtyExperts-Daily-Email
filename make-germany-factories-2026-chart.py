#!/usr/bin/env python3
"""
make-germany-factories-2026-chart.py  DATA_DIR  [outdir]

The 10/26/26 daily's Economy chart, a SUBSTITUTE. Harv attached the newsletter's
"Services Drag German Growth" graphic: three bars of the HCOB flash Germany PMI
for October 2026 (Manufacturing 54.2, Composite 52.8, Services 51.7). The PMI
release carries S&P Global's notice that "any unauthorised use, including but
not limited to copying, distributing, transmitting or otherwise of any data
appearing is not permitted without S&P Global's prior consent", the same problem
as ISM's license (memory reference-ism-pmi-license-no-derived-charts). So no PMI
chart: the readings go in the copy as text, and this chart tells the German
growth story from official statistics. Emits BOTH:

  germany-factories-102626.png      plain HB monogram    -> RE email + Agent Hub
  germany-factories-102626-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds gva-long.json, the Eurostat dissemination API pull:
  ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/namq_10_a10
  ?geo=DE&unit=CLV_PCH_SM&s_adj=SCA&na_item=B1G&nace_r2=TOTAL&nace_r2=C
  &nace_r2=B-E&sinceTimePeriod=2017-Q1&format=JSON
Gross value added, chain linked volumes, percent change on the same quarter of
the previous year, seasonally and calendar adjusted. Dataset updated Oct. 22,
2026; 2023 Q1 onward flagged provisional ("p"). Eurostat permits reuse with
acknowledgement of the source.

=============================================================================
VERIFICATION 10/26/26
=============================================================================
* Manufacturing (NACE C): +1.3% in 2022 Q4, then 13 straight quarters below
  zero (2023 Q1 -0.2 through 2026 Q1 -0.5, deepest -4.8 in 2023 Q4), then
  +0.9% in 2026 Q2: the first year over year gain since 2022 Q4.
* Whole economy (TOTAL gross value added): +1.1% in 2026 Q2, its best since
  2022 Q4 (+1.2%).
* The October flash PMI that the newsletter charted (for the COPY, not this
  chart; FXStreet and investingLive reports of the Oct. 23 HCOB release):
  composite 52.8 from 53.8 (53.3 expected), services 51.7 from 52.9,
  manufacturing 54.2 from 53.9. The surveys say the same split continued in
  October: factories stronger, services softer.

matplotlib; build with python3.13 on Mac.
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
STAMP = "102626"

CREAM = "#fdf6e8"
INK = "#1f2933"
RED = "#d6363c"
GREEN = "#2f7d4f"
ORANGE = "#e0892b"
GRID = "#d8cdb8"
MUTED = "#8a8172"

FIRST = "2022-Q1"


def load():
    d = json.load(open(os.path.join(DATA, "gva-long.json")))
    dims, size = d["id"], d["size"]
    idx = {k: d["dimension"][k]["category"]["index"] for k in dims}
    times = sorted(idx["time"], key=lambda t: idx["time"][t])

    def val(nace, t):
        flat = 0
        for k, s in zip(dims, size):
            p = idx[k][{"nace_r2": nace, "time": t}[k]] if k in ("nace_r2", "time") else 0
            flat = flat * s + p
        return d["value"].get(str(flat))

    assert d["updated"].startswith("2026-10-22"), d["updated"]
    assert list(idx["unit"]) == ["CLV_PCH_SM"] and list(idx["s_adj"]) == ["SCA"]
    qs = [t for t in times if t >= FIRST]
    mfg = [val("C", t) for t in qs]
    tot = [val("TOTAL", t) for t in qs]
    assert None not in mfg and None not in tot
    m = dict(zip(qs, mfg))
    T = dict(zip(qs, tot))
    assert qs[-1] == "2026-Q2" and m["2026-Q2"] == 0.9 and m["2026-Q1"] == -0.5, (qs[-1], m["2026-Q2"])
    assert m["2022-Q4"] == 1.3 and min(m.values()) == -4.8 == m["2023-Q4"]
    run = [t for t in qs if "2023-Q1" <= t <= "2026-Q1"]
    assert len(run) == 13 and all(m[t] < 0 for t in run), run
    assert T["2026-Q2"] == 1.1 and T["2022-Q4"] == 1.2
    assert all(T[t] < 1.1 for t in qs if "2023-Q1" <= t <= "2026-Q1")
    return qs, mfg, tot


def build():
    qs, mfg, tot = load()
    x = list(range(len(qs)))

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.075, 0.17, 0.89, 0.62])
    ax.set_facecolor(CREAM)

    colors = [GREEN if v > 0 else RED for v in mfg]
    ax.bar(x, mfg, width=0.62, color=colors, zorder=3)
    ax.plot(x, tot, color=ORANGE, lw=2.4, marker="o", ms=6.5, mfc=CREAM, mec=ORANGE,
            mew=2, zorder=4)
    ax.axhline(0, color=INK, lw=1.1, zorder=2)

    # value labels on every manufacturing bar; the LAST one goes inside its bar in
    # white, because above the bar it sat on the whole economy dot (+1.1)
    for xi, v in zip(x, mfg):
        if xi == x[-1]:
            ax.text(xi, v / 2, f"{v:+.1f}", ha="center", va="center", fontsize=11,
                    color="white", fontweight="bold", zorder=5)
            continue
        ax.text(xi, v + (0.25 if v > 0 else -0.25), f"{v:+.1f}".replace("-", "−"),
                ha="center", va="bottom" if v > 0 else "top", fontsize=11,
                color=GREEN if v > 0 else RED, fontweight="bold", zorder=5)

    # bracket over the 13 down quarters, sitting in the empty band above zero
    i0, i1 = qs.index("2023-Q1"), qs.index("2026-Q1")
    yb = 2.35
    ax.plot([i0 - 0.3, i0 - 0.3, i1 + 0.3, i1 + 0.3], [yb - 0.3, yb, yb, yb - 0.3],
            color=MUTED, lw=1.2, zorder=3)
    ax.text((i0 + i1) / 2, yb + 0.2, "13 straight quarters of decline", ha="center",
            va="bottom", fontsize=13, color=MUTED)

    # callout on the turn
    xl = len(qs) - 1
    ax.annotate("First gain since\nlate 2022", xy=(xl - 0.05, 1.45), xytext=(xl - 0.75, 4.3),
                ha="center", va="bottom", fontsize=13.5, fontweight="bold", color=GREEN,
                arrowprops=dict(arrowstyle="-", color=GREEN, lw=1.3, shrinkA=2, shrinkB=2))

    ax.set_xticks(x)
    ax.set_xticklabels([q.replace("-Q", "\nQ") if q.endswith("Q1") else q[-2:] for q in qs],
                       fontsize=11.5, color=MUTED)
    ax.set_xlim(-0.7, len(qs) - 0.3)
    ax.set_ylim(-6.0, 6.0)
    ax.set_yticks([-6, -4, -2, 0, 2, 4, 6])
    ax.set_yticklabels(["−6%", "−4%", "−2%", "0%", "+2%", "+4%", "+6%"], fontsize=12, color=MUTED)
    ax.tick_params(axis="both", length=0, pad=6)
    ax.grid(axis="y", color=GRID, lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # legend, top left under the subtitle
    fig.text(0.075, 0.835, "■", fontsize=15, color=GREEN, ha="left", va="center")
    fig.text(0.091, 0.835, "■", fontsize=15, color=RED, ha="left", va="center")
    fig.text(0.110, 0.835, "Manufacturing", fontsize=13, color=INK, ha="left", va="center")
    fig.text(0.235, 0.835, "●", fontsize=13, color=ORANGE, ha="left", va="center")
    fig.text(0.252, 0.835, "Whole economy", fontsize=13, color=INK, ha="left", va="center")

    fig.text(0.035, 0.955, "Germany's Factories Are Growing Again", fontsize=26,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.035, 0.895,
             "Real output (gross value added), percent change from the same quarter a year earlier, seasonally adjusted.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035,
             "Source: Eurostat quarterly national accounts (namq_10_a10), chain linked volumes, updated Oct. 22, 2026. Figures from 2023 on are provisional.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"germany-factories-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
