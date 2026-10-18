# -*- coding: utf-8 -*-
"""
FLARE / 炸场版 — 舞蹈字幕样片生成器

约 31 秒样片，取 chorus 1（歌曲 0:36.65 – 1:08.00）：
满画幅动态排版、拍点砸字、色差、故障切片、闪白、空心字。

所有排版先在 1920x1080 设计坐标里写好，渲染时按画布映射到 16:9 / 9:16。
"""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)


# ---------------------------------------------------------------- colours ---
def C(rgb):
    r, g, b = rgb
    return "&H%02X%02X%02X&" % (b, g, r)


WHITE = (244, 241, 234)
EMBER = (255, 59, 30)
GOLD  = (255, 201, 84)
CYAN  = (34, 230, 255)
BLACK = (10, 9, 8)

WHITE_C, EMBER_C, GOLD_C, CYAN_C, BLACK_C = (C(WHITE), C(EMBER), C(GOLD),
                                             C(CYAN), C(BLACK))

FONTS = {
    "impact": "Impact",
    "black":  "Arial Black",
    "jp":     "Microsoft YaHei",
    "cn":     "Microsoft YaHei Light",
}

SAMPLE_START = 36.65
SAMPLE_END = 68.00
FPS = 30
BEAT = 0.4474          # inferred from the LRC phrase grid (~134 BPM)


