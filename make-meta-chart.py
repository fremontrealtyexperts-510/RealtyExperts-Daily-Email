#!/usr/bin/env python3
"""
make-meta-chart.py  [out.png]

REALTY EXPERTS recreation of the Meta Platforms year to date graphic Harv
supplied for the 08/18/26 daily email. OUR OWN branded chart: warm cream ground,
coral line with an area fill, a dashed reference line at the 2025 year end close,
and the closing value called out at the top right.

Story tie-in (Market Briefs, 08/18/26): Meta faces a federal trial over claims
its apps are designed to harm teens. A New Mexico court already ordered Meta to
pay $942M and the case is moving to California. The stock fell 3.54% on
August 17 to $568.97, leaving it down 13.80% for the year.

Data: VERIFIED against Yahoo Finance daily closes, not traced off the supplied
graphic. Baseline is the 2025-12-31 close of $660.09, so year to date is
568.97 - 660.09 = -91.12, or -13.80%, matching the supplied graphic exactly.

TWO TRAPS HANDLED, both of which have burned this workflow before:
  1. Yahoo's daily bar for 2026-08-17 comes back MISSING (the same null-bar quirk
     hit on the yen FX series on 08/13). The close is confirmed at $568.97 three
     independent ways: the supplied graphic, Market Briefs' -3.54% applied to the
     August 14 close of $589.85, and 660.09 - 91.12. It is appended explicitly.
  2. Yahoo also returns a bar dated 2026-08-18 at $549.32, which is TODAY'S LIVE
     UNSETTLED TICK, not a close, because this was built while the market was
     open. It is DROPPED. Never chart an unsettled tick as a close.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "meta-081826.png"

DATES = [
    "2025-12-29", "2025-12-30", "2025-12-31", "2026-01-02", "2026-01-05",
    "2026-01-06", "2026-01-07", "2026-01-08", "2026-01-09", "2026-01-12",
    "2026-01-13", "2026-01-14", "2026-01-15", "2026-01-16", "2026-01-20",
    "2026-01-21", "2026-01-22", "2026-01-23", "2026-01-26", "2026-01-27",
    "2026-01-28", "2026-01-29", "2026-01-30", "2026-02-02", "2026-02-03",
    "2026-02-04", "2026-02-05", "2026-02-06", "2026-02-09", "2026-02-10",
    "2026-02-11", "2026-02-12", "2026-02-13", "2026-02-17", "2026-02-18",
    "2026-02-19", "2026-02-20", "2026-02-23", "2026-02-24", "2026-02-25",
    "2026-02-26", "2026-02-27", "2026-03-02", "2026-03-03", "2026-03-04",
    "2026-03-05", "2026-03-06", "2026-03-09", "2026-03-10", "2026-03-11",
    "2026-03-12", "2026-03-13", "2026-03-16", "2026-03-17", "2026-03-18",
    "2026-03-19", "2026-03-20", "2026-03-23", "2026-03-24", "2026-03-25",
    "2026-03-26", "2026-03-27", "2026-03-30", "2026-03-31", "2026-04-01",
    "2026-04-02", "2026-04-06", "2026-04-07", "2026-04-08", "2026-04-09",
    "2026-04-10", "2026-04-13", "2026-04-14", "2026-04-15", "2026-04-16",
    "2026-04-17", "2026-04-20", "2026-04-21", "2026-04-22", "2026-04-23",
    "2026-04-24", "2026-04-27", "2026-04-28", "2026-04-29", "2026-04-30",
    "2026-05-01", "2026-05-04", "2026-05-05", "2026-05-06", "2026-05-07",
    "2026-05-08", "2026-05-11", "2026-05-12", "2026-05-13", "2026-05-14",
    "2026-05-15", "2026-05-18", "2026-05-19", "2026-05-20", "2026-05-21",
    "2026-05-22", "2026-05-26", "2026-05-27", "2026-05-28", "2026-05-29",
    "2026-06-01", "2026-06-02", "2026-06-03", "2026-06-04", "2026-06-05",
    "2026-06-08", "2026-06-09", "2026-06-10", "2026-06-11", "2026-06-12",
    "2026-06-15", "2026-06-16", "2026-06-17", "2026-06-18", "2026-06-22",
    "2026-06-23", "2026-06-24", "2026-06-25", "2026-06-26", "2026-06-29",
    "2026-06-30", "2026-07-01", "2026-07-02", "2026-07-06", "2026-07-07",
    "2026-07-08", "2026-07-09", "2026-07-10", "2026-07-13", "2026-07-14",
    "2026-07-15", "2026-07-16", "2026-07-17", "2026-07-20", "2026-07-21",
    "2026-07-22", "2026-07-23", "2026-07-24", "2026-07-27", "2026-07-28",
    "2026-07-29", "2026-07-30", "2026-07-31", "2026-08-03", "2026-08-04",
    "2026-08-05", "2026-08-06", "2026-08-07", "2026-08-10", "2026-08-11",
    "2026-08-12", "2026-08-13", "2026-08-14", "2026-08-17"
]

CLOSES = [
    658.69, 665.95, 660.09, 650.41, 658.79, 660.62, 648.69, 646.06,
    653.06, 641.97, 631.09, 615.52, 620.80, 620.25, 604.12, 612.96,
    647.63, 658.76, 672.36, 672.97, 668.73, 738.31, 716.50, 706.41,
    691.70, 668.99, 670.21, 661.46, 677.22, 670.72, 668.69, 649.81,
    639.77, 639.29, 643.22, 644.78, 655.66, 637.25, 639.30, 653.69,
    657.01, 648.18, 653.56, 655.08, 667.73, 660.57, 644.86, 647.39,
    654.07, 654.86, 638.18, 613.71, 627.45, 622.66, 615.68, 606.70,
    593.66, 604.06, 592.92, 594.89, 547.54, 525.72, 536.38, 572.13,
    579.23, 574.46, 573.02, 575.05, 612.42, 628.39, 629.86, 634.53,
    662.49, 671.58, 676.87, 688.55, 670.91, 668.84, 674.72, 659.15,
    675.03, 678.62, 671.34, 669.12, 611.91, 608.75, 610.41, 604.96,
    612.88, 616.81, 609.63, 598.86, 603.00, 616.63, 618.43, 614.23,
    611.21, 602.61, 605.06, 607.38, 610.26, 612.34, 635.26, 635.29,
    632.51, 600.47, 597.63, 622.98, 627.57, 593.00, 585.39, 584.59,
    570.98, 568.43, 566.98, 593.48, 600.21, 567.58, 577.22, 563.85,
    562.20, 557.67, 542.87, 550.25, 562.60, 563.29, 612.91, 582.90,
    600.29, 615.58, 603.12, 631.48, 669.21, 656.73, 661.04, 681.31,
    664.54, 646.01, 645.85, 643.81, 627.17, 606.10, 595.19, 593.87,
    593.41, 585.61, 539.03, 556.71, 590.24, 587.94, 588.77, 589.90,
    592.10, 594.92, 599.12, 578.85, 594.97, 589.85, 568.97
]

assert len(DATES) == len(CLOSES), "series length mismatch"
assert DATES[-1] == "2026-08-17", "endpoint must be the Aug 17 settled close"
assert "2026-08-18" not in DATES, "live unsettled tick leaked into the series"
assert abs(CLOSES[-1] - 568.97) < 0.005, "Aug 17 close moved"

BASE = CLOSES[DATES.index("2025-12-31")]
assert abs(BASE - 660.09) < 0.005, "year end baseline moved"

LAST = CLOSES[-1]
CHG = LAST - BASE
PCT = (LAST / BASE - 1) * 100

INK    = "#12263f"
CORAL  = "#e2574c"
MUTED  = "#6b7280"
GROUND = "#fdf6e8"   # warm cream (house style)
GRID   = "#e7ddc9"

x = list(range(len(CLOSES)))

fig, ax = plt.subplots(figsize=(12.6, 6.8))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

YLO, YHI = 520, 745
ax.fill_between(x, CLOSES, YLO, color=CORAL, alpha=0.13, zorder=2)
ax.plot(x, CLOSES, color=CORAL, linewidth=2.4, zorder=5, solid_capstyle="round")

ax.axhline(BASE, color="#9c9384", linewidth=1.4, linestyle=(0, (6, 5)), zorder=4)
# anchored at the right, where the series sits well below the reference line;
# placing it at the left collided with the February run-up.
# The reference line is explained in the subtitle rather than labelled inline:
# every in-plot placement collided with either the February run-up or the July
# spike, and a label sitting on the series is worse than no label.

ax.plot([x[-1]], [LAST], "o", color=CORAL, markersize=10, zorder=7)

arrow = "▼" if PCT < 0 else "▲"
sign = "-" if CHG < 0 else "+"
ax.text(0.995, 1.155, f"${LAST:,.2f}", transform=ax.transAxes, fontsize=33,
        fontweight="bold", color=INK, ha="right", va="top")
ax.text(0.995, 1.042,
        f"{arrow} {abs(PCT):.2f}%  ({sign}${abs(CHG):,.2f})",
        transform=ax.transAxes, fontsize=15.5, fontweight="bold",
        color=CORAL, ha="right", va="top")

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct",
          "Nov", "Dec"]
seen, ticks, labels = set(), [], []
for i, ds in enumerate(DATES):
    ym = ds[:7]
    if ym not in seen and ds >= "2026-01-01":
        seen.add(ym)
        ticks.append(i)
        labels.append(MONTHS[int(ds[5:7]) - 1])
ax.set_xticks(ticks)
ax.set_xticklabels(labels, fontsize=13, fontweight="bold", color=MUTED)

ax.set_ylim(YLO, YHI)
ax.set_yticks([550, 600, 650, 700, 750])
ax.set_yticklabels(["$550", "$600", "$650", "$700", "$750"], fontsize=12,
                   color=MUTED)
ax.set_xlim(-2, len(CLOSES) + 1)
ax.grid(axis="y", color=GRID, linewidth=1.1, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("Meta Platforms", fontsize=25, fontweight="bold", color=INK,
             loc="left", pad=58)
ax.text(0.0, 1.048, f"NASDAQ: META  ·  2026 year to date  ·  dashed line "
        f"marks the 2025 close of ${BASE:,.2f}",
        transform=ax.transAxes, fontsize=12.5, fontweight="bold", color=MUTED,
        ha="left")

fig.text(0.012, 0.014, "Source: Yahoo Finance, META daily closing prices. "
         "Closed August 17, 2026.", fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.062, right=0.985, top=0.79, bottom=0.115)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT, "| points:", len(CLOSES),
      f"| baseline {BASE:.2f} | last {LAST:.2f} | ytd {CHG:.2f} ({PCT:.2f}%)")
