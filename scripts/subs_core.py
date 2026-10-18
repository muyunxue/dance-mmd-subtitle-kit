# -*- coding: utf-8 -*-
"""
Who is she (Japanese Ver.) · 舞蹈字幕
Art direction: 「灰与火 / ASH & EMBER」
ivory serif type · ember accents · breathing rules · heartbeat in the break
"""
import os
import re

from PIL import ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
OUT = os.path.join(ROOT, "输出")

# ---------------------------------------------------------------- colours ----
def C(rgb):
    r, g, b = rgb
    return "&H%02X%02X%02X&" % (b, g, r)

IVORY     = C((255, 244, 230))
EMBER     = C((255, 91, 61))
GOLD      = C((245, 199, 120))
ASH       = C((167, 158, 147))
PALE      = C((226, 216, 202))
ICE       = C((163, 200, 216))
NEARBLACK = C((12, 10, 9))

ACCENT_COLORS = {"ember": EMBER, "gold": GOLD, "ice": ICE}

# ---------------------------------------------------------------- fonts -----
FONT_FILES = {
    "georgia_i": r"C:\Windows\Fonts\georgiai.ttf",
    "georgia":   r"C:\Windows\Fonts\georgia.ttf",
    "serif_sc":  r"C:\Windows\Fonts\STSONG.TTF",
    "sans_sc":   r"C:\Windows\Fonts\msyhl.ttc",
}
FONT_NAMES = {
    "georgia_i": "Georgia",
    "serif_sc":  "STSong",
    "sans_sc":   "Microsoft YaHei Light",
}

_font_cache = {}
def _font(key, size):
    key2 = (key, size)
    if key2 not in _font_cache:
        path = FONT_FILES[key]
        try:
            f = ImageFont.truetype(path, size, index=0)
        except Exception:
            f = ImageFont.truetype(path, size)
        _font_cache[key2] = f
    return _font_cache[key2]


def is_jp(ch):
    o = ord(ch)
    return (0x3040 <= o <= 0x30FF or 0x4E00 <= o <= 0x9FFF or 0x3000 <= o <= 0x303F
            or 0xFF01 <= o <= 0xFF60)


def split_runs(text):
    runs, cur, buf = [], None, ""
    for ch in text:
        kind = "jp" if is_jp(ch) else "lat"
        if kind != cur:
            if buf:
                runs.append((cur, buf))
            cur, buf = kind, ch
        else:
            buf += ch
    if buf:
        runs.append((cur, buf))
    return runs


def text_width(text, fs, track_lat=0.6, track_jp=3.0):
    total = 0.0
    for kind, seg in split_runs(text):
        font = _font("serif_sc" if kind == "jp" else "georgia_i", 100)
        total += font.getlength(seg) * fs / 100.0
        total += (track_jp if kind == "jp" else track_lat) * max(0, len(seg) - 1)
    return total


