# -*- coding: utf-8 -*-
"""Burn the NEON subtitle sample onto the graded ultra-wide base."""
import os
import subprocess
import sys

from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import flare_wide as FW
import neon_wide as NW
import grade_ffmpeg as G

OUT = os.path.join(os.path.dirname(BASE), "输出", "字幕小样")
FF = G.FF


def main():
    base = os.path.join(OUT, "_base_graded_15s.mp4")
    if not os.path.exists(base):
        G.START, G.DUR = NW.T0, NW.T1 - NW.T0
        G.render(os.path.join(os.path.dirname(BASE), "输出", "调色测试", "_mask_final.png"),
                 base, bg_dim=-0.045, bg_sat=0.87, bg_cool=0.05,
                 sub_gain=0.018, sub_sat=1.05, bloom=0.16, vignette=0.24, soft=0.5)
    ass = os.path.join(OUT, "NEON_ultrawide_15s.ass")
    with open(ass, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(NW.build())
    out = os.path.join(OUT, "字幕小样_霓虹_15s.mp4")
    cmd = [FF, "-v", "error", "-y", "-i", base,
           "-vf", "ass=NEON_ultrawide_15s.ass",
           "-c:v", "libx264", "-preset", "medium", "-crf", "16",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    p = subprocess.run(cmd, cwd=OUT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    print("burn", p.returncode, (p.stderr or "")[-600:])
    times = (51.8, 53.0, 56.2, 59.6, 61.2, 64.2)
    files = []
    for t in times:
        fp = os.path.join(OUT, "_n_%.1f.jpg" % t)
        subprocess.run([FF, "-v", "error", "-ss", "%.2f" % (t - NW.T0), "-i", out,
                        "-frames:v", "1", "-q:v", "2", "-y", fp], capture_output=True)
        files.append(fp)
    ims = [Image.open(f).convert("RGB") for f in files]
    tw, th = 1280, 540
    sheet = Image.new("RGB", (tw * 2, th * 3), (8, 7, 12))
    for i, im in enumerate(ims):
        sheet.paste(im.resize((tw, th), Image.LANCZOS), ((i % 2) * tw, (i // 2) * th))
    sheet.save(os.path.join(OUT, "小样_霓虹_关键帧.jpg"), quality=90)
    print("done", out)


if __name__ == "__main__":
    main()

