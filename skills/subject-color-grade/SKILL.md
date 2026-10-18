---
name: subject-color-grade
description: Subject-aware colour grading for the MMD dance videos in this workspace — make the dancer stand out (background dim/cool/desat, subject lift/warm/sharpen/bloom) using either a soft stage-light ellipse or a hard character matte, with ffmpeg recipes, measured parameter sets and known failure modes (cast-shadow matte contamination, banding, truncated sources). Load this when asked to 调色/突出人物/压背景/统一色调, or when a graded clip shows weird bright blobs around the dancer.
---

# MMD 主体感知调色（突出人物）

## 0. 结论先行
- MMD 舞台片想“突出人物”，两条路：
  1. **光区塑形（推荐，干净）**：以人物为中心的柔光椭圆/径向渐变——椭圆内人物提亮/暖/锐/辉光，椭圆外背景压暗/冷/降饱和/轻微虚化；边缘过渡很宽，几乎看不到“圈”。
  2. **硬抠像分离（上限高但脏）**：帧差背景板取人物 mask，人物/背景分别调色再合成。**难点是人物投影（cast shadow）会跟着人物一起动，和人物连成一片**，mask 会带上大片阴影 → 出现亮斑；强行腐蚀又啃翅膀羽毛。
- 只有成片时选 1；能从 Blender/MMD 重渲染带 alpha 的角色层时选 2（质量最高）。

## 1. 素材与工具
| 东西 | 路径 |
|---|---|
| 源片 | `D:\mmd.mp4\0002-4956.mkv`（完整 165.166s）/ `字幕\0001-4956 - 副本.mkv`（截断到 ~137s） |
| 调色脚本 | `字幕\build\grade_ffmpeg.py`（光区/柔光）、`grade_final5s.py`（5s 成品参数）、`color_grade.py`（旧版帧差抠像）、`gothic_art.py`（静态帧哥特调色） |
| 验证脚本 | `avoid_layout.py`（占用分析）、`avoid_side2.py`（占用+bbox） |
| ffmpeg | `C:\Users\35530\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe` |
| Python | `C:\Users\35530\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe`（PIL/numpy，无 cv2/深度学习） |

## 2. 路线 A：光区塑形（本项目的默认做法）

### 2.1 生成柔光 mask（一次性 PNG）
```python
import numpy as np
from PIL import Image
W,H = 2560,1080
yy,xx = np.mgrid[0:H,0:W].astype(np.float32)
cx,cy = 0.515,0.565          # 人物中心（2560x1080 竖构图约在此；换片先抽帧确认）
rx,ry = 0.245,0.47           # 半宽/半高（比例）；太小会看出圈，太大没有分离
q = ((xx-W*cx)/(W*rx))**2 + ((yy-H*cy)/(H*ry))**2
mask = np.clip(1.0-q,0,1)**0.55          # 0.5–0.7 比较柔
Image.fromarray((mask*255).astype(np.uint8)).save("_mask_final.png")
```
参考成品：`字幕\输出\调色测试\_mask_final.png`、`字幕\输出\字幕小样\_mask_final.png`。

### 2.2 ffmpeg 合成（悬浮人物 + 压暗背景）
思路：人物调色版 + 背景调色版，用 mask 做 alpha 合并：
```
[0:v]split=2[sv][bv];
[sv]eq=brightness=0.050:contrast=1.06:saturation=1.15,
    colorbalance=rs=0.02:bs=-0.02:rm=0.05:bm=-0.06:rh=0.02:bh=-0.02,
    split=2[sm][sh];[sh]gblur=sigma=14[blur];
    [sm][blur]blend=all_mode=screen:all_opacity=0.34[sub];
    [sub]format=yuva420p[suba];
[1:v]format=gray[gm];[suba][gm]alphamerge[subj];
[bv]eq=brightness=-0.045:contrast=1.07:saturation=0.87,
    colorbalance=rm=-0.03:bm=0.05,gblur=sigma=0.6[bg];
[bg][subj]overlay=0:0,format=yuv420p[v]
```
命令：
```powershell
& $ff -v error -y -ss 36.5 -t 30 -i src.mkv -loop 1 -i _mask_final.png `
  -filter_complex "<上面 graph>" -map "[v]" -t 30 `
  -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p OUT.mp4
```
> 注意：`-loop 1 -i mask.png` 时 mask 是静止流；`overlay` 结束后记得 `-t` 限长。
> 参数含义：bg brightness 负=压暗、saturation<1=降饱和、`bm>0`=背景偏蓝（冷）、`gblur`=轻微虚化；subj 里 brightness/饱和/暖色/`blend screen` 做辉光。

