# -*- coding: utf-8 -*-
"""More cover variants for the Remiel MMD video: 16:9 and 4:3."""
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import make_covers as MC

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
SRC = os.path.join(ROOT, "输出", "S4S6_完整版", "_work", "_base_full.mp4")
OUT = os.path.join(ROOT, "输出", "封面")
FRAMES = os.path.join(OUT, "_frames2")
FF = r"C:\Users\35530\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"

WHITE, CREAM, PINK, LAV = MC.WHITE, MC.CREAM, MC.PINK, MC.LAV
LAV_DEEP, INK, GOLD = MC.LAV_DEEP, MC.INK, MC.GOLD
F_ARCHIVO, F_BEBAS, F_ANTON, F_SILK = MC.F_ARCHIVO, MC.F_BEBAS, MC.F_ANTON, MC.F_SILK
F_MARKER, F_MSYH, F_MSYHB = MC.F_MARKER, MC.F_MSYH, MC.F_MSYHB
paste = MC.paste


def ensure_frames():
    os.makedirs(FRAMES, exist_ok=True)
    for t in ("20.7", "32.7", "72.7", "76.7", "100.7", "112.7", "136.7"):
        p = os.path.join(FRAMES, "clean_%s.jpg" % t)
        if not os.path.exists(p):
            subprocess.run([FF, "-v", "error", "-y", "-ss", t, "-i", SRC,
                            "-frames:v", "1", "-q:v", "2", p], capture_output=True)


def fr(t):
    return Image.open(os.path.join(FRAMES, "clean_%s.jpg" % t)).convert("RGB")


def crop_4x3(im):
    w, h = im.size
    cw = int(h * 4 / 3)
    x0 = (w - cw) // 2
    return im.crop((x0, 0, x0 + cw, h)).resize((1440, 1080), Image.LANCZOS)


def gradient_fill(layer, stops):
    w, h = layer.size
    ys = np.linspace(0, 1, h)
    cols = np.zeros((h, 3), np.float32)
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        mask = (ys >= p0) & (ys <= p1)
        t = (ys[mask] - p0) / max(1e-6, p1 - p0)
        for k in range(3):
            cols[mask, k] = c0[k] + (c1[k] - c0[k]) * t
    grad = np.repeat(cols[:, None, :], w, axis=1)
    grad_img = Image.fromarray(np.clip(grad, 0, 255).astype(np.uint8)).convert("RGB")
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.paste(grad_img, (0, 0), layer.getchannel("A"))
    # gloss band
    gloss = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(gloss)
    gd.polygon([(0, int(h * 0.18)), (w, int(h * 0.04)), (w, int(h * 0.28)),
                (0, int(h * 0.40))], fill=(255, 255, 255, 120))
    gloss = gloss.filter(ImageFilter.GaussianBlur(3))
    band = Image.new("RGBA", layer.size, (255, 255, 255, 0))
    band.putalpha(gloss.getchannel("A").point(lambda v: int(v * 0.55)))
    out.alpha_composite(Image.composite(band, Image.new("RGBA", layer.size, (0, 0, 0, 0)),
                                        layer.getchannel("A")))
    return out


def outline(layer, color, width):
    a = layer.getchannel("A")
    for _ in range(width):
        a = a.filter(ImageFilter.MaxFilter(3))
    out = Image.new("RGBA", layer.size, color + (0,))
    out.putalpha(a.point(lambda v: min(255, v * 2)))
    return out


def glow(layer, radius, color, alpha=0.8):
    a = layer.getchannel("A").filter(ImageFilter.GaussianBlur(radius))
    g = Image.new("RGBA", layer.size, color + (0,))
    g.putalpha(a.point(lambda v: int(v * alpha)))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.alpha_composite(g)
    out.alpha_composite(layer)
    return out


def chrome(image):
    return gradient_fill(image, [(0.0, (255, 255, 255)), (0.26, (212, 220, 238)),
                                 (0.45, (122, 132, 158)), (0.60, (248, 251, 255)),
                                 (0.80, (168, 176, 198)), (1.0, (238, 242, 250))])


