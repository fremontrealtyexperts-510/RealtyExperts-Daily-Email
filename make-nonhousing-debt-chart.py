#!/usr/bin/env python3
"""
make-nonhousing-debt-chart.py  [out.png]

REALTY EXPERTS branded recreation of the "Non-Housing Debt Balance" graphic for
the 08/12/26 daily email (Market Briefs "Big swing." / the More Debt story).
OUR OWN branded chart, not the source image.

VINTAGE CORRECTION. The supplied graphic was titled "Q1 2026 total: $5.1 trillion".
The New York Fed released the Q2 2026 Household Debt and Credit Report on
August 11, 2026, which is the release the newsletter story is actually reporting
on ("card balances hit $1.26T"). This chart is rebuilt on the Q2 2026 vintage,
pulled straight from the source workbook (HHD_C_Report_2026Q2.xlsx, Page 3 Data),
so the endpoint is the current release rather than the prior quarter. The
supplied graphic's component callouts did not match Q1 2026 in the current
vintage either (it showed auto $1.65T and student $1.63T against an actual
$1.69T and $1.66T), so every point here comes from the workbook.

Q2 2026 endpoint, non-housing debt: auto $1.71T, credit card $1.26T, student
$1.65T, other $0.57T, total $5.20T.

Warm cream ground (Meridian paper), stacked areas in the house palette with the
credit card band carried in coral because that is the story, end labels on each
band. No authorship label; footer carries the data source only. Run python3.13.
"""
import sys
from decimal import Decimal, ROUND_HALF_UP
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "nonhousing-debt-081226.png"


def t(x):
    """Trillions label, rounded HALF_UP (Python's default rounds half-to-even)."""
    return "$" + str(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)) + "T"


