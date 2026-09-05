#!/usr/bin/env python3
"""
make-jobsreport-charts.py  [outdir]

Recreates the FIVE graphics Harv supplied for the 09/05/26 Saturday special
edition on the August 2026 jobs report. Emits:

  jobs-fedwatch-090526.png     CME FedWatch, Sept 16 2026 FOMC probabilities
  jobs-unemployment-090526.png U.S. unemployment rate, Jan 2022 to Aug 2026
  jobs-growth-090526.png       Monthly payroll change, Jan 2024 to Aug 2026
  jobs-wages-090526.png        Average hourly earnings, YoY, Jan 2022 to Aug 2026
  jobs-sectors-090526.png      Employment change by sector, July to Aug 2026

=============================================================================
VERIFICATION DONE 09/05/26 (feedback-verify-supplied-chart-values-before-
recreating.md: a supplied graphic is a design brief, NOT a data source)
=============================================================================

Every value was re-pulled from the BLS public API v1 (keyless), not traced off
the supplied images:
  POST https://api.bls.gov/publicAPI/v1/timeseries/data/

FOUR of the five graphics reproduced EXACTLY. That is unusual enough to state
plainly, given how often these fail:

  LNS14000000    unemployment rate      Aug 2026 = 4.1%     matches CNBC
  CES0000000001  total nonfarm          159,075 - 158,913 = +162K   matches NBC
                 YTD: 159,075 - 158,432 (Dec 2025) = +643K  matches NBC
  CES0500000003  avg hourly earnings    $37.75 vs $36.62 = +3.09%, prints 3.1%
                                                            matches CNBC
  16 sector series, July to Aug 2026 change, ALL SIXTEEN matched the Business
  Insider graphic to the tenth of a thousand:
      Leisure and hospitality  +62.0    Wholesale trade            +7.8
      Government               +35.0    Transportation/warehousing +5.0
      Construction             +22.0    Other services             +3.0
      Manufacturing            +16.0    Mining and logging         +3.0
      Social assistance        +15.5    Utilities                  +2.5
      Health care              +12.9    Retail trade               +1.4
      Prof. and business svcs  +10.0    Private educational svcs   +1.1
                                        Financial activities      -11.0
                                        Information               -23.0

ONE CORRECTION we make to the supplied CNBC unemployment graphic
------------------------------------------------------------------
CNBC draws its unemployment line SOLID and unbroken across October 2025. There
is no October 2025 observation. The BLS API returns value "-" for LNS14000000
2025-M10 carrying footnote code 9, verbatim: "Data unavailable due to the 2025
lapse in appropriations." The household survey was not collected that month.
So our version bridges the gap with a DASHED segment and says so in the footer.
Same data, one fewer implied observation. This is the only place our chart and
theirs disagree, and it is theirs that is wrong.

The FedWatch panel: market-implied, arithmetically self-consistent
------------------------------------------------------------------
The CME panel is not a BLS series and cannot be diffed against one, so it was
checked for internal consistency instead. Its own printed ZQU6 mid of 96.3038
implies an average September effective rate of 100 - 96.3038 = 3.6962%. With
the current target midpoint at 3.625% and the meeting on Sept 16 (14 to 15 of
30 days at the new rate), the implied hike probability solves to roughly 57% to
61%, which brackets the printed 58.4%. The panel is coherent with itself.

Independently corroborated that a HIKE is genuinely what is priced (this is
counterintuitive enough to be worth a second source): Forbes, Aug 31 2026,
"CME FedWatch Provides A 66% Chance Fed Will Hike Rates In September". The
supplied screenshot reads 58.4%, LOWER than that 66%, which is the story: the
softer wage number in this report cooled hike odds. It did not remove them.

⚠️ These are market-implied probabilities from fed funds futures, NOT a
forecast and NOT a Fed statement. The copy must say so.

Sum note for the sector chart: the 16 listed sectors total +163.2K against a
+162K headline. Rounding plus sectors not broken out separately. The footer
says the categories do not sum to the headline rather than pretending they do.

BRAND MARK (standing, Harv 08/26/26): silver HB monogram, bottom right, no name
text, alpha 0.20. Copied verbatim from make-rentbuy-chart.py.

matplotlib only; build with python3.13 on Mac.
"""
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
LOGO = "hb-logo-mark.png"
STAMP = "090526"

