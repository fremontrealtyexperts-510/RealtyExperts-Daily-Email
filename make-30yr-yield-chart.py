#!/usr/bin/env python3
"""
make-30yr-yield-chart.py  [out.png]

Recreation of "The 30-Year Yield Just Hit A 19-Year High," supplied for the
09/01/26 daily email.

✅ VERIFICATION PASSED, INCLUDING THE HEADLINE CLAIM. Checked against Treasury's
own Daily Par Yield Curve Rates and the full FRED DGS30 daily history:

  claim on graphic              verified
  Aug 31, 2026 close  5.25%     5.25%  (Treasury daily curve, 08/31/2026)
  August peak         5.31%     5.31%  on 08/17/2026
  "19-year high"                the last daily reading ABOVE 5.31% was
                                06/12/2007 at 5.35%, which is 19 years

  month-end 2026, Treasury: Jan 4.87, Feb 4.64, Mar 4.88, Apr 4.98, May 4.99,
  Jun 4.91, Jul 5.27, Aug 5.25. The supplied graphic's plotted path matches.

Two graphics in one morning that needed no correction, after four sessions where
every single one did.

⚠️ WHY THIS IS DRAWN DIFFERENTLY ANYWAY. The supplied version plots only the
eight months of 2026, so it ASSERTS the nineteen year claim without showing it.
A reader cannot see 2007 on a chart that starts in January. This version plots
the whole span the claim covers, which turns the headline into something the eye
can check: the line clears everything since the summer of 2007.

BASIS: the highest daily reading in each month, since 2005. That is deliberately
the same statistic the claim is about, a peak rather than a month-end. Using
month-end values would put August at 5.25% and would never show the 5.31% the
headline rests on, and mixing a month-end line with a daily peak annotation is
exactly the sort of two-instruments-one-label error that produced four different
"Brent" prices on 08/05. One basis, stated on the chart.

⚠️ FRED lags a day or two, so its DGS30 stopped at 08/28 (5.22) when this was
built. Treasury's own curve has 08/31 at 5.25, which is BELOW the 08/17 peak of
5.31, so August's maximum is unaffected. The build asserts this rather than
assuming it.

BRAND MARK: silver HB monogram, bottom right, no name text (Harv, 08/26/26).
matplotlib only; build with python3.13 on Mac.
"""
import sys
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

OUT = sys.argv[1] if len(sys.argv) > 1 else "yield30-090126.png"
LOGO = "hb-logo-mark.png"

