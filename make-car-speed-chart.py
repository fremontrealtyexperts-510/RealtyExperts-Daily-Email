#!/usr/bin/env python3
"""
make-car-speed-chart.py  [out.png]

Sunday 09/06/26 edition. C.A.R.'s weekly dashboard for the week ending 08/29/26
says the California market is cooling. This chart asks the only question a
Fremont reader actually cares about: does that cooling reach us.

⚠️ BASIS DISCIPLINE (the whole reason this file has a long docstring).
The C.A.R. weekly PDF Harv supplied prints a statewide median days on market of
29. DO NOT put that number next to a city letter. The weekly dashboard is a
snapshot of all MLS activity for one week; the city letters are MONTHLY and are
existing SINGLE FAMILY ONLY. Charting 29 against Fremont's 12 would be a period
mismatch and a scope mismatch stacked on each other.

The number that IS comparable is in C.A.R.'s July 2026 Home Sales and Price
Report (released 08/17/26): statewide median days on market for existing
single family homes was 26, against 28 in July 2025. Same month, same property
type, same publisher as the city letters. That is the 26 plotted here.

SOURCES (all C.A.R., all July 2026, all existing single family)
  statewide   car.org July 2026 Home Sales and Price Report .......... 26 days
  city letters content.car.org/images/Market_Overview/City/Letter/<CITY>.pdf

VERIFIED 09/06/26: every city value read straight off its own PDF, no
arithmetic in between. Fremont 12, Milpitas 12, San Jose 13, Hayward 14,
Newark 16, Union City 16, Oakland 17.

Fremont and Milpitas tie at 12 and Newark and Union City tie at 16; the sort is
stable so the ranking still reads cleanly top to bottom.

BRAND MARK: HB monogram bottom right, no name text (Harv, 08/26/26).
matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "car-speed-090626.png"
LOGO = "hb-logo-mark.png"

# label, median days on market, role: state | fremont | ledger | nearby
ROWS = [
    ("California",  26, "state"),
    ("Oakland",     17, "nearby"),
    ("Newark",      16, "ledger"),
    ("Union City",  16, "ledger"),
    ("Hayward",     14, "ledger"),
    ("San Jose",    13, "nearby"),
    ("Fremont",     12, "fremont"),
    ("Milpitas",    12, "ledger"),
]
assert ROWS == sorted(ROWS, key=lambda r: -r[1]), "chart must read as a ranking"

CREAM = "#fdf6e8"
INK   = "#1f2933"
CORAL = "#e2574c"
DEEP  = "#b8433a"
TAN   = "#d9a05b"
SLATE = "#8a9bb0"
GRID  = "#d8cdb8"
MUTED = "#8a8172"

FILL = {"state": SLATE, "fremont": DEEP, "ledger": CORAL, "nearby": TAN}


def add_logo(fig, path=LOGO, height=0.05, x=0.985, y=0.026, alpha=0.20):
    """HB monogram, bottom right, deliberately near invisible but CRISP."""
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


fig, ax = plt.subplots(figsize=(12.6, 7.2), dpi=170)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

labels = [r[0] for r in ROWS]
values = [r[1] for r in ROWS]
ys = list(range(len(ROWS)))[::-1]
colors = [FILL[r[2]] for r in ROWS]

ax.barh(ys, values, height=0.60, color=colors, zorder=3)

for y, v in zip(ys, values):
    ax.text(v + 0.35, y, f"{v} days", va="center", ha="left", fontsize=20,
            fontweight="bold", color=INK, zorder=5)

ax.set_yticks(ys)
ax.set_yticklabels(labels, fontsize=15.5, fontweight="bold")
ax.set_xlim(0, 33)
ax.set_xticks([0, 5, 10, 15, 20, 25, 30])
ax.grid(axis="x", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=12.5, colors=MUTED)
for lbl in ax.get_yticklabels():
    lbl.set_color(INK)

fig.text(0.046, 0.962, "Every city here sells faster than California does",
         fontsize=24, fontweight="bold", color=INK, va="top")
fig.text(0.046, 0.905,
         "Median days from listing to contract, July 2026, existing single family homes",
         fontsize=13.5, color=MUTED, va="top")
fig.text(0.046, 0.856,
         "Slate bar is the statewide figure. Tan bars are neighboring cities shown for context.",
         fontsize=11.5, color=MUTED, style="italic", va="top")

fig.text(0.008, 0.020,
         "California Association of REALTORS®. Statewide figure from the July 2026 Home Sales and Price Report; "
         "city figures from C.A.R.'s July 2026 city market reports.\nAll eight figures are the same month, the same "
         "property type and the same publisher.",
         fontsize=10.5, color=MUTED, linespacing=1.5)
add_logo(fig)

fig.subplots_adjust(left=0.135, right=0.975, top=0.775, bottom=0.150)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
for lb, v, role in ROWS:
    print(f"  {lb:<12} {v:>3} days   ({role})")
