---
name: mmd-subtitle-pipeline
description: End-to-end recipe for making subtitles for the MMD dance videos in this workspace (字幕/ project) — probe the source, pick a segment, map LRC cues, choose a style, build ASS, burn, verify, and deliver. Load this when starting or resuming any subtitle task (静态稿/5s小样/30s小样/全片/透明叠加层), when a render "succeeded" but the video has no text, or when you need this project's paths, font list, cue sheet and acceptance criteria.
---

# MMD 舞蹈视频字幕：端到端流程

## 0. 一句话原则
**写完/渲完必须抽帧看一眼**：`ffprobe` 时长对 ≠ 字幕真的出现；ASS 时间戳或 Style 颜色格式错都会「渲染成功但没字」。
本项目已有多次「以为改好了，其实没烧进去」的教训，验收一律以抽帧截图为准。

## 1. 资产与路径（本 workspace）
| 东西 | 路径 |
|---|---|
| 字幕项目 | `D:\yingyong2\论项目\字幕\` |
| LRC 歌词 | `字幕\[by维尔日记].txt` — KISS OF LIFE《Who is she (Japanese Ver.)》，36 句 |
| 旧 MMD 成片 | `字幕\0001-4956 - 副本.mkv`（2560×1080 / 30fps；**文件不完整**，标称 165s 实际只能解到 ~137s） |
| 新 MMD 成片 | `D:\mmd.mp4\0002-4956.mkv`（2560×1080 / 30fps / 165.166s，**完整**） |
| 字体 | `字幕\build\fonts\`（Anton, ArchivoBlack, BebasNeue, Bungee, Monoton, PermanentMarker, RubikGlitch, Silkscreen, PirataOne, UnifrakturCook）+ 系统 Georgia / Microsoft YaHei |
| 生成脚本 | `字幕\build\*.py` |
| 成片输出 | `字幕\输出\<任务名>\`（每个任务一个文件夹，交付名带中文可读名） |
| ffmpeg | `C:\Users\35530\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe` |
| python | `C:\Users\35530\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe`（PIL 12.3 / numpy 2.3，无 cv2） |

## 2. 七步主流程
```
① 探测素材   ffprobe 分辨率/帧率/时长/色彩；解码测试判断文件是否截断
② 选片段     歌曲段 vs 舞蹈动作；小样 5s / 30s / 全片
③ 对歌词     LRC 绝对时间 → 减去片段起点 = ASS 相对时间
④ 定风格     参考 S1–S6（见 style-frames-compare）；先出静态帧，再出动态
⑤ 写 ASS     Python 生成；遵守 ass-render-playbook 的格式硬规则
⑥ 渲染       ffmpeg 烧录（或透明叠加层）；先出 5–10s 验证，再全段
⑦ 验收       抽帧（每句至少 1 帧）+ 拼关键帧表；看构图、无中文、不挡脸、收尾淡出
```

### ① 探测素材
```powershell
$ff='...\ffmpeg.exe'; $fp='...\ffprobe.exe'
& $fp -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,nb_frames,pix_fmt,color_space -show_entries format=duration -of default=nw=1 $v
& $ff -v error -i $v -map 0:v:0 -c copy -f null NUL   # 报 "File ended prematurely" = 截断
```
- 本项目素材都是 **2560×1080 / 30fps / h264 yuv420p / bt709**，超宽 64:27。
- 165s 视频 ≈ 4956 帧；30s 成片 = 900 帧。

### ② 选片段
- LRC 副歌第一段：`36.892 / 40.366 / 44.003 / 47.577 / 51.179 / 54.698 / 58.309 / 61.926`，到 ~66s 收。
- 5s 对比样片常用 `0:58.2–1:03.2`；30s 样片常用 `0:36.5–1:06.5`；全片 0–154.6s（旧文件只能到 137s）。
- 裁片：`-ss 36.5 -t 30 -i src -vf "eq=brightness=-0.05:contrast=1.04:saturation=1.02" -c:v libx264 -crf 16 -pix_fmt yuv420p`
  （轻微压暗是为了让白/奶油字有对比；完整调色另见 subject-color-grade）

### ③ 对歌词
LRC 是绝对时间；ASS 用相对片段起点的时间。例：片段从 36.5s 开始，则 36.892 → `0.392s`。
一句一个 cue；句内再按词拆多个事件（见下）。结尾事件要提前 0.14–0.4s 收掉，避免跨句粘连。

### ④ 定风格
- 先读 `style-frames-compare` 技能，按目标气质选 S1–S6，先出静态帧给用户看。
- 重要约束：**用户明确说"不要中文"时，只保留原歌词英文/日文**；人物在中间，大字放左右安全栏与上下角。
- 已有可复用生成器：`styles_anim.py`（S2/S4/S6 的 5s 动画）、`flare_wide.py`（炸场）、`neon_wide.py`（霓虹）、`avoid_side2.py`（完全避让）、`kpop_styles.py`（静态稿）、`art_frames.py`（艺术字静态稿）。

### ⑤ 写 ASS
- 用 Python 生成（比手写稳）：定义 `Ass` 类 + `word()/rect()` 辅助，最后 `write()`。
- 硬规则、模板、坑见 `ass-render-playbook`（时间格式 `H:MM:SS.cc`、Style 色值无尾 `&`、fontsdir 相对路径等）。

### ⑥ 渲染
- 工作目录 = 输出目录；ASS 用 ASCII 文件名；字体目录相对：
```powershell
cd "字幕\输出\S4S6_30s"
& $ff -v error -y -i _base_30s.mp4 -vf "ass=_s4.ass:fontsdir=fonts" `
  -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p -movflags +faststart S4_30s.mp4
```
- 透明叠加层（后期用）：`-f lavfi -i "color=black@0.0:s=2560x1080:r=30,format=rgba" -vf "ass=x.ass:alpha=1"` + VP9 `yuva420p`（详见 ass-render-playbook）。

