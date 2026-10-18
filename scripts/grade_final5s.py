# -*- coding: utf-8 -*-
"""Final 5s sample: refined subject-pop grade (wide soft light falloff)."""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grade_ffmpeg as G

OUT = G.OUT
W, H = G.W, G.H


def make_mask_final(path,
                    cx=0.515, cy=0.565, rx=0.245, ry=0.47, power=0.55):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    q = ((xx - W * cx) / (W * rx)) ** 2 + ((yy - H * cy) / (H * ry)) ** 2
    m = np.clip(1.0 - q, 0, 1) ** power
    m = (m * 255).astype(np.uint8)
    Image.fromarray(m).save(path)
    return path


def main():
    mask = make_mask_final(os.path.join(OUT, "_mask_final.png"))
    out = os.path.join(OUT, "调色_成品方向_5s.mp4")
    G.render(mask, out,
             bg_dim=-0.085, bg_sat=0.68, bg_cool=0.10,
             sub_gain=0.050, sub_sat=1.15, bloom=0.30,
             vignette=0.38, soft=1.3)
    orig = os.path.join(OUT, "原片_5s.mp4")
    if os.path.exists(orig):
        G.stack(orig, out, "对比_原片vs成品_5s.mp4", "原片", "调色 · 成品方向")
    # stills
    cells = []
    for name, path in (("o", orig), ("f", out)):
        p = G.grab(path, 1.2, os.path.join(OUT, "_fin_%s.jpg" % name))
        cells.append(Image.open(p).convert("RGB"))
    x1, x2, y1, y2 = 850, 1900, 150, 1050
    sheet = Image.new("RGB", (1000, 429 + 32), (12, 10, 9))
    f = ImageFont.truetype(G.MSYH, 22)
    d = ImageDraw.Draw(sheet)
    for i, (im, lab) in enumerate(((cells[0], "原片"), (cells[1], "调色 · 成品方向"))):
        sheet.paste(im.crop((x1, y1, x2, y2)).resize((500, 429), Image.LANCZOS), (i * 500, 30))
        d.text((i * 500 + 12, 6), lab, font=f, fill=(240, 240, 240))
    sheet.save(os.path.join(OUT, "对比_成品_人物特写.jpg"), quality=92)
    print("done", out)


if __name__ == "__main__":
    main()
