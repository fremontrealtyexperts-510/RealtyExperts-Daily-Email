#!/usr/bin/env python3
"""
make-broadcom-ai-chart.py  [out.png]

Recreation of the "Broadcom's AI Doubling Act" graphic Harv supplied for the
09/03/26 daily email.

✅ VERIFICATION 09/03/26. All four values trace to Broadcom's Q3 FY2026 earnings
call (September 2, 2026) and to its FY2025 results:

    FY2025   $20B    ACTUAL. AI revenue grew 65% YoY to $20B in fiscal 2025,
                     against $64B of TOTAL consolidated company revenue.
    FY2026   $58B    company guidance, raised from $56B on this call, +186% YoY
                     (20 x 2.86 = 57.2, so $58B and the growth rate agree).
    FY2027   $115B   company target
    FY2028   $230B   company target

⚠️ THE ONE THING THE NEWSLETTER GOT WRONG, AND THE GRAPHIC GOT RIGHT. Market
Briefs wrote "$115 billion in AI chip sales expected in 2027" and then "$230
billion in REVENUE is expected in 2028", which reads as though the 2028 figure
is total company revenue. It is not. Both are AI revenue, on the same basis. The
supplied graphic's axis label, "AI chip revenue by fiscal year", is correct and
the newsletter's sentence is the sloppy one. Checked because a compound headline
that switches units halfway is exactly the 08/31 failure; this time the graphic
survived it.

⚠️ WHAT THE SUPPLIED CHART UNDERSTATES: that three of its four bars are a
COMPANY FORECAST, and one is a result. It does say so in a small legend, but the
forecast bars are drawn in the same confident gradient as the actual, so the
roadmap reads like history. Here the single actual bar is solid and the three
forecast bars are hatched, which is a difference you cannot miss at a glance.

The scale point worth making, and it is verifiable: the FY2028 AI-only target of
$230B is about 3.6x Broadcom's ENTIRE company revenue in FY2025 ($64B). That is
the real content of the word "doubling" here.

Context for the copy, not the chart: Q3 FY2026 revenue was $29.6B, up 86% YoY,
with AI semiconductor revenue of $16.7B, up 221% YoY and 56% of the total.
Management said demand already exceeds the $115B FY2027 target and that supply,
not orders, is the binding constraint. The stock still fell 0.66% on the day.

BRAND MARK: silver HB monogram, bottom right, no name text (Harv, 08/26/26).
matplotlib only; build with python3.13 on Mac.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "broadcom-ai-090326.png"
LOGO = "hb-logo-mark.png"

# fiscal year, AI revenue $B, is_actual
DATA = [
    ("FY2025",  20, True),
    ("FY2026",  58, False),
    ("FY2027", 115, False),
    ("FY2028", 230, False),
]
FY25_TOTAL_COMPANY_REV = 64   # $B, all segments, for the scale annotation

CREAM = "#fdf6e8"
INK   = "#1f2933"
CORAL = "#e2574c"
DEEP  = "#b8433a"
SLATE = "#4a5568"
SAND  = "#c9b896"
GRID  = "#d8cdb8"
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

labels = [d[0] for d in DATA]
vals = [d[1] for d in DATA]
actual = [d[2] for d in DATA]
xs = list(range(len(DATA)))

fig, ax = plt.subplots(figsize=(12.6, 7.0), dpi=170)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)

for x, v, is_act in zip(xs, vals, actual):
    if is_act:
        ax.bar(x, v, width=0.6, color=DEEP, zorder=3)
    else:
        # Hatched + hollow so a forecast can never be mistaken for a result.
        ax.bar(x, v, width=0.6, facecolor=CREAM, edgecolor=CORAL, lw=2.0,
               hatch="////", zorder=3)
    ax.text(x, v + 6, f"\\${v}B", ha="center", va="bottom", fontsize=19,
            fontweight="bold", color=INK, zorder=5)

ax.text(0, -20, "actual", ha="center", va="top", fontsize=12.5,
        fontweight="bold", color=DEEP, zorder=5)
ax.text(2.0, -20, "company forecast", ha="center", va="top", fontsize=12.5,
        fontweight="bold", color=CORAL, zorder=5)

# Scale line: FY2025 revenue for the WHOLE company.
ax.axhline(FY25_TOTAL_COMPANY_REV, color=SLATE, lw=1.6, ls=(0, (6, 4)), zorder=4)
# Label sits far LEFT, over the two short bars. Right-aligned at x=3.42 it ran
# straight through the FY2027 and FY2028 bars; caught by eyeballing the render.
ax.text(-0.42, FY25_TOTAL_COMPANY_REV + 5,
        f"Whole company, FY2025: \\${FY25_TOTAL_COMPANY_REV}B",
        ha="left", va="bottom", fontsize=12, fontweight="bold", color=SLATE, zorder=6)

ax.annotate("The FY2028 AI target alone is\nabout 3.6x the whole company\nin FY2025",
            xy=(3, 228), xytext=(1.28, 196),
            fontsize=13, fontweight="bold", color=INK, ha="left", va="center",
            arrowprops=dict(arrowstyle="-|>", color=SLATE, lw=1.5,
                            connectionstyle="arc3,rad=-0.18"), zorder=7)

ax.set_xticks(xs)
ax.set_xticklabels(labels, fontsize=15, fontweight="bold")
ax.set_ylim(0, 268)
ax.set_yticks([0, 50, 100, 150, 200, 250])
ax.set_yticklabels(["0", "\\$50B", "\\$100B", "\\$150B", "\\$200B", "\\$250B"])
ax.grid(axis="y", color=GRID, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="both", length=0, labelsize=12.5, colors=SLATE)
for lbl in ax.get_xticklabels():
    lbl.set_color(INK)

fig.text(0.046, 0.958, "Broadcom's AI roadmap, and what is actually banked",
         fontsize=25, fontweight="bold", color=INK, va="top")
fig.text(0.046, 0.897,
         "AI revenue by fiscal year. One bar is a result. Three are company targets.",
         fontsize=14, color=SLATE, va="top")

fig.text(0.008, 0.038,
         "Source: Broadcom Q3 FY2026 earnings call, September 2, 2026, and FY2025 results.",
         fontsize=10.5, color=SLATE)
fig.text(0.008, 0.013,
         "FY2026 guidance was raised to \\$58B on this call. Management said demand already "
         "exceeds the FY2027 target and that supply, not orders, is the constraint.",
         fontsize=10.5, color=SLATE)
add_logo(fig)

fig.subplots_adjust(left=0.082, right=0.988, top=0.800, bottom=0.155)
fig.savefig(OUT, facecolor=CREAM)
print(f"wrote {OUT}")
for lb, v, a in DATA:
    print(f"  {lb}  \\${v:>4}B   {'ACTUAL' if a else 'forecast'}")
print(f"  FY2028 target / FY2025 whole-company revenue = {vals[-1]/FY25_TOTAL_COMPANY_REV:.2f}x")
