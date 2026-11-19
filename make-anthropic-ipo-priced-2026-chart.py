"""
make-anthropic-ipo-priced-2026-chart.py  DATA_DIR  [outdir]

The 11/19/26 daily's Stocks chart. Harv supplied "Anthropic Set To Top SpaceX's
IPO Raise" (initial IPO proceeds at pricing, before overallotment options:
Anthropic priced Nov. 18, 2026 $81.34B, SpaceX Jun. 2026 $75.00B, Saudi Aramco
Dec. 2019 $25.60B, SoftBank Corp. Dec. 2018 $23.50B). Rebuilt as OUR chart from
the primary filings, the same base deal basis as the 11/11/26 chart
(make-anthropic-ipo-rank-2026-chart.py), with a marker for the top of the price
range Anthropic filed on Nov. 10.

Emits BOTH:
  anthropic-ipo-priced-111926.png      plain HB monogram    -> RE email + Agent Hub
  anthropic-ipo-priced-111926-hb.png   monogram + wordmark  -> harvrealtor.com / .net / app

DATA_DIR holds the filings as plain text (HTML stripped):
  anthropic-424b4.txt  Anthropic, PBC 424B4, prospectus dated Nov. 18, 2026, filed
                       Nov. 19 (CIK 2130357, acc. 0001628280-26-074944):
                       980,000,000 shares at $83.00 = $81,340,000,000; underwriters'
                       option for 147,000,000 more; $26.0B concurrent private placement.
  anthropic-s1a2.txt   S-1/A No. 2, Nov. 10, 2026 (acc. 0001628280-26-072484):
                       825,000,000 shares between $70.00 and $78.00.
  spacex-424b4.txt     SpaceX 424B4, June 12, 2026 (CIK 1181412): 555,555,555 at $135.
  alibaba-424b4.txt    Alibaba 424B4, Sept. 22, 2014 (CIK 1577552): 320,106,100 ADSs at $68.
Saudi Aramco is not an SEC filer: Dec. 5, 2019 final price announcement, 3,000,000,000
shares at SAR 32 = SAR 96.0 billion (US$25.6 billion). Hard-coded with that citation.

=============================================================================
VERIFICATION 11/19/26
=============================================================================
* Anthropic $81.34B, SpaceX $75.00B and Aramco $25.6B match the graphic exactly.
* SoftBank Corp. $23.5B does NOT fit the graphic's own "before overallotment" basis:
  Reuters/CNBC (Dec. 10, 2018) "reaches $23.5 billion after extra share sale"; the
  base deal (about 1.6 billion shares at 1,500 yen) was about $21 billion (Bloomberg,
  "SoftBank Sets $21 Billion IPO"). On a base deal basis Alibaba's $21.8B (SEC filing)
  ranks fourth, so the fourth bar is Alibaba and the footer explains SoftBank.
* Anthropic upsized from 825M to 980M shares and priced $5 above the top of its
  $70 to $78 range: the filed top was 825M x $78 = $64.35B.

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
STAMP = "111926"

CREAM = "#fdf6e8"
INK = "#1f2933"
SLATE = "#4f6d8a"
ORANGE = "#ea580c"
GRID = "#e6dcc8"
MUTED = "#8a8172"
AXIS = "#8a7f6a"

AR_USD_B = Decimal("25.6")   # Saudi Aramco final price announcement, Dec. 5, 2019


def txt(name):
    return open(os.path.join(DATA, name), encoding="utf-8", errors="ignore").read()


def num(s):
    return int(s.replace(",", ""))


def b1(x):
    return (Decimal(x) / Decimal(1_000_000_000)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def load():
    a = txt("anthropic-424b4.txt")
    m = re.search(r"Class A Common Stock ([\d,]+) Shares Anthropic, PBC", a)
    shares = num(m.group(1))
    px = Decimal(re.search(r"The initial public offering price per share is \$([\d.]+)", a).group(1))
    assert (shares, px) == (980_000_000, Decimal("83.00")), (shares, px)
    assert "public offering price $ 83.00 $ 81,340,000,000" in a
    assert "Prospectus dated November 18, 2026" in a
    assert "option to purchase up to an additional 147,000,000 shares" in a
    assert "aggregate of $26.0 billion of our Class N common stock" in a

    s1 = txt("anthropic-s1a2.txt")
    m = re.search(r"Class A Common Stock ([\d,]+) Shares Anthropic, PBC", s1)
    r = re.search(r"initial public offering price per share will be between \$([\d.]+) and \$([\d.]+)", s1)
    filed_sh, lo, hi = num(m.group(1)), Decimal(r.group(1)), Decimal(r.group(2))
    assert (filed_sh, lo, hi) == (825_000_000, Decimal("70.00"), Decimal("78.00")), (filed_sh, lo, hi)

    s = txt("spacex-424b4.txt")
    sx = re.search(r"We are offering ([\d,]+) shares of our Class A common stock.*?The initial public offering price is \$([\d.]+) per share", s)
    sx_amt = num(sx.group(1)) * Decimal(sx.group(2))
    assert sx_amt == Decimal("74999999925"), sx_amt

    al = txt("alibaba-424b4.txt")
    al_sh = num(re.search(r"Registration No\. 333-195736 ([\d,]+) American Depositary Shares", al).group(1))
    al_px = Decimal(re.search(r"The initial public offering price of the ADSs is US\$([\d.]+) per ADS", al).group(1))
    assert (al_sh, al_px) == (320_106_100, Decimal("68.00"))

    v = {"ant": b1(shares * px), "ant_filed_top": b1(filed_sh * hi), "spacex": b1(sx_amt),
         "aramco": AR_USD_B, "alibaba": b1(al_sh * al_px)}
    assert v == {"ant": Decimal("81.3"), "ant_filed_top": Decimal("64.4"), "spacex": Decimal("75.0"),
                 "aramco": Decimal("25.6"), "alibaba": Decimal("21.8")}, v
    return v, shares, px, filed_sh, lo, hi


def build():
    v, shares, px, filed_sh, lo, hi = load()
    fig = plt.figure(figsize=(14.0, 7.9), dpi=100)
    fig.patch.set_facecolor(CREAM)
    ax = fig.add_axes([0.255, 0.17, 0.70, 0.60])
    ax.set_facecolor(CREAM)

    rows = [("Anthropic", "priced Nov. 18, 2026", float(v["ant"]), True),
            ("SpaceX", "June 2026", float(v["spacex"]), False),
            ("Saudi Aramco", "December 2019", float(v["aramco"]), False),
            ("Alibaba", "September 2014", float(v["alibaba"]), False)]
    n = len(rows)
    for i, (name, when, val, lead) in enumerate(rows):
        y = n - 1 - i
        ax.barh(y, val, height=0.62, color=ORANGE if lead else SLATE, zorder=3)
        ax.text(val + 1.0, y, f"\\${val:.1f}B", va="center", ha="left", fontsize=18 if lead else 17,
                fontweight="bold", color=ORANGE if lead else INK)
        if lead:
            top = float(v["ant_filed_top"])
            ax.plot([top, top], [y - 0.31, y + 0.31], color=CREAM, lw=2.2, ls=(0, (3, 2)), zorder=4)
            ax.text(top, y - 0.40, f"top of the range filed Nov. 10: \\${top:.1f}B", va="top", ha="center",
                    fontsize=11, color=MUTED, zorder=5)
        ly = 0.17 + 0.60 * (y + 0.6) / (n + 0.2)
        fig.text(0.235, ly + 0.018, name, fontsize=17, fontweight="bold", color=ORANGE if lead else INK,
                 ha="right", va="center")
        fig.text(0.235, ly - 0.022, when, fontsize=11.5, color=MUTED, ha="right", va="center")
    for x in (20, 40, 60, 80):
        ax.axvline(x, color=GRID, lw=1, zorder=1)
        ax.text(x, -0.85, f"\\${x}B", ha="center", va="top", fontsize=10.5, color=MUTED)
    ax.axvline(0, color=AXIS, lw=1.4, zorder=4)
    ax.set_xlim(0, 96)
    ax.set_ylim(-0.7, n - 0.4)
    ax.axis("off")

    fig.text(0.035, 0.955, "Anthropic Prices the Biggest IPO Ever", fontsize=26, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.035, 0.897, "Largest initial public offerings by base deal size, in U.S. dollars", fontsize=13.5,
             color=MUTED, ha="left", va="top")
    fig.text(0.035, 0.862,
             f"{shares / 1e6:,.0f} million shares at \\${px:.0f}, up from {filed_sh / 1e6:,.0f} million at "
             f"\\${lo:.0f} to \\${hi:.0f} in last week's filing",
             fontsize=13.5, color=INK, ha="left", va="top")
    fig.text(0.035, 0.020,
             "Base deal, before the underwriters' option to buy more shares (Anthropic's covers 147 million more). "
             "SoftBank Corp. (Dec. 2018) is often listed\nat \\$23.5B, but that includes its extra shares; its base "
             "deal was about \\$21B. Sources: SEC filings (Anthropic prospectus, Nov. 18, 2026; SpaceX and\nAlibaba "
             "prospectuses); Saudi Aramco final price announcement, Dec. 5, 2019; Reuters and Bloomberg on SoftBank.",
             fontsize=10.0, color=MUTED, ha="left", va="bottom", linespacing=1.4)
    return fig


if __name__ == "__main__":
    fig = build()
    out = os.path.join(OUTDIR, f"anthropic-ipo-priced-{STAMP}.png")
    save_pair(fig, out, facecolor=CREAM)
    plt.close(fig)
    print("wrote", out)
