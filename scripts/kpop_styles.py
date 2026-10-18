# -*- coding: utf-8 -*-
"""K-pop girl-group PV subtitle style mockups (static frames).

Styles derived from current 4th-gen girl-group typography trends:
  S1 Y2K chrome + sticker collage       (chrome bubble letters, candy colours)
  S2 Minimal kinetic typography         (clean grotesk, staggered words)
  S3 Futurism / glitch                  (RGB split, scanlines, glitch type)
  S4 Mix & match editorial              (serif italic x condensed sans, tape)
  S5 Graphic emphasis                   (huge display type, sticker outline)
  S6 Hand-marker journal                (marker lettering, highlighter, doodles)
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
FR_DIR = os.path.join(ROOT, "输出", "字幕设计")
OUT = os.path.join(ROOT, "输出", "字幕风格参考")
FONT_DIR = os.path.join(BASE, "fonts")
WIN_FONTS = r"C:\Windows\Fonts"
W, H = 2560, 1080

F_ANTON = os.path.join(FONT_DIR, "Anton-Regular.ttf")
F_ARCHIVO = os.path.join(FONT_DIR, "ArchivoBlack-Regular.ttf")
F_BEBAS = os.path.join(FONT_DIR, "BebasNeue-Regular.ttf")
F_BUNGEE = os.path.join(FONT_DIR, "Bungee-Regular.ttf")
F_MONOTON = os.path.join(FONT_DIR, "Monoton-Regular.ttf")
F_MARKER = os.path.join(FONT_DIR, "PermanentMarker-Regular.ttf")
F_GLITCH = os.path.join(FONT_DIR, "RubikGlitch-Regular.ttf")
F_PIXEL = os.path.join(FONT_DIR, "Silkscreen-Regular.ttf")
F_GEORGIA_I = os.path.join(WIN_FONTS, "georgiai.ttf")
F_GEORGIA = os.path.join(WIN_FONTS, "georgia.ttf")
F_MSYH = os.path.join(WIN_FONTS, "msyh.ttc")

WHITE = (250, 248, 244)
INK = (17, 15, 20)
PINK = (255, 92, 179)
AQUA = (72, 226, 230)
LAV = (196, 164, 255)
LILAC = (232, 220, 255)
CREAM = (248, 238, 215)
CYAN = (0, 240, 255)
MAGENTA = (255, 0, 170)
GOLD = (255, 201, 84)


def font(path, size):
    return ImageFont.truetype(path, int(size))


def text_img(text, fontpath, size, color, tracking=0, stroke=0, stroke_color=INK,
             alpha=255):
    f = font(fontpath, size)
    widths = []
    for ch in text:
        bb = f.getbbox(ch)
        widths.append(bb[2] - bb[0] if bb[2] > bb[0] else int(size * 0.3))
    tw = int(sum(widths) + tracking * max(0, len(text) - 1)) + int(size * 0.5)
    th = int(size * 2.0)
    img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = int(size * 0.15)
    for ch, w in zip(text, widths):
        d.text((x, int(size * 0.3)), ch, font=f, fill=color + (alpha,),
               stroke_width=stroke, stroke_fill=stroke_color + (alpha,))
        x += w + tracking
    return img


def rot(img, angle):
    return img.rotate(angle, expand=True, resample=Image.BICUBIC)


def paste(base, layer, x, y, alpha=1.0, anchor="center"):
    if alpha < 1.0:
        a = layer.getchannel("A").point(lambda v: int(v * alpha))
        layer = layer.copy()
        layer.putalpha(a)
    w, h = layer.size
    pos = (int(x - w / 2), int(y - h / 2)) if anchor == "center" else (int(x), int(y))
    base.alpha_composite(layer, pos)


def gradient_fill(layer, stops):
    """stops: list of (pos 0..1, (r,g,b))"""
    w, h = layer.size
    ys = np.linspace(0, 1, h)
    cols = np.zeros((h, 3), np.float32)
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        m = (ys >= p0) & (ys <= p1)
        t = (ys[m] - p0) / max(1e-6, p1 - p0)
        for k in range(3):
            cols[m, k] = c0[k] + (c1[k] - c0[k]) * t
    grad = np.repeat(cols[:, None, :], w, axis=1)
    grad_img = Image.fromarray(np.clip(grad, 0, 255).astype(np.uint8)).convert("RGB")
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.paste(grad_img, (0, 0), layer.getchannel("A"))
    # gloss band
    gloss = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(gloss)
    gd.polygon([(0, int(h * 0.20)), (w, int(h * 0.05)), (w, int(h * 0.30)),
                (0, int(h * 0.42))], fill=(255, 255, 255, 110))
    gloss = gloss.filter(ImageFilter.GaussianBlur(3))
    gmask = gloss.getchannel("A").point(lambda v: v)
    band = Image.new("RGBA", layer.size, (255, 255, 255, 0))
    band.putalpha(gmask.point(lambda v: int(v * 0.55)))
    out.alpha_composite(Image.composite(band, Image.new("RGBA", layer.size, (0, 0, 0, 0)),
                                        layer.getchannel("A")))
    return out


def outline_solid(layer, color, width):
    """Sticker-like outline: dilate alpha."""
    a = layer.getchannel("A")
    grown = a
    for _ in range(width):
        grown = grown.filter(ImageFilter.MaxFilter(3))
    out = Image.new("RGBA", layer.size, color + (0,))
    out.putalpha(grown.point(lambda v: min(255, v * 2)))
    return out


def sparkle(size, color=WHITE, alpha=230):
    s = int(size)
    img = Image.new("RGBA", (s * 2, s * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = s
    d.polygon([(cx, cy - s), (cx + s * 0.16, cy - s * 0.16), (cx + s, cy),
               (cx + s * 0.16, cy + s * 0.16), (cx, cy + s),
               (cx - s * 0.16, cy + s * 0.16), (cx - s, cy),
               (cx - s * 0.16, cy - s * 0.16)], fill=color + (alpha,))
    return img


def heart(size, color, alpha=220):
    s = size
    img = Image.new("RGBA", (s * 2, s * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, s, s], fill=color + (alpha,))
    d.ellipse([s, 0, s * 2, s], fill=color + (alpha,))
    d.polygon([(0, s * 0.55), (s * 2, s * 0.55), (s, s * 1.9)], fill=color + (alpha,))
    return img


def star(size, color, alpha=220):
    s = size
    img = Image.new("RGBA", (s * 2, s * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = []
    for i in range(10):
        r = s if i % 2 == 0 else s * 0.45
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((s + r * math.cos(a), s + r * math.sin(a)))
    d.polygon(pts, fill=color + (alpha,))
    return img


def tape(w, h, angle, alpha=120, color=(246, 243, 232)):
    img = Image.new("RGBA", (int(w), int(h)), color + (alpha,))
    d = ImageDraw.Draw(img)
    for _ in range(6):
        x = random.randint(0, int(w))
        d.line([(x, 0), (x, h)], fill=color + (alpha + 40,), width=1)
    return rot(img, angle)


def rounded_badge(w, h, color, radius=26, alpha=240, border=None):
    img = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=color + (alpha,))
    if border:
        d.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius,
                            outline=border + (255,), width=6)
    return img


def halftone(size, spacing=10, radius=2.4, alpha=70, color=INK):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for y in range(0, size[1], spacing):
        for x in range(0, size[0], spacing):
            d.ellipse([x, y, x + radius, y + radius], fill=color + (alpha,))
    return img


def scanlines(size, alpha=18, spacing=4, color=(0, 0, 0)):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for y in range(0, size[1], spacing):
        d.line([(0, y), (size[0], y)], fill=color + (alpha,))
    return img


def add_noise(img, amount=5, seed=1):
    rnd = np.random.default_rng(seed)
    a = np.asarray(img).astype(np.int16)
    n = rnd.normal(0, amount, (a.shape[0], a.shape[1], 1)).astype(np.int16)
    a[:, :, :3] = np.clip(a[:, :, :3] + n, 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def load_frame(sec):
    return Image.open(os.path.join(FR_DIR, "_frame_%.1f.jpg" % sec)).convert("RGBA")


def glow(layer, radius, strength=1.0, color=None):
    a = layer.getchannel("A").filter(ImageFilter.GaussianBlur(radius))
    col = color or WHITE
    g = Image.new("RGBA", layer.size, col + (0,))
    g.putalpha(a.point(lambda v: int(min(255, v * strength))))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.alpha_composite(g)
    out.alpha_composite(layer)
    return out


def chroma(layer, dx=6, dy=0, ca=(255, 40, 120), cb=(40, 200, 255)):
    a = layer.getchannel("A")
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    la = Image.new("RGBA", layer.size, ca + (0,))
    la.putalpha(a.point(lambda v: int(v * 0.45)))
    lb = Image.new("RGBA", layer.size, cb + (0,))
    lb.putalpha(a.point(lambda v: int(v * 0.45)))
    out.alpha_composite(la, (dx, dy))
    out.alpha_composite(lb, (-dx, -dy))
    out.alpha_composite(layer)
    return out


def glitch_slices(layer, seed=3, n=8, max_shift=36):
    rnd = random.Random(seed)
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    w, h = layer.size
    y = 0
    while y < h:
        hh = rnd.randint(10, max(14, int(h * 0.08)))
        strip = layer.crop((0, y, w, min(h, y + hh)))
        if rnd.random() < 0.6:
            dx = rnd.randint(-max_shift, max_shift)
            strip = strip.transform(strip.size, Image.AFFINE, (1, 0, -dx, 0, 1, 0),
                                    resample=Image.BILINEAR)
        out.alpha_composite(strip, (0, y))
        y += hh
    return out


# ===================================================================== S1
def s1_y2k():
    """Y2K chrome + sticker collage: SHE?"""
    base = load_frame(13.2)
    # holographic backdrop bloc
    holo = Image.new("RGBA", (1700, 520), (0, 0, 0, 0))
    hd = ImageDraw.Draw(holo)
    for i in range(500):
        x = i * 4
        col = (int(255 - 60 * math.sin(x / 180)), int(170 + 60 * math.sin(x / 240)),
               int(240 + 15 * math.cos(x / 300)))
        hd.line([(x, 0), (x, 520)], fill=col + (34,))
    holo = holo.filter(ImageFilter.GaussianBlur(28))
    paste(base, holo, 1900, 780, alpha=0.7)

    t = text_img("SHE?", F_BUNGEE, 430, WHITE, tracking=-14, stroke=4, stroke_color=(30, 18, 40))
    t = rot(t, -5)
    t = gradient_fill(t, [(0.0, (255, 255, 255)), (0.28, (214, 220, 236)),
                          (0.46, (126, 134, 158)), (0.62, (246, 249, 255)),
                          (0.80, (172, 178, 198)), (1.0, (238, 242, 250))])
    # outline + shadow
    ol = outline_solid(t, (28, 18, 38), 4)
    paste(base, ol.filter(ImageFilter.GaussianBlur(8)), 1930, 700, alpha=0.8)
    paste(base, ol, 1925, 690)
    paste(base, t, 1920, 685)
    # sparkles
    for (x, y, s) in ((2140, 380, 42), (1760, 520, 30), (2410, 760, 34), (2060, 940, 24)):
        paste(base, sparkle(s, WHITE, 235), x, y)
    for (x, y, s) in ((1820, 830, 22), (2300, 470, 18)):
        paste(base, star(s, AQUA, 230), x, y)

    # sticker badge
    badge = rounded_badge(560, 120, PINK, radius=60, border=WHITE)
    d = ImageDraw.Draw(badge)
    cap = text_img("who is she?", F_ARCHIVO, 54, WHITE, tracking=4)
    badge.alpha_composite(cap, (int(280 - cap.size[0] / 2), int(60 - cap.size[1] / 2)))
    badge = rot(badge, 6)
    paste(base, badge, 900, 210)
    # small sticker
    badge2 = rounded_badge(210, 78, AQUA, radius=22, border=WHITE)
    d2 = ImageDraw.Draw(badge2)
    tt = text_img("JP", F_PIXEL, 40, (10, 26, 30), tracking=2)
    badge2.alpha_composite(tt, (int(105 - tt.size[0] / 2), int(39 - tt.size[1] / 2)))
    paste(base, rot(badge2, -10), 420, 880)
    return add_noise(base, 4, 31)


# ===================================================================== S2
def s2_minimal():
    """Minimal kinetic typography: feel the fire"""
    base = load_frame(8.6)
    ink = WHITE
    small = text_img("FEEL  THE", F_ANTON, 92, ink, tracking=26)
    paste(base, small, 520, 300)
    t = text_img("FIRE", F_ANTON, 330, ink, tracking=14)
    # ghosts to imply motion
    for i, dx in enumerate((-46, -22)):
        g = t.copy()
        g = Image.merge("RGBA", (g.getchannel("R"), g.getchannel("G"), g.getchannel("B"),
                                 g.getchannel("A").point(lambda v, a=0.10: int(v * a))))
        paste(base, g, 560 + dx, 700)
    paste(base, t, 560, 700)
    d = ImageDraw.Draw(base)
    d.line([(250, 900), (1000, 900)], fill=WHITE + (150,), width=3)
    cap = text_img("YOU CAN COME AND SEE ME", F_PIXEL, 34, WHITE, tracking=6, alpha=210)
    paste(base, cap, 520, 948)
    num = text_img("03 / 07", F_PIXEL, 40, LAV, tracking=4, alpha=230)
    paste(base, num, 2280, 210)
    b = text_img("baby", F_ANTON, 120, WHITE, tracking=10)
    paste(base, b, 2210, 900, alpha=0.95)
    d.line([(2130, 830), (2420, 830)], fill=LAV + (140,), width=2)
    return add_noise(base, 3, 32)


# ===================================================================== S3
def s3_glitch():
    """Futurism / glitch: WHO IS SHE?"""
    base = load_frame(13.2)
    # HUD corners
    d = ImageDraw.Draw(base)
    for (x, y, sx, sy) in ((120, 120, 1, 1), (W - 120, 120, -1, 1),
                           (120, H - 120, 1, -1), (W - 120, H - 120, -1, -1)):
        d.line([(x, y), (x + 160 * sx, y)], fill=CYAN + (150,), width=2)
        d.line([(x, y), (x, y + 90 * sy)], fill=CYAN + (150,), width=2)

    t = text_img("WHO IS", F_ANTON, 190, WHITE, tracking=10)
    t = chroma(t, 7, 0, (255, 0, 160), (0, 230, 255))
    t = glitch_slices(t, seed=11, n=4, max_shift=16)
    paste(base, t, 1900, 420)
    t2 = text_img("SHE?", F_GLITCH, 300, WHITE, tracking=6)
    t2 = chroma(t2, 9, 0, (255, 0, 160), (0, 230, 255))
    t2 = glitch_slices(t2, seed=5, n=6, max_shift=26)
    paste(base, t2, 1900, 700)
    # pixel noise blocks
    rnd = random.Random(4)
    for _ in range(28):
        x = rnd.randint(1450, 2500)
        y = rnd.randint(300, 980)
        w = rnd.randint(8, 90)
        h = rnd.randint(2, 7)
        col = rnd.choice([CYAN, MAGENTA, WHITE, (0, 0, 0)])
        ImageDraw.Draw(base).rectangle([x, y, x + w, y + h], fill=col + (rnd.randint(60, 200),))
    scan = scanlines(base.size, alpha=14, spacing=3)
    base.alpha_composite(scan)
    cap = text_img("SYS/LRC_ 0127", F_PIXEL, 30, CYAN, tracking=4, alpha=200)
    paste(base, cap, 2500, 200)
    cap2 = text_img("no signal", F_PIXEL, 28, MAGENTA, tracking=3, alpha=180)
    paste(base, cap2, 380, 950)
    return add_noise(base, 5, 33)


# ===================================================================== S4
def s4_mixmatch():
    """Mix & match editorial: MAKING / everybody / GO"""
    base = load_frame(5.4)
    # tape strips
    tape1 = tape(700, 96, -8, alpha=120)
    paste(base, tape1, 470, 190)
    tape2 = tape(520, 84, 12, alpha=110)
    paste(base, tape2, 900, 430)

    def serif_word(text, size, color, x, y, angle, italic=True):
        f = F_GEORGIA_I if italic else F_GEORGIA
        t = text_img(text, f, size, color, tracking=2)
        paste(base, rot(t, angle), x, y)

    def sans_word(text, fontpath, size, color, x, y, angle, track=0):
        t = text_img(text, fontpath, size, color, tracking=track)
        paste(base, rot(t, angle), x, y)

    # "everybody" big serif italic in cream
    ew = text_img("everybody", F_GEORGIA_I, 240, CREAM, tracking=0, stroke=3,
                  stroke_color=(40, 28, 50))
    paste(base, rot(ew, -7), 720, 380)
    # MAKING condensed
    sans_word("MAKING", F_BEBAS, 170, WHITE, 430, 180, -4, track=8)
    # GO block
    go = text_img("GO!", F_ARCHIVO, 200, WHITE, tracking=0)
    block = rounded_badge(go.size[0] + 80, go.size[1] + 40, (58, 30, 86), radius=14)
    block.alpha_composite(go, (40, 20))
    paste(base, rot(block, 5), 480, 700)
    # small caption
    cap = text_img("get up / get down", F_PIXEL, 30, CREAM, tracking=5, alpha=200)
    paste(base, cap, 1180, 880)
    # doodles
    paste(base, star(34, PINK, 230), 1050, 200)
    paste(base, heart(26, LAV, 220), 1260, 300)
    paste(base, sparkle(22, CREAM, 200), 870, 560)
    d = ImageDraw.Draw(base)
    d.line([(340, 430), (150, 470), (210, 520)], fill=CREAM + (200,), width=4)
    d.line([(150, 470), (210, 510)], fill=CREAM + (200,), width=4)
    # halftone corner
    ht = halftone((520, 300), spacing=12, radius=2.6, alpha=50, color=(30, 20, 40))
    paste(base, ht, 220, 850, alpha=0.5)
    return add_noise(base, 4, 34)


# ===================================================================== S5
def s5_graphic():
    """Graphic emphasis: STEP (sticker display type)"""
    base = load_frame(1.6)
    # diagonal stripes block
    stripes = Image.new("RGBA", (1100, 700), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripes)
    for i in range(-600, 1400, 70):
        sd.line([(i, 0), (i + 600, 700)], fill=PINK + (60,), width=26)
    stripes = rot(stripes, -12)
    paste(base, stripes, 520, 700, alpha=0.55)

    t = text_img("STEP", F_ANTON, 430, WHITE, tracking=6, stroke=0)
    # sticker outline
    ol = outline_solid(t, WHITE, 7)
    shadow = outline_solid(t, (28, 18, 40), 9)
    paste(base, shadow.filter(ImageFilter.GaussianBlur(10)), 560, 690, alpha=0.75)
    paste(base, ol, 545, 675)
    # pink offset copy
    pk = outline_solid(t, PINK, 4)
    paste(base, pk, 520, 700, alpha=0.9)
    paste(base, t, 530, 660)

    # badge
    badge = rounded_badge(640, 110, AQUA, radius=55, border=WHITE)
    cap = text_img("ONTO THE STAGE", F_ARCHIVO, 46, (8, 30, 34), tracking=4)
    badge.alpha_composite(cap, (int(320 - cap.size[0] / 2), int(55 - cap.size[1] / 2)))
    paste(base, rot(badge, -3), 560, 330)
    # halftone shadow under letters
    ht = halftone((700, 200), spacing=10, radius=2.2, alpha=90, color=(30, 12, 30))
    paste(base, rot(ht, -6), 600, 880, alpha=0.5)
    # small stars
    paste(base, star(26, WHITE, 220), 940, 260)
    paste(base, sparkle(20, AQUA, 220), 1030, 760)
    return add_noise(base, 4, 35)


# ===================================================================== S6
def s6_marker():
    """Hand-marker journal: fire / baby"""
    base = load_frame(8.6)
    # highlighter swipe
    swipe = Image.new("RGBA", (900, 210), (0, 0, 0, 0))
    sd = ImageDraw.Draw(swipe)
    sd.rounded_rectangle([0, 20, 900, 190], radius=40, fill=PINK + (110,))
    swipe = swipe.filter(ImageFilter.GaussianBlur(2))
    paste(base, rot(swipe, -4), 600, 740)

    t = text_img("fire", F_MARKER, 320, INK, tracking=2)
    paste(base, rot(t, -4), 600, 730)
    t2 = text_img("baby", F_MARKER, 150, CREAM, tracking=2, stroke=3, stroke_color=INK)
    paste(base, rot(t2, 6), 1030, 930)
    # doodles
    paste(base, rot(heart(30, PINK, 240), -12), 1870, 790)
    paste(base, star(30, GOLD, 240), 1670, 860)
    paste(base, rot(star(24, PINK, 230), 15), 340, 240)
    d = ImageDraw.Draw(base)
    # arrow doodle toward dancer
    d.line([(1350, 780), (1560, 720), (1500, 700)], fill=CREAM + (220,), width=5)
    d.line([(1560, 720), (1500, 745)], fill=CREAM + (220,), width=5)
    # handwritten note on cream sticker
    note = rounded_badge(560, 110, CREAM, radius=10)
    nt = text_img("come and see me", F_MARKER, 46, INK, tracking=1)
    note.alpha_composite(nt, (int(280 - nt.size[0] / 2), int(55 - nt.size[1] / 2)))
    paste(base, rot(note, 3), 500, 240)
    # scribble underline
    d.line([(400, 950), (520, 930), (640, 950), (760, 930)], fill=PINK + (230,), width=5)
    return add_noise(base, 6, 36)


# ================================================================== sheet
def contact_sheet(paths, labels, subs, out_path, cols=3):
    cw, ch, bar = 853, 360, 54
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cw * cols, (ch + bar) * rows), (10, 9, 10))
    d = ImageDraw.Draw(sheet)
    f = font(F_MSYH, 24)
    f2 = font(F_MSYH, 17)
    for i, (p, lab, sub) in enumerate(zip(paths, labels, subs)):
        im = Image.open(p).convert("RGB").resize((cw, ch), Image.LANCZOS)
        x = (i % cols) * cw
        y = (i // cols) * (ch + bar)
        sheet.paste(im, (x, y + bar))
        d.text((x + 14, y + 5), lab, font=f, fill=(242, 238, 232))
        d.text((x + 14, y + 31), sub, font=f2, fill=(170, 164, 176))
    sheet.save(out_path, quality=92)


def main():
    os.makedirs(OUT, exist_ok=True)
    random.seed(7)
    jobs = [
        ("S1_Y2K铬字贴纸.jpg", "S1 · Y2K 铬字 + 贴纸", "参考：K-pop Y2K Seoul（chrome bubble / sticker）", s1_y2k),
        ("S2_极简动态字.jpg", "S2 · 极简动态排版", "参考：aespa / NewJeans kinetic typography", s2_minimal),
        ("S3_故障未来字.jpg", "S3 · 故障未来感", "参考：4th-gen Futurism / glitch（aespa 系）", s3_glitch),
        ("S4_混排杂志.jpg", "S4 · 混排杂志感", "参考：Mix & Match（serif × condensed × tape）", s4_mixmatch),
        ("S5_大字号贴纸.jpg", "S5 · 大字号图形强调", "参考：Graphic emphasis（Blackpink / XG 系海报字）", s5_graphic),
        ("S6_手写荧光笔.jpg", "S6 · 手写 / 荧光笔", "参考：日记手写歌词（NewJeans 系青春感）", s6_marker),
    ]
    paths, labels, subs = [], [], []
    for name, lab, sub, fn in jobs:
        img = fn()
        p = os.path.join(OUT, name)
        img.convert("RGB").save(p, quality=93)
        paths.append(p)
        labels.append(lab)
        subs.append(sub)
        print("rendered", name)
    contact_sheet(paths, labels, subs, os.path.join(OUT, "女团PV字幕_风格参考总览.jpg"))
    print("done")


if __name__ == "__main__":
    main()
