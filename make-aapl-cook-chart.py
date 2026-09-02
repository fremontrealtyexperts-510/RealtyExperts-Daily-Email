#!/usr/bin/env python3
"""
make-aapl-cook-chart.py  [out.png]

Recreation of the Apple all-time stock graphic Harv supplied for the 09/02/26
daily email, REFRAMED. Today's news is the handoff: John Ternus became Apple's
CEO on September 1, 2026, succeeding Tim Cook after 15 years.

⚠️ VERIFICATION 09/02/26 — THE SUPPLIED GRAPHIC'S HEADLINE NUMBER IS WRONG.

The supplied card reads "$325.13 / ALL TIME / +203,106%", sourced to Google
Finance, split adjusted, September 1, 2026.

  ✅ $325.13 is correct. AAPL's split adjusted close on 2026-09-01 was exactly
     $325.13 (Yahoo Finance daily series, cross checked against the monthly).

  ❌ +203,106% does not reconcile with any all time base. Apple's first trading
     day was 1980-12-12, closing at $28.75, which is $0.128348 split adjusted
     (the cumulative factor since the IPO is 224: 2:1 in 1987, 2000 and 2005,
     7:1 in 2014, 4:1 in 2020; 0.128348 x 224 = 28.75, so the series is
     internally consistent). From that close:

         price only, split adjusted   325.13 / 0.128348  ->  +253,219%
         total return, dividends in   325.13 / 0.098122  ->  +331,251%

     Neither is 203,106%. Working backwards, +203,106% implies a base of
     $0.16000, which is not the IPO close: AAPL first closed at $0.16016 in
     JUNE 1986, five and a half years after listing. So the card either starts
     its "all time" in the middle of 1986 or the number is simply wrong. Either
     way it is not the all time return, and it UNDERSTATES it by about 50,000
     percentage points.

⚠️ AND THE FRAME HIDES ITS OWN STORY. The supplied chart is linear and spans
1980 to 2026, so Cook's first decade is a flat line hugging zero. Its one
annotation, "Tim Cook takes over as CEO", points at a stretch of chart where
visibly nothing happens. The arrow marks the handoff but the drawing makes the
tenure look like the boring part. On the day Cook hands the company over, the
chart worth showing is the one that shows what his tenure actually did.

So this recreation plots COOK'S TENURE, where the shape is legible and the
headline is visible rather than asserted:

    2011-08-24  Cook's first day as CEO, close  $13.4350   (split adjusted)
    2026-09-01  Ternus's first day, close      $325.1300
    return                                     +2,320.0%

Market Briefs put the same figure at "about 2,275%" this morning. Close, and
they hedged it with "about", but the arithmetic off the actual closes is
+2,320%, so the report uses that.

Monthly closes below are month end split adjusted closes from the Yahoo Finance
daily series, with the true 2026-09-01 close appended as the final point.

BRAND MARK: silver HB monogram, bottom right, no name text (Harv, 08/26/26).
matplotlib only; build with python3.13 on Mac.
"""
import sys
import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "aapl-cook-090226.png"
LOGO = "hb-logo-mark.png"

