# -*- coding: utf-8 -*-
"""Make B站 / 竖屏 covers (16:9 and 3:4) for the Remiel MMD video."""
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
FRAMES = os.path.join(ROOT, "输出", "封面", "_frames")
OUT = os.path.join(ROOT, "输出", "封面")
FONTS = os.path.join(BASE, "fonts")
WIN = r"C:\Windows\Fonts"

F_ARCHIVO = os.path.join(FONTS, "ArchivoBlack-Regular.ttf")
F_BEBAS = os.path.join(FONTS, "BebasNeue-Regular.ttf")
F_ANTON = os.path.join(FONTS, "Anton-Regular.ttf")
F_SILK = os.path.join(FONTS, "Silkscreen-Regular.ttf")
F_MARKER = os.path.join(FONTS, "PermanentMarker-Regular.ttf")
F_GEOI = os.path.join(WIN, "georgiai.ttf")
F_MSYH = os.path.join(WIN, "msyh.ttc")
F_MSYHB = os.path.join(WIN, "msyhbd.ttc")

WHITE = (248, 245, 238)
CREAM = (247, 238, 215)
PINK = (255, 92, 179)
LAV = (196, 164, 255)
LAV_DEEP = (88, 42, 122)
INK = (18, 14, 22)
GOLD = (255, 201, 84)


def font(path, size):
    return ImageFont.truetype(path, int(size))


def text_img(text, fontpath, size, color, tracking=0, stroke=0, stroke_color=INK):
    f = font(fontpath, size)
    widths = []
    for ch in text:
        bb = f.getbbox(ch)
        widths.append(bb[2] - bb[0] if bb[2] > bb[0] else int(size * 0.3))
    tw = int(sum(widths) + tracking * max(0, len(text) - 1)) + int(size * 0.6)
    th = int(size * 2.0)
    img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = int(size * 0.2)
    for ch, w in zip(text, widths):
        d.text((x, int(size * 0.32)), ch, font=f, fill=color + (255,),
               stroke_width=stroke, stroke_fill=stroke_color + (255,))
        x += w + tracking
    bb = img.getbbox()
    return img.crop(bb) if bb else img


def rot(img, angle):
    return img.rotate(angle, expand=True, resample=Image.BICUBIC)


def paste(base, layer, xy, alpha=1.0):
    if alpha < 1:
        a = layer.getchannel("A").point(lambda v: int(v * alpha))
        layer = layer.copy()
        layer.putalpha(a)
    base.alpha_composite(layer, (int(xy[0]), int(xy[1])))


def pill(text, fontpath, size, fg, bg, pad=(34, 16), radius=40, track=2):
    t = text_img(text, fontpath, size, fg, tracking=track)
    w, h = t.size[0] + pad[0] * 2, t.size[1] + pad[1] * 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=bg + (236,))
    img.alpha_composite(t, (pad[0], pad[1]))
    return img


def star(size, color, alpha=230):
    s = int(size)
    img = Image.new("RGBA", (s * 2, s * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = []
    for i in range(10):
        r = s if i % 2 == 0 else s * 0.42
        a = -3.14159 / 2 + i * 3.14159 / 5
        pts.append((s + r * np.cos(a), s + r * np.sin(a)))
    d.polygon(pts, fill=color + (alpha,))
    return img


def heart(size, color, alpha=230):
    s = int(size)
    img = Image.new("RGBA", (s * 2, s * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, s, s], fill=color + (alpha,))
    d.ellipse([s, 0, s * 2, s], fill=color + (alpha,))
    d.polygon([(0, s * 0.55), (s * 2, s * 0.55), (s, s * 1.9)], fill=color + (alpha,))
    return img


def polish(im):
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255.0
    l = 0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]
    a = np.clip(l[:, :, None] + (a - l[:, :, None]) * 1.06, 0, 1)
    a = np.clip((a - 0.5) * 1.05 + 0.5, 0, 1)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    vd = ((xx - w / 2) / (w * 0.62)) ** 2 + ((yy - h / 2) / (h * 0.64)) ** 2
    vig = np.clip(1.0 - 0.28 * np.clip(vd, 0, 1.4) ** 1.35, 0.45, 1.0)
    a = a * vig[:, :, None]
    return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8), "RGB")


def crop_16x9(im):
    w, h = im.size
    cw = int(h * 16 / 9)
    x0 = (w - cw) // 2
    return im.crop((x0, 0, x0 + cw, h)).resize((1920, 1080), Image.LANCZOS)


