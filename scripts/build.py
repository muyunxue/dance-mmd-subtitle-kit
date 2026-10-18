# -*- coding: utf-8 -*-
"""Build ASS / SRT / previews / overlays for the 'Who is she' dance subtitles.

usage:
    python build.py ass [stills] [videos] [alpha] [preview]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import subs_core as core

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
OUT = os.path.join(ROOT, "输出")
SUB_DIR = os.path.join(OUT, "字幕文件")
STILLS = os.path.join(OUT, "样张")
PREVIEW = os.path.join(OUT, "预览")
OVERLAY = os.path.join(OUT, "叠加层")

FFMPEG = r"C:\Users\35530\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
FPS = 30

VARIANTS = [("orig_main", "原文主"), ("cn_main", "中文主"),
            ("orig_only", "纯原文"), ("cn_only", "纯中文")]
VNAME = dict(VARIANTS)
CANVASES = ["16x9", "9x16"]
CANVAS_LABEL = {"16x9": "16x9", "9x16": "9x16"}


def ensure_dirs():
    for d in (OUT, SUB_DIR, STILLS, PREVIEW, OVERLAY):
        os.makedirs(d, exist_ok=True)


def write_text(path, text):
    with open(path, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(text)
    return path


def ass_filename(variant, canvas_key):
    return "WhoIsShe_字幕_%s_%s.ass" % (VNAME[variant], canvas_key)


def ass_path(variant, canvas_key):
    return os.path.join(SUB_DIR, ass_filename(variant, canvas_key))


# ----------------------------------------------------------------- build ----
def build_subtitles():
    ensure_dirs()
    made = []
    for vkey, _ in VARIANTS:
        for ckey in CANVASES:
            ass = core.build_variant(vkey, ckey)
            made.append(write_text(ass_path(vkey, ckey), ass))
    for lang, name in (("bilingual", "双语"), ("orig", "原文"), ("cn", "中文")):
        path = os.path.join(SUB_DIR, "WhoIsShe_字幕_%s.srt" % name)
        made.append(write_text(path, core.build_srt(lang)))
    return made


# ------------------------------------------------------------- backgrounds --
def _radial_add(im, cx, cy, r, color, strength=1.0):
    from PIL import ImageChops
    w, h = im.size
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(glow)
    steps = 90
    for i in range(steps, 0, -1):
        t = i / steps
        rr = max(1, int(r * t))
        a = (1 - t) ** 2.4 * strength
        col = tuple(int(c * a) for c in color)
        d.ellipse([cx - rr, cy - rr * 0.92, cx + rr, cy + rr * 0.92], fill=col)
    glow = glow.filter(ImageFilter.GaussianBlur(max(2, r * 0.06)))
    return ImageChops.add(im, glow)


def _vertical_gradient(w, h, top, bottom):
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return im


def _grain_vignette(im, g=5.0, vig=0.52):
    import numpy as np
    w, h = im.size
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = w / 2.0, h / 2.0
    rr = np.sqrt(((xx - cx) / (w * 0.62)) ** 2 + ((yy - cy) / (h * 0.62)) ** 2)
    mask = np.clip(1 - vig * np.clip(rr, 0, 1.25) ** 2, 0, 1)
    a = np.array(im).astype("float32") * mask[:, :, None]
    a += np.random.normal(0, g, (h, w, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8"))


def make_preview_background(canvas_key):
    path = os.path.join(PREVIEW, "bg_%s.png" % canvas_key)
    if os.path.exists(path):
        return path
    ensure_dirs()
    if canvas_key == "16x9":
        w, h = 1920, 1080
        im = _vertical_gradient(w, h, (27, 21, 20), (7, 6, 7))
        im = _radial_add(im, 505, 250, 980, (168, 100, 55), 0.62)
        im = _radial_add(im, 1520, 700, 820, (120, 62, 40), 0.34)
        im = _radial_add(im, 1020, 300, 440, (255, 178, 100), 0.22)
    else:
        w, h = 1080, 1920
        im = _vertical_gradient(w, h, (26, 20, 19), (6, 5, 6))
        im = _radial_add(im, 330, 430, 760, (170, 102, 56), 0.55)
        im = _radial_add(im, 820, 1180, 900, (120, 60, 38), 0.32)
        im = _radial_add(im, 600, 520, 360, (255, 176, 100), 0.20)
    im = _grain_vignette(im)
    im.save(path, quality=94)
    return path


# ----------------------------------------------------------------- stills ---
STILL_TS = [
    ("01_intro", 9.40),
    ("02_miracle", 25.60),
    ("03_hook_count", 32.60),
    ("04_hook", 49.60),
    ("05_verse", 76.10),
    ("06_break", 113.90),
    ("07_final_chorus", 129.60),
    ("08_ending", 152.90),
]


def shift_ass(ass_text, shift):
    """Shift events so `shift` becomes 0; keep only events overlapping it."""
    import re
    def repl(m):
        start = _parse_ts(m.group(3))
        end = _parse_ts(m.group(4))
        if end <= shift:
            return None
        s = max(0.0, start - shift)
        e = max(0.0, end - shift)
        if e <= 0:
            return None
        return "%s%s,%s,%s,%s" % (m.group(1), m.group(2), _fmt_ts(s), _fmt_ts(e), m.group(5))
    out = []
    for line in ass_text.splitlines():
        if line.startswith("Dialogue:"):
            m = re.match(r"^(Dialogue: )(\d+),(-?\d+:\d\d:\d\d\.\d\d),(-?\d+:\d\d:\d\d\.\d\d),(.*)$",
                         line)
            if not m:
                out.append(line)
                continue
            r = repl(m)
            if r:
                out.append(r)
        else:
            out.append(line)
    return "\n".join(out)


def _parse_ts(s):
    sign = -1 if s.startswith("-") else 1
    s = s.lstrip("-")
    h, m, rest = s.split(":")
    return sign * (int(h) * 3600 + int(m) * 60 + float(rest))


def _fmt_ts(sec):
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int(sec % 3600 // 60)
    return "%d:%02d:%05.2f" % (h, m, sec - h * 3600 - m * 60)


def render_stills(variant="orig_main", canvas_key="16x9", ts=None, bg=None, tag=""):
    ensure_dirs()
    path = ass_path(variant, canvas_key)
    if not os.path.exists(path):
        build_subtitles()
    with open(path, encoding="utf-8-sig") as f:
        ass_text = f.read()
    if bg is None:
        bg = make_preview_background(canvas_key)
    tmp_ass = os.path.join(STILLS, "_tmp_still.ass")
    made = []
    for name, t in (ts or STILL_TS):
        write_text(tmp_ass, shift_ass(ass_text, max(0.0, t - 1.0)))
        out = os.path.join(STILLS, "样张_%s_%s%s_%s.png" % (canvas_key, variant, tag, name))
        p = subprocess.run(
            [FFMPEG, "-v", "error", "-loop", "1", "-framerate", str(FPS), "-i", bg,
             "-ss", "1.0", "-vf", "ass=_tmp_still.ass",
             "-frames:v", "1", "-y", out],
            cwd=STILLS, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if p.returncode != 0:
            print("STILL FAILED", name, (p.stderr or "")[-400:])
        else:
            made.append(out)
    return made


# --------------------------------------------------------------- overlays ---
def render_overlay_screen(variant, canvas_key, crf=18, preset="medium"):
    """Light type on pure black: drop on any footage with blend mode 滤色/变亮."""
    ensure_dirs()
    path = ass_path(variant, canvas_key)
    if not os.path.exists(path):
        build_subtitles()
    cfg = core.CANVAS[canvas_key]
    out = os.path.join(OVERLAY, "叠加层_%s_%s_滤色.mp4" % (VNAME[variant], canvas_key))
    cmd = [FFMPEG, "-v", "error", "-y",
           "-f", "lavfi", "-i", "color=c=black:s=%dx%d:r=%d:d=%.2f"
           % (cfg["W"], cfg["H"], FPS, core.END_HOLD),
           "-vf", "ass=%s" % os.path.basename(path),
           "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
           "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           out]
    p = subprocess.run(cmd, cwd=SUB_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace")
    ok = p.returncode == 0 and os.path.exists(out)
    print("OVERLAY-screen", VNAME[variant], canvas_key, "OK" if ok else "FAILED", (p.stderr or "")[-200:])
    return out if ok else None


def render_overlay_alpha(variant, canvas_key, crf=30):
    """Transparent VP9/WebM overlay (real alpha channel)."""
    ensure_dirs()
    path = ass_path(variant, canvas_key)
    if not os.path.exists(path):
        build_subtitles()
    cfg = core.CANVAS[canvas_key]
    out = os.path.join(OVERLAY, "叠加层_%s_%s_透明.webm" % (VNAME[variant], canvas_key))
    src = "color=c=black@0.0:s=%dx%d:r=%d:d=%.2f,format=rgba" % (
        cfg["W"], cfg["H"], FPS, core.END_HOLD)
    cmd = [FFMPEG, "-v", "error", "-y", "-f", "lavfi", "-i", src,
           "-vf", "ass=%s:alpha=1" % os.path.basename(path),
           "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", str(crf),
           "-row-mt", "1", "-auto-alt-ref", "0",
           "-metadata:s:v:0", "alpha_mode=1",
           out]
    p = subprocess.run(cmd, cwd=SUB_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace")
    ok = p.returncode == 0 and os.path.exists(out)
    print("OVERLAY-alpha", VNAME[variant], canvas_key, "OK" if ok else "FAILED", (p.stderr or "")[-200:])
    return out if ok else None


# ---------------------------------------------------------------- preview ---
def render_preview(variant, canvas_key, crf=22, preset="medium"):
    ensure_dirs()
    path = ass_path(variant, canvas_key)
    if not os.path.exists(path):
        build_subtitles()
    bg = make_preview_background(canvas_key)
    cfg = core.CANVAS[canvas_key]
    dur = core.END_HOLD
    out = os.path.join(PREVIEW, "预览_%s_%s.mp4" % (VNAME[variant], canvas_key))
    # ass filter needs a colon-free relative path -> local temp copy
    tmp_ass = os.path.join(PREVIEW, "_preview.ass")
    with open(path, encoding="utf-8-sig") as f:
        write_text(tmp_ass, f.read())
    w, h = cfg["W"], cfg["H"]
    vf = ("scale=%d:%d,zoompan=z='1+0.05*on/%d':d=1:x='iw/2-(iw/zoom)/2':y='ih/2-(ih/zoom)/2'"
          ":s=%dx%d:fps=%d,ass=_preview.ass,fade=t=in:st=0:d=0.9,fade=t=out:st=%.2f:d=1.2,format=yuv420p"
          % (int(w * 1.22), int(h * 1.22), int(dur * FPS), w, h, FPS,
             dur - 1.45))
    cmd = [FFMPEG, "-v", "error", "-y",
           "-loop", "1", "-framerate", str(FPS), "-i", bg,
           "-t", "%.2f" % dur, "-vf", vf,
           "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
           "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           os.path.basename(out)]
    p = subprocess.run(cmd, cwd=PREVIEW, capture_output=True, text=True, encoding="utf-8", errors="replace")
    ok = p.returncode == 0 and os.path.exists(out)
    print("PREVIEW", VNAME[variant], canvas_key, "OK" if ok else "FAILED", (p.stderr or "")[-200:])
    return out if ok else None


# ------------------------------------------------------------------- main ---
if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or "ass" in args:
        for f in build_subtitles():
            print("WROTE", os.path.relpath(f, OUT))
    if "stills" in args:
        for f in render_stills("orig_main", "16x9"):
            print("STILL", os.path.basename(f))
        for f in render_stills("orig_main", "9x16"):
            print("STILL", os.path.basename(f))
    if "videos" in args:
        for ck in CANVASES:
            render_overlay_screen("orig_main", ck)
            render_overlay_screen("cn_main", ck)
    if "alpha" in args:
        for ck in CANVASES:
            render_overlay_alpha("orig_main", ck)
    if "preview" in args:
        for ck in CANVASES:
            render_preview("orig_main", ck)
