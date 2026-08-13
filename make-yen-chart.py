#!/usr/bin/env python3
"""
make-yen-chart.py  [out.png]

REALTY EXPERTS branded recreation of the "The Yen Keeps Sliding" graphic for the
08/13/26 daily email (Market Briefs "Insert coin." / the Yen On Edge story).
OUR OWN branded chart, not the source image.

VERIFICATION against Yahoo Finance JPY=X daily closes (chart API, range=1y):
  * peak 163.864 on 2026-07-28  ->  the graphic's "163.9 peak" is CORRECT.
  * endpoint 159.379 on 2026-08-12 -> the graphic's 159.35 is within normal FX
    vendor cutoff variation (it cites Trading Economics), so CORRECT.
  * "up 3.8% over six months" is NOT correct. Six months back from the Aug 12
    endpoint is 2026-02-12 at 152.821, which makes the move +4.29%, not 3.8%.
    This chart prints the computed +4.3% and names the exact window.

DATA HOLE, documented: Yahoo's DAILY series carries a null close for 2026-08-12.
The 24 hourly bars for that date are complete, so the Aug 12 close is taken from
the last hourly bar of that day (159.379). Same vendor, same instrument, one
filled point, noted here so it is never mistaken for an invented value.

The 160 line is drawn because it is the story: Japanese officials have stepped in
around that level before, and the pair is sitting just under it.

Warm cream ground (Meridian paper), no authorship label, footer is the data
source only. Run python3.13.
"""
import sys
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "yen-081326.png"

