# 字幕 / MMD 视频处理技能（Skills）

这套字幕工作流的**可复用技能库**，按 DSH `SKILL.md` 约定组织（`skills/<name>/SKILL.md`，YAML frontmatter：`name` + `description`）。

## 安装位置（重要）

DSH 的本地 skill 发现根目录是 **`<项目根>/.dsh/skills/<name>/SKILL.md`**（本项目无 `.git`，所以项目根 = 工作目录 `D:\yingyong2\论项目`）：

```
D:\yingyong2\论项目\.dsh\skills\<name>\SKILL.md     ← 真身
D:\yingyong2\论项目\字幕\skills\<name>              ← junction，方便在字幕项目里浏览
D:\yingyong2\论项目\字幕\skills\README_技能索引.md   ← 本索引
```

> 注意：当前会话的 `skill` 工具目录里还看不到它们（本机 profile 未挂载 `@deepseek-ai/dsh-skill-filesystem` 提供方，已实测 `skill` 调用返回 unknown）。
> 有该提供方的环境 / 重新挂载后，重启或等目录刷新即可用 `skill` 按名字加载；在那之前，直接读 `SKILL.md` 文件同样有效。

| 技能 | 什么时候用 |
|---|---|
| [mmd-subtitle-pipeline](mmd-subtitle-pipeline/SKILL.md) | 任何字幕任务的总流程：探测素材→选段→对 LRC→定风格→写 ASS→渲染→验收；含全部路径、字体、交付规范、子代理并行玩法 |
| [ass-render-playbook](ass-render-playbook/SKILL.md) | 写 ASS / 烧录前必读：时间格式、Style 颜色、fontsdir、`\p1` 锚点、动画标签、故障速查 |
| [subject-color-grade](subject-color-grade/SKILL.md) | 调色/突出人物：光区塑形（推荐）与硬抠像（脏）的取舍、ffmpeg 合成图、实测参数档、色带/投影坑 |
| [avoid-subtitles](avoid-subtitles/SKILL.md) | 字幕不挡人：1/4 分辨率 bbox + 逐句并集 + 侧栏排版 + 逐帧 0 重叠复核 |
| [style-frames-compare](style-frames-compare/SKILL.md) | 风格方案/静态帧/对比小样：S1–S6 风格库、PIL/numpy 效果配方、对比交付规范、子代理分工 |

## 已有产物（对照看）
- 全套字幕（灰与火优雅版）：`字幕/输出/字幕文件/`、`字幕/README_字幕使用说明.md`
- 炸场样片：`字幕/输出/样片_炸裂版/`
- 人物避让演示：`字幕/输出/人物避让演示/README_避让方案说明.md`
- 调色测试：`字幕/输出/调色测试/说明_调色方案.md`
- 霓虹/FLARE 15s：`字幕/输出/字幕小样/说明_小样.md`
- 6 风格静态稿 + 参考调研：`字幕/输出/字幕风格参考/说明_风格参考.md`
- S4/S6 30s 对比：`字幕/输出/S4S6_30s/说明_S4S6_30s.md`

## 生成脚本（`字幕/build/`）
- 字幕：`subs_core.py`、`build.py`、`flare.py`、`flare_wide.py`、`neon_wide.py`
- 调色：`grade_ffmpeg.py`、`grade_final5s.py`、`color_grade.py`
- 避让：`avoid_layout.py`、`avoid_side2.py`、`avoid_demo.py`
- 风格：`kpop_styles.py`、`art_frames.py`、`gothic_art.py`
- 动画样片/对比：`styles_anim.py`、`s4s6_compare.py`、`flare_wide_render.py`、`neon_wide_render.py`
- 字体：`字幕/build/fonts/`

## 维护约定
- 新任务先按 pipeline 技能走；踩到新坑**回写到对应 SKILL.md**（尤其是 ASS 格式和 ffmpeg 版本行为）。
- 新风格先做静态帧，再做 5s，再做 30s，最后全片；每层都要抽帧验收。
- 用户偏好：不要哥特/血红；无中文（当要求时）；人物脸和身体不要被挡；紫色霓虹舞台优先白/紫/粉配色。
