#!/usr/bin/env python3
"""
make-canada-autos-chart.py  [out.png]

REALTY EXPERTS recreation of the "Toyota & Honda Build 76.5% Of Canada's Cars"
graphic Harv supplied for the 08/25/26 daily email.

VERIFICATION. Unusually, every figure on the supplied graphic held up.

* Total 2025 Canadian vehicle production: 1,226,099, per Global Automakers of
  Canada, which is the graphic's own cited source.
* Toyota 535,000. Toyota Motor Manufacturing Canada states it assembled more than
  535,000 vehicles in Canada in 2025 and expects its 12 millionth Canadian
  vehicle this year.
* Honda 403,000. Corroborated independently by Honda's Alliston output of roughly
  198,000 Civic and 202,000 CR-V in 2025, which lands at about 400,000.
* Ford + GM + Stellantis 288,099. This one is a RESIDUAL, total minus Toyota minus
  Honda, and it is not published as a standalone figure. It is kept because GAC
  states separately that each of Toyota and Honda individually out-produced Ford,
  GM and Stellantis COMBINED, which is only true if the combined figure is below
  403,000. The residual is labeled as a residual on the chart.
* 76.5%. (535,000 + 403,000) / 1,226,099 = 76.5%. Exact.

The Canadian context worth knowing: production fell about 5.4% year over year in
2025, steeper than the U.S. or Mexico, after U.S. tariffs pushed Stellantis to
move Jeep Compass work out of Brampton and Honda to shift some CR-V output south.

CREDIT LINE (new standing instruction, Harv, 08/25/26): our recreations now carry
"Created by Harv Balu" because the charts were being reshared without
attribution. This REVERSES the 06/29 rule that the footer carry only the data
source. See feedback-custom-chart-recreate-host-wordpress-show-first.md.

matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "canada-autos-082526.png"

TOTAL = 1226099
TOYOTA = 535000
HONDA = 403000
DETROIT3 = TOTAL - TOYOTA - HONDA          # 288,099, a residual

LABELS = ["Toyota", "Honda", "Ford + GM +\nStellantis"]
VALUES = [TOYOTA, HONDA, DETROIT3]
SHARE = (TOYOTA + HONDA) / TOTAL * 100

assert DETROIT3 == 288099
assert round(SHARE, 1) == 76.5, "headline share must reproduce GAC's 76.5%"
assert TOYOTA > DETROIT3 and HONDA > DETROIT3, "GAC: each alone beats the three combined"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
DEEP = "#b8433a"
SLATE = "#4a5568"
SAND = "#c9b896"
GRID = "#d8cdb8"
MUTED = "#8a8172"

fig, ax = plt.subplots(figsize=(12.6, 7.0), dpi=170)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

ys = [2, 1, 0]
colors = [CORAL, DEEP, SAND]
ax.barh(ys, VALUES, height=0.52, color=colors, zorder=3)

for y, v in zip(ys, VALUES):
    ax.text(v + 9000, y, f"{v:,}", va="center", ha="left", fontsize=17,
            fontweight="bold", color=INK, zorder=5)

ax.text(DETROIT3 + 9000, -0.47, "residual: total minus Toyota minus Honda",
        va="center", ha="left", fontsize=10.8, color=MUTED, style="italic")

# Callout parked in the empty band between the Honda and Detroit bars, right
# aligned so the eye reads it as a caption for the bar underneath it.
ax.text(692000, 0.52,
        "Each of Toyota and Honda alone\nout-builds all three of these combined",
        fontsize=13.2, color=DEEP, fontweight="bold", ha="right", va="center",
        linespacing=1.7)

ax.set_yticks(ys)
ax.set_yticklabels(LABELS, fontsize=15, fontweight="bold")
ax.set_xlim(0, 700000)
ax.set_xticks([0, 100000, 200000, 300000, 400000, 500000])
ax.set_xticklabels(["0", "100k", "200k", "300k", "400k", "500k"])
ax.set_ylim(-0.85, 2.75)

ax.grid(axis="x", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=13, colors=SLATE)
for lbl in ax.get_yticklabels():
    lbl.set_color(INK)

fig.text(0.046, 0.958, "Toyota and Honda build 76.5% of Canada's cars",
         fontsize=26.5, fontweight="bold", color=INK, va="top")
fig.text(0.046, 0.897,
         "Vehicles assembled in Canada in 2025, out of 1,226,099 built in total",
         fontsize=14, color=SLATE, va="top")

fig.text(0.008, 0.022,
         "Sources: Global Automakers of Canada, 2025 Canadian vehicle production; "
         "Toyota Motor Manufacturing Canada.",
         fontsize=11, color=SLATE)
# Faint attribution watermark. Deliberately low contrast: present for credit,
# never competing with the data (Harv, 08/25/26).
fig.text(0.992, 0.022, "Created by Harv Balu",
         fontsize=9.5, color=MUTED, alpha=0.5, ha="right")

fig.subplots_adjust(left=0.175, right=0.988, top=0.805, bottom=0.115)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
print(f"  Toyota   {TOYOTA:>9,}")
print(f"  Honda    {HONDA:>9,}")
print(f"  Detroit3 {DETROIT3:>9,}  (residual)")
print(f"  total    {TOTAL:>9,}   share {SHARE:.1f}%")
