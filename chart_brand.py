#!/usr/bin/env python3
"""
chart_brand.py — the corner mark for every recreated chart.

TWO VARIANTS OF EVERY CHART, decided by Harv on 2026-09-06.

  plain    HB monogram only, ghosted. Goes to the REALTY EXPERTS daily email and
           the Agent Hub broadcast. NEVER carries a HarvRealtor wordmark, because
           that surface is the brokerage's, not Harv's.
  branded  HB monogram plus "HarvRealtor.com" in legible muted type. Goes to
           harvrealtor.com, harvrealtor.net and any other non Agent Hub site.

Same data, same figure, two files: `<name>.png` and `<name>-hb.png`.

⚠️ The two MLS images are NOT in scope. `RE-Daily-1` and `RE-Daily-2` come out of
`mls-csv-to-images.py`, stay hosted on raw.githubusercontent.com, and appear only
on the REALTY EXPERTS surfaces. Do not brand them and do not move them to
WordPress. Everything else we draw ourselves goes to WordPress in both variants.

VISIBILITY (Harv, 2026-09-06): "legible but quiet". The monogram keeps its 0.20
alpha ghost. The wordmark does NOT: an unreadable URL earns nothing, so it sits
at 0.85 alpha in the muted warm grey already used for footnotes. Per the 08/26
rule the ink stays dark and alpha does the fading; gold and light silver were
both rejected then and are still rejected.

LOCKUP ORDER is monogram then wordmark, right aligned to the same x the bare
monogram uses, so the branded and plain variants sit on the same baseline. The
wordmark width is MEASURED from the renderer rather than estimated, so the pair
never drifts or collides with the source footnote.
"""
from __future__ import annotations

MUTED = "#8a8172"
WORDMARK = "HarvRealtor.com"


def _load_logo(path):
    try:
        from PIL import Image
        return Image.open(path).convert("RGBA")
    except (FileNotFoundError, OSError, ImportError):
        print(f"WARN: {path} unavailable, chart rendered without the brand mark")
        return None


def _text_width_frac(fig, text, size, weight="normal"):
    """Width of `text` as a fraction of figure width, measured not guessed."""
    t = fig.text(0, 0, text, fontsize=size, fontweight=weight)
    fig.canvas.draw()
    bb = t.get_window_extent(renderer=fig.canvas.get_renderer())
    t.remove()
    return bb.width / (fig.get_size_inches()[0] * fig.dpi)


def add_brand(fig, path="hb-logo-mark.png", height=0.05, x=0.985, y=0.026,
              alpha=0.20, wordmark=None, text_size=11.0,
              text_color=MUTED, text_alpha=0.85):
    """HB monogram bottom right, optionally followed by a wordmark.

    wordmark=None      -> the plain Agent Hub mark (identical to the old add_logo)
    wordmark="Harv..." -> the branded mark for Harv's own sites

    Resample ONCE with PIL to the exact pixel size the figure draws, then blit
    1:1 with interpolation="none". A missing file or PIL is non fatal.
    """
    src = _load_logo(path)
    if src is None:
        return False

    import numpy as np

    fw, fh = fig.get_size_inches()
    px_h = max(1, int(round(height * fh * fig.dpi)))
    px_w = max(1, int(round(src.width * px_h / src.height)))
    src = src.resize((px_w, px_h), __import__("PIL.Image", fromlist=["Image"]).LANCZOS)
    w = px_w / (fw * fig.dpi)

    if wordmark:
        gap = 0.007
        tw = _text_width_frac(fig, wordmark, text_size)
        logo_right = x - tw - gap          # monogram sits left, wordmark right
        fig.text(x, y + height / 2.0, wordmark, ha="right", va="center",
                 fontsize=text_size, color=text_color, alpha=text_alpha,
                 zorder=10)
    else:
        logo_right = x

    ax = fig.add_axes((logo_right - w, y, w, height), zorder=10)
    ax.imshow(np.asarray(src), interpolation="none", alpha=alpha)
    ax.axis("off")
    return True


# Where each variant's mark sits.
#
# PLAIN keeps the 08/26/26 spec exactly: ghosted monogram, bottom right. It is
# faint enough to sit over the source footnote without hurting anything.
#
# BRANDED goes TOP right instead, and that is deliberate. A legible wordmark at
# the bottom right lands straight on top of the source footnote, which runs the
# full width and whose length changes chart to chart (verified 09/06/26: the
# first render had "HarvRealtor.com" overprinting "...city market reports"). The
# top right is reliably empty because every title in this house style is left
# aligned and short, so the lockup cannot collide no matter how long the footnote
# gets. Reads as a masthead rather than a watermark, which is the better job for
# a URL anyway.
PLAIN_POS = dict(x=0.985, y=0.026)
BRANDED_POS = dict(x=0.985, y=0.930)


def save_pair(fig, out, logo="hb-logo-mark.png", facecolor="#fdf6e8",
              plain_pos=None, branded_pos=None, **kw):
    """Write BOTH variants from one figure and return (plain, branded) paths.

    `out` is the plain filename; the branded one gets a `-hb` suffix. The brand
    artists are added, saved, then removed, so the two files differ only in the
    corner mark and nothing else can drift between them.
    """
    import os

    base, ext = os.path.splitext(out)
    branded = f"{base}-hb{ext}"
    before = (list(fig.texts), list(fig.axes))

    def _reset():
        for a in list(fig.axes):
            if a not in before[1]:
                a.remove()
        for t in list(fig.texts):
            if t not in before[0]:
                t.remove()

    add_brand(fig, path=logo, wordmark=None, **{**PLAIN_POS, **(plain_pos or {}), **kw})
    fig.savefig(out, facecolor=facecolor)
    _reset()

    add_brand(fig, path=logo, wordmark=WORDMARK,
              **{**BRANDED_POS, **(branded_pos or {}), **kw})
    fig.savefig(branded, facecolor=facecolor)
    _reset()

    print(f"wrote {out} (plain, Agent Hub) + {branded} (branded, harvrealtor.com)")
    return out, branded