def crop_3x4(im, cx=0.5):
    w, h = im.size
    cw = int(h * 3 / 4)
    x0 = int(w * cx - cw / 2)
    x0 = max(0, min(w - cw, x0))
    return im.crop((x0, 0, x0 + cw, h)).resize((1080, 1440), Image.LANCZOS)


def darken_edges(im, top=110, bottom=150):
    w, h = im.size
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for i in range(top):
        a = int(150 * (1 - i / top))
        d.line([(0, i), (w, i)], fill=(6, 4, 10, a))
    for i in range(bottom):
        a = int(200 * (1 - i / bottom))
        d.line([(0, h - 1 - i), (w, h - 1 - i)], fill=(6, 4, 10, a))
    im = im.convert("RGBA")
    im.alpha_composite(ov)
    return im


# ------------------------------------------------------------------ covers
def cover_s4_169():
    im = polish(crop_16x9(Image.open(os.path.join(FRAMES, "clean_64.7.jpg"))))
    im = darken_edges(im, 90, 200)
    c = im.copy()

    # tag
    pill16 = pill("MMD · 韩舞", F_MSYHB, 30, WHITE, LAV_DEEP, pad=(30, 13), radius=34, track=4)
    paste(c, pill16, (80, 70))
    # top small
    top = text_img("KISS OF LIFE  ·  Who is she (JP Ver.)", F_SILK, 24, CREAM, tracking=3)
    paste(c, top, (1920 - top.size[0] - 80, 84), 0.9)

    # name + sub (above the title block)
    nm = text_img("蕾米埃尔", F_MSYHB, 88, WHITE, tracking=8, stroke=4, stroke_color=INK)
    c.alpha_composite(nm, (96, 596))
    sub = text_img("紫焰舞台 · 韩舞 MMD", F_MSYHB, 30, LAV, tracking=4)
    c.alpha_composite(sub, (100, 700))
    # tape behind title
    tape = Image.new("RGBA", (960, 250), LAV + (80,))
    tape = rot(tape.filter(ImageFilter.GaussianBlur(1)), -4)
    paste(c, tape, (56, 740))
    # big title
    t1 = text_img("WHO IS", F_ARCHIVO, 128, PINK, tracking=2)
    c.alpha_composite(t1, (92, 748))
    t2 = text_img("SHE?", F_ARCHIVO, 168, WHITE, tracking=2, stroke=4, stroke_color=INK)
    c.alpha_composite(t2, (88, 872))
    # accents
    paste(c, star(34, PINK, 235), (1500, 740))
    paste(c, star(22, WHITE, 200), (1660, 850))
    paste(c, heart(20, LAV, 220), (1380, 940))
    return c.convert("RGB")


def cover_s6_169():
    im = polish(crop_16x9(Image.open(os.path.join(FRAMES, "clean_112.7.jpg"))))
    im = darken_edges(im, 90, 210)
    c = im.copy()
    # sticky note top-left
    note = Image.new("RGBA", (420, 150), CREAM + (240,))
    nd = ImageDraw.Draw(note)
    nd.line([(20, 20), (400, 20)], fill=(200, 190, 170, 120), width=2)
    nt = text_img("MMD 韩舞", F_MSYHB, 44, INK, tracking=5)
    note.alpha_composite(nt, (36, 44))
    paste(c, rot(note, -4), (70, 60))
    # highlighter + marker title
    swipe = Image.new("RGBA", (1000, 240), PINK + (150,))
    swipe = rot(swipe.filter(ImageFilter.GaussianBlur(2)), -3)
    paste(c, swipe, (60, 760))
    t = text_img("WHO IS SHE?", F_MARKER, 145, INK, tracking=2)
    c.alpha_composite(t, (110, 786))
    nm = text_img("蕾米埃尔", F_MSYHB, 88, CREAM, tracking=8, stroke=4, stroke_color=INK)
    c.alpha_composite(nm, (112, 636))
    sub = text_img("KISS OF LIFE · Who is she (JP Ver.)", F_SILK, 24, CREAM, tracking=2)
    c.alpha_composite(sub, (1920 - sub.size[0] - 80, 1010), )
    paste(c, heart(22, PINK, 230), (1660, 760))
    paste(c, star(26, GOLD, 230), (1800, 870))
    return c.convert("RGB")


