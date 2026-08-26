#!/usr/bin/env python3
"""
make-debasement-chart.py  [out.png]

Recreation of the "The Debasement Trade" graphic Harv supplied for the 08/26/26
daily email.

✅ VERIFICATION DONE 08/26/26. Every return recomputed month to date from each
asset's own July 31, 2026 close. The supplied graphic was a design brief only,
and it was wrong on Bitcoin by more than two points:

  asset      Jul 31 close    Aug 25 close    recomputed   graphic said
  Bitcoin      62,888.41       78,879.42       +25.4%        +23%
  Gold          4,049.10        4,638.10       +14.6%        +15%
  S&P 500       7,489.72        7,677.28        +2.5%         +2%

Bitcoin is CoinGecko hourly, last print of each UTC day. Gold is COMEX front
month futures (GC=F). S&P 500 is the index (^GSPC). Each return is computed
INSIDE one series, so no cross vendor level mixing.

Endpoint is the SETTLED August 25 close, and the subtitle now says so instead of
the open ended "so far in August" the graphic used. Today's August 26 session is
deliberately excluded: gold and Bitcoin were still trading when this was built.

Also checked: Market Briefs claimed "Bitcoin hit $81,000/coin at one point
yesterday". It did not. The August 25 intraday high was about $79,540.

BRAND MARK (Harv, 08/26/26): SILVER HB monogram bottom right at very low
opacity, no name text. Gold was rejected as too bright.

matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "debasement-082626.png"
LOGO = "hb-logo-mark.png"

ROWS = [("Bitcoin", 25.4), ("Gold", 14.6), ("S&P 500", 2.5)]
AS_OF = "the August 25 close"

CREAM  = "#fdf6e8"
INK    = "#1f2933"
ORANGE = "#e08a1e"
GOLD   = "#c8951c"
SLATE  = "#4a5568"
STEEL  = "#7a93b5"
GRID   = "#d8cdb8"


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


fig, ax = plt.subplots(figsize=(12.6, 7.0), dpi=170)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

labels = [r[0] for r in ROWS]
values = [r[1] for r in ROWS]
xs = range(len(ROWS))
ax.bar(xs, values, width=0.5, color=[ORANGE, GOLD, STEEL], zorder=3)

for x, v in zip(xs, values):
    ax.text(x, v + 0.7, f"+{v:.1f}%", ha="center", va="bottom", fontsize=27,
            fontweight="bold", color=INK, zorder=5)

ax.set_xticks(list(xs))
ax.set_xticklabels(labels, fontsize=16, fontweight="bold")
ax.set_ylim(0, 29.5)
ax.set_yticks([0, 5, 10, 15, 20, 25])
ax.set_yticklabels(["0", "5%", "10%", "15%", "20%", "25%"])

ax.grid(axis="y", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=12.5, colors=SLATE)
for lbl in ax.get_xticklabels():
    lbl.set_color(INK)

fig.text(0.046, 0.958, "The debasement trade",
         fontsize=26.5, fontweight="bold", color=INK, va="top")
fig.text(0.046, 0.897, f"Month to date return, July 31 close through {AS_OF}",
         fontsize=14, color=SLATE, va="top")

fig.text(0.008, 0.022,
         "Sources: CoinGecko (Bitcoin, UTC daily close); COMEX front month gold, GC=F; "
         "S&P 500 index. Month to date from the July 31, 2026 close.",
         fontsize=11, color=SLATE)
add_logo(fig)

fig.subplots_adjust(left=0.085, right=0.975, top=0.805, bottom=0.115)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
for lb, v in ROWS:
    print(f"  {lb:<10} +{v:.1f}%")
