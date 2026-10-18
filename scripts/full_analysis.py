# -*- coding: utf-8 -*-
"""Full-length prep: background plate + per-cue character bbox for the 165s MMD video."""
import json
import os
import subprocess
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
SRC = r"D:\mmd.mp4\0002-4956.mkv"
OUT = os.path.join(ROOT, "输出", "S4S6_完整版")
FF = r"C:\Users\35530\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
FPS = 30
W, H = 2560, 1080
QW, QH = 640, 270
DUR = 165.166

# LRC absolute times (from 字幕/[by维尔日记].txt)
LRC = [
    (7.969, "I feel it silence gettin' deeper 息のむ瞬間"),
    (15.186, "弾けそう I know I'm gonna be the girl in the fire"),
    (20.408, "(We don't think twice)"),
    (21.626, "I guess you'll never know"),
    (23.857, "灰の中に咲く miracle 高鳴る鼓動は magical"),
    (30.942, "底なしにハマる 3 2 1 who is she?"),
    (36.892, "When I walk onto the stage yeah I got this"),
    (40.366, "息が燃え出す キュンと heartbeat"),
    (44.003, "Come around baby you can come and see me"),
    (47.577, "Making everybody go who is she?"),
    (51.179, "When I step onto the stage yeah I got this"),
    (54.698, "息つけない mood キュンと heartbeat"),
    (58.309, "Feel the fire baby you can come and see me"),
    (61.926, "Making everybody go who is she?"),
    (68.240, "I can be hot I can be cold"),
    (69.910, "Born to be X nobody knows"),
    (71.731, "妄想 trigger gotta just breathe in"),
    (74.127, "I'm the whole damn show yeah"),
    (75.746, "Who's the one that takes the reset"),
    (77.591, "また shhh ってなるわ burn"),
    (79.457, "集中して燃えて watch me now now"),
    (82.139, "I guess you'll never know"),
    (84.834, "壊れて花咲く miracle 心が目覚める magical"),
    (91.944, "奥深く刺さる 3 2 1 who is she?"),
    (97.768, "When I walk onto the stage yeah I got this"),
    (101.349, "息が燃え出す キュンと heartbeat"),
    (104.854, "Come around baby you can come and see me"),
    (108.440, "Making everybody go who is she?"),
    (126.470, "When I move onto the stage yeah I got this"),
    (129.985, "息が燃え出す キュンと heartbeat"),
    (133.577, "Feel the vibe baby 感じたら breathing"),
    (137.107, "Making everybody go who is she?"),
    (140.677, "When I move onto the stage yeah I got this"),
    (144.341, "息つけない mood キュンと heartbeat"),
    (147.939, "Feel the vibe baby 感じたら breathing"),
    (151.454, "Making everybody go who is she"),
]


def build_bg():
    path = os.path.join(OUT, "_bg_q.npy")
    if os.path.exists(path):
        return np.load(path)
    cmd = [FF, "-v", "error", "-i", SRC, "-vf", "fps=0.5,scale=%d:%d" % (QW, QH),
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    fsz = QW * QH * 3
    frames = []
    while True:
        buf = p.stdout.read(fsz)
        if len(buf) < fsz:
            break
        frames.append(np.frombuffer(buf, np.uint8).reshape(QH, QW, 3))
    p.stdout.close(); p.wait()
    bg = np.median(np.stack(frames), axis=0).astype(np.uint8)
    np.save(path, bg)
    print("bg frames", len(frames))
    return bg


def read_frames():
    cmd = [FF, "-v", "error", "-i", SRC, "-vf", "scale=%d:%d" % (QW, QH),
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    fsz = QW * QH * 3
    try:
        while True:
            buf = p.stdout.read(fsz)
            if len(buf) < fsz:
                break
            yield np.frombuffer(buf, np.uint8).reshape(QH, QW, 3)
    finally:
        p.stdout.close(); p.wait()


def largest_comp_bbox(mask):
    """mask: bool 160x68 -> bbox in that small grid."""
    h, w = mask.shape
    lab = np.zeros((h, w), np.int32)
    cur = 0
    best = (0, 0, 0, 0, 0)
    for y in range(h):
        for x in range(w):
            if mask[y, x] and lab[y, x] == 0:
                cur += 1
                q = deque([(y, x)])
                lab[y, x] = cur
                cnt = 0
                x0 = x1 = x; y0 = y1 = y
                while q:
                    cy, cx = q.popleft()
                    cnt += 1
                    x0 = min(x0, cx); x1 = max(x1, cx)
                    y0 = min(y0, cy); y1 = max(y1, cy)
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and lab[ny, nx] == 0:
                            lab[ny, nx] = cur
                            q.append((ny, nx))
                if cnt > best[0]:
                    best = (cnt, x0, x1, y0, y1)
    return best


def main():
    os.makedirs(OUT, exist_ok=True)
    bg = build_bg()
    # cue windows (end = next start - 0.15, capped at +6.5; last end 155.2)
    cues = []
    for i, (t, text) in enumerate(LRC):
        if i + 1 < len(LRC):
            end = min(LRC[i + 1][0] - 0.15, t + 6.5)
        else:
            end = 155.2
        end = max(end, t + 1.6)
        cues.append(dict(i=i, start=t, end=round(end, 3), text=text,
                         bbox=[W, 0, H, 0]))
    # assign frames
    for fi, fr in enumerate(read_frames()):
        t = fi / FPS
        d = np.abs(fr.astype(np.int16) - bg.astype(np.int16)).max(axis=2)
        m = (d > 38).astype(np.uint8)
        m = np.asarray(Image.fromarray(m * 255).filter(ImageFilter.MaxFilter(5))) > 127
        small = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                           .resize((QW // 4, QH // 4), Image.BOX)) > 60
        cnt, x0, x1, y0, y1 = largest_comp_bbox(small)
        if cnt == 0:
            continue
        bx0, bx1, by0, by1 = x0 * 16, x1 * 16 + 16, y0 * 16, y1 * 16 + 16
        for c in cues:
            if c["start"] - 0.1 <= t <= c["end"] + 0.1:
                c["bbox"][0] = min(c["bbox"][0], bx0)
                c["bbox"][1] = max(c["bbox"][1], bx1)
                c["bbox"][2] = min(c["bbox"][2], by0)
                c["bbox"][3] = max(c["bbox"][3], by1)
        if fi % 600 == 0:
            print("frame", fi, flush=True)
    with open(os.path.join(OUT, "cues.json"), "w", encoding="utf-8") as f:
        json.dump(cues, f, ensure_ascii=False, indent=1)
    print("cues saved", len(cues))
    for c in cues:
        b = c["bbox"]
        print("%2d %6.2f-%6.2f bbox %4d-%4d %4d-%4d" % (c["i"], c["start"], c["end"],
                                                       b[0], b[1], b[2], b[3]))


if __name__ == "__main__":
    main()
