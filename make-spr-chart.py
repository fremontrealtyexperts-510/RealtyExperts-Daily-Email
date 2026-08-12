#!/usr/bin/env python3
"""
make-spr-chart.py  [out.png]

REALTY EXPERTS recreation of the Strategic Petroleum Reserve graphic Harv supplied
for the 08/11/26 daily email. OUR OWN branded chart on the house cream ground: the
full 44-year history, the 2010 peak flagged, the 1983 reference level the reserve
has just fallen back to, and the latest PUBLISHED level called out in a pill.

WHY THE ENDPOINT DIFFERS FROM THE SUPPLIED GRAPHIC (a supplied graphic is a design
brief, not a data source). The image ends at "Aug. 7, 2026 = 298.7M". That week does
not exist yet:
  * EIA's weekly series (WCSSTUS1) was last updated Wed 2026-08-05 (verified by the
    file's own Last-Modified header, and byte-identical on a cache-busted re-fetch).
  * Its latest published observation is week ending 2026-07-31 = 304,809 thousand
    barrels. The week ending 08-07 publishes Wed 2026-08-12, the day AFTER this
    report ships.
So 298.7M is an unpublished figure presented as EIA data. Market Briefs printed the
same 298.7M on 08/11. This chart ends at the last point EIA has actually released.

WHAT DID CHECK OUT on the supplied image:
  * "727M peak" -> the all-time high is 726.615M in January 2010. Rounds correctly.
  * "Lowest point since 1983" -> TRUE even at the published 304.809M. The last week
    at or below that level was 1983-02-18, during the reserve's original fill.
So the story is sound; only the endpoint was borrowed from a week nobody has seen.

Data: EIA Weekly U.S. Ending Stocks of Crude Oil in SPR (WCSSTUS1), thousand barrels,
downloaded from eia.gov and thinned to MONTH-END observations (month-end, not
month-start, so the final point is the true latest week rather than 2026-07-03).
528 contiguous months, 1982-08 through 2026-07.

No authorship label on the chart (per Harv, 06/29): the footer carries only the data
source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "spr-081126.png"

# EIA WCSSTUS1, month-end observations in MILLIONS of barrels, 1982-08 .. 2026-07.
STOCKS = [
    272.603, 276.833, 284.268, 288.156, 293.214, 298.379, 305.348, 310.320, 317.456, 324.116,
    330.079, 339.962, 349.031, 360.456, 366.141, 370.630, 378.309, 384.455, 386.935, 391.798,
    395.957, 400.842, 412.610, 420.094, 429.467, 431.066, 433.895, 443.046, 449.157, 454.165,
    458.753, 461.266, 464.051, 471.336, 476.150, 482.052, 486.860, 489.249, 489.616, 491.057,
    492.666, 494.389, 495.057, 496.590, 498.170, 499.479, 501.384, 503.095, 504.973, 506.381,
    507.518, 509.267, 511.001, 513.935, 516.491, 518.918, 521.250, 524.820, 526.772, 529.670,
    531.971, 533.395, 535.305, 537.707, 540.158, 542.432, 543.656, 544.927, 546.690, 547.597,
    549.361, 551.345, 552.141, 554.146, 556.003, 558.179, 559.513, 561.186, 563.374, 565.578,
    567.430, 569.420, 571.721, 574.045, 574.732, 577.128, 577.782, 579.487, 579.854, 580.228,
    580.925, 581.417, 582.656, 586.181, 586.686, 586.678, 589.623, 589.623, 589.623, 586.903,
    585.692, 585.692, 583.245, 571.410, 568.482, 568.483, 568.483, 568.488, 568.502, 568.503,
    568.503, 568.505, 568.502, 568.508, 568.510, 568.510, 568.511, 568.511, 569.521, 569.520,
    570.092, 570.322, 573.503, 573.837, 574.562, 575.247, 575.721, 577.378, 581.485, 582.037,
    582.425, 582.939, 583.837, 585.508, 586.079, 586.627, 587.018, 587.164, 587.192, 589.169,
    591.179, 591.173, 591.178, 591.670, 591.673, 591.675, 591.676, 591.674, 591.673, 591.670,
    591.671, 591.673, 591.672, 591.671, 591.669, 591.672, 591.670, 591.673, 591.668, 591.663,
    591.648, 591.640, 591.630, 589.122, 586.493, 585.815, 584.469, 583.114, 578.649, 573.665,
    573.659, 571.119, 567.467, 563.793, 563.482, 563.474, 563.479, 563.463, 563.459, 563.455,
    563.452, 563.449, 563.444, 563.439, 563.430, 563.479, 563.430, 563.426, 563.426, 563.426,
    563.428, 563.429, 563.426, 563.426, 563.426, 564.015, 568.525, 571.405, 571.951, 571.951,
    571.951, 572.452, 573.595, 574.799, 575.702, 574.876, 575.472, 569.836, 567.684, 568.414,
    569.095, 569.412, 569.413, 569.413, 568.417, 569.467, 571.106, 570.668, 567.886, 554.277,
    541.188, 540.678, 541.676, 542.291, 542.350, 543.270, 543.270, 543.733, 543.734, 544.759,
    544.760, 547.325, 549.047, 553.504, 559.171, 560.915, 565.517, 570.742, 575.417, 578.048,
    580.885, 585.283, 588.563, 594.637, 598.895, 599.247, 599.247, 599.247, 599.448, 602.527,
    607.327, 610.700, 616.993, 622.000, 629.986, 633.380, 636.355, 641.063, 646.581, 650.882,
    657.588, 660.346, 662.380, 664.516, 668.516, 670.442, 669.715, 671.247, 674.000, 678.627,
    681.513, 686.878, 691.215, 693.295, 695.800, 698.205, 700.500, 693.250, 685.200, 685.100,
    684.600, 683.700, 684.600, 686.300, 687.614, 688.598, 688.598, 687.846, 687.842, 687.838,
    688.438, 688.605, 688.605, 688.605, 688.605, 688.603, 689.313, 689.988, 690.270, 690.270,
    690.271, 692.804, 693.943, 695.409, 696.375, 698.145, 698.711, 699.750, 701.339, 704.102,
    705.823, 706.300, 707.213, 704.414, 701.833, 701.830, 701.824, 703.519, 704.903, 711.015,
    716.673, 721.700, 723.419, 724.096, 724.092, 725.087, 725.082, 725.603, 726.127, 726.615,
    726.610, 726.607, 726.601, 726.595, 726.592, 726.589, 726.583, 726.350, 726.552, 726.548,
    726.546, 726.544, 726.543, 726.542, 726.542, 726.542, 726.531, 719.761, 701.825, 695.953,
    695.951, 695.951, 695.951, 695.951, 695.951, 695.951, 695.951, 695.951, 695.951, 695.950,
    695.950, 694.952, 694.952, 694.952, 694.952, 695.460, 695.969, 695.969, 695.969, 695.969,
    695.969, 695.969, 695.969, 695.969, 695.969, 695.969, 695.969, 695.969, 695.969, 695.969,
    693.613, 690.971, 690.972, 690.972, 690.972, 690.970, 690.967, 690.965, 690.963, 690.957,
    690.955, 690.952, 690.948, 692.346, 693.692, 695.134, 695.133, 695.128, 695.127, 695.125,
    695.120, 695.117, 695.115, 695.112, 695.108, 695.106, 695.104, 695.099, 695.094, 695.091,
    695.088, 695.085, 695.082, 695.079, 695.076, 692.135, 689.338, 686.682, 682.037, 678.884,
    678.880, 673.649, 670.587, 665.111, 663.748, 664.686, 665.281, 665.456, 664.266, 660.777,
    660.016, 660.014, 660.012, 660.010, 654.935, 649.561, 649.139, 649.139, 649.139, 649.126,
    648.587, 644.818, 644.818, 644.818, 644.818, 644.818, 641.652, 635.166, 634.967, 634.967,
    634.967, 634.967, 636.117, 647.779, 655.413, 656.141, 648.165, 643.151, 639.270, 638.190,
    638.085, 638.086, 637.773, 637.773, 633.427, 627.833, 622.487, 621.304, 621.302, 618.689,
    612.541, 602.556, 593.682, 588.912, 580.020, 568.322, 549.985, 526.592, 497.868, 469.855,
    449.998, 416.389, 399.792, 389.116, 372.380, 371.579, 371.579, 371.175, 364.938, 355.436,
    347.159, 346.759, 349.542, 351.280, 351.274, 351.587, 354.388, 357.402, 360.254, 363.641,
    366.271, 370.187, 372.595, 375.097, 379.672, 382.553, 385.831, 391.807, 393.570, 395.064,
    395.313, 396.434, 398.542, 401.822, 402.765, 402.741, 404.710, 406.700, 409.595, 411.674,
    413.219, 415.213, 415.441, 415.064, 397.924, 357.119, 325.655, 304.809,
]

END = STOCKS[-1]                 # 304.809M, week ending 2026-07-31
PEAK = max(STOCKS)               # 726.615M, January 2010
PEAK_I = STOCKS.index(PEAK)

# index 0 = 1982-08, one point per month
MONTH_TICKS = [(29, "1985"), (149, "1995"), (269, "2005"), (389, "2015"), (509, "2025")]

OIL = "#c9702f"
OIL_D = "#9c4f1c"
INK = "#12263f"
MUTED = "#6b7280"
GROUND = "#fdf6e8"   # warm cream (house style)
GRID = "#e7ddc9"

FLOOR = 0

x = list(range(len(STOCKS)))

fig, ax = plt.subplots(figsize=(12, 6.4))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.plot(x, STOCKS, color=OIL, linewidth=2.4, zorder=4, solid_capstyle="round")
ax.fill_between(x, STOCKS, FLOOR, color=OIL, alpha=0.13, zorder=2)

# the level the reserve has fallen back to, and when it was last here
ax.axhline(END, color="#b9ad93", linewidth=1.3, linestyle=(0, (4, 4)), zorder=3)
ax.text(150, END - 42, "Last at this level in February 1983",
        fontsize=11, color="#8a8172", ha="left", zorder=5)

# 2010 peak
ax.plot([PEAK_I], [PEAK], "o", color=OIL_D, markersize=7, zorder=6)
ax.annotate(f"{PEAK:.0f}M peak, Jan 2010",
            xy=(PEAK_I, PEAK), xytext=(PEAK_I - 12, PEAK + 42),
            fontsize=12, fontweight="bold", color=OIL_D, ha="center", zorder=6)

# latest published level
ax.plot([x[-1]], [END], "o", color=OIL_D, markersize=8, zorder=6)
ax.annotate(f"{END:.1f}M", xy=(x[-1], END), xytext=(x[-1] + 12, END),
            fontsize=15, fontweight="bold", color="white", va="center", zorder=7,
            bbox=dict(boxstyle="round,pad=0.42", facecolor=OIL_D, edgecolor="none"))

ax.set_xlim(-8, len(STOCKS) + 78)
ax.set_ylim(FLOOR, 830)
ax.set_yticks([0, 200, 400, 600, 800])
ax.set_yticklabels(["0", "200M", "400M", "600M", "800M"], fontsize=12, color=MUTED)
ax.set_xticks([i for i, _ in MONTH_TICKS])
ax.set_xticklabels([m for _, m in MONTH_TICKS], fontsize=12.5,
                   fontweight="bold", color=MUTED)
ax.grid(axis="y", color=GRID, linewidth=1.1, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("The U.S. Emergency Oil Reserve Is Back To 1983 Levels", fontsize=23,
             fontweight="bold", color=INK, loc="left", pad=30)
ax.text(0.0, 1.045,
        "U.S. crude oil stocks in the Strategic Petroleum Reserve, barrels, month end",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="left")
ax.text(1.0, 1.045, "DOWN 58% FROM THE PEAK",
        transform=ax.transAxes, fontsize=14.5, fontweight="bold",
        color=OIL_D, ha="right")

fig.text(0.012, 0.014,
         "Source: U.S. Energy Information Administration, weekly series WCSSTUS1. "
         "August 1982 to the week ending July 31, 2026, the latest published.",
         fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.075, right=0.985, top=0.82, bottom=0.085)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT,
      f"| months: {len(STOCKS)} | peak {PEAK:.3f}M (idx {PEAK_I}) "
      f"| last {END:.3f}M | down {(1 - END / PEAK) * 100:.1f}% from peak")
