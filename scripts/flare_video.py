# -*- coding: utf-8 -*-
"""Render the FLARE sample: generated stage background + ASS type, piped to ffmpeg."""
import os
import subprocess
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flare
import build as B

SAMPLES = os.path.join(B.ROOT, "输出", "样片_炸裂版")
FF = B.FFMPEG
FPS = 30

DUR = flare.SAMPLE_END - flare.SAMPLE_START
NFRAMES = int(round(DUR * FPS))
BEAT = flare.BEAT
HITS = [(48.94, 0.9), (49.37, 0.7), (58.88, 1.0), (63.30, 0.7), (66.55, 1.0)]


def _gradient(w, h, top, bottom):
    im = np.zeros((h, w, 3), dtype=np.float32)
    t = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
    for c in range(3):
        im[:, :, c] = (top[c] + (bottom[c] - top[c]) * t)
    return im


def make_base(w, h):
    im = _gradient(w, h, (27, 17, 13), (5, 4, 4))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = w * 0.5, h * 0.36
    d2 = ((xx - cx) / (w * 0.55)) ** 2 + ((yy - cy) / (h * 0.55)) ** 2
    warm = np.exp(-d2 * 1.9)[:, :, None] * np.array([24, 13, 8], np.float32)
    im = im + warm
    vd = ((xx - w / 2) / (w * 0.62)) ** 2 + ((yy - h / 2) / (h * 0.62)) ** 2
    vig = np.clip(1.0 - 0.66 * np.clip(vd, 0, 1.3) ** 1.5, 0.08, 1.0).astype(np.float32)
    return im, vig, xx, yy


def glow_layer(w, h, spots):
    """spots: [(cx, cy, rx, ry, amp, color)] in full-res coords; computed low-res."""
    lw, lh = w // 4, h // 4
    yy, xx = np.mgrid[0:lh, 0:lw].astype(np.float32)
    out = np.zeros((lh, lw, 3), dtype=np.float32)
    for (cx, cy, rx, ry, amp, color) in spots:
        d2 = ((xx - cx / 4.0) / (rx / 4.0)) ** 2 + ((yy - cy / 4.0) / (ry / 4.0)) ** 2
        g = np.exp(-d2 * 2.0) * amp
        out += g[:, :, None] * np.array(color, np.float32)
    img = Image.fromarray(np.clip(out, 0, 255).astype("uint8"))
    img = img.resize((w, h), Image.BILINEAR)
    return np.asarray(img, dtype=np.float32)


def gen_frames(key, w, h):
    base, vig, xx, yy = make_base(w, h)
    yyf = (yy / h)
    for i in range(NFRAMES):
        t = flare.SAMPLE_START + i / float(FPS)
        rel = t - flare.SAMPLE_START
        # moving warm spotlights
        a1 = 2 * np.pi * rel / 11.0
        a2 = 2 * np.pi * rel / 7.3
        s1 = (w * (0.50 + 0.22 * np.sin(a1)), h * (0.34 + 0.10 * np.sin(a2)),
              w * 0.30, h * 0.27, 0.70, (128, 70, 32))
        s2 = (w * (0.42 + 0.18 * np.sin(a2 + 1.7)), h * (0.62 + 0.12 * np.cos(a1)),
              w * 0.28, h * 0.24, 0.46, (98, 46, 24))
        s3 = (w * (0.55 + 0.10 * np.cos(a1 * 0.6)), h * (0.20 + 0.08 * np.sin(a2 * 0.8)),
              w * 0.22, h * 0.20, 0.24, (64, 46, 32))
        s4 = (w * (0.09 + 0.05 * np.sin(a2 * 0.7)), h * (0.55 + 0.12 * np.cos(a1 * 0.8)),
              w * 0.17, h * 0.40, 0.30, (24, 66, 92))
        glows = glow_layer(w, h, [s1, s2, s3, s4])

        # beat breathing
        phase = (rel % BEAT) / BEAT
        beat_env = np.exp(-phase * 8.0) * 0.035
        # section hits
        hit = 0.0
        for (ht, amp) in HITS:
            dt = rel - (ht - flare.SAMPLE_START)
            if 0.0 <= dt < 1.2:
                hit += amp * np.exp(-dt / 0.16) * 0.10

        frame = base + glows * (1.0 + hit * 0.8)
        frame = frame * (1.0 + beat_env + hit)
        frame = frame * vig[:, :, None]

        # slow vertical light sweep
        sweep_y = (rel * 0.35) % 1.25
        sweep = np.exp(-(((yyf[:, 0] - sweep_y + 0.5) % 1.0 - 0.5) ** 2) / 0.0008)
        frame += sweep[:, None, None] * np.array([16, 9, 5], np.float32) * 0.45

        # grain
        noise = np.random.randint(-7, 8, (h, w, 1), dtype=np.int16).astype(np.float32)
        frame = frame + noise * 0.45

        yield np.clip(frame, 0, 255).astype(np.uint8)


