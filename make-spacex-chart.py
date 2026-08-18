#!/usr/bin/env python3
"""
make-spacex-chart.py  [out.png]

Creative REALTY EXPERTS recreation of the SpaceX share price graphic Harv supplied
for the 08/03/26 daily email. OUR OWN branded chart, not the source image: warm
cream ground, a coral price line with a soft fill, the June record high flagged,
the $135 IPO price drawn as a reference line, and the closing price called out in
a pill.

Story tie-in (Market Briefs "Shorting SpaceX", 08/03/26): traders are betting hard
against SpaceX ahead of a share unlock that frees up to 911.5 million shares just
after its first earnings. About 34% of shares outstanding have been sold short.
The price path lands in the Stocks section.

Data: SpaceX (SPCX) daily closing prices, pulled from the Yahoo Finance daily
series, NOT transcribed from the source graphic. June 12, 2026 market debut close
of $160.95 through the July 31, 2026 close of $108.37, down 32.67% ($52.58).

NOTE on framing: the source graphic labels this "year to date," but SPCX only
began trading on June 12, 2026, so a year-to-date frame is wrong. This chart is
labeled "since its market debut," which is what the series actually covers.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "spacex-080326.png"

# (date, close) SPCX daily closes, Yahoo Finance daily series.
DATA = [
    ("06-12", 160.95), ("06-15", 192.50), ("06-16", 211.39), ("06-17", 191.82),
    ("06-18", 185.00), ("06-22", 154.60), ("06-23", 156.11), ("06-24", 154.54),
    ("06-25", 153.00), ("06-26", 153.23), ("06-29", 164.19), ("06-30", 170.86),
    ("07-01", 157.54), ("07-02", 162.00), ("07-06", 160.42), ("07-07", 149.47),
    ("07-08", 148.30), ("07-09", 152.16), ("07-10", 145.30), ("07-13", 139.14),
    ("07-14", 136.08), ("07-15", 135.27), ("07-16", 131.11), ("07-17", 123.99),
    ("07-20", 119.85), ("07-21", 123.54), ("07-22", 115.26), ("07-23", 118.24),
    ("07-24", 115.07), ("07-27", 113.50), ("07-28", 116.41), ("07-29", 112.55),
    ("07-30", 112.20), ("07-31", 108.37),
]
PRICES = [v for _, v in DATA]
START = PRICES[0]          # 160.95, the debut close
END = PRICES[-1]           # 108.37, the July 31 close
CHG_DOL = END - START      # -52.58
CHG_PCT = CHG_DOL / START * 100.0   # -32.67%
IPO_PRICE = 135.00         # priced at $135 in the June 11 IPO

PEAK_I = PRICES.index(max(PRICES))   # June 16 record high, $211.39

# tick every Monday-ish anchor so the axis reads cleanly
MONTH_TICKS = [(0, "Jun 12"), (5, "Jun 22"), (12, "Jul 1"),
               (19, "Jul 13"), (24, "Jul 20"), (29, "Jul 27"), (33, "Jul 31")]

CORAL   = "#ef5350"
CORAL_D = "#c62828"
INK     = "#12263f"
MUTED   = "#6b7280"
GROUND  = "#fdf6e8"   # warm cream (house style)
GRID    = "#e7ddc9"

FLOOR = 95            # baseline for the area fill

x = list(range(len(PRICES)))

fig, ax = plt.subplots(figsize=(12, 6.4))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.plot(x, PRICES, color=CORAL, linewidth=2.8, zorder=4, solid_capstyle="round")
ax.fill_between(x, PRICES, FLOOR, color=CORAL, alpha=0.13, zorder=2)

# $135 IPO price reference, so "below its IPO price" reads visually
ax.axhline(IPO_PRICE, color="#b9ad93", linewidth=1.4, linestyle=(0, (4, 4)),
           zorder=3)
# label parked on the right, where the price line has already dropped clear of it
ax.text(24.0, IPO_PRICE + 3, f"IPO priced at ${IPO_PRICE:,.0f}",
        fontsize=11, color="#8a8172", ha="left", zorder=5)

# June record high callout
ax.plot([PEAK_I], [PRICES[PEAK_I]], "o", color=CORAL_D, markersize=7, zorder=5)
ax.annotate(f"Jun 16 high  ${PRICES[PEAK_I]:,.2f}",
            xy=(PEAK_I, PRICES[PEAK_I]),
            xytext=(PEAK_I + 1.0, PRICES[PEAK_I] + 3),
            fontsize=12, fontweight="bold", color=CORAL_D, zorder=6)

# debut close marker
ax.plot([0], [START], "o", color=CORAL_D, markersize=6, zorder=5)
ax.annotate(f"Debut close  ${START:,.2f}", xy=(0, START),
            xytext=(0.7, START - 14),
            fontsize=11.5, fontweight="bold", color="#8a8172", zorder=6)

# closing price pill
ax.plot([x[-1]], [END], "o", color=CORAL_D, markersize=8, zorder=6)
ax.annotate(f"${END:,.2f}", xy=(x[-1], END), xytext=(x[-1] + 0.7, END),
            fontsize=15, fontweight="bold", color="white", va="center",
            zorder=7,
            bbox=dict(boxstyle="round,pad=0.42", facecolor=CORAL_D,
                      edgecolor="none"))

ax.set_xlim(-0.6, len(PRICES) + 3.0)
ax.set_ylim(FLOOR, 228)
ax.set_yticks([100, 120, 140, 160, 180, 200, 220])
ax.set_yticklabels(["100", "120", "140", "160", "180", "200", "220"],
                   fontsize=12, color=MUTED)
ax.set_xticks([i for i, _ in MONTH_TICKS])
ax.set_xticklabels([m for _, m in MONTH_TICKS], fontsize=12,
                   fontweight="bold", color=MUTED)
ax.grid(axis="y", color=GRID, linewidth=1.1, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("SpaceX Has Given Back A Third Since Its Debut", fontsize=25,
             fontweight="bold", color=INK, loc="left", pad=30)
ax.text(0.0, 1.045, "SPCX share price, since its market debut",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="left")
ax.text(1.0, 1.045, f"{CHG_PCT:.2f}%  (-${abs(CHG_DOL):,.2f})  SINCE DEBUT",
        transform=ax.transAxes, fontsize=14.5, fontweight="bold",
        color=CORAL_D, ha="right")

fig.text(0.012, 0.014,
         "Source: Yahoo Finance. Daily closes, June 12 to July 31, 2026.",
         fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.062, right=0.985, top=0.82, bottom=0.085)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT,
      f"| sessions: {len(PRICES)} | debut ${START:,.2f} | close ${END:,.2f} "
      f"| {CHG_PCT:.2f}% (${CHG_DOL:,.2f}) | vs IPO ${IPO_PRICE:,.0f}: "
      f"{(END/IPO_PRICE-1)*100:.1f}%")