CREAM = "#fdf6e8"
INK   = "#1f2933"
CORAL = "#e2574c"
DEEP  = "#b8433a"
GREEN = "#2f8f5b"
SLATE = "#4a5568"
GRID  = "#d8cdb8"
MUTED = "#8a8172"
PALE  = "#e7ddc9"

BLS_SRC = "Source: U.S. Bureau of Labor Statistics, seasonally adjusted. Retrieved from the BLS public API, September 5, 2026."


def add_logo(fig, path=LOGO, height=0.05, x=0.985, y=0.026, alpha=0.20):
    """Silver HB monogram, bottom right, deliberately near invisible.

    Verbatim from make-rentbuy-chart.py per the standing 08/26/26 instruction.
    Resample ONCE with PIL to the exact pixel height the figure draws at, then
    blit 1:1 with interpolation="none", or the hairlines turn to mush."""
    try:
        from PIL import Image
        import numpy as np
        src = Image.open(path).convert("RGBA")
    except (FileNotFoundError, OSError, ImportError):
        print(f"WARN: {path} unavailable, chart rendered without the brand mark")
        return False
    fw, fh = fig.get_size_inches()
    px_h = max(1, int(round(height * fh * fig.dpi)))
    px_w = max(1, int(round(src.width * px_h / src.height)))
    src = src.resize((px_w, px_h), Image.LANCZOS)
    w = px_w / (fw * fig.dpi)
    ax = fig.add_axes((x - w, y, w, height), zorder=10)
    ax.imshow(np.asarray(src), interpolation="none", alpha=alpha)
    ax.axis("off")
    return True


def frame(ax, xspine=True):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    if xspine:
        ax.spines["bottom"].set_color(GRID)
    else:
        ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="both", length=0, labelsize=12.5, colors=SLATE)
    ax.set_axisbelow(True)


def save(fig, name):
    path = os.path.join(OUTDIR, name)
    fig.savefig(path, facecolor=CREAM)
    plt.close(fig)
    print(f"  wrote {path}")


# ---------------------------------------------------------------- data (BLS)
# LNS14000000. Note the deliberate absence of 2025-10: see the header.
UR = [
    ('2022-01',4.0),('2022-02',3.9),('2022-03',3.7),('2022-04',3.7),('2022-05',3.6),('2022-06',3.6),
    ('2022-07',3.5),('2022-08',3.6),('2022-09',3.5),('2022-10',3.6),('2022-11',3.6),('2022-12',3.5),
    ('2023-01',3.5),('2023-02',3.6),('2023-03',3.5),('2023-04',3.4),('2023-05',3.6),('2023-06',3.6),
    ('2023-07',3.5),('2023-08',3.7),('2023-09',3.7),('2023-10',3.9),('2023-11',3.7),('2023-12',3.8),
    ('2024-01',3.7),('2024-02',3.9),('2024-03',3.9),('2024-04',3.9),('2024-05',3.9),('2024-06',4.1),
    ('2024-07',4.2),('2024-08',4.2),('2024-09',4.1),('2024-10',4.1),('2024-11',4.2),('2024-12',4.1),
    ('2025-01',4.0),('2025-02',4.2),('2025-03',4.2),('2025-04',4.2),('2025-05',4.3),('2025-06',4.1),
    ('2025-07',4.3),('2025-08',4.3),('2025-09',4.4),            ('2025-11',4.5),('2025-12',4.4),
    ('2026-01',4.3),('2026-02',4.4),('2026-03',4.3),('2026-04',4.3),('2026-05',4.3),('2026-06',4.2),
    ('2026-07',4.1),('2026-08',4.1),
]