# ---------------------------------------------------------------- content ---
RAW = [
    (7.969,   "I feel it silence gettin' deeper 息のむ瞬間", "沉默渐深，屏住呼吸的一瞬"),
    (15.186,  "弾けそう I know I'm gonna be the girl in the fire", "快要迸裂，我注定是火中的女孩"),
    (20.408,  "(We don't think twice)", "我们从不迟疑"),
    (21.626,  "I guess you'll never know", "我想你永远不会知道"),
    (23.857,  "灰の中に咲く miracle 高鳴る鼓動は magical", "灰烬里绽放奇迹，心跳轰鸣 宛如魔法"),
    (30.942,  "底なしにハマる 3 2 1 who is she?", "无止境地沉溺，3 2 1 她是谁？"),
    (36.892,  "When I walk onto the stage yeah I got this", "当我走上舞台，是的 我自带锋芒"),
    (40.366,  "息が燃え出す キュンと heartbeat", "呼吸开始燃烧，心跳怦然"),
    (44.003,  "Come around baby you can come and see me", "靠近一点 宝贝，你可以来看我"),
    (47.577,  "Making everybody go who is she?", "让所有人都在问，她是谁？"),
    (51.179,  "When I step onto the stage yeah I got this", "当我踏上舞台，是的 我掌控全场"),
    (54.698,  "息つけない mood キュンと heartbeat", "令人屏息的氛围，心跳怦然"),
    (58.309,  "Feel the fire baby you can come and see me", "感受这火焰 宝贝，来看我吧"),
    (61.926,  "Making everybody go who is she?", "让所有人都在问，她是谁？"),
    (68.240,  "I can be hot I can be cold", "我可以炽热，也可以冰冷"),
    (69.910,  "Born to be X nobody knows", "生来就是未知数，无人知晓"),
    (71.731,  "妄想 trigger gotta just breathe in", "妄想扣动扳机，只需深呼吸"),
    (74.127,  "I'm the whole damn show yeah", "整场戏，唯我独演"),
    (75.746,  "Who's the one that takes the reset", "是谁按下了重置键"),
    (77.591,  "また \"shhh\"ってなるわ burn", "又被喝止「嘘」，却仍在燃烧"),
    (79.457,  "集中して燃えて watch me now now", "全神贯注地燃烧，现在看着我"),
    (82.139,  "I guess you'll never know", "我想你永远不会知道"),
    (84.834,  "壊れて花咲く miracle 心が目覚める magical", "破碎中开出奇迹，心苏醒 宛如魔法"),
    (91.944,  "奥深く刺さる 3 2 1 who is she?", "深深刺入心底，3 2 1 她是谁？"),
    (97.768,  "When I walk onto the stage yeah I got this", "当我走上舞台，是的 我自带锋芒"),
    (101.349, "息が燃え出す キュンと heartbeat", "呼吸开始燃烧，心跳怦然"),
    (104.854, "Come around baby you can come and see me", "靠近一点 宝贝，你可以来看我"),
    (108.440, "Making everybody go who is she?", "让所有人都在问，她是谁？"),
    (126.470, "When I move onto the stage yeah I got this", "当我游走于舞台，是的 我游刃有余"),
    (129.985, "息が燃え出す キュンと heartbeat", "呼吸开始燃烧，心跳怦然"),
    (133.577, "Feel the vibe baby 感じたら breathing", "感受这氛围 宝贝，感受到了就呼吸"),
    (137.107, "Making everybody go who is she?", "让所有人都在问，她是谁？"),
    (140.677, "When I move onto the stage yeah I got this", "当我游走于舞台，是的 我游刃有余"),
    (144.341, "息つけない mood キュンと heartbeat", "令人屏息的氛围，心跳怦然"),
    (147.939, "Feel the vibe baby 感じたら breathing", "感受这氛围 宝贝，感受到了就呼吸"),
    (151.454, "Making everybody go who is she", "让所有人都在问，她是谁"),
]

SECTION_OF = {
    0: "intro", 1: "intro", 2: "intro", 3: "intro", 4: "intro", 5: "intro",
    6: "chorus1", 7: "chorus1", 8: "chorus1", 9: "chorus1", 10: "chorus1",
    11: "chorus1", 12: "chorus1", 13: "chorus1",
    14: "verse2", 15: "verse2", 16: "verse2", 17: "verse2", 18: "verse2",
    19: "verse2", 20: "verse2", 21: "verse2", 22: "verse2", 23: "verse2",
    24: "chorus2", 25: "chorus2", 26: "chorus2", 27: "chorus2",
    28: "final", 29: "final", 30: "final", 31: "final", 32: "final",
    33: "final", 34: "final", 35: "final",
}

ACCENTS = {
    0: [], 1: [("fire", "ember")], 2: [], 3: [],
    4: [("miracle", "gold"), ("magical", "ember")],
    5: [("3 2 1", "gold"), ("who is she?", "ember")],
    6: [], 7: [("heartbeat", "ember")], 8: [],
    9: [("who is she?", "ember")], 10: [], 11: [("heartbeat", "ember")],
    12: [("fire", "ember")], 13: [("who is she?", "ember")],
    14: [("hot", "ember"), ("cold", "ice")],
    15: [("X", "gold")], 16: [], 17: [],
    18: [("reset", "ember")], 19: [("burn", "ember")], 20: [("now now", "ember")],
    21: [], 22: [("miracle", "gold"), ("magical", "ember")],
    23: [("3 2 1", "gold"), ("who is she?", "ember")],
    24: [], 25: [("heartbeat", "ember")], 26: [],
    27: [("who is she?", "ember")], 28: [], 29: [("heartbeat", "ember")],
    30: [], 31: [("who is she?", "ember")], 32: [],
    33: [("heartbeat", "ember")], 34: [], 35: [],
}

