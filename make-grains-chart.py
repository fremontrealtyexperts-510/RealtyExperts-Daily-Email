#!/usr/bin/env python3
"""
make-grains-chart.py  [out.png]

Correction of the "Wheat And Corn Hit 3-Year Highs" graphic Harv supplied for
the 08/31/26 daily email.

❌ THE SUPPLIED GRAPHIC DOES NOT RECONCILE. Its own source line reads "CBOT
futures settlements, Aug. 28, 2026," and NOT ONE of its four numbers is an
Aug 28 settlement. Every figure is a Monday 08/31 intraday quote, taken while
the pit was still open, and labeled as Friday's close.

  claim on graphic        Aug 28 SETTLE (ZW=F / ZC=F)      what the claim really is
  wheat $7.84/bu          767.00c  = $7.67/bu              08/31 intraday HIGH 784.75c
  wheat +54.5% YTD        +51.28%                          784.75 / 507 base
  corn  $5.37/bu          512.00c  = $5.12/bu              08/31 live tick ~536.5c
  corn  +21.8% YTD        +16.30%                          536.5 / 440.25 base

The YTD base is right in both cases (wheat 507.00, corn 440.25, the 12/31/25
closes), so the percentages are internally consistent with the graphic's own
inflated prices. It is the PRICES that are live ticks wearing a settlement label.
Market Briefs printed the same numbers the same way on 08/31.

⚠️ AND THE HEADLINE IS HALF WRONG. "Wheat And Corn Hit 3-Year Highs":
  • WHEAT, yes. At the 767.00 settle the last higher close was 02/15/23 at
    769.25, so "highest since February 2023" survives on settled data.
  • CORN, no. At the 512.00 settle corn was not at any kind of high: it closed
    HIGHER two sessions earlier, at 514.00 on 08/26. Corn only clears its
    July 2023 mark (540.25 on 07/26/23) on Monday's LIVE tick of ~535.50, which
    is not a settlement and could be given back before the 2:20 PM ET close.

So this chart plots the SETTLED series and marks Monday's in-progress session as
what it is. Same rule as Brent and as the 08/28 silver chart: report the last
completed session, draw a live leg dashed to an open marker, never let an
unsettled tick pose as a close.

WHY YTD PERCENT AND NOT TWO PRICE BARS: the supplied graphic's two bars hide the
actual news, which is that essentially the entire move is two weeks old. Wheat
closed at 682.75 on 08/20 and 767.00 on 08/28. A line over the year shows that;
a bar cannot.

DATA: CBOT front-month futures daily closes via Yahoo (ZW=F Chicago SRW wheat,
ZC=F corn), pulled 08/31/26. Indexed to the 12/31/25 close.

BRAND MARK: silver HB monogram, bottom right, no name text (Harv, 08/26/26).
matplotlib only; build with python3.13 on Mac.
"""
import sys
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

OUT = sys.argv[1] if len(sys.argv) > 1 else "grains-083126.png"
LOGO = "hb-logo-mark.png"

