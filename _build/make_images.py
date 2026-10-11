#!/usr/bin/env python3
"""
Generate the raster brand assets the HTML references:
  assets/img/og-healthspan-standard-2027.png   1200 x 630 social card
  assets/img/apple-touch-icon.png              180 x 180
  assets/img/icon-512.png                      512 x 512 maskable

Drawn with Pillow using a serif face from the system font directory, so it
needs no network and no design tool. Re-run after changing the palette.
"""

import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img")

PAPER_GOLD = (248, 238, 214)
MAROON_DEEP = (78, 18, 12)
MAROON = (107, 26, 18)
CRIMSON = (142, 36, 24)
GOLD = (217, 174, 82)
GOLD_DARK = (184, 134, 43)
GOLD_SOFT = (201, 165, 106)
CREAM = (241, 228, 200)
SAFFRON = (232, 135, 43)
GREEN = (30, 122, 50)

FONT_DIRS = [r"C:\Windows\Fonts", "/usr/share/fonts/truetype", "/Library/Fonts"]
SERIF = ["georgiab.ttf", "georgia.ttf", "timesbd.ttf", "DejaVuSerif-Bold.ttf"]
SANS = ["seguisb.ttf", "segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"]


def find_font(candidates):
    for d in FONT_DIRS:
        for name in candidates:
            p = os.path.join(d, name)
            if os.path.exists(p):
                return p
    return None


SERIF_PATH = find_font(SERIF)
SANS_PATH = find_font(SANS)


def font(path, size):
    try:
        return ImageFont.truetype(path, size) if path else ImageFont.load_default()
    except OSError:
        return ImageFont.load_default()


def centred(draw, y, text, f, fill, width, tracking=0):
    """Draw text centred horizontally, optionally letter-spaced."""
    if tracking:
        widths = [draw.textlength(ch, font=f) + tracking for ch in text]
        total = sum(widths) - tracking
        x = (width - total) / 2
        for ch, w in zip(text, widths):
            draw.text((x, y), ch, font=f, fill=fill)
            x += w
        return total
    w = draw.textlength(text, font=f)
    draw.text(((width - w) / 2, y), text, font=f, fill=fill)
    return w


def guilloche(draw, cx, cy, r_outer, rings=11):
    """The concentric seal used across the identity."""
    draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer],
                 fill=PAPER_GOLD, outline=GOLD_DARK, width=3)
    step = (r_outer - 6) / rings
    for i in range(rings):
        r = r_outer - 6 - i * step
        if r < 3:
            break
        colour = CRIMSON if i % 2 == 0 else GOLD_SOFT
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=colour, width=2 if i % 3 == 0 else 1)
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=CRIMSON)


def make_og():
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), MAROON)
    d = ImageDraw.Draw(img)

    # Vignette toward the edges
    for i in range(H):
        t = abs(i - H / 2) / (H / 2)
        shade = int(10 * t)
        d.line([(0, i), (W, i)], fill=(MAROON[0] - shade, MAROON[1] - shade, MAROON[2] - shade))

    # Double rule frame
    d.rectangle([28, 28, W - 29, H - 29], outline=GOLD_DARK, width=2)
    d.rectangle([40, 40, W - 41, H - 41], outline=CRIMSON, width=1)

    guilloche(d, W // 2, 150, 66)

    f_kicker = font(SANS_PATH, 19)
    f_title = font(SERIF_PATH, 78)
    f_sub = font(SANS_PATH, 25)
    f_meta = font(SANS_PATH, 22)

    centred(d, 240, "A CONSTITUTION FOR LONGEVITY & REGENERATIVE MEDICINE", f_kicker, GOLD, W, tracking=3)
    centred(d, 282, "HEALTHSPAN STANDARD", f_title, PAPER_GOLD, W, tracking=2)
    centred(d, 374, "2027", f_title, GOLD, W, tracking=12)

    # Tricolour rules flanking the place line
    y = 492
    for x0 in (330, 724):
        for k, colour in enumerate((SAFFRON, (255, 255, 255), GREEN)):
            d.rectangle([x0, y + k * 6, x0 + 146, y + k * 6 + 4], fill=colour)
    centred(d, y + 2, "DELHI · INDIA", f_sub, PAPER_GOLD, W, tracking=7)

    centred(d, 552, "10 – 11 APRIL 2027   ·   NEW DELHI   ·   EVIDENCE BEFORE ENTHUSIASM",
            f_meta, CREAM, W, tracking=2)

    img.save(os.path.join(OUT, "og-healthspan-standard-2027.png"), optimize=True)
    print("  · og-healthspan-standard-2027.png  1200x630")


def make_icon(size, name, pad_ratio=0.0):
    img = Image.new("RGB", (size, size), MAROON_DEEP)
    d = ImageDraw.Draw(img)
    cx = cy = size / 2
    r = (size / 2) * (0.78 if pad_ratio else 0.86)
    guilloche(d, cx, cy, r, rings=max(5, size // 46))
    f = font(SERIF_PATH, int(size * 0.3))
    text = "HS"
    w = d.textlength(text, font=f)
    bbox = d.textbbox((0, 0), text, font=f)
    d.text((cx - w / 2, cy - (bbox[3] - bbox[1]) / 2 - bbox[1]), text, font=f, fill=CRIMSON)
    img.save(os.path.join(OUT, name), optimize=True)
    print(f"  · {name}  {size}x{size}")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print(f"Serif: {SERIF_PATH}\nSans:  {SANS_PATH}\n")
    make_og()
    make_icon(180, "apple-touch-icon.png")
    make_icon(512, "icon-512.png", pad_ratio=0.12)
    print("\nDone.")
