---
name: ass-render-playbook
description: Hard rules, templates, ffmpeg commands and failure diagnosis for authoring ASS/SSA subtitles and burning them with libass on this machine. Load this before writing any ASS file, when a burn "succeeds" but no text appears, when text is misplaced/too big, when \p1 drawings are offset, or when you need the transparent-overlay export recipe. Contains the exact pitfalls hit in this project (timestamp format, style colour trailing ampersand, fontsdir, drawing anchor, chained \t, Permanent Marker sizing).
---

# ASS 编写 / libass 烧录 实战手册

## 1. 文件头模板（直接抄）
```
[Script Info]
ScriptType: v4.00+
PlayResX: 2560
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: X,Microsoft YaHei,100,&H00F4F1EA,&H00F4F1EA,&H00140F11,&HFF000000,0,0,0,0,100,100,0,0,1,0,0,5,30,30,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.39,0:00:03.75,X,,0,0,0,,{\an5\pos(500,300)\fnAnton\fs150\1c&H00F4F1EA&\bord3\3c&H00140F11&\frz-4\fscx118\fscy118\t(0,130,\fscx100\fscy100)\fad(100,100)}WALK
```

## 2. 四个致命格式坑（本项目全踩过）
1. **时间戳必须是 `H:MM:SS.cc`**
   - 对：`0:00:01.50`、`0:01:02.30`
   - 错：`0:01.50`（libass 报 `Bad timestamp`，整句被丢弃 → 整个视频没字，但 ffmpeg 返回 0）
2. **Style 行颜色结尾不能带 `&`**
   - 对：`&H00F4F1EA,&H00F4F1EA,&H00140F11,&HFF000000`
   - 错：`&H00F4F1EA&,...` → Style 行解析失败 → 同样「成功但没字」
   - 事件内联标签里的颜色**要**带 `&`：`\1c&H00F4F1EA&`
3. **字体目录 `fontsdir` 用相对路径 + 工作目录**
   - 在输出目录放 `fonts/`，`cd` 到该目录再 `ass=x.ass:fontsdir=fonts`。
   - 绝对路径带盘符冒号在 filtergraph 里容易翻车；中文相对路径没事（cwd 可以中文，但 filter 参数里尽量 ASCII）。
4. **ASS 文件用 `utf-8-sig` 写、ASCII 文件名**
   - 中文文件名在 filter 参数里不稳；写 `_s4.ass` 这种。

诊断命令（看 libass 到底读到什么）：
```powershell
& $ff -hide_banner -v verbose -f lavfi -i "color=c=0x303040:s=2560x1080:r=30:d=2" `
  -vf "ass=_s4.ass:fontsdir=fonts" -c:v libx264 -crf 22 -pix_fmt yuv420p _t.mp4 2>&1 | Select-String 'Bad timestamp|Style|font file'
```

## 3. 颜色 / alpha 语义
- 颜色：`&HBBGGRR&`（蓝绿红顺序），例：白 `&H00F4F1EA&`、墨黑 `&H00140F11&`、粉 `&H00B35CFF&`、薰衣草 `&H00FFA4C4&`、奶油 `&H00D7EEF8&`、金 `&H0054C9FF&`。
- 透明度 `\1a`：`&H00&` 完全不透明；`&HFF&` 完全透明（十六进制越高越透明）。早期炸场版闪烁失效就是 alpha 反了。
- Style 行的 PrimaryColour 是 `&HAABBGGRR`（AA 在前，不带尾 &）。

## 4. 字体
- libass 用 fontconfig/directwrite，**family name 必须对**。用 PIL 查：
```python
from PIL import ImageFont
ImageFont.truetype(r"...\fonts\Anton-Regular.ttf", 40).getname()  # ('Anton','Regular')
```
- 本项目字体：Anton / Archivo Black / Bebas Neue / Permanent Marker / Silkscreen / Rubik Glitch / Bungee / Monoton / Pirata One / UnifrakturCook；系统 Georgia、Microsoft YaHei 可直接 `\fnGeorgia`、`\fnMicrosoft YaHei`。
- **Permanent Marker 在 libass 里实际约 0.79×fs**，要按这个系数放大字号 / 色块尺寸。
- 缺字形（如 ♥ ★）会自动回退 ArialMT，能显示但字形不同；要精确就用 `\fnMicrosoft YaHei`。

## 5. 动画标签速查
| 标签 | 用法 |
|---|---|
| `\fad(in,out)` | 毫秒淡入淡出 |
| `\move(x1,y1,x2,y2,t1,t2)` | 位移（与 `\pos` 二选一，move 优先） |
| `\t(t1,t2,\tag...)` | 定时插值，例 `\t(0,130,\fscx100\fscy100\blur(0))` |
| `\frz` / `\fscx` / `\fscy` | 旋转/缩放（负值可做翻转） |
| `\blur(n)` | 模糊（大词落地前模糊→清晰很有效） |
| `\clip(x1,y1,x2,y2)` | 矩形裁切（做切片/扫光/显现） |
| `\org(x,y)` | 旋转/缩放中心点 |
| `\p1`+绘图 | `m 0 0 l w 0 w h 0 h` 矩形等 |

**坑**：同一属性连续两个 `\t` 会只取一个（例如规则线收缩动画），拆成两个事件/两次重绘解决。
**坑**：`\p1` 绘图坐标是**左上角锚点**，libass 还会把整块按高度上移 h/2；用 `\an7\pos(左上角)` + 绝对坐标最稳，旋转/扫出用 `\org` 定原点。
**坑**：荧光笔色块想在词后面“扫出”，用绘图层 `\fscx0 → \t(0,150,\fscx100)`，原点用 `\org`。

## 6. 渲染命令
### 6.1 直接烧录（最常用）
```powershell
cd 输出目录
& $ff -v error -y -i _base_30s.mp4 -vf "ass=_s4.ass:fontsdir=fonts" `
  -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p -movflags +faststart OUT.mp4
```
30s / 2560×1080 / 中文字幕量 ≈ 1–3 分钟。

