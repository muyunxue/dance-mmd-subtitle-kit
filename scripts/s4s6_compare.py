# -*- coding: utf-8 -*-
"""Assemble S4 vs S6 comparison video + keyframe sheet for the 30 s sample."""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
OUT = os.path.join(ROOT, "输出", "S4S6_30s")
FF = r"C:\Users\35530\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
FONTS = os.path.join(BASE, "fonts")
W, H = 2560, 1080

S4 = os.path.join(OUT, "S4_30s.mp4")
S6 = os.path.join(OUT, "S6_30s.mp4")
CMP = os.path.join(OUT, "对比_S4S6_30s.mp4")


def ts(sec):
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int(sec % 3600 // 60)
    return "%d:%02d:%05.2f" % (h, m, sec - h * 3600 - m * 60)


def make_cmp_ass():
    p = os.path.join(OUT, "_cmp.ass")
    with open(p, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write("""[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: L,Microsoft YaHei,28,&H00F4F1EA,&H000000FF,&H00140F11,&H00000000,0,0,0,0,100,100,2,0,1,2,1,7,60,60,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:30.00,L,,0,0,0,,{\\pos(30,14)}S4 · 混排杂志感
Dialogue: 0,0:00:00.00,0:00:30.00,L,,0,0,0,,{\\pos(30,554)}S6 · 手写 / 荧光笔
""")
    return p


def main():
    for f in (S4, S6):
        if not os.path.exists(f):
            raise SystemExit("missing " + f)
    ass = make_cmp_ass()
    cmd = [FF, "-v", "error", "-y", "-i", S4, "-i", S6,
           "-filter_complex",
           "[0:v]scale=1280:540[a];[1:v]scale=1280:540[b];[a][b]vstack=inputs=2,ass=_cmp.ass[v]",
           "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", CMP]
    p = subprocess.run(cmd, cwd=OUT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    print("cmp", p.returncode, (p.stderr or "")[-300:])

    times = (1.5, 8.2, 12.5, 16.2, 22.3, 26.6)
    cells = []
    for name, path in (("S4", S4), ("S6", S6)):
        row = []
        for t in times:
            fp = os.path.join(OUT, "_c_%s_%.1f.jpg" % (name, t))
            subprocess.run([FF, "-v", "error", "-ss", "%.2f" % t, "-i", path,
                            "-frames:v", "1", "-q:v", "2", "-y", fp], capture_output=True)
            row.append(fp)
        cells.append(row)
    cw, ch, bar = 853, 360, 44
    sheet = Image.new("RGB", (cw * 3, (ch + bar) * 2), (10, 9, 10))
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype(os.path.join(r"C:\Windows\Fonts", "msyhbd.ttc"), 24)
    labels = ("S4 · 混排杂志感", "S6 · 手写 / 荧光笔")
    for ci in range(2):
        for k in range(3):
            im = Image.open(cells[ci][k]).convert("RGB").resize((cw, ch), Image.LANCZOS)
            sheet.paste(im, (k * cw, ci * (ch + bar) + bar))
        d.text((14, ci * (ch + bar) + 8), labels[ci], font=f, fill=(240, 236, 230))
    sheet.save(os.path.join(OUT, "对比_S4S6_关键帧.jpg"), quality=90)
    print("sheet done")


if __name__ == "__main__":
    main()
