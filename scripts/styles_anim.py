# -*- coding: utf-8 -*-
"""S2 / S4 / S6 animated subtitle samples (5 s) + 3-way comparison.

Segment: song 0:58.2 - 1:03.2 ("feel the fire baby..." + "making everybody go...")
Renders three 5s clips at 2560x1080 and one stacked comparison clip.
"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
OUT = os.path.join(ROOT, "输出", "字幕风格参考")
ASSETS = os.path.join(ROOT, "输出", "字幕小样")
FF = r"C:\Users\35530\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
FONTS = os.path.join(BASE, "fonts")
W, H = 2560, 1080
START = 7.2      # 58.2 - 51.0 in the graded base
DUR = 5.0

WHITE = "&H00F4F1EA&"
CREAM = "&H00E3F2F8&"   # BGR of (248,242,227)
INK = "&H00140F11&"
PINK = "&H00B35CFF&"    # BGR of (255,92,179)
PINKSOFT = "&H0080B8FF&"
LAV = "&H00FFA4C4&"     # BGR of (196,164,255)
AQUA = "&H00E6E248&"
CLEAR = "&HFF000000&"


def ts(sec):
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int(sec % 3600 // 60)
    return "%d:%02d:%05.2f" % (h, m, sec - h * 3600 - m * 60)


class Ass:
    def __init__(self, path, w=W, h=H):
        self.path = path
        self.w, self.h = w, h
        self.ev = []

    def add(self, layer, t0, t1, tags, text):
        self.ev.append((layer, t0, t1, tags, text))

    def write(self):
        head = """[Script Info]
ScriptType: v4.00+
PlayResX: %d
PlayResY: %d
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: X,Anton,100,%s,%s,%s,%s,0,0,0,0,100,100,0,0,1,0,0,5,30,30,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" % (self.w, self.h, WHITE.rstrip("&"), WHITE.rstrip("&"), INK.rstrip("&"), CLEAR.rstrip("&"))
        lines = []
        for layer, t0, t1, tags, text in sorted(self.ev, key=lambda e: (e[0], e[1])):
            lines.append("Dialogue: %d,%s,%s,X,,0,0,0,,{%s}%s"
                         % (layer, ts(t0), ts(t1), tags, text))
        with open(self.path, "w", encoding="utf-8-sig", newline="\n") as f:
            f.write(head + "\n".join(lines) + "\n")


def word(a, layer, t0, t1, text, x, y, fs, font="Anton", color=WHITE,
         track=0, anim="slam", rot=0.0, border=0, border_color=INK,
         chroma=False, fade=(100, 100), alpha="&H00&", glow=None):
    base = ("\\an5\\pos(%d,%d)\\fn%s\\fs%d\\fsp%d\\1c%s\\1a%s"
            "\\bord%d\\3c%s\\shad0" % (x, y, font, fs, track, color, alpha,
                                      border, border_color))
    if anim == "slam":
        ent = "\\fscx116\\fscy116\\blur(6)\\t(0,120,\\fscx100\\fscy100\\blur(0))"
    elif anim == "slamrot":
        ent = ("\\frz%.1f\\fscx118\\fscy118\\blur(7)"
               "\\t(0,130,\\frz%.1f\\fscx100\\fscy100\\blur(0))" % (rot + 8, rot))
    elif anim == "slide":
        ent = "\\move(%d,%d,%d,%d,0,200)" % (x - 130, y, x, y)
    elif anim == "rise":
        ent = "\\move(%d,%d,%d,%d,0,260)" % (x, y + 60, x, y)
    elif anim == "fade":
        ent = ""
    else:
        ent = ""
    ent += "\\fad(%d,%d)" % fade
    if glow:
        a.add(layer - 1, t0, t1, base.replace("\\1c" + color, "\\1c" + glow)
              .replace("\\3c" + border_color, "\\3c" + glow)
              .replace("\\bord%d" % border, "\\bord%d" % (border + 10))
              .replace("\\1a%s" % alpha, "\\1a&H80&") + "\\blur(16)" + ent, text)
    if chroma:
        a.add(layer - 1, t0, t1, base.replace("\\1c" + color, "\\1c&H00FFFF&")
              .replace("\\1a%s" % alpha, "\\1a&H70&").replace("\\pos(%d,%d)" % (x, y),
                                                               "\\pos(%d,%d)" % (x + 8, y + 3)) + ent, text)
    a.add(layer, t0, t1, base + "\\frz%.1f" % rot + ent, text)


def rect(a, layer, t0, t1, x1, y1, x2, y2, color, alpha="&H40&", rot=0.0, blur=0):
    w = x2 - x1
    h = y2 - y1
    draw = "m 0 0 l %d 0 %d %d 0 %d" % (w, w, h, h)
    a.add(layer, t0, t1,
          "\\an7\\pos(%d,%d)\\p1\\bord0\\shad0\\1c%s\\1a%s\\frz%.1f\\blur(%d)\\fad(120,120)"
          % (x1, y1, color, alpha, rot, blur), draw)


