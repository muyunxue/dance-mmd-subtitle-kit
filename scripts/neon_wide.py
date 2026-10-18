# -*- coding: utf-8 -*-
"""Neon subtitle sample for the ultra-wide MMD clip (2560x1080).

Fits the purple 'LOVE' stage / synth-pop mood: thin neon lettering, lavender
glow, pink accents, beat-synced pulses, no Chinese translation lines.
15 s excerpt: song 0:51.0 - 1:06.4.
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
OUT = os.path.join(ROOT, "输出", "字幕小样")

W, H = 2560, 1080
T0, T1 = 51.0, 66.4
BPM = 134.0
BEAT = 60.0 / BPM


def C(rgb):
    r, g, b = rgb
    return "&H%02X%02X%02X&" % (b, g, r)


WHITE = C((242, 240, 245))
LAV = C((201, 167, 255))
PINK = C((255, 111, 216))
VIOLET = C((122, 60, 255))
DIM = C((232, 225, 240))

EV = []


def ts(sec):
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int(sec % 3600 // 60)
    return "%d:%02d:%05.2f" % (h, m, sec - h * 3600 - m * 60)


def ev(layer, t0, t1, tags, text):
    t0, t1 = t0 - T0, t1 - T0
    if t1 <= 0:
        return
    t0 = max(0.0, t0)
    EV.append("Dialogue: %d,%s,%s,Neon,,0,0,0,,{%s}%s" % (layer, ts(t0), ts(t1), tags, text))


def neon(t0, t1, text, x, y, fs, color=WHITE, font="Microsoft YaHei Light",
         track=2.0, anim="fade", rot=0.0, hollow=False, glow=LAV,
         glow_a=0xB4, layer=3, flicker=None, pulses=None, alpha=0x00,
         fade=(180, 180), shadow=0):
    ft = "\\fn%s\\fs%d\\b0\\fsp%.1f\\shad%d" % (font, fs, track, shadow)
    ent = ""
    if anim == "rise":
        ent = "\\move(%d,%d,%d,%d,0,220)\\fad(%d,0)" % (x, y + 40, x, y, fade[0])
    elif anim == "slam":
        ent = ("\\fscx112\\fscy112\\blur(6)\\t(0,150,\\fscx100\\fscy100\\blur(0))"
               "\\fad(80,0)")
    elif anim == "fade":
        ent = "\\fad(%d,%d)" % fade
    elif anim == "cut":
        ent = ""
    # outer glow layers
    for bl, ga, la in ((22, glow_a + 0x30, 1), (10, glow_a, 1), (4, glow_a - 0x30, 2)):
        ev(la, t0, t1, "\\an5\\pos(%d,%d)%s\\1c%s\\1a&H%02X&\\bord0\\shad0\\blur(%d)%s"
           % (x, y, ft, glow, min(255, ga), bl, ent), text)
    if hollow:
        main = (ft + "\\1a&HFF&\\bord3.4\\3c%s\\3a&H28&\\blur(0.8)" % color)
    else:
        main = (ft + "\\1c%s\\1a&H%02X&\\bord1.8\\3c%s\\3a&H70&\\blur(0.5)"
                % (color, alpha, VIOLET))
    ev(layer, t0, t1, "\\an5\\pos(%d,%d)%s%s" % (x, y, main, ent), text)
    if flicker:
        for ft0 in flicker:
            for d in (0.04, 0.10):
                ev(layer + 2, max(t0, ft0 + d), min(t1, ft0 + d + 0.05),
                   "\\an5\\pos(%d,%d)%s\\1a&H50&" % (x, y, main), text)
    if pulses:
        for pt in pulses:
            ev(layer + 1, max(t0, pt), min(t1, pt + 0.12),
               "\\an5\\pos(%d,%d)\\fscx104\\fscy104\\fad(0,90)%s" % (x, y, main), text)


def flash(t, color=WHITE, alpha=0x50, dur=0.06, layer=6):
    shape = "m 0 0 l %d 0 %d %d 0 %d" % (W, W, H, H)
    ev(layer, t, t + 0.02 + dur, "\\an7\\pos(0,0)\\p1\\bord0\\shad0\\1c%s\\1a&H%02X&\\fad(0,%d)"
       % (color, alpha, int(dur * 1000)), shape)


def line(t0, t1, x1, y1, x2, y2, color=LAV, thick=3, alpha=0x60, layer=2, glow=True):
    w = abs(x2 - x1)
    h = abs(y2 - y1)
    if glow:
        ev(layer, t0, t1, "\\an7\\pos(%d,%d)\\p1\\bord0\\shad0\\1c%s\\1a&HA0&\\blur(10)\\fad(0,0)"
           % (min(x1, x2), min(y1, y2), color),
           "m 0 0 l %d 0 %d %d 0 %d" % (w, w, h, h))
    ev(layer + 1, t0, t1, "\\an7\\pos(%d,%d)\\p1\\bord0\\shad0\\1c%s\\1a&H%02X&\\fad(100,100)"
       % (min(x1, x2), min(y1, y2), color, alpha),
       "m 0 0 l %d 0 %d %d 0 %d" % (w, w, h, h))


def beats(a, b):
    out = []
    k = 0
    t = T0
    while t < b:
        if t >= a:
            out.append(t)
        k += 1
        t = T0 + k * BEAT
    return out


def header():
    return """[Script Info]