# ------------------------------------------------------------- 16:9 variants
def c16_y2k():
    im = MC.polish(MC.crop_16x9(fr("20.7")))
    im = MC.darken_edges(im, 70, 120)
    c = im.copy()
    # chrome SHE?
    t = MC.text_img("SHE?", F_ARCHIVO, 350, WHITE, tracking=-4, stroke=4, stroke_color=(30, 18, 40))
    t = chrome(t)
    ol = outline(t, (30, 18, 40), 4)
    paste = MC.paste
    paste(c, ol.filter(ImageFilter.GaussianBlur(8)), (830, 620))
    paste(c, ol, (826, 614))
    paste(c, t, (820, 608))
    # badge + name
    b = MC.pill("who is she? · KISS OF LIFE", F_ARCHIVO, 42, WHITE, PINK, pad=(34, 15), radius=44, track=2)
    paste(c, MC.rot(b, 4), (120, 96))
    nm = MC.text_img("蕾米埃尔 × 紫焰舞台", F_MSYHB, 40, WHITE, tracking=6, stroke=3, stroke_color=INK)
    paste(c, nm, (120, 950))
    sub = MC.text_img("MMD · 韩舞 · Who is she (JP Ver.)", F_MSYH, 26, CREAM, tracking=4)
    paste(c, sub, (120, 1010))
    for xy, s in (((930, 560), 30), ((1560, 520), 24), ((880, 900), 20), ((1700, 940), 26)):
        paste(c, MC.star(s, WHITE, 235), xy)
    return c.convert("RGB")


def c16_minimal():
    im = MC.polish(MC.crop_16x9(fr("32.7")))
    im = MC.darken_edges(im, 80, 160)
    c = im.copy()
    top = MC.text_img("KISS OF LIFE  ·  WHO IS SHE (JP VER.)", F_SILK, 22, CREAM, tracking=5)
    paste(c, top, (1920 - top.size[0] - 80, 76), 0.85)
    nm = MC.text_img("蕾米埃尔", F_MSYHB, 44, WHITE, tracking=14, stroke=2, stroke_color=INK)
    paste(c, nm, (90, 90))
    t1 = MC.text_img("WHO IS", F_ANTON, 150, WHITE, tracking=20)
    t2 = MC.text_img("SHE?", F_ANTON, 190, WHITE, tracking=16)
    paste(c, t1, (92, 690))
    paste(c, t2, (88, 850))
    ln = Image.new("RGBA", (600, 4), WHITE + (170,))
    c.alpha_composite(ln, (96, 660))
    tag = MC.text_img("MMD · 韩舞 · 紫焰舞台", F_MSYH, 24, LAV, tracking=6)
    paste(c, tag, (96, 1030))
    return c.convert("RGB")


def c16_sticker():
    im = MC.polish(MC.crop_16x9(fr("76.7")))
    im = MC.darken_edges(im, 80, 170)
    c = im.copy()
    # stripes
    stripes = Image.new("RGBA", (900, 700), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripes)
    for i in range(-500, 1200, 64):
        sd.line([(i, 0), (i + 500, 700)], fill=PINK + (55,), width=22)
    stripes = MC.rot(stripes, -12)
    paste = MC.paste
    paste(c, stripes, (700, 550))
    # SHE? big sticker
    t = MC.text_img("SHE?", F_ANTON, 420, WHITE, tracking=2)
    ol = outline(t, WHITE, 7)
    shadow = outline(t, (28, 18, 40), 9)
    paste(c, shadow.filter(ImageFilter.GaussianBlur(10)), (1000, 600))
    paste(c, ol, (988, 588))
    pk = outline(t, PINK, 4)
    paste(c, pk, (960, 620))
    paste(c, t, (975, 585))
    # WHO IS small
    wi = MC.text_img("WHO IS", F_ARCHIVO, 120, PINK, tracking=4)
    paste(c, wi, (1000, 500))
    # badge
    b = MC.pill("MMD · 韩舞 · 蕾米埃尔", F_MSYHB, 34, WHITE, LAV_DEEP, pad=(30, 14), radius=32, track=3)
    paste(c, MC.rot(b, -3), (90, 90))
    sub = MC.text_img("KISS OF LIFE · Who is she (JP Ver.)", F_SILK, 22, CREAM, tracking=2)
    paste(c, sub, (1920 - sub.size[0] - 80, 1000))
    paste(c, MC.star(26, GOLD, 230), (1620, 620))
    return c.convert("RGB")


