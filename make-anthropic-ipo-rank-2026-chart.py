"""
make-anthropic-ipo-rank-2026-chart.py  DATA_DIR  [outdir]

The 11/11/26 daily's Stocks chart. Harv supplied "Anthropic Eyes the 2nd-Biggest
IPO Ever" (largest IPOs by amount raised: SpaceX 2026 $75.0B, Anthropic up to
$64.4B pending, Saudi Aramco 2019 $25.6B, Alibaba 2014 $21.8B; "base deal size,
Anthropic at top of $70 to $78 range"). Rebuilt as OUR chart from the primary
filings, with Anthropic drawn as its full price range (low and top), not just
the top.

Emits BOTH:
  anthropic-ipo-rank-111126.png      plain HB monogram    -> RE email + Agent Hub
  anthropic-ipo-rank-111126-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds the filings as plain text (HTML stripped):
  anthropic-s1a2.txt  Anthropic, PBC S-1/A No. 2, filed Nov. 10, 2026 (CIK 2130357,
                      acc. 0001628280-26-072484): "825,000,000 Shares ... between
                      $70.00 and $78.00", Nasdaq "ANT", up to 20% to retail.
  anthropic-fees.txt  the filing fee exhibit: 948,750,000 shares incl. the
                      underwriters' 123,750,000 share option, x $78 = $74.0B.
  spacex-424b4.txt    Space Exploration Technologies Corp 424B4, June 12, 2026
                      (CIK 1181412): 555,555,555 shares at $135.00 = $74,999,999,925.
  alibaba-424b4.txt   Alibaba Group 424B4, Sept. 22, 2014 (CIK 1577552):
                      320,106,100 ADSs at US$68.00.
Saudi Aramco is not an SEC filer: its Dec. 5, 2019 final price announcement
(aramco.com) gives 3,000,000,000 shares at SAR 32, SAR 96.0 billion (US$25.6
billion), US$29.4 billion if the over-allotment is exercised. Hard-coded below
with that citation.

=============================================================================
VERIFICATION 11/11/26
=============================================================================
* Every bar of the supplied graphic matches its primary filing at BASE deal
  size (before the underwriters' extra shares): SpaceX 75.0, Anthropic top of
  range 64.35, Aramco 25.6, Alibaba 21.77.
* Anthropic low end of range: 825M x $70 = $57.75B. Even the low end would rank
  second, behind SpaceX.
* The S-1/A gives no pricing date. "Next week" (Market Briefs) is not in the
  filing and is not on the chart.

matplotlib; build with python3.13 on Mac, run from the workspace (brand mark path).
"""
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
STAMP = "111126"

CREAM = "#fdf6e8"
INK = "#1f2933"
SLATE = "#4f6d8a"
ORANGE = "#ea580c"
ORANGE_LIGHT = "#f6b48a"
GRID = "#e6dcc8"
MUTED = "#8a8172"
AXIS = "#8a7f6a"

AR_SHARES, AR_SAR, AR_USD_B = 3_000_000_000, 32, Decimal("25.6")   # Aramco final price announcement, Dec. 5, 2019


def txt(name):
    return open(os.path.join(DATA, name), encoding="utf-8", errors="ignore").read()


def num(s):
    return int(s.replace(",", ""))