### 6.2 透明叠加层（交给剪辑软件用）
```powershell
& $ff -v error -y -f lavfi -i "color=black@0.0:s=2560x1080:r=30,format=rgba" `
  -vf "fps=30,ass=_sub.ass:alpha=1" -t 154.6 `
  -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 0 -crf 30 -row-mt 1 -auto-alt-ref 0 `
  -metadata:s:v:0 alpha_mode=1 OUT_alpha.webm
```
- 解码必须 `-c:v libvpx-vp9`；原生 vp9 解码会丢 alpha。
- 兼容性优先的“滤色叠加”mp4：黑底 + 亮度字，剪辑软件用 Screen/Lighten 混合。

### 6.3 抽帧验收（别看渲染日志，看图）
```powershell
& $ff -v error -ss 12.4 -i OUT.mp4 -frames:v 1 -q:v 2 -y _check.jpg
```
> 注意：`-ss` 放在 `-i` **前面**（输入 seek）时，某些情况下 ASS 时间轴相对输出被重定向，预览会空白；验证抽帧用**输出侧 seek**（`-i OUT.mp4 -ss 12.4`）或直接抽整段再选。

## 7. 故障速查表
| 现象 | 原因 | 修法 |
|---|---|---|
| 全片一个字都没有 | 时间戳格式 / Style 颜色尾 `&` | 改 `H:MM:SS.cc`；Style 颜色去尾 `&` |
| 部分句没有 | 该句时间戳写错或 start>end | 逐句检查 |
| 字很小/字型不对 | 字体 family 名错 | PIL `getname()` 核对 |
| `\p1` 色块偏上/偏下 | 绘图锚点 + libass 上移 h/2 | `\an7` + 左上绝对坐标 + 实测标定帧 |
| 旋转中心不对 | 默认中心不是想要的 | 加 `\org(x,y)` |
| 淡出没生效/闪烁反了 | alpha 语义反了 | `&H00` 不透明、`&HFF` 透明 |
| 30s 渲染只有前 4 句 | 循环只遍历了前几句 | 检查事件生成循环范围 |
| 中文路径/文件名渲染失败 | filter 参数里带非 ASCII | ASS 与底片用 ASCII 文件名 + 中文 cwd |

## 8. 生成器骨架（Python）
```python
def ts(sec):
    h=int(sec//3600); m=int(sec%3600//60)
    return "%d:%02d:%05.2f" % (h,m,sec-h*3600-m*60)

class Ass:
    def __init__(self,path,w=2560,h=1080): self.ev=[]; self.path=path; self.w=w; self.h=h
    def add(self,layer,t0,t1,tags,text): self.ev.append((layer,t0,t1,tags,text))
    def write(self):
        head = open("template_header.ass",encoding="utf-8").read()  # 或在代码里内联
        lines=[]
        for layer,t0,t1,tags,text in sorted(self.ev,key=lambda e:(e[0],e[1])):
            lines.append("Dialogue: %d,%s,%s,X,,0,0,0,,{%s}%s"%(layer,ts(t0),ts(t1),tags,text))
        open(self.path,"w",encoding="utf-8-sig",newline="\n").write(head+"\n".join(lines)+"\n")
```
参考实现：`字幕/build/styles_anim.py`（S2/S4/S6）、`flare_wide.py`、`neon_wide.py`、`avoid_side2.py`。
