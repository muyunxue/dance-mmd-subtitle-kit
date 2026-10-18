---
name: style-frames-compare
description: Design and deliver subtitle style mockups and animated comparison samples for the MMD/K-pop dance videos — S1–S6 style catalogue (Y2K chrome, minimal kinetic, glitch, mix&match editorial, graphic emphasis, hand-marker), PIL/numpy effect recipes, font list, contact-sheet/comparison video conventions, and the parallel-subagent workflow used for S4 vs S6. Load this when asked 出几个静态帧方案/参考女团PV字幕/做个小样/对比几个风格, or when choosing a visual direction before building a full-length subtitle track.
---

# 字幕风格方案 / 静态帧 / 对比小样

## 0. 先调研、再出稿
女团 PV 字幕的公开资料归纳（2024 KCI 论文 + K-pop Y2K Seoul 风格指南）：
- **Graphic 图形强调**：粗细对比不规则、装饰性笔画的大字（Blackpink / XG 海报系）；
- **Mix & Match 混排**：衬线 + 无衬线 + 压缩体 + 倾斜混用，杂志编辑感；
- **Minimalism 极简**：干净无衬线、去装饰、留白，随节拍出现（NewJeans/aespa kinetic typography）；
- **Futurism 未来感**：数字化无衬线 + glitch / RGB 错位 / 扫描线；
- **Y2K 铬字 + 贴纸**：chrome bubble lettering、糖果色（hot pink + aqua）、贴纸拼贴、星光闪点；
- **手写日记感**：马克笔/荧光笔 + 便签 + 涂鸦（NewJeans 青春感）。

## 1. 六种本片适配风格（S1–S6）
| 代号 | 风格 | 关键元素 | 适合 |
|---|---|---|---|
| S1 | Y2K 铬字 + 贴纸 | Bungee 铬字渐变 + 粉色徽章 + 星光 | 最“女团”，粉/水色可换紫粉 |
| S2 | 极简动态 | Anton 白色大字、错位、细线、Silkscreen 小字 | 正规歌词版，最稳、不抢背景 |
| S3 | 故障未来感 | RubikGlitch + Anton、RGB 错位、扫描线、HUD 角 | break / 转场 |
| S4 | 混排杂志感 | Georgia Italic × Bebas Neue × Archivo Black、胶带、GO! 色块、便签 | 青春/杂志感，段落过渡 |
| S5 | 图形强调 | Anton 巨字 + 白色贴纸描边 + 粉色错位 + 条纹 | 副歌爆点短词 |
| S6 | 手写/荧光笔 | Permanent Marker + 粉色荧光块 + 便签 + ♥★ 箭头 | 间奏/特写点缀 |