# ------------------------------------------------------------------ S2 ---
def build_s2(a):
    word(a, 2, 0.15, 3.55, "FEEL  THE", 500, 300, 86, track=26, anim="slide")
    word(a, 2, 0.40, 3.55, "FIRE", 560, 690, 320, track=12, anim="slam")
    word(a, 2, 2.25, 3.55, "baby", 2180, 880, 110, track=10, anim="fade")
    word(a, 2, 0.9, 3.55, "YOU CAN COME AND SEE ME", 540, 950, 30,
         font="Silkscreen", color=LAV, track=6, anim="fade", border=0)
    word(a, 2, 0.9, 3.55, "03 / 07", 2290, 210, 36, font="Silkscreen",
         color=LAV, track=4, anim="fade", border=0)
    rect(a, 1, 0.9, 3.55, 300, 915, 1000, 918, WHITE, "&H60&")
    # next line
    word(a, 2, 3.55, 5.0, "MAKING EVERYBODY GO", 1200, 200, 54, track=20,
         color=WHITE, anim="fade", alpha="&H40&")
    word(a, 2, 3.95, 5.0, "WHO IS", 560, 640, 170, track=8, anim="slam")
    word(a, 2, 4.30, 5.0, "SHE?", 600, 880, 230, track=6, anim="slam")


# ------------------------------------------------------------------ S4 ---
def build_s4(a):
    # tape strips
    rect(a, 1, 0.2, 3.55, 240, 150, 980, 250, CREAM, "&H78&", rot=-8, blur=1)
    rect(a, 1, 0.5, 3.55, 860, 330, 1400, 420, PINK, "&H60&", rot=11, blur=1)
    # MAKING
    word(a, 3, 0.10, 3.55, "MAKING", 520, 215, 165, font="Bebas Neue", track=8,
         color=WHITE, anim="slamrot", rot=-4, border=3)
    # everybody (serif italic, cream)
    word(a, 3, 0.55, 3.55, "everybody", 850, 430, 230, font="Georgia",
         track=0, color=CREAM, anim="slamrot", rot=-6, border=4)
    a.add(2, 0.55, 3.55, "\\an5\\pos(850,430)\\fnGeorgia\\i1\\fs230\\1c%s\\bord4\\3c%s\\shad0"
          "\\frz-6\\fscx112\\fscy112\\t(0,140,\\fscx100\\fscy100)\\fad(140,120)" % (CREAM, INK),
          "everybody")
    # GO block
    rect(a, 1, 2.35, 3.55, 250, 700, 620, 900, "&H00562A3A&", "&H10&", rot=5, blur=0)
    word(a, 3, 2.30, 3.55, "GO!", 420, 790, 175, font="Archivo Black", track=2,
         color=WHITE, anim="slamrot", rot=5, border=0)
    word(a, 2, 2.75, 3.55, "get up / get down", 1150, 930, 26, font="Silkscreen",
         color=CREAM, track=6, anim="fade", border=0)
    # doodles
    a.add(3, 2.95, 3.55, "\\an5\\pos(1080,220)\\fnMicrosoft YaHei\\fs70\\1c%s\\bord0\\shad0"
          "\\fad(150,120)" % PINK, "star")
    a.add(3, 3.05, 3.55, "\\an5\\pos(1250,300)\\fnMicrosoft YaHei\\fs58\\1c%s\\bord0\\shad0"
          "\\fad(150,120)" % LAV, "heart")
    # next line
    word(a, 2, 3.55, 5.0, "MAKING EVERYBODY GO", 780, 200, 52, font="Bebas Neue",
         track=14, color=WHITE, anim="fade", alpha="&H40&", border=2)
    word(a, 2, 3.95, 5.0, "who is she?", 750, 620, 190, font="Georgia",
         color=CREAM, anim="slamrot", rot=-4, border=4)
    a.add(2, 3.95, 5.0, "\\an5\\pos(750,620)\\fnGeorgia\\i1\\fs190\\1c%s\\bord4\\3c%s\\shad0"
          "\\frz-4\\fscx116\\fscy116\\t(0,130,\\fscx100\\fscy100)\\fad(120,100)" % (CREAM, INK),
          "who is she?")


