#!/usr/bin/env python3
"""
make-silver-chart.py  [out.png]

Built for the 08/28/26 daily email. Silver over one year, the metal story the
newsletter left out entirely.

WHY: Market Briefs printed no silver at all on 08/28 (it rarely does, which is
why gold and silver are a standing mandatory pair in this report). Silver at
Friday's spot print was $70.62 an ounce, up 3.33% on the day, up 20.94% on the
month and up 80.89% on the year, per Fortune. That is the largest single move in
the Economy section and it deserved a picture.

⚠️ TWO SERIES, DELIBERATELY NOT MIXED. Our Economy card quotes Fortune SPOT at
6:30 a.m. ET, which is the series our own history is built on and which
reconciles exactly against yesterday's published $68.34. This CHART plots COMEX
front-month FUTURES (Yahoo SI=F) daily closes, because spot has no free, dated,
reproducible daily history and futures do. Futures and spot are close but not
identical, so the chart's endpoint will not equal the card to the penny. The
caption says which is which. Same discipline as Brent, where quoting one
instrument's level against another instrument's change produced four different
"Brent" prices in one morning on 08/05.

⚠️ ENDPOINT AND THE REVERSAL, THE REASON THIS CHART IS DRAWN THE WAY IT IS.
Fortune's $70.62 was stamped 6:30 a.m. ET. Silver then sold off hard through the
US session: SI=F settled at $69.43 on 08/27 and was trading at $66.86 at 2:53
p.m. ET on 08/28, roughly 3.7% below the prior settle. Gold did the same thing,
$4,609.70 down to $4,495.90, about 2.5%. So the morning print is real but is NOT
where the metal sits as this publishes.

Rather than pretend the last bar is a close, the chart follows the house pattern
set on 08/20: the SETTLED series runs solid through the 08/27 close, then a
DASHED leg reaches an OPEN marker for the in-progress 08/28 session, labeled as
not settled. Never draw a live tick as if it were a settlement (the error caught
in a supplied graphic on 08/07).

The one-year gain is measured to the last SETTLED close: $39.19 on 08/28/25 to
$69.43 on 08/27/26, +77.2%.

⚠️ FRAMING, CAUGHT BY EYEBALLING THE FIRST RENDER. "Silver is up 77% in a year"
was the first headline on this chart and it fought the picture: the line clearly
runs up to $115.08 on 01/26/26 and then falls away. Point-to-point over a year
is +77.2%, but from that January peak silver is DOWN 39.7%. A headline that
quotes only the flattering leg of a round trip is accurate and still misleading,
which is the failure mode logged on 08/27 (every value right, the series still
wrong). The chart now says BOTH, and marks the peak.

BRAND MARK: silver HB monogram, bottom right, no name text (Harv, 08/26/26).
matplotlib only; build with python3.13 on Mac.
"""
import sys
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

OUT = sys.argv[1] if len(sys.argv) > 1 else "silver-082826.png"
LOGO = "hb-logo-mark.png"