# (period, auto loan, credit card, student loan, other) in $ trillions.
# NOTE column order: index 3 is STUDENT LOAN, index 4 is OTHER.
# Source: New York Fed Consumer Credit Panel / Equifax, Household Debt and Credit
# Report 2026 Q2, "Page 3 Data" (Total Debt Balance and Its Composition).
SERIES = [
    ("03:Q1", 0.6410, 0.6880, 0.2407, 0.4776),
    ("03:Q2", 0.6220, 0.6930, 0.2429, 0.4860),
    ("03:Q3", 0.6840, 0.6930, 0.2488, 0.4773),
    ("03:Q4", 0.7040, 0.6980, 0.2529, 0.4486),
    ("04:Q1", 0.7200, 0.6950, 0.2598, 0.4465),
    ("04:Q2", 0.7430, 0.6970, 0.2629, 0.4231),
    ("04:Q3", 0.7510, 0.7060, 0.3300, 0.4100),
    ("04:Q4", 0.7280, 0.7170, 0.3457, 0.4229),
    ("05:Q1", 0.7250, 0.7100, 0.3636, 0.3941),
    ("05:Q2", 0.7740, 0.7170, 0.3744, 0.4024),
    ("05:Q3", 0.8300, 0.7320, 0.3777, 0.4054),
    ("05:Q4", 0.7920, 0.7360, 0.3917, 0.4155),
    ("06:Q1", 0.7880, 0.7230, 0.4345, 0.4183),
    ("06:Q2", 0.7960, 0.7390, 0.4389, 0.4232),
    ("06:Q3", 0.8210, 0.7540, 0.4467, 0.4417),
    ("06:Q4", 0.8210, 0.7670, 0.4816, 0.4057),
    ("07:Q1", 0.7940, 0.7640, 0.5064, 0.4039),
    ("07:Q2", 0.8070, 0.7960, 0.5140, 0.4078),
    ("07:Q3", 0.8180, 0.8170, 0.5285, 0.4130),
    ("07:Q4", 0.8150, 0.8390, 0.5475, 0.4221),
    ("08:Q1", 0.8080, 0.8370, 0.5792, 0.4153),
    ("08:Q2", 0.8100, 0.8500, 0.5863, 0.4008),
    ("08:Q3", 0.8090, 0.8580, 0.6109, 0.4115),
    ("08:Q4", 0.7910, 0.8660, 0.6393, 0.4116),
    ("09:Q1", 0.7660, 0.8430, 0.6628, 0.4088),
    ("09:Q2", 0.7430, 0.8240, 0.6754, 0.3888),
    ("09:Q3", 0.7390, 0.8120, 0.6945, 0.3815),
    ("09:Q4", 0.7219, 0.7950, 0.7213, 0.3785),
    ("10:Q1", 0.7047, 0.7624, 0.7578, 0.3629),
    ("10:Q2", 0.7022, 0.7444, 0.7617, 0.3491),
    ("10:Q3", 0.7100, 0.7311, 0.7782, 0.3427),
    ("10:Q4", 0.7110, 0.7296, 0.8118, 0.3410),
    ("11:Q1", 0.7056, 0.6964, 0.8392, 0.3287),
    ("11:Q2", 0.7130, 0.6943, 0.8514, 0.3303),
    ("11:Q3", 0.7304, 0.6933, 0.8702, 0.3266),
    ("11:Q4", 0.7341, 0.7040, 0.8736, 0.3300),
    ("12:Q1", 0.7365, 0.6788, 0.9037, 0.3185),
    ("12:Q2", 0.7500, 0.6720, 0.9140, 0.3120),
    ("12:Q3", 0.7680, 0.6740, 0.9560, 0.3110),
    ("12:Q4", 0.7830, 0.6790, 0.9660, 0.3170),
    ("13:Q1", 0.7940, 0.6600, 0.9860, 0.3070),
    ("13:Q2", 0.8140, 0.6680, 0.9940, 0.2960),
    ("13:Q3", 0.8450, 0.6720, 1.0270, 0.3040),
    ("13:Q4", 0.8630, 0.6830, 1.0800, 0.3170),
    ("14:Q1", 0.8750, 0.6590, 1.1110, 0.3140),
    ("14:Q2", 0.9050, 0.6690, 1.1180, 0.3230),
    ("14:Q3", 0.9340, 0.6800, 1.1260, 0.3270),
    ("14:Q4", 0.9550, 0.7000, 1.1570, 0.3350),
    ("15:Q1", 0.9680, 0.6840, 1.1890, 0.3290),
    ("15:Q2", 1.0060, 0.7030, 1.1900, 0.3390),
    ("15:Q3", 1.0450, 0.7140, 1.2030, 0.3510),
    ("15:Q4", 1.0640, 0.7330, 1.2320, 0.3510),
    ("16:Q1", 1.0710, 0.7120, 1.2610, 0.3540),
    ("16:Q2", 1.1030, 0.7290, 1.2590, 0.3560),
    ("16:Q3", 1.1350, 0.7470, 1.2790, 0.3670),
    ("16:Q4", 1.1570, 0.7790, 1.3100, 0.3770),
    ("17:Q1", 1.1670, 0.7640, 1.3440, 0.3670),
    ("17:Q2", 1.1900, 0.7840, 1.3440, 0.3780),
    ("17:Q3", 1.2130, 0.8080, 1.3570, 0.3860),
    ("17:Q4", 1.2210, 0.8340, 1.3780, 0.3890),
    ("18:Q1", 1.2290, 0.8150, 1.4070, 0.3850),
    ("18:Q2", 1.2380, 0.8290, 1.4050, 0.3900),
    ("18:Q3", 1.2650, 0.8440, 1.4420, 0.3990),
    ("18:Q4", 1.2740, 0.8700, 1.4570, 0.4070),
    ("19:Q1", 1.2800, 0.8480, 1.4860, 0.4040),
    ("19:Q2", 1.2970, 0.8680, 1.4780, 0.4120),
    ("19:Q3", 1.3150, 0.8810, 1.4980, 0.4250),
    ("19:Q4", 1.3310, 0.9270, 1.5080, 0.4320),
    ("20:Q1", 1.3460, 0.8930, 1.5350, 0.4270),
    ("20:Q2", 1.3430, 0.8170, 1.5370, 0.4180),
    ("20:Q3", 1.3600, 0.8070, 1.5460, 0.4170),
    ("20:Q4", 1.3740, 0.8190, 1.5550, 0.4190),
    ("21:Q1", 1.3820, 0.7700, 1.5840, 0.4130),
    ("21:Q2", 1.4150, 0.7870, 1.5700, 0.4210),
    ("21:Q3", 1.4430, 0.8040, 1.5840, 0.4230),
    ("21:Q4", 1.4580, 0.8560, 1.5760, 0.4380),
    ("22:Q1", 1.4690, 0.8410, 1.5900, 0.4450),
    ("22:Q2", 1.5020, 0.8870, 1.5890, 0.4700),
    ("22:Q3", 1.5240, 0.9250, 1.5740, 0.4910),
    ("22:Q4", 1.5520, 0.9860, 1.5950, 0.5070),
    ("23:Q1", 1.5620, 0.9860, 1.6040, 0.5120),
    ("23:Q2", 1.5820, 1.0310, 1.5690, 0.5270),
    ("23:Q3", 1.5950, 1.0790, 1.5990, 0.5290),
    ("23:Q4", 1.6070, 1.1290, 1.6010, 0.5540),
    ("24:Q1", 1.6160, 1.1150, 1.5950, 0.5430),
    ("24:Q2", 1.6260, 1.1420, 1.5850, 0.5440),
    ("24:Q3", 1.6440, 1.1660, 1.6060, 0.5460),
    ("24:Q4", 1.6550, 1.2110, 1.6150, 0.5540),
    ("25:Q1", 1.6420, 1.1820, 1.6310, 0.5420),
    ("25:Q2", 1.6550, 1.2090, 1.6380, 0.5400),
    ("25:Q3", 1.6550, 1.2330, 1.6530, 0.5500),
    ("25:Q4", 1.6670, 1.2770, 1.6640, 0.5641),
    ("26:Q1", 1.6850, 1.2420, 1.6580, 0.5620),
    ("26:Q2", 1.7130, 1.2630, 1.6510, 0.5680),]

