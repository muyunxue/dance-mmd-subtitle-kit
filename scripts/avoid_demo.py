# -*- coding: utf-8 -*-
"""
Subject-aware subtitle placement demo.

1) analyse a video: per-frame person mask (background subtraction) -> occupancy grid
2) for every lyric cue, search type size / line shape / screen position that keeps the
   text block off the person during that cue (average + worst-frame occupancy)
3) render two versions of the same clip: fixed bottom subtitles vs auto-avoid subtitles
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
OUT = os.path.join(ROOT, "输出", "人物避让演示")
FFMPEG = r"C:\Users\35530\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"

W, H = 1920, 1080
FPS = 30
DUR = 12.0
NF = int(round(DUR * FPS))
GW, GH = 16, 9            # occupancy grid
QW, QH = 480, 270         # analysis resolution
MARGIN = 70

IMPACT = r"C:\Windows\Fonts\impact.ttf"
MSYHL = r"C:\Windows\Fonts\msyhl.ttc"

WHITE = (244, 241, 234)
EMBER = (255, 59, 30)
GOLD = (255, 201, 84)


def C(rgb):
    r, g, b = rgb
    return "&H%02X%02X%02X&" % (b, g, r)


def ts(sec):
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int(sec % 3600 // 60)
    return "%d:%02d:%05.2f" % (h, m, sec - h * 3600 - m * 60)


# ------------------------------------------------------------------ video ---
def read_frames_q(video):
    """Decode the clip and return quarter-res frames (numpy uint8)."""
    cmd = [FFMPEG, "-v", "error", "-i", video, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    frames = []
    fsz = W * H * 3
    try:
        for i in range(NF):
            buf = p.stdout.read(fsz)
            if len(buf) < fsz:
                break
            arr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
            frames.append(np.ascontiguousarray(arr[::4, ::4]))
    finally:
        p.stdout.close()
        p.wait()
    return frames


def boxes(mask):
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return None
    return (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))


def dilate(m, it=2):
    m = m.copy()
    for _ in range(it):
        g = m.copy()
        g[1:, :] |= m[:-1, :]
        g[:-1, :] |= m[1:, :]
        g[:, 1:] |= m[:, :-1]
        g[:, :-1] |= m[:, 1:]
        m = g
    return m


def analyse(video):
    cache = os.path.join(OUT, "analysis.npz")
    if os.path.exists(cache):
        d = np.load(cache)
        return d["occ"], d["bbox"]
    frames = read_frames_q(video)
    stack = np.stack([f for i, f in enumerate(frames) if i % 10 == 0]).astype(np.float32)
    bg = np.median(stack, axis=0)
    occ = np.zeros((NF, GH, GW), np.float32)
    bbox = np.zeros((NF, 4), np.int32)
    masks = {}
    for i, f in enumerate(frames):
        diff = np.abs(f.astype(np.float32) - bg).max(axis=2)
        mask = dilate(diff > 22, 2)
        # fill small holes: blur + threshold
        # smooth the mask a little (blur + threshold) to close gaps
        m_img = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
        mask = np.asarray(m_img) > 120
        occ[i] = mask.reshape(GH, QH // GH, GW, QW // GW).mean(axis=(1, 3))
        bb = boxes(mask)
        bbox[i] = bb if bb else (0, 0, 0, 0)
        if i in (30, 90, 156, 282, 330):
            masks[i] = mask
    np.savez_compressed(cache, occ=occ, bbox=bbox)
    # keep a few masks for the debug figure
    np.savez_compressed(os.path.join(OUT, "masks.npz"),
                        **{str(k): v for k, v in masks.items()})
    return occ, bbox


# ----------------------------------------------------------------- layout ---
def text_width(text, fs, font=IMPACT):
    f = ImageFont.truetype(font, fs)
    return f.getlength(text)


def rows_options(text, fs):
    words = text.split()
    opts = [[text]]
    if len(words) >= 2:
        best = None
        for k in range(1, len(words)):
            a, b = " ".join(words[:k]), " ".join(words[k:])
            wa, wb = text_width(a, fs), text_width(b, fs)
            if best is None or abs(wa - wb) < best[0]:
                best = (abs(wa - wb), [a, b])
        opts.append(best[1])
    if len(words) >= 3:
        opts.append(words)
    out = []
    for rows in opts:
        w = max(text_width(r, fs) for r in rows)
        h = len(rows) * fs * 1.12 + (len(rows) - 1) * 6
        out.append((rows, w, h))
    return out


def rect_overlap(occ_avg, x1, y1, x2, y2):
    """Fraction of the rect covered by the averaged person occupancy."""
    area = max(1.0, (x2 - x1) * (y2 - y1))
    tot = 0.0
    for gy in range(GH):
        cy1, cy2 = gy * H / GH, (gy + 1) * H / GH
        oy = max(0.0, min(y2, cy2) - max(y1, cy1))
        if oy <= 0:
            continue
        for gx in range(GW):
            cx1, cx2 = gx * W / GW, (gx + 1) * W / GW
            ox = max(0.0, min(x2, cx2) - max(x1, cx1))
            if ox <= 0:
                continue
            tot += occ_avg[gy, gx] * ox * oy
    return tot / area


def frame_occ(frames_occ):
    return frames_occ


def choose_layout(text, cn, frames_idx, occ):
    """Pick the largest type size + line shape + position that stays off the person."""
    avg = occ[frames_idx].mean(axis=0)
    worst = occ[frames_idx].max(axis=0)
    cnw = text_width(cn, 44, MSYHL)
    global_best = None

    for fs in (190, 172, 154, 138, 122, 106, 92):
        best_at_fs = None
        for rows, tw, th in rows_options(text, fs):
            block_w = max(tw, cnw)
            block_h = th + 26 + 62
            if block_w > W - 2 * MARGIN or block_h > H - 2 * MARGIN:
                continue
            for xf in (0.14, 0.28, 0.42, 0.56, 0.70, 0.85):
                for yf in (0.13, 0.25, 0.37, 0.49, 0.61, 0.73, 0.84):
                    cx, cy = W * xf, H * yf
                    x1, x2 = cx - block_w / 2, cx + block_w / 2
                    y1, y2 = cy - block_h / 2, cy + block_h / 2
                    if x1 < MARGIN or x2 > W - MARGIN or y1 < MARGIN or y2 > H - MARGIN:
                        continue
                    th_main = th
                    main_y1 = y1
                    cn_top = main_y1 + th_main + 26
                    ov = rect_overlap(avg, x1, y1, x2, y2)
                    wv = rect_overlap(worst, x1, y1, x2, y2)
                    cand = dict(text=text, cn=cn, fs=fs, rows=rows,
                                score=ov + 0.5 * wv + 0.005 * (len(rows) - 1),
                                overlap=ov, worst=wv, cx=cx,
                                main_top=main_y1, cn_top=cn_top,
                                block=(x1, y1, x2, y2))
                    if best_at_fs is None or cand["score"] < best_at_fs["score"]:
                        best_at_fs = cand
                    if global_best is None or cand["score"] < global_best["score"]:
                        global_best = cand
        # accept this size if its best placement is essentially clear
        if best_at_fs and best_at_fs["overlap"] <= 0.015 and best_at_fs["worst"] <= 0.06:
            return best_at_fs
    return global_best


# ---------------------------------------------------------------- subtitles --
CUE_DEFS = [
    (0.30, 2.10, "MAKING EVERYBODY GO", "让所有人都在问", "EVERYBODY"),
    (2.25, 4.10, "WHO IS SHE?", "她是谁？", "SHE?"),
    (4.25, 6.05, "HEARTBEAT", "心跳怦然", "HEARTBEAT"),
    (6.20, 8.05, "FEEL THE FIRE", "感受这火焰", "FIRE"),
    (8.20, 10.05, "COME AND SEE ME", "来看我吧", "SEE"),
    (10.20, 11.90, "WHO IS SHE?", "她是谁？", "SHE?"),
]


def inline(text, accent, fs, base_color=None):
    base_color = base_color or C(WHITE)
    out = ""
    if accent and accent in text:
        idx = text.index(accent)
        pre, acc, post = text[:idx], text[idx:idx + len(accent)], text[idx + len(accent):]
        runs = [(pre, base_color), (acc, C(EMBER)), (post, base_color)]
    else:
        runs = [(text, base_color)]
    for s, col in runs:
        if not s:
            continue
        out += ("{\\fnImpact\\fs%d\\b0\\fsp1.0\\1c%s\\bord0\\shad0}" % (fs, col)) + s
    return out


def ass_header(title, w=W, h=H):
    return """[Script Info]