WHEAT_BASE, CORN_BASE = 507.00, 440.25     # 12/31/25 closes, cents per bushel
WHEAT = [
    ("2026-01-02",-0.099), ("2026-01-05",1.085), ("2026-01-06",0.69), ("2026-01-07",2.17),
    ("2026-01-08",2.17), ("2026-01-09",2.022), ("2026-01-12",0.838), ("2026-01-13",0.69),
    ("2026-01-14",1.085), ("2026-01-15",0.69), ("2026-01-16",2.17), ("2026-01-20",0.641),
    ("2026-01-21",0.148), ("2026-01-22",1.677), ("2026-01-23",4.438), ("2026-01-26",3.057),
    ("2026-01-27",3.205), ("2026-01-28",5.72), ("2026-01-29",6.805), ("2026-01-30",6.114),
    ("2026-02-02",4.093), ("2026-02-03",4.29), ("2026-02-04",3.895), ("2026-02-05",5.572),
    ("2026-02-06",4.487), ("2026-02-09",4.29), ("2026-02-10",4.191), ("2026-02-11",5.966),
    ("2026-02-12",8.974), ("2026-02-13",8.235), ("2026-02-17",6.065), ("2026-02-18",7.89),
    ("2026-02-19",10.355), ("2026-02-20",13.116), ("2026-02-23",12.327), ("2026-02-24",11.933),
    ("2026-02-25",11.588), ("2026-02-26",12.771), ("2026-02-27",16.617), ("2026-03-02",13.314),
    ("2026-03-03",12.87), ("2026-03-04",11.785), ("2026-03-05",14.941), ("2026-03-06",20.562),
    ("2026-03-09",17.949), ("2026-03-10",15.335), ("2026-03-11",16.075), ("2026-03-12",16.815),
    ("2026-03-13",21.992), ("2026-03-16",17.801), ("2026-03-17",16.321), ("2026-03-18",19.181),
    ("2026-03-19",19.921), ("2026-03-20",17.406), ("2026-03-23",15.927), ("2026-03-24",16.371),
    ("2026-03-25",17.899), ("2026-03-26",19.329), ("2026-03-27",19.329), ("2026-03-30",19.724),
    ("2026-03-31",21.548), ("2026-04-01",17.85), ("2026-04-02",17.998), ("2026-04-06",17.406),
    ("2026-04-07",17.949), ("2026-04-08",14.448), ("2026-04-09",13.314), ("2026-04-10",12.623),
    ("2026-04-13",14.842), ("2026-04-14",16.765), ("2026-04-15",17.11), ("2026-04-16",18.047),
    ("2026-04-17",16.617), ("2026-04-20",17.751), ("2026-04-21",19.329), ("2026-04-22",18.195),
    ("2026-04-23",20.464), ("2026-04-24",19.97), ("2026-04-27",22.584), ("2026-04-28",28.008),
    ("2026-04-29",26.677), ("2026-04-30",23.028), ("2026-05-01",23.176), ("2026-05-04",24.162),
    ("2026-05-05",21.598), ("2026-05-06",19.527), ("2026-05-07",18.688), ("2026-05-08",19.822),
    ("2026-05-11",22.732), ("2026-05-12",31.164), ("2026-05-13",31.164), ("2026-05-14",27.613),
    ("2026-05-15",25.394), ("2026-05-18",31.065), ("2026-05-19",31.607), ("2026-05-20",30.276),
    ("2026-05-21",27.712), ("2026-05-22",27.465), ("2026-05-26",25.345), ("2026-05-27",22.781),
    ("2026-05-28",23.077), ("2026-05-29",20.414), ("2026-06-01",20.069), ("2026-06-02",18.935),
    ("2026-06-03",15.828), ("2026-06-04",14.744), ("2026-06-05",14.398), ("2026-06-08",15.039),
    ("2026-06-09",15.434), ("2026-06-10",15.878), ("2026-06-11",15.73), ("2026-06-12",15.286),
    ("2026-06-15",16.321), ("2026-06-16",17.554), ("2026-06-17",20.858), ("2026-06-18",19.477),
    ("2026-06-22",17.85), ("2026-06-23",15.73), ("2026-06-24",15.533), ("2026-06-25",16.568),
    ("2026-06-26",14.053), ("2026-06-29",12.327), ("2026-06-30",14.546), ("2026-07-01",16.765),
    ("2026-07-02",16.469), ("2026-07-06",19.527), ("2026-07-07",20.168), ("2026-07-08",18.245),
    ("2026-07-09",20.562), ("2026-07-10",24.655), ("2026-07-13",23.669), ("2026-07-14",24.507),
    ("2026-07-15",33.629), ("2026-07-16",33.087), ("2026-07-17",34.665), ("2026-07-20",32.939),
    ("2026-07-21",33.728), ("2026-07-22",39.201), ("2026-07-23",37.327), ("2026-07-24",33.728),
    ("2026-07-27",30.178), ("2026-07-28",30.671), ("2026-07-29",30.325), ("2026-07-30",30.868),
    ("2026-07-31",26.085), ("2026-08-03",28.402), ("2026-08-04",25.937), ("2026-08-05",26.677),
    ("2026-08-06",24.507), ("2026-08-07",26.183), ("2026-08-10",26.331), ("2026-08-11",24.31),
    ("2026-08-12",28.748), ("2026-08-13",28.748), ("2026-08-14",33.087), ("2026-08-17",33.087),
    ("2026-08-18",31.065), ("2026-08-19",34.172), ("2026-08-20",34.665), ("2026-08-21",34.418),
    ("2026-08-24",34.467), ("2026-08-25",35.207), ("2026-08-26",44.083), ("2026-08-27",46.499),
    ("2026-08-28",51.282), ("2026-08-31",51.282),]