# (ISO date, USD/JPY close). Source: Yahoo Finance JPY=X daily closes.
# 2026-08-12 filled from that day's final hourly bar (daily close was null).
SERIES = [
    ("2026-02-12", 152.821),
    ("2026-02-15", 152.779),
    ("2026-02-16", 153.609),
    ("2026-02-17", 153.149),
    ("2026-02-18", 154.693),
    ("2026-02-19", 155.160),
    ("2026-02-22", 154.339),
    ("2026-02-23", 154.635),
    ("2026-02-24", 155.880),
    ("2026-02-25", 156.200),
    ("2026-02-26", 155.859),
    ("2026-03-01", 156.633),
    ("2026-03-02", 157.257),
    ("2026-03-03", 157.773),
    ("2026-03-04", 156.983),
    ("2026-03-05", 157.534),
    ("2026-03-08", 158.427),
    ("2026-03-09", 157.848),
    ("2026-03-10", 158.114),
    ("2026-03-11", 159.075),
    ("2026-03-12", 159.206),
    ("2026-03-15", 159.568),
    ("2026-03-16", 159.105),
    ("2026-03-17", 158.889),
    ("2026-03-18", 159.795),
    ("2026-03-19", 157.924),
    ("2026-03-22", 159.234),
    ("2026-03-23", 158.479),
    ("2026-03-24", 158.718),
    ("2026-03-25", 159.384),
    ("2026-03-26", 159.704),
    ("2026-03-29", 160.234),
    ("2026-03-30", 159.841),
    ("2026-03-31", 158.579),
    ("2026-04-01", 158.688),
    ("2026-04-02", 159.491),
    ("2026-04-05", 159.780),
    ("2026-04-06", 159.683),
    ("2026-04-07", 158.716),
    ("2026-04-08", 158.642),
    ("2026-04-09", 159.112),
    ("2026-04-12", 159.680),
    ("2026-04-13", 159.214),
    ("2026-04-14", 158.792),
    ("2026-04-15", 158.809),
    ("2026-04-16", 159.195),
    ("2026-04-19", 159.161),
    ("2026-04-20", 158.844),
    ("2026-04-21", 159.373),
    ("2026-04-22", 159.488),
    ("2026-04-23", 159.747),
    ("2026-04-26", 159.576),
    ("2026-04-27", 159.357),
    ("2026-04-28", 159.552),
    ("2026-04-29", 160.184),
    ("2026-04-30", 156.978),
    ("2026-05-03", 156.846),
    ("2026-05-04", 157.194),
    ("2026-05-05", 157.677),
    ("2026-05-06", 156.508),
    ("2026-05-07", 156.829),
    ("2026-05-10", 156.858),
    ("2026-05-11", 157.231),
    ("2026-05-12", 157.671),
    ("2026-05-13", 157.851),
    ("2026-05-14", 158.382),
    ("2026-05-17", 158.844),
    ("2026-05-18", 158.861),
    ("2026-05-19", 159.035),
    ("2026-05-20", 158.888),
    ("2026-05-21", 159.018),
    ("2026-05-24", 158.946),
    ("2026-05-25", 158.954),
    ("2026-05-26", 159.243),
    ("2026-05-27", 159.568),
    ("2026-05-28", 159.270),
    ("2026-05-31", 159.353),
    ("2026-06-01", 159.636),
    ("2026-06-02", 159.968),
    ("2026-06-03", 159.940),
    ("2026-06-04", 159.990),
    ("2026-06-07", 160.327),
    ("2026-06-08", 160.174),
    ("2026-06-09", 160.384),
    ("2026-06-10", 160.527),
    ("2026-06-11", 160.130),
    ("2026-06-14", 159.955),
    ("2026-06-15", 160.229),
    ("2026-06-16", 160.419),
    ("2026-06-17", 160.600),
    ("2026-06-18", 161.289),
    ("2026-06-21", 161.433),
    ("2026-06-22", 161.570),
    ("2026-06-23", 161.599),
    ("2026-06-24", 161.763),
    ("2026-06-25", 161.805),
    ("2026-06-28", 161.787),
    ("2026-06-29", 161.923),
    ("2026-06-30", 162.628),
    ("2026-07-01", 162.539),
    ("2026-07-02", 161.449),
    ("2026-07-05", 161.452),
    ("2026-07-06", 162.088),
    ("2026-07-07", 162.363),
    ("2026-07-08", 162.539),
    ("2026-07-09", 162.363),
    ("2026-07-12", 161.878),
    ("2026-07-13", 162.429),
    ("2026-07-14", 162.187),
    ("2026-07-15", 162.072),
    ("2026-07-16", 162.376),
    ("2026-07-19", 162.512),
    ("2026-07-20", 162.487),
    ("2026-07-21", 163.186),
    ("2026-07-22", 163.081),
    ("2026-07-23", 163.832),
    ("2026-07-26", 163.611),
    ("2026-07-27", 163.771),
    ("2026-07-28", 163.864),
    ("2026-07-29", 163.300),
    ("2026-07-30", 160.183),
    ("2026-08-02", 157.582),
    ("2026-08-03", 157.529),
    ("2026-08-04", 157.692),
    ("2026-08-05", 157.600),
    ("2026-08-06", 158.409),
    ("2026-08-09", 157.891),
    ("2026-08-10", 159.156),
    ("2026-08-11", 159.265),
    ("2026-08-12", 159.379),]

BLUE   = "#3b6ea5"   # the pair
FILL   = "#c3d6ea"
CORAL  = "#e8734a"   # peak marker
GOLD   = "#B08C1E"   # endpoint
GROUND = "#FAF7F0"   # Meridian paper
INK    = "#2e2e2e"
MUTED  = "#8a8172"
GRID   = "#ddd5c6"

dates = [date.fromisoformat(d) for d, _ in SERIES]
vals  = [v for _, v in SERIES]
x = list(range(len(SERIES)))

start_v, end_v = vals[0], vals[-1]
pct = (end_v / start_v - 1.0) * 100.0
pk_i = max(x, key=lambda i: vals[i])

Y_LO, Y_HI = 150.5, 166.0

fig, ax = plt.subplots(figsize=(12, 6.5))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.fill_between(x, vals, Y_LO, color=FILL, alpha=0.55, zorder=1)
ax.plot(x, vals, color=BLUE, linewidth=2.8, zorder=3, solid_capstyle="round")

