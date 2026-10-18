# -*- coding: utf-8 -*-
"""Render the 9:16 sample + transparent overlay samples."""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flare
import build as B
import flare_video as V

SAMPLES = V.SAMPLES
FF = B.FFMPEG


def render_alpha_overlay(key):
    tmp_ass = "_flare_%s.ass" % key
    if not os.path.exists(os.path.join(SAMPLES, tmp_ass)):
        V.render_sample(key)          # also produces the shifted ass
    w, h = {"16x9": (1920, 1080), "9x16": (1080, 1920)}[key]
    out = os.path.join(SAMPLES, "叠加层_炸裂版_小样_%s_透明.webm" % key)
    src = "color=c=black@0.0:s=%dx%d:r=30:d=%.3f,format=rgba" % (w, h, V.DUR)
    cmd = [FF, "-v", "error", "-y", "-f", "lavfi", "-i", src,
           "-vf", "ass=%s:alpha=1" % tmp_ass,
           "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0",
           "-crf", "30", "-row-mt", "1", "-auto-alt-ref", "0",
           "-metadata:s:v:0", "alpha_mode=1", out]
    p = subprocess.run(cmd, cwd=SAMPLES, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    print("ALPHA", key, "rc", p.returncode, (p.stderr or "")[-200:])


if __name__ == "__main__":
    for key in ("16x9", "9x16"):
        V.render_sample(key)
    for key in ("16x9", "9x16"):
        render_alpha_overlay(key)
    print("DONE")
