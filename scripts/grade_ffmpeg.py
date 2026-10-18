# -*- coding: utf-8 -*-
"""5s color test v3 — fast ffmpeg render.

Subject-pop look = soft elliptical 'stage light' around the dancer:
  subject: brighter / warmer / more saturated + highlight bloom
  background: dimmer / cooler / desaturated / slightly soft + vignette
Implemented with a static radial mask PNG (dancer stays centred in this clip)
+ alphamerge/overlay, so it renders in seconds at full 2560x1080.
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
SRC = os.path.join(ROOT, "0001-4956 - 副本.mkv")
OUT = os.path.join(ROOT, "输出", "调色测试")
FF = r"C:\Users\35530\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
MSYH = r"C:\Windows\Fonts\msyh.ttc"
W, H = 2560, 1080
START, DUR = 62.0, 5.0


def make_mask(path, cx=0.515, cy=0.565, rx=0.215, ry=0.42, power=0.62):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    q = ((xx - W * cx) / (W * rx)) ** 2 + ((yy - H * cy) / (H * ry)) ** 2
    m = np.clip(1.0 - q, 0, 1) ** power
    m = (m * 255).astype(np.uint8)
    Image.fromarray(m).save(path)
    return path


def render(mask_path, out_path, bg_dim, bg_sat, bg_cool, sub_gain, sub_sat,
           bloom, vignette, soft=0.0):
    # subject chain: eq + colorbalance + bloom + alpha from mask
    subj = ("eq=brightness=%.3f:contrast=1.06:saturation=%.3f,"
            "colorbalance=rs=0.02:bs=-0.02:rm=0.05:bm=-0.06:rh=0.02:bh=-0.02"
            % (sub_gain, sub_sat))
    bg = ("eq=brightness=%.3f:contrast=1.07:saturation=%.3f,"
          "colorbalance=rm=%.3f:bm=%.3f:rh=-0.01"
          % (bg_dim, bg_sat, -bg_cool * 0.6, bg_cool))
    if soft > 0:
        bg += ",gblur=sigma=%.2f" % soft
    graph = (
        "[0:v]split=2[sv][bv];"
        "[sv]%s,split=2[sm][sh];"
        "[sh]gblur=sigma=14[blur];"
        "[sm][blur]blend=all_mode=screen:all_opacity=%.2f[sub];"
        "[sub]format=yuva420p[suba];"
        "[1:v]format=gray[gm];"
        "[suba][gm]alphamerge[subj];"
        "[bv]%s[bg];"
        "[bg][subj]overlay=0:0,"
        "vignette=angle=PI/4.2,format=yuv420p[v]"
        % (subj, bloom, bg)
    )
    # vignette strength via 'mode' isn't parameterisable enough; apply a second
    # darkening ring by compositing a pre-made vignette grade if needed
    cmd = [FF, "-v", "error", "-y", "-ss", "%.3f" % START, "-t", "%.3f" % DUR,
           "-i", SRC, "-loop", "1", "-framerate", "30", "-i", mask_path,
           "-filter_complex", graph, "-map", "[v]", "-t", "%.3f" % DUR,
           "-c:v", "libx264", "-preset", "medium", "-crf", "16",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_path]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(os.path.basename(out_path), p.returncode, (p.stderr or "")[-400:])
    return out_path


def grab(video, t, path):
    subprocess.run([FF, "-v", "error", "-ss", "%.2f" % t, "-i", video,
                    "-frames:v", "1", "-q:v", "2", "-y", path], capture_output=True)
    return path


def stack(left, right, out, la, lb):
    ass = os.path.join(OUT, "_cmp2.ass")
    with open(ass, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write("""[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: L,Microsoft YaHei,30,&H00F4F1EA,&H000000FF,&H00100806,&H00000000,0,0,0,0,100,100,2,0,1,2,1,7,60,60,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.00,L,,0,0,0,,{\\pos(40,18)}%s
Dialogue: 0,0:00:00.00,0:00:05.00,L,,0,0,0,,{\\pos(40,558)}%s
""" % (la, lb))
    cmd = [FF, "-v", "error", "-y", "-i", left, "-i", right,
           "-filter_complex",
           "[0:v]scale=1280:540[a];[1:v]scale=1280:540[b];[a][b]vstack=inputs=2,ass=_cmp2.ass[v]",
           "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", os.path.join(OUT, out)]
    p = subprocess.run(cmd, cwd=OUT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print("stack", out, p.returncode, (p.stderr or "")[-200:])


def main():
    os.makedirs(OUT, exist_ok=True)
    mask = make_mask(os.path.join(OUT, "_mask_spot.png"))
    original = os.path.join(OUT, "原片_5s.mp4")
    if not os.path.exists(original):
        subprocess.run([FF, "-v", "error", "-y", "-ss", "%.3f" % START, "-t", "%.3f" % DUR,
                        "-i", SRC, "-c:v", "libx264", "-preset", "medium", "-crf", "16",
                        "-pix_fmt", "yuv420p", "-movflags", "+faststart", original],
                       capture_output=True)
    a = os.path.join(OUT, "调色A_自然_5s.mp4")
    b = os.path.join(OUT, "调色B_强化_5s.mp4")
    render(mask, a, bg_dim=-0.04, bg_sat=0.82, bg_cool=0.05,
           sub_gain=0.035, sub_sat=1.10, bloom=0.22, vignette=0.3, soft=0.6)
    render(mask, b, bg_dim=-0.09, bg_sat=0.66, bg_cool=0.09,
           sub_gain=0.065, sub_sat=1.18, bloom=0.40, vignette=0.45, soft=1.2)
    stack(original, a, "对比_原片vsA_5s.mp4", "原片", "调色 A · 自然")
    stack(a, b, "对比_AvsB_5s.mp4", "调色 A · 自然", "调色 B · 强化")

    # stills
    cells = {}
    for name, path in (("o", original), ("a", a), ("b", b)):
        cells[name] = grab(path, 1.2, os.path.join(OUT, "_g_%s.jpg" % name))
        cells[name + "2"] = grab(path, 3.2, os.path.join(OUT, "_g2_%s.jpg" % name))
    x1, x2, y1, y2 = 850, 1900, 150, 1050
    sheet = Image.new("RGB", (1500, 858 + 32), (12, 10, 9))
    f = ImageFont.truetype(MSYH, 22)
    d = ImageDraw.Draw(sheet)
    for r, (k, lab) in enumerate((("o", "原片"), ("a", "调色 A · 自然"), ("b", "调色 B · 强化"))):
        im = Image.open(cells[k]).convert("RGB").crop((x1, y1, x2, y2)).resize((500, 429), Image.LANCZOS)
        sheet.paste(im, (r * 500, 30))
        d.text((r * 500 + 12, 6), lab, font=f, fill=(240, 240, 240))
        if r == 0:
            pass
    sheet.save(os.path.join(OUT, "对比_人物特写.jpg"), quality=92)
    sheet2 = Image.new("RGB", (2560, 748), (12, 10, 9))
    for r, t in enumerate((1.2, 3.2)):
        for c, (name, lab) in enumerate((("o", "原片"), ("a", "调色 A · 自然"), ("b", "调色 B · 强化"))):
            key = name if r == 0 else name + "2"
            im = Image.open(cells[key]).convert("RGB").resize((850, 359), Image.LANCZOS)
            sheet2.paste(im, (c * 850 + 5, r * 374 + 5))
    d2 = ImageDraw.Draw(sheet2)
    for c, lab in enumerate(("原片", "调色 A · 自然", "调色 B · 强化")):
        d2.text((c * 850 + 16, 8), lab, font=f, fill=(240, 240, 240))
    sheet2.save(os.path.join(OUT, "对比_全画面.jpg"), quality=92)
    print("done")


if __name__ == "__main__":
    main()

