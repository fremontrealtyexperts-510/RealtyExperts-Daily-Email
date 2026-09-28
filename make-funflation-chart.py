#!/usr/bin/env python3
"""
make-funflation-chart.py  DATA_DIR  [outdir]

"Fun is getting pricier", recreated for the 09/28/26 daily from Harv's supplied
graphic (airfares +26.5%, hobby and sport stores +10.7%, hobby spending +7.9%,
all retail sales +6.0%, recreation prices +2.7%, "12 months through August
2026", source "BLS, U.S. Census Bureau, Bank of America via CNBC").

  funflation-092826.png      plain monogram -> RE email + Agent Hub
  funflation-092826-hb.png   + wordmark     -> harvrealtor.com / .net / app

=============================================================================
WHAT CHANGED FROM THE SUPPLIED GRAPHIC, AND WHY
=============================================================================

1. AIRFARES WAS THE WRONG MONTH. BLS CPI airline fares (CUUR0000SETG01, not
   seasonally adjusted) rose 23.4% in the 12 months through AUGUST 2026. The
   graphic's 26.5% is JUNE's reading (26.54%); July was 25.55%. CNBC's own
   text says "26.5% year-on-year, according to federal data in August", which
   is where the graphic got it. Corrected to August's figure.
2. PRICES AND SPENDING ARE SEPARATED. The original ranked price changes (CPI)
   and sales changes (Census, Bank of America cards) as one list under a
   "pricier" title, but store sales and card spending are dollars spent, not
   prices. Two labeled groups keep the title honest.
3. LOCAL BAR ADDED (feedback-localize-national-studies). BLS publishes CPI
   recreation for the San Francisco, Oakland and Hayward area (CUURS49BSAR,
   bimonthly, even months), which includes Alameda County. August 2026 is its
   latest reading. U.S. all items CPI is added as the price baseline, the way
   all retail sales is the spending baseline.

Verified unchanged: recreation +2.7% (CUUR0000SAR), sporting goods, hobby,
musical instrument and book stores +10.7% and retail and food services +6.0%
(Census advance report of September 16, 2026, adjusted, August over August),
and Bank of America's hobby card spending +7.9% (August 2026 year on year, as
reported by CNBC on 09/27/26; the bank's public Consumer Checkpoint does not
carry the hobby cut, so CNBC's verbatim sentence is the citation).

DATA_DIR must hold, fetched with shell curl on 09/28/26:
  bls.json               BLS API v2 response for the CPI series above
  marts.txt              pdftotext -layout of census.gov marts_current.pdf
  cnbc-funflation.txt    text of the CNBC article (syndicated copy; cnbc.com 403s)
Every value is parsed from those files at build time, never typed.

matplotlib only; build with python3.13 on Mac.
"""
import json
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

DATA = sys.argv[1]
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "."
STAMP = "092826"
LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hb-logo-mark.png")

CREAM = "#fdf6e8"
INK = "#1f2933"
GRID = "#d8cdb8"
MUTED = "#8a8172"
BLUE = "#2f6f9f"     # the fun categories
CORAL = "#e2574c"    # the local bar
TAN = "#b8a582"      # the all items / all sales baselines


def q1(x):
    return Decimal(str(x)).quantize(Decimal("0.1"), ROUND_HALF_UP)


# ---------------------------------------------------------------- BLS CPI
bls = {s["seriesID"]: {(r["year"], r["period"]): r["value"] for r in s["data"]}
       for s in json.load(open(os.path.join(DATA, "bls.json")))["Results"]["series"]}


def cpi_yoy(sid, y="2026", p="M08"):
    a, b = float(bls[sid][(y, p)]), float(bls[sid][(str(int(y) - 1), p)])
    return (a / b - 1) * 100


AIR = cpi_yoy("CUUR0000SETG01")
AIR_JUN = cpi_yoy("CUUR0000SETG01", p="M06")
REC = cpi_yoy("CUUR0000SAR")
ALL = cpi_yoy("CUUR0000SA0")
REC_SF = cpi_yoy("CUURS49BSAR")
ALL_SF = cpi_yoy("CUURS49BSA0")
assert q1(AIR_JUN) == Decimal("26.5"), AIR_JUN   # the graphic's number is June's