# COMEX front-month silver futures (SI=F), daily close, pulled from Yahoo's
# chart API on 08/28/26. The final row is the LIVE, UNSETTLED 08/28 session.
SERIES = [
    ("2025-08-28",39.19), ("2025-08-29",40.2), ("2025-09-02",41.071), ("2025-09-03",41.542), ("2025-09-04",40.911),
    ("2025-09-05",41.074), ("2025-09-08",41.426), ("2025-09-09",40.878), ("2025-09-10",41.133), ("2025-09-11",41.697),
    ("2025-09-12",42.387), ("2025-09-15",42.517), ("2025-09-16",42.471), ("2025-09-17",41.722), ("2025-09-18",41.707),
    ("2025-09-19",42.536), ("2025-09-22",43.799), ("2025-09-23",44.192), ("2025-09-24",43.777), ("2025-09-25",44.697),
    ("2025-09-26",46.221), ("2025-09-29",46.612), ("2025-09-30",46.253), ("2025-10-01",47.29), ("2025-10-02",46),
    ("2025-10-03",47.597), ("2025-10-06",48.082), ("2025-10-07",47.179), ("2025-10-08",48.656), ("2025-10-09",46.85),
    ("2025-10-10",46.938), ("2025-10-13",50.13), ("2025-10-14",50.314), ("2025-10-15",51.073), ("2025-10-16",53.023),
    ("2025-10-17",49.864), ("2025-10-20",51.119), ("2025-10-21",47.45), ("2025-10-22",47.461), ("2025-10-23",48.482),
    ("2025-10-24",48.377), ("2025-10-27",46.562), ("2025-10-28",47.125), ("2025-10-29",47.721), ("2025-10-30",48.428),
    ("2025-10-31",47.994), ("2025-11-03",47.888), ("2025-11-04",47.13), ("2025-11-05",47.863), ("2025-11-06",47.794),
    ("2025-11-07",48.017), ("2025-11-10",50.177), ("2025-11-11",50.618), ("2025-11-12",53.332), ("2025-11-13",53.074),
    ("2025-11-14",50.59), ("2025-11-17",50.625), ("2025-11-18",50.45), ("2025-11-19",50.79), ("2025-11-20",50.247),
    ("2025-11-21",49.873), ("2025-11-24",50.295), ("2025-11-25",50.934), ("2025-11-26",52.916), ("2025-11-28",56.446),
    ("2025-12-01",58.418), ("2025-12-02",57.983), ("2025-12-03",57.921), ("2025-12-04",56.847), ("2025-12-05",58.422),
    ("2025-12-08",57.779), ("2025-12-09",60.169), ("2025-12-10",60.379), ("2025-12-11",63.929), ("2025-12-12",61.362),
    ("2025-12-15",62.94), ("2025-12-16",62.7), ("2025-12-17",66.237), ("2025-12-18",64.592), ("2025-12-19",66.845),
    ("2025-12-22",67.906), ("2025-12-23",70.485), ("2025-12-24",71.031), ("2025-12-26",76.486), ("2025-12-29",69.856),
    ("2025-12-30",77.374), ("2025-12-31",70.134), ("2026-01-02",70.556), ("2026-01-05",76.164), ("2026-01-06",80.53),
    ("2026-01-07",77.135), ("2026-01-08",74.716), ("2026-01-09",78.884), ("2026-01-12",84.61), ("2026-01-13",85.877),
    ("2026-01-14",90.869), ("2026-01-15",91.876), ("2026-01-16",88.091), ("2026-01-20",94.206), ("2026-01-21",92.21),
    ("2026-01-22",95.976), ("2026-01-23",100.925), ("2026-01-26",115.08), ("2026-01-27",105.523), ("2026-01-28",113.111),
    ("2026-01-29",114.037), ("2026-01-30",78.29), ("2026-02-02",76.778), ("2026-02-03",83.042), ("2026-02-04",84.165),
    ("2026-02-05",76.529), ("2026-02-06",76.735), ("2026-02-09",82.065), ("2026-02-10",80.218), ("2026-02-11",83.754),
    ("2026-02-12",75.546), ("2026-02-13",77.851), ("2026-02-17",73.447), ("2026-02-18",77.509), ("2026-02-19",77.565),
    ("2026-02-20",82.283), ("2026-02-23",86.523), ("2026-02-24",87.457), ("2026-02-25",90.939), ("2026-02-26",86.998),
    ("2026-02-27",92.682), ("2026-03-02",88.284), ("2026-03-03",82.923), ("2026-03-04",82.633), ("2026-03-05",81.687),
    ("2026-03-06",83.816), ("2026-03-09",84.032), ("2026-03-10",89.083), ("2026-03-11",85.065), ("2026-03-12",84.67),
    ("2026-03-13",80.914), ("2026-03-16",80.263), ("2026-03-17",79.53), ("2026-03-18",77.238), ("2026-03-19",70.902),
    ("2026-03-20",69.36), ("2026-03-23",69.049), ("2026-03-24",69.274), ("2026-03-25",72.361), ("2026-03-26",67.671),
    ("2026-03-27",69.545), ("2026-03-30",70.324), ("2026-03-31",74.69), ("2026-04-01",75.867), ("2026-04-02",72.735),
    ("2026-04-06",72.661), ("2026-04-07",71.826), ("2026-04-08",75.224), ("2026-04-09",76.277), ("2026-04-10",76.324),
    ("2026-04-13",75.523), ("2026-04-14",79.391), ("2026-04-15",79.491), ("2026-04-16",78.606), ("2026-04-17",81.738),
    ("2026-04-20",79.951), ("2026-04-21",76.411), ("2026-04-22",77.893), ("2026-04-23",75.465), ("2026-04-24",76.383),
    ("2026-04-27",75.003), ("2026-04-28",73.205), ("2026-04-29",71.569), ("2026-04-30",73.534), ("2026-05-01",75.951),
    ("2026-05-04",73.072), ("2026-05-05",73.108), ("2026-05-06",76.811), ("2026-05-07",79.701), ("2026-05-08",80.395),
    ("2026-05-11",85.485), ("2026-05-12",85.13), ("2026-05-13",88.888), ("2026-05-14",84.912), ("2026-05-15",77.161),
    ("2026-05-18",77.073), ("2026-05-19",74.828), ("2026-05-20",75.851), ("2026-05-21",76.414), ("2026-05-22",75.893),
    ("2026-05-26",76.305), ("2026-05-27",74.599), ("2026-05-28",75.645), ("2026-05-29",75.616), ("2026-06-01",75.007),
    ("2026-06-02",75.311), ("2026-06-03",73.476), ("2026-06-04",73.779), ("2026-06-05",68.943), ("2026-06-08",68.425),
    ("2026-06-09",65.094), ("2026-06-10",64.599), ("2026-06-11",63.885), ("2026-06-12",67.859), ("2026-06-15",70.066),
    ("2026-06-16",69.899), ("2026-06-17",70.696), ("2026-06-18",66.255), ("2026-06-22",65.527), ("2026-06-23",62.02),
    ("2026-06-24",58.052), ("2026-06-25",58.348), ("2026-06-26",59.217), ("2026-06-29",58.175), ("2026-06-30",59.477),
    ("2026-07-01",60.085), ("2026-07-02",60.643), ("2026-07-06",61.92), ("2026-07-07",60.931), ("2026-07-08",58.164),
    ("2026-07-09",60.378), ("2026-07-10",59.809), ("2026-07-13",57.634), ("2026-07-14",58.772), ("2026-07-15",57.11),
    ("2026-07-16",55.898), ("2026-07-17",56.038), ("2026-07-20",56.802), ("2026-07-21",58.835), ("2026-07-22",60.019),
    ("2026-07-23",57.798), ("2026-07-24",58.656), ("2026-07-27",58.472), ("2026-07-28",57.296), ("2026-07-29",57.863),
    ("2026-07-30",58.815), ("2026-07-31",57.591), ("2026-08-03",57.667), ("2026-08-04",60.056), ("2026-08-05",62.099),
    ("2026-08-06",61.439), ("2026-08-07",63.332), ("2026-08-10",65.106), ("2026-08-11",64.769), ("2026-08-12",65.555),
    ("2026-08-13",64.873), ("2026-08-14",64.988), ("2026-08-17",66.121), ("2026-08-18",63.941), ("2026-08-19",65.734),
    ("2026-08-20",68.026), ("2026-08-21",69.466), ("2026-08-24",68.541), ("2026-08-25",68.636), ("2026-08-26",67.99),
    ("2026-08-27",69.429), ("2026-08-28",66.855),]