### ⑦ 验收清单
- [ ] `ffprobe` duration 与设计一致（5.000 / 30.000 / 154.6）
- [ ] 抽帧：每句至少 1 帧，确认**字真的出现**、位置对、无乱码
- [ ] 用户要求无中文 → 抽 2–3 帧确认只有英文/日文
- [ ] 人物脸/身体未被遮挡（近景/特写帧尤其检查）
- [ ] 尾句在结束前淡出（如 29.86s 前），不留残字
- [ ] 拼 `关键帧.jpg`（2×2 或 2×3，每格 1280×540，带标签）方便用户看
- [ ] 文件名可读 + 说明 md 一并交付

## 3. 任务类型 → 交付物
| 任务 | 交付 |
|---|---|
| 静态帧方案 | N 张 2560×1080 jpg + `总览.jpg` + 说明 md |
| 5s 小样 | 1–3 条 5s mp4 + 对比视频 + 关键帧表 |
| 30s 小样 | 1–2 条 30s mp4（900 帧）+ 对比版 + 关键帧表 + 说明 md |
| **成对交付（常见）** | 每个风格 2 条：`X_有背景_30s.mp4`（H.264 烧录）+ `X_纯字幕_透明_30s.webm`（VP9 alpha）；N 风格 × 2 条视频，附 `纯字幕_透明预览.jpg`（棋盘格合成预览） |
| 全片 | 字幕 ASS + 烧录 mp4 / 透明 webm + 说明 |
| 调色 | 调色 mp4 + 对比帧 + 参数说明 / LUT |

> 透明版渲染（与有背景版同一个 ASS，帧对帧一致）：
> ```powershell
> & $ff -v error -y -f lavfi -i "color=c=black@0.0:s=2560x1080:r=30,format=rgba" `
>   -vf "ass=_s4.ass:alpha=1:fontsdir=fonts" -t 30 -c:v libvpx-vp9 -pix_fmt yuva420p `
>   -b:v 0 -crf 30 -row-mt 1 -auto-alt-ref 0 -metadata:s:v:0 alpha_mode=1 OUT.webm
> ```
> 验证 alpha：`ffmpeg -c:v libvpx-vp9 -ss 12.4 -i OUT.webm -frames:v 1 -pix_fmt rgba f.png`，PIL 检查 alpha min=0 / max=255、覆盖率>0；**抽帧必须显式 `-c:v libvpx-vp9`**，否则丢 alpha 全变 255。

## 4. 并行（子代理）约定
用户说「子代理分开做」时的标准玩法：
1. 主代理先准备**共享底片**（裁好、统一压暗）与 `fonts/` 副本、cue sheet（相对时间表）；
2. 每个风格一个子代理，提示词里给死：输入路径、输出文件名（`S4_30s.mp4` 等）、ASS 硬规则、时间轴表、验收要求；
3. 子代理各自只写自己的前缀文件，互不覆盖；
4. 主代理收齐后做对比视频/关键帧表/说明，并统一验收抽帧。
实测：单个 30s 样式（2560×1080、8 句、约 40–60 个 Dialogue）从设计到成片约 10–20 分钟；两子代理并行≈最慢那个的时间。
