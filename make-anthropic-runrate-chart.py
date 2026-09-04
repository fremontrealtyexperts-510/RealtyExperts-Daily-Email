#!/usr/bin/env python3
"""
make-anthropic-runrate-chart.py  [out.png]

Recreation of the "Anthropic: $9B to $65B in Seven Months" graphic Harv supplied
for the 09/04/26 daily email.

⚠️ DISCLOSURE: this chart is about Anthropic, the company that makes Claude, which
is the assistant that built this chart. It is verified and written to exactly the
same standard as every other chart in this workspace, with the caveats stated
plainly rather than softened. Harv was told about the conflict when the chart was
delivered so he could decide whether to run it at all.

✅ VERIFICATION 09/04/26. All five supplied values are real company disclosures:

    Dec 2025   $9B    Anthropic ("approximately $9 billion at the end of 2025")
    Feb 2026   $14B   company disclosure
    Apr 2026   $30B   Anthropic ("run-rate revenue has now surpassed $30 billion")
    May 2026   $47B   company disclosure (early May was $44B, mid-May $47B)
    Jul 2026   $65B   reported by CNBC, Aug 17 2026: "Anthropic tells investors
                      annualized revenue run rate climbed to $65 billion in July"

⚠️ TWO PROBLEMS WITH THE SUPPLIED CHART, both about the x axis rather than the
values.

1. **It omits March 2026, which was $19B.** That point exists and is disclosed.
   Leaving it out is not neutral: it removes the one month that shows the pace
   between February and April.

2. **It draws unequal time gaps at equal widths.** Dec to Feb is two months, Feb
   to Apr is two, Apr to May is ONE, May to Jul is two. Drawn evenly, the single
   fastest stretch in the whole series, the $17B added in the one month from
   April to May, looks exactly as wide as the two-month gaps. That flatters a
   curve that does not need flattering, and it hides where the real acceleration
   was. This build puts every point on a true date axis, so the spacing carries
   information.

⚠️ AND THE UNIT IS NOT REVENUE. "Annualized revenue run rate" is the latest
period scaled up to a year. It is not $65B booked, not audited, and not a
forecast of the calendar year. The supplied graphic's footer does say
"Company-disclosed, unaudited", which is to its credit, and this build keeps that
caveat in the subtitle where it cannot be missed.

Note also that Market Briefs described the figure as "Bloomberg projects it's on
pace for over $65B in yearly revenue." That is a mischaracterization twice over:
it is a disclosed run rate, not a Bloomberg projection, and a run rate is not
yearly revenue.

BRAND MARK: silver HB monogram, bottom right, no name text (Harv, 08/26/26).
matplotlib only; build with python3.13 on Mac.
"""
import sys
import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "anthropic-runrate-090426.png"
LOGO = "hb-logo-mark.png"

# (date of disclosure, annualized run rate $B, label, was_in_supplied_graphic)
DATA = [
    (datetime.date(2025, 12, 31),  9, "Dec '25", True),
    (datetime.date(2026,  2, 15), 14, "Feb",     True),
    (datetime.date(2026,  3, 15), 19, "Mar",     False),   # omitted by the supplied chart
    (datetime.date(2026,  4, 15), 30, "Apr",     True),
    (datetime.date(2026,  5, 15), 47, "May",     True),
    (datetime.date(2026,  7, 15), 65, "Jul",     True),
]

CREAM = "#fdf6e8"
INK   = "#1f2933"
CORAL = "#e2574c"
DEEP  = "#b8433a"
SLATE = "#4a5568"
SAND  = "#c9b896"
GRID  = "#d8cdb8"
def add_logo(fig, path=LOGO, height=0.05, x=0.985, y=0.026, alpha=0.20):
    """Silver HB monogram, bottom right corner, deliberately near invisible.

    Harv, 08/26/26: "the logo is not the main thing here, almost transparent as
    possible, just barely visible", then "make the logo a bit small", then "not
    clear or sharp". So: small, faint, but CRISP.

    Sharpness comes from resampling ONCE, with PIL, to the exact pixel size the
    figure will draw at, then blitting 1:1 with interpolation="none". Letting
    matplotlib rescale a 500px hairline master down to ~60px softens the strokes
    to mush. There is no vector master for this monogram, so this is as sharp as
    it gets. Missing file or missing PIL is non-fatal."""
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