COOK_START = ("2011-08-24", 13.4350)   # first day as CEO
SERIES = [
    ("2011-08-31", 13.7439),
    ("2011-09-30", 13.6186),
    ("2011-10-31", 14.4564),
    ("2011-11-30", 13.6500),
    ("2011-12-30", 14.4643),
    ("2012-01-31", 16.3029),
    ("2012-02-29", 19.3729),
    ("2012-03-30", 21.4125),
    ("2012-04-30", 20.8564),
    ("2012-05-31", 20.6332),
    ("2012-06-29", 20.8571),
    ("2012-07-31", 21.8129),
    ("2012-08-31", 23.7586),
    ("2012-09-28", 23.8250),
    ("2012-10-31", 21.2614),
    ("2012-11-30", 20.9029),
    ("2012-12-31", 19.0061),
    ("2013-01-31", 16.2675),
    ("2013-02-28", 15.7643),
    ("2013-03-28", 15.8093),
    ("2013-04-30", 15.8136),
    ("2013-05-31", 16.0618),
    ("2013-06-28", 14.1618),
    ("2013-07-31", 16.1618),
    ("2013-08-30", 17.4007),
    ("2013-09-30", 17.0268),
    ("2013-10-31", 18.6679),
    ("2013-11-29", 19.8596),
    ("2013-12-31", 20.0364),
    ("2014-01-31", 17.8786),
    ("2014-02-28", 18.7943),
    ("2014-03-31", 19.1693),
    ("2014-04-30", 21.0746),
    ("2014-05-30", 22.6071),
    ("2014-06-30", 23.2325),
    ("2014-07-31", 23.9000),
    ("2014-08-29", 25.6250),
    ("2014-09-30", 25.1875),
    ("2014-10-31", 27.0000),
    ("2014-11-28", 29.7325),
    ("2014-12-31", 27.5950),
    ("2015-01-30", 29.2900),
    ("2015-02-27", 32.1150),
    ("2015-03-31", 31.1075),
    ("2015-04-30", 31.2875),
    ("2015-05-29", 32.5700),
    ("2015-06-30", 31.3575),
    ("2015-07-31", 30.3250),
    ("2015-08-31", 28.1900),
    ("2015-09-30", 27.5750),
    ("2015-10-30", 29.8750),
    ("2015-11-30", 29.5750),
    ("2015-12-31", 26.3150),
    ("2016-01-29", 24.3350),
    ("2016-02-29", 24.1725),
    ("2016-03-31", 27.2475),
    ("2016-04-29", 23.4350),
    ("2016-05-31", 24.9650),
    ("2016-06-30", 23.9000),
    ("2016-07-29", 26.0525),
    ("2016-08-31", 26.5250),
    ("2016-09-30", 28.2625),
    ("2016-10-31", 28.3850),
    ("2016-11-30", 27.6300),
    ("2016-12-30", 28.9550),
    ("2017-01-31", 30.3375),
    ("2017-02-28", 34.2475),
    ("2017-03-31", 35.9150),
    ("2017-04-28", 35.9125),
    ("2017-05-31", 38.1900),
    ("2017-06-30", 36.0050),
    ("2017-07-31", 37.1825),
    ("2017-08-31", 41.0000),
    ("2017-09-29", 38.5300),
    ("2017-10-31", 42.2600),
    ("2017-11-30", 42.9625),
    ("2017-12-29", 42.3075),
    ("2018-01-31", 41.8575),
    ("2018-02-28", 44.5300),
    ("2018-03-29", 41.9450),
    ("2018-04-30", 41.3150),
    ("2018-05-31", 46.7175),
    ("2018-06-29", 46.2775),
    ("2018-07-31", 47.5725),
    ("2018-08-31", 56.9075),
    ("2018-09-28", 56.4350),
    ("2018-10-31", 54.7150),
    ("2018-11-30", 44.6450),
    ("2018-12-31", 39.4350),
    ("2019-01-31", 41.6100),
    ("2019-02-28", 43.2875),
    ("2019-03-29", 47.4875),
    ("2019-04-30", 50.1675),
    ("2019-05-31", 43.7675),
    ("2019-06-28", 49.4800),
    ("2019-07-31", 53.2600),
    ("2019-08-30", 52.1850),
    ("2019-09-30", 55.9925),
    ("2019-10-31", 62.1900),
    ("2019-11-29", 66.8125),
    ("2019-12-31", 73.4125),
    ("2020-01-31", 77.3775),
    ("2020-02-28", 68.3400),
    ("2020-03-31", 63.5725),
    ("2020-04-30", 73.4500),
    ("2020-05-29", 79.4850),
    ("2020-06-30", 91.2000),
    ("2020-07-31", 106.2600),
    ("2020-08-31", 129.0400),
    ("2020-09-30", 115.8100),
    ("2020-10-30", 108.8600),
    ("2020-11-30", 119.0500),
    ("2020-12-31", 132.6900),
    ("2021-01-29", 131.9600),
    ("2021-02-26", 121.2600),
    ("2021-03-31", 122.1500),
    ("2021-04-30", 131.4600),
    ("2021-05-28", 124.6100),
    ("2021-06-30", 136.9600),
    ("2021-07-30", 145.8600),
    ("2021-08-31", 151.8300),
    ("2021-09-30", 141.5000),
    ("2021-10-29", 149.8000),
    ("2021-11-30", 165.3000),
    ("2021-12-31", 177.5700),
    ("2022-01-31", 174.7800),
    ("2022-02-28", 165.1200),
    ("2022-03-31", 174.6100),
    ("2022-04-29", 157.6500),
    ("2022-05-31", 148.8400),
    ("2022-06-30", 136.7200),
    ("2022-07-29", 162.5100),
    ("2022-08-31", 157.2200),
    ("2022-09-30", 138.2000),
    ("2022-10-31", 153.3400),
    ("2022-11-30", 148.0300),
    ("2022-12-30", 129.9300),
    ("2023-01-31", 144.2900),
    ("2023-02-28", 147.4100),
    ("2023-03-31", 164.9000),
    ("2023-04-28", 169.6800),
    ("2023-05-31", 177.2500),
    ("2023-06-30", 193.9700),
    ("2023-07-31", 196.4500),
    ("2023-08-31", 187.8700),
    ("2023-09-29", 171.2100),
    ("2023-10-31", 170.7700),
    ("2023-11-30", 189.9500),
    ("2023-12-29", 192.5300),
    ("2024-01-31", 184.4000),
    ("2024-02-29", 180.7500),
    ("2024-03-28", 171.4800),
    ("2024-04-30", 170.3300),
    ("2024-05-31", 192.2500),
    ("2024-06-28", 210.6200),
    ("2024-07-31", 222.0800),
    ("2024-08-30", 229.0000),
    ("2024-09-30", 233.0000),
    ("2024-10-31", 225.9100),
    ("2024-11-29", 237.3300),
    ("2024-12-31", 250.4200),
    ("2025-01-31", 236.0000),
    ("2025-02-28", 241.8400),
    ("2025-03-31", 222.1300),
    ("2025-04-30", 212.5000),
    ("2025-05-30", 200.8500),
    ("2025-06-30", 205.1700),
    ("2025-07-31", 207.5700),
    ("2025-08-29", 232.1400),
    ("2025-09-30", 254.6300),
    ("2025-10-31", 270.3700),
    ("2025-11-28", 278.8500),
    ("2025-12-31", 271.8600),
    ("2026-01-30", 259.4800),
    ("2026-02-27", 264.1800),
    ("2026-03-31", 253.7900),
    ("2026-04-30", 271.3500),
    ("2026-05-29", 312.0600),
    ("2026-06-30", 289.3600),
    ("2026-07-31", 308.9100),
    ("2026-08-28", 319.7000),
    ("2026-09-01", 325.1300),]