# CES0000000001, month over month change in thousands
JOBS = [
    ('2024-01',175),('2024-02',206),('2024-03',228),('2024-04',64),('2024-05',78),('2024-06',87),
    ('2024-07',53),('2024-08',9),('2024-09',155),('2024-10',33),('2024-11',134),('2024-12',237),
    ('2025-01',-48),('2025-02',42),('2025-03',67),('2025-04',108),('2025-05',13),('2025-06',-20),
    ('2025-07',64),('2025-08',-70),('2025-09',76),('2025-10',-140),('2025-11',41),('2025-12',-17),
    ('2026-01',160),('2026-02',-156),('2026-03',214),('2026-04',148),('2026-05',63),('2026-06',31),
    ('2026-07',21),('2026-08',162),
]

# CES0500000003, year over year percent change
AHE = [
    ('2022-01',5.58),('2022-02',5.29),('2022-03',5.89),('2022-04',5.76),('2022-05',5.56),('2022-06',5.40),
    ('2022-07',5.48),('2022-08',5.39),('2022-09',5.13),('2022-10',5.01),('2022-11',5.09),('2022-12',4.94),
    ('2023-01',4.49),('2023-02',4.77),('2023-03',4.62),('2023-04',4.60),('2023-05',4.36),('2023-06',4.66),
    ('2023-07',4.67),('2023-08',4.47),('2023-09',4.42),('2023-10',4.22),('2023-11',4.11),('2023-12',4.10),
    ('2024-01',4.39),('2024-02',4.13),('2024-03',4.15),('2024-04',3.98),('2024-05',4.15),('2024-06',3.92),
    ('2024-07',3.63),('2024-08',3.92),('2024-09',3.91),('2024-10',4.05),('2024-11',4.18),('2024-12',4.08),
    ('2025-01',3.97),('2025-02',4.11),('2025-03',4.21),('2025-04',3.91),('2025-05',3.98),('2025-06',3.86),
    ('2025-07',3.96),('2025-08',3.98),('2025-09',3.85),('2025-10',3.92),('2025-11',3.93),('2025-12',3.73),
    ('2026-01',3.66),('2026-02',3.70),('2026-03',3.43),('2026-04',3.57),('2026-05',3.34),('2026-06',3.38),
    ('2026-07',3.24),('2026-08',3.09),
]

SECTORS = [
    ("Leisure and hospitality",           62.0),
    ("Government",                        35.0),
    ("Construction",                      22.0),
    ("Manufacturing",                     16.0),
    ("Social assistance",                 15.5),
    ("Health care",                       12.9),
    ("Professional and business services",10.0),
    ("Wholesale trade",                    7.8),
    ("Transportation and warehousing",     5.0),
    ("Other services",                     3.0),
    ("Mining and logging",                 3.0),
    ("Utilities",                          2.5),
    ("Retail trade",                       1.4),
    ("Private educational services",       1.1),
    ("Financial activities",             -11.0),
    ("Information",                      -23.0),
]

FEDWATCH = [("3.50% to 3.75%\nNo change", 41.6), ("3.75% to 4.00%\nQuarter point higher", 58.4)]

MONTH_IDX = {k: i for i, (k, _) in enumerate(AHE)}


def xticks_years(ax, keys, years):
    pos = [keys.index(f"{y}-01") for y in years if f"{y}-01" in keys]
    ax.set_xticks(pos)
    ax.set_xticklabels([str(y) for y in years if f"{y}-01" in keys], fontsize=13)


