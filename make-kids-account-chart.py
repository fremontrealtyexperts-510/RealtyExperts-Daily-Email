#!/usr/bin/env python3
"""
make-kids-account-chart.py  [outdir]

Recreates the Market Briefs graphic "The Trump Account Max" for the 09/16/26
edition as a neutral explainer of the 2026 limits. Emits BOTH variants:

  kids-account-091626.png      plain monogram    -> RE email + Agent Hub
  kids-account-091626-hb.png   + wordmark        -> harvrealtor.com / .net / app

=============================================================================
VERIFICATION 09/16/26 (feedback-verify-supplied-chart-values-before-recreating)
=============================================================================

Primary sources: IRS Notice 2025-68; IRS news release IR-2025-117;
26 U.S.C. 530A, 6434 and 4973; Form 4547 instructions.

  $5,000 annual limit for 2026 and 2027 ........ Notice 2025-68, p.18. RIGHT.
  Employer up to $2,500, COUNTS AGAINST the $5,000 ... IR-2025-117. The graphic's
      bracket is RIGHT; the newsletter's "employers can add $2,500 more" is WRONG.
      The $2,500 is per EMPLOYEE, not per child (Notice 2025-68, Q&A I-1).
  Family can fund the full $5,000 ................ IR-2025-117. The graphic's
      $2,500 / $2,500 split is only ONE example, so both splits are drawn here.
  $1,000 Treasury seed, outside the cap .......... 26 USC 530A(c)(2)(B)(iii).
      One time, U.S. citizen children born 2025 through 2028 with an SSN
      (26 USC 6434). The graphic implied every child gets it; labeled here.
  Government and charity gifts are also outside the cap (Form 4547 instr.),
      so $6,000 is not a hard ceiling; footnoted.
  Dec. 31 deadline, no carryback ................. Notice 2025-68, Q&A C-4. RIGHT.
  First contributions July 4, 2026 ............... IR-2025-117.
  6% yearly tax on excess ........................ 26 USC 4973(a) via 530A(h)(5).
  Source line "IRS, U.S. Treasury, Sept. 15, 2026": nothing matching was published
      that day, so the footer credits the actual documents.

NEUTRAL per Harv 09/16/26: the account's legal name appears once, as a fact.

matplotlib only; build with python3.13 on Mac.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_brand import save_pair

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "."
STAMP = "091626"

CREAM = "#fdf6e8"
INK = "#1f2933"
CORAL = "#e2574c"
GREEN = "#4f9d69"
GOLD = "#e8a33d"
GRID = "#d8cdb8"
MUTED = "#8a8172"
DEEP = "#b8433a"
BOX = "#f6e7cf"

CAP = 5000
SEED = 1000
ROWS = [  # (row label, [(segment label, dollars, colour)])
    ("Family pays\nthe full cap", [("Parents, family, friends", 5000, CORAL)]),
    ("With an\nemployer", [("Family", 2500, CORAL), ("Employer", 2500, GREEN)]),
]


def build():
    for _, segs in ROWS:
        assert sum(v for _, v, _ in segs) == CAP

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    ys = [1.0, 0.0]
    h = 0.5
    for y, (row, segs) in zip(ys, ROWS):
        x = 0
        for label, v, col in segs:
            ax.add_patch(Rectangle((x, y - h / 2), v, h, color=col, zorder=2))
            ax.text(x + v / 2, y + 0.06, f"\\${v:,}", ha="center", va="center",
                    fontsize=21, fontweight="bold", color="white", zorder=3)
            ax.text(x + v / 2, y - 0.13, label, ha="center", va="center",
                    fontsize=12.5, color="white", zorder=3)
            x += v
            if x < CAP:
                ax.plot([x, x], [y - h / 2, y + h / 2], color=CREAM, lw=3, zorder=3)
        ax.add_patch(Rectangle((CAP, y - h / 2), SEED, h, color=GOLD, zorder=2))
        ax.text(CAP + SEED / 2, y + 0.06, "\\$1,000", ha="center", va="center",
                fontsize=21, fontweight="bold", color=INK, zorder=3)
        ax.text(CAP + SEED / 2, y - 0.13, "Treasury seed*", ha="center", va="center",
                fontsize=11.5, color=INK, zorder=3)
        ax.text(CAP + SEED + 90, y, "\\$6,000", ha="left", va="center",
                fontsize=19, fontweight="bold", color=INK)
        ax.text(-90, y, row, ha="right", va="center", fontsize=15,
                fontweight="bold", color=INK, linespacing=1.3)

    # cap bracket above the top row
    top = ys[0] + h / 2 + 0.1
    ax.plot([0, 0, CAP, CAP], [top - 0.05, top, top, top - 0.05], color=INK, lw=1.6)
    ax.text(CAP / 2, top + 0.05, "\\$5,000 annual cap: every family and employer dollar counts",
            ha="center", va="bottom", fontsize=13.5, fontweight="bold", color=INK)
    ax.plot([CAP, CAP, CAP + SEED, CAP + SEED], [top - 0.05, top, top, top - 0.05],
            color=GOLD, lw=1.6)
    ax.text(CAP + SEED / 2, top + 0.05, "Outside the cap", ha="center", va="bottom",
            fontsize=13.5, fontweight="bold", color="#b87a1e")

    ax.set_xlim(-1500, 7000)
    ax.set_ylim(-0.45, 1.75)
    ax.axis("off")

    ax.text((CAP + SEED) / 2, 0.5,
            "2026 contributions must be in by Dec. 31, 2026; January money counts for 2027",
            ha="center", va="center", fontsize=13, color=INK,
            bbox=dict(boxstyle="round,pad=0.5", fc=BOX, ec=GRID))

    fig.text(0.045, 0.945, "The 2026 Limits On A Child's New Account",
             fontsize=25, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.045, 0.888,
             "Trump Accounts, the IRS savings accounts for children: two ways to reach the 2026 maximum",
             fontsize=14, color=MUTED, ha="left", va="top")

    fig.text(0.045, 0.125,
             "Employer money (up to \\$2,500 per employee, not per child) counts inside the \\$5,000. *The \\$1,000 seed is one time,\n"
             "for U.S. citizen children born 2025 through 2028. Government and charity gifts also sit outside the cap. "
             "Excess contributions face a 6% yearly tax.",
             fontsize=11, color=DEEP, ha="left", va="bottom", linespacing=1.5)
    fig.text(0.045, 0.035,
             "Source: IRS Notice 2025-68; IRS news release IR-2025-117; 26 U.S.C. sections 530A, 6434 and 4973. "
             "Contributions opened July 4, 2026.",
             fontsize=10.5, color=MUTED, ha="left", va="bottom")

    fig.subplots_adjust(left=0.03, right=0.975, top=0.84, bottom=0.22)
    return fig


if __name__ == "__main__":
    fig = build()
    save_pair(fig, os.path.join(OUTDIR, f"kids-account-{STAMP}.png"),
              logo=os.path.join(os.path.dirname(os.path.abspath(__file__)), "hb-logo-mark.png"))