Title: NEON subtitle sample 2560x1080
ScriptType: v4.00+
PlayResX: %d
PlayResY: %d
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Neon,Microsoft YaHei Light,100,&H00F2F0F5,&H000000FF,&H001E1230,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,40,40,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" % (W, H)


def build():
    del EV[:]
    # ---------------- line 11: when I step onto the stage ----------------
    neon(51.06, 54.55, "STEP", 500, 640, 300, color=WHITE, font="Microsoft YaHei Light",
         track=10, anim="slam", glow=LAV, pulses=beats(51.2, 54.4)[::2])
    neon(51.75, 54.55, "ONTO THE STAGE", 560, 380, 92, color=DIM, track=8, anim="rise")
    neon(53.2, 54.55, "GOT THIS", 470, 940, 64, color=LAV, track=12, anim="fade")

    # ---------------- line 12: 息つけない mood heartbeat ----------------
    neon(54.58, 58.1, "息つけない", 600, 300, 118, color=WHITE, font="Microsoft YaHei",
         track=4, anim="fade", glow=PINK, glow_a=0x9C)
    neon(55.05, 58.1, "mood", 640, 620, 250, color=LAV, font="Microsoft YaHei Light",
         track=16, anim="slam", hollow=True, glow=LAV)
    neon(56.0, 58.1, "heartbeat", 1210, 980, 84, color=WHITE, track=14, anim="fade",
         pulses=beats(56.0, 58.0)[::2])

    # ---------------- line 13: feel the fire ----------------
    neon(58.19, 61.7, "feel the", 520, 330, 96, color=DIM, track=10, anim="rise")
    neon(58.86, 61.7, "fire", 540, 660, 330, color=PINK, font="Microsoft YaHei Light",
         track=10, anim="slam", glow=PINK, glow_a=0x78,
         flicker=[59.2, 60.1, 60.9], pulses=beats(59.0, 61.6)[::2])
    flash(58.88, C((255, 220, 250)), 0x44, 0.05)
    neon(60.05, 61.7, "baby", 2140, 380, 80, color=LAV, track=10, anim="fade")

    # ---------------- line 14: making everybody go who is she ----------------
    neon(61.81, 66.2, "MAKING EVERYBODY GO", 1280, 190, 54, color=DIM, track=16,
         anim="fade", glow=LAV, glow_a=0xC8)
    flash(63.3, LAV, 0x3C, 0.06)
    neon(63.3, 66.2, "who is", 560, 570, 230, color=WHITE, font="Microsoft YaHei Light",
         track=8, anim="slam", glow=LAV, pulses=beats(63.4, 66.0)[::2])
    neon(63.3, 66.2, "she?", 2040, 650, 300, color=PINK, font="Microsoft YaHei Light",
         track=8, anim="slam", glow=PINK, glow_a=0x78,
         flicker=[63.9, 64.6, 65.3], pulses=beats(63.5, 66.0)[::2])
    neon(64.2, 66.2, "?", 2300, 330, 130, color=LAV, track=2, anim="fade",
         glow=LAV, flicker=[64.8, 65.6])

    EV.sort(key=lambda e: int(e.split(",")[0].split(":")[1]))
    return header() + "\n".join(EV) + "\n"


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "NEON_ultrawide_15s.ass")
    with open(p, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(build())
    print("WROTE", p)


