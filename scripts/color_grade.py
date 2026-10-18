# -*- coding: utf-8 -*-
"""Subject-aware color grade test for the MMD video (5s sample).

Pipeline:
1) estimate the static-stage background (temporal median, half resolution)
2) per frame: background subtraction -> character mask (soft, feathered)
3) grade: character (lift / sat / sharpen / skin / bloom / rim) vs background
   (dim / desaturate / cool / soften) composited through the mask
4) 5s encodes: original, subtle grade, stronger grade + comparison stacks
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
SRC = os.path.join(ROOT, "0001-4956 - 副本.mkv")
OUT = os.path.join(ROOT, "输出", "调色测试")

FFMPEG = r"C:\Users\35530\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
W, H = 2560, 1080
HW, HH = W // 2, H // 2
FPS = 30
START, DUR = 62.0, 5.0
NFRAMES = int(DUR * FPS)

MSYH = r"C:\Windows\Fonts\msyh.ttc"


# ------------------------------------------------------------------ utils ---
def ff_read_segment(start=START, dur=DUR):
    cmd = [FFMPEG, "-v", "error", "-ss", "%.3f" % start, "-t", "%.3f" % dur,
           "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    fsz = W * H * 3
    try:
        for _ in range(NFRAMES):
            buf = p.stdout.read(fsz)
            if len(buf) < fsz:
                break
            yield np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    finally:
        p.stdout.close()
        p.wait()


def build_background(sample_step=2.0):
    """Median of sampled frames across the whole clip (background plate)."""
    cmd = [FFMPEG, "-v", "error", "-i", SRC, "-vf",
           "fps=1/%.2f,scale=%d:%d" % (sample_step, HW, HH),
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    fsz = HW * HH * 3
    frames = []
    while True:
        buf = p.stdout.read(fsz)
        if len(buf) < fsz:
            break
        frames.append(np.frombuffer(buf, np.uint8).reshape(HH, HW, 3))
    p.stdout.close()
    p.wait()
    print("bg samples", len(frames))
    return np.median(np.stack(frames), axis=0).astype(np.uint8)


# ------------------------------------------------------------------ grade ---
def _blur(arr, r):
    return np.asarray(Image.fromarray(arr).filter(ImageFilter.GaussianBlur(r)))


def _luma(img):
    return (0.2126 * img[:, :, 0] + 0.7152 * img[:, :, 1] + 0.0722 * img[:, :, 2])


def _saturation(img, k):
    l = _luma(img)[:, :, None]
    return np.clip(l + (img - l) * k, 0, 255)


def _s_curve(img, contrast=0.06, lift=6.0):
    x = img.astype(np.float32) / 255.0
    y = 0.5 + (x - 0.5) * (1.0 + contrast * 2.0)
    y = y + (lift / 255.0) * (1.0 - x) ** 2
    return np.clip(y * 255.0, 0, 255).astype(np.float32)


def _warm(img, r, g, b):
    out = img.copy()
    out[:, :, 0] += r
    out[:, :, 1] += g
    out[:, :, 2] += b
    return np.clip(out, 0, 255)


def _skin_mask(img):
    """Rough skin selector in YCbCr (works on clean CG colors)."""
    r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    y = 0.299 * r + 0.587 * g + 0.114 * b
    cb = 128 - 0.168736 * r - 0.331264 * g + 0.5 * b
    cr = 128 + 0.5 * r - 0.418688 * g - 0.081312 * b
    m = (cr > 136) & (cr < 176) & (cb > 90) & (cb < 128) & (y > 60) & (r > g)
    return m.astype(np.float32)


def character_mask(frame):
    small = np.asarray(Image.fromarray(frame).resize((HW, HH), Image.BILINEAR))
    diff = np.abs(small.astype(np.int16) - bg_half.astype(np.int16)).max(axis=2)
    m = (diff > 20).astype(np.uint8)
    m_img = Image.fromarray(m * 255)
    m_img = m_img.filter(ImageFilter.MaxFilter(7))
    m_img = m_img.filter(ImageFilter.MinFilter(5))
    m_img = m_img.filter(ImageFilter.GaussianBlur(6))
    soft = np.asarray(m_img.resize((W, H), Image.BILINEAR)).astype(np.float32) / 255.0
    return np.clip(soft * 1.25, 0, 1)


def grade(frame, strong=False):
    img = frame.astype(np.float32)
    m = character_mask(frame)[:, :, None]
    # ---------------- background ----------------
    bgl = _saturation(img, 0.62 if strong else 0.72)
    bgl = _s_curve(bgl, 0.03, 2.0)
    bgl = bgl * (0.80 if strong else 0.87)
    bgl = _warm(bgl, -5, 1, 9)
    bgl = _blur(bgl.astype(np.uint8), 1.1).astype(np.float32)
    # vignette on background
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vd = ((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.60)) ** 2
    vig = np.clip(1.0 - (0.42 if strong else 0.32) * np.clip(vd, 0, 1.4) ** 1.4, 0.2, 1.0)
    bgl = bgl * vig[:, :, None]

    # ---------------- character ----------------
    ch = img * (1.10 if strong else 1.06)
    ch = _saturation(ch, 1.16 if strong else 1.09)
    # local contrast / sharpen
    sharp = np.asarray(Image.fromarray(np.clip(ch, 0, 255).astype(np.uint8))
                       .filter(ImageFilter.UnsharpMask(radius=2, percent=115 if strong else 80,
                                                       threshold=2))).astype(np.float32)
    ch = sharp
    ch = _s_curve(ch, 0.05, 3.0)
    # skin warmth
    sm = _skin_mask(frame)[:, :, None]
    ch = _warm(ch, 4, 2, -1) * sm + ch * (1 - sm)
    # bloom inside character highlights
    lum = _luma(ch)
    bright = np.clip(lum - 150, 0, 255) / 105.0
    bm = (bright * m[:, :, 0])[:, :, None] * ch
    bloom = _blur(bm.astype(np.uint8), 92 if False else 16).astype(np.float32)
    ch = np.clip(ch + bloom * (0.55 if strong else 0.35), 0, 255)

    # rim light from mask edge
    edge = np.clip(m[:, :, 0] - _blur(m[:, :, 0].astype(np.uint8), 5) * 1.0, 0, 1)
    rim = _blur((edge * 255).astype(np.uint8), 7).astype(np.float32) / 255.0
    rim_col = np.array([255, 205, 190], np.float32)
    ch = np.clip(ch + rim[:, :, None] * rim_col * (0.55 if strong else 0.35), 0, 255)

    out = bgl * (1 - m) + ch * m
    # film grain
    noise = np.random.normal(0, 2.2 if strong else 1.8, (H, W, 1))
    out = np.clip(out + noise, 0, 255)
    return out.astype(np.uint8)


# --------------------------------------------------------------- renders ----
def encode_segment(path, strong):
    tmp = path + ".tmp"
    cmd = [FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "16",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    for fr in ff_read_segment():
        p.stdin.write(grade(fr, strong).tobytes())
    p.stdin.close()
    err = p.stderr.read()
    p.wait()
    print("encode", os.path.basename(path), p.returncode, (err or b"").decode("utf-8", "replace")[-200:])


def make_original():
    out = os.path.join(OUT, "原片_5s.mp4")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", "%.3f" % START,
                    "-t", "%.3f" % DUR, "-i", SRC,
                    "-c:v", "libx264", "-preset", "medium", "-crf", "16",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
                   capture_output=True)
    print("original ok")
    return out


def stack_compare(a, b, out, label_a, label_b):
    """vertical stack: top = a, bottom = b (both scaled to 1280x540)."""
    w, h = 1280, 540
    ass = os.path.join(OUT, "_cmp.ass")
    with open(ass, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write("""[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 1080
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: L,Microsoft YaHei,30,&H00F4F1EA,&H000000FF,&H00100806,&H00000000,0,0,0,0,100,100,2,0,1,2,1,7,60,60,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.00,L,,0,0,0,,{\\pos(40,18)}%s
Dialogue: 0,0:00:00.00,0:00:05.00,L,,0,0,0,,{\\pos(40,558)}%s
""" % (label_a, label_b))
    cmd = [FFMPEG, "-v", "error", "-y", "-i", a, "-i", b,
           "-filter_complex",
           "[0:v]scale=%d:%d[a];[1:v]scale=%d:%d[b];[a][b]vstack=inputs=2,ass=%s[v]"
           % (w, h, w, h, "_cmp.ass"),
           "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    p = subprocess.run(cmd, cwd=OUT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    print("stack", os.path.basename(out), p.returncode, (p.stderr or "")[-200:])


def stills(orig, graded, strong_graded):
    cmd = [FFMPEG, "-v", "error", "-y"]
    # extract frames from each video at t=1..4
    made = {}
    for name, path in (("o", orig), ("g", graded), ("s", strong_graded)):
        files = []
        for k, t in enumerate((1.0, 2.5, 4.0)):
            f = os.path.join(OUT, "_still_%s_%d.jpg" % (name, k))
            subprocess.run([FFMPEG, "-v", "error", "-ss", "%.2f" % t, "-i", path,
                            "-frames:v", "1", "-q:v", "2", "-y", f], capture_output=True)
            files.append(f)
        made[name] = files
    # comparison sheet: rows = moments, cols = original / subtle / strong
    cells = []
    for k in range(3):
        row = [Image.open(made[n][k]).convert("RGB").resize((640, 270), Image.LANCZOS)
               for n in ("o", "g", "s")]
        cells.append(row)
    sheet = Image.new("RGB", (1920, 270 * 3 + 30), (12, 10, 9))
    for r, row in enumerate(cells):
        for c, im in enumerate(row):
            sheet.paste(im, (c * 640, r * (270 + 10) + 10))
    draw = ImageDraw.Draw(sheet)
    f = ImageFont.truetype(MSYH, 22)
    for c, lab in enumerate(("原片", "调色 A · 自然", "调色 B · 强化")):
        draw.text((c * 640 + 16, 6), lab, font=f, fill=(240, 240, 240))
    sheet.save(os.path.join(OUT, "对比_关键帧.jpg"), quality=92)
    print("still sheet ok")


def mask_debug():
    """One frame: original | mask overlay | graded."""
    frame = next(ff_read_segment())
    m = character_mask(frame)
    arr = frame.copy()
    edge = np.clip(m - _blur((m * 255).astype(np.uint8), 3) / 255.0, 0, 1)
    arr[edge > 0.15] = [60, 230, 240]
    ov = Image.fromarray(arr).resize((853, 360), Image.LANCZOS)
    o = Image.fromarray(frame).resize((853, 360), Image.LANCZOS)
    g = Image.fromarray(grade(frame, False)).resize((853, 360), Image.LANCZOS)
    sheet = Image.new("RGB", (853 * 3 + 20, 360 + 40), (12, 10, 9))
    draw = ImageDraw.Draw(sheet)
    f = ImageFont.truetype(MSYH, 22)
    for i, (im, lab) in enumerate(((o, "原片"), (ov, "人物 mask"), (g, "调色后"))):
        sheet.paste(im, (i * (853 + 10), 34))
        draw.text((i * (853 + 10) + 8, 6), lab, font=f, fill=(240, 240, 240))
    sheet.save(os.path.join(OUT, "分析_人物mask.jpg"), quality=92)
    print("mask debug ok")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    bg_half = build_background()
    np.save(os.path.join(OUT, "bg_half.npy"), bg_half)
    mask_debug()
    orig = make_original()
    a = os.path.join(OUT, "调色A_自然_5s.mp4")
    b = os.path.join(OUT, "调色B_强化_5s.mp4")
    encode_segment(a, False)
    encode_segment(b, True)
    stack_compare(orig, a, os.path.join(OUT, "对比_A_自然_5s.mp4"), "原片", "调色 A·自然")
    stack_compare(a, b, os.path.join(OUT, "对比_AB_5s.mp4"), "调色 A·自然", "调色 B·强化")
    stills(orig, a, b)
    print("DONE")
