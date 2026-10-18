# -*- coding: utf-8 -*-
"""FLARE subtitle sample for the ultra-wide MMD clip (2560x1080).

15 s excerpt: song 0:51.0 – 1:06.0 (lines 11-14 of 'Who is she').
Character sits around x=1200; type is placed left/right of her, not only at bottom.
"""
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
SRC = os.path.join(ROOT, "0001-4956 - 副本.mkv")
OUT = os.path.join(ROOT, "输出", "字幕小样")
FF = r"C:\Users\35530\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"

W, H = 2560, 1080
FPS = 30
T0, T1 = 51.0, 66.4
DUR = T1 - T0


def C(rgb):
    r, g, b = rgb
    return "&H%02X%02X%02X&" % (b, g, r)


WHITE, EMBER, GOLD, CYAN, BLACK = C((244, 241, 234)), C((255, 59, 30)), C((255, 201, 84)), C((34, 230, 255)), C((10, 9, 8))


def ts(sec):
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int(sec % 3600 // 60)
    return "%d:%02d:%05.2f" % (h, m, sec - h * 3600 - m * 60)


EV = []


def ev(layer, t0, t1, tags, text):
    t0, t1 = t0 - T0, t1 - T0
    EV.append("Dialogue: %d,%s,%s,Base,,0,0,0,,{%s}%s" % (layer, ts(t0), ts(t1), tags, text))


def word(t0, t1, text, x, y, fs, color=WHITE, font="Impact", track=0.0,
         anim="slam", rot=0.0, border=0.0, border_a=0x60, chroma=False,
         glitch=None, pulses=None, alpha=0x00, bold=0, hollow=False, layer=3):
    font_tags = "\\fn%s\\fs%d\\b%d\\fsp%.2f" % (font, fs, bold, track)
    if hollow:
        base = font_tags + "\\1a&HFF&\\bord%.1f\\3c%s\\3a&H18&" % (max(border, 4), color)
    else:
        base = font_tags + "\\1c%s\\1a&H%02X&\\bord%.1f\\3c%s\\3a&H%02X&" % (
            color, alpha, border, BLACK, border_a)
    base += "\\shad0"
    if anim == "slam":
        ent = "\\fscx168\\fscy168\\blur(9)\\t(0,120,\\fscx100\\fscy100\\blur(0))"
    elif anim == "slam_rot":
        ent = ("\\frz%.1f\\fscx168\\fscy168\\blur(9)"
               "\\t(0,130,\\frz%.1f\\fscx100\\fscy100\\blur(0))" % (rot + 9, rot))
    elif anim == "rise":
        ent = "\\move(%d,%d,%d,%d,0,170)\\fad(60,0)" % (x, y + 80, x, y)
    elif anim == "fade":
        ent = "\\fad(140,0)"
    elif anim == "cut":
        ent = ""
    else:
        ent = ""
    # glow
    if not hollow:
        ev(1, t0, t1, "\\an5\\pos(%d,%d)%s\\1c%s\\1a&H9C&\\bord0\\shad0\\blur(14)%s"
           % (x, y, font_tags, color, ent), text)
    # chroma ghosts
    if chroma:
        for dx, col in ((-10, CYAN), (10, EMBER)):
            ev(2, t0, t1, "\\an5\\pos(%d,%d)%s\\1c%s\\1a&H78&\\bord0\\shad0%s"
               % (x + dx, y + 3, font_tags, col, ent), text)
    ev(layer, t0, t1, "\\an5\\pos(%d,%d)%s%s" % (x, y, base, ent), text)
    # glitch slices
    if glitch:
        for gt in glitch:
            for dy, hh, dx in ((-int(fs * 0.32), int(fs * 0.13), 24),
                               (0, int(fs * 0.10), -30),
                               (int(fs * 0.27), int(fs * 0.12), 18)):
                y1 = max(0, y + dy - hh)
                y2 = min(H, y + dy + hh)
                if y2 <= y1:
                    continue
                ev(4, gt, gt + 0.09,
                   "\\an5\\pos(%d,%d)\\clip(0,%d,%d,%d)%s" % (x + dx, y, y1, W, y2, base), text)
    if pulses:
        for pt, sc in pulses:
            ev(layer + 1, pt, pt + 0.16, "\\an5\\pos(%d,%d)\\fscx%d\\fscy%d\\fad(0,70)%s"
               % (x, y, int(sc * 100), int(sc * 100), base), text)


def flash(t, color=WHITE, alpha=0x30, dur=0.08, layer=6):
    shape = "m 0 0 l %d 0 %d %d 0 %d" % (W, W, H, H)
    ev(layer, t, t + 0.03 + dur, "\\an7\\pos(0,0)\\p1\\bord0\\shad0\\1c%s\\1a&H%02X&\\fad(0,%d)"
       % (color, alpha, int(dur * 1000)), shape)


def cn(t0, t1, text, x, y, fs=44, alpha=0x12, color=C((232, 224, 212))):
    ev(3, t0, t1, "\\an5\\pos(%d,%d)\\fnMicrosoft YaHei Light\\fs%d\\fsp1.6"
       "\\1c%s\\1a&H%02X&\\bord1.6\\3c%s\\3a&H60&\\fad(160,160)"
       % (x, y, fs, color, alpha, BLACK), text)


def header():
    return """[Script Info]
Title: FLARE subtitle sample 2560x1080
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
""" % (W, H)


def build():
    del EV[:]
    # ---------- line 11: when I step onto the stage ----------
    word(51.06, 54.55, "STEP", 470, 640, 300, color=EMBER, anim="slam_rot",
         rot=4, chroma=True, glitch=[51.10, 52.2],
         pulses=[(51.5, 1.04), (51.95, 1.07)])
    word(51.9, 54.55, "ONTO THE STAGE", 520, 360, 112, track=4, anim="rise")
    word(53.2, 54.55, "GOT THIS", 450, 920, 90, color=GOLD, anim="slam")
    cn(51.1, 54.55, "当我踏上舞台  是的 我掌控全场", 500, 1010)

    # ---------- line 12: 息つけない mood heartbeat ----------
    word(54.58, 58.1, "息つけない", 560, 300, 128, font="Microsoft YaHei",
         bold=1, anim="slam_rot", rot=-3)
    word(55.05, 58.1, "MOOD", 620, 610, 230, hollow=True, border=4.5,
         anim="slam", chroma=True, glitch=[55.1])
    word(56.0, 58.1, "HEARTBEAT", 1260, 975, 96, track=5, anim="slam",
         pulses=[(56.0, 1.05), (56.45, 1.10), (56.9, 1.05), (57.35, 1.10)])
    cn(54.62, 58.1, "令人屏息的氛围  心跳怦然", 2150, 960)

    # ---------- line 13: feel the fire baby ----------
    word(58.19, 61.7, "FEEL THE", 500, 300, 100, track=6, anim="slam")
    flash(58.88, WHITE, 0xC8, 0.07)
    word(58.86, 61.7, "FIRE", 520, 650, 340, color=EMBER, anim="slam_rot",
         rot=-4, glitch=[58.95, 60.3],
         pulses=[(59.7, 1.03), (60.15, 1.05)])
    word(60.05, 61.7, "BABY", 2140, 350, 90, track=3, anim="slam_rot", rot=-8)
    cn(58.25, 61.7, "感受这火焰 宝贝  来看我吧", 520, 950)

    # ---------- line 14: making everybody go who is she ----------
    word(61.81, 66.2, "MAKING EVERYBODY GO", 520, 250, 68, track=8,
         alpha=0x18, anim="fade")
    flash(63.3, EMBER, 0xBE, 0.07)
    word(63.3, 66.2, "WHO IS", 560, 560, 210, anim="slam_rot", rot=-2,
         chroma=True, glitch=[63.36, 65.2], pulses=[(63.75, 1.04), (64.2, 1.06)])
    word(63.3, 66.2, "SHE?", 2070, 660, 280, color=EMBER, anim="slam_rot",
         rot=3, chroma=True, glitch=[63.36, 63.44], pulses=[(63.75, 1.05), (64.2, 1.07)])
    word(64.2, 66.2, "?", 2330, 300, 150, color=GOLD, anim="slam_rot", rot=12)
    cn(61.85, 66.2, "让所有人都在问  她是谁？", 1260, 1020)

    EV.sort(key=lambda e: int(e.split(",")[0].split(":")[1]))
    return header() + "\n".join(EV) + "\n"


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "FLARE_ultrawide_15s.ass")
    with open(path, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(build())
    print("WROTE", path)