SERIES = [COOK_START] + SERIES

CREAM = "#fdf6e8"
INK   = "#1f2933"
CORAL = "#e2574c"
DEEP  = "#b8433a"
SLATE = "#4a5568"
GRID  = "#d8cdb8"

start_v = COOK_START[1]
end_d, end_v = SERIES[-1]
ret = (end_v / start_v - 1) * 100
assert abs(ret - 2320.0) < 1.0, f"Cook era return moved: {ret:.1f}%"
assert end_v == 325.13, "final close must be the verified 09/01/26 close"

xs = [datetime.date.fromisoformat(d) for d, _ in SERIES]
ys = [v for _, v in SERIES]

fig, ax = plt.subplots(figsize=(12.6, 7.0), dpi=170)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

ax.plot(xs, ys, color=CORAL, lw=2.6, zorder=4, solid_capstyle="round")
ax.fill_between(xs, ys, color=CORAL, alpha=0.11, zorder=2)

# endpoints
ax.plot([xs[0]], [ys[0]], "o", ms=9, color=DEEP, zorder=6)
ax.plot([xs[-1]], [ys[-1]], "o", ms=10, color=DEEP, zorder=6)

ax.annotate("Tim Cook becomes CEO\nAug 24, 2011   \\$13.44",
            xy=(xs[0], ys[0]), xytext=(datetime.date(2012, 10, 1), 88),
            fontsize=13.5, fontweight="bold", color=INK, ha="left", va="center",
            arrowprops=dict(arrowstyle="-|>", color=SLATE, lw=1.6,
                            connectionstyle="arc3,rad=0.28"), zorder=7)

ax.annotate("John Ternus takes over\nSep 1, 2026   \\$325.13",
            xy=(xs[-1], ys[-1]), xytext=(datetime.date(2020, 1, 1), 322),
            fontsize=13.5, fontweight="bold", color=INK, ha="left", va="center",
            arrowprops=dict(arrowstyle="-|>", color=SLATE, lw=1.6,
                            connectionstyle="arc3,rad=-0.22"), zorder=7)

ax.text(datetime.date(2013, 6, 1), 205, "+2,320%",
        fontsize=46, fontweight="bold", color=DEEP, ha="left", va="center", zorder=7)
ax.text(datetime.date(2013, 6, 1), 172,
        "Apple's split adjusted share price\nover Cook's 15 years",
        fontsize=13.5, color=SLATE, ha="left", va="center", zorder=7)

ax.set_ylim(0, 360)
ax.set_xlim(datetime.date(2011, 1, 1), datetime.date(2027, 6, 1))
ax.set_yticks([0, 100, 200, 300])
ax.set_yticklabels(["0", "\\$100", "\\$200", "\\$300"])
ax.set_xticks([datetime.date(y, 1, 1) for y in (2012, 2015, 2018, 2021, 2024)])
ax.set_xticklabels(["2012", "2015", "2018", "2021", "2024"])

ax.grid(axis="y", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=12.5, colors=SLATE)

fig.text(0.046, 0.958, "What Tim Cook's 15 years built",
         fontsize=26.5, fontweight="bold", color=INK, va="top")
fig.text(0.046, 0.897,
         "Apple's share price from Cook's first day as CEO to the handoff, split adjusted",
         fontsize=14, color=SLATE, va="top")

fig.text(0.008, 0.022,
         "Source: Nasdaq daily closes via Yahoo Finance, split adjusted. Cook became CEO "
         "Aug 24, 2011; John Ternus succeeded him Sep 1, 2026.",
         fontsize=11, color=SLATE)


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


add_logo(fig)

fig.subplots_adjust(left=0.082, right=0.985, top=0.805, bottom=0.115)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
print(f"  Cook start {COOK_START[0]}  ${start_v:,.4f}")
print(f"  handoff    {end_d}  ${end_v:,.2f}")
print(f"  return     +{ret:,.1f}%")
print(f"  supplied graphic claimed +203,106% all time; true all time is +253,219%")