# Bands are stacked in the source graphic's order, bottom to top.
BANDS = [
    ("Auto Loan",    1, "#4a9d6b", "#2f7a4d"),
    ("Credit Card",  2, "#e8734a", "#c9532c"),   # coral: the story band
    ("Other",        4, "#a8b3c4", "#7d8a9e"),
    ("Student Loan", 3, "#e0a83c", "#b8831f"),
]

GROUND = "#FAF7F0"   # Meridian paper
INK    = "#2e2e2e"
MUTED  = "#8a8172"
GRID   = "#ddd5c6"

periods = [r[0] for r in SERIES]
x = list(range(len(SERIES)))


def year_of(p):
    yy = int(p.split(":")[0])
    return 2000 + yy


fig, ax = plt.subplots(figsize=(12, 6.6))
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

# stack the bands
base = [0.0] * len(SERIES)
tops = {}
for name, idx, fill, edge in BANDS:
    vals = [r[idx] for r in SERIES]
    top = [b + v for b, v in zip(base, vals)]
    ax.fill_between(x, base, top, color=fill, zorder=2,
                    linewidth=1.1, edgecolor=edge)
    tops[name] = (base[:], top[:], vals[:])
    base = top

total_last = base[-1]

# end-of-series value label centred in each band
for name, idx, fill, edge in BANDS:
    b, tp, vals = tops[name]
    mid = (b[-1] + tp[-1]) / 2
    ax.text(x[-1] - 1.0, mid, t(vals[-1]), ha="right", va="center",
            fontsize=15, fontweight="bold", color="#1f2937", zorder=6)

# gridlines behind
for gy in [1, 2, 3, 4, 5]:
    ax.axhline(gy, color=GRID, linewidth=1.0, linestyle=(0, (5, 5)), zorder=1)

# titles
ax.set_title("Non-Housing Debt Balance", fontsize=25, fontweight="bold",
             color=INK, loc="left", pad=44, x=-0.055)
ax.text(-0.055, 1.075, "Q2 2026 total: $5.20 trillion",
        transform=ax.transAxes, fontsize=14.5, color=MUTED, ha="left")

# legend as coloured chips on one row, under the subtitle
chip_x = -0.055
for name, idx, fill, edge in BANDS:
    ax.add_patch(plt.Rectangle((chip_x, 1.015), 0.022, 0.036,
                               transform=ax.transAxes, facecolor=fill,
                               edgecolor="none", clip_on=False, zorder=7))
    ax.text(chip_x + 0.030, 1.033, name, transform=ax.transAxes,
            fontsize=13, fontweight="bold", color=INK, va="center", zorder=7)
    chip_x += 0.030 + len(name) * 0.0098 + 0.030

# axes cosmetics
ax.set_xlim(0, len(SERIES) - 1)
ax.set_ylim(0, 5.85)
ax.set_yticks([0, 1, 2, 3, 4, 5])
ax.set_yticklabels(["$0T", "$1T", "$2T", "$3T", "$4T", "$5T"])

tick_years = [2004, 2008, 2012, 2016, 2020, 2024, 2026]
tick_pos, tick_lab = [], []
for ty in tick_years:
    for i, p in enumerate(periods):
        if year_of(p) == ty and p.endswith("Q1"):
            tick_pos.append(i)
            tick_lab.append(str(ty))
            break
ax.set_xticks(tick_pos)
ax.set_xticklabels(tick_lab)

ax.tick_params(axis="both", labelsize=14, colors=MUTED, length=0)
for lbl in ax.get_xticklabels() + ax.get_yticklabels():
    lbl.set_fontweight("bold")
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.spines["bottom"].set_linewidth(1.4)

# footer: source only, no authorship label
fig.text(0.055, 0.028,
         "Source: New York Fed Consumer Credit Panel / Equifax  ·  "
         "Household Debt and Credit Report, Q2 2026 (released Aug 11, 2026)",
         fontsize=11.5, color=MUTED, ha="left")

plt.subplots_adjust(left=0.085, right=0.975, top=0.80, bottom=0.135)
fig.savefig(OUT, dpi=170, facecolor=GROUND)
print("wrote", OUT)
print("Q2 2026 non-housing total: %.3fT" % total_last)
for name, idx, fill, edge in BANDS:
    print("  %-13s %s" % (name, t(SERIES[-1][idx])))
