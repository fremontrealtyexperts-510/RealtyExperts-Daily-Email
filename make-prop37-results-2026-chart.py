"""
make-prop37-results-2026-chart.py  DATA_DIR  [outdir]

The 11/04/26 daily's election chart, at Harv's request ("put a picture or graph
for the prop 37, the current status of it"), modeled on the NYT results page he
supplied. Emits BOTH:

  prop37-results-110426.png      plain HB monogram    -> RE email + Agent Hub
  prop37-results-110426-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds the California Secretary of State's semi-official results JSON
(api.sos.ca.gov/returns/ballot-measures and .../county/<slug>), saved the
morning of Nov. 4, 2026:
  statewide.json alameda.json santa-clara.json contra-costa.json
  san-mateo.json san-francisco.json

=============================================================================
VERIFICATION 11/04/26
=============================================================================
* Every number is read from the SOS JSON, never typed. Statewide at 8:08 AM PT:
  Yes 4,605,778 (61.0%), No 2,946,506 (39.0%). The NYT page Harv supplied
  (AP, 10:20 AM ET) had 4,595,175 to 2,937,535, an earlier snapshot; same 61.0%.
* AP called the race at 9:06 PM PT Nov. 3 (KQED's results page, AP feed).
* Percent labels are recomputed from the vote counts and asserted against the
  SOS's own printed percent, so the bar and the label cannot disagree.
* "100% of precincts reporting" is NOT "all votes counted": California counts
  mail ballots that arrive up to seven days after Election Day. The subtitle
  says the count continues. Keep it neutral: no campaign, party or endorsement.
* Local: Alameda County holds Fremont, Hayward, Newark and Union City; Milpitas
  is in Santa Clara County.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
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

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "110426"

CREAM = "#fdf6e8"
INK = "#1f2933"
YES = "#2b7a78"
NO = "#d9b48f"
GRID = "#d8cdb8"
MUTED = "#8a8172"
WHITE = "#ffffff"

COUNTIES = [
    ("san-francisco", "San Francisco", ""),
    ("alameda", "Alameda", "Fremont, Hayward, Newark, Union City"),
    ("san-mateo", "San Mateo", ""),
    ("contra-costa", "Contra Costa", ""),
    ("santa-clara", "Santa Clara", "Milpitas"),
]


def p1(x):
    return Decimal(x).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def load(slug):
    d = json.load(open(os.path.join(DATA, slug + ".json")))
    m = [x for x in d["ballot-measures"] if x["Number"] == "37"]
    assert len(m) == 1 and "Middle-Income" in m[0]["Name"], m
    m = m[0]
    y, n = int(m["yesVotes"]), int(m["noVotes"])
    yp = p1(Decimal(y) * 100 / (y + n))
    assert str(yp) == m["yesPercent"], (slug, yp, m["yesPercent"])
    assert str(p1(100 - yp)) == m["noPercent"] or str(p1(Decimal(n) * 100 / (y + n))) == m["noPercent"], slug
    return {"yes": y, "no": n, "yp": float(yp), "np": float(p1(Decimal(n) * 100 / (y + n))),
            "time": d["ReportingTime"]}


def build():
    st = load("statewide")
    assert (st["yes"], st["no"], st["yp"]) == (4605778, 2946506, 61.0), st
    assert st["time"] == "November 4, 2026, 8:08 a.m.", st["time"]
    rows = [(name, note, load(slug)) for slug, name, note in COUNTIES]
    yps = [r[2]["yp"] for r in rows]
    assert yps == sorted(yps, reverse=True), yps                     # drawn in order of Yes share
    assert all(v > 50 for v in yps)
    times = sorted(r[2]["time"] for r in rows)
    assert set(times) == {"November 3, 2026, 11:25 p.m.", "November 3, 2026, 11:41 p.m.", "November 4, 2026, 12:05 a.m.",
                          "November 4, 2026, 2:05 a.m.", "November 4, 2026, 2:19 a.m."}, times   # footnote's range

    fig = plt.figure(figsize=(14.0, 8.2), dpi=100)
    fig.patch.set_facecolor(CREAM)

    # ---- statewide bar ----
    ax0 = fig.add_axes([0.035, 0.600, 0.93, 0.115])
    ax0.set_facecolor(CREAM)
    ax0.barh(0, st["yp"], height=1.0, color=YES)
    ax0.barh(0, st["np"], left=st["yp"], height=1.0, color=NO)
    ax0.text(1.2, 0.12, f"YES  {st['yp']:.1f}%", fontsize=24, fontweight="bold", color=WHITE, va="center", ha="left")
    ax0.text(1.2, -0.30, f"{st['yes']:,} votes", fontsize=13, color=WHITE, va="center", ha="left")
    ax0.text(98.8, 0.12, f"NO  {st['np']:.1f}%", fontsize=24, fontweight="bold", color=INK, va="center", ha="right")
    ax0.text(98.8, -0.30, f"{st['no']:,} votes", fontsize=13, color=INK, va="center", ha="right")
    ax0.axvline(50, color=INK, lw=1.2, ls=(0, (3, 3)), ymin=-0.08, ymax=1.08, clip_on=False)
    ax0.set_xlim(0, 100)
    ax0.set_ylim(-0.5, 0.5)
    ax0.axis("off")
    fig.text(0.035, 0.735, "California statewide", fontsize=15, fontweight="bold", color=INK, ha="left", va="bottom")
    fig.text(0.5 * 0.93 + 0.035, 0.582, "50%", fontsize=10.5, color=MUTED, ha="center", va="top")

    # ---- Bay Area counties ----
    ax = fig.add_axes([0.255, 0.125, 0.71, 0.36])
    ax.set_facecolor(CREAM)
    n = len(rows)
    for i, (name, note, r) in enumerate(rows):
        yv = n - 1 - i
        ax.barh(yv, r["yp"], height=0.62, color=YES)
        ax.barh(yv, r["np"], left=r["yp"], height=0.62, color=NO)
        ax.text(1.2, yv, f"{r['yp']:.1f}%", fontsize=14, fontweight="bold", color=WHITE, va="center", ha="left")
        ax.text(98.8, yv, f"{r['np']:.1f}%", fontsize=13, color=INK, va="center", ha="right")
        bold = bool(note)
        ax.text(-2.0, yv + (0.13 if note else 0), name, fontsize=14.5, fontweight="bold" if bold else "normal",
                color=INK, va="center", ha="right")
        if note:
            ax.text(-2.0, yv - 0.25, note, fontsize=10.5, color=MUTED, va="center", ha="right")
    ax.axvline(50, color=INK, lw=1.0, ls=(0, (3, 3)))
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.6, n - 0.4)
    ax.axis("off")
    fig.text(0.035, 0.505, "Bay Area counties", fontsize=15, fontweight="bold", color=INK, ha="left", va="bottom")

    fig.text(0.035, 0.955, "Prop. 37 Is Projected to Pass", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.895, "Loans for middle income buyers of newly built homes. Semi-official count as of 8:08 AM PT, Nov. 4, 2026;",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.860, "the Associated Press called the race at 9:06 PM PT, Nov. 3. Mail ballots are still being counted.",
             fontsize=13.5, color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.035, "Source: California Secretary of State, semi-official election results (county counts updated "
             "11:25 PM Nov. 3 to 2:19 AM Nov. 4); AP race call via KQED.", fontsize=10.2, color=MUTED, ha="left", va="bottom")
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"prop37-results-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
