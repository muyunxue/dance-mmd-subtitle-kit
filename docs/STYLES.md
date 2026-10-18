# 风格库 S1–S6

来自女团 PV / 歌词版视频的常见排版方向（调研见 `skills/style-frames-compare/SKILL.md`）。
每种风格都有静态稿脚本 + 动态 ASS 参考实现。

| 代号 | 风格 | 关键元素 | 脚本 | 适合 |
|---|---|---|---|---|
| **S1** | Y2K 铬字 + 贴纸 | 镀铬泡泡字、糖果色（粉/水蓝）、星心贴纸、全息闪光 | `scripts/kpop_styles.py`（s1_y2k） | 最“女团”，适合可爱/概念向 |
| **S2** | 极简动态 | 白色 Anton、错位排布、细线、等宽小字 | `scripts/styles_anim.py` | 正规歌词版，最稳、不抢画面 |
| **S3** | 故障未来感 | Rubik Glitch、RGB 错位、扫描线、HUD 角 | `scripts/kpop_styles.py`（s3_glitch） | break / 转场 |
| **S4** | 混排杂志 | Georgia 斜体 × Bebas Neue × Archivo Black、胶带、GO! 色块、便签 | `scripts/styles_anim.py` / `scripts/full_ass.py` | 青春/杂志感，段落过渡 |
| **S5** | 大字号图形强调 | 巨字、白色贴纸描边、粉色错位、条纹 | `scripts/kpop_styles.py`（s5_graphic） | 副歌爆点短词 |
| **S6** | 手写 / 荧光笔 | Permanent Marker、粉色荧光条、便签、♥★ | `scripts/styles_anim.py` / `scripts/full_ass.py` | 间奏/特写点缀 |

## 选型建议

- 背景空旷、人物居中 → S2 或 S4；
- 背景元素（灯牌、文字）很满 → S2（白字压背景最稳）；
- 想要“女团感” → S1 / S6；
- 副歌重拍 → S4 / S5 / S6 大字；
- 转场/碎拍 → S3。

## 配色原则

- 主题色永远从画面里取：紫色舞台 → 骨白 + 薰衣草 + 品红粉；
- 纯白/骨白做主体，彩色只做强调（荧光条、贴纸、小字）；
- 不要用与背景冲突的大面积纯色（例如紫色舞台上的血红大字）。

## 不要做

- 哥特全屏黑体（用户已否过，视觉与 K-pop 舞台冲突）；
- 整段同一种动作/同一套字号，会显得像模板；
- 字压人物脸（会被观众骂，且平台封面审核也可能卡）。

## 动画套路（ASS）

- 砸入：`\fscx118\fscy118\blur(6)\t(0,130,\fscx100\fscy100\blur(0))`
- 旋转落字：`\frz+7 \t(0,180,\frz0)`
- 滑入：`\move(x-90,y,x,y,0,200)`
- 荧光笔扫出：`\p1` 矩形 + `\fscx0\t(0,180,\fscx100)` + `\org`
- 淡出：`\fad(120,180)`（最后一句可 `\fad(0,420)`）

参考实现：`scripts/styles_anim.py`、`scripts/full_ass.py`。