def render_sample(key, crf=19):
    w, h = {"16x9": (1920, 1080), "9x16": (1080, 1920)}[key]
    ass_path = os.path.join(SAMPLES, "FLARE_小样_%s.ass" % key)
    if not os.path.exists(ass_path):
        flare.main()
    # libass filter path must be ASCII + relative; shift the ASS so that
    # SAMPLE_START becomes 0 and frames keep their normal PTS
    tmp_ass_name = "_flare_%s.ass" % key
    with open(ass_path, encoding="utf-8-sig") as f:
        ass_text = f.read()
    with open(os.path.join(SAMPLES, tmp_ass_name), "w", encoding="utf-8-sig", newline="\n") as g:
        g.write(B.shift_ass(ass_text, flare.SAMPLE_START))
    out_name = "FLARE_炸场版_小样_%s.mp4" % key
    out_path = os.path.join(SAMPLES, out_name)
    cmd = [FF, "-v", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (w, h),
           "-r", str(FPS), "-i", "-",
           "-vf", "ass=%s,format=yuv420p" % tmp_ass_name,
           "-frames:v", str(NFRAMES), "-c:v", "libx264", "-preset", "medium",
           "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           out_name]
    log_path = os.path.join(SAMPLES, "_render_%s.log" % key)
    log = open(log_path, "wb")
    p = subprocess.Popen(cmd, cwd=SAMPLES, stdin=subprocess.PIPE, stderr=log)
    try:
        for k, frame in enumerate(gen_frames(key, w, h)):
            p.stdin.write(frame.tobytes())
            if k % 120 == 0:
                print("frame", k, "/", NFRAMES, flush=True)
    except (BrokenPipeError, OSError) as e:
        print("PIPE ERR", e)
    p.stdin.close()
    p.wait()
    log.close()
    err = open(log_path, encoding="utf-8", errors="replace").read()
    ok = p.returncode == 0 and os.path.getsize(out_path) > 10000
    print("RENDER", key, "rc", p.returncode, "ok", ok, err[-400:])
    return out_path if ok else None


def stills_from_video(key):
    ass_name = "FLARE_小样_%s.ass" % key
    src = os.path.join(SAMPLES, "FLARE_炸场版_小样_%s.mp4" % key)
    out_dir = os.path.join(SAMPLES, "stills")
    os.makedirs(out_dir, exist_ok=True)
    times = [37.10, 38.10, 40.60, 42.60, 44.30, 48.95, 49.55, 51.60,
             55.20, 59.10, 63.50, 65.30, 66.75]
    for t in times:
        out = os.path.join(out_dir, "video_%s_%.2f.jpg" % (key, t))
        subprocess.run([FF, "-v", "error", "-ss", "%.3f" % (t - flare.SAMPLE_START),
                        "-i", src, "-frames:v", "1", "-q:v", "2", "-y", out],
                       capture_output=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    keys = [a for a in args if a in ("16x9", "9x16")] or ["16x9"]
    for key in keys:
        render_sample(key)
        stills_from_video(key)


