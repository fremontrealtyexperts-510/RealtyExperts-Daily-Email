#!/usr/bin/env python3
"""
make-us-growth-chart.py  [out.png]

REALTY EXPERTS recreation of the "U.S. Economic Growth" graphic Harv supplied for
the 08/24/26 daily email. Two panels, both built only from numbers the primary
releases actually print.

⚠️ THE SUPPLIED GRAPHIC'S ENDPOINT LABEL IS WRONG. It prints 56.1 for the August
composite. The primary source, the S&P Global Flash US PMI news release embargoed
to 0945 EDT on 21 August 2026, prints "Flash US Composite PMI Output Index: 56.0
(July: 54.5). 52-month high." Market Briefs' looser "hit 56 in August" is right.
This chart uses 56.0.

WHY THE DESIGN CHANGED. The supplied graphic is a crop of the release's own
chart: a monthly S&P Global Composite PMI line from 2019 with quarterly GDP bars
behind it. The GDP half is fully sourceable. The PMI half is NOT: S&P Global's
monthly index history is licensed and is not published in the release, on FRED,
or anywhere free that agrees with the release. The one free series found
(MQL5's "Markit Composite PMI" export) contradicts the release outright, showing
53.6 where S&P Global prints 54.5 for July, so it was discarded rather than
drawn. Rather than trace ~90 points off a JPEG, this chart keeps both stories
using only published values: the long arc of GDP on the left, and the August
survey against July, sector by sector, on the right.

DATA PROVENANCE.
* GDP bars: Bureau of Economic Analysis, real gross domestic product, percent
  change from the quarter one year ago (series A191RO1Q156NBEA), pulled from
  ALFRED, vintage 2026-08-24. 2019Q1 through 2026Q2, the latest published
  quarter. "annualised % yr/yr" on the S&P chart is this year-over-year series,
  not the quarter-over-quarter annualized rate: the release's own axes align PMI
  50 with GDP 0, and its 2020Q2 trough and 2021Q2 spike match -7.4 and +12.4,
  which is the yr/yr series, not the -28.1 and +34.8 of the quarterly rate.
* PMI bars: S&P Global Flash US PMI news release, 21 August 2026. Composite
  Output 56.0 (July 54.5), Services Business Activity 56.8 (July 54.6),
  Manufacturing Output 51.9 (July 53.9), Manufacturing PMI 53.2 (July 53.9).
  Data were collected 12 to 20 August 2026.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data sources. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

OUT = sys.argv[1] if len(sys.argv) > 1 else "us-growth-082426.png"

# --- BEA A191RO1Q156NBEA, real GDP, % change from same quarter a year earlier --
QUARTERS = [
    "2019Q1", "2019Q2", "2019Q3", "2019Q4",
    "2020Q1", "2020Q2", "2020Q3", "2020Q4",
    "2021Q1", "2021Q2", "2021Q3", "2021Q4",
    "2022Q1", "2022Q2", "2022Q3", "2022Q4",
    "2023Q1", "2023Q2", "2023Q3", "2023Q4",
    "2024Q1", "2024Q2", "2024Q3", "2024Q4",
    "2025Q1", "2025Q2", "2025Q3", "2025Q4",
    "2026Q1", "2026Q2",
]
GDP = [
    1.9, 2.2, 2.8, 3.4,
    1.4, -7.4, -1.4, -0.9,
    1.8, 12.4, 5.2, 5.8,
    4.0, 2.5, 2.3, 1.3,
    2.3, 2.8, 3.2, 3.4,
    2.9, 3.1, 2.8, 2.4,
    2.0, 2.1, 2.3, 2.0,
    2.7, 2.1,
]

# --- S&P Global Flash US PMI, 21 August 2026 ----------------------------------
PMI_LABELS = ["Composite\nOutput", "Services\nActivity",
              "Manufacturing\nOutput", "Manufacturing\nPMI"]
PMI_AUG = [56.0, 56.8, 51.9, 53.2]
PMI_JUL = [54.5, 54.6, 53.9, 53.9]

assert len(QUARTERS) == len(GDP) == 30
assert GDP[-1] == 2.1 and QUARTERS[-1] == "2026Q2"
assert PMI_AUG[0] == 56.0, "composite must be the released 56.0, not the graphic's 56.1"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
SLATE = "#4a5568"
GREEN = "#2f7d5d"
SAND = "#c9b896"
GRID = "#d8cdb8"

fig, (axl, axr) = plt.subplots(
    1, 2, figsize=(13.6, 6.6), dpi=170,
    gridspec_kw={"width_ratios": [1.58, 1.0], "wspace": 0.30})
fig.patch.set_facecolor(CREAM)
for a in (axl, axr):
    a.set_facecolor(CREAM)

# ============================ LEFT: GDP year over year ========================
xs = list(range(len(GDP)))
colors = [CORAL if v < 0 else (GREEN if i == len(GDP) - 1 else SAND)
          for i, v in enumerate(GDP)]
axl.bar(xs, GDP, width=0.74, color=colors, zorder=3)
axl.axhline(0, color=INK, lw=1.3, zorder=4)

axl.annotate(f"2026 Q2\n{GDP[-1]:.1f}%",
             xy=(xs[-1], GDP[-1]), xytext=(xs[-1] - 1.9, GDP[-1] + 3.1),
             ha="center", va="bottom", fontsize=12.4, fontweight="bold",
             color=GREEN,
             arrowprops=dict(arrowstyle="-", color=GREEN, lw=1.5,
                             shrinkA=2, shrinkB=3))
axl.annotate("2020 Q2\n-7.4%", xy=(5, -7.4), xytext=(6.6, -6.2),
             ha="left", va="center", fontsize=11.6, fontweight="bold",
             color=CORAL)

axl.set_title("Real GDP growth, percent change from a year earlier",
              fontsize=14.2, color=SLATE, loc="left", pad=10)
axl.set_ylim(-9.6, 14.4)
axl.yaxis.set_major_locator(MultipleLocator(3))
axl.set_xlim(-1.0, len(GDP) + 0.4)
ticks = [i for i, q in enumerate(QUARTERS) if q.endswith("Q1")]
axl.set_xticks(ticks)
axl.set_xticklabels([QUARTERS[i][2:4] for i in ticks])

# ====================== RIGHT: August survey vs July ==========================
ys = list(range(len(PMI_LABELS)))[::-1]
h = 0.34
axr.barh([y + h / 2 + 0.02 for y in ys], PMI_AUG, height=h, color=CORAL,
         zorder=3, label="August 2026 (flash)")
axr.barh([y - h / 2 - 0.02 for y in ys], PMI_JUL, height=h, color=SLATE,
         zorder=3, label="July 2026")
axr.axvline(50, color=INK, lw=1.6, ls=(0, (4, 3)), zorder=5)
axr.text(50, -0.86, "50 = no change", fontsize=11.4, color=INK,
         ha="center", va="center", fontweight="bold")

for y, va, vj in zip(ys, PMI_AUG, PMI_JUL):
    axr.text(va + 0.35, y + h / 2 + 0.02, f"{va:.1f}", va="center", ha="left",
             fontsize=12.8, fontweight="bold", color=CORAL)
    axr.text(vj + 0.35, y - h / 2 - 0.02, f"{vj:.1f}", va="center", ha="left",
             fontsize=12.0, color=SLATE)

axr.set_title("S&P Global flash PMI, August versus July",
              fontsize=14.2, color=SLATE, loc="left", pad=10)
axr.set_yticks(ys)
axr.set_yticklabels(PMI_LABELS, fontsize=12.2)
axr.set_xlim(45, 60.5)
axr.set_ylim(-1.25, 3.62)
axr.xaxis.set_major_locator(MultipleLocator(5))

_h, _l = axr.get_legend_handles_labels()
leg = fig.legend(_h, _l, loc="upper right", bbox_to_anchor=(0.988, 0.982),
                 ncol=2, frameon=False, fontsize=12.4, handlelength=1.5,
                 columnspacing=1.8)
for t in leg.get_texts():
    t.set_color(INK)
    t.set_fontweight("bold")

# ============================== shared chrome =================================
for a, axis in ((axl, "y"), (axr, "x")):
    a.grid(axis=axis, color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
    a.set_axisbelow(True)
for a in (axl, axr):
    for s in ("top", "right", "left"):
        a.spines[s].set_visible(False)
    a.spines["bottom"].set_color(GRID)
    a.tick_params(axis="both", length=0, labelsize=12.6, colors=SLATE)

fig.text(0.038, 0.955, "U.S. Economic Growth", fontsize=26,
         fontweight="bold", color=INK, va="top")
fig.text(0.038, 0.893,
         "Business activity is running at a 52 month high while GDP growth "
         "holds near 2 percent",
         fontsize=13.6, color=SLATE, va="top")

fig.text(0.008, 0.052,
         "Sources: S&P Global Flash US PMI news release, 21 August 2026. Data "
         "were collected 12 to 20 August 2026.",
         fontsize=10.6, color=SLATE)
fig.text(0.008, 0.018,
         "Bureau of Economic Analysis, real GDP, percent change from a year "
         "earlier, through 2026 Q2.",
         fontsize=10.6, color=SLATE)

fig.subplots_adjust(left=0.055, right=0.988, top=0.795, bottom=0.145)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
print(f"  GDP latest      {QUARTERS[-1]} = {GDP[-1]:.1f}% yr/yr")
print(f"  Composite PMI   Aug {PMI_AUG[0]:.1f} vs Jul {PMI_JUL[0]:.1f}")
print(f"  Services        Aug {PMI_AUG[1]:.1f} vs Jul {PMI_JUL[1]:.1f}")