HOOK = {5, 9, 13, 23, 27, 31}
ASIDE = {2}
RAPID = set(range(14, 24))
FINAL = 35

SECTION = {
    "intro":   dict(rule=ASH,   rule_a=0x26, glow=GOLD,  glow_a=0x8A),
    "chorus1": dict(rule=EMBER, rule_a=0x1C, glow=EMBER, glow_a=0x78),
    "verse2":  dict(rule=GOLD,  rule_a=0x1E, glow=EMBER, glow_a=0x78),
    "chorus2": dict(rule=EMBER, rule_a=0x16, glow=EMBER, glow_a=0x68),
    "final":   dict(rule=EMBER, rule_a=0x16, glow=EMBER, glow_a=0x62),
}
BREAK = (112.30, 126.20)
END_HOLD = 154.60

CANVAS = {
    "16x9": dict(key="16x9", W=1920, H=1080, main=62, cn=36, aside=44, maxw=1580,
                 track_lat=0.6, track_jp=3.0, cn_bottom=974, rule_w=150),
    "9x16": dict(key="9x16", W=1080, H=1920, main=58, cn=38, aside=42, maxw=930,
                 track_lat=0.5, track_jp=2.6, cn_bottom=1640, rule_w=124),
}

# hand-tuned row breaks for the narrow vertical canvas (semantic, not just balanced)
WRAP_HINTS = {
    "9x16": {
        0: "I feel it silence gettin' deeper|息のむ瞬間",
        1: "弾けそう|I know I'm gonna be the girl in the fire",
        4: "灰の中に咲く miracle|高鳴る鼓動は magical",
        6: "When I walk onto the stage|yeah I got this",
        8: "Come around baby|you can come and see me",
        10: "When I step onto the stage|yeah I got this",
        11: "息つけない mood|キュンと heartbeat",
        12: "Feel the fire baby|you can come and see me",
        20: "集中して燃えて|watch me now now",
        22: "壊れて花咲く miracle|心が目覚める magical",
        24: "When I walk onto the stage|yeah I got this",
        26: "Come around baby|you can come and see me",
        28: "When I move onto the stage|yeah I got this",
        30: "Feel the vibe baby|感じたら breathing",
        32: "When I move onto the stage|yeah I got this",
        33: "息つけない mood|キュンと heartbeat",
        34: "Feel the vibe baby|感じたら breathing",
    }
}


def load_cues():
    cues = []
    n = len(RAW)
    for i, (t, orig, cn) in enumerate(RAW):
        end = (RAW[i + 1][0] - 0.24) if i + 1 < n else END_HOLD - 0.9
        if i == 27:
            end = BREAK[0]
        cues.append(dict(i=i, t=t, start=t - 0.12, end=end, orig=orig, cn=cn,
                         sec=SECTION_OF[i], accents=ACCENTS[i],
                         hook=i in HOOK, aside=i in ASIDE, rapid=i in RAPID,
                         final=(i == FINAL)))
    return cues