def cover_s4_34():
    im = polish(crop_3x4(Image.open(os.path.join(FRAMES, "clean_72.7.jpg"))))
    im = darken_edges(im, 300, 260)
    c = im.copy()
    # top tag
    p = pill("MMD · 韩舞", F_MSYHB, 34, WHITE, LAV_DEEP, pad=(34, 15), radius=36, track=4)
    paste(c, p, ((1080 - p.size[0]) / 2, 90))
    # name
    nm = text_img("蕾米埃尔", F_MSYHB, 96, WHITE, tracking=10, stroke=4, stroke_color=INK)
    paste(c, nm, ((1080 - nm.size[0]) / 2, 170))
    sub = text_img("紫焰舞台 · 韩舞 MMD", F_MSYHB, 32, LAV, tracking=6)
    paste(c, sub, ((1080 - sub.size[0]) / 2, 300))
    # bottom block: tape + title
    tape = Image.new("RGBA", (960, 250), LAV + (80,))
    tape = rot(tape.filter(ImageFilter.GaussianBlur(1)), -4)
    paste(c, tape, (40, 1040))
    t1 = text_img("WHO IS", F_ARCHIVO, 138, PINK, tracking=2)
    c.alpha_composite(t1, (70, 1010))
    t2 = text_img("SHE?", F_ARCHIVO, 180, WHITE, tracking=2, stroke=4, stroke_color=INK)
    c.alpha_composite(t2, (66, 1140))
    small = text_img("KISS OF LIFE · Who is she (JP Ver.)", F_SILK, 22, CREAM, tracking=1)
    c.alpha_composite(small, (int((1080 - small.size[0]) / 2), 1380))
    paste(c, star(30, PINK, 230), (860, 1010))
    paste(c, heart(18, LAV, 220), (150, 960))
    return c.convert("RGB")


def cover_s6_34():
    im = polish(crop_3x4(Image.open(os.path.join(FRAMES, "clean_136.7.jpg"))))
    im = darken_edges(im, 300, 280)
    c = im.copy()
    note = Image.new("RGBA", (460, 160), CREAM + (240,))
    nd = ImageDraw.Draw(note)
    nd.line([(20, 22), (440, 22)], fill=(200, 190, 170, 120), width=2)
    nt = text_img("韩舞 MMD", F_MSYHB, 48, INK, tracking=6)
    note.alpha_composite(nt, (36, 48))
    paste(c, rot(note, 3), ((1080 - 460) / 2, 80))
    nm = text_img("蕾米埃尔", F_MSYHB, 92, CREAM, tracking=10, stroke=4, stroke_color=INK)
    paste(c, nm, (int((1080 - nm.size[0]) / 2), 240))
    # bottom
    swipe = Image.new("RGBA", (980, 260), PINK + (150,))
    swipe = rot(swipe.filter(ImageFilter.GaussianBlur(2)), -3)
    paste(c, swipe, (40, 1080))
    t = text_img("WHO IS SHE?", F_MARKER, 128, INK, tracking=2)
    c.alpha_composite(t, (70, 1120))
    small = text_img("KISS OF LIFE · Who is she (JP Ver.)", F_SILK, 22, CREAM, tracking=1)
    c.alpha_composite(small, (int((1080 - small.size[0]) / 2), 1360))
    paste(c, star(28, GOLD, 230), (880, 1000))
    paste(c, heart(18, PINK, 230), (150, 1010))
    return c.convert("RGB")


def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = [
        ("封面_16x9_A_S4.jpg", cover_s4_169),
        ("封面_16x9_B_S6.jpg", cover_s6_169),
        ("封面_3x4_A_S4.jpg", cover_s4_34),
        ("封面_3x4_B_S6.jpg", cover_s6_34),
    ]
    made = []
    for name, fn in jobs:
        img = fn()
        p = os.path.join(OUT, name)
        img.save(p, quality=95, subsampling=1)
        made.append((name, p, img.size))
        print("made", name, img.size)
    # preview sheet 2x2 (scale)
    cells = []
    for name, p, size in made:
        im = Image.open(p).convert("RGB")
        w = 720
        h = int(w * im.size[1] / im.size[0])
        cells.append(im.resize((w, h), Image.LANCZOS))
    pad = 20
    cw = max(c.size[0] for c in cells) + pad * 2
    ch = max(c.size[1] for c in cells) + pad * 2
    sheet = Image.new("RGB", (cw * 2, ch * 2), (12, 10, 14))
    f = font(F_MSYHB, 22)
    for i, c in enumerate(cells):
        x = (i % 2) * cw + pad
        y = (i // 2) * ch + pad
        sheet.paste(c, (x, y))
    d = ImageDraw.Draw(sheet)
    for i, (name, p, size) in enumerate(made):
        x = (i % 2) * cw + pad
        y = (i // 2) * ch + pad + cells[i].size[1] + 4
        d.text((x, y), "%s (%dx%d)" % (name, size[0], size[1]), font=f, fill=(230, 226, 220))
    sheet.save(os.path.join(OUT, "封面_预览.jpg"), quality=90)
    print("done")


if __name__ == "__main__":
    main()