AUG31_CLOSE = 5.25          # Treasury daily curve, 08/31/2026
# month, highest daily 30-year yield in that month (FRED DGS30)
SERIES = [
    ("2005-01",4.91), ("2005-02",4.71), ("2005-03",4.88), ("2005-04",4.78), ("2005-05",4.64), ("2005-06",4.44),
    ("2005-07",4.48), ("2005-08",4.58), ("2005-09",4.56), ("2005-10",4.77), ("2005-11",4.84), ("2005-12",4.72),
    ("2006-01",4.7), ("2006-02",4.69), ("2006-03",4.9), ("2006-04",5.18), ("2006-05",5.29), ("2006-06",5.28),
    ("2006-07",5.27), ("2006-08",5.12), ("2006-09",4.95), ("2006-10",4.95), ("2006-11",4.81), ("2006-12",4.81),
    ("2007-01",4.99), ("2007-02",4.93), ("2007-03",4.84), ("2007-04",4.93), ("2007-05",5.01), ("2007-06",5.35),
    ("2007-07",5.28), ("2007-08",5.03), ("2007-09",4.96), ("2007-10",4.91), ("2007-11",4.67), ("2007-12",4.68),
    ("2008-01",4.44), ("2008-02",4.67), ("2008-03",4.6), ("2008-04",4.61), ("2008-05",4.76), ("2008-06",4.79),
    ("2008-07",4.69), ("2008-08",4.68), ("2008-09",4.43), ("2008-10",4.35), ("2008-11",4.34), ("2008-12",3.22),
    ("2009-01",3.58), ("2009-02",3.71), ("2009-03",3.83), ("2009-04",4.05), ("2009-05",4.59), ("2009-06",4.76),
    ("2009-07",4.62), ("2009-08",4.61), ("2009-09",4.33), ("2009-10",4.37), ("2009-11",4.41), ("2009-12",4.69),
    ("2010-01",4.74), ("2010-02",4.74), ("2010-03",4.77), ("2010-04",4.85), ("2010-05",4.53), ("2010-06",4.29),
    ("2010-07",4.1), ("2010-08",4.07), ("2010-09",3.92), ("2010-10",4.06), ("2010-11",4.38), ("2010-12",4.59),
    ("2011-01",4.6), ("2011-02",4.76), ("2011-03",4.66), ("2011-04",4.64), ("2011-05",4.38), ("2011-06",4.39),
    ("2011-07",4.4), ("2011-08",4.07), ("2011-09",3.51), ("2011-10",3.45), ("2011-11",3.13), ("2011-12",3.12),
    ("2012-01",3.15), ("2012-02",3.2), ("2012-03",3.48), ("2012-04",3.41), ("2012-05",3.16), ("2012-06",2.77),
    ("2012-07",2.74), ("2012-08",2.96), ("2012-09",3.09), ("2012-10",3.02), ("2012-11",2.92), ("2012-12",3),
    ("2013-01",3.19), ("2013-02",3.23), ("2013-03",3.26), ("2013-04",3.1), ("2013-05",3.31), ("2013-06",3.6),
    ("2013-07",3.68), ("2013-08",3.9), ("2013-09",3.88), ("2013-10",3.78), ("2013-11",3.9), ("2013-12",3.96),
    ("2014-01",3.93), ("2014-02",3.73), ("2014-03",3.73), ("2014-04",3.65), ("2014-05",3.49), ("2014-06",3.47),
    ("2014-07",3.47), ("2014-08",3.3), ("2014-09",3.37), ("2014-10",3.15), ("2014-11",3.09), ("2014-12",3),
    ("2015-01",2.69), ("2015-02",2.73), ("2015-03",2.83), ("2015-04",2.76), ("2015-05",3.07), ("2015-06",3.25),
    ("2015-07",3.21), ("2015-08",2.95), ("2015-09",3.08), ("2015-10",2.96), ("2015-11",3.12), ("2015-12",3.07),
    ("2016-01",3.01), ("2016-02",2.77), ("2016-03",2.75), ("2016-04",2.76), ("2016-05",2.71), ("2016-06",2.63),
    ("2016-07",2.3), ("2016-08",2.32), ("2016-09",2.48), ("2016-10",2.62), ("2016-11",3.02), ("2016-12",3.19),
    ("2017-01",3.1), ("2017-02",3.11), ("2017-03",3.2), ("2017-04",3), ("2017-05",3.04), ("2017-06",2.87),
    ("2017-07",2.93), ("2017-08",2.86), ("2017-09",2.87), ("2017-10",2.96), ("2017-11",2.88), ("2017-12",2.88),
    ("2018-01",2.98), ("2018-02",3.22), ("2018-03",3.16), ("2018-04",3.21), ("2018-05",3.25), ("2018-06",3.13),
    ("2018-07",3.11), ("2018-08",3.13), ("2018-09",3.23), ("2018-10",3.4), ("2018-11",3.46), ("2018-12",3.27),
    ("2019-01",3.09), ("2019-02",3.09), ("2019-03",3.13), ("2019-04",2.99), ("2019-05",2.94), ("2019-06",2.63),
    ("2019-07",2.65), ("2019-08",2.44), ("2019-09",2.37), ("2019-10",2.34), ("2019-11",2.43), ("2019-12",2.39),
    ("2020-01",2.38), ("2020-02",2.14), ("2020-03",1.78), ("2020-04",1.41), ("2020-05",1.47), ("2020-06",1.68),
    ("2020-07",1.45), ("2020-08",1.52), ("2020-09",1.46), ("2020-10",1.67), ("2020-11",1.75), ("2020-12",1.73),
    ("2021-01",1.88), ("2021-02",2.33), ("2021-03",2.45), ("2021-04",2.36), ("2021-05",2.4), ("2021-06",2.3),
    ("2021-07",2.07), ("2021-08",2.03), ("2021-09",2.09), ("2021-10",2.16), ("2021-11",2.02), ("2021-12",1.96),
    ("2022-01",2.18), ("2022-02",2.37), ("2022-03",2.6), ("2022-04",3.01), ("2022-05",3.23), ("2022-06",3.45),
    ("2022-07",3.27), ("2022-08",3.32), ("2022-09",3.87), ("2022-10",4.4), ("2022-11",4.34), ("2022-12",3.98),
    ("2023-01",3.88), ("2023-02",3.98), ("2023-03",4.03), ("2023-04",3.81), ("2023-05",4.01), ("2023-06",3.95),
    ("2023-07",4.06), ("2023-08",4.45), ("2023-09",4.73), ("2023-10",5.11), ("2023-11",4.96), ("2023-12",4.43),
    ("2024-01",4.41), ("2024-02",4.49), ("2024-03",4.46), ("2024-04",4.82), ("2024-05",4.74), ("2024-06",4.59),
    ("2024-07",4.64), ("2024-08",4.28), ("2024-09",4.14), ("2024-10",4.53), ("2024-11",4.63), ("2024-12",4.82),
    ("2025-01",4.98), ("2025-02",4.83), ("2025-03",4.73), ("2025-04",4.91), ("2025-05",5.08), ("2025-06",4.99),
    ("2025-07",5.01), ("2025-08",4.94), ("2025-09",4.97), ("2025-10",4.76), ("2025-11",4.75), ("2025-12",4.85),
    ("2026-01",4.91), ("2026-02",4.91), ("2026-03",4.98), ("2026-04",4.98), ("2026-05",5.18), ("2026-06",5.03),
    ("2026-07",5.27), ("2026-08",5.31),]

