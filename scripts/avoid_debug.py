# -*- coding: utf-8 -*-
"""Analysis figure + overlap stats for the subject-aware subtitle demo."""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import avoid_demo as A

OUT = A.OUT
FF = A.FFMPEG
VIDEO = os.path.join(OUT, "演示素材_舞者.mp4")
MSYH = r"C:\Windows\Fonts\msyh.ttc"
CYAN = (60, 220, 235)
EMBER = (255, 110, 70)


def frame_at(t):
    path = os.path.join(OUT, "_dbg_%.2f.jpg" % t)
    subprocess.run([FF, "-v", "error", "-ss", "%.3f" % t, "-i", VIDEO,
                    "-frames:v", "1", "-q:v", "2", "-y", path], capture_output=True)
    return Image.open(path).convert("RGB")


def mask_edges(mask):
    m = mask.astype(np.uint8)
    e = np.zeros_like(m)
    e[1:, :] |= (m[1:, :] != m[:-1, :])
    e[:, 1:] |= (m[:, 1:] != m[:, :-1])
    return e.astype(bool)


def cue_idx(t0, t1):
    return list(range(int(t0 * A.FPS), min(A.NF, int(t1 * A.FPS) + 1), 6))


def heat(avg, size=(160, 90)):
    norm = avg / max(1e-6, avg.max())
    m = np.clip(norm * 255, 0, 255).astype(np.uint8)
    img = np.zeros((*m.shape, 3), np.uint8)
    img[:, :, 0] = m
    img[:, :, 1] = (m * 0.35).astype(np.uint8)
    return Image.fromarray(img).resize(size, Image.BILINEAR)


def main():
    d = np.load(os.path.join(OUT, "analysis.npz"))
    occ = d["occ"]
    masks = np.load(os.path.join(OUT, "masks.npz"))
    fixed = A.fixed_layouts()

    # auto layouts
    auto = []
    for (t0, t1, text, cn, accent) in A.CUE_DEFS:
        idx = cue_idx(t0, t1)
        lay = A.choose_layout(text, cn, idx, occ)
        lay["accent"] = accent
        lay["t0"], lay["t1"] = t0, t1
        auto.append(lay)

    # overlap stats
    auto_ov, fixed_ov = [], []
    for lay in auto:
        avg = occ[cue_idx(lay["t0"], lay["t1"])].mean(axis=0)
        x1, y1, x2, y2 = lay["block"]
        auto_ov.append(A.rect_overlap(avg, x1, y1, x2, y2))
    for (t0, t1, lay) in fixed:
        idx = cue_idx(t0, t1)
        avg = occ[idx].mean(axis=0)
        fs = lay["fs"]
        width = max(A.text_width(r, fs) for r in lay["rows"])
        x1, x2 = lay["cx"] - width / 2, lay["cx"] + width / 2
        y1 = lay["main_top"]
        y2 = lay["cn_top"] + 62
        fixed_ov.append(A.rect_overlap(avg, x1, y1, x2, y2))
    hit = lambda arr: sum(1 for r in arr if r > 0.03)
    print("fixed overlaps", [round(r, 3) for r in fixed_ov], "hit", hit(fixed_ov))
    print("auto  overlaps", [round(r, 3) for r in auto_ov], "hit", hit(auto_ov))
    with open(os.path.join(OUT, "stats.txt"), "w", encoding="utf-8") as f:
        f.write("固定底部：%d/6 句压到人物，单句平均占位重叠 %s\n" %
                (hit(fixed_ov), [round(r, 3) for r in fixed_ov]))
        f.write("自动避让：%d/6 句压到人物，单句平均占位重叠 %s\n" %
                (hit(auto_ov), [round(r, 3) for r in auto_ov]))

    # figure: 4 moments, mask contour + chosen block + heatmap
    picks = [(0, 1.0), (1, 3.0), (2, 5.2), (4, 9.4)]
    panels = []
    for (ci, t) in picks:
        lay = auto[ci]
        img = frame_at(t)
        fidx = int(round(t * A.FPS))
        key = str(min(masks.files, key=lambda k: abs(int(k) - fidx)))
        ed = mask_edges(masks[key])
        up = Image.fromarray((ed * 255).astype(np.uint8)).resize((A.W, A.H), Image.NEAREST)
        arr = np.asarray(img).copy()
        arr[np.asarray(up) > 0] = np.array(CYAN, np.uint8)
        img = Image.fromarray(arr)
        draw = ImageDraw.Draw(img)
        x1, y1, x2, y2 = lay["block"]
        draw.rectangle([x1, y1, x2, y2], outline=EMBER, width=5)
        f_cn = ImageFont.truetype(MSYH, 26)
        f_small = ImageFont.truetype(MSYH, 20)
        draw.text((x1 + 14, y1 + 8), "自动选位框", font=f_cn, fill=EMBER)
        avg = occ[cue_idx(lay["t0"], lay["t1"])].mean(axis=0)
        img.paste(heat(avg), (A.W - 200, 40))
        draw.text((A.W - 200, 138), "人物占位热区", font=f_small, fill=(225, 225, 225))
        draw.text((40, 34), "t=%.1fs  青色=检测到的人物区域" % t, font=f_cn,
                  fill=(240, 240, 240))
        draw.text((40, 82), '%s  →  字号 %d / %d 行 / 落点 (%d,%d)' %
                  (lay["text"], lay["fs"], len(lay["rows"]), lay["cx"], lay["main_top"]),
                  font=f_small, fill=(200, 200, 200))
        panels.append(img)

    tw, th = 900, 506
    sheet = Image.new("RGB", (1820, 1040), (10, 9, 8))
    for i, im in enumerate(panels):
        sheet.paste(im.resize((tw, th), Image.LANCZOS),
                    ((i % 2) * (tw + 12) + 4, (i // 2) * (th + 14) + 4))
    sheet.save(os.path.join(OUT, "分析_占位与选位.jpg"), quality=93)
    print("figure ok")


if __name__ == "__main__":
    main()