# ---------------------------------------------------------------- helpers ---
def ts(sec):
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int(sec % 3600 // 60)
    s = sec - h * 3600 - m * 60
    return "%d:%02d:%05.2f" % (h, m, s)


def cn_sub_line(cn):
    return cn.replace("，", "　").replace("、", "　")


def wrap_text(text, fs, cfg, track_lat, track_jp):
    if text_width(text, fs, track_lat, track_jp) <= cfg["maxw"]:
        return [text]
    cands = [m.end() for m in re.finditer(r"\s+", text)]
    for k in range(1, len(text)):
        if is_jp(text[k - 1]) != is_jp(text[k]):
            cands.append(k)
    best = None
    for p in cands:
        left, right = text[:p].strip(), text[p:].strip()
        if not left or not right:
            continue
        lw = text_width(left, fs, track_lat, track_jp)
        rw = text_width(right, fs, track_lat, track_jp)
        if lw > cfg["maxw"] or rw > cfg["maxw"]:
            continue
        score = abs(lw - rw) + (200 if is_jp(text[p - 1]) != is_jp(text[p]) else 0)
        if best is None or score < best[0]:
            best = (score, left, right)
    if best is None:
        mid = len(text) // 2
        return [text[:mid].strip(), text[mid:].strip()]
    return [best[1], best[2]]


def build_body(text, fs, cfg, accents=None, color=IVORY, latin_italic=1,
               track=None):
    accents = accents or []
    track = track or (cfg["track_lat"], cfg["track_jp"])
    tl, tj = track
    pieces = []
    for kind, seg in split_runs(text):
        chunks = [(seg, None)]
        for word, key in accents:
            new = []
            for s, ak in chunks:
                if ak is not None or not word:
                    new.append((s, ak))
                    continue
                low, wl = s.lower(), word.lower()
                idx = low.find(wl)
                if idx < 0:
                    new.append((s, ak))
                else:
                    new += [(s[:idx], None), (s[idx:idx + len(word)], key),
                            (s[idx + len(word):], None)]
            chunks = new
        for s, ak in chunks:
            if s:
                pieces.append((kind, s, ak))
    out = []
    for kind, s, ak in pieces:
        if kind == "jp":
            tag = "\\fn%s\\i0\\fsp%.1f\\fs%d\\1c%s" % (
                FONT_NAMES["serif_sc"], tj, fs, color)
        else:
            tag = "\\fn%s\\i%d\\fsp%.1f\\fs%d\\1c%s" % (
                FONT_NAMES["georgia_i"], latin_italic, tl, fs, color)
        if ak:
            tag += "\\1c" + ACCENT_COLORS.get(ak, EMBER)
        out.append("{" + tag + "}" + s)
    return "".join(out)


# ---------------------------------------------------------------- events ----
def draw_rule(x, y, width, color, alpha, t0, t1, collapse_at=None):
    h = 1.6
    half = width / 2.0
    shape = "m %.1f 0 l %.1f 0 %.1f %.1f %.1f %.1f" % (-half, half, half, h, -half, h)
    if collapse_at:
        cs, ce = collapse_at
        start_s = t0 + cs / 1000.0
        dur_ms = ce - cs
        tag = ("{\\an5\\pos(%d,%d)\\p1\\bord0\\shad0\\1c%s\\1a&H%02X&"
               "\\fscx0\\t(0,300,\\fscx100)\\fad(220,0)}"
               % (x, y, color, alpha))
        tag2 = ("{\\an5\\pos(%d,%d)\\p1\\bord0\\shad0\\1c%s\\1a&H%02X&"
                "\\fscx100\\t(0,%d,\\fscx0)\\fad(0,360)}"
                % (x, y, color, alpha, dur_ms))
        return ["Dialogue: 1,%s,%s,Base,,0,0,0,,%s%s" % (ts(t0), ts(start_s), tag, shape),
                "Dialogue: 1,%s,%s,Base,,0,0,0,,%s%s" % (ts(start_s), ts(t1), tag2, shape)]
    tag = ("{\\an5\\pos(%d,%d)\\p1\\bord0\\shad0\\1c%s\\1a&H%02X&"
           "\\fscx0\\t(0,300,\\fscx100)\\fad(220,340)}" % (x, y, color, alpha))
    return ["Dialogue: 1,%s,%s,Base,,0,0,0,,%s%s" % (ts(t0), ts(t1), tag, shape)]


def text_halo(body, y, t0, t1, x, alpha=0x52, bord=10, blur=17):
    tag = ("{\\an5\\pos(%d,%d)\\bord%d\\3c%s\\3a&H%02X&\\1c%s\\1a&H%02X&"
           "\\shad0\\blur(%d)\\fad(340,340)}"
           % (x, y, bord, NEARBLACK, alpha, NEARBLACK, alpha, blur))
    return "Dialogue: 0,%s,%s,Base,,0,0,0,,%s%s" % (ts(t0), ts(t1), tag, body)


def main_glow(body, y, t0, t1, x, color, alpha, blur=16):
    tag = ("{\\an5\\pos(%d,%d)\\bord0\\shad0\\blur(%d)\\1c%s\\1a&H%02X&\\fad(340,340)}"
           % (x, y, blur, color, alpha))
    return "Dialogue: 0,%s,%s,Base,,0,0,0,,%s%s" % (ts(t0), ts(t1), tag, body)


def main_event(body, y, t0, t1, x, speed="normal", hook=False):
    if speed == "fast":
        anim = "\\fad(90,190)\\blur4\\t(0,220,\\blur(0))\\fscx102\\fscy102\\t(0,240,\\fscx100\\fscy100)"
    elif speed == "slow":
        anim = "\\fad(420,900)\\blur9\\t(0,760,\\blur(0))\\fscx102\\fscy102\\t(0,980,\\fscx100\\fscy100)"
    else:
        anim = "\\fad(150,280)\\blur6\\t(0,320,\\blur(0))\\fscx103\\fscy103\\t(0,360,\\fscx100\\fscy100)"
    if hook:
        anim = "\\fad(130,300)\\blur7\\t(0,300,\\blur(0))\\fscx107\\fscy106\\t(0,420,\\fscx100\\fscy100)"
    legibility = "\\bord1.7\\3c%s\\3a&H78&\\shad0" % NEARBLACK
    tag = "{\\an5\\pos(%d,%d)%s%s}" % (x, y, anim, legibility)
    return "Dialogue: 1,%s,%s,Base,,0,0,0,,%s%s" % (ts(t0), ts(t1), tag, body)


def sub_event(text, y, t0, t1, x, fs, color=PALE, italic=0, serif=False, delay=0.12):
    fn = FONT_NAMES["serif_sc"] if serif else FONT_NAMES["sans_sc"]
    body = ("{\\fn%s\\i%d\\fsp1.6\\fs%d\\1c%s\\bord1.3\\3c%s\\3a&H74&\\shad0\\blur0.8}%s"
            % (fn, italic, fs, color, NEARBLACK, text))
    tag = "{\\an5\\pos(%d,%d)\\fad(320,340)\\blur5\\t(0,440,\\blur(0))}" % (x, y)
    return "Dialogue: 1,%s,%s,Base,,0,0,0,,%s%s" % (ts(t0 + delay), ts(t1), tag, body)


def circle_shape(r):
    """Circle as four cubic beziers (libass does not support the arc command)."""
    k = 0.5522847 * r
    return ("m 0 %.2f b %.2f %.2f %.2f %.2f %.2f 0 "
            "b %.2f %.2f %.2f %.2f 0 %.2f "
            "b %.2f %.2f %.2f %.2f %.2f 0 "
            "b %.2f %.2f %.2f %.2f 0 %.2f"
            % (-r, k, -r, r, -k, r,
               r, k, k, r, r,
               -k, r, -r, k, -r,
               -r, -k, -k, -r, -r))


def star_shape(r, waist=0.22):
    w = r * waist
    pts = [(0, -r), (w, -w), (r, 0), (w, w), (0, r), (-w, w), (-r, 0), (-w, -w)]
    return "m %.2f %.2f l " % pts[0] + " ".join("%.2f %.2f" % p for p in pts[1:])


def sweep_event(t, x, y, width, color=EMBER, alpha=0x30, dur=1.4, direction=1):
    """A thin ember line sweeping across the lower third — section transitions."""
    half = width / 2.0
    shape = "m %.1f 0.8 l %.1f 0.8 %.1f 1.8 %.1f 1.8" % (-half, half, half, -half)
    if direction > 0:
        tag = ("{\\an5\\pos(%d,%d)\\p1\\bord0\\shad0\\1c%s\\1a&H%02X&"
               "\\fscx0\\t(0,%d,\\fscx100)\\fad(260,%d)}"
               % (x, y, color, alpha, int(dur * 1000), int(dur * 1000)))
    else:
        tag = ("{\\an5\\pos(%d,%d)\\p1\\bord0\\shad0\\1c%s\\1a&H%02X&"
               "\\fscx100\\t(0,%d,\\fscx0)\\fad(260,%d)}"
               % (x, y, color, alpha, int(dur * 1000), int(dur * 1000)))
    return "Dialogue: 1,%s,%s,Base,,0,0,0,,%s%s" % (ts(t), ts(t + dur), tag, shape)


def hook_sparks(t, x, y, width, colors=None):
    """A few tiny embers lifting off the hook line."""
    colors = colors or [GOLD, GOLD, EMBER]
    xs = [-0.34, 0.02, 0.38]
    evs = []
    for k, dx in enumerate(xs):
        col = colors[k % len(colors)]
        evs += ember_spark(t + 0.10 + 0.16 * k, x + int(width * dx), y + 18,
                           color=col, drift=30 + 6 * k, dur=1.9, size=1.5 + 0.2 * (k % 2))
    return evs


def ornament_pulse(t, x, y, color=EMBER, r=15, growth=30, dur=1.4):
    """Slow ember heartbeat: a soft aura, a ring that breathes out, a glowing core."""
    ev = []
    # soft aura — the 'breath'
    tag0 = ("{\\an5\\pos(%d,%d)\\p1\\bord0\\shad0\\1c%s\\1a&H5A&\\blur(34)"
            "\\fad(420,%d)}" % (x, y, color, int(dur * 900)))
    ev.append("Dialogue: 0,%s,%s,Base,,0,0,0,,%s%s"
              % (ts(t), ts(t + dur), tag0, circle_shape(40)))
    scale_to = int(100 * (r + growth) / r)
    tag = ("{\\an5\\pos(%d,%d)\\p1\\1a&HFF&\\3c%s\\3a&H16&\\bord2.4\\shad0"
           "\\t(0,%d,\\fscx%d\\fscy%d\\3a&HFF&)}"
           % (x, y, color, int(dur * 1000), scale_to, scale_to))
    ev.append("Dialogue: 1,%s,%s,Base,,0,0,0,,%s%s"
              % (ts(t), ts(t + dur), tag, circle_shape(r)))
    tag2 = ("{\\an5\\pos(%d,%d)\\p1\\bord0\\shad0\\1c%s\\1a&H00&\\blur(3.6)"
            "\\fad(150,%d)}" % (x, y, color, int(dur * 900)))
    ev.append("Dialogue: 1,%s,%s,Base,,0,0,0,,%s%s"
              % (ts(t), ts(t + dur), tag2, circle_shape(3.4)))
    return ev


def ember_spark(t, x, y, color=GOLD, drift=30, dur=2.0, size=1.8):
    tag = ("{\\an5\\pos(%d,%d)\\p1\\bord0\\shad0\\1c%s\\1a&H20&\\blur(1.2)"
           "\\move(%d,%d,%d,%d,0,%d)\\fad(340,%d)}"
           % (x, y, color, x, y, x + int(drift * 0.3), y - drift,
              int(dur * 1000), int(dur * 850)))
    return ["Dialogue: 2,%s,%s,Base,,0,0,0,,%s%s"
            % (ts(t), ts(t + dur), tag, star_shape(size, 0.18))]


# ---------------------------------------------------------------- builder ---
def layout_for(variant, cue, cfg):
    """Return dict(rows, fs, main_ys, sub_y, sub_fs, rule_y, rule_w)."""
    W, H = cfg["W"], cfg["H"]
    bottom = cfg["cn_bottom"]
    tl, tj = cfg["track_lat"], cfg["track_jp"]
    key = cfg.get("key")

    def rows_for(text, fs):
        hint = WRAP_HINTS.get(key, {}).get(cue["i"])
        if hint:
            a, b = [s.strip() for s in hint.split("|")]
            if (a in text and b in text
                    and text_width(a, fs, tl, tj) <= cfg["maxw"]
                    and text_width(b, fs, tl, tj) <= cfg["maxw"]):
                return [a, b]
        return wrap_text(text, fs, cfg, tl, tj)

    if variant == "orig_main":
        fs = cfg["aside"] if cue["aside"] else cfg["main"]
        rows = rows_for(cue["orig"], fs)
        gap = int(fs * 1.18)
        n = len(rows)
        row_bottom = bottom - 76
        main_ys = [row_bottom - (n - 1 - k) * gap for k in range(n)]
        top = min(main_ys) - fs * 0.60
        rule_y = int(top - (30 if cue["aside"] else 38))
        return dict(rows=rows, fs=fs, main_ys=main_ys, sub_y=bottom,
                    sub_fs=cfg["cn"], rule_y=rule_y, rule_w=None)
    if variant == "cn_main":
        fs = 46 if cfg["W"] == 1920 else 44
        rows = rows_for(cue["cn"], fs)
        gap = int(fs * 1.2)
        n = len(rows)
        row_bottom = bottom - 44
        main_ys = [row_bottom - (n - 1 - k) * gap for k in range(n)]
        top = min(main_ys) - fs * 0.60
        sub_y = int(top - 30)
        rule_y = int(sub_y - 26)
        return dict(rows=rows, fs=fs, main_ys=main_ys, sub_y=sub_y,
                    sub_fs=26 if cfg["W"] == 1920 else 25, rule_y=rule_y, rule_w=None,
                    sub_col=GOLD, sub_italic=1)
    if variant == "orig_only":
        fs = cfg["aside"] if cue["aside"] else cfg["main"]
        rows = rows_for(cue["orig"], fs)
        gap = int(fs * 1.18)
        n = len(rows)
        main_ys = [bottom - (n - 1 - k) * gap for k in range(n)]
        top = min(main_ys) - fs * 0.60
        return dict(rows=rows, fs=fs, main_ys=main_ys, sub_y=None, sub_fs=0,
                    rule_y=int(top - 38), rule_w=None)
    # cn_only
    fs = 46 if cfg["W"] == 1920 else 44
    rows = rows_for(cue["cn"], fs)
    gap = int(fs * 1.2)
    n = len(rows)
    main_ys = [bottom - (n - 1 - k) * gap for k in range(n)]
    top = min(main_ys) - fs * 0.60
    return dict(rows=rows, fs=fs, main_ys=main_ys, sub_y=None, sub_fs=0,
                rule_y=int(top - 38), rule_w=None)


def build_variant(variant, canvas_key):
    cfg = CANVAS[canvas_key]
    W, H = cfg["W"], cfg["H"]
    cx = W // 2
    cues = load_cues()
    events = []

    # ---------------- dance break: heartbeat + sparks ----------------
    b0, b1 = BREAK
    orn_y = cfg["cn_bottom"] - 70
    for t in (b0 + 1.0, b0 + 4.5, b0 + 8.0, b0 + 11.5):
        events += ornament_pulse(t, cx, orn_y, dur=1.25)
    for (t, dx) in ((b0 + 2.5, -255), (b0 + 3.3, 175), (b0 + 6.9, -120),
                    (b0 + 9.6, 300), (b0 + 10.4, -350), (b0 + 12.9, 95)):
        events += ember_spark(t, cx + dx, orn_y - 10,
                              color=GOLD, drift=34, dur=2.2, size=1.7)

    # ---------------- section transitions ----------------
    # (intentionally silent: the colour of type and rule carries each new section,
    #  so the choreography keeps the frame to itself)

    for cue in cues:
        sec = SECTION[cue["sec"]]
        hook = cue["hook"]
        lay = layout_for(variant, cue, cfg)
        rows, fs, main_ys, sub_y, sub_fs = lay["rows"], lay["fs"], lay["main_ys"], lay["sub_y"], lay["sub_fs"]
        t0, t1 = cue["start"], cue["end"]

        # hook sparks (a few embers lifting off the line)
        if hook and variant in ("orig_main", "orig_only"):
            tw = text_width(" ".join(rows), fs)
            events += hook_sparks(t0 + 0.2, cx, main_ys[-1], tw)

        # rule
        if cue["aside"]:
            events += draw_rule(cx, lay["rule_y"], 96, ASH, 0x40, t0, t1)
        else:
            rw = cfg["rule_w"] + (74 if hook else 0)
            collapse = (1500, 2150) if cue["final"] else None
            events += draw_rule(cx, lay["rule_y"], rw, sec["rule"],
                                sec["rule_a"], t0, t1, collapse_at=collapse)

        speed = "fast" if cue["rapid"] else ("slow" if cue["final"] else "normal")

        if variant == "cn_main":
            for k, row in enumerate(rows):
                color = PALE if cue["final"] else IVORY
                body = build_body(row, fs, cfg, color=color, latin_italic=0)
                events.append(main_glow(body, main_ys[k], t0, t1, cx,
                                        GOLD if cue["final"] else sec["glow"],
                                        0x96 if cue["final"] else sec["glow_a"], 18))
                halo_body = build_body(row, fs, cfg, color=NEARBLACK, latin_italic=0)
                events.append(text_halo(halo_body, main_ys[k], t0, t1, cx))
                events.append(main_event(body, main_ys[k], t0, t1, cx,
                                         speed="slow" if cue["final"] else "normal"))
            body_sub = ("{\\fn%s\\i1\\fsp1.3\\fs%d\\1c%s\\bord0\\shad0\\blur0.6}%s"
                        % (FONT_NAMES["georgia_i"], sub_fs, GOLD, cue["orig"]))
            events.append("Dialogue: 1,%s,%s,Base,,0,0,0,,%s%s"
                          % (ts(t0), ts(t1),
                             "{\\an5\\pos(%d,%d)\\fad(340,360)\\blur1.5\\t(0,420,\\blur0)}"
                             % (cx, sub_y), body_sub))
        else:
            accents = cue["accents"]
            for k, row in enumerate(rows):
                color = ASH if cue["aside"] else (PALE if cue["final"] else IVORY)
                body = build_body(row, fs, cfg, accents=accents if not cue["aside"] else [],
                                  color=color)
                halo_body = build_body(row, fs, cfg, accents=[], color=NEARBLACK)
                events.append(text_halo(halo_body, main_ys[k], t0, t1, cx,
                                        alpha=0x50 if cue["aside"] else 0x5A))
                if not cue["aside"]:
                    glow_col = GOLD if cue["final"] else sec["glow"]
                    glow_a = 0x9A if cue["final"] else sec["glow_a"]
                    events.append(main_glow(body, main_ys[k], t0, t1, cx,
                                            glow_col, glow_a, 18 if hook else 16))
                events.append(main_event(body, main_ys[k], t0, t1, cx,
                                         speed=speed, hook=hook))
            if sub_y is not None:
                events.append(sub_event(cn_sub_line(cue["cn"]), sub_y, t0, t1, cx, sub_fs,
                                        color=ASH if cue["aside"] else PALE))

        # ---------------- finale: a late, dissolving question mark ----------------
        if cue["final"] and variant in ("orig_main", "orig_only"):
            last_row = rows[-1]
            tw = text_width(last_row, fs)
            qx = int(cx + tw / 2 + fs * 0.04)
            qy = main_ys[-1]
            qfs = int(fs * 0.94)
            tag = ("{\\an5\\pos(%d,%d)\\fn%s\\i1\\fs%d\\1c%s\\bord1.1\\3c%s\\3a&H70&"
                   "\\shad0\\blur0.5\\fad(880,780)}"
                   % (qx, qy, FONT_NAMES["georgia_i"], qfs, EMBER, NEARBLACK))
            events.append("Dialogue: 1,%s,%s,Base,,0,0,0,,%s?"
                          % (ts(t0 + 1.05), ts(t1), tag))

    events.sort(key=_ev_sort_key)
    return build_header(canvas_key) + "\n".join(events) + "\n"


def _ev_sort_key(line):
    # layer order guarantees the render stack; keep it stable so the shipped
    # videos and the editable .ass stay pixel-identical
    try:
        return int(line.split(",")[0].split(":")[1])
    except Exception:
        return 0


def build_header(canvas_key):
    cfg = CANVAS[canvas_key]
    return """[Script Info]
Title: Who is she (Japanese Ver.) - 舞蹈字幕 灰与火 / ASH & EMBER
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
Style: Base,%s,%d,&H00FFF4E6,&H000000FF,&H14100E,&H64000000,0,0,0,0,100,100,0,0,1,0,0,5,60,60,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" % (cfg["W"], cfg["H"], FONT_NAMES["georgia_i"], cfg["main"])


# ---------------------------------------------------------------- srt -------
def srt_ts(sec):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def build_srt(lang):
    cues = load_cues()
    out = []
    for idx, cue in enumerate(cues, 1):
        if lang == "bilingual":
            text = cue["orig"] + "\n" + cue["cn"]
        elif lang == "cn":
            text = cue["cn"]
        else:
            text = cue["orig"]
        out += [str(idx), "%s --> %s" % (srt_ts(cue["start"]), srt_ts(cue["end"])),
                text, ""]
    return "\n".join(out)