# =========================================================== 1. FedWatch
def chart_fedwatch():
    fig, ax = plt.subplots(figsize=(11.6, 6.6), dpi=170)
    fig.patch.set_facecolor(CREAM); ax.set_facecolor(CREAM)

    labels = [r[0] for r in FEDWATCH]
    vals = [r[1] for r in FEDWATCH]
    xs = [0, 1]
    ax.bar(xs, vals, width=0.44, color=[SLATE, CORAL], zorder=3)

    for x, v in zip(xs, vals):
        ax.text(x, v + 1.6, f"{v}%", ha="center", va="bottom", fontsize=27,
                fontweight="bold", color=INK, zorder=5)

    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=14.5, fontweight="bold")
    for lbl in ax.get_xticklabels():
        lbl.set_color(INK)
    ax.set_ylim(0, 78)
    ax.set_yticks([0, 20, 40, 60])
    ax.set_yticklabels(["0", "20%", "40%", "60%"])
    ax.set_xlim(-0.62, 1.62)
    ax.grid(axis="y", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
    frame(ax)

    fig.text(0.052, 0.955, "What the bond market expects from the Fed",
             fontsize=26, fontweight="bold", color=INK, va="top")
    fig.text(0.052, 0.888,
             "Probability of each outcome at the September 16, 2026 Fed meeting. Current target rate is 3.50% to 3.75%.",
             fontsize=13.5, color=SLATE, va="top")
    fig.text(0.008, 0.035,
             "Source: CME FedWatch, implied by 30-day fed funds futures (ZQU6), September 4, 2026. "
             "Probability of a cut was 0.0%.",
             fontsize=10.5, color=SLATE)
    fig.text(0.008, 0.008,
             "Market-implied odds from futures pricing. Not a forecast and not a Federal Reserve statement. These move daily.",
             fontsize=10.5, color=MUTED)
    add_logo(fig)
    fig.subplots_adjust(left=0.085, right=0.985, top=0.79, bottom=0.175)
    save(fig, f"jobs-fedwatch-{STAMP}.png")


# ======================================================= 2. Unemployment
def chart_unemployment():
    fig, ax = plt.subplots(figsize=(12.6, 6.8), dpi=170)
    fig.patch.set_facecolor(CREAM); ax.set_facecolor(CREAM)

    keys = [k for k, _ in AHE]              # full monthly spine, Jan 2022 on
    have = dict(UR)
    # split into contiguous runs so the missing month is a real gap
    runs, cur = [], []
    for i, k in enumerate(keys):
        if k in have:
            cur.append((i, have[k]))
        elif cur:
            runs.append(cur); cur = []
    if cur:
        runs.append(cur)

    for run in runs:
        ax.plot([p[0] for p in run], [p[1] for p in run], color=CORAL, lw=3.4,
                solid_capstyle="round", zorder=4)
    # dashed bridge across the un-collected month
    for a, b in zip(runs, runs[1:]):
        ax.plot([a[-1][0], b[0][0]], [a[-1][1], b[0][1]], color=CORAL, lw=2.2,
                ls=(0, (3, 3)), alpha=0.55, zorder=3)

    last_i, last_v = runs[-1][-1]
    ax.plot([last_i], [last_v], "o", ms=11, color=CORAL, zorder=6)
    ax.annotate(f"Aug. 2026\n{last_v}%", xy=(last_i, last_v),
                xytext=(last_i + 2.0, last_v), fontsize=15,
                fontweight="bold", color=DEEP, ha="left", va="center", zorder=7)

    ax.set_ylim(3.15, 4.75)
    ax.set_yticks([3.25, 3.5, 3.75, 4.0, 4.25, 4.5])
    ax.set_yticklabels(["3.25", "3.5", "3.75", "4", "4.25", "4.5%"])
    ax.set_xlim(-1.5, len(keys) + 10.0)
    xticks_years(ax, keys, [2022, 2023, 2024, 2025, 2026])
    ax.grid(axis="y", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
    frame(ax)

    fig.text(0.046, 0.955, "U.S. unemployment rate", fontsize=26.5,
             fontweight="bold", color=INK, va="top")
    fig.text(0.046, 0.893, "January 2022 to August 2026", fontsize=14,
             color=SLATE, va="top")
    fig.text(0.008, 0.035, BLS_SRC, fontsize=10.5, color=SLATE)
    fig.text(0.008, 0.008,
             "Dashed segment spans October 2025, when the household survey was not collected and BLS published no rate.",
             fontsize=10.5, color=MUTED)
    add_logo(fig)
    fig.subplots_adjust(left=0.072, right=0.985, top=0.80, bottom=0.145)
    save(fig, f"jobs-unemployment-{STAMP}.png")


# ======================================================== 3. Jobs growth
def chart_jobs():
    fig, ax = plt.subplots(figsize=(12.6, 7.0), dpi=170)
    fig.patch.set_facecolor(CREAM); ax.set_facecolor(CREAM)

    keys = [k for k, _ in JOBS]
    vals = [v for _, v in JOBS]
    xs = list(range(len(keys)))
    colors = []
    for i, v in enumerate(vals):
        if i == len(vals) - 1:
            colors.append(DEEP)                       # August 2026, the subject
        else:
            colors.append(GREEN if v >= 0 else CORAL)
    ax.bar(xs, vals, width=0.66, color=colors, zorder=3)

    ax.text(xs[-1], vals[-1] + 9, f"{vals[-1]:,}K", ha="center", va="bottom",
            fontsize=16, fontweight="bold", color=DEEP, zorder=6)

    ax.axhline(0, color=INK, lw=1.3, zorder=4)
    ax.set_ylim(-200, 275)
    ax.set_yticks([-200, -100, 0, 100, 200])
    ax.yaxis.set_major_formatter(FuncFormatter(
        lambda v, _: "0" if v == 0 else f"{v:,.0f}K"))
    ax.set_xlim(-1.0, len(keys) - 0.1)
    tickmap = [("2024-01", "Jan.\n2024"), ("2024-07", "July"),
               ("2025-01", "Jan.\n2025"), ("2025-07", "July"),
               ("2026-01", "Jan.\n2026"), ("2026-07", "July")]
    ax.set_xticks([keys.index(k) for k, _ in tickmap])
    ax.set_xticklabels([lb for _, lb in tickmap], fontsize=12.5)
    ax.grid(axis="y", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
    frame(ax, xspine=False)

    fig.text(0.046, 0.958, "Monthly jobs growth", fontsize=26.5,
             fontweight="bold", color=INK, va="top")
    fig.text(0.046, 0.897,
             "In August the U.S. economy added 162,000 jobs, bringing the 2026 total so far to 643,000.",
             fontsize=14, color=SLATE, va="top")
    fig.text(0.008, 0.035, BLS_SRC, fontsize=10.5, color=SLATE)
    fig.text(0.008, 0.008,
             "Change in total nonfarm payrolls from the prior month. Figures are revised as later survey responses arrive.",
             fontsize=10.5, color=MUTED)
    add_logo(fig)
    fig.subplots_adjust(left=0.082, right=0.985, top=0.80, bottom=0.145)
    save(fig, f"jobs-growth-{STAMP}.png")


# ============================================================== 4. Wages
def chart_wages():
    fig, ax = plt.subplots(figsize=(12.6, 6.8), dpi=170)
    fig.patch.set_facecolor(CREAM); ax.set_facecolor(CREAM)

    keys = [k for k, _ in AHE]
    vals = [v for _, v in AHE]
    xs = list(range(len(keys)))
    ax.plot(xs, vals, color="#2f6f9e", lw=3.2, solid_capstyle="round", zorder=4)
    ax.plot([xs[-1]], [vals[-1]], "o", ms=11, color="#2f6f9e", zorder=6)
    ax.annotate(f"Aug. 2026\n{vals[-1]:.1f}%", xy=(xs[-1], vals[-1]),
                xytext=(xs[-1] + 2.0, vals[-1]), fontsize=15,
                fontweight="bold", color="#1f5478", ha="left", va="center", zorder=7)

    ax.set_ylim(2.85, 6.15)
    ax.set_yticks([3, 3.5, 4, 4.5, 5, 5.5, 6])
    ax.set_yticklabels(["3", "3.5", "4", "4.5", "5", "5.5", "6%"])
    ax.set_xlim(-1.5, len(keys) + 10.0)
    xticks_years(ax, keys, [2022, 2023, 2024, 2025, 2026])
    ax.grid(axis="y", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
    frame(ax)

    fig.text(0.046, 0.955, "Growth in average hourly earnings",
             fontsize=26.5, fontweight="bold", color=INK, va="top")
    fig.text(0.046, 0.893,
             "Year over year percent change, January 2022 to August 2026. All employees on private nonfarm payrolls.",
             fontsize=14, color=SLATE, va="top")
    fig.text(0.008, 0.035, BLS_SRC, fontsize=10.5, color=SLATE)
    fig.text(0.008, 0.008,
             "August 2026 average hourly earnings were \\$37.75 against \\$36.62 a year earlier, a gain of 3.09%.",
             fontsize=10.5, color=MUTED)
    add_logo(fig)
    fig.subplots_adjust(left=0.072, right=0.985, top=0.80, bottom=0.145)
    save(fig, f"jobs-wages-{STAMP}.png")


# ============================================================ 5. Sectors
def chart_sectors():
    fig, ax = plt.subplots(figsize=(12.6, 8.8), dpi=170)
    fig.patch.set_facecolor(CREAM); ax.set_facecolor(CREAM)

    labels = [r[0] for r in SECTORS]
    vals = [r[1] for r in SECTORS]
    ys = list(range(len(SECTORS) - 1, -1, -1))
    ax.barh(ys, vals, height=0.62, color=[GREEN if v >= 0 else CORAL for v in vals],
            zorder=3)

    for y, v in zip(ys, vals):
        lbl = f"{v:+.1f}K"
        if v >= 0:
            ax.text(v + 0.9, y, lbl, va="center", ha="left", fontsize=13.5,
                    fontweight="bold", color=INK, zorder=5)
        else:
            ax.text(v - 0.9, y, lbl, va="center", ha="right", fontsize=13.5,
                    fontweight="bold", color=INK, zorder=5)

    ax.axvline(0, color=INK, lw=1.3, zorder=4)
    ax.set_yticks(ys)
    ax.set_yticklabels(labels, fontsize=13.5, fontweight="bold")
    for lbl in ax.get_yticklabels():
        lbl.set_color(INK)
    ax.set_xlim(-34, 76)
    ax.set_xticks([-20, 0, 20, 40, 60])
    ax.xaxis.set_major_formatter(FuncFormatter(
        lambda v, _: "0" if v == 0 else f"{v:,.0f}K"))
    ax.set_ylim(-0.8, len(SECTORS) - 0.2)
    ax.grid(axis="x", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
    frame(ax, xspine=False)

    fig.text(0.046, 0.966, "Where the jobs came from, and where they went",
             fontsize=25, fontweight="bold", color=INK, va="top")
    fig.text(0.046, 0.922, "Change in employment by sector, July 2026 to August 2026",
             fontsize=14, color=SLATE, va="top")
    fig.text(0.008, 0.030, BLS_SRC, fontsize=10.5, color=SLATE)
    fig.text(0.008, 0.007,
             "Categories overlap and do not sum to the 162,000 headline. Sectors not shown separately are included in the total.",
             fontsize=10.5, color=MUTED)
    add_logo(fig)
    fig.subplots_adjust(left=0.305, right=0.985, top=0.875, bottom=0.105)
    save(fig, f"jobs-sectors-{STAMP}.png")


if __name__ == "__main__":
    print("building 09/05/26 jobs report chart set")
    chart_fedwatch()
    chart_unemployment()
    chart_jobs()
    chart_wages()
    chart_sectors()
    print("done. EYEBALL every PNG before it ships (label collisions only show visually).")