def c16_neon():
    im = MC.polish(MC.crop_16x9(fr("136.7")))
    im = MC.darken_edges(im, 80, 150)
    c = im.copy()
    t = MC.text_img("who is she?", F_MSYH, 150, (245, 240, 255), tracking=6)
    t = MC.rot(t, -3)
    n = glow(t, 22, LAV, 0.75)
    paste = MC.paste
    paste(c, n, (120, 600))
    nm = MC.text_img("蕾米埃尔", F_MSYHB, 60, WHITE, tracking=12, stroke=2, stroke_color=(40, 20, 60))
    paste(c, nm, (128, 520))
    line = Image.new("RGBA", (620, 3), LAV + (150,))
    c.alpha_composite(line, (130, 590))
    k = MC.text_img("KISS OF LIFE  ·  MMD 韩舞", F_MSYH, 24, LAV, tracking=4)
    paste(c, k, (130, 780))
    # corner frame
    d = ImageDraw.Draw(c)
    for (x, y, sx, sy) in ((60, 60, 1, 1), (1860, 60, -1, 1), (60, 1020, 1, -1), (1860, 1020, -1, -1)):
        d.line([(x, y), (x + 150 * sx, y)], fill=LAV + (110,), width=2)
        d.line([(x, y), (x, y + 90 * sy)], fill=LAV + (110,), width=2)
    for xy, s in (((1500, 470), 24), ((1650, 560), 18), ((980, 870), 16)):
        paste(c, MC.star(s, PINK, 230), xy)
    return c.convert("RGB")


# -------------------------------------------------------------- 4:3 variants
def c43_s4():
    im = MC.polish(crop_4x3(fr("72.7")))
    im = MC.darken_edges(im, 260, 250)
    c = im.copy()
    p = MC.pill("MMD · 韩舞", F_MSYHB, 32, WHITE, LAV_DEEP, pad=(32, 14), radius=34, track=4)
    paste = MC.paste
    paste(c, p, ((1440 - p.size[0]) / 2, 80))
    nm = MC.text_img("蕾米埃尔", F_MSYHB, 86, WHITE, tracking=10, stroke=4, stroke_color=INK)
    paste(c, nm, (int((1440 - nm.size[0]) / 2), 150))
    sub = MC.text_img("紫焰舞台 · 韩舞 MMD", F_MSYHB, 30, LAV, tracking=6)
    paste(c, sub, (int((1440 - sub.size[0]) / 2), 265))
    tape = Image.new("RGBA", (1100, 230), LAV + (80,))
    tape = MC.rot(tape.filter(ImageFilter.GaussianBlur(1)), -4)
    paste(c, tape, (150, 790))
    t1 = MC.text_img("WHO IS", F_ARCHIVO, 132, PINK, tracking=2)
    c.alpha_composite(t1, (200, 770))
    t2 = MC.text_img("SHE?", F_ARCHIVO, 176, WHITE, tracking=2, stroke=4, stroke_color=INK)
    c.alpha_composite(t2, (196, 890))
    small = MC.text_img("KISS OF LIFE · Who is she (JP Ver.)", F_SILK, 21, CREAM, tracking=1)
    c.alpha_composite(small, (int((1440 - small.size[0]) / 2), 1035))
    paste(c, MC.star(28, PINK, 230), (1150, 750))
    paste(c, MC.heart(17, LAV, 220), (330, 720))
    return c.convert("RGB")


def c43_s6():
    im = MC.polish(crop_4x3(fr("112.7")))
    im = MC.darken_edges(im, 260, 260)
    c = im.copy()
    note = Image.new("RGBA", (420, 150), CREAM + (240,))
    nd = ImageDraw.Draw(note)
    nd.line([(20, 22), (400, 22)], fill=(200, 190, 170, 120), width=2)
    nt = MC.text_img("韩舞 MMD", F_MSYHB, 44, INK, tracking=6)
    note.alpha_composite(nt, (34, 46))
    paste = MC.paste
    paste(c, MC.rot(note, 3), (int((1440 - 420) / 2), 70))
    nm = MC.text_img("蕾米埃尔", F_MSYHB, 88, CREAM, tracking=8, stroke=4, stroke_color=INK)
    paste(c, nm, (int((1440 - nm.size[0]) / 2), 230))
    swipe = Image.new("RGBA", (1240, 250), PINK + (150,))
    swipe = MC.rot(swipe.filter(ImageFilter.GaussianBlur(2)), -3)
    paste(c, swipe, (90, 820))
    t = MC.text_img("WHO IS SHE?", F_MARKER, 138, INK, tracking=2)
    c.alpha_composite(t, (140, 850))
    small = MC.text_img("KISS OF LIFE · Who is she (JP Ver.)", F_SILK, 21, CREAM, tracking=1)
    c.alpha_composite(small, (int((1440 - small.size[0]) / 2), 1030))
    paste(c, MC.star(26, GOLD, 230), (1180, 740))
    paste(c, MC.heart(17, PINK, 230), (300, 750))
    return c.convert("RGB")