def ts(sec):
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int(sec % 3600 // 60)
    return "%d:%02d:%05.2f" % (h, m, sec - h * 3600 - m * 60)


# ----------------------------------------------------------------- layout ---
class Layout:
    def __init__(self, w, h, design_w=1920, design_h=1080):
        self.w, self.h = w, h
        self.dw, self.dh = design_w, design_h
        self.fs = 1.0 if w == 1920 else 0.72

    def p(self, x, y):
        return (int(round(x / self.dw * self.w)), int(round(y / self.dh * self.h)))

    def f(self, fs):
        return int(round(fs * self.fs))


# ---------------------------------------------------------------- builder ---
class Flare:
    def __init__(self, layout):
        self.L = layout
        self.events = []

    def sx(self, v):
        return int(round(v * self.L.w / 1920.0))

    def sy(self, v):
        return int(round(v * self.L.h / 1080.0))

    def ev(self, layer, t0, t1, tags, text):
        self.events.append("Dialogue: %d,%s,%s,Base,,0,0,0,,{%s}%s"
                           % (layer, ts(t0), ts(t1), tags, text))

    # ------------------------------------------------------------- word ----
    def word(self, t0, t1, text, x, y, fs, color=WHITE_C, font="impact",
             tracking=0.0, border=0.0, border_alpha=0x60, border_color=None,
             alpha=0x00, bold=0, italic=0, anim="slam", rot=0.0,
             chroma=0, hollow=False, glitch=None, pulses=None, jitter=None,
             trail=0, layer=3, glow=True):
        L = self.L
        X, Y = L.p(x, y)
        FS = L.f(fs)
        bc = border_color or BLACK_C

        if hollow:
            base = ("\\fn%s\\fs%d\\b%d\\i%d\\fsp%.2f\\1a&HFF&"
                    "\\bord%g\\3c%s\\3a&H%02X&\\shad0"
                    % (FONTS[font], FS, bold, italic, tracking,
                       max(border, 4.0), color, 0x16))
        else:
            base = ("\\fn%s\\fs%d\\b%d\\i%d\\fsp%.2f\\1c%s\\1a&H%02X&"
                    "\\bord%g\\3c%s\\3a&H%02X&\\shad0"
                    % (FONTS[font], FS, bold, italic, tracking, color, alpha,
                       border, bc, border_alpha))
        font_tags = "\\fn%s\\fs%d\\b%d\\i%d\\fsp%.2f" % (
            FONTS[font], FS, bold, italic, tracking)

        def ent_tags():
            if anim == "slam":
                return ("\\fscx168\\fscy168\\blur(9)"
                        "\\t(0,120,\\fscx100\\fscy100\\blur(0))")
            if anim == "slam_rot":
                return ("\\frz%.1f\\fscx168\\fscy168\\blur(9)"
                        "\\t(0,130,\\frz%.1f\\fscx100\\fscy100\\blur(0))"
                        % (rot + 9, rot))
            if anim == "pop":
                return "\\fscx45\\fscy45\\blur(6)\\t(0,110,\\fscx100\\fscy100\\blur(0))"
            if anim == "fade":
                return "\\fad(140,0)"
            if anim == "cut":
                return ""
            if anim == "rise":
                return ("\\move(%d,%d,%d,%d,0,170)\\fad(60,0)"
                        % (X, Y + self.sy(80), X, Y))
            if anim == "whip_l":
                return ("\\move(%d,%d,%d,%d,0,150)\\fad(40,0)"
                        % (X - self.sx(760), Y, X, Y))
            if anim == "whip_r":
                return ("\\move(%d,%d,%d,%d,0,150)\\fad(40,0)"
                        % (X + self.sx(760), Y, X, Y))
            return ""

        ent = ent_tags()
        tags = "\\an5\\pos(%d,%d)%s%s" % (X, Y, base, ent)

        # trails for whip moves
        if trail:
            for i in range(1, trail + 1):
                tdx = self.sx(420 + 280 * (i - 1)) * (1 if anim == "whip_r" else -1)
                tr = ("\\an5\\pos(%d,%d)%s\\fad(0,%d)"
                      % (X + tdx, Y, font_tags + "\\1c%s\\1a&H%02X&\\bord0\\shad0"
                         % (color, 0x58 + i * 0x30), 130))
                self.ev(2, t0, t0 + 0.22, tr, text)

        # chroma ghosts
        if chroma:
            for ddx, col in ((-0x0D, CYAN_C), (0x0D, EMBER_C)):
                tags2 = ("\\an5\\pos(%d,%d)%s\\1c%s\\1a&H%02X&\\bord0\\shad0%s"
                         % (X + self.sx(ddx), Y + self.sy(3), font_tags, col,
                            0x78, ent))
                self.ev(2, t0, t1, tags2, text)

        # glow
        if glow and not hollow:
            tags3 = ("\\an5\\pos(%d,%d)%s\\1c%s\\1a&H%02X&\\bord0\\shad0\\blur(%d)%s"
                     % (X, Y, font_tags, color, 0x9C, max(6, int(13 * L.fs)), ent))
            self.ev(1, t0, t1, tags3, text)

        self.ev(layer, t0, t1, tags, text)

        # glitch slices
        if glitch:
            for gt in glitch:
                for (dy, hh, dx) in ((-int(FS * 0.34), int(FS * 0.14), 22),
                                     (0, int(FS * 0.10), -28),
                                     (int(FS * 0.28), int(FS * 0.12), 16)):
                    y1 = max(0, Y + dy - hh)
                    y2 = min(L.h, Y + dy + hh)
                    if y2 <= y1:
                        continue
                    gt_tags = ("\\an5\\pos(%d,%d)\\clip(0,%d,%d,%d)%s"
                               % (X + self.sx(dx), Y, y1, L.w, y2, base))
                    self.ev(4, gt, gt + 0.09, gt_tags, text)

        # beat pulses
        if pulses:
            for (pt, scale) in pulses:
                pt_tags = ("\\an5\\pos(%d,%d)\\fscx%d\\fscy%d\\fad(0,70)%s"
                           % (X, Y, int(scale * 100), int(scale * 100), base))
                self.ev(layer + 1, pt, pt + 0.16, pt_tags, text)

        # jitter copies (fire shake)
        if jitter:
            for (jt, jdx, jdy) in jitter:
                jt_tags = ("\\an5\\pos(%d,%d)\\fad(0,50)%s"
                           % (X + self.sx(jdx), Y + self.sy(jdy), base))
                self.ev(layer + 1, jt, jt + 0.10, jt_tags, text)

    # ----------------------------------------------------------- ghost ----
    def ghost(self, t0, t1, text, x, y, fs, color=WHITE_C, alpha=0xE8,
              border=3.5, rot=0.0, rot_to=None, font="impact", tracking=0.0,
              layer=0):
        L = self.L
        X, Y = L.p(x, y)
        FS = L.f(fs)
        tags = ("\\an5\\pos(%d,%d)\\fn%s\\fs%d\\b1\\fsp%.2f"
                "\\1a&HFF&\\3c%s\\3a&H%02X&\\bord%g\\shad0"
                % (X, Y, FONTS[font], FS, tracking, color, alpha, border))
        if rot:
            tags += "\\frz%.1f" % rot
        if rot_to is not None:
            tags += "\\t(0,%d,\\frz%.1f)" % (int((t1 - t0) * 1000), rot_to)
        tags += "\\fad(400,400)"
        self.ev(layer, t0, t1, tags, text)

    # ---------------------------------------------------------- ticker ----
    def ticker(self, t0, t1, text, y, fs=40, speed_px=2600, color=WHITE_C,
               alpha=0x30, tracking=6.0, layer=2):
        L = self.L
        Y = L.p(0, y)[1]
        FS = L.f(fs)
        dur = t1 - t0
        x0 = L.w + self.sx(120)
        x1 = -self.sx(speed_px)
        tags = ("\\an4\\pos(%d,%d)\\clip(0,%d,%d,%d)\\fn%s\\fs%d\\b1\\fsp%.1f"
                "\\1c%s\\1a&H%02X&\\bord0\\shad0\\move(%d,%d,%d,%d,0,%d)"
                % (x0, Y, max(0, Y - int(FS * 0.8)), L.w, Y + int(FS * 0.35),
                   FONTS["impact"], FS, tracking, color, alpha,
                   x0, Y, x1, Y, int(dur * 1000)))
        self.ev(layer, t0, t1, tags, text)

    # ----------------------------------------------------------- flash ----
    def flash(self, t, color=WHITE_C, alpha=0x38, dur=0.07, layer=6):
        L = self.L
        shape = "m 0 0 l %d 0 %d %d 0 %d" % (L.w, L.w, L.h, L.h)
        tags = ("\\an7\\pos(0,0)\\p1\\bord0\\shad0\\1c%s\\1a&H%02X&\\fad(0,%d)"
                % (color, alpha, int(max(0.01, dur) * 1000)))
        self.ev(layer, t, t + 0.03 + dur, tags, shape)

    # ----------------------------------------------------- glitch bars ----
    def glitch_bars(self, t, color=WHITE_C, alpha=0xB4, layer=5, n=4, seed=0):
        import random
        L = self.L
        rnd = random.Random(int(t * 1000) + seed)
        out = []
        for i in range(n):
            y = rnd.randint(60, L.h - 60)
            hh = rnd.choice((2, 3, 6, 10))
            x0 = rnd.randint(-L.w // 4, L.w // 2)
            w = rnd.randint(L.w // 5, L.w)
            shape = "m %d %d l %d %d %d %d %d %d" % (
                x0, y, x0 + w, y, x0 + w, y + hh, x0, y + hh)
            tags = ("\\an7\\pos(0,0)\\p1\\bord0\\shad0\\1c%s\\1a&H%02X&\\fad(0,%d)"
                    % (color, alpha, rnd.randint(40, 90)))
            out.append("Dialogue: %d,%s,%s,Base,,0,0,0,,{%s}%s"
                       % (layer, ts(t), ts(t + rnd.uniform(0.04, 0.09)), tags, shape))
        self.events.extend(out)

    # ------------------------------------------------------------ slash ---
    def slash(self, t, x, y, height, width=9, angle=-20.0, color=EMBER_C,
              alpha=0x26, dur=0.24, layer=2):
        L = self.L
        X, Y = L.p(x, y)
        hh = int(L.p(0, height)[1] - L.p(0, 0)[1])
        ww = self.sx(width)
        shape = "m %d %d l %d %d %d %d %d %d" % (
            -ww // 2, -hh // 2, ww // 2, -hh // 2, ww // 2, hh // 2, -ww // 2, hh // 2)
        tags = ("\\an5\\pos(%d,%d)\\p1\\bord0\\shad0\\frz%.1f\\1c%s\\1a&H%02X&"
                "\\fad(0,%d)" % (X, Y, angle, color, alpha, int(dur * 1000)))
        self.ev(layer, t, t + dur, tags, shape)

    def build(self):
        self.events.sort(key=lambda e: int(e.split(",")[0].split(":")[1]))
        return header(self.L) + "\n".join(self.events) + "\n"


def header(L):
    return """[Script Info]
Title: Who is she - FLARE 炸场版 小样
ScriptType: v4.00+
PlayResX: %d
PlayResY: %d
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
Collisions: Normal
Timer: 100.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Base,Impact,100,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,40,40,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" % (L.w, L.h)


# ------------------------------------------------------------------ sample --
def sample(layout_key):
    L = Layout(*{"16x9": (1920, 1080), "9x16": (1080, 1920)}[layout_key])
    F = Flare(L)

    # 黑场切入
    F.flash(36.63, BLACK_C, 0x00, 0.16, layer=7)
    # 背景镂空大字（贯穿前半段）
    F.ghost(36.80, 50.9, "WHO IS SHE?", 880, 760, 560, alpha=0xF0, border=2.6,
            rot=10, rot_to=6, tracking=4)
    # 后半段的 FIRE 镂空
    F.ghost(54.60, 68.0, "FIRE", 1000, 620, 760, alpha=0xF2, border=2.4,
            rot=-12, rot_to=-7, tracking=2)

    # ============ line 7 : When I walk onto the stage =====================
    F.word(36.77, 38.45, "WALK", 620, 330, 185, anim="slam_rot", rot=-7,
           chroma=1, pulses=[(37.66, 1.04), (38.11, 1.07)])
    F.word(37.52, 40.10, "STAGE", 1140, 600, 330, anim="slam_rot", rot=3,
           chroma=1, glitch=[37.56, 38.60],
           pulses=[(37.66, 1.04), (38.11, 1.07), (38.55, 1.03)])
    F.slash(37.62, 760, 470, 300, 10, -22)
    F.slash(37.66, 1500, 700, 260, 10, 18)
    F.slash(38.11, 900, 830, 220, 8, -16)
    F.glitch_bars(37.60, seed=3)
    F.word(38.55, 40.10, "YEAH I GOT THIS", 960, 885, 88, color=EMBER_C,
           tracking=3, anim="rise")
    F.word(36.85, 40.10, "当我走上舞台  是的 我自带锋芒", 960, 1002, 46,
           font="cn", tracking=2.0, border=1.6, border_alpha=0x50,
           alpha=0x12, anim="fade")
    F.word(36.77, 38.4, "WHEN I", 300, 175, 58, tracking=10, alpha=0x30,
           anim="fade")

    # ============ line 8 : 息が燃え出す / heartbeat =======================
    F.word(40.25, 41.90, "息が燃え出す", 690, 360, 142, font="jp", bold=1,
           anim="slam_rot", rot=-4, chroma=1,
           pulses=[(40.70, 1.04), (41.15, 1.06)])
    F.word(41.28, 41.90, "キュンと", 1370, 640, 62, font="jp", bold=1,
           color=GOLD_C, anim="pop", rot=6)
    F.word(41.95, 43.72, "HEARTBEAT", 960, 730, 190, anim="slam",
           pulses=[(42.00, 1.06), (42.45, 1.11), (42.90, 1.06), (43.35, 1.11)])
    F.slash(42.02, 700, 840, 260, 9, -18)
    F.slash(42.05, 1230, 560, 220, 9, 16)
    F.glitch_bars(42.00, seed=51)
    F.word(40.30, 43.72, "呼吸开始燃烧  心跳怦然", 470, 165, 44, font="cn",
           tracking=2.0, border=1.6, border_alpha=0x50, alpha=0x12, anim="fade")

    # ============ line 9 : come around ====================================
    F.word(43.88, 47.30, "COME", 450, 320, 215, anim="whip_l", chroma=1,
           pulses=[(44.33, 1.04), (44.78, 1.06)])
    F.word(44.50, 47.30, "AROUND", 1260, 650, 225, color=EMBER_C,
           anim="whip_r", pulses=[(44.95, 1.04), (45.40, 1.06)])
    F.word(45.55, 47.30, "BABY", 700, 880, 130, anim="slam_rot", rot=7)
    F.word(46.10, 47.30, "COME AND SEE ME", 1450, 235, 58, tracking=6,
           alpha=0x12, anim="fade")
    F.word(43.95, 47.30, "靠近一点 宝贝  你可以来看我", 960, 150, 44, font="cn",
           tracking=2.0, border=1.6, border_alpha=0x50, alpha=0x12, anim="fade")

    # ============ line 10 : making everybody go ===========================
    F.word(47.46, 48.70, "MAKING", 520, 400, 88, anim="whip_l")
    F.word(47.72, 48.70, "EVERYBODY", 640, 505, 88, hollow=True,
           anim="whip_l")
    F.word(47.98, 48.70, "GO", 770, 610, 86, color=GOLD_C, anim="whip_l")
    F.ticker(47.60, 48.9,
             "MAKING EVERYBODY GO   /   MAKING EVERYBODY GO   /   MAKING EVERYBODY GO   ",
             165, fs=46, speed_px=3600, alpha=0x2A)
    F.flash(48.94, WHITE_C, 0xC8, 0.07)
    F.glitch_bars(48.94, seed=11)
    F.glitch_bars(49.37, seed=12)
    F.word(48.92, 50.90, "WHO IS", 830, 380, 235, anim="slam_rot", rot=-2,
           chroma=1, glitch=[48.99, 49.07, 49.58],
           pulses=[(49.82, 1.04), (50.27, 1.06)])
    F.flash(49.37, EMBER_C, 0xBE, 0.07)
    F.word(49.37, 50.90, "SHE?", 1150, 690, 330, color=EMBER_C,
           anim="slam_rot", rot=3, chroma=1, glitch=[49.42, 49.50, 49.95],
           pulses=[(49.82, 1.05), (50.27, 1.07)])
    F.slash(49.42, 610, 470, 320, 11, -24)
    F.slash(49.46, 1500, 560, 300, 11, 20)
    F.slash(50.05, 1180, 900, 200, 8, -14)
    F.word(49.22, 50.90, "WHO IS", 830, 380, 235, alpha=0xDD, anim="cut",
           layer=2)
    F.word(49.28, 50.90, "SHE?", 1150, 690, 330, color=EMBER_C, alpha=0xDD,
           anim="cut", layer=2)
    F.word(50.05, 50.90, "?", 1530, 300, 260, color=EMBER_C, anim="slam_rot",
           rot=14)
    F.word(47.50, 50.90, "让所有人都在问  她是谁？", 1440, 930, 46, font="cn",
           tracking=2.0, border=1.6, border_alpha=0x50, alpha=0x12, anim="fade")

    # ============ line 11 : step onto the stage ===========================
    F.word(51.06, 54.42, "STEP", 1330, 380, 310, color=EMBER_C,
           anim="slam_rot", rot=4, chroma=1, glitch=[51.10, 52.15],
           pulses=[(51.51, 1.04), (51.96, 1.06), (52.41, 1.03)])
    F.slash(51.12, 930, 500, 340, 11, -22)
    F.slash(51.16, 1700, 640, 280, 10, 17)
    F.glitch_bars(51.10, seed=21)
    F.word(51.90, 54.42, "ONTO THE STAGE", 650, 780, 100, tracking=4,
           anim="rise")
    F.word(53.20, 54.42, "GOT THIS", 1470, 905, 80, color=GOLD_C,
           anim="slam")
    F.word(51.12, 54.42, "当我踏上舞台  是的 我掌控全场", 470, 165, 44, font="cn",
           tracking=2.0, border=1.6, border_alpha=0x50, alpha=0x12, anim="fade")

    # ============ line 12 : 息つけない mood ================================
    F.word(54.58, 56.00, "息つけない", 600, 320, 128, font="jp", bold=1,
           anim="slam_rot", rot=-3)
    F.word(55.05, 58.02, "MOOD", 1180, 530, 235, hollow=True, anim="slam",
           chroma=1, glitch=[55.10])
    F.word(56.00, 58.02, "HEARTBEAT", 960, 880, 120, tracking=4,
           pulses=[(56.00, 1.06), (56.45, 1.10), (56.90, 1.06), (57.35, 1.10),
                   (57.80, 1.06)])
    F.word(54.62, 58.02, "令人屏息的氛围  心跳怦然", 1440, 170, 44, font="cn",
           tracking=2.0, border=1.6, border_alpha=0x50, alpha=0x12, anim="fade")

    # ============ line 13 : feel the fire =================================
    F.word(58.19, 61.65, "FEEL THE", 580, 280, 112, tracking=5, anim="slam")
    F.flash(58.88, WHITE_C, 0xC6, 0.08)
    F.glitch_bars(58.90, seed=31)
    F.word(58.86, 61.65, "FIRE", 960, 610, 380, color=EMBER_C,
           anim="slam_rot", rot=-4, glitch=[58.95, 60.30],
           jitter=[(59.02, -8, 2), (59.18, 6, -3), (59.34, -5, 1),
                   (59.50, 4, -2)],
           pulses=[(59.66, 1.03), (60.11, 1.05)])
    F.slash(58.92, 640, 500, 420, 12, -18)
    F.slash(58.96, 1330, 740, 380, 12, 22)
    F.slash(59.66, 1520, 430, 240, 9, -12)
    F.word(60.05, 61.65, "BABY", 1450, 860, 100, tracking=3, anim="slam_rot",
           rot=-6)
    F.word(58.25, 61.65, "感受这火焰 宝贝  来看我吧", 510, 940, 44, font="cn",
           tracking=2.0, border=1.6, border_alpha=0x50, alpha=0x12, anim="fade")

    # ============ line 14 : who is she (reprise) ==========================
    F.word(61.81, 63.25, "MAKING EVERYBODY GO", 960, 175, 62, tracking=8,
           alpha=0x18, anim="fade")
    F.flash(63.30, EMBER_C, 0xC0, 0.07)
    F.glitch_bars(63.31, seed=41)
    F.glitch_bars(65.15, seed=42)
    F.glitch_bars(66.56, seed=43)
    F.word(63.30, 66.40, "WHO", 450, 330, 205, anim="whip_l", chroma=1,
           pulses=[(63.75, 1.04), (64.20, 1.06)])
    F.word(64.20, 66.40, "IS", 890, 560, 210, hollow=True, color=EMBER_C,
           anim="slam_rot", rot=8)
    F.word(65.10, 66.40, "SHE?", 1360, 805, 245, anim="whip_r", chroma=1,
           glitch=[65.15], pulses=[(65.55, 1.04), (66.00, 1.06)])
    F.word(61.85, 66.40, "让所有人都在问  她是谁？", 960, 1010, 46, font="cn",
           tracking=2.0, border=1.6, border_alpha=0x50, alpha=0x12, anim="fade")
    F.flash(66.55, WHITE_C, 0xBE, 0.09)
    F.word(66.50, 67.85, "WHO IS SHE?", 960, 540, 255, anim="slam",
           glitch=[66.58, 66.66], chroma=1)
    F.word(66.50, 67.85, "WHO IS SHE?", 960, 540, 255, alpha=0xE0, anim="cut",
           layer=2)
    F.flash(67.92, BLACK_C, 0x00, 0.16, layer=7)
    return F.build()


def main():
    out_dir = os.path.join(ROOT, "输出", "样片_炸裂版")
    os.makedirs(out_dir, exist_ok=True)
    for key in ("16x9", "9x16"):
        ass = sample(key)
        path = os.path.join(out_dir, "FLARE_小样_%s.ass" % key)
        with open(path, "w", encoding="utf-8-sig", newline="\n") as f:
            f.write(ass)
        print("WROTE", path)


if __name__ == "__main__":
    main()





