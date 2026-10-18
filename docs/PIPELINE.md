# 7 步流水线（舞蹈 MMD 字幕）

完整技能版见 `skills/mmd-subtitle-pipeline/SKILL.md`，这里是仓库视角的精简操作版。

## 0. 一句话原则

**渲完必须抽帧看**：`ffprobe` 成功 ≠ 字幕出现。ASS 时间戳格式或 Style 色值格式错了会「渲染成功但没字」。

## 1. 探测素材

```powershell
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,nb_frames,pix_fmt ^
  -show_entries format=duration -of default=nw=1 input.mkv
ffmpeg -v error -i input.mkv -map 0:v:0 -c copy -f null NUL   # 报 "File ended prematurely" = 文件截断
```

记录：分辨率、帧率、总帧数、时长、色彩标记、是否截断。

## 2. 选片段

- 小样：5s / 30s（30s = 900 帧 @30fps）
- 全片：整首（按 LRC 最后一句 + 余量）
- 需要的话先统一压暗一点方便白字：`eq=brightness=-0.05:contrast=1.04:saturation=1.02`

## 3. LRC 对轴

LRC 是绝对时间；ASS 用相对片段起点：`cue_rel = cue_abs - segment_start`。
- 每句结束 = 下一句开始 − 0.15s，且单句最长不超过 6.5s（避免间奏拖字）。
- 句内再拆「词级」事件做动画。

模板：`examples/templates/lrc_template.txt`。

## 4. 定风格

先读 `skills/style-frames-compare/SKILL.md`，从 S1–S6 选方向；**先出静态帧**给用户确认，再做 5s，再做 30s，最后全片。

风格说明见 `docs/STYLES.md`。

## 5. 写 ASS

- 用 Python 生成，别手写：`scripts/full_ass.py`（全片）、`scripts/styles_anim.py`（5s 动画）可直接改。
- 硬规则（详见 `skills/ass-render-playbook/SKILL.md`）：
  - 时间戳 `H:MM:SS.cc`（`0:00:01.50`，不是 `0:01.50`）
  - Style 行颜色结尾**不能**带 `&`
  - 字体用 `fontsdir=相对路径` + 工作目录
  - `\p1` 绘图锚点：`\an7` + 绝对坐标 + `\org`
- 排版前先跑 `scripts/full_analysis.py` 得到每句人物包围盒，把字放在左右安全栏；或者用 `scripts/avoid_side2.py` 的逐帧复核版本。

## 6. 渲染

```powershell
# 烧录
ffmpeg -v error -y -i base.mp4 -vf "ass=_s4_full.ass:fontsdir=fonts" ^
  -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p -movflags +faststart out.mp4

# 透明叠层（VP9 + alpha）
ffmpeg -v error -y -f lavfi -i "color=c=black@0.0:s=2560x1080:r=30,format=rgba" ^
  -vf "ass=_s4_full.ass:alpha=1:fontsdir=fonts" -t 165.166 ^
  -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 0 -crf 30 -row-mt 1 -auto-alt-ref 0 -cpu-used 4 ^
  -metadata:s:v:0 alpha_mode=1 out_alpha.webm
```

> 整段渲染前先渲一个 20s 测试段（`-ss` 取段 + 对应平移的 ASS）验证效果。

## 7. 验收

- [ ] `ffprobe` 时长/帧数/分辨率与设计一致
- [ ] 每句至少抽 1 帧：字出现、位置对、无乱码
- [ ] 无中文字幕（如要求）/ 无错字
- [ ] 人物脸和身体没被遮挡（近景/特写重点查）
- [ ] 尾句在结束前淡出
- [ ] 关键帧表 / 对比视频 / 说明文档一并交付

## 常见故障

| 现象 | 原因 | 修法 |
|---|---|---|
| 全片没字 | 时间戳格式 / Style 颜色带尾 `&` | 改 `H:MM:SS.cc`、去尾 `&` |
| 部分句没字 | start >= end 或时间写错 | 逐句检查 |
| 字体不对/很小 | family 名写错 | 用 PIL `getname()` 核对 |
| `\p1` 色块偏上 | libass 绘图锚点上移 h/2 | `\an7` + 绝对坐标 + 实测标定帧 |
| 透明 webm 解码全黑 | 解码丢了 alpha | 解码加 `-c:v libvpx-vp9` |
