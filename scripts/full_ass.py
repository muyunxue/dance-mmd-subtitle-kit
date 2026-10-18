# -*- coding: utf-8 -*-
"""Generate full-length S4 (mix&match) and S6 (hand-marker) ASS for the 165s MMD video.

Reads cues.json (per-cue character bbox) produced by full_analysis.py and lays the
lyric typography out in character-free side columns.
"""
import json
import os
import random

from PIL import ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
OUT = os.path.join(ROOT, "输出", "S4S6_完整版")
FONTS = os.path.join(BASE, "fonts")
WIN = r"C:\Windows\Fonts"
W, H = 2560, 1080

F_ARCHIVO = os.path.join(FONTS, "ArchivoBlack-Regular.ttf")
F_BEBAS = os.path.join(FONTS, "BebasNeue-Regular.ttf")
F_ANTON = os.path.join(FONTS, "Anton-Regular.ttf")
F_GEORGIAI = os.path.join(WIN, "georgiai.ttf")
F_GEORGIA = os.path.join(WIN, "georgia.ttf")
F_SILK = os.path.join(FONTS, "Silkscreen-Regular.ttf")
F_MARKER = os.path.join(FONTS, "PermanentMarker-Regular.ttf")
F_MSYH = os.path.join(WIN, "msyh.ttc")

C_WHITE = "&H00F4F1EA&"
C_CREAM = "&H00D7EEF8&"
C_PINK = "&H00B35CFF&"
C_LAV = "&H00FFA4C4&"
C_GOLD = "&H0054C9FF&"
C_INK = "&H00140F11&"