Title: %s
ScriptType: v4.00+
PlayResX: %d
PlayResY: %d
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Base,Impact,100,&H00F4F1EA,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,40,40,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" % (title, w, h)


def build_ass(layouts, variant="auto"):
    ev = []
    for (t0, t1, lay) in layouts:
        fs = lay["fs"]
        rows = lay["rows"]
        line_h = fs * 1.12
        for k, row in enumerate(rows):
            y = lay["main_top"] + line_h / 2 + k * (line_h + 6)
            body = inline(row, lay.get("accent", ""), fs)
            tags = ("{\\an5\\pos(%d,%d)\\fad(40,120)\\blur(6)"
                    "\\fscx124\\fscy124\\t(0,140,\\fscx100\\fscy100\\blur(0))"
                    "\\bord%g\\3c%s\\3a&H30&}"
                    % (lay["cx"], y, max(2, fs / 28.0), C((8, 6, 5))))
            ev.append("Dialogue: 1,%s,%s,Base,,0,0,0,,%s%s"
                      % (ts(t0), ts(t1), tags, body))
        cn_fs = 44
        cn_y = lay["cn_top"] + 31
        tags = ("{\\an5\\pos(%d,%d)\\fnMicrosoft YaHei Light\\fs%d\\1c%s\\bord2"
                "\\3c%s\\3a&H60&\\fad(120,140)\\fsp2}"
                % (lay["cx"], cn_y, cn_fs, C((232, 224, 212)), C((8, 6, 5))))
        ev.append("Dialogue: 1,%s,%s,Base,,0,0,0,,%s%s"
                  % (ts(t0), ts(t1), tags, lay["cn"]))
    return ass_header("avoid-%s" % variant) + "\n".join(ev) + "\n"