CREAM = "#fdf6e8"
INK   = "#1f2933"
CORAL = "#e2574c"
DEEP  = "#b8433a"
SLATE = "#4a5568"
GRID  = "#d8cdb8"

TODAY = "2026-08-28"          # in progress at build time, not a settlement
settled = [(d, v) for d, v in SERIES if d < TODAY]
live    = [(d, v) for d, v in SERIES if d == TODAY]
assert live, "expected an in-progress bar for %s" % TODAY
assert settled[-1][0] == "2026-08-27", "last settled close should be 08/27"

start_d, start_v = settled[0]
end_d,   end_v   = settled[-1]
live_d,  live_v  = live[0]
gain = (end_v / start_v - 1) * 100


def add_logo(fig, path=LOGO, height=0.05, x=0.985, y=0.026, alpha=0.20):
    """Silver HB monogram, bottom right corner, deliberately near invisible.

    Copied verbatim from make-rentbuy-chart.py, which Harv approved 08/26/26."""
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


def dt(s):
    y, m, d = (int(x) for x in s.split("-"))
    return date(y, m, d)


fig, ax = plt.subplots(figsize=(12.6, 7.0), dpi=170)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

xs = [dt(d) for d, _ in settled]
ys = [v for _, v in settled]
ax.plot(xs, ys, color=CORAL, lw=2.4, zorder=4, solid_capstyle="round")
ax.fill_between(xs, ys, min(ys) - 4, color=CORAL, alpha=0.10, zorder=2)

