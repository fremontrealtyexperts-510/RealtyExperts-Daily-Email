#!/usr/bin/env python3
"""
make-copper-chart.py  [out.png]

REALTY EXPERTS recreation of the copper graphic Harv supplied for the 08/07/26
daily email. OUR OWN branded chart on the house cream ground, with a copper-toned
price line, the March low and the record close both flagged, and the last settled
price called out in a pill.

WHY IT WAS REBUILT RATHER THAN COPIED (a supplied graphic is a design brief, not a
data source). Every point here is pulled from the COMEX front-month copper series,
and three claims on the supplied image did not survive the check:
  1. It printed $6.76 as the August 6 price. The August 6 SETTLEMENT was $6.687.
     $6.7655 is the intraday high on August 7, the session that had not settled
     when the graphic went out, so a live tick was labeled as a prior-day close.
  2. Its title said "Highest Price of 2026". August 6 was a DOWN day (-0.24%).
     The record close is $6.703 on August 5.
  3. It said "up 19% year to date". Through the August 6 close the gain is 18.56%.
Market Briefs' own stat line was worse: it printed COPPER $6.17 (-0.01%) against
an actual $6.687 (-0.24%), and its story claimed copper "neared $6.90 a pound"
when the highest tick in the entire series is $6.7655.

What DID check out: copper really is at a record. The August 5 close of $6.703 is
the highest in the COMEX series going back to 2000, so the story is sound even
though the numbers on the picture were not.

Story tie-in (Market Briefs, 08/07/26): copper at a record on supply disruption
and AI data center demand rather than broad growth. Macro metal, so it lands in
the Economy section.

NOTE (restored 2026-08-12): this file is git-TRACKED. The 08/07 rebuild was written
locally but never pushed, and the Mac launchd auto-pull reverted it to the old
06/25/26 version. Reconstructed and pushed so the reproducibility record survives.
Anything edited here must be pushed the same day via a /tmp clone, because
push-to-github.sh does NOT carry make-*.py.

No authorship label on the chart (per Harv, 06/29): the footer carries only the
data source. matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "copper-080726.png"

# COMEX front-month copper (HG) daily settlements, 2026-01-02 through 2026-08-06.
CLOSES = [
    5.6400, 5.9245, 6.0105, 5.8090, 5.7465, 5.8555, 5.9850, 5.9700,
    6.0090, 5.9480, 5.7885, 5.7730, 5.7295, 5.7425, 5.9110, 5.9840,
    5.8285, 5.8925, 6.1755, 5.8970, 5.8015, 6.0625, 5.8260, 5.7990,
    5.8635, 5.9450, 5.8960, 5.9490, 5.7710, 5.7925, 5.6330, 5.7935,
    5.7300, 5.8310, 5.7730, 5.9230, 5.9795, 5.9470, 6.0045, 5.8945,
    5.7735, 5.8550, 5.7530, 5.7570, 5.8005, 5.9040, 5.8455, 5.8245,
    5.7145, 5.7905, 5.7265, 5.5540, 5.4330, 5.3425, 5.4395, 5.4225,
    5.5290, 5.4465, 5.4670, 5.4760, 5.5875, 5.6240, 5.5630, 5.5835,
    5.5445, 5.7595, 5.7480, 5.8705, 5.9760, 6.0705, 6.0720, 6.0665,
    6.1035, 6.0360, 6.0015, 6.1200, 6.0755, 6.0235, 6.0180, 5.9145,
    5.8785, 5.9260, 5.9320, 5.7950, 5.9430, 6.1365, 6.1275, 6.2490,
    6.4135, 6.4850, 6.6355, 6.5675, 6.2515, 6.2720, 6.1650, 6.2905,
    6.2570, 6.3420, 6.3610, 6.3050, 6.3960, 6.3595, 6.5240, 6.6495,
    6.4810, 6.5110, 6.2635, 6.3295, 6.3025, 6.2490, 6.2590, 6.4305,
    6.4825, 6.4890, 6.4815, 6.3745, 6.3565, 6.1410, 5.9430, 6.0705,
    6.1415, 6.0975, 6.1925, 6.1235, 6.1145, 6.1780, 6.1715, 6.0545,
    6.2150, 6.2335, 6.2330, 6.3300, 6.2935, 6.2960, 6.2200, 6.2990,
    6.5110, 6.4510, 6.3050, 6.3200, 6.3390, 6.3220, 6.2735, 6.4445,
    6.4360, 6.5140, 6.6185, 6.7030, 6.6870,
]

BASE = CLOSES[0]                     # 5.64, the January 2 close
END = CLOSES[-1]                     # 6.687, the August 6 settlement
CHG_PCT = (END / BASE - 1) * 100.0   # +18.56%

PEAK = max(CLOSES)                   # 6.703, the record close on August 5
LOW_I = CLOSES.index(min(CLOSES))    # March 20 low, 5.3425

# index of the first session of each month
MONTH_TICKS = [(0, "JAN"), (20, "FEB"), (39, "MAR"), (61, "APR"),
               (82, "MAY"), (102, "JUN"), (123, "JUL"), (145, "AUG")]

COPPER = "#c9702f"
COPPER_D = "#9c4f1c"
INK = "#12263f"
MUTED = "#6b7280"
GROUND = "#fdf6e8"   # warm cream (house style)
GRID = "#e7ddc9"

FLOOR = 5.1          # baseline for the area fill

x = list(range(len(CLOSES)))

fig, ax = plt.subplots(figsize=(12, 6.4))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.plot(x, CLOSES, color=COPPER, linewidth=2.6, zorder=4, solid_capstyle="round")
ax.fill_between(x, CLOSES, FLOOR, color=COPPER, alpha=0.14, zorder=2)

# record-close line, so the reader sees the ceiling the price just reached
ax.axhline(PEAK, color="#b9ad93", linewidth=1.4, linestyle=(0, (4, 4)), zorder=3)
ax.text(1.0, PEAK + 0.022, f"Record close ${PEAK:.2f} on Aug 5",
        fontsize=11, color="#8a8172", ha="left", zorder=5)

# where the year started
ax.axhline(BASE, color="#cbbfa6", linewidth=1.2, linestyle=(0, (4, 4)), zorder=3)
ax.text(1.0, BASE - 0.105, f"Started the year at ${BASE:.2f}",
        fontsize=11, color="#8a8172", ha="left", zorder=5)

# March low callout, parked below the point where the panel is empty
ax.plot([LOW_I], [CLOSES[LOW_I]], "o", color=COPPER_D, markersize=7, zorder=5)
ax.annotate(f"Mar 20 low  ${CLOSES[LOW_I]:.2f}",
            xy=(LOW_I, CLOSES[LOW_I]), xytext=(LOW_I + 3, CLOSES[LOW_I] - 0.145),
            fontsize=12, fontweight="bold", color=COPPER_D, ha="left", zorder=6)

# last settled price pill
ax.plot([x[-1]], [END], "o", color=COPPER_D, markersize=8, zorder=6)
ax.annotate(f"${END:.2f}", xy=(x[-1], END), xytext=(x[-1] + 2.5, END),
            fontsize=15, fontweight="bold", color="white", va="center",
            zorder=7,
            bbox=dict(boxstyle="round,pad=0.42", facecolor=COPPER_D,
                      edgecolor="none"))

ax.set_xlim(-1.5, len(CLOSES) + 16)
ax.set_ylim(FLOOR, 6.95)
ax.set_yticks([5.25, 5.50, 5.75, 6.00, 6.25, 6.50, 6.75])
ax.set_yticklabels(["$5.25", "$5.50", "$5.75", "$6.00", "$6.25", "$6.50", "$6.75"],
                   fontsize=12, color=MUTED)
ax.set_xticks([i for i, _ in MONTH_TICKS])
ax.set_xticklabels([m for _, m in MONTH_TICKS], fontsize=12.5,
                   fontweight="bold", color=MUTED)
ax.grid(axis="y", color=GRID, linewidth=1.1, linestyle=(0, (5, 5)), zorder=1)
ax.tick_params(length=0)
for sp in ("top", "right", "left", "bottom"):
    ax.spines[sp].set_visible(False)

ax.set_title("Copper Is Trading At The Highest Price On Record", fontsize=24,
             fontweight="bold", color=INK, loc="left", pad=30)
ax.text(0.0, 1.045,
        "COMEX front-month copper futures, dollars per pound, 2026 year to date",
        transform=ax.transAxes, fontsize=13, color=MUTED, ha="left")
ax.text(1.0, 1.045, f"+{CHG_PCT:.1f}%  YEAR TO DATE",
        transform=ax.transAxes, fontsize=14.5, fontweight="bold",
        color=COPPER_D, ha="right")

fig.text(0.012, 0.014,
         "Source: COMEX front-month copper futures (HG), daily settlements. "
         "January 2 to August 6, 2026.",
         fontsize=9.5, color="#a99f88", ha="left")

fig.subplots_adjust(left=0.075, right=0.985, top=0.82, bottom=0.085)
fig.savefig(OUT, dpi=150, facecolor=GROUND)
plt.close(fig)
print("wrote", OUT,
      f"| sessions: {len(CLOSES)} | base ${BASE:.4f} | close ${END:.4f} "
      f"| YTD {CHG_PCT:+.2f}% | low ${min(CLOSES):.4f} | record close ${PEAK:.4f}")
