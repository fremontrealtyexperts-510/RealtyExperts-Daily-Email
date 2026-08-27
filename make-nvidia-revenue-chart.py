#!/usr/bin/env python3
"""
make-nvidia-revenue-chart.py  [out.png]

Recreation of the "Nvidia's Revenue Keeps Doubling" graphic Harv supplied for the
08/27/26 daily email, rebuilt in house style (cream ground, no authorship text).

✅ VERIFICATION DONE 08/27/26. Every quarter was read off NVIDIA's own results
releases, not the graphic. One bar was WRONG and is corrected here:

  quarter (ends)        graphic     NVIDIA filing      note
  Jul 2025  Q2 FY26      $46.7B     $46,743M           ok
  Oct 2025  Q3 FY26      $56.8B     $57,006M           ✗ CORRECTED to $57.0B
  Jan 2026  Q4 FY26      $68.1B     $68,127M           ok
  Apr 2026  Q1 FY27      $81.6B     $81,615M           ok
  Jul 2026  Q2 FY27      $96.2B     $96,221M           ok
  Oct 2026  Q3 FY27     $108.0B     $108.0B +/- 2%     ok, GUIDANCE not a result

The $56.8B was off by about $206M. NVIDIA's Q3 FY26 release headlines "record
revenue of $57.0 billion", and the same 57,006 appears in the income statement
and again in the Q4 FY26 comparison table, so 57.0 is not in doubt.

★ THE TITLE CLAIM WAS ALSO CHECKED, not just the bars. "Keeps doubling" is a
statement about the year over year rate, and it holds: 46,743 -> 96,221 is
+105.9%, and NVIDIA itself states 106%. Data center revenue was $89.0B, +117%.

The Oct 2026 bar is COMPANY GUIDANCE ("$108.0 billion, plus or minus 2%",
excluding any Data Center compute revenue from China), so it is drawn hatched
and open, labeled "guidance", and never presented as a reported result. Quarters
are labeled by END MONTH because NVIDIA's fiscal year runs a year ahead of the
calendar and "Q2 FY27" would mislead a general reader.

BRAND MARK (Harv, 08/26/26): HB monogram bottom right, very low opacity, no name
text. Gold rejected as too bright, light silver as too low contrast.

matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "nvidia-revenue-082726.png"
LOGO = "hb-logo-mark.png"

# label, revenue $B, is_guidance   (newest first, drawn top down)
ROWS = [
    ("Oct '26", 108.0, True),
    ("Jul '26",  96.2, False),
    ("Apr '26",  81.6, False),
    ("Jan '26",  68.1, False),
    ("Oct '25",  57.0, False),
    ("Jul '25",  46.7, False),
]

CREAM  = "#fdf6e8"
INK    = "#1f2933"
ORANGE = "#e08a1e"
DEEP   = "#c2740f"
SAND   = "#e8c98a"
GRID   = "#d8cdb8"
MUTED  = "#8a8172"


def add_logo(fig, path=LOGO, height=0.05, x=0.985, y=0.026, alpha=0.20):
    """HB monogram, bottom right, near invisible but CRISP. Resample ONCE with
    PIL to the exact pixel size the figure draws, then blit 1:1 with
    interpolation="none". Missing file or PIL is non-fatal."""
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
ys = list(range(len(ROWS)))[::-1]

for y, (lb, v, guid) in zip(ys, ROWS):
    if guid:
        ax.barh(y, v, height=0.6, facecolor=SAND, edgecolor=DEEP, hatch="///",
                linewidth=1.6, linestyle=(0, (4, 2)), zorder=3)
    else:
        ax.barh(y, v, height=0.6, color=ORANGE, zorder=3)

for y, (lb, v, guid) in zip(ys, ROWS):
    ax.text(v + 1.8, y, f"${v:.1f}B", va="center", ha="left", fontsize=21,
            fontweight="bold", color=INK, zorder=5)
    if guid:
        # inside the bar: outside it collides with the wide "$108.0B" value label
        ax.text(2.6, y, "company guidance", va="center", ha="left", fontsize=13,
                style="italic", fontweight="bold", color=DEEP, zorder=5)

ax.set_yticks(ys)
ax.set_yticklabels(labels, fontsize=15.5, fontweight="bold")
ax.set_xlim(0, 132)
ax.set_xticks([0, 25, 50, 75, 100])
ax.set_xticklabels(["0", "$25B", "$50B", "$75B", "$100B"])

ax.grid(axis="x", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=12.5, colors=MUTED)
for lbl in ax.get_yticklabels():
    lbl.set_color(INK)

fig.text(0.046, 0.958, "Nvidia's revenue keeps doubling",
         fontsize=26.5, fontweight="bold", color=INK, va="top")
fig.text(0.046, 0.897,
         "Quarterly revenue, quarters labeled by the month they end. Latest quarter is up 106% from a year earlier.",
         fontsize=13.5, color=MUTED, va="top")

fig.text(0.008, 0.022,
         "Source: NVIDIA quarterly results releases. The Oct 2026 bar is company guidance of $108.0B plus or minus 2%, "
         "not a reported result.",
         fontsize=10.5, color=MUTED)
add_logo(fig)

fig.subplots_adjust(left=0.105, right=0.975, top=0.795, bottom=0.125)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
for lb, v, guid in ROWS:
    print(f"  {lb:<9} ${v:>6.1f}B{'   (guidance)' if guid else ''}")