## 2. 制作静态帧（PIL + numpy，无 AI 库）
脚本：
- `字幕\build\kpop_styles.py` — S1–S6 六张 2560×1080 静态稿（2025 调研版）
- `字幕\build\art_frames.py` — 早期 6 个艺术字方案（故障切片/霓虹崩坏/立体巨字/拼贴/轮廓回声/竖排）
- `字幕\build\gothic_art.py` — 哥特全屏（已被用户否掉，留档）
字体目录：`字幕\build\fonts\`（Anton, ArchivoBlack, BebasNeue, Bungee, Monoton, PermanentMarker, RubikGlitch, Silkscreen, PirataOne, UnifrakturCook）+ `C:\Windows\Fonts`（Georgia / Georgia Italic / Microsoft YaHei / Impact / Arial Black）。
下载字体（Google Fonts GitHub raw 可用）：
```
https://raw.githubusercontent.com/google/fonts/main/ofl/<family>/<File>.ttf
```

### 常用效果函数（PIL/numpy）
- 文字层：逐字绘制 + tracking（`text_img`），`stroke_width/stroke_fill` 做描边；
- 铬字：alpha mask 上贴竖向多段渐变（`gradient_fill`）+ 斜向高光带；
- 贴纸描边：对 alpha 做 `MaxFilter(3)` 膨胀 N 次再着色；
- 错位/故障：RGB 通道分别平移（`chroma`）、横向条带随机位移（`glitch_slices`）、扫描线；
- 立体字：同一文字多次偏移叠画，由远到近做深紫→薰衣草渐变；
- 半调：网格圆点叠加（`halftone`）；
- 手写荧光笔：文字后垫半透明圆角矩形 + `GaussianBlur`；
- 便签/胶带：半透明矩形 + 细线纹理 + 旋转；
- 星光/爱心：4 角星多边形、双圆 + 三角心形；
- 颗粒：`np.random.normal` 叠加 1–3 级防色带。

## 3. 动态小样（ASS 动画）
- 5s 三风格：`字幕\build\styles_anim.py` → `公众号/输出/字幕风格参考/小样_S2_5s.mp4` 等；
- S4/S6 30s：`字幕\输出\S4S6_30s\`（两个子代理各做一版，见下）；
- 炸场 FLARE：`flare.py` + `flare_video.py`；霓虹：`neon_wide.py`；
- 完全避让霓虹：`avoid_side2.py`。
- 动画套路：砸入（`\fscx118→100` + `\t` + `\blur`）、旋转落字（`\frz` + `\t`）、滑入（`\move`）、淡入、色块缩放/扫出（`\p1` + `\fscx`）、便签上移、拍点脉冲（每 0.447s 一个 134BPM 拍）。

## 4. 对比交付规范
- 单条样片：2560×1080 / 30fps / H.264 crf16 / faststart；30s=900 帧，5s=150 帧。
- 对比视频：上下 `vstack`，每条缩到 1280×540，输出 1280×1080（或 3 条 → 1280×1620），用 ASS 叠标签。
- 关键帧表：2×2 / 2×3 / 3×3 拼图，每格 853×360 或 1280×540，带风格名和时刻标签。
- 说明 md：风格说明 + 文件表 + 时间轴 + 已知限制。
- 示例：`字幕\输出\字幕风格参考\`（6 风格静态 + S2/S4/S6 5s 对比）、`字幕\输出\S4S6_30s\`（两版 30s + 对比）。

## 5. 并行子代理工作流（"子代理分开做"）
1. 主代理准备**共享底片**（裁好 + 轻微压暗）→ `_base_30s.mp4`；复制 `fonts/` 到输出目录；写 cue sheet（相对时间）。
2. 每个风格一个子代理，提示词必须包含：
   - 底片绝对路径、输出目录、输出文件名（`S4_30s.mp4` / `S6_30s.mp4`）；
   - 字体目录、ffmpeg 路径、ASS 硬规则（时间格式、Style 色值无尾 &、fontsdir 相对、ASCII 文件名）；
   - 逐句时间轴（8 句）+ 风格描述 + "不要中文 / 不挡脸" 约束；
   - 自查要求（ffprobe 30s、抽帧看字、无中文、脸部干净）。
3. 子代理只写自己前缀的文件，互不覆盖；完成后汇报排法/动效/踩坑。
4. 主代理收齐后：`s4s6_compare.py` 合成对比视频 + 关键帧表 + 统一说明 md；再自己抽帧验收一遍。

## 6. 选型建议（紫粉霓虹舞台 + 翅膀人物）
- 最稳：**S2 极简动态**；
- 最女团：**S1 Y2K 铬字**（把颜色换紫粉主题色）；
- 段落过渡：**S4 混排**；爆点：**S5**；间奏/特写：**S6**；break：**S3**。
- 用户明确否过：哥特全屏、血红配色。别再出哥特方向。

## 7. 验收清单
- [ ] 静态稿是 2560×1080、无中文错字
- [ ] 动态样片 ffprobe 时长正确（5.000/30.000）
- [ ] 抽帧确认字幕出现、不挡脸、无中文
- [ ] 对比视频 + 关键帧表 + 说明 md 齐全
- [ ] 风格名/文件命名统一（`S4_30s.mp4`、`对比_S4S6_30s.mp4`）