# the 160 intervention line: the whole point of the story
ax.axhline(160, color=CORAL, linewidth=1.6, linestyle=(0, (6, 4)), zorder=2)
ax.text(len(x) * 0.012, 160.28, "160 line: where Tokyo has stepped in before",
        fontsize=12.5, fontweight="bold", color=CORAL, va="bottom", zorder=6)

# the coordinated intervention: the cliff between the July peak and the early
# August trough. Japan and the U.S. Treasury ran a rare joint yen-buying
# operation; Tokyo had already intervened alone on April 30 after the pair
# pushed past 160. Marked because it is the most striking feature of the line.
trough_i = min(range(pk_i, len(vals)), key=lambda i: vals[i])
ax.annotate("US and Japan\nintervene jointly",
            xy=(trough_i, vals[trough_i]),
            xytext=(trough_i - 26, vals[trough_i] - 3.2),
            fontsize=12, fontweight="bold", color=INK, ha="center",
            linespacing=1.45,
            arrowprops=dict(arrowstyle="->", color=INK, linewidth=1.4))

# peak
ax.scatter([pk_i], [vals[pk_i]], s=150, color=CORAL, edgecolors=GROUND,
           linewidths=2.4, zorder=6)
ax.annotate("%.1f peak" % vals[pk_i], xy=(pk_i, vals[pk_i]),
            xytext=(pk_i - 12, vals[pk_i] + 1.25),
            fontsize=14, fontweight="bold", color=CORAL, ha="center",
            arrowprops=dict(arrowstyle="-", color=CORAL, linewidth=1.5))

# endpoint: label sits in the right margin so the intervention arrow below
# cannot run through it
ax.scatter([x[-1]], [end_v], s=150, color=GOLD, edgecolors=GROUND,
           linewidths=2.4, zorder=6)
ax.text(x[-1] + 2.0, end_v, "%.2f" % end_v,
        fontsize=15.5, fontweight="bold", color=GOLD,
        ha="left", va="center", zorder=6)

for gy in range(152, 167, 2):
    ax.axhline(gy, color=GRID, linewidth=0.9, linestyle=(0, (5, 5)), zorder=0)

ax.set_title("The Yen Keeps Sliding", fontsize=25, fontweight="bold",
             color=INK, loc="left", pad=38, x=-0.055)
ax.text(-0.055, 1.045,
        "USD/JPY  ·  up %.1f%% over six months  ·  a higher line means a weaker yen" % pct,
        transform=ax.transAxes, fontsize=13.5, color=MUTED, ha="left")

ax.set_xlim(0, len(x) - 1 + 11)
ax.set_ylim(Y_LO, Y_HI)
ax.set_yticks(list(range(152, 167, 2)))
ax.set_yticklabels([str(v) for v in range(152, 167, 2)])

tick_pos, tick_lab = [], []
seen = set()
for i, d in enumerate(dates):
    if d.month not in seen:
        seen.add(d.month)
        tick_pos.append(i)
        tick_lab.append(d.strftime("%b"))
ax.set_xticks(tick_pos)
ax.set_xticklabels(tick_lab)

ax.tick_params(axis="both", labelsize=14, colors=MUTED, length=0)
for lbl in ax.get_xticklabels() + ax.get_yticklabels():
    lbl.set_fontweight("bold")
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.spines["bottom"].set_linewidth(1.4)

fig.text(0.055, 0.028,
         "Source: Yahoo Finance, USD/JPY (JPY=X) daily closes, Feb 12 to Aug 12, 2026",
         fontsize=11.5, color=MUTED, ha="left")

plt.subplots_adjust(left=0.075, right=0.975, top=0.815, bottom=0.135)
fig.savefig(OUT, dpi=170, facecolor=GROUND)
print("wrote", OUT)
print("  start %s %.3f   end %s %.3f   change %+.2f%%"
      % (dates[0], start_v, dates[-1], end_v, pct))
print("  peak  %s %.3f" % (dates[pk_i], vals[pk_i]))