### 2.3 实测参数档（2560×1080，紫舞台 MMD）
| 档 | bg brightness | bg sat | subj gain | subj sat | bloom | vignette | 效果 |
|---|---|---|---|---|---|---|---|
| A 自然 | −0.035 | 0.82 | +0.030 | 1.08 | 0.20 | 0.30 | 轻提人物，几乎不改氛围 |
| B 强化 | −0.075 | 0.70 | +0.055 | 1.16 | 0.34 | 0.42 | 明显分离，光区边缘稍可见 |
| 成品方向 | −0.085 | 0.68 | +0.050 | 1.15 | 0.30 | 0.38 | 柔光很宽，推荐做全片底片 |
> 在 5s 上试参数，满意后直接套 30s/全片（ffmpeg 一次跑完，比逐帧 Python 快）。

## 3. 路线 B：硬抠像（需要更干净的 mask 时）

### 3.1 背景板
- 抽全片 1/2s 采样帧，缩到 1280×540，逐像素**中位数** = 背景板 `bg_half.npy`。
- 命令/复盘：`字幕\build\color_grade.py` 的 `build_background()`。
- 已知问题：人物长期站在中间时，中位数会被人物“污染”（人物身上某些像素常常是人物）→ 帧差在躯干处偏小 → mask 有洞。用 `fill_holes` 或 bbox 兜底。

### 3.2 帧差 mask（1/4 分辨率最快）
```python
m = |frame_q - bg_q|.max(axis=2) > 38
m = MaxFilter(5)（外扩）→ largest connected component → 可选填洞/羽化
```
- 用于**占用分析/避让**（见 avoid-subtitles）；用于调色时要再加“人物相似度”约束，否则投影/光斑混进来。

### 3.3 已知翻车点（本项目实测）
- **投影污染**：人物影子跟着动，mask 连成一片 → 调色后人物周围出现亮斑/色块。解决：不要用帧差当精确 matte；要么接受“连影子一起提亮”（很怪），要么回到光区塑形。
- **中位背景污染**：人物站桩处 mask 有洞 → 躯干没被调色，出现斑驳。解决：填洞/用 bbox。
- **8bit 色带**：大幅推色后天空/渐变会出色带 → 加 1–3 级颗粒（ffmpeg `noise=alls=6:allf=t+u`）或输出 10bit/HEVC。
- **字幕对比度**：底片压暗后白字更清楚；若压得太狠人物也变暗，需要再提人物或加 bloom。

## 4. 哥特/霓虹等风格化调色（静态帧用）
- 哥特红黑（已被用户否掉，仅留档）：`字幕\build\gothic_art.py` 的 `gothic_grade()`：压暗 0.42–0.52、降饱和 0.30–0.42、中间调紫/红、强暗角、雾。
- 主题色版（用户最终要的）：白/骨白为主 + 薰衣草紫/品红粉辉光，背景压成深紫黑；见 `gothic_art.py` 里的调色常量（BLOOD/LAV/PINK/VIOLET）。
- 霓虹版：`neon_wide.py`（ASS 直接画霓虹，无需调色）。
- 快速套色：`eq` + `colorbalance` + `vignette` 三件套就能把紫色舞台压成任何色调：
  - 冷青：`colorbalance=bs=0.10:bm=0.12:bm...`（偏移蓝）、降饱和；
  - 暖烬火：`colorbalance=rs=0.10:rm=0.08`、`eq=saturation=1.1`。

## 5. 验证清单
- [ ] 抽 3–5 帧：人物亮度和背景分离是否自然，光区边缘有没有明显圈
- [ ] 近景/特写：脸有没有过曝、肤色是否偏
- [ ] 暗部有没有死黑/色带（8bit）
- [ ] 与字幕合看：白字是否够清楚
- [ ] 输出 `ffprobe` 时长/帧率正确；10bit 输出用 `-pix_fmt yuv420p10le -c:v libx265`

## 6. 资源
- 5s 成品参数与对比：`字幕\输出\调色测试\`（A自然/B强化/成品方向 + 对比视频）
- 30s 底片：`字幕\输出\S4S6_30s\_base_30s.mp4`（仅轻微压暗，未做完整调色）
- 之前尝试过但被否的方向：哥特（`字幕\输出\字幕设计\G1…G3`）、FLARE 炸场、霓虹（`字幕\输出\字幕小样`）——留档可参考参数。