CREAM = "#fdf6e8"; INK = "#1f2933"; CORAL = "#e2574c"; DEEP = "#b8433a"
SLATE = "#4a5568"; GRID = "#d8cdb8"; MUTED = "#9aa5b1"

cur_m, cur_v = SERIES[-1]
assert cur_m == "2026-08" and cur_v == 5.31, "August peak drifted"
prior = [(m, v) for m, v in SERIES[:-1] if v > cur_v]
assert prior, "nothing higher in the window, the headline would be wrong"
PRIOR_M, PRIOR_V = prior[-1]
YEARS = int(cur_m[:4]) - int(PRIOR_M[:4])
assert YEARS == 19, f"the headline says 19 years, the data says {YEARS}"


def add_logo(fig, path=LOGO, height=0.05, x=0.985, y=0.026, alpha=0.20):
    """Silver HB monogram, bottom right. Verbatim from make-rentbuy-chart.py."""
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


def dt(m):
    y, mo = (int(x) for x in m.split("-")); return date(y, mo, 1)


fig, ax = plt.subplots(figsize=(12.6, 7.0), dpi=170)
fig.patch.set_facecolor(CREAM); ax.set_facecolor(CREAM)

xs = [dt(m) for m, _ in SERIES]
ys = [v for _, v in SERIES]
ax.plot(xs, ys, color=CORAL, lw=2.2, zorder=4)
ax.fill_between(xs, ys, 0.9, color=CORAL, alpha=0.09, zorder=2)

# The horizontal line IS the argument: everything between 2007 and now sits under it.
ax.axhline(cur_v, color=DEEP, lw=1.5, ls=(0, (5, 4)), zorder=5)

ax.plot([dt(cur_m)], [cur_v], marker="o", ms=9, color=DEEP, zorder=7)
ax.annotate(f"{cur_v:.2f}%\nAug 2026", xy=(dt(cur_m), cur_v), xytext=(-14, 16),
            textcoords="offset points", ha="right", va="bottom", fontsize=13.5,
            fontweight="bold", color=DEEP, linespacing=1.35)

ax.plot([dt(PRIOR_M)], [PRIOR_V], marker="o", ms=8, color=INK, zorder=7)
ax.annotate(f"{PRIOR_V:.2f}%  June 2007", xy=(dt(PRIOR_M), PRIOR_V),
            xytext=(16, 14), textcoords="offset points", ha="left",
            fontsize=13, fontweight="bold", color=INK)

ax.annotate(f"nothing in {YEARS} years came back above this line",
            xy=(date(2015, 1, 1), cur_v), xytext=(0, -30),
            textcoords="offset points", ha="center", va="top",
            fontsize=12.5, color=SLATE)

ax.xaxis.set_major_locator(mdates.YearLocator(3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.yaxis.set_major_formatter(lambda v, p: f"{v:.1f}%")
# The 2020 trough runs to 1.19%. An axis starting at 1.9 clipped it off the
# bottom, which is cutting data to make a chart look tidy; caught by eyeballing.
ax.set_ylim(0.9, 5.9)
ax.grid(axis="y", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=12.5, colors=SLATE)
ax.set_ylabel("Highest daily yield in the month", fontsize=12.5, color=SLATE, labelpad=10)

fig.text(0.046, 0.958, "The 30-year yield is back where it was in 2007",
         fontsize=26.5, fontweight="bold", color=INK, va="top")
fig.text(0.046, 0.897,
         f"U.S. 30-year Treasury. August peaked at {cur_v:.2f}%, a level last "
         f"exceeded in June 2007.",
         fontsize=14, color=SLATE, va="top")
fig.text(0.008, 0.038,
         "Source: U.S. Treasury Daily Par Yield Curve Rates via FRED (DGS30). Each point is the "
         "highest daily reading in that month.",
         fontsize=11, color=SLATE)
fig.text(0.008, 0.012,
         f"The August 31 close was {AUG31_CLOSE:.2f}%, just under the month's {cur_v:.2f}% peak.",
         fontsize=11, color=SLATE)
add_logo(fig)

fig.subplots_adjust(left=0.088, right=0.978, top=0.805, bottom=0.115)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
print(f"  Aug 2026 peak      : {cur_v:.2f}%  ({cur_m})")
print(f"  Aug 31 close       : {AUG31_CLOSE:.2f}%")
print(f"  last month higher  : {PRIOR_M} at {PRIOR_V:.2f}%  -> {YEARS} years")
