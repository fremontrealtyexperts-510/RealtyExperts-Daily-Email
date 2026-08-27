#!/usr/bin/env python3
"""
make-corepce-chart.py  [out.png]

Recreation of the "Inflation Is Stuck Above The Fed's Target" graphic Harv
supplied for the 08/27/26 daily email, rebuilt in house style (cream ground).

✅ VERIFICATION DONE 08/27/26, and it turned into a VINTAGE question rather than
an error hunt. Two internally consistent series exist and they are not the same:

  month   BEA current index   YoY      BEA's ORIGINAL monthly print   graphic
  Jan 26     128.455        +3.105%             n/a (release 404)       3.1
  Feb 26     128.961        +3.049%             n/a (release 404)       3.1
  Mar 26     129.343        +3.254%                    3.2              3.2
  Apr 26     129.681        +3.330%                    3.3              3.3
  May 26     130.147        +3.464%                    3.4              3.4
  Jun 26     130.338        +3.344%                    3.3              3.3
  Jul 26     130.658        +3.344%                    3.3              3.3

The supplied graphic tracks BEA's ORIGINAL PRINTS exactly (every month Mar
through Jul matches the press release prose). That is a legitimate series, but
it MIXES SEVEN VINTAGES: March and May have since been revised up, so a line
built that way partly plots revision timing rather than inflation.

★ WE PLOT THE CURRENT VINTAGE, ONE SERIES, recomputed from BEA's published core
PCE price index (NIPA table 2.8.4, line 25, "PCE excluding food and energy").
Anyone who checks this chart against today's BEA index reproduces it exactly.
Consequence to disclose, and it IS disclosed in the footer and the copy: March
reads 3.3 here against the 3.2 first reported, and May reads 3.5 against 3.4.

⚠️ February is a genuine coin flip, not a correction. It computes to 3.0493%,
and the published index carries only three decimals, so the true value sits
within a thousandth of the 3.05 rounding boundary. Plotted as 3.0 by standard
rounding. Do not "fix" it back to 3.1 on a later run without re-deriving it.

Sanity check that the index is the right vintage: April, June and July all
reproduce BEA's own stated prints (3.3, 3.3, 3.3) to the decimal. Only the two
revised months diverge, which is exactly the expected signature.

July 2026 core PCE of 3.3% is the number in the news and it is UNREVISED, so the
headline reading the audience will have seen elsewhere matches this chart.

BRAND MARK (Harv, 08/26/26): HB monogram bottom right, very low opacity, no name
text.

matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "corepce-082726.png"
LOGO = "hb-logo-mark.png"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]
CORE   = [3.1, 3.0, 3.3, 3.3, 3.5, 3.3, 3.3]   # current vintage, see docstring
TARGET = 2.0

CREAM = "#fdf6e8"
INK   = "#1f2933"
CORAL = "#e2574c"
STEEL = "#7a93b5"
GRID  = "#d8cdb8"
MUTED = "#8a8172"


def add_logo(fig, path=LOGO, height=0.05, x=0.985, y=0.026, alpha=0.20):
    """HB monogram, bottom right, near invisible but CRISP."""
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

xs = range(len(MONTHS))

ax.plot(xs, [TARGET] * len(MONTHS), color=STEEL, lw=3.0, ls=(0, (7, 5)), zorder=3)
ax.plot(xs, CORE, color=CORAL, lw=3.6, marker="o", markersize=10,
        markerfacecolor=CORAL, markeredgecolor=CREAM, markeredgewidth=2.2, zorder=4)

# end labels
ax.annotate(f"{CORE[-1]:.1f}%", xy=(len(MONTHS) - 1, CORE[-1]), xytext=(14, 0),
            textcoords="offset points", va="center", ha="left", fontsize=20,
            fontweight="bold", color="#ffffff", zorder=6,
            bbox=dict(boxstyle="round,pad=0.42", facecolor=CORAL, edgecolor="none"))
ax.annotate(f"{TARGET:.1f}%", xy=(len(MONTHS) - 1, TARGET), xytext=(14, 0),
            textcoords="offset points", va="center", ha="left", fontsize=20,
            fontweight="bold", color="#ffffff", zorder=6,
            bbox=dict(boxstyle="round,pad=0.42", facecolor=STEEL, edgecolor="none"))

# the gap is the whole point
ax.annotate("", xy=(1.0, CORE[1]), xytext=(1.0, TARGET),
            arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1.6), zorder=5)
ax.text(1.13, (CORE[1] + TARGET) / 2, "stuck about a point\nabove the target",
        fontsize=13, color=MUTED, va="center", ha="left", style="italic", zorder=5)

ax.set_xticks(list(xs))
ax.set_xticklabels(MONTHS, fontsize=15, fontweight="bold")
ax.set_xlim(-0.35, len(MONTHS) - 0.35)
ax.set_ylim(1.55, 3.95)
ax.set_yticks([2.0, 2.5, 3.0, 3.5])
ax.set_yticklabels(["2.0%", "2.5%", "3.0%", "3.5%"])

ax.grid(axis="y", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=12.5, colors=MUTED)
for lbl in ax.get_xticklabels():
    lbl.set_color(INK)

fig.text(0.046, 0.958, "Inflation is stuck above the Fed's target",
         fontsize=26.5, fontweight="bold", color=INK, va="top")
fig.text(0.046, 0.897,
         "Core PCE price index, change from a year earlier, 2026. Dashed line is the Fed's 2% target.",
         fontsize=13.5, color=MUTED, va="top")

fig.text(0.008, 0.022,
         "Source: Bureau of Economic Analysis, core PCE price index, current vintage. Revisions have lifted March "
         "and May a tenth above\ntheir originally reported 3.2% and 3.4%. July's 3.3% is unrevised.",
         fontsize=10.5, color=MUTED, linespacing=1.5)
add_logo(fig)

fig.subplots_adjust(left=0.085, right=0.905, top=0.795, bottom=0.155)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
for m, v in zip(MONTHS, CORE):
    print(f"  {m}  {v:.1f}%")
