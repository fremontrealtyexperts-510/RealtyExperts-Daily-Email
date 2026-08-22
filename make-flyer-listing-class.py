#!/usr/bin/env python3
"""
make-flyer-listing-class.py  [out.png]

REALTY EXPERTS training flyer for the Agent Hub announcement posted 08/21/26:
Chuck Edell AND Melrose Forde host the C.A.R. Listing Agreement class, Monday
August 24 and Tuesday August 25, 2026, 10:00 AM to Noon, at the office
(41051 Mission Blvd, Fremont). The Tuesday office meeting is cancelled in favor
of the class. Harv's brief: "bring paper and a pen or pencil, come ready to take
notes", otherwise creative.

Built with Pillow (not matplotlib): cinematic navy ground with a soft coral glow,
the FULL official REALTY EXPERTS logo (gold RE mark + wordmark + "Our Experience
is the Difference") on a white badge, Avenir Next for display type and New York
italic for the accent line, two "ticket" date cards, a coral callout band for the
cancelled meeting, and a two column HOSTED BY block. Portrait 1200 x 1500 so it
reads on a phone inside the hub and in the broadcast email.

⚠️ The logo must sit on a WHITE badge. It is a transparent PNG whose wordmark is
gold with BLACK rules above and below; drop it straight onto the navy ground and
those black elements vanish. The white badge is what keeps the brand lockup intact.

House style: no dashes anywhere in the copy ("10:00 AM to Noon", "Monday,
August 24 and Tuesday, August 25"). REALTY EXPERTS always with the (R).
"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1] if len(sys.argv) > 1 else "re-listing-agreement-class-082426.png"
LOGO = "REALTY-EXPERTS-Official-Transparent-logo.png"   # official lockup, content bbox (45,21,871,410)

W, H = 1200, 1500
NAVY_DK = (11, 22, 48)
NAVY    = (27, 42, 75)
CORAL   = (231, 110, 80)
GOLD    = (212, 162, 76)
CREAM   = (253, 246, 232)
SLATE   = (98, 119, 167)
WHITE   = (255, 255, 255)
INK     = (18, 38, 63)

AV = "/System/Library/Fonts/Avenir Next.ttc"
def av(size, face):  # face: 0 Bold, 2 Demi Bold, 5 Medium, 7 Regular, 8 Heavy
    return ImageFont.truetype(AV, size, index=face)
NY_IT = ImageFont.truetype("/System/Library/Fonts/NewYorkItalic.ttf", 40)

# ---------- ground: vertical navy gradient + soft coral glow ----------
img = Image.new("RGB", (W, H), NAVY_DK)
px = img.load()
for y in range(H):
    t = y / (H - 1)
    r = int(NAVY_DK[0] + (NAVY[0] - NAVY_DK[0]) * t)
    g = int(NAVY_DK[1] + (NAVY[1] - NAVY_DK[1]) * t)
    b = int(NAVY_DK[2] + (NAVY[2] - NAVY_DK[2]) * t)
    for x in range(W):
        px[x, y] = (r, g, b)

glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse((720, -260, 1420, 440), fill=CORAL + (110,))
gd.ellipse((-380, 1180, 420, 1900), fill=SLATE + (70,))
glow = glow.filter(ImageFilter.GaussianBlur(140))
img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
d = ImageDraw.Draw(img)

# faint diagonal hairlines for texture
tex = Image.new("RGBA", (W, H), (0, 0, 0, 0))
td = ImageDraw.Draw(tex)
for k in range(-H, W + H, 90):
    td.line([(k, 0), (k + H, H)], fill=WHITE + (9,), width=1)
img = Image.alpha_composite(img.convert("RGBA"), tex).convert("RGB")
d = ImageDraw.Draw(img)

def tracked(xy, text, font, fill, tracking=0.0, anchor_center=False):
    """Draw text with letter spacing. Returns total width."""
    x, y = xy
    widths = [d.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    if anchor_center:
        x = x - total / 2
    for c, w in zip(text, widths):
        d.text((x, y), c, font=font, fill=fill)
        x += w + tracking
    return total

def centered(y, text, font, fill):
    w = d.textlength(text, font=font)
    d.text(((W - w) / 2, y), text, font=font, fill=fill)
    return w

# ---------- header: RE badge + kicker ----------
logo = Image.open(LOGO).convert("RGBA").crop((45, 21, 871, 410))   # trim transparent margin
logo.thumbnail((360, 170), Image.LANCZOS)
badge_w, badge_h = logo.width + 48, logo.height + 40
d.rounded_rectangle((90, 62, 90 + badge_w, 62 + badge_h), radius=20, fill=WHITE)
img.paste(logo, (90 + (badge_w - logo.width) // 2, 62 + (badge_h - logo.height) // 2), logo)
d = ImageDraw.Draw(img)
tracked((92, 62 + badge_h + 22), "AGENT TRAINING SESSION", av(22, 2), GOLD, tracking=5)

# ---------- headline ----------
d.text((88, 342), "The C.A.R.", font=av(88, 8), fill=WHITE)
d.text((88, 436), "Listing Agreement", font=av(88, 8), fill=WHITE)
d.text((92, 552), "A working session with Chuck and Melrose", font=NY_IT, fill=CREAM)
d.rounded_rectangle((92, 616, 92 + 140, 616 + 6), radius=3, fill=CORAL)

# ---------- date tickets ----------
def ticket(x, y, dow, day, month):
    tw, th = 470, 262
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x + 6, y + 14, x + tw + 6, y + th + 14), radius=22, fill=(0, 0, 0, 110))
    return (x, y, tw, th, dow, day, month, shadow)

tickets = [ticket(90, 662, "MONDAY", "24", "AUGUST 2026"),
           ticket(640, 662, "TUESDAY", "25", "AUGUST 2026")]
for (x, y, tw, th, dow, day, month, shadow) in tickets:
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x, y, x + tw, y + th), radius=22, fill=CREAM)
    d.rounded_rectangle((x, y, x + tw, y + 16), radius=8, fill=CORAL)   # top band
    d.rectangle((x, y + 8, x + tw, y + 16), fill=CORAL)
    # punch notches (ticket look)
    d.ellipse((x - 14, y + th // 2 - 14, x + 14, y + th // 2 + 14), fill=NAVY_DK)
    d.ellipse((x + tw - 14, y + th // 2 - 14, x + tw + 14, y + th // 2 + 14), fill=NAVY_DK)
    f_dow, f_day, f_mo = av(26, 2), av(150, 8), av(26, 5)
    d.text((x + tw / 2 - d.textlength(dow, font=f_dow) / 2, y + 34), dow, font=f_dow, fill=SLATE)
    d.text((x + tw / 2 - d.textlength(day, font=f_day) / 2, y + 52), day, font=f_day, fill=INK)
    d.text((x + tw / 2 - d.textlength(month, font=f_mo) / 2, y + 214), month, font=f_mo, fill=SLATE)

# ---------- time ----------
# clock glyph
cx, cy, cr = 330, 986, 22
d.ellipse((cx - cr, cy - cr, cx + cr, cy + cr), outline=CORAL, width=4)
d.line([(cx, cy), (cx, cy - 12)], fill=CORAL, width=4)
d.line([(cx, cy), (cx + 10, cy + 4)], fill=CORAL, width=4)
d.text((372, 952), "10:00 AM to Noon", font=av(54, 8), fill=WHITE)
d.text((376, 1018), "both days", font=av(26, 5), fill=CREAM)

# ---------- location ----------
# pin glyph
pxx, pyy = 330, 1100
d.ellipse((pxx - 16, pyy - 30, pxx + 16, pyy + 2), outline=CORAL, width=4)
d.polygon([(pxx - 13, pyy - 6), (pxx + 13, pyy - 6), (pxx, pyy + 22)], fill=CORAL)
d.ellipse((pxx - 6, pyy - 20, pxx + 6, pyy - 8), fill=NAVY_DK)
d.text((372, 1068), "REALTY EXPERTS® Office", font=av(32, 2), fill=WHITE)
d.text((372, 1110), "41051 Mission Blvd, Fremont", font=av(28, 5), fill=CREAM)

# ---------- coral callout band ----------
d.rectangle((0, 1176, W, 1284), fill=CORAL)
centered(1194, "NO OFFICE MEETING TUESDAY, AUGUST 25", av(34, 8), WHITE)
centered(1238, "Come to class instead.", av(26, 5), WHITE)

# ---------- bring + instructor + footer ----------
d.rounded_rectangle((90, 1320, 90 + 14, 1320 + 14), radius=3, fill=CORAL)
d.text((122, 1310), "Bring paper and a pen or pencil. Come ready to take notes.", font=av(26, 5), fill=CREAM)

tracked((92, 1358), "HOSTED BY", av(19, 2), CORAL, tracking=4)
d.text((90, 1386), "Chuck Edell", font=av(32, 0), fill=WHITE)
d.text((90, 1426), "General Manager / REALTOR®", font=av(22, 5), fill=SLATE)
d.text((640, 1386), "Melrose Forde", font=av(32, 0), fill=WHITE)
d.text((640, 1426), "REALTY EXPERTS®", font=av(22, 5), fill=SLATE)

d.line([(90, 1462), (W - 90, 1462)], fill=(255, 255, 255, 40), width=1)
tracked((92, 1470), "TEAMREALTYEXPERTS.COM", av(19, 2), GOLD, tracking=3)
dre = "DRE #00414413"
d.text((W - 90 - d.textlength(dre, font=av(19, 5)), 1470), dre, font=av(19, 5), fill=SLATE)

img.save(OUT, "PNG", optimize=True)
print("wrote", OUT, img.size)
