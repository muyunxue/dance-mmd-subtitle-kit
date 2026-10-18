# -*- coding: utf-8 -*-
"""Character-safe side-column NEON subtitles (fast version).

Only needs the dancer's bounding box per frame: diff mask at 1/4 resolution,
largest connected component, union bbox per lyric cue, then sidebar layout.
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import neon_wide as NW
import grade_ffmpeg as G

ROOT = os.path.dirname(BASE)
SRC = os.path.join(ROOT, "0001-4956 - 副本.mkv")
OUT = os.path.join(ROOT, "输出", "字幕小样")
FF = G.FF
W, H = 2560, 1080
QW, QH = 640, 270          # analysis resolution
FPS = 30
T0, T1 = 51.0, 66.4
KEYS = ("c1", "c2", "c3", "c4")
CUES = [(51.06, 54.55), (54.58, 58.10), (58.19, 61.70), (61.81, 66.20)]
BG = np.load(os.path.join(ROOT, "输出", "调色测试", "bg_half.npy")).astype(np.int16)
BGQ = np.asarray(Image.fromarray(BG.astype(np.uint8)).resize((QW, QH), Image.BILINEAR)).astype(np.int16)


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


def comp_label(m):
    """Largest 4-connected component, iterative scan with row runs (fast enough
    on 640x270)."""
    h, w = m.shape
    lab = np.zeros((h, w), np.int32)
    cur = 0
    sizes = [0]
    for y in range(h):
        x = 0
        while x < w:
            if m[y, x] and lab[y, x] == 0:
                cur += 1
                stack = [(y, x)]
                lab[y, x] = cur
                cnt = 0
                while stack:
                    cy, cx = stack.pop()
                    cnt += 1
                    for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                        if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and lab[ny, nx] == 0:
                            lab[ny, nx] = cur
                            stack.append((ny, nx))
                sizes.append(cnt)
            x += 1
    if cur == 0:
        return m
    return (lab == int(np.argmax(sizes))).astype(np.uint8)


def qmask(fr):
    q = np.asarray(Image.fromarray(fr).resize((QW, QH), Image.BILINEAR)).astype(np.int16)
    d = np.abs(q - BGQ).max(axis=2)
    m = (d > 38).astype(np.uint8)
    m = np.asarray(Image.fromarray(m * 255).filter(ImageFilter.MaxFilter(5))) > 127
    m = comp_label(m.astype(np.uint8))
    return m


def pass1():
    bounds = {k: [QW * 4, 0, QH * 4, 0] for k in KEYS}
    for i, fr in enumerate(read_frames()):
        t = T0 + i / FPS
        m = qmask(fr)
        ys, xs = np.where(m > 0)
        if len(xs) == 0:
            continue
        x0, x1 = xs.min() * 4, xs.max() * 4
        y0, y1 = ys.min() * 4, ys.max() * 4
        for ci, (a, b) in enumerate(CUES):
            if a - 0.05 <= t <= b + 0.05:
                k = KEYS[ci]
                bounds[k][0] = min(bounds[k][0], x0)
                bounds[k][1] = max(bounds[k][1], x1)
                bounds[k][2] = min(bounds[k][2], y0)
                bounds[k][3] = max(bounds[k][3], y1)
        if i % 120 == 0:
            print("pass1", i, flush=True)
    for k in KEYS:
        print(k, "bounds", bounds[k])
    return bounds


EL = []


def el(cue, text, side, y, fs, color, font, track, hollow=False, glow=None, ga=0xB4, anim="fade"):
    EL.append(dict(cue=cue, text=text, side=side, y=y, fs=fs, color=color, font=font,
                   track=track, hollow=hollow, glow=glow or NW.LAV, ga=ga, anim=anim))


# ---- content & design (original lyrics only, no Chinese) ----
el(0, "STEP", "L", 780, 172, NW.WHITE, "Microsoft YaHei Light", 8, anim="slam")
el(0, "ONTO THE STAGE", "L", 250, 44, NW.DIM, "Microsoft YaHei Light", 8, anim="rise")
el(0, "GOT THIS", "R", 250, 48, NW.LAV, "Microsoft YaHei Light", 10)
el(1, "息つけない", "L", 250, 70, NW.WHITE, "Microsoft YaHei", 4, glow=NW.PINK, ga=0x9C)
el(1, "mood", "L", 700, 162, NW.LAV, "Microsoft YaHei Light", 14, hollow=True, anim="slam")
el(1, "heartbeat", "R", 430, 46, NW.WHITE, "Microsoft YaHei Light", 8)
el(2, "feel the", "L", 250, 48, NW.DIM, "Microsoft YaHei Light", 8, anim="rise")
el(2, "fire", "L", 730, 160, NW.PINK, "Microsoft YaHei Light", 8,
   glow=NW.PINK, ga=0x78, anim="slam")
el(2, "baby", "R", 430, 46, NW.LAV, "Microsoft YaHei Light", 8)
el(3, "MAKING EVERYBODY GO", "L", 220, 34, NW.DIM, "Microsoft YaHei Light", 10)
el(3, "who is", "L", 620, 112, NW.WHITE, "Microsoft YaHei Light", 8, anim="slam")
el(3, "she?", "R", 600, 112, NW.PINK, "Microsoft YaHei Light", 8,
   glow=NW.PINK, ga=0x78, anim="slam")
el(3, "?", "R", 250, 70, NW.LAV, "Microsoft YaHei Light", 2)


def text_w(text, fs):
    cjk = sum(1 for ch in text if ord(ch) > 0x2E80)
    ascii_n = len(text) - cjk
    return cjk * fs * 1.06 + ascii_n * fs * 0.68


def layout(bounds):
    out = []
    for e in EL:
        k = KEYS[e["cue"]]
        bl, br, bt, bb = bounds[k]
        if e["side"] == "L":
            avail = bl - 50
            w = text_w(e["text"], e["fs"])
            if w > avail:
                e = dict(e, fs=max(24, int(e["fs"] * avail / w)))
                w = text_w(e["text"], e["fs"])
            x = int(max(40 + w / 2, min(avail - w / 2 - 10, avail / 2)))
        else:
            avail = W - (br + 50)
            w = text_w(e["text"], e["fs"])
            if w > avail:
                e = dict(e, fs=max(24, int(e["fs"] * avail / w)))
                w = text_w(e["text"], e["fs"])
            x = int(min(W - 30 - w / 2, max(br + 50 + w / 2 + 10, W - avail / 2)))
        out.append(dict(e, x=x))
    return out


def box_of(text, x, y, fs, pad=10):
    w = text_w(text, fs)
    return (x - w / 2 - pad, y - fs * 0.66 - pad, x + w / 2 + pad, y + fs * 0.66 + pad)


def verify(plist):
    worst, worst_info = 0, {}
    for i, fr in enumerate(read_frames()):
        t = T0 + i / FPS
        m = qmask(fr)
        for ci, (a, b) in enumerate(CUES):
            if not (a - 0.05 <= t <= b + 0.05):
                continue
            for e in [p for p in plist if p["cue"] == ci]:
                x0, y0, x1, y1 = box_of(e["text"], e["x"], e["y"], e["fs"])
                qx0, qy0 = max(0, int(x0) // 4), max(0, int(y0) // 4)
                qx1, qy1 = min(QW, int(x1) // 4), min(QH, int(y1) // 4)
                if qx1 <= qx0 or qy1 <= qy0:
                    continue
                h = int(m[qy0:qy1, qx0:qx1].sum())
                if h > worst:
                    worst, worst_info = h, (e["text"], x0, y0, x1, y1)
    print("VERIFY worst hit =", worst, worst_info)
    return worst


def build_ass(plist):
    NW.EV.clear()
    starts = [[0.0, 0.8, 1.7], [0.0, 0.5, 1.5], [0.0, 0.8, 1.8], [0.0, 1.3, 1.5, 2.4]]
    idx = {}
    for e in plist:
        ci = e["cue"]
        idx[ci] = idx.get(ci, 0)
        st = CUES[ci][0] + starts[ci][idx[ci] % len(starts[ci])]
        idx[ci] += 1
        NW.neon(st, CUES[ci][1] - 0.04, e["text"], e["x"], e["y"], e["fs"],
                color=e["color"], font=e["font"], track=e["track"],
                anim=e["anim"], hollow=e["hollow"], glow=e["glow"], glow_a=e["ga"])
    NW.EV.sort(key=lambda x: int(x.split(",")[0].split(":")[1]))
    return NW.header() + "\n".join(NW.EV) + "\n"


def main():
    bounds = pass1()
    plist = layout(bounds)
    worst = verify(plist)
    for _ in range(3):
        if worst == 0:
            break
        for e in plist:
            e["fs"] = max(24, int(e["fs"] * 0.85))
        print("shrink & re-verify")
        worst = verify(plist)
    for e in plist:
        print("c%d %-22s %s x=%d y=%d fs=%d"
              % (e["cue"] + 1, e["text"], e["side"], e["x"], e["y"], e["fs"]))
    ass = build_ass(plist)
    with open(os.path.join(OUT, "NEON_avoid_15s.ass"), "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(ass)
    base = os.path.join(OUT, "_base_graded_15s.mp4")
    out = os.path.join(OUT, "字幕小样_避让_15s.mp4")
    cmd = [FF, "-v", "error", "-y", "-i", base, "-vf", "ass=NEON_avoid_15s.ass",
           "-c:v", "libx264", "-preset", "medium", "-crf", "16",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    p = subprocess.run(cmd, cwd=OUT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    print("burn", p.returncode, (p.stderr or "")[-300:])
    times = (52.2, 53.4, 56.3, 59.8, 61.4, 64.6)
    files = []
    for t in times:
        fp = os.path.join(OUT, "_av_%.1f.jpg" % t)
        subprocess.run([FF, "-v", "error", "-ss", "%.2f" % (t - T0), "-i", out,
                        "-frames:v", "1", "-q:v", "2", "-y", fp], capture_output=True)
        files.append(fp)
    ims = [Image.open(f).convert("RGB") for f in files]
    tw, th = 1280, 540
    sheet = Image.new("RGB", (tw * 2, th * 3), (8, 7, 12))
    for i, im in enumerate(ims):
        sheet.paste(im.resize((tw, th), Image.LANCZOS), ((i % 2) * tw, (i // 2) * th))
    sheet.save(os.path.join(OUT, "小样_避让_关键帧.jpg"), quality=90)
    print("done", out)


if __name__ == "__main__":
    main()

