# -*- coding: utf-8 -*-
"""Render the FLARE ultra-wide subtitle sample: graded base + burned ASS."""
import os
import subprocess
import sys

from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import grade_ffmpeg as G
import flare_wide as FW

OUT = os.path.join(os.path.dirname(BASE), "输出", "字幕小样")
FF = G.FF
MASK = os.path.join(os.path.dirname(BASE), "输出", "调色测试", "_mask_final.png")

os.makedirs(OUT, exist_ok=True)


def main():
    # 1) graded base 15s
    G.START, G.DUR = FW.T0, FW.DUR
    base = os.path.join(OUT, "_base_graded_15s.mp4")
    if not os.path.exists(base):
        G.render(MASK, base, bg_dim=-0.085, bg_sat=0.68, bg_cool=0.10,
                 sub_gain=0.050, sub_sat=1.15, bloom=0.30, vignette=0.38, soft=1.3)
    # 2) ASS
    ass_path = os.path.join(OUT, "FLARE_ultrawide_15s.ass")
    with open(ass_path, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(FW.build())
    # 3) burn (cwd = OUT, relative ascii ass name)
    out = os.path.join(OUT, "字幕小样_FLARE_15s.mp4")
    cmd = [FF, "-v", "error", "-y", "-i", base,
           "-vf", "ass=FLARE_ultrawide_15s.ass",
           "-c:v", "libx264", "-preset", "medium", "-crf", "16",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    p = subprocess.run(cmd, cwd=OUT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    print("burn", p.returncode, (p.stderr or "")[-500:])
    # 4) stills
    times = (52.6, 56.4, 59.6, 61.0, 64.2)
    files = []
    for t in times:
        fp = os.path.join(OUT, "_st_%.1f.jpg" % t)
        subprocess.run([FF, "-v", "error", "-ss", "%.2f" % (t - FW.T0), "-i", out,
                        "-frames:v", "1", "-q:v", "2", "-y", fp], capture_output=True)
        files.append(fp)
    ims = [Image.open(f).convert("RGB") for f in files]
    tw, th = 1280, 540
    sheet = Image.new("RGB", (tw * 2, th * 3), (10, 9, 8))
    for i, im in enumerate(ims[:5]):
        sheet.paste(im.resize((tw, th), Image.LANCZOS), ((i % 2) * tw, (i // 2) * th))
    # last cell: info
    sheet.save(os.path.join(OUT, "小样_关键帧.jpg"), quality=90)
    print("done", out)


if __name__ == "__main__":
    main()

