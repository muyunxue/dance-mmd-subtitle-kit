# scripts

Windows 环境下实测的 Python 脚本，负责「字幕生成 / 风格稿 / 调色 / 避让 / 封面」。

## 先改路径

所有脚本里都有类似：

```python
ROOT = os.path.dirname(BASE)          # 项目根
SRC = os.path.join(ROOT, "...mkv")    # 输入视频
OUT = os.path.join(ROOT, "输出", "...") # 输出目录
FONT_DIR = os.path.join(BASE, "fonts")  # 字体
```

使用前把 `SRC` / `OUT` 改成本机路径；字体统一放 `scripts/fonts/`（跑 `fonts/download_fonts.ps1`）。

## 脚本清单

| 脚本 | 作用 |
|---|---|
| `subs_core.py` | 优雅版字幕：36 句歌词数据 + ASS 生成 + 背景/规则线/心跳装饰 |
| `build.py` | 渲染入口：批量生成 ASS/SRT、预览背景、抽帧、叠加层、预览视频 |
| `styles_anim.py` | S2/S4/S6 三风格的 5s 动画小样 + 三版对比 |
| `full_analysis.py` | 全片逐句人物包围盒分析（1/4 分辨率，快） |
| `full_ass.py` | 读 cues.json 生成全片 S4/S6 ASS（安全栏排版 + 动画） |
| `s4s6_compare.py` | 把两版 30s 成片叠成对比视频 + 关键帧表 |
| `kpop_styles.py` | S1–S6 静态风格稿（PIL/numpy） |
| `art_frames.py` | 更炸的 6 种艺术字静态稿（故障切片/立体/拼贴…） |
| `gothic_art.py` | 哥特全屏（留档，不建议用） |
| `flare.py` / `flare_video.py` / `flare_wide.py` / `flare_wide_render.py` | FLARE 炸场动态字（ASS + 视频） |
| `neon_wide.py` / `neon_wide_render.py` | 霓虹动态字（超宽画幅） |
| `avoid_side2.py` | **完全不挡人**：bbox → 侧栏 → 逐帧 0 重叠复核 |
| `avoid_layout.py` / `avoid_demo.py` / `avoid_debug.py` | 占用热区分析 / 合成演示（早期版本） |
| `grade_ffmpeg.py` | 调色：光区塑形 + 背景压暗 + 辉光 + 暗角 |
| `grade_final5s.py` | 5s 成品调色参数（可直接套全片） |
| `color_grade.py` | 旧版帧差抠像调色（会被投影污染，留档） |
| `make_covers.py` / `make_covers2.py` | 封面：16:9 / 4:3 / 3:4，多种风格 |

## 运行顺序（全片）

1. `full_analysis.py` → `cues.json`
2. `full_ass.py` → `_s4_full.ass` / `_s6_full.ass`
3. 先 20s 测试渲染，再全片烧录 / 透明叠层
4. `s4s6_compare.py` 做对比

## 依赖

- Python 3.10+：Pillow、numpy（见根目录 requirements.txt）
- ffmpeg（libass、libvpx-vp9、libx264）
- Windows 系统字体 Georgia / Microsoft YaHei
