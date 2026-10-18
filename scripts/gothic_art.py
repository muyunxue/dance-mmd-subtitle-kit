# -*- coding: utf-8 -*-
"""Gothic full-bleed subtitle concepts + a short 'briefly fills the screen' video test."""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
FR_DIR = os.path.join(ROOT, "输出", "字幕设计")
OUT = FR_DIR
FONT_DIR = os.path.join(BASE, "fonts")
W, H = 2560, 1080

BONE = (232, 224, 208)
BLOOD = (150, 22, 112)
DARKRED = (46, 16, 74)
BLACK = (8, 6, 8)
SILVER = (200, 196, 190)
PINK = (255, 111, 216)
LAV = (201, 167, 255)
VIOLET = (122, 60, 255)

F_BLACK = os.path.join(FONT_DIR, "PirataOne-Regular.ttf")
F_FRAKTUR = os.path.join(FONT_DIR, "UnifrakturCook-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, int(size))


def text_img(text, fontpath, size, color, tracking=0, stroke=0, stroke_color=BLACK,
             alpha=255, shadow=False):
    f = font(fontpath, size)
    widths = []
    for ch in text:
        bb = f.getbbox(ch)
        widths.append(bb[2] - bb[0] if bb[2] > bb[0] else int(size * 0.3))
    tw = int(sum(widths) + tracking * max(0, len(text) - 1)) + int(size * 0.4)
    th = int(size * 1.9)
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
    if anchor == "center":
        pos = (int(x - w / 2), int(y - h / 2))
    else:
        pos = (int(x), int(y))
    base.alpha_composite(layer, pos)


def scaled(img, fx=1.0, fy=1.0):
    return img.resize((max(1, int(img.size[0] * fx)), max(1, int(img.size[1] * fy))),
                      Image.LANCZOS)


def glow(layer, radius, strength=1.0, color=None):
    a = layer.getchannel("A").filter(ImageFilter.GaussianBlur(radius))
    col = color or (255, 255, 255)
    g = Image.new("RGBA", layer.size, col + (0,))
    g.putalpha(a.point(lambda v: int(min(255, v * strength))))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.alpha_composite(g)
    out.alpha_composite(layer)
    return out


def add_noise(img, amount=5, seed=1):
    rnd = np.random.default_rng(seed)
    a = np.asarray(img).astype(np.int16)
    n = rnd.normal(0, amount, (a.shape[0], a.shape[1], 1)).astype(np.int16)
    a[:, :, :3] = np.clip(a[:, :, :3] + n, 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def gothic_grade(frame, dark=0.52, desat=0.42, red=0.10, vignette=0.62):
    a = np.asarray(frame.convert("RGB")).astype(np.float32)
    l = 0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]
    a = (l[:, :, None] + (a - l[:, :, None]) * desat) * dark
    # cold violet shadows + pink-violet midtone glow (theme colours)
    mid = np.clip(1 - np.abs(l / 255 - 0.45), 0, 1) * 0.5
    a[:, :, 0] += red * 255 * mid * 0.55
    a[:, :, 2] += red * 255 * mid * 1.05 + 18 * np.clip(1 - l / 255, 0, 1)
    a[:, :, 1] *= 0.90
    # S curve
    x = np.clip(a, 0, 255) / 255
    y = 0.5 + (x - 0.5) * 1.22
    a = np.clip(y, 0, 1) * 255
    # vignette
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vd = ((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.58)) ** 2
    vig = np.clip(1.0 - vignette * np.clip(vd, 0, 1.6) ** 1.5, 0.10, 1.0)
    a = a * vig[:, :, None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def fog(size, color=(96, 46, 148), alpha=46, blur=90, seed=3):
    rnd = np.random.default_rng(seed)
    small = rnd.normal(0.5, 0.22, (size[1] // 40, size[0] // 40)).astype(np.float32)
    small = np.clip(small, 0, 1)
    img = Image.fromarray((small * 255).astype(np.uint8)).resize(size, Image.BICUBIC)
    img = img.filter(ImageFilter.GaussianBlur(blur))
    layer = Image.new("RGBA", size, color + (0,))
    layer.putalpha(img.point(lambda v: int(v * alpha / 255)))
    return layer


def drips(text_layer, color=PINK, n=26, seed=7):
    """Add blood-like drips from the bottom edge of a text layer."""
    rnd = random.Random(seed)
    mask = np.asarray(text_layer.getchannel("A"))
    h, w = mask.shape
    img = Image.new("RGBA", text_layer.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cols = np.where((mask > 60).any(axis=0))[0]
    if len(cols) == 0:
        return text_layer
    for _ in range(n):
        x = int(rnd.choice(cols))
        ys = np.where(mask[:, max(0, x - 1):x + 2] > 60)[0]
        if len(ys) == 0:
            continue
        y0 = int(ys.max())
        ln = rnd.randint(24, 150)
        wd = rnd.choice([2, 2, 3, 4, 5])
        for k in range(0, ln, 6):
            r = wd * (1 - k / max(1, ln))
            if r < 0.6:
                break
            d.ellipse([x - r, y0 + k, x + r, y0 + k + 7],
                      fill=color + (rnd.randint(50, 140),))
    out = text_layer.copy()
    out.alpha_composite(img)
    return out


def cross(d, cx, cy, size, color, alpha=160, width=3):
    d.line([(cx - size, cy), (cx + size, cy)], fill=color + (alpha,), width=width)
    d.line([(cx, cy - size * 0.6), (cx, cy + size)], fill=color + (alpha,), width=width)


def rules(d, y, color=BONE, alpha=70, width=2, inset=200):
    d.line([(inset, y), (W - inset, y)], fill=color + (alpha,), width=width)


def ornate_frame(d, color=BONE, alpha=60):
    # thin inner border + corner crosses
    m = 46
    d.rectangle([m, m, W - m, H - m], outline=color + (alpha,), width=2)
    for cx, cy in ((m, m), (W - m, m), (m, H - m), (W - m, H - m)):
        cross(d, cx, cy, 26, color, alpha=alpha + 40, width=2)


# ---------------------------------------------------------------- concepts
def load_frame(sec):
    return Image.open(os.path.join(FR_DIR, "_frame_%.1f.jpg" % sec)).convert("RGBA")


def g1(overlay_only=False):
    """G1 · full-bleed 'SHE?'"""
    base = load_frame(13.2)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # giant cross silhouette
    d.rectangle([W // 2 - 70, 0, W // 2 + 70, H], fill=(58, 22, 92, 44))
    d.rectangle([W // 2 - 620, 360, W // 2 + 620, 470], fill=(58, 22, 92, 36))

    # red rules
    rules(d, 90, BLOOD, 120, 3, 160)
    rules(d, 1000, BLOOD, 120, 3, 160)
    ornate_frame(d, BONE, 46)

    # shadow + main blackletter text (cropped by canvas => full bleed)
    t = text_img("SHE?", F_BLACK, 1500, BONE, tracking=-40, stroke=5, stroke_color=BLACK)
    t = t.rotate(-2, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", t.size, (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", t.size, VIOLET + (255,)), (0, 0), t.getchannel("A"))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    paste(layer, sh, W / 2 + 16, 566 + 22, alpha=0.85)
    t = drips(t, PINK, n=22, seed=5)
    t = glow(t, 18, 0.5, (255, 100, 235))
    paste(layer, t, W / 2, 566)

    # small fraktur
    who = text_img("Who Is", F_FRAKTUR, 150, BONE, tracking=8, stroke=2, stroke_color=BLACK)
    paste(layer, glow(rot(who, -2), 10, 0.6, (255, 120, 230)), 330, 190)
    sub = text_img("she", F_FRAKTUR, 110, PINK, tracking=6, stroke=2, stroke_color=BLACK)
    paste(layer, sub, W - 330, 900)

    if overlay_only:
        return layer

    base = gothic_grade(base)
    base.alpha_composite(fog(base.size, alpha=42, seed=2))
    base.alpha_composite(layer)
    # dust
    rnd = random.Random(9)
    dust = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dust)
    for _ in range(160):
        x, y = rnd.randint(0, W), rnd.randint(0, H)
        r = rnd.choice([1, 1, 2])
        dd.ellipse([x, y, x + r, y + r], fill=(220, 200, 180, rnd.randint(20, 70)))
    base.alpha_composite(dust)
    return add_noise(base, 6, 21)


def fit_text(text, fontpath, size, color=BONE, stroke=5, stroke_color=BLACK,
             target_w=None, target_h=None, tracking=-10):
    t = text_img(text, fontpath, size, color, tracking=tracking, stroke=stroke,
                 stroke_color=stroke_color)
    # crop to alpha
    bb = t.getbbox()
    if bb:
        t = t.crop(bb)
    fx = (target_w / t.size[0]) if target_w else 1.0
    fy = (target_h / t.size[1]) if target_h else 1.0
    return t.resize((max(1, int(t.size[0] * fx)), max(1, int(t.size[1] * fy))), Image.LANCZOS)


def g2(overlay_only=False):
    """G2 · single full-bleed line WHO IS SHE?"""
    base = load_frame(13.2)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    d.arc([-1200, -1600, W + 1200, 1600], 20, 160, fill=BONE + (30,), width=3)
    d.arc([-1000, -1400, W + 1000, 1400], 20, 160, fill=BLOOD + (46,), width=2)

    t = text_img("WHO IS SHE?", F_BLACK, 640, BONE, tracking=-18, stroke=6,
                 stroke_color=BLACK)
    bb = t.getbbox()
    if bb:
        t = t.crop(bb)
    t = t.resize((int(W * 1.10), int(t.size[1] * (W * 1.10) / t.size[0])), Image.LANCZOS)

    paste(layer, glow(t, 30, 0.55, (255, 100, 235)), W / 2, 520)
    sh = Image.new("RGBA", t.size, (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", t.size, VIOLET + (255,)), (0, 0), t.getchannel("A"))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    paste(layer, sh, W / 2 + 10, 542, alpha=0.85)
    t = drips(t, BLOOD, 20, seed=31)
    paste(layer, t, W / 2, 520)

    small = text_img("who is", F_FRAKTUR, 120, BONE, tracking=10, stroke=2,
                     stroke_color=BLACK)
    paste(layer, glow(rot(small, -3), 10, 0.55, (255, 110, 235)), 400, 130)
    small2 = text_img("she?", F_FRAKTUR, 130, PINK, tracking=8, stroke=2,
                      stroke_color=BLACK)
    paste(layer, small2, W - 420, 950)

    rules(d, 90, BLOOD, 110, 3, 160)
    rules(d, 1000, BLOOD, 110, 3, 160)
    cross(d, 120, 120, 26, BONE, 100)
    cross(d, W - 120, 120, 26, BONE, 100)
    cross(d, 120, H - 120, 26, BONE, 100)
    cross(d, W - 120, H - 120, 26, BONE, 100)

    if overlay_only:
        return layer
    base = gothic_grade(base, dark=0.46, desat=0.35, red=0.14, vignette=0.68)
    base.alpha_composite(fog(base.size, alpha=52, seed=4))
    base.alpha_composite(layer)
    return add_noise(base, 6, 22)

def g3(overlay_only=False):
    """G3 · LOVE with thorns"""
    base = load_frame(8.6)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    t = text_img("LOVE", F_FRAKTUR, 700, BONE, tracking=-20, stroke=6, stroke_color=BLACK)
    t = scaled(t, W / t.size[0] * 0.96, 1.0)
    t = t.rotate(-1, expand=True, resample=Image.BICUBIC)

    sh = Image.new("RGBA", t.size, (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", t.size, VIOLET + (255,)), (0, 0), t.getchannel("A"))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    paste(layer, sh, W / 2 + 12, 540 + 20, alpha=0.9)
    tx, ty = W / 2, 540

    # thorns: jagged branches around the word
    rnd = random.Random(13)
    thorn = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(thorn)
    for _ in range(26):
        x = rnd.randint(60, W - 60)
        y = rnd.randint(60, H - 60)
        pts = [(x, y)]
        for _ in range(4):
            x += rnd.randint(-70, 70)
            y += rnd.randint(-60, 60)
            pts.append((x, y))
        td.line(pts, fill=(34, 16, 56, rnd.randint(70, 150)), width=rnd.choice([2, 3]))
        # spikes
        for (px, py) in pts[1:]:
            td.line([(px, py), (px + rnd.randint(-18, 18), py + rnd.randint(-18, 18))],
                    fill=(52, 24, 86, 130), width=2)

    t = drips(t, PINK, 30, seed=17)
    t = glow(t, 26, 0.45, (220, 70, 235))
    paste(layer, thorn, W / 2, H / 2, alpha=0.75)
    paste(layer, t, tx, ty)

    small = text_img("she", F_FRAKTUR, 120, BONE, tracking=4, stroke=2, stroke_color=BLACK)
    paste(layer, glow(small, 10, 0.5, (255, 100, 235)), W - 260, 900)
    rules(d, 110, BLOOD, 110, 3, 200)
    rules(d, 980, BLOOD, 110, 3, 200)

    if overlay_only:
        return layer
    base = gothic_grade(base, dark=0.42, desat=0.30, red=0.18, vignette=0.72)
    base.alpha_composite(fog(base.size, alpha=60, seed=6))
    base.alpha_composite(layer)
    return add_noise(base, 6, 23)


def contact_sheet(paths, labels, out_path, cols=2):
    cw, ch, bar = 1280, 540, 36
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cw * cols, (ch + bar) * rows), (10, 9, 8))
    d = ImageDraw.Draw(sheet)
    f = font(r"C:\Windows\Fonts\msyhbd.ttc", 24)
    for i, (p, lab) in enumerate(zip(paths, labels)):
        im = Image.open(p).convert("RGB").resize((cw, ch), Image.LANCZOS)
        x = (i % cols) * cw
        y = (i // cols) * (ch + bar)
        sheet.paste(im, (x, y + bar))
        d.text((x + 18, y + 7), lab, font=f, fill=(238, 232, 222))
    sheet.save(out_path, quality=92)


def main():
    jobs = [
        ("G1_全屏血字_SHE.jpg", "G1 · 全屏血字「SHE?」", g1),
        ("G2_三行巨字_WHO_IS_SHE.jpg", "G2 · 三行满幅「WHO / IS / SHE?」", g2),
        ("G3_荆棘LOVE.jpg", "G3 · 荆棘「LOVE」", g3),
    ]
    paths, labels = [], []
    for name, lab, fn in jobs:
        img = fn()
        p = os.path.join(OUT, name)
        img.convert("RGB").save(p, quality=93)
        paths.append(p)
        labels.append(lab)
        print("rendered", name)
    contact_sheet(paths, labels, os.path.join(OUT, "哥特_方案总览.jpg"))
    # overlay for the video test
    ov = g1(overlay_only=True)
    ov.save(os.path.join(OUT, "_gothic_overlay_G1.png"))
    print("done")


if __name__ == "__main__":
    main()