CORN = [
    ("2026-01-02",-0.625), ("2026-01-05",0.965), ("2026-01-06",0.852), ("2026-01-07",1.476),
    ("2026-01-08",1.306), ("2026-01-09",1.249), ("2026-01-12",-4.259), ("2026-01-13",-4.656),
    ("2026-01-14",-4.145), ("2026-01-15",-4.543), ("2026-01-16",-3.521), ("2026-01-20",-3.748),
    ("2026-01-21",-4.202), ("2026-01-22",-3.691), ("2026-01-23",-2.215), ("2026-01-26",-2.726),
    ("2026-01-27",-3.123), ("2026-01-28",-2.328), ("2026-01-29",-2.158), ("2026-01-30",-2.726),
    ("2026-02-02",-3.294), ("2026-02-03",-2.669), ("2026-02-04",-2.442), ("2026-02-05",-1.193),
    ("2026-02-06",-2.271), ("2026-02-09",-2.612), ("2026-02-10",-2.612), ("2026-02-11",-2.896),
    ("2026-02-12",-2.044), ("2026-02-13",-1.931), ("2026-02-17",-3.18), ("2026-02-18",-3.01),
    ("2026-02-19",-3.294), ("2026-02-20",-2.896), ("2026-02-23",-2.896), ("2026-02-24",-2.839),
    ("2026-02-25",-2.215), ("2026-02-26",-1.59), ("2026-02-27",-0.341), ("2026-03-02",-1.59),
    ("2026-03-03",-1.363), ("2026-03-04",-1.931), ("2026-03-05",0.284), ("2026-03-06",1.533),
    ("2026-03-09",-0.625), ("2026-03-10",-0.909), ("2026-03-11",0.909), ("2026-03-12",1.817),
    ("2026-03-13",2.783), ("2026-03-16",3.123), ("2026-03-17",3.123), ("2026-03-18",5.224),
    ("2026-03-19",6.701), ("2026-03-20",5.735), ("2026-03-23",4.373), ("2026-03-24",5.054),
    ("2026-03-25",6.133), ("2026-03-26",6.076), ("2026-03-27",4.94), ("2026-03-30",3.521),
    ("2026-03-31",3.975), ("2026-04-01",3.18), ("2026-04-02",2.726), ("2026-04-06",3.123),
    ("2026-04-07",1.988), ("2026-04-08",1.59), ("2026-04-09",0.852), ("2026-04-10",0.17),
    ("2026-04-13",0), ("2026-04-14",0.625), ("2026-04-15",2.499), ("2026-04-16",1.874),
    ("2026-04-17",1.931), ("2026-04-20",2.669), ("2026-04-21",3.066), ("2026-04-22",3.18),
    ("2026-04-23",3.464), ("2026-04-24",3.35), ("2026-04-27",4.656), ("2026-04-28",5.679),
    ("2026-04-29",5.963), ("2026-04-30",5.565), ("2026-05-01",6.36), ("2026-05-04",7.609),
    ("2026-05-05",5.735), ("2026-05-06",2.839), ("2026-05-07",2.839), ("2026-05-08",3.634),
    ("2026-05-11",4.656), ("2026-05-12",6.133), ("2026-05-13",5.963), ("2026-05-14",2.555),
    ("2026-05-15",3.521), ("2026-05-18",8.348), ("2026-05-19",7.95), ("2026-05-20",5.792),
    ("2026-05-21",4.997), ("2026-05-22",5.224), ("2026-05-26",3.918), ("2026-05-27",2.783),
    ("2026-05-28",3.521), ("2026-05-29",1.476), ("2026-06-01",0.852), ("2026-06-02",0.057),
    ("2026-06-03",-1.988), ("2026-06-04",-3.578), ("2026-06-05",-5.168), ("2026-06-08",-4.884),
    ("2026-06-09",-4.713), ("2026-06-10",-4.827), ("2026-06-11",-6.474), ("2026-06-12",-6.246),
    ("2026-06-15",-5.622), ("2026-06-16",-6.019), ("2026-06-17",-4.373), ("2026-06-18",-5.168),
    ("2026-06-22",-6.53), ("2026-06-23",-6.928), ("2026-06-24",-7.553), ("2026-06-25",-5.792),
    ("2026-06-26",-6.246), ("2026-06-29",-8.688), ("2026-06-30",-6.246), ("2026-07-01",-4.373),
    ("2026-07-02",-3.464), ("2026-07-06",0.114), ("2026-07-07",0.511), ("2026-07-08",-1.249),
    ("2026-07-09",-2.839), ("2026-07-10",-0.511), ("2026-07-13",-0.568), ("2026-07-14",-1.476),
    ("2026-07-15",1.647), ("2026-07-16",0.284), ("2026-07-17",1.022), ("2026-07-20",2.101),
    ("2026-07-21",2.839), ("2026-07-22",4.94), ("2026-07-23",5.395), ("2026-07-24",5.451),
    ("2026-07-27",2.612), ("2026-07-28",4.145), ("2026-07-29",1.988), ("2026-07-30",1.249),
    ("2026-07-31",0.114), ("2026-08-03",2.044), ("2026-08-04",0.454), ("2026-08-05",-0.795),
    ("2026-08-06",-0.284), ("2026-08-07",-0.284), ("2026-08-10",-0.454), ("2026-08-11",-0.795),
    ("2026-08-12",3.805), ("2026-08-13",1.76), ("2026-08-14",4.259), ("2026-08-17",5.622),
    ("2026-08-18",5.224), ("2026-08-19",7.439), ("2026-08-20",8.745), ("2026-08-21",9.881),
    ("2026-08-24",11.641), ("2026-08-25",13.685), ("2026-08-26",16.752), ("2026-08-27",15.9),
    ("2026-08-28",16.298), ("2026-08-31",21.635),]