xs = [d[0] for d in DATA]
ys = [d[1] for d in DATA]
labels = [d[2] for d in DATA]
supplied = [d[3] for d in DATA]

fig, ax = plt.subplots(figsize=(12.6, 7.0), dpi=170)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

# bars on a TRUE date axis: width in days, so unequal gaps stay unequal
for x, y, in_supplied in zip(xs, ys, supplied):
    ax.bar(x, y, width=22, color=(SAND if in_supplied else CORAL),
           edgecolor=(DEEP if not in_supplied else "none"),
           lw=(1.8 if not in_supplied else 0), zorder=3)
ax.bar(xs[-1], ys[-1], width=22, color=DEEP, zorder=4)

for x, y, lb in zip(xs, ys, labels):
    ax.text(x, y + 1.8, f"\\${y}B", ha="center", va="bottom", fontsize=15.5,
            fontweight="bold", color=INK, zorder=6)

ax.annotate("March, $19B, was left off\nthe version going around",
            xy=(xs[2], 19), xytext=(datetime.date(2025, 12, 20), 40),
            fontsize=12, fontweight="bold", color=DEEP, ha="left", va="center",
            arrowprops=dict(arrowstyle="-|>", color=DEEP, lw=1.5,
                            connectionstyle="arc3,rad=-0.22"), zorder=7)

# the one-month stretch that did the most work
ax.annotate("", xy=(xs[3], 70), xytext=(xs[4], 70),
            arrowprops=dict(arrowstyle="<->", color=SLATE, lw=1.6), zorder=6)
ax.text(datetime.date(2026, 4, 30), 72,
        "one month:\n+\\$17B", ha="center", va="bottom", fontsize=12,
        fontweight="bold", color=SLATE, zorder=6)

ax.set_ylim(0, 88)
ax.set_xlim(datetime.date(2025, 11, 25), datetime.date(2026, 8, 25))
ax.set_yticks([0, 20, 40, 60, 80])
ax.set_yticklabels(["0", "\\$20B", "\\$40B", "\\$60B", "\\$80B"])
ax.set_xticks(xs)
ax.set_xticklabels(labels, fontsize=13, fontweight="bold")

ax.grid(axis="y", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=12.5, colors=SLATE)
for lbl in ax.get_xticklabels():
    lbl.set_color(INK)

fig.text(0.046, 0.958, "Anthropic went from \\$9B to \\$65B in seven months",
         fontsize=25, fontweight="bold", color=INK, va="top")
fig.text(0.046, 0.897,
         "Annualized revenue RUN RATE, not booked revenue. Company disclosed and unaudited.",
         fontsize=14, color=SLATE, va="top")

fig.text(0.008, 0.038,
         "Sources: Anthropic disclosures; July figure reported by CNBC, August 17, 2026. "
         "Bars sit on a true date axis, so the gaps between disclosures are to scale.",
         fontsize=10.5, color=SLATE)
fig.text(0.008, 0.013,
         "A run rate annualizes the latest period. It is not a year of revenue, not a forecast, "
         "and no month between these disclosures was reported.",
         fontsize=10.5, color=SLATE)
add_logo(fig)

fig.subplots_adjust(left=0.078, right=0.988, top=0.800, bottom=0.150)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
for (d, v, lb, insup) in DATA:
    print(f"  {lb:<8} {d}  \\${v:>3}B   {'' if insup else '<- omitted by supplied chart'}")
print(f"  Apr to May: +\\${DATA[4][1]-DATA[3][1]}B in one month (the fastest stretch)")
