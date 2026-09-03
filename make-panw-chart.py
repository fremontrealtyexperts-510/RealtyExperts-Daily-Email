#!/usr/bin/env python3
"""
make-panw-chart.py  [out.png]

Recreation of the "Palo Alto Stock Is Up 78% in 2026" graphic Harv supplied for
the 09/03/26 daily email.

✅ VERIFICATION 09/03/26. Every claim on the supplied card checks out against the
Yahoo Finance daily series for PANW. This one is clean:

    Sep 2, 2026 close          $328.48   card says $328.48        ok
    Dec 31, 2025 close         $184.20   (the YTD base)
    year to date               +78.3%    card says "up 78%"       ok
    Aug 31 close               $382.13
    two sessions after earnings  -14.0%  card says "fell 14%"     ok
                                         (382.13 -> 362.09 -> 328.48)

The two day drop reconciles with the newsletter's own prior day note that PANW
fell 5.24% on September 1: 382.13 to 362.09 is exactly -5.24%.

⚠️ WHY IT IS REDRAWN ANYWAY: the headline fights the news. "Up 78% in 2026" is
true and it is measured from December 31, but the reason the stock is in the
newsletter today is that it just gave up 14% in two sessions and now sits BELOW
its June close. A reader scanning the card takes away a winner; the chart's own
last move says something else happened this week. Both facts are true, so this
build shows both and lets neither hide the other.

⚠️ ENDPOINT DISCIPLINE (the 08/20 lesson): this chart was built at about 11 AM
Pacific on September 3 with the market OPEN and PANW trading near $328.73. That
is a live tick, not a close, so it is NOT plotted. The series ends at the last
settled close, September 2, which is also what the supplied card used.

Points are month end closes from Dec 2025 through Aug 2026, plus the Sep 2 close.

BRAND MARK: silver HB monogram, bottom right, no name text (Harv, 08/26/26).
matplotlib only; build with python3.13 on Mac.
"""
import sys
import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "panw-090326.png"
LOGO = "hb-logo-mark.png"

# month-end closes, then the last settled close (Sep 2)
SERIES = [
    ("2025-12-31", 184.20), ("2026-01-30", 176.97), ("2026-02-27", 148.92),
    ("2026-03-31", 160.32), ("2026-04-30", 179.32), ("2026-05-29", 281.69),
    ("2026-06-30", 341.02), ("2026-07-31", 331.83), ("2026-08-31", 382.13),
    ("2026-09-02", 328.48),
]
BASE = 184.20      # Dec 31, 2025 close
PRE_EARNINGS = 382.13
LAST = 328.48

CREAM = "#fdf6e8"
INK   = "#1f2933"
CORAL = "#e2574c"
DEEP  = "#b8433a"
GREEN = "#2f8f5b"
SLATE = "#4a5568"
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

ytd = (LAST / BASE - 1) * 100
drop = (LAST / PRE_EARNINGS - 1) * 100
assert abs(ytd - 78.3) < 0.3, f"YTD moved: {ytd:.1f}%"
assert abs(drop + 14.04) < 0.2, f"two day drop moved: {drop:.2f}%"

xs = [datetime.date.fromisoformat(d) for d, _ in SERIES]
ys = [v for _, v in SERIES]

fig, ax = plt.subplots(figsize=(12.6, 7.0), dpi=170)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

# the run up, then the post-earnings leg in coral
ax.plot(xs[:-1], ys[:-1], color=GREEN, lw=2.8, zorder=4, solid_capstyle="round")
ax.plot(xs[-2:], ys[-2:], color=DEEP, lw=3.2, zorder=5, solid_capstyle="round")
# Full-width wash under the whole series. The earlier version filled only where
# price sat above the Dec base, which left a hard-edged block starting in May
# that read as a shaded region with meaning it did not have.
ax.fill_between(xs, ys, 120, color=GREEN, alpha=0.09, zorder=2)

ax.axhline(BASE, color=SLATE, lw=1.5, ls=(0, (6, 4)), zorder=3)
ax.text(datetime.date(2025, 12, 18), BASE - 13,
        f"Dec 31, 2025 close: \\${BASE:,.2f}", ha="left", va="top",
        fontsize=12, fontweight="bold", color=SLATE, zorder=6)

ax.plot([xs[-2]], [ys[-2]], "o", ms=8, color=SLATE, zorder=6)
ax.plot([xs[-1]], [ys[-1]], "o", ms=11, color=DEEP, zorder=7)

# Label sits to the RIGHT of the final point, in empty plot space. The first
# version ran a long curved arrow back across the June to August line, which
# read as a second data series. No arrow now, and nothing crosses the line.
ax.text(datetime.date(2026, 9, 11), LAST + 6, f"\\${LAST:,.2f}",
        fontsize=17, fontweight="bold", color=DEEP, ha="left", va="bottom", zorder=8)
ax.text(datetime.date(2026, 9, 11), LAST - 8,
        f"Q4 earnings\n{drop:.0f}% in two sessions",
        fontsize=12.5, fontweight="bold", color=DEEP, ha="left", va="top", zorder=8)

ax.text(datetime.date(2026, 1, 8), 392, f"+{ytd:.0f}% year to date",
        fontsize=29, fontweight="bold", color=GREEN, ha="left", va="center", zorder=7)
ax.text(datetime.date(2026, 1, 8), 366,
        "and still 14% below where it closed on August 31",
        fontsize=13, color=SLATE, ha="left", va="center", zorder=7)

ax.set_ylim(120, 428)
ax.set_xlim(datetime.date(2025, 12, 10), datetime.date(2026, 12, 20))
ax.set_yticks([150, 200, 250, 300, 350, 400])
ax.set_yticklabels([f"\\${v}" for v in (150, 200, 250, 300, 350, 400)])
ax.set_xticks([datetime.date(2025, 12, 31)] +
              [datetime.date(2026, m, 28) for m in (2, 4, 6, 8)])
ax.set_xticklabels(["Dec", "Feb", "Apr", "Jun", "Aug"])

ax.grid(axis="y", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=12.5, colors=SLATE)

fig.text(0.046, 0.958, "Palo Alto's big year, and its bad week",
         fontsize=26.5, fontweight="bold", color=INK, va="top")
fig.text(0.046, 0.897,
         "PANW month end closing price, December 2025 through the September 2, 2026 close",
         fontsize=14, color=SLATE, va="top")

fig.text(0.008, 0.038,
         "Source: PANW daily closes via Yahoo Finance. Year to date is measured from the "
         "December 31, 2025 close of \\$184.20.",
         fontsize=10.5, color=SLATE)
fig.text(0.008, 0.013,
         "Series ends at the last settled close. Shares were trading near \\$328.73 midday on "
         "September 3, which is a live tick and is not plotted.",
         fontsize=10.5, color=SLATE)
add_logo(fig)

fig.subplots_adjust(left=0.082, right=0.988, top=0.800, bottom=0.155)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
print(f"  base {BASE}  last {LAST}  YTD +{ytd:.1f}%  two-day {drop:.2f}%")