def fixed_layouts():
    """Plain bottom-centred subtitles, same text, no avoidance."""
    out = []
    for (t0, t1, text, cn, accent) in CUE_DEFS:
        fs = 140
        opts = rows_options(text, fs)
        rows = opt = None
        for rows_opt, tw, th in opts:
            if tw <= W - 2 * MARGIN:
                rows, opt = rows_opt, (tw, th)
                break
        if rows is None:
            rows = [text]
        th = len(rows) * fs * 1.12 + (len(rows) - 1) * 6
        main_top = H - 190 - th
        lay = dict(text=text, cn=cn, accent=accent, fs=fs, rows=rows,
                   cx=W / 2, main_top=main_top, cn_top=H - 165)
        out.append((t0, t1, lay))
    return out


# ----------------------------------------------------------------- render ---
def render_video(ass_path, out_name):
    out = os.path.join(OUT, out_name)
    tmp = "_tmp_avoid.ass"
    with open(ass_path, encoding="utf-8-sig") as f, \
            open(os.path.join(OUT, tmp), "w", encoding="utf-8-sig", newline="\n") as g:
        g.write(f.read())
    cmd = [FFMPEG, "-v", "error", "-y", "-i", os.path.join(OUT, "演示素材_舞者.mp4"),
           "-vf", "ass=%s" % tmp, "-c:v", "libx264", "-preset", "medium",
           "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    p = subprocess.run(cmd, cwd=OUT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    print("RENDER", out_name, p.returncode, (p.stderr or "")[-200:])
    return out


def side_by_side(left, right, out_name):
    out = os.path.join(OUT, out_name)
    tmp_label = "_label.ass"
    label_ass = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: L,Microsoft YaHei,38,&H00F4F1EA,&H000000FF,&H00100806,&H00000000,0,0,0,0,100,100,2,0,1,2,1,7,60,60,30,1
Style: R,Microsoft YaHei,38,&H00F4F1EA,&H000000FF,&H00100806,&H00000000,0,0,0,0,100,100,2,0,1,2,1,7,60,60,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.30,0:00:11.90,L,,0,0,0,,{\\pos(40,34)}固定底部 · 人物被挡
Dialogue: 0,0:00:00.30,0:00:11.90,R,,0,0,0,,{\\pos(1000,34)}自动避让 · 跟着空位走
"""
    with open(os.path.join(OUT, tmp_label), "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(label_ass)
    cmd = [FFMPEG, "-v", "error", "-y", "-i", left, "-i", right,
           "-filter_complex",
           "[0:v]scale=960:540[l];[1:v]scale=960:540[r];[l][r]hstack=inputs=2,ass=%s[v]"
           % tmp_label,
           "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    p = subprocess.run(cmd, cwd=OUT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    print("SBS", p.returncode, (p.stderr or "")[-300:])
    return out


# ------------------------------------------------------------------- main ---
def main():
    os.makedirs(OUT, exist_ok=True)
    video = os.path.join(OUT, "演示素材_舞者.mp4")
    if not os.path.exists(video):
        import avoid_dancer
        avoid_dancer.render()
    occ, bbox = analyse(video)

    layouts = []
    for (t0, t1, text, cn, accent) in CUE_DEFS:
        idx = list(range(int(t0 * FPS), min(NF, int(t1 * FPS) + 1), 6))
        lay = choose_layout(text, cn, idx, occ)
        lay["accent"] = accent
        layouts.append((t0, t1, lay))
        print("cue", round(t0, 2), "fs", lay["fs"], "rows", len(lay["rows"]),
              "overlap", round(lay["overlap"], 3), "worst", round(lay["worst"], 3),
              "pos", int(lay["cx"]), int(lay["main_top"]))
    json.dump([{k: (v if isinstance(v, (int, float, str, list)) else str(v))
                for k, v in lay.items()}
               for (_, _, lay) in layouts],
              open(os.path.join(OUT, "layout.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    auto_ass = os.path.join(OUT, "演示_自动避让.ass")
    with open(auto_ass, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(build_ass(layouts, "auto"))

    fixed = fixed_layouts()
    fixed_ass = os.path.join(OUT, "演示_固定底部.ass")
    with open(fixed_ass, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(build_ass(fixed, "fixed"))

    a = render_video(auto_ass, "演示_自动避让_16x9.mp4")
    b = render_video(fixed_ass, "演示_固定底部_16x9.mp4")
    side_by_side(b, a, "对比_固定底部_vs_自动避让_16x9.mp4")
    print("DONE")


if __name__ == "__main__":
    main()