# The in-progress session: dashed reach to an open marker, never drawn as a close.
ax.plot([dt(end_d), dt(live_d)], [end_v, live_v], color=SLATE, lw=1.9,
        ls=(0, (4, 3)), zorder=5)
ax.plot([dt(live_d)], [live_v], marker="o", ms=10, mfc=CREAM, mec=SLATE,
        mew=2.1, zorder=6)

ax.annotate(f"\\${live_v:,.2f}\nAug 28, not settled",
            xy=(dt(live_d), live_v), xytext=(-14, -68), textcoords="offset points",
            ha="right", va="bottom", fontsize=12.5, color=SLATE, linespacing=1.45)

ax.plot([dt(end_d)], [end_v], marker="o", ms=8, color=DEEP, zorder=7)
ax.annotate(f"\\${end_v:,.2f}  Aug 27 close",
            xy=(dt(end_d), end_v), xytext=(-16, 20), textcoords="offset points",
            ha="right", fontsize=13.5, fontweight="bold", color=DEEP)

# The January peak, without which the headline's second clause is unreadable.
peak_d, peak_v = max(settled, key=lambda r: r[1])
drawdown = (end_v / peak_v - 1) * 100
ax.plot([dt(peak_d)], [peak_v], marker="o", ms=8, color=INK, zorder=7)
ax.annotate(f"\\${peak_v:,.2f}  Jan 26 peak",
            xy=(dt(peak_d), peak_v), xytext=(16, 4), textcoords="offset points",
            ha="left", fontsize=13.5, fontweight="bold", color=INK)

ax.annotate(f"\\${start_v:,.2f}",
            xy=(dt(start_d), start_v), xytext=(10, -6), textcoords="offset points",
            ha="left", fontsize=13.5, fontweight="bold", color=INK)

ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.set_ylim(min(ys) - 4, max(max(ys), live_v) + 9)
ax.grid(axis="y", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=12.5, colors=SLATE)
ax.set_ylabel("Dollars per ounce", fontsize=12.5, color=SLATE, labelpad=10)

fig.text(0.046, 0.958,
         f"Silver: up {gain:.0f}% in a year, down {abs(drawdown):.0f}% from January",
         fontsize=26.5, fontweight="bold", color=INK, va="top")
fig.text(0.046, 0.897,
         "COMEX front-month silver futures, daily close, August 2025 to August 2026. "
         "Both numbers are true, which is the point.",
         fontsize=14, color=SLATE, va="top")

fig.text(0.008, 0.038,
         "Source: ICE/COMEX front-month silver futures (SI=F) daily closes via Yahoo Finance.",
         fontsize=11, color=SLATE)
fig.text(0.008, 0.012,
         "The Economy section quotes Fortune SPOT silver, a different series, so its level differs slightly from this line.",
         fontsize=11, color=SLATE)
add_logo(fig)

fig.subplots_adjust(left=0.085, right=0.978, top=0.805, bottom=0.115)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
print(f"  settled points : {len(settled)}  {start_d} -> {end_d}")
print(f"  start          : ${start_v:,.2f}")
print(f"  last settled   : ${end_v:,.2f}  ({gain:+.1f}% over the year)")
print(f"  live unsettled : ${live_v:,.2f}  ({(live_v/end_v-1)*100:+.2f}% vs the 08/27 close)")
print(f"  peak           : ${peak_v:,.2f} on {peak_d}  ({drawdown:+.1f}% from peak to the 08/27 close)")
