# -*- coding: utf-8 -*-
"""Artistic / explosive static subtitle frame concepts for the MMD clip.

Five proposals, each composed on a graded 2560x1080 frame with PIL + numpy
post effects (glitch slices, chroma split, 3D extrusion, halftone, collage...).
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
FR_DIR = os.path.join(ROOT, "输出", "字幕设计")
OUT = FR_DIR
FONTS = r"C:\Windows\Fonts"
W, H = 2560, 1080

WHITE = (244, 241, 234)
EMBER = (255, 59, 30)
PINK = (255, 111, 216)
LAV = (201, 167, 255)
VIOLET = (122, 60, 255)
CYAN = (34, 230, 255)
GOLD = (255, 201, 84)
BLACK = (10, 9, 8)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), int(size))


def text_img(text, fontname, size, color, tracking=0, stroke=0, stroke_color=BLACK,
             alpha=255, italic=False):
    f = font(fontname, size)
    # measure
    widths = []
    for ch in text:
        bb = f.getbbox(ch)
        widths.append(bb[2] - bb[0] if bb[2] > bb[0] else int(size * 0.3))
    tw = int(sum(widths) + tracking * max(0, len(text) - 1)) + int(size * 0.3)
    th = int(size * 1.7)
    img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = int(size * 0.1)
    for ch, w in zip(text, widths):
        d.text((x, int(size * 0.22)), ch, font=f, fill=color + (alpha,),
               stroke_width=stroke, stroke_fill=stroke_color + (alpha,))
        x += w + tracking
    return img


def rot(img, angle):
    return img.rotate(angle, expand=True, resample=Image.BICUBIC)


def paste(base, layer, x, y, anchor="center", alpha=1.0):
    if alpha < 1.0:
        a = layer.getchannel("A").point(lambda v: int(v * alpha))
        layer = layer.copy()
        layer.putalpha(a)
    w, h = layer.size
    if anchor == "center":
        pos = (int(x - w / 2), int(y - h / 2))
    elif anchor == "left":
        pos = (int(x), int(y - h / 2))
    elif anchor == "topleft":
        pos = (int(x), int(y))
    else:
        pos = (int(x), int(y))
    base.alpha_composite(layer, pos)


def glow(layer, radius, strength=1.0, color=None):
    """Add coloured outer glow behind/around a text layer (returns RGBA)."""
    a = layer.getchannel("A").filter(ImageFilter.GaussianBlur(radius))
    col = color or (255, 255, 255)
    g = Image.new("RGBA", layer.size, col + (0,))
    g.putalpha(a.point(lambda v: int(min(255, v * strength))))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.alpha_composite(g)
    out.alpha_composite(layer)
    return out


def chroma(layer, dx=8, dy=0):
    r, g, b, a = layer.split()
    r = Image.new("L", layer.size, 0)
    b = r.copy()
    r.paste(layer.getchannel("R"), (dx, dy))
    b.paste(layer.getchannel("B"), (-dx, -dy))
    out = Image.merge("RGBA", (r, g, b, a))
    return out


def glitch_slices(layer, seed=3, n=7, max_shift=40):
    rnd = random.Random(seed)
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    w, h = layer.size
    y = 0
    while y < h:
        hh = rnd.randint(8, max(12, int(h * 0.09)))
        strip = layer.crop((0, y, w, min(h, y + hh)))
        if rnd.random() < 0.55:
            dx = rnd.randint(-max_shift, max_shift)
            strip = strip.transform(strip.size, Image.AFFINE, (1, 0, -dx, 0, 1, 0),
                                    resample=Image.BILINEAR)
        out.alpha_composite(strip, (0, y))
        y += hh
    return out


def scanlines(size, alpha=16, spacing=4, color=(0, 0, 0)):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for y in range(0, size[1], spacing):
        d.line([(0, y), (size[0], y)], fill=color + (alpha,))
    return img


def halftone(size, spacing=9, radius=2.2, alpha=90, color=(0, 0, 0)):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for y in range(0, size[1], spacing):
        for x in range(0, size[0], spacing):
            d.ellipse([x, y, x + radius, y + radius], fill=color + (alpha,))
    return img


def add_noise(img, amount=6, seed=1):
    rnd = np.random.default_rng(seed)
    a = np.asarray(img).astype(np.int16)
    n = rnd.normal(0, amount, (a.shape[0], a.shape[1], 1)).astype(np.int16)
    a[:, :, :3] = np.clip(a[:, :, :3] + n, 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def hard_light_screen(base, layer, alpha=1.0):
    lb = layer.filter(ImageFilter.GaussianBlur(0.4))
    base.alpha_composite(lb if alpha >= 1 else lb.point(lambda v: int(v * alpha)))


def stripe(base, xy, w, h, color, angle=0.0, alpha=90):
    img = Image.new("RGBA", (int(w), int(h)), color + (alpha,))
    img = rot(img, angle)
    paste(base, img, xy[0], xy[1])
    return base


def circle_arc(base, center, r, color, width=3, alpha=120, start=0, end=360):
    """Draw an ellipse outline on a transparent layer."""
    w = r[0] * 2 + width * 2
    h = r[1] * 2 + width * 2
    img = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([width, width, w - width, h - width], outline=color + (alpha,), width=width)
    img = rot(img, start)
    paste(base, img, center[0], center[1])
    return base


# ============================ concepts ============================
def load_frame(seconds):
    p = os.path.join(FR_DIR, "_frame_%.1f.jpg" % seconds)
    return Image.open(p).convert("RGBA")


def design_a():
    """A · 故障切片 SHE?"""
    base = load_frame(13.2)

    # subtle magenta bar behind the word
    bar = Image.new("RGBA", (1500, 320), (255, 20, 90, 46))
    bar = bar.filter(ImageFilter.GaussianBlur(34))
    paste(base, bar, 1980, 810, alpha=0.9)

    t = text_img("SHE?", "impact.ttf", 470, WHITE, tracking=-6, stroke=0)
    t = t.rotate(-7, expand=True, resample=Image.BICUBIC)

    # chromatic copies behind (solid colours)
    red_c = text_img("SHE?", "impact.ttf", 470, (255, 40, 30), tracking=-6)
    red_c = red_c.rotate(-7, expand=True, resample=Image.BICUBIC)
    red_c = Image.merge("RGBA", (red_c.getchannel("R"), red_c.getchannel("G"),
                                 red_c.getchannel("B"),
                                 red_c.getchannel("A").point(lambda v: int(v * 0.55))))
    paste(base, red_c, 1962, 792)
    cyan_c = text_img("SHE?", "impact.ttf", 470, (20, 220, 255), tracking=-6)
    cyan_c = cyan_c.rotate(-7, expand=True, resample=Image.BICUBIC)
    cyan_c = Image.merge("RGBA", (cyan_c.getchannel("R"), cyan_c.getchannel("G"),
                                  cyan_c.getchannel("B"),
                                  cyan_c.getchannel("A").point(lambda v: int(v * 0.45))))
    paste(base, cyan_c, 2000, 824)

    g = glitch_slices(t, seed=5, n=6, max_shift=38)
    g = glow(g, 22, 0.55, PINK)
    paste(base, g, 1980, 808)

    who = text_img("WHO IS", "msyhl.ttc", 92, WHITE, tracking=14, alpha=225)
    who = who.rotate(-3, expand=True, resample=Image.BICUBIC)
    paste(base, glow(who, 10, 0.8, LAV), 2065, 195)

    q = text_img("?", "msyhl.ttc", 150, GOLD, tracking=0)
    paste(base, glow(rot(q, 12), 16, 0.9, GOLD), 2290, 300)

    base.alpha_composite(scanlines(base.size, alpha=10, spacing=3))
    return add_noise(base, 5, 11)


def design_b():
    """B · 霓虹崩坏 fire"""
    base = load_frame(8.6)
    f = text_img("fire", "msyhl.ttc", 540, PINK, tracking=8, alpha=245)
    f = f.rotate(-6, expand=True, resample=Image.BICUBIC)

    # smeared echo
    for i, (dx, dy, col, al) in enumerate([(-46, -6, CYAN, 0.30), (-22, -3, PINK, 0.35),
                                          (26, 4, VIOLET, 0.35)]):
        e = f.copy()
        e = Image.merge("RGBA", (e.getchannel("R"), e.getchannel("G"), e.getchannel("B"),
                                 e.getchannel("A").point(lambda v: int(v * al))))
        e = Image.merge("RGBA", (
            e.getchannel("R").point(lambda v, c=col[0]: int(c * 0.4)),
            e.getchannel("G").point(lambda v, c=col[1]: int(c * 0.4)),
            e.getchannel("B").point(lambda v, c=col[2]: int(c * 0.4)),
            e.getchannel("A")))
        paste(base, e, 585 + dx, 735 + dy)
    g = glitch_slices(f, seed=9, n=6, max_shift=22)
    g = glow(g, 34, 0.8, PINK)
    paste(base, g, 585, 735)

    # cracks
    cracks = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(cracks)
    rnd = random.Random(4)
    for s in range(6):
        x = rnd.randint(320, 980)
        y = rnd.randint(500, 900)
        pts = [(x, y)]
        for _ in range(5):
            x += rnd.randint(-40, 60)
            y += rnd.randint(-50, 40)
            pts.append((x, y))
        d.line(pts, fill=(255, 255, 255, 70), width=2)
    base.alpha_composite(cracks)

    ft = text_img("feel the", "msyhl.ttc", 84, WHITE, tracking=14, alpha=230)
    ft = ft.rotate(-4, expand=True, resample=Image.BICUBIC)
    paste(base, glow(ft, 12, 0.8, LAV), 420, 470)

    baby = text_img("baby", "msyhl.ttc", 70, LAV, tracking=12, alpha=230)
    baby = baby.rotate(-8, expand=True, resample=Image.BICUBIC)
    paste(base, glow(baby, 12, 0.8, LAV), 2280, 950)

    # sparks
    sp = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sp)
    rnd = random.Random(7)
    for _ in range(90):
        x = rnd.randint(150, 1200)
        y = rnd.randint(350, 1000)
        r = rnd.choice([1, 1, 2, 3])
        a = rnd.randint(40, 160)
        d.ellipse([x, y, x + r, y + r], fill=PINK + (a,))
    base.alpha_composite(sp)
    base.alpha_composite(scanlines(base.size, alpha=8, spacing=3))
    return add_noise(base, 5, 12)


def design_c():
    """C · 立体巨字 WHO / IS / SHE?"""
    base = load_frame(10.4)

    def extrude(text, size, tracking=0, steps=14, dx=5, dy=7, rot_angle=-6):
        t = text_img(text, "impact.ttf", size, (244, 241, 234), tracking=tracking,
                     stroke=2, stroke_color=(36, 8, 48))
        t = t.rotate(rot_angle, expand=True, resample=Image.BICUBIC)
        out = Image.new("RGBA", (t.size[0] + steps * dx + 60, t.size[1] + steps * dy + 60),
                        (0, 0, 0, 0))
        for i in range(steps, 0, -1):
            f = i / steps
            col = (int(40 + (201 - 40) * (1 - f)), int(10 + (167 - 10) * (1 - f)),
                   int(80 + (255 - 80) * (1 - f)))
            s = Image.merge("RGBA", (
                t.getchannel("R").point(lambda v, c=col[0]: c),
                t.getchannel("G").point(lambda v, c=col[1]: c),
                t.getchannel("B").point(lambda v, c=col[2]: c),
                t.getchannel("A")))
            out.alpha_composite(s, (30 + i * dx, 30 + i * dy))
        rim = Image.merge("RGBA", (
            t.getchannel("R").point(lambda v: 255),
            t.getchannel("G").point(lambda v: 111),
            t.getchannel("B").point(lambda v: 216),
            t.getchannel("A").point(lambda v: int(v * 0.9))))
        out.alpha_composite(rim, (38, 38))
        out.alpha_composite(t, (30, 30))
        return out

    who = extrude("WHO", 285, tracking=-4, steps=15, dx=5, dy=7)
    paste(base, who, 520, 560)
    iss = extrude("IS", 210, tracking=0, steps=12, dx=4, dy=6)
    paste(base, iss, 300, 830)
    she = extrude("SHE?", 235, tracking=-4, steps=13, dx=5, dy=6, rot_angle=4)
    paste(base, she, 680, 990)

    ht = halftone(base.size, spacing=8, radius=1.8, alpha=32, color=(20, 0, 40))
    base.alpha_composite(ht)

    mk = text_img("making everybody go", "msyhl.ttc", 64, WHITE, tracking=16, alpha=210)
    paste(base, glow(mk, 10, 0.7, LAV), 1300, 160)

    d = ImageDraw.Draw(base)
    d.line([(120, 420), (900, 420)], fill=GOLD + (110,), width=3)
    d.line([(150, 1040), (1000, 1040)], fill=GOLD + (70,), width=2)
    return add_noise(base, 4, 13)


def design_d():
    """D · 拼贴艺术 MAKING / EVERYBODY / GO"""
    base = load_frame(5.4)
    d = ImageDraw.Draw(base)

    def strip(img_text, fontname, size, fg, bg, x, y, pad=(70, 34), angle=0,
              tracking=0, tape=True):
        t = text_img(img_text, fontname, size, fg, tracking=tracking)
        w = t.size[0] + pad[0] * 2
        h = t.size[1] + pad[1] * 2
        s = Image.new("RGBA", (int(w), int(h)), bg + (235,))
        s.alpha_composite(t, (pad[0], pad[1] - int(size * 0.1)))
        s = rot(s, angle)
        paste(base, s, x, y)
        if tape:
            for tx, ty, ta, tw, th in ((x - w * 0.32, y - h * 0.45, -22, 190, 46),
                                       (x + w * 0.30, y + h * 0.42, 18, 160, 40)):
                tape_img = Image.new("RGBA", (int(tw), int(th)), (245, 242, 235, 120))
                tape_img = rot(tape_img, ta)
                paste(base, tape_img, tx, ty)
        return s

    strip("MAKING", "impact.ttf", 112, (16, 12, 20), (244, 241, 234),
          430, 220, angle=-5, tracking=2)
    strip("EVERYBODY", "impact.ttf", 122, (16, 12, 20), (255, 111, 216),
          640, 420, angle=3, tracking=0)
    strip("GO", "impact.ttf", 230, (244, 241, 234), (32, 20, 60),
          330, 700, angle=-8, tracking=6)
    strip("she?", "msyhl.ttc", 96, (255, 201, 84), (24, 16, 40),
          900, 880, angle=12, tracking=6, pad=(46, 22), tape=False)

    # staples
    sp = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d2 = ImageDraw.Draw(sp)
    for (x, y) in ((240, 160), (640, 300), (200, 620), (900, 820)):
        d2.rectangle([x, y, x + 34, y + 8], fill=(230, 228, 220, 200))
    base.alpha_composite(sp)
    base.alpha_composite(scanlines(base.size, alpha=8, spacing=4))
    return add_noise(base, 5, 14)


def design_e():
    """E · 轮廓回声 FIRE"""
    base = load_frame(10.4)
    f = font("ariblk.ttf", 380)
    t = text_img("FIRE", "ariblk.ttf", 380, WHITE, tracking=6, stroke=5,
                 stroke_color=WHITE)
    # hollow: keep only stroke -> make fill transparent
    arr = t.split()
    a = arr[3].point(lambda v: int(v * 0.42))
    t2 = Image.merge("RGBA", (arr[0], arr[1], arr[2], a))
    t2 = t2.rotate(-5, expand=True, resample=Image.BICUBIC)

    # ring behind
    ring = Image.new("RGBA", (1100, 700), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    rd.ellipse([40, 120, 1040, 640], outline=PINK + (90,), width=3)
    rd.ellipse([120, 190, 960, 590], outline=LAV + (60,), width=2)
    ring = ring.rotate(-5, expand=True, resample=Image.BICUBIC)
    paste(base, ring, 1980, 740)

    # echo outlines
    for i, (dx, alpha, col) in enumerate([(-80, 0.16, CYAN), (-50, 0.24, LAV),
                                          (-25, 0.34, PINK), (0, 1.0, WHITE)]):
        c = t2.copy()
        c = Image.merge("RGBA", (
            c.getchannel("R").point(lambda v, cc=col[0]: int(cc)),
            c.getchannel("G").point(lambda v, cc=col[1]: int(cc)),
            c.getchannel("B").point(lambda v, cc=col[2]: int(cc)),
            c.getchannel("A").point(lambda v, a=alpha: int(v * a))))
        if i == 3:
            c = glow(c, 18, 0.9, PINK)
        paste(base, c, 1980 + dx, 740)

    ft = text_img("feel the", "msyhl.ttc", 76, WHITE, tracking=16, alpha=220)
    ft = ft.rotate(-6, expand=True, resample=Image.BICUBIC)
    paste(base, glow(ft, 10, 0.8, LAV), 1780, 560)

    # sparks + light streak
    sp = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sp)
    rnd = random.Random(21)
    for _ in range(70):
        x = rnd.randint(1450, 2500)
        y = rnd.randint(480, 1020)
        r = rnd.choice([1, 1, 2])
        d.ellipse([x, y, x + r, y + r], fill=PINK + (rnd.randint(50, 160),))
    d.line([(1450, 900), (2500, 700)], fill=PINK + (70,), width=2)
    base.alpha_composite(sp)
    base.alpha_composite(scanlines(base.size, alpha=8, spacing=3))
    return add_noise(base, 5, 15)


def contact_sheet(paths, labels, out_path):
    cell_w, cell_h = 1280, 540
    bar = 36
    cols = 2
    rows = (len(paths) + 1) // cols
    sheet = Image.new("RGB", (cell_w * cols, (cell_h + bar) * rows), (10, 9, 8))
    d = ImageDraw.Draw(sheet)
    f = font("msyhbd.ttc", 24)
    for i, (p, lab) in enumerate(zip(paths, labels)):
        im = Image.open(p).convert("RGB").resize((cell_w, cell_h), Image.LANCZOS)
        x = (i % cols) * cell_w
        y = (i // cols) * (cell_h + bar)
        sheet.paste(im, (x, y + bar))
        d.text((x + 18, y + 7), lab, font=f, fill=(240, 236, 230))
    sheet.save(out_path, quality=92)


def main():
    random.seed(42)
    np.random.seed(42)
    jobs = [
        ("方案A_故障切片.jpg", "A · 故障切片「SHE?」", design_a),
        ("方案B_霓虹崩坏.jpg", "B · 霓虹崩坏「fire」", design_b),
        ("方案C_立体巨字.jpg", "C · 立体巨字「WHO / IS / SHE?」", design_c),
        ("方案D_拼贴排版.jpg", "D · 拼贴艺术「MAKING / EVERYBODY / GO」", design_d),
        ("方案E_轮廓回声.jpg", "E · 轮廓回声「FIRE」", design_e),
        ("方案F_竖排霓虹.jpg", "F · 竖排霓虹「SHE?」", design_f),
    ]
    paths = []
    labels = []
    for name, lab, fn in jobs:
        img = fn()
        rgb = img.convert("RGB")
        p = os.path.join(OUT, name)
        rgb.save(p, quality=93)
        paths.append(p)
        labels.append(lab)
        print("rendered", name)
    contact_sheet(paths, labels, os.path.join(OUT, "字幕设计_方案总览.jpg"))
    print("done")


def design_f():
    """F · 竖排霓虹 SHE?"""
    base = load_frame(13.2)
    letters = "SHE?"
    f = font("impact.ttf", 230)
    ys = [250, 470, 690, 930]
    for ch, y in zip(letters, ys):
        t = text_img(ch, "impact.ttf", 230, WHITE, tracking=0)
        t = t.rotate(-2, expand=True, resample=Image.BICUBIC)
        red = Image.merge("RGBA", (
            t.getchannel("R").point(lambda v: 255), t.getchannel("G").point(lambda v: 40),
            t.getchannel("B").point(lambda v: 30),
            t.getchannel("A").point(lambda v: int(v * 0.5))))
        cyan = Image.merge("RGBA", (
            t.getchannel("R").point(lambda v: 20), t.getchannel("G").point(lambda v: 220),
            t.getchannel("B").point(lambda v: 255),
            t.getchannel("A").point(lambda v: int(v * 0.4))))
        paste(base, red, 2374, y + 6)
        paste(base, cyan, 2390, y - 6)
        paste(base, glow(t, 16, 0.65, PINK), 2382, y)

    d = ImageDraw.Draw(base)
    d.line([(2230, 140), (2230, 1000)], fill=LAV + (90,), width=2)
    d.line([(2260, 140), (2260, 1000)], fill=PINK + (50,), width=1)

    who = text_img("WHO IS", "msyhl.ttc", 78, WHITE, tracking=14, alpha=220)
    who = who.rotate(90, expand=True)
    paste(base, glow(who, 10, 0.7, LAV), 2170, 560)

    q = text_img("?", "msyhl.ttc", 120, GOLD, tracking=0)
    paste(base, glow(rot(q, 8), 14, 0.9, GOLD), 2170, 180)
    base.alpha_composite(scanlines(base.size, alpha=8, spacing=3))
    return add_noise(base, 4, 16)

if __name__ == "__main__":
    main()