# ------------------------------------------------------------------ S6 ---
def build_s6(a):
    # highlighter swipe
    rect(a, 1, 0.25, 3.4, 180, 700, 980, 890, PINK, "&H50&", rot=-4, blur=2)
    rect(a, 1, 0.25, 3.4, 200, 740, 960, 850, PINK, "&H38&", rot=-4, blur=4)
    word(a, 3, 0.25, 3.4, "fire", 560, 790, 330, font="Permanent Marker",
         color=INK, track=0, anim="slamrot", rot=-4, border=0)
    word(a, 3, 2.20, 3.4, "baby", 980, 950, 150, font="Permanent Marker",
         color=CREAM, track=2, anim="fade", border=3)
    # note sticker
    rect(a, 1, 1.35, 3.4, 240, 170, 800, 290, CREAM, "&H10&", rot=3, blur=0)
    word(a, 3, 1.40, 3.4, "come and see me", 520, 230, 46, font="Permanent Marker",
         color=INK, track=1, anim="fade", border=0)
    # doodles
    a.add(3, 2.8, 3.4, "\\an5\\pos(1750,800)\\fnMicrosoft YaHei\\fs64\\1c%s\\bord0\\shad0\\fad(150,120)" % PINK, "heart")
    a.add(3, 2.9, 3.4, "\\an5\\pos(1620,880)\\fnMicrosoft YaHei\\fs60\\1c%s\\bord0\\shad0\\fad(150,120)" % "&H0054C9FF&", "star")
    # next line
    word(a, 3, 3.55, 5.0, "who is she?", 700, 300, 110, font="Permanent Marker",
         color=CREAM, track=2, anim="fade", border=3)
    word(a, 3, 3.95, 5.0, "SHE?", 640, 700, 280, font="Permanent Marker",
         color=INK, track=0, anim="slamrot", rot=-4, border=0)
    rect(a, 1, 3.9, 5.0, 220, 590, 1060, 760, PINK, "&H58&", rot=-4, blur=2)


# ---------------------------------------------------------------- render ---
def render(style, ass_name):
    out = os.path.join(OUT, "小样_%s_5s.mp4" % style)
    cmd = [FF, "-v", "error", "-y", "-ss", "%.3f" % START, "-t", "%.3f" % DUR,
           "-i", os.path.join(ASSETS, "_base_graded_15s.mp4"),
           "-vf", "ass=%s:fontsdir=fonts" % ass_name,
           "-c:v", "libx264", "-preset", "medium", "-crf", "16",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    p = subprocess.run(cmd, cwd=BASE, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    print("render", style, p.returncode, (p.stderr or "")[-300:])
    return out


def compare(clips):
    labels = ["S2 · 极简动态排版", "S4 · 混排杂志感", "S6 · 手写 / 荧光笔"]
    ass = Ass(os.path.join(BASE, "_cmp3.ass"), 1280, 1620)
    for i, lab in enumerate(labels):
        ass.add(9, 0.0, DUR, "\\an7\\pos(24,%d)\\fnMicrosoft YaHei\\fs26\\bord2\\3c&H00000000&"
                "\\1c&H00F4F1EA&\\shad0\\fad(0,0)" % (i * 540 + 12), lab)
    ass.write()
    inputs = []
    for c in clips:
        inputs += ["-i", c]
    fc = "".join("[%d:v]scale=1280:540[v%d];" % (i, i) for i in range(3))
    fc += "[v0][v1][v2]vstack=inputs=3[vs];[vs]ass=_cmp3.ass:fontsdir=fonts[v]"
    cmd = [FF, "-v", "error", "-y"] + inputs + ["-filter_complex", fc, "-map", "[v]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           os.path.join(OUT, "对比_S2S4S6_5s.mp4")]
    p = subprocess.run(cmd, cwd=BASE, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    print("compare", p.returncode, (p.stderr or "")[-300:])
    # stills: 3 styles x 3 moments
    times = (1.3, 2.7, 4.3)
    cells = []
    for ci, c in enumerate(clips):
        row = []
        for t in times:
            fp = os.path.join(OUT, "_cell_%d_%.1f.jpg" % (ci, t))
            subprocess.run([FF, "-v", "error", "-ss", "%.2f" % t, "-i", c,
                            "-frames:v", "1", "-q:v", "2", "-y", fp], capture_output=True)
            row.append(fp)
        cells.append(row)
    cw, ch, bar = 853, 360, 44
    sheet = Image.new("RGB", (cw * 3, (ch + bar) * 3), (10, 9, 10))
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype(os.path.join(r"C:\Windows\Fonts", "msyhbd.ttc"), 24)
    for ci in range(3):
        for k in range(3):
            im = Image.open(cells[ci][k]).convert("RGB").resize((cw, ch), Image.LANCZOS)
            sheet.paste(im, (k * cw, ci * (ch + bar) + bar))
        d.text((14, ci * (ch + bar) + 8), labels[ci], font=f, fill=(240, 236, 230))
    sheet.save(os.path.join(OUT, "对比_S2S4S6_关键帧.jpg"), quality=90)
    print("sheet done")


def main():
    a2 = Ass(os.path.join(BASE, "_s2.ass")); build_s2(a2); a2.write()
    a4 = Ass(os.path.join(BASE, "_s4.ass")); build_s4(a4); a4.write()
    a6 = Ass(os.path.join(BASE, "_s6.ass")); build_s6(a6); a6.write()
    clips = [render("S2", "_s2.ass"), render("S4", "_s4.ass"), render("S6", "_s6.ass")]
    compare(clips)


if __name__ == "__main__":
    main()