def c43_y2k():
    im = MC.polish(crop_4x3(fr("20.7")))
    im = MC.darken_edges(im, 220, 200)
    c = im.copy()
    t = MC.text_img("SHE?", F_ARCHIVO, 240, WHITE, tracking=-4, stroke=4, stroke_color=(30, 18, 40))
    t = chrome(t)
    ol = outline(t, (30, 18, 40), 4)
    paste = MC.paste
    paste(c, ol.filter(ImageFilter.GaussianBlur(8)), (520, 730))
    paste(c, ol, (516, 724))
    paste(c, t, (510, 718))
    b = MC.pill("who is she? · KISS OF LIFE", F_ARCHIVO, 36, WHITE, PINK, pad=(30, 13), radius=40, track=2)
    paste(c, MC.rot(b, 4), (90, 90))
    nm = MC.text_img("蕾米埃尔 × 紫焰舞台", F_MSYHB, 38, WHITE, tracking=6, stroke=3, stroke_color=INK)
    paste(c, nm, (92, 990))
    sub = MC.text_img("MMD · 韩舞 · Who is she (JP Ver.)", F_SILK, 22, CREAM, tracking=3)
    paste(c, sub, (92, 1042))
    for xy, s in (((640, 620), 26), ((1180, 560), 22), ((560, 900), 18)):
        paste(c, MC.star(s, WHITE, 235), xy)
    return c.convert("RGB")


def c43_neon():
    im = MC.polish(crop_4x3(fr("100.7")))
    im = MC.darken_edges(im, 240, 220)
    c = im.copy()
    t = MC.text_img("who is she?", F_MSYH, 120, (245, 240, 255), tracking=5)
    t = MC.rot(t, -3)
    paste = MC.paste
    paste(c, glow(t, 20, LAV, 0.75), (110, 720))
    nm = MC.text_img("蕾米埃尔", F_MSYHB, 58, WHITE, tracking=12, stroke=2, stroke_color=(40, 20, 60))
    paste(c, nm, (116, 650))
    line = Image.new("RGBA", (520, 3), LAV + (150,))
    c.alpha_composite(line, (118, 712))
    k = MC.text_img("KISS OF LIFE  ·  MMD 韩舞", F_MSYH, 23, LAV, tracking=4)
    paste(c, k, (118, 880))
    d = ImageDraw.Draw(c)
    for (x, y, sx, sy) in ((50, 50, 1, 1), (1390, 50, -1, 1), (50, 1030, 1, -1), (1390, 1030, -1, -1)):
        d.line([(x, y), (x + 120 * sx, y)], fill=LAV + (110,), width=2)
        d.line([(x, y), (x, y + 80 * sy)], fill=LAV + (110,), width=2)
    paste(c, MC.star(22, PINK, 230), (1150, 640))
    return c.convert("RGB")


def main():
    ensure_frames()
    jobs = [
        ("封面_16x9_C_Y2K.jpg", c16_y2k, 16),
        ("封面_16x9_D_极简.jpg", c16_minimal, 16),
        ("封面_16x9_E_贴纸.jpg", c16_sticker, 16),
        ("封面_16x9_F_霓虹.jpg", c16_neon, 16),
        ("封面_4x3_A_S4.jpg", c43_s4, 43),
        ("封面_4x3_B_S6.jpg", c43_s6, 43),
        ("封面_4x3_C_Y2K.jpg", c43_y2k, 43),
        ("封面_4x3_D_霓虹.jpg", c43_neon, 43),
    ]
    made16, made43 = [], []
    for name, fn, r in jobs:
        img = fn()
        p = os.path.join(OUT, name)
        img.save(p, quality=95, subsampling=1)
        (made16 if r == 16 else made43).append((name, p, img.size))
        print("made", name, img.size)
    # previews
    def sheet(items, cols, out_name, pad=18):
        cells = []
        for name, p, size in items:
            im = Image.open(p).convert("RGB")
            w = 720 if im.size[0] > im.size[1] else 520
            h = int(w * im.size[1] / im.size[0])
            cells.append((im.resize((w, h), Image.LANCZOS), name))
        cw = max(c[0].size[0] for c in cells) + pad * 2
        ch = max(c[0].size[1] for c in cells) + pad * 2 + 26
        rows = (len(cells) + cols - 1) // cols
        sh = Image.new("RGB", (cw * cols, ch * rows), (12, 10, 14))
        d = ImageDraw.Draw(sh)
        f = MC.font(F_MSYHB, 18)
        for i, (im, name) in enumerate(cells):
            x = (i % cols) * cw + pad
            y = (i // cols) * ch + pad
            sh.paste(im, (x, y))
            d.text((x, y + im.size[1] + 3), name, font=f, fill=(230, 226, 220))
        sh.save(os.path.join(OUT, out_name), quality=90)
        print("sheet", out_name, sh.size)

    sheet(made16, 2, "_preview_16x9_new.jpg")
    sheet(made43, 2, "_preview_4x3_new.jpg")


if __name__ == "__main__":
    main()
