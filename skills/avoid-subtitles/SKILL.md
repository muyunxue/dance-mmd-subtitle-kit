---
name: avoid-subtitles
description: Character-avoiding subtitle layout for the MMD dance videos — measure the dancer's per-frame bounding box, compute a per-cue union, place text in safe side/top columns, and verify zero overlap on every frame. Load this when asked 字幕不要挡住人物/完全不挡/避让, or when text overlaps wings/body and you need a verified-free layout with measured overlap counts.
---

# 人物避让字幕（完全/尽量不挡人）

## 0. 两种目标要分清
- **"完全不挡"**：每个字框与每一帧人物 mask 的交集 = 0。代价是字只能放两侧/顶部窄栏，字号受限。
- **"尽量不挡"**：允许压翅膀边缘/背景，但脸和身体必须干净。可以继续用大字风格（S4/S6 等），只检查近景帧。

本技能默认做「完全不挡」并给出可验证数据；如果用户说“炸裂/大字/艺术字”，大概率是后者。

## 1. 核心算法（快版：只求 bbox）
不再逐像素求精确 matte，只需要人物**包围盒**，用 1/4 分辨率算，极快：
1. 背景板 `bg_half.npy`（1280×540，见 subject-color-grade 的 2.1/3.1）。
2. 每帧缩到 **640×270**，与背景板做差：`d = |frame-bg|.max(axis=2)`，阈值 **38**（低阈值会把 LOVE 灯牌/光斑算进来）。
3. `MaxFilter(5)` 膨胀 → **最大连通域**（BFS，640×270 上很快）→ 取 bbox ×4 还原到全分辨率。
4. 按歌词句窗口把每帧 bbox 并起来（一句内人物会动，用**整句最宽范围**），得到每句 `bounds = (left,right,top,bottom)`。
5. 排版：文字列放在 `left-50` 左侧 / `right+50` 右侧 / 顶部 / 底部；字号按可用宽度收缩。
6. **逐帧复核**：把每个字框映射回 640×270，与每帧 mask 求交集，报告 worst hit；不为 0 就整体缩字号再验，直到 0。

## 2. 可直接复用的实现
`字幕\build\avoid_side2.py`（推荐，完整版：pass1 测 bbox → layout → verify → 渲染 → 关键帧）：
```powershell
$py='C:\Users\35530\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
& $py '字幕\build\avoid_side2.py'
```
它固定处理旧片（`0001-4956`）的 15.4s 片段；换片/换段时改这些常量：
- `SRC` / `OUT` / `T0,T1`
- `CUES`（每句起止，相对片段）
- `EL` 里的字号/位置候选（`L`/`R` 列、y、fs）
- `LEFT_MARGIN`/右侧可用宽度逻辑
产物：`NEON_avoid_15s.ass` + 渲染视频 + 关键帧表。
旧版（合成演示）：`avoid_demo.py`、`avoid_debug.py`、`avoid_layout.py`（占用热区图 `分析_占位与选位.jpg`）。

## 3. 本项目的实测数据（旧片 0:51–1:06.4）
- 固定底部排版：6/6 句压到人物，人物区域遮挡率 7%–12%。
- 侧栏避让：0/6 句压到人物，单句遮挡 ≤0.2%；逐帧复核 **0 像素**。
- 每句可用侧栏（旧片，全 2560 宽）：左栏约 0–500px，右栏约 2100–2560px，具体每句不同，**必须现算**。
- 人物在画面中央、翅膀展开时占宽约 48%–82%，近景/特写时几乎占满 → 特写帧只能把字放上下角。

## 4. 排版策略（不挡人时也好看）
- 主歌词放**左栏**、点缀词放**右栏**，形成“左右对唱”的观感；
- 顶部放长句（`MAKING EVERYBODY GO` 之类），底部只留小字/等宽信息；
- 每句只有一个“视觉主角”，其余词做小字，避免整句全大导致侧栏放不下；
- 字框估算要**保守**：ASCII 宽 ≈ fs×0.66、CJK ≈ fs×1.06；留 10–14px pad。

## 5. 验证清单
- [ ] 每句窗口的 bbox 是否漏掉翅膀尖/头顶（看 `分析_占用区域.jpg`）
- [ ] 逐帧复核 worst hit = 0（脚本会打印）
- [ ] 抽 3–4 帧看：字是否贴边/被裁、是否压到小指/翅膀
- [ ] 近景/特写帧单独抽查
- [ ] 若允许“尽量不挡”，记录哪些帧压到了翅膀（可接受）

## 6. 已知坑
- 背景 LOL 灯牌/光斑会被帧差误判 → 阈值 38 + 最大连通域通常能去掉；仍不行就加空间先验（人物在中央）。
- 人物投影可能被当成人物（bbox 变大）→ 对避让是**安全**的（你会避开影子），但会让侧栏更窄。
- 滤镜 `MaxFilter` 在 640×270 上 ≈ 外扩 8px 全分辨率，复核时不要再额外放大 pad。
- 若换了新视频/新机位，**所有 bounds 都要重算**，不能复用旧片数字。