# ---------------- lyric specs: (role, text, opts) ----------------
SPECS = {
    0: [("sub", "I FEEL IT"), ("hero", "SILENCE"), ("mid", "GETTIN' DEEPER", {"serif": True}),
        ("accent", "息のむ瞬間", {"jp": True})],
    1: [("sub", "弾けそう", {"jp": True}), ("hero", "FIRE", {"color": C_PINK}),
        ("sub", "I KNOW I'M GONNA BE THE GIRL IN", {"serif": True})],
    2: [("sub", "WE DON'T"), ("hero", "THINK TWICE")],
    3: [("sub", "I GUESS", {"serif": True}), ("mid", "YOU'LL NEVER KNOW", {"serif": True})],
    4: [("sub", "灰の中に咲く", {"jp": True}), ("hero", "MIRACLE"),
        ("mid", "MAGICAL", {"serif": True})],
    5: [("sub", "底なしにハマる", {"jp": True}), ("mid", "3 2 1"),
        ("hero2", "WHO IS SHE?", {"serif": True})],
    6: [("sub", "WHEN I"), ("hero", "WALK"), ("mid", "ONTO THE STAGE"),
        ("accent", "YEAH I GOT THIS")],
    7: [("sub", "息が燃え出す", {"jp": True}), ("mid", "キュンと", {"jp": True}),
        ("hero", "HEARTBEAT")],
    8: [("sub", "COME AROUND"), ("hero", "BABY"), ("mid", "YOU CAN COME"),
        ("accent", "AND SEE ME")],
    9: [("sub", "MAKING EVERYBODY GO"), ("hero", "WHO IS"), ("hero2", "SHE?", {"color": C_PINK})],
    10: [("sub", "WHEN I"), ("hero", "STEP"), ("mid", "ONTO THE STAGE"),
         ("accent", "YEAH I GOT THIS")],
    11: [("sub", "息つけない", {"jp": True}), ("mid", "MOOD"), ("hero", "HEARTBEAT")],
    12: [("sub", "FEEL THE"), ("hero", "FIRE", {"color": C_PINK}), ("mid", "BABY"),
         ("accent", "YOU CAN COME AND SEE ME")],
    13: [("sub", "MAKING EVERYBODY GO"), ("hero", "WHO IS"), ("hero2", "SHE?", {"color": C_PINK})],
    14: [("sub", "I CAN BE"), ("hero", "HOT"), ("mid", "I CAN BE"), ("hero2", "COLD")],
    15: [("sub", "BORN TO BE"), ("hero", "X"), ("mid", "NOBODY KNOWS", {"serif": True})],
    16: [("sub", "妄想", {"jp": True}), ("hero", "TRIGGER"), ("accent", "GOTTA JUST BREATHE IN")],
    17: [("sub", "I'M THE WHOLE"), ("hero", "DAMN SHOW")],
    18: [("sub", "WHO'S THE ONE"), ("hero", "RESET")],
    19: [("sub", "また", {"jp": True}), ("mid", "SHHH"), ("hero", "BURN")],
    20: [("sub", "集中して燃えて", {"jp": True}), ("hero", "WATCH ME"), ("accent", "NOW NOW")],
    21: [("sub", "I GUESS", {"serif": True}), ("mid", "NEVER KNOW", {"serif": True})],
    22: [("sub", "壊れて花咲く", {"jp": True}), ("hero", "MIRACLE"),
         ("mid", "MAGICAL", {"serif": True})],
    23: [("sub", "奥深く刺さる", {"jp": True}), ("accent", "3 2 1"),
         ("hero2", "WHO IS SHE?", {"serif": True})],
    24: [("sub", "WHEN I"), ("hero", "WALK"), ("mid", "ONTO THE STAGE"),
         ("accent", "YEAH I GOT THIS")],
    25: [("sub", "息が燃え出す", {"jp": True}), ("mid", "キュンと", {"jp": True}),
         ("hero", "HEARTBEAT")],
    26: [("sub", "COME AROUND"), ("hero", "BABY"), ("mid", "YOU CAN COME"),
         ("accent", "AND SEE ME")],
    27: [("sub", "MAKING EVERYBODY GO"), ("hero", "WHO IS"), ("hero2", "SHE?", {"color": C_PINK})],
    28: [("sub", "WHEN I"), ("hero", "MOVE"), ("mid", "ONTO THE STAGE"),
         ("accent", "YEAH I GOT THIS")],
    29: [("sub", "息が燃え出す", {"jp": True}), ("mid", "キュンと", {"jp": True}),
         ("hero", "HEARTBEAT")],
    30: [("sub", "感じたら", {"jp": True}), ("hero", "VIBE"), ("mid", "BABY"),
         ("accent", "BREATHING")],
    31: [("sub", "MAKING EVERYBODY GO"), ("hero", "WHO IS"), ("hero2", "SHE?", {"color": C_PINK})],
    32: [("sub", "WHEN I"), ("hero", "MOVE"), ("mid", "ONTO THE STAGE"),
         ("accent", "YEAH I GOT THIS")],
    33: [("sub", "息つけない", {"jp": True}), ("mid", "MOOD"), ("hero", "HEARTBEAT")],
    34: [("sub", "感じたら", {"jp": True}), ("hero", "VIBE"), ("mid", "BABY"),
         ("accent", "BREATHING")],
    35: [("sub", "MAKING EVERYBODY GO"), ("hero", "WHO IS"), ("hero2", "SHE?", {"color": C_PINK})],
}

STICKY_TEXTS = ["oct.18", "diary no.7", "stage 06", "i'm the one", "she can't stop", "no.2"]