def b(x):
    return (Decimal(x) / Decimal(1_000_000_000)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def load():
    a = txt("anthropic-s1a2.txt")
    m = re.search(r"Class A Common Stock ([\d,]+) Shares Anthropic, PBC", a)
    shares = num(m.group(1))
    r = re.search(r"initial public offering price per share will be between \$([\d.]+) and \$([\d.]+)", a)
    lo, hi = Decimal(r.group(1)), Decimal(r.group(2))
    assert shares == 825_000_000 and (lo, hi) == (Decimal("70.00"), Decimal("78.00")), (shares, lo, hi)
    assert "up to 20% of the shares of Class A common stock offered" in a
    f = txt("anthropic-fees.txt")
    assert "Includes an additional 123,750,000 shares" in f
    assert "$ 74,002,500,000.00" in f                              # 948,750,000 x $78, with the option

    s = txt("spacex-424b4.txt")
    sx = re.search(r"We are offering ([\d,]+) shares of our Class A common stock.*?The initial public offering price is \$([\d.]+) per share", s)
    sx_sh, sx_px = num(sx.group(1)), Decimal(sx.group(2))
    assert sx_sh * sx_px == Decimal("74999999925"), sx_sh * sx_px
    assert "$ 74,999,999,925" in s

    al = txt("alibaba-424b4.txt")
    g = re.search(r"Registration No\. 333-195736 ([\d,]+) American Depositary Shares", al)
    al_sh = num(g.group(1))
    p = re.search(r"The initial public offering price of the ADSs is US\$([\d.]+) per ADS", al)
    al_px = Decimal(p.group(1))
    assert (al_sh, al_px) == (320_106_100, Decimal("68.00"))

    out = {
        "spacex": b(sx_sh * sx_px),
        "ant_lo": b(shares * lo),
        "ant_hi": b(shares * hi),
        "aramco": AR_USD_B,
        "alibaba": b(al_sh * al_px),
    }
    assert out == {"spacex": Decimal("75.0"), "ant_lo": Decimal("57.8"), "ant_hi": Decimal("64.4"),
                   "aramco": Decimal("25.6"), "alibaba": Decimal("21.8")}, out
    return out, shares, lo, hi


def build():
    v, shares, lo, hi = load()
    fig = plt.figure(figsize=(14.0, 7.8), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.255, 0.15, 0.70, 0.62])
    ax.set_facecolor(CREAM)

    rows = [("SpaceX", "June 2026", float(v["spacex"]), None),
            ("Anthropic", "pending, San Francisco", float(v["ant_lo"]), float(v["ant_hi"])),
            ("Saudi Aramco", "December 2019", float(v["aramco"]), None),
            ("Alibaba", "September 2014", float(v["alibaba"]), None)]
    n = len(rows)
    for i, (name, when, val, top) in enumerate(rows):
        y = n - 1 - i
        if top is None:
            ax.barh(y, val, height=0.62, color=SLATE, zorder=3)
            ax.text(val + 1.0, y, f"\\${val:.1f}B", va="center", ha="left", fontsize=17, fontweight="bold", color=INK)
        else:
            ax.barh(y, val, height=0.62, color=ORANGE, zorder=3)
            ax.barh(y, top - val, left=val, height=0.62, color=ORANGE_LIGHT, zorder=3)
            ax.text(top + 1.0, y + 0.10, f"\\${val:.1f}B to \\${top:.1f}B", va="center", ha="left", fontsize=17,
                    fontweight="bold", color=ORANGE)
            ax.text(top + 1.0, y - 0.22, f"at \\${lo:.0f} to \\${hi:.0f} a share", va="center", ha="left", fontsize=11.5,
                    color=MUTED)
        ly = 0.15 + 0.62 * (y + 0.6) / (n + 0.2)
        fig.text(0.235, ly + 0.018, name, fontsize=17, fontweight="bold", color=ORANGE if top else INK, ha="right",
                 va="center")
        fig.text(0.235, ly - 0.022, when, fontsize=11.5, color=MUTED, ha="right", va="center")
    for x in (20, 40, 60, 80):
        ax.axvline(x, color=GRID, lw=1, zorder=1)
        ax.text(x, -0.75, f"\\${x}B", ha="center", va="top", fontsize=10.5, color=MUTED)
    ax.axvline(0, color=AXIS, lw=1.4, zorder=4)
    ax.set_xlim(0, 96)
    ax.set_ylim(-0.6, n - 0.4)
    ax.axis("off")

    fig.text(0.035, 0.955, "Anthropic Eyes the Second Biggest IPO Ever", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.897, "Largest initial public offerings by base deal size, in U.S. dollars", fontsize=13.5,
             color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.862, f"Anthropic is selling {shares / 1e6:,.0f} million shares; even the low end of its range would rank second",
             fontsize=13.5, color=INK, ha="left", va="top")
    fig.text(0.035, 0.022, "Base deal, before the underwriters' option to buy more shares. Sources: SEC filings (Anthropic S-1/A, "
             "Nov. 10, 2026;\nSpaceX and Alibaba prospectuses); Saudi Aramco final price announcement, Dec. 5, 2019.",
             fontsize=10.2, color=MUTED, ha="left", va="bottom", linespacing=1.4)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"anthropic-ipo-rank-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
