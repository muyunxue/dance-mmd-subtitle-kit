# -*- coding: utf-8 -*-
"""Analyse character occupancy for 0:51-1:06.4 and find subtitle-free columns."""
import os
import subprocess
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
SRC = os.path.join(ROOT, "0001-4956 - 副本.mkv")
OUT = os.path.join(ROOT, "输出", "字幕小样")
FF = r"C:\Users\35530\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
MSYH = r"C:\Windows\Fonts\msyh.ttc"

W, H = 2560, 1080
HW, HH = W // 2, H // 2
FPS = 30
T0, T1 = 51.0, 66.4
N = int(round((T1 - T0) * FPS))

bg = np.load(os.path.join(ROOT, "输出", "调色测试", "bg_half.npy"))

# cue windows in song time
CUES = [
    ("c1", 51.06, 54.55),
    ("c2", 54.58, 58.10),
    ("c3", 58.19, 61.70),
    ("c4", 61.81, 66.20),
]


def read_frames():
    cmd = [FF, "-v", "error", "-ss", "%.3f" % T0, "-t", "%.3f" % (T1 - T0), "-i", SRC,
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    fsz = W * H * 3
    try:
        while True:
            buf = p.stdout.read(fsz)
            if len(buf) < fsz:
                break
            yield np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    finally:
        p.stdout.close()
        p.wait()


def fill_holes(m):
    h, w = m.shape
    inv = (m == 0).astype(np.uint8)
    seen = np.zeros_like(inv)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if inv[y, x] and not seen[y, x]:
                seen[y, x] = 1
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if inv[y, x] and not seen[y, x]:
                seen[y, x] = 1
                q.append((y, x))
    while q:
        cy, cx = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < h and 0 <= nx < w and inv[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = 1
                q.append((ny, nx))
    return (m.astype(bool) | (inv.astype(bool) & (seen == 0))).astype(np.uint8)


def mask_frame(fr_small):
    d = np.abs(fr_small.astype(np.int16) - bg.astype(np.int16)).max(axis=2)
    m = (d > 30).astype(np.uint8)
    mi = Image.fromarray(m * 255).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(3))
    m = (np.asarray(mi) > 127).astype(np.uint8)
    # always keep a central body core (median background hides the torso)
    yy, xx = np.mgrid[0:HH, 0:HW]
    core = (((xx - HW * 0.49) / (HW * 0.115)) ** 2 + ((yy - HH * 0.55) / (HH * 0.30)) ** 2) <= 1.0
    m = (m | core.astype(np.uint8))
    m = fill_holes(m)
    mi = Image.fromarray(m * 255).filter(ImageFilter.GaussianBlur(5))
    return np.asarray(mi).astype(np.float32) / 255.0


def main():
    union = np.zeros((HH, HW), np.float32)
    cue_masks = {k: np.zeros((HH, HW), np.float32) for k, _, _ in CUES}
    for i, fr in enumerate(read_frames()):
        small = np.asarray(Image.fromarray(fr).resize((HW, HH), Image.BILINEAR))
        m = mask_frame(small)
        union = np.maximum(union, m)
        t = T0 + i / FPS
        for k, a, b in CUES:
            if a <= t <= b:
                cue_masks[k] = np.maximum(cue_masks[k], m)
        if i % 60 == 0:
            print("frame", i, flush=True)
    np.savez_compressed(os.path.join(OUT, "occ_union.npz"),
                        union=union, **{k: v for k, v in cue_masks.items()})
    # reports
    for k, a, b in CUES:
        m = cue_masks[k]
        ys, xs = np.where(m > 0.5)
        if len(xs) == 0:
            print(k, "empty")
            continue
        print(k, "bbox x %d-%d y %d-%d" % (xs.min() * 2, xs.max() * 2, ys.min() * 2, ys.max() * 2))
        # free left / right widths at several y bands
        for y0, y1 in ((100, 300), (300, 600), (600, 900), (900, 1060)):
            band = m[y0 // 2:y1 // 2]
            cols = band.max(axis=0)
            free = np.where(cols < 0.5)[0]
            left = free[free < HW // 2]
            right = free[free > HW // 2]
            print("   y%d-%d  left free max x=%s  right free min x=%s"
                  % (y0, y1,
                     (left.max() * 2 if len(left) else -1),
                     (right.min() * 2 if len(right) else -1)))
    # visualise union
    ov = None
    base_fr = next(read_frames())
    arr = base_fr.astype(np.float32) * 0.45
    mu = np.repeat(union[:, :, None], 3, axis=2)
    mu_full = np.asarray(Image.fromarray((mu * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR))
    arr = arr + (mu_full / 255.0)[:, :, None] * np.array([255, 60, 40]) * 0.55
    Image.fromarray(arr.astype(np.uint8)).save(os.path.join(OUT, "分析_占用区域.jpg"), quality=88)
    print("saved union")


if __name__ == "__main__":
    main()