def ts(sec):
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int(sec % 3600 // 60)
    return "%d:%02d:%05.2f" % (h, m, sec - h * 3600 - m * 60)


def measure(text, fontpath, size):
    try:
        f = ImageFont.truetype(fontpath, int(size))
        return f.getlength(text)
    except Exception:
        return len(text) * size * 0.6


def esc(text):
    return text.replace("{", "(").replace("}", ")")


class Ass:
    def __init__(self):
        self.ev = []

    def add(self, layer, t0, t1, tags, text):
        self.ev.append((layer, round(t0, 3), round(t1, 3), tags, esc(text)))

    def write(self, path, shift=0.0, window=None):
        evs = []
        for layer, t0, t1, tags, text in self.ev:
            a, b = t0 - shift, t1 - shift
            if window:
                a, b = max(a, window[0]), min(b, window[1])
            if b <= a + 0.02:
                continue
            evs.append((layer, a, b, tags, text))
        evs.sort(key=lambda e: (e[0], e[1]))
        head = """[Script Info]
ScriptType: v4.00+
PlayResX: 2560
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: X,Microsoft YaHei,100,&H00F4F1EA,&H00F4F1EA,&H00140F11,&HFF000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        lines = ["Dialogue: %d,%s,%s,X,,0,0,0,,{%s}%s"
                 % (l, ts(t0), ts(t1), tags, text) for l, t0, t1, tags, text in evs]
        with open(path, "w", encoding="utf-8-sig", newline="\n") as f:
            f.write(head + "\n".join(lines) + "\n")
        return len(lines)


# ------------------------------------------------------------------ styles
def style_spec(style, cue_i):
    """Return dict role->dict(font, color, size, track, serif)."""
    if style == "S4":
        return {
            "hero": dict(path=F_ARCHIVO, name="Archivo Black", color=C_WHITE, size=150, track=2),
            "hero2": dict(path=F_BEBAS, name="Bebas Neue", color=C_CREAM, size=128, track=6),
            "mid": dict(path=F_BEBAS, name="Bebas Neue", color=C_CREAM, size=88, track=4),
            "sub": dict(path=F_GEORGIAI, name="Georgia", color=C_CREAM, size=58,
                        track=1, italic=True),
            "accent": dict(path=F_ANTON, name="Anton", color=C_GOLD, size=40, track=8),
            "jp": dict(path=F_MSYH, name="Microsoft YaHei", color=C_WHITE, size=64, track=2),
        }
    else:
        return {
            "hero": dict(path=F_MARKER, name="Permanent Marker", color=C_INK, size=200, track=0),
            "hero2": dict(path=F_MARKER, name="Permanent Marker", color=C_CREAM, size=145, track=0),
            "mid": dict(path=F_MARKER, name="Permanent Marker", color=C_CREAM, size=92, track=0),
            "sub": dict(path=F_MARKER, name="Permanent Marker", color=C_CREAM, size=56, track=0),
            "accent": dict(path=F_MARKER, name="Permanent Marker", color=C_GOLD, size=40, track=0),
            "jp": dict(path=F_MSYH, name="Microsoft YaHei", color=C_CREAM, size=60, track=1),
        }


def text_event(a, style, layer, t0, t1, text, x, y, fs, font_name, color,
               rot=0.0, anim="fade", italic=False, track=0, fade_in=140, fade_out=180):
    b = "\\an5\\pos(%d,%d)\\fn%s\\fs%d\\fsp%.1f\\1c%s\\bord0\\3c&H00140F11&\\shad0"
    base = b % (int(x), int(y), font_name, int(fs), track, color)
    if italic:
        base += "\\i1"
    if anim == "slam":
        ent = ("\\fscx118\\fscy118\\blur(6)"
               "\\t(0,130,\\fscx100\\fscy100\\blur(0))")
    elif anim == "rot":
        ent = ("\\frz%.1f\\t(0,180,\\frz%.1f)" % (rot + 7, rot))
    elif anim == "rise":
        ent = "\\move(%d,%d,%d,%d,0,220)" % (x, y + 50, x, y)
    elif anim == "slide":
        ent = "\\move(%d,%d,%d,%d,0,200)" % (x - 90, y, x, y)
    else:
        ent = ""
    a.add(layer, t0, t1, base + "\\frz%.1f" % rot + ent + "\\fad(%d,%d)" % (fade_in, fade_out),
          text)


def rect_event(a, layer, t0, t1, x, y, w, h, color, alpha="&H50&", rot=0.0,
               blur=0, sweep=False):
    cx, cy = x + w / 2, y + h / 2
    tags = ("\\an7\\pos(%d,%d)\\p1\\bord0\\shad0\\1c%s\\1a%s\\frz%.1f\\blur(%d)\\org(%.1f,%.1f)"
            % (int(x), int(y), color, alpha, rot, blur, cx, cy))
    if sweep:
        tags += "\\fscx0\\t(0,180,\\fscx100)"
    tags += "\\fad(60,150)"
    draw = "m 0 0 l %d 0 %d %d 0 %d" % (int(w), int(w), int(h), int(h))
    a.add(layer, t0, t1, tags, draw)


def line_event(a, layer, t0, t1, x1, y, x2, color, alpha="&H60&", thick=3, rot=0.0):
    rect_event(a, layer, t0, t1, x1, y, x2 - x1, thick, color, alpha, rot,
               blur=0)


def glyph(a, layer, t0, t1, ch, x, y, fs, color, rot=0.0):
    a.add(layer, t0, t1,
          "\\an5\\pos(%d,%d)\\fnMicrosoft YaHei\\fs%d\\1c%s\\bord0\\shad0\\frz%.1f\\fad(200,200)"
          % (int(x), int(y), int(fs), color, rot), ch)


# ------------------------------------------------------------------ layout
def build(style, cues, seed=7):
    rnd = random.Random(seed)
    a = Ass()
    colored = (style == "S4")
    for cue in cues:
        i = cue["i"]
        t0, t1 = cue["start"], cue["end"]
        elems = SPECS.get(i, [("sub", cue["text"])])
        ss = style_spec(style, i)
        bx0, bx1 = cue["bbox"][0], cue["bbox"][1]
        # fallback when occupancy analysis was contaminated by lighting changes
        if bx1 - bx0 > 2300 or bx1 - bx0 < 260:
            bx0, bx1 = 900, 1660
        left_w = max(0, bx0 - 70 - 80)
        right_w = max(0, 2470 - (bx1 + 70))
        # prefer the wider side, alternate when both are comfortable
        if left_w > 620 and right_w > 620:
            side = "L" if (i % 2 == 0) else "R"
        else:
            side = "L" if left_w >= right_w else "R"
        col_w = left_w if side == "L" else right_w
        cx = 80 + left_w / 2 if side == "L" else bx1 + 70 + right_w / 2
        cx = max(160, min(2400, cx))

        # measure / scale
        plan = []
        max_w = 0
        for role, text, *opts in elems:
            o = opts[0] if opts else {}
            key = "jp" if o.get("jp") else role
            sp = ss[key]
            serif = False if style == "S6" else o.get("serif", False)
            path = F_GEORGIAI if serif else sp["path"]
            name = "Georgia" if serif else sp["name"]
            size = sp["size"]
            w = measure(text, path, size * (0.79 if style == "S6" else 1.0)) * 1.08
            plan.append(dict(role=role, text=text, o=o, path=path, name=name,
                             size=size, w=w, serif=serif))
            max_w = max(max_w, w)
        scale = 1.0
        if col_w > 0 and max_w > col_w - 30:
            scale = max(0.52, (col_w - 30) / max_w)
        for p in plan:
            p["size"] = p["size"] * scale
            p["w"] = p["w"] * scale
        heights = []
        for p in plan:
            h = p["size"] * (1.12 if style == "S4" else 1.0) + 20
            heights.append(h)
        gap = 16 * scale
        total_h = sum(heights) + gap * (len(plan) - 1)
        if total_h > 850:
            f = 850 / total_h
            for p in plan:
                p["size"] *= f
                p["w"] *= f
            heights = [h * f for h in heights]
            total_h = 850
        y = max(120, 520 - total_h / 2)
        if y + total_h > 1000:
            y = 1000 - total_h

        # decorations behind (S4 tape/block, S6 highlighter)
        for k, p in enumerate(plan):
            p["y"] = y + heights[k] / 2
            y += heights[k] + gap

        # hero decorations
        for p in plan:
            if p["role"] in ("hero", "hero2"):
                rot = rnd.uniform(-6, 6)
                p["rot"] = rot
                if style == "S4":
                    dup = p["role"] == "hero"
                    rect_event(a, 1, t0, t1, cx - p["w"] / 2 - 20,
                               p["y"] - p["size"] * 0.46,
                               p["w"] + 40, p["size"] * 0.92,
                               C_LAV if dup else C_PINK, "&H55&", rot + 2, blur=0.5,
                               sweep=True)
                else:
                    rect_event(a, 1, t0, t1, cx - p["w"] / 2 - 18,
                               p["y"] - p["size"] * 0.34,
                               p["w"] + 36, p["size"] * 0.68,
                               C_PINK, "&H58&", rot + 2, blur=2, sweep=True)
            else:
                p["rot"] = rnd.uniform(-3, 3)

        # sub/mid occasional block (S4)
        if style == "S4" and i % 3 == 2:
            mid = next((p for p in plan if p["role"] == "mid"), None)
            if mid:
                rect_event(a, 1, t0, t1, cx - mid["w"] / 2 - 14,
                           mid["y"] - mid["size"] * 0.5,
                           mid["w"] + 28, mid["size"], "&H00562A3A&", "&H50&", 0)

        # texts
        for k, p in enumerate(plan):
            st = t0 + 0.04 + k * 0.10
            anim = "slam" if p["role"] in ("hero", "hero2") else ("rise" if p["role"] == "sub" else "rot")
            color = p["o"].get("color") or ss["jp" if p["o"].get("jp") else p["role"]]["color"]
            if style == "S6":
                if p["role"] == "hero":
                    color = p["o"].get("color") or C_INK
                elif p["role"] == "hero2":
                    color = p["o"].get("color") or C_CREAM
            fade_out = 420 if i == 35 else 180
            text_event(a, style, 2, st, t1, p["text"], cx, p["y"], p["size"],
                       p["name"], color, rot=p["rot"], anim=anim,
                       italic=p["serif"], track=ss["jp"]["track"] if p["o"].get("jp") else 0,
                       fade_in=120, fade_out=fade_out)

        # accents / doodles
        if style == "S4":
            acc = next((p for p in plan if p["role"] == "accent"), None)
            if acc and i % 2 == 0:
                line_event(a, 1, t0, t1, cx - acc["w"] / 2, acc["y"] + acc["size"] * 0.75,
                           cx + acc["w"] / 2, C_GOLD, "&H70&", 3)
            if i % 3 == 1:
                glyph(a, 3, t0, t1, "★", cx + max(p["w"] for p in plan) / 2 + 30,
                      plan[0]["y"] - 40, 44, C_PINK, rnd.uniform(-15, 15))
            if i % 5 == 3:
                glyph(a, 3, t0, t1, "♥", cx + max(p["w"] for p in plan) / 2 + 26,
                      plan[-1]["y"] + 30, 40, C_LAV, rnd.uniform(-10, 10))
        else:
            if i % 2 == 0:
                glyph(a, 3, t0, t1, "♥", cx + max(p["w"] for p in plan) / 2 + 34,
                      plan[0]["y"], 38, C_PINK, rnd.uniform(-12, 12))
            if i % 3 == 1:
                glyph(a, 3, t0, t1, "★", cx + max(p["w"] for p in plan) / 2 + 28,
                      plan[-1]["y"], 36, C_GOLD, rnd.uniform(-10, 10))
            # sticky note every 5th cue
            if i % 5 == 0:
                nw, nh = 330, 120
                nx = 120 if side == "R" else 2110
                ny = 150 if i % 10 == 0 else 810
                ntxt = STICKY_TEXTS[(i // 5) % len(STICKY_TEXTS)]
                rect_event(a, 1, t0, t1, nx, ny, nw, nh, C_CREAM, "&H10&",
                           rnd.uniform(-5, 5), blur=0)
                a.add(2, t0, t1,
                      "\\an5\\pos(%d,%d)\\fnPermanent Marker\\fs42\\1c%s\\bord0\\shad0"
                      "\\frz%.1f\\fad(160,180)"
                      % (int(nx + nw / 2), int(ny + nh / 2), C_INK, rnd.uniform(-5, 5)),
                      ntxt)

    # instrumental ambience (108.6 – 126.2)
    for k, tt in enumerate((113.5, 116.8, 120.1, 123.4)):
        ch = "♪"
        col = C_LAV if style == "S4" else C_PINK
        x = 300 + (k % 2) * 1900
        glyph(a, 2, tt, tt + 2.4, ch, x, 520 + (k % 3) * 60,
              90 if style == "S4" else 100, col, rnd.uniform(-12, 12))
    return a


def main():
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "cues.json"), encoding="utf-8") as f:
        cues = json.load(f)
    for style, name in (("S4", "-s4-full"), ("S6", "-s6-full")):
        a = build(style, cues)
        n = a.write(os.path.join(OUT, "_%s_full.ass" % style.lower()))
        print(style, "events", n)
        # 20s test window 40-60 shifted to 0
        n2 = a.write(os.path.join(OUT, "_%s_test.ass" % style.lower()), shift=40.0,
                     window=(0.0, 20.0))
        print(style, "test events", n2)


if __name__ == "__main__":
    main()