# ---------------------------------------------------------------- Census
marts = open(os.path.join(DATA, "marts.txt")).read()
assert "ADVANCE MONTHLY SALES FOR RETAIL AND FOOD SERVICES, AUGUST 2026" in marts
t2 = marts[marts.index("Table 2."):]
# Table 2 columns: Aug 2026 from Jul 2026, Aug 2026 from Aug 2025, ...
m451 = re.search(r"451\s+Sporting goods, hobby, musical\s+instrument, & book stores\s*[.…\s]*"
                 r"([-\d.]+)\s+([-\d.]+)", t2)
mtot = re.search(r"Retail & food services,\s+total\s*[.…\s]*([-\d.]+)\s+([-\d.]+)", t2)
HOBBY_STORES = float(m451.group(2))
ALL_RETAIL = float(mtot.group(2))

# ---------------------------------------------------------------- BofA via CNBC
cnbc = open(os.path.join(DATA, "cnbc-funflation.txt")).read()
mb = re.search(r"grew (\d+\.\d)% in August 2026, year on year, per the bank", cnbc)
BOFA = float(mb.group(1))

PRICES = [("Airline fares", AIR, BLUE),
          ("Recreation, Bay Area*", REC_SF, CORAL),
          ("All items (overall inflation)", ALL, TAN),
          ("Recreation, U.S.", REC, BLUE)]
SPEND = [("Sporting goods, hobby,\nmusic and book stores", HOBBY_STORES, BLUE),
         ("Hobby spending,\nBank of America cards", BOFA, BLUE),
         ("All retail and\nrestaurant sales", ALL_RETAIL, TAN)]

fig, ax = plt.subplots(figsize=(11.6, 8.2))
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)
for s in ("top", "right", "left", "bottom"):
    ax.spines[s].set_visible(False)
ax.set_xticks([])
ax.set_yticks([])

rows = []          # (y, label, value, color)
y = 0.0
GAP_ROW, GAP_GROUP = 1.0, 1.25
heads = []
heads.append((y, "WHAT IT COSTS  (consumer prices)"))
y -= 0.85
for lab, v, c in PRICES:
    rows.append((y, lab, v, c))
    y -= GAP_ROW
y -= GAP_GROUP - GAP_ROW + 0.35
heads.append((y, "WHAT PEOPLE SPEND  (sales)"))
y -= 0.85
for lab, v, c in SPEND:
    rows.append((y, lab, v, c))
    y -= GAP_ROW

XMAX = 30.0
for yy, lab, v, c in rows:
    ax.barh(yy, v, height=0.62, color=c, edgecolor=CREAM, linewidth=2, zorder=3)
    ax.text(-0.6, yy, lab, ha="right", va="center", fontsize=12.5, color=INK,
            linespacing=1.15)
    ax.text(v + 0.5, yy, f"+{q1(v)}%", ha="left", va="center", fontsize=14.5,
            fontweight="bold", color=INK)
for yy, h in heads:
    ax.text(-0.6, yy, h, ha="right", va="center", fontsize=10.5, color=MUTED,
            fontweight="bold")
    ax.plot([-0.3, XMAX], [yy, yy], color=GRID, lw=0.8, zorder=1)

ax.set_xlim(-0.2, XMAX)
ax.set_ylim(y + 0.4, 0.6)
fig.subplots_adjust(left=0.30, right=0.975, top=0.855, bottom=0.13)

fig.text(0.062, 0.955, "Fun is getting pricier, and people keep paying",
         fontsize=20, fontweight="bold", color=INK, ha="left")
fig.text(0.062, 0.915,
         "Change from a year earlier, August 2026. Prices on top, spending below.",
         fontsize=11.4, color=MUTED, ha="left")
fig.text(0.062, 0.030,
         "Sources: BLS Consumer Price Index (not seasonally adjusted); Census Bureau advance retail sales, Sept 16, 2026;\n"
         "Bank of America card data as reported by CNBC. *BLS San Francisco, Oakland and Hayward area, which includes Alameda County.",
         fontsize=8.8, color=MUTED, ha="left", linespacing=1.45)
save_pair(fig, os.path.join(OUTDIR, f"funflation-{STAMP}.png"), logo=LOGO)

print("\nChecks (Aug 2026 vs Aug 2025):")
for lab, v, _ in PRICES + SPEND:
    print(f"  {lab.replace(chr(10), ' '):<45} {v:6.2f}%")
print(f"  airline fares June 2026 (the graphic's number): {AIR_JUN:.2f}%")
print(f"  Bay Area all items: {ALL_SF:.2f}%")