TODAY = "2026-08-31"        # in progress at build time
CREAM = "#fdf6e8"; INK = "#1f2933"; CORAL = "#e2574c"; DEEP = "#b8433a"
GOLD  = "#d9922e"; SLATE = "#4a5568"; GRID = "#d8cdb8"

def split(series):
    return [p for p in series if p[0] < TODAY], [p for p in series if p[0] == TODAY]

w_set, w_live = split(WHEAT)
c_set, c_live = split(CORN)
assert w_set[-1][0] == "2026-08-28" and c_set[-1][0] == "2026-08-28"
assert w_live and c_live, "expected an in-progress 08/31 bar"

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

def dt(s):
    y, m, d = (int(x) for x in s.split("-")); return date(y, m, d)

fig, ax = plt.subplots(figsize=(12.6, 7.0), dpi=170)
fig.patch.set_facecolor(CREAM); ax.set_facecolor(CREAM)

for series, live, color, label in ((w_set, w_live, DEEP, "Wheat"),
                                   (c_set, c_live, GOLD, "Corn")):
    ax.plot([dt(d) for d, _ in series], [v for _, v in series],
            color=color, lw=2.6, zorder=4, solid_capstyle="round")
    # in-progress Monday session: dashed reach to an open marker, never a close
    ax.plot([dt(series[-1][0]), dt(live[0][0])], [series[-1][1], live[0][1]],
            color=color, lw=1.8, ls=(0, (4, 3)), zorder=5)
    ax.plot([dt(live[0][0])], [live[0][1]], marker="o", ms=9,
            mfc=CREAM, mec=color, mew=2.1, zorder=6)

ax.axhline(0, color=SLATE, lw=1.1, zorder=2)

ax.annotate(f"Wheat  +{w_set[-1][1]:.1f}%",
            xy=(dt(w_set[-1][0]), w_set[-1][1]), xytext=(-6, 20),
            textcoords="offset points", ha="right", fontsize=15,
            fontweight="bold", color=DEEP)
ax.annotate(f"Corn  +{c_set[-1][1]:.1f}%",
            xy=(dt(c_set[-1][0]), c_set[-1][1]), xytext=(-6, -30),
            textcoords="offset points", ha="right", fontsize=15,
            fontweight="bold", color=GOLD)
# Placed in the empty band above +50% and given a leader to the wheat marker.
# Sitting it beside the markers (xytext=(-190,-6)) drew the text straight across
# the wheat line; caught by eyeballing the render.
ax.annotate("open markers are Monday's\nunsettled session",
            xy=(dt(TODAY), w_live[0][1]), xytext=(dt("2026-05-20"), 57.5),
            ha="left", va="center", fontsize=11.5, color=SLATE, linespacing=1.4,
            arrowprops=dict(arrowstyle="-", color=SLATE, lw=1.0,
                            shrinkA=6, shrinkB=10, alpha=0.65))

ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.yaxis.set_major_formatter(lambda v, p: f"{v:+.0f}%".replace("+0%", "0%"))
ax.set_ylim(-16, 62)
ax.grid(axis="y", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=12.5, colors=SLATE)
ax.set_ylabel("Change since December 31, 2025", fontsize=12.5, color=SLATE, labelpad=10)

fig.text(0.046, 0.958, "Grain prices went vertical in the last two weeks",
         fontsize=26.5, fontweight="bold", color=INK, va="top")
fig.text(0.046, 0.897,
         "2026 change in CBOT front month futures. Wheat is at its highest settle "
         "since February 2023.",
         fontsize=14, color=SLATE, va="top")
fig.text(0.008, 0.038,
         "Source: CBOT front month futures daily closes (ZW=F, ZC=F). Indexed to the "
         "December 31, 2025 close: wheat 507.00c, corn 440.25c.",
         fontsize=11, color=SLATE)
fig.text(0.008, 0.012,
         "Lines end at the August 28 settlement, the last completed session. Monday August 31 was "
         "still trading when this was built.",
         fontsize=11, color=SLATE)
add_logo(fig)

fig.subplots_adjust(left=0.088, right=0.978, top=0.805, bottom=0.115)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
print(f"  wheat settle 08/28 : +{w_set[-1][1]:.2f}%  (767.00c = $7.67/bu)   live 08/31 +{w_live[0][1]:.2f}%")
print(f"  corn  settle 08/28 : +{c_set[-1][1]:.2f}%  (512.00c = $5.12/bu)   live 08/31 +{c_live[0][1]:.2f}%")
print(f"  graphic claimed    : wheat +54.5% ($7.84), corn +21.8% ($5.37)  <- both Monday intraday")
