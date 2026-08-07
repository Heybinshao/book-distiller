---
name: book-distiller
description: 【书籍榨干器】从epub/pdf/md文件提取书籍的完整知识：心智模型、关键概念、金句、案例、反模式、行动清单。
  用户提供文件并说「拆解」「蒸馏」「榨干」时触发。命名规范化提取干净书名作为基准名（去副标题/括号/作者冗余，保留系列号），
  转换后自动清理HTML标签、坏图片链接。输出路径读 config.json（默认知识库收集箱/书籍拆解，不存在自动创建）。
author: 彬少
version: 1.3.0
created: 2026-06-25
updated: 2026-08-08
metadata:
  hermes:
    tags: [书籍, 拆解, 蒸馏, 榨干, epub, pdf]
    category: personal
---

# 书籍榨干器

> 每一本书的知识，100%提取出来，不浪费一页纸。

---

## 快速开始

```
用户：提供epub/pdf/md文件 + "拆解这本书"
→ Step 1：格式转换（epub→md），清理残留格式
→ Step 2：通读全文，提取所有概念、金句、案例、反模式
→ Step 3：写入完整拆解文档（15KB+）
→ Step 4：质量检查，确认输出
```

---

## 核心理念

这个技能只做一件事：**从一本书中提取所有有价值的内容**。

### 什么是「榨干」

- **完整提取** — 所有独立概念单独列出，不合并、不省略、不人为限制篇幅
- **保留原话** — 金句保留书中原话，案例保留细节，不做转述精简
- **结构清晰** — MOC + 章节 + 附录 的多文件架构，核心内容在前，附录在后
- **可回顾** — 拆解文档要方便日后翻阅，不是写完了就扔

### 什么是不要做

- ❌ 提取图片、封面、插图、图表（只保留文字内容）
- ❌ 保留目录页、版权页、出版社信息、广告页
- ❌ 为了篇幅限制而省略任何有价值的框架或概念
- ❌ 合并多个独立概念为一个
- ❌ 用自己的话概括代替书中原话
- ❌ 只写结论不写论证过程

### 优先级

```
完整 > 原话 > 结构 > 篇幅
```

宁可长，不要漏。拆给自己看的，不是出版。

---

## 书籍蒸馏流程

### 🔴 环境检测（首次使用自动执行）

在开始拆书之前，先检查当前环境是否具备所有工具：

```bash
# 检查 pandoc（epub/md 转换核心工具）
if ! command -v pandoc &>/dev/null; then
    echo "⚠️ 缺少 pandoc — 用于 epub→md 转换"
    echo "   macOS: brew install pandoc"
    echo "   Windows: winget install pandoc 或官网下载"
    echo "   安装后重新启动即可"
    exit 1
fi

# 检查 python3（用于格式清理和批量处理）
if ! command -v python3 &>/dev/null; then
    echo "⚠️ 缺少 python3 — 用于格式清理和批量处理"
    echo "   请安装 Python 3.x (python.org)"
    exit 1
fi

# 检查 opencc（可选，繁体→简体转换）
if command -v opencc &>/dev/null; then
    echo "✅ opencc 已安装 → 支持繁体→简体自动转换"
else
    echo "ℹ️  opencc 未安装 — 处理繁体书籍时需手动安装"
    echo "   macOS: brew install opencc"
fi

# 检查 pdftotext（可选，pdf→md 转换备选工具）
if command -v pdftotext &>/dev/null; then
    echo "✅ pdftotext 已安装 → 支持 pdf→md 转换"
else
    echo "ℹ️  pdftotext 未安装 — pdf 转换将依赖 pandoc（方法1），失败时用 pip install pymupdf（方法3）"
fi

echo "✅ 环境就绪"
```

> **说明**：pandoc 是核心依赖（epub→md 全靠它），python3 用来清理格式垃圾，opencc 只有拆繁体书时才需要，pdftotext/pymupdf 是 pdf 转换的备选工具。如果检测到缺失，安装后重新运行即可。

### 🟡 开始前确认

- 确认文件路径正确
- 确认文件格式（epub/pdf/md）
- **检测输出路径：**
  - 读 config.json 的 `output_path`
  - **如果路径不存在（含 `01｜书籍原文`、`02｜蒸馏拆解` 子目录）→ 自动创建**（`mkdir -p`），不要报错、不要等用户手动建
  - 已有配置 → 使用配置路径
  - 询问：「使用默认路径吗？」或「指定其他路径？」

### 🟡 源文件命名检查（可选操作，不影响拆解命名）

- 用 clean_book_title 对比原文件名与干净书名
- 若不一致（原文件含副标题/括号/作者等冗余）→ **询问用户**：「检测到原文件名含冗余，是否将源文件重命名为「{干净书名}.{ext}」？」
  - 用户同意 → 重命名源文件（epub/pdf/md 均可）
  - 用户拒绝/跳过 → 源文件保留原名
- **无论是否重命名源文件**，转换出的书籍原文和拆解文件一律用干净书名——源文件处理与拆解命名互不影响

### 默认路径

```
{config.json output_path}/          # 当前：你的知识库收集箱/书籍拆解（config.json 可改）
├── 01｜书籍原文/           # 转换后的md文件（用干净书名命名）
│   └── {干净书名}.md
└── 02｜蒸馏拆解/           # 拆解后的文档
    └── {干净书名}-完整拆解.md
```

> 输出到「收集箱/书籍拆解」是设计：拆解产物先进收集箱（处理中），确认质量后由用户决定是否归档到知识库正式位置。给别人用时，对方改 config.json 的 output_path 指向自己的路径即可——目录不存在会自动创建。

### 配置文件

- 位置：`Skill 安装目录下的 config.json（通常在 ~/.hermes/skills/ 下）`
- 内容：记录用户指定的输出路径
- 首次使用时自动创建，后续使用直接读取

### Step 1: 格式转换

**按输入格式处理：**
- `.epub` → 走下方「epub转md」
- `.pdf` → 走下方「pdf转md」
- `.md` → **跳过 pandoc 转换**：源 md 即书籍文本。直接跑「清理epub残留格式」（clean_md 清理 HTML 残留），并复制为 `01｜书籍原文/{干净书名}.md`——若源文件名不干净，**复制成干净名**（源文件保留原样，或按「源文件命名检查」询问结果处理）

**epub转md：**
```bash
# 第一步：提取干净书名（见下方 clean_book_title 函数），全流程基准名
# 原文件名可能带副标题/括号/作者，统一规范化后再转换
BOOK_TITLE="$(python3 -c "
import re, sys
def clean_book_title(filename):
    name = filename
    name = re.sub(r'（[^）]*）', '', name)
    name = re.sub(r'\([^)]*\)', '', name)
    name = re.sub(r'\s*=\s*[^（(]*$', '', name)
    name = re.sub(r'[：:].*$', '', name)
    name = re.sub(r'\s*--?\s*\S+$', '', name)
    name = re.sub(r'\s*[\[\[].*$', '', name)
    name = re.sub(r'\s{2,}', ' ', name)
    return name.strip()
print(clean_book_title(sys.argv[1]))
" "${file%.epub}")"
echo "干净书名: $BOOK_TITLE"

# 基本转换（只提取文字，跳过图片）
pandoc "$file" -t markdown --wrap=none -o "${BOOK_TITLE}.md"

# 转换后清理非文字内容
python3 -c "
import re, sys
with open('${BOOK_TITLE}.md', 'r') as f:
    content = f.read()
# 删除图片引用
content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
# 删除 SVG/HTML
content = re.sub(r'<svg[^>]*>.*?</svg>', '', content, flags=re.DOTALL)
content = re.sub(r'<[^>]+>', '', content)
# 删除 CSS 类标记
content = re.sub(r'\{\.?[a-zA-Z][^}]*\}', '', content)
# 合并连续空行
content = re.sub(r'\n{4,}', '\n\n\n', content)
with open('${BOOK_TITLE}.md', 'w') as f:
    f.write(content)
"

# 批量处理（每本先 clean_book_title 提取干净书名，同单本逻辑）
for file in *.epub; do
  BOOK_TITLE="$(python3 -c "
import re, sys
def clean_book_title(filename):
    name = filename
    name = re.sub(r'（[^）]*）', '', name)
    name = re.sub(r'\([^)]*\)', '', name)
    name = re.sub(r'\s*=\s*[^（(]*$', '', name)
    name = re.sub(r'[：:].*$', '', name)
    name = re.sub(r'\s*--?\s*\S+$', '', name)
    name = re.sub(r'\s*[\[\[].*$', '', name)
    name = re.sub(r'\s{2,}', ' ', name)
    return name.strip()
print(clean_book_title(sys.argv[1]))
" "${file%.epub}")"
  pandoc "$file" -t markdown --wrap=none -o "${BOOK_TITLE}.md"
  # 同样清理非文字内容
  python3 -c "
import re
with open('${BOOK_TITLE}.md', 'r') as f:
    content = f.read()
content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
content = re.sub(r'<svg[^>]*>.*?</svg>', '', content, flags=re.DOTALL)
content = re.sub(r'<[^>]+>', '', content)
content = re.sub(r'\{\.?[a-zA-Z][^}]*\}', '', content)
content = re.sub(r'\n{4,}', '\n\n\n', content)
with open('${BOOK_TITLE}.md', 'w') as f:
    f.write(content)
"
done
```

> ⚠️ **不要用 `sed` 从 metadata 提取书名再裁剪**——`sed 's/ - .*//'` 会把作者名砍掉（`成法 - 稻盛和夫` → `成法`），`sed 's/[:：].*//'` 会把副标题砍掉（`加分：脱颖而出` → `加分`）。直接用文件名最可靠。

**命名规范化（重要）**：原文件名可能很长（副标题、括号、作者、英文对照等冗余），转换前统一提取**干净书名**作为全流程基准名：

```python
import re
def clean_book_title(filename):
    """从文件名提取干净书名。顺序：去括号 > 去=英文标题 > 去：副标题 > 去--作者 > 去[出版社]"""
    name = filename
    name = re.sub(r'（[^）]*）', '', name)                  # 去 （副标题）全角括号
    name = re.sub(r'\([^)]*\)', '', name)                 # 去 (副标题/来源) 半角括号
    name = re.sub(r'\s*=\s*[^（(]*$', '', name)           # 去 =英文标题
    name = re.sub(r'[：:].*$', '', name)                  # 去 ：后描述（副标题）
    name = re.sub(r'\s*--?\s*\S+$', '', name)             # 去 --作者 / - 作者
    name = re.sub(r'\s*[\[\[].*$', '', name)             # 去 [出版社]
    name = re.sub(r'\s{2,}', ' ', name)                   # 合并多余空格
    return name.strip()
```

> ⚠️ **顺序很重要**：必须先删括号再删作者——否则 `(Z-Library)` 里的连字符会被当成作者分隔符误删（实测坑）。示例：`三十岁，一切刚刚开始 (李尚龙) (Z-Library)` → `三十岁，一切刚刚开始`；`重来2：更为简单高效的工作方式` → `重来2`。

- **保留系列号**：重来2、好好说话2、财务自由之路Ⅲ 等数字/罗马数字不删（区分系列）
- 提取后全流程统一使用干净名：`{干净书名}.md`（书籍原文）、`{干净书名}-完整拆解.md`（拆解）
- **禁止 subagent 自行简化/改名**——命名由主 agent 统一决定，subagent 只按给定名字输出

**pdf转md：**
```bash
# 文件名若带冗余（副标题/括号/作者），先 clean_book_title 提取干净名再转换（同 epub）
BOOK_TITLE="$(python3 -c "
import re, sys
def clean_book_title(filename):
    name = filename
    name = re.sub(r'（[^）]*）', '', name)
    name = re.sub(r'\([^)]*\)', '', name)
    name = re.sub(r'\s*=\s*[^（(]*$', '', name)
    name = re.sub(r'[：:].*$', '', name)
    name = re.sub(r'\s*--?\s*\S+$', '', name)
    name = re.sub(r'\s*[\[\[].*$', '', name)
    name = re.sub(r'\s{2,}', ' ', name)
    return name.strip()
print(clean_book_title(sys.argv[1]))
" "${file%.pdf}")"
echo "干净书名: $BOOK_TITLE"

# 方法1：pandoc（推荐，只提取文字）
pandoc "$file" -t markdown --wrap=none -o "${BOOK_TITLE}.md"

# 方法2：pdftotext（纯文字提取，跳过图片）
pdftotext "$file" - | python3 -c "
import sys
content = sys.stdin.read()
# 清理多余空行
import re
content = re.sub(r'\n{4,}', '\n\n\n', content)
print(content)
" > "${BOOK_TITLE}.md"

# 方法3：python工具（如果以上都失败）
pip install pymupdf
python3 -c "
import fitz
doc = fitz.open('$file')
text = ''
for page in doc:
    text += page.get_text()
with open('${BOOK_TITLE}.md', 'w') as f:
    f.write(text)
"
```

**清理epub残留格式：**
转换完成后，用 Python 脚本清理非文字内容：
```python
import re, os

def clean_md(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 删除所有图片引用（封面、插图、图表）
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)

    # 2. 删除SVG/HTML标签
    content = re.sub(r'<svg[^>]*>.*?</svg>', '', content, flags=re.DOTALL)
    content = re.sub(r'<[^>]+>', '', content)

    # 3. 删除CSS类标记
    content = re.sub(r'\{\.?[a-zA-Z][^}]*\}', '', content)

    # 4. 删除常见非文字页面（目录、版权、出版社信息）
    # 匹配 "目录"、"版权"、"出版"、"印刷"、"发行" 等段落
    content = re.sub(r'^.*?(版权信息|出版信息|印刷|发行|CIP数据|ISBN).*$', '', content, flags=re.MULTILINE)

    # 5. 合并连续空行
    content = re.sub(r'\n{4,}', '\n\n\n', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

clean_md('${BOOK_TITLE}.md')
```

**路径处理：**
转换产物 `${BOOK_TITLE}.md` 生成在当前工作目录，**必须移动到原文目录**：
```bash
# 确保目录存在并移入原文目录（epub/pdf 转换后必做，md 分支同理）
mkdir -p "{配置路径}/01｜书籍原文"
mv "${BOOK_TITLE}.md" "{配置路径}/01｜书籍原文/"
```
- 原文：`{配置路径}/01｜书籍原文/{BOOK_TITLE}.md`
- 最终文档：`{配置路径}/02｜蒸馏拆解/{BOOK_TITLE}-完整拆解.md`

🟡 **CHECKPOINT：格式转换确认**
- 确认转换成功
- 确认文件大小合理

🟡 **CHECKPOINT：书名关键词校验（防装错书）**
- 转换完成后，取干净书名的**核心词**在 md 正文中搜索
- **核心词提取**：干净书名去掉系列号（重来2 → 重来）、去掉通用词（「入门」「指南」「完全手册」等）后，剩余的最短有区分度词（2-6 字）
- **0 次出现的两种可能**：① 源文件装错书（实战：「麦肯锡图表工作法.epub」实为《高频交易员》，「麦肯锡」全书 0 次）；② 正常——系列书/主题书正文不写书名（如《重来2》正文讲远程办公，不一定出现「重来」）
- 处理：**报告用户确认**（附核心词与出现次数），由用户决定继续拆还是另找源文件；**不要自行判定装错书**

🟡 **CHECKPOINT：覆盖检查（必须在写入/分发 subagent 之前做）**
- 检查目标文件 `{配置路径}/02｜蒸馏拆解/{干净书名}-完整拆解.md` 是否已存在
- **已存在** → 明确告知用户，询问「是否覆盖？」，用户确认后才进入 Step 2
- 未经确认不写入；**绝不自动创建副本**（`xxx 1.md`、`xxx-copy.md` 一律禁止）

### Step 2: 通读全文并提取

**先确认拆解模式**（用户没说时默认完整拆解）：
- 用户说「快速拆解/只要重点」→ **只提 P0**（核心命题、关键概念、心智模型/框架），不提取金句/案例/反模式/行动清单
- 用户说「完整拆解」或没说 → P0+P1+P2 全提（默认路径，见下方完整流程）
- 优先级定义见 `references/extraction-framework.md` 第三节

用Read工具通读全文（大文件需多次Read，offset递增）。目标是100%覆盖。

> ⚠️ **read_file 误判 Binary 的坑（2026-08-04 实测）**：read_file 工具对「中文内容为主、超过约 1KB 的文件」可能误报 `Binary file - cannot display as text`——文件本身完全正常（`file` 命令显示 Unicode text、python 读取无碍、无 NUL 字节），是工具二进制启发式对非 ASCII 占比高的采样判定过严。**遇到就改用 python 分段读取兜底，不要跟 read_file 较劲**：
> ```bash
> python3 -c "
> with open('{文件路径}', encoding='utf-8') as f:
>     content = f.read()
> lines = content.split('\n')
> print(len(lines))
> "
> # 然后分段 print（如每段 300-500 行，多次执行确保读完 100%）
> ```
> 派 subagent 拆书时，**必须在 subagent prompt 里明确指示用 python 读取**，否则 subagent 的 read_file 会同样失败。

通读的同时，提取书中出现的每一个：
- **核心命题** — 这本书想论证什么
- **关键概念** — 作者定义了什么新概念、新术语
- **心智模型/框架** — 作者用了什么分析框架
- **核心公式** — 如果有公式或模型图
- **案例** — 书中用了什么案例来支撑论点
- **金句** — 原话保留，标注章节位置
- **反模式** — 作者反对什么做法
- **行动清单** — 读完可以做什么

**原则**：不要合并、不要省略、不要精简。保留书中原话金句和具体案例细节。

如果书籍内容量较大（>2000行或概念密集），用 `delegate_task` 分拆多个 subagent 并行提取：
- subagent 1：提取核心概念和心智模型
- subagent 2：提取案例、金句和引用
- subagent 3：提取反模式、行动清单和隐含假设
每个 subagent 传入 Step 1 转换后的 md 文件路径，避免重复读取。

### Step 3: 写入完整文档

拆解文档格式如下：

```markdown
# [书名] - 完整拆解

> [一句话核心命题]

---

## [主题1名称]

### [概念1名称]
**定义**：[一句话描述]

**机制**：[如何运作]

**案例**：[书中的具体案例]

**启示**：[可操作的行动建议]

### [概念2名称]
...

---

## [主题2名称]
...

---

## 金句集锦

> "[原话1]" — 第X章

> "[原话2]" — 第X章
...

> **空行规范（必须遵守）**：金句与金句之间、定义/机制/案例/启示之间必须空行，否则 Obsidian 渲染会挤在一起（连续 `>` 引用会被合并成一个引用块）。

---

## 反模式清单

| 反模式 | 危害 | 书中建议 |
|--------|------|---------|

---

## 批判性审视

| 书中观点 | 质疑 | 我的看法 |
|---------|------|---------|

---

## 行动清单

读完这本书，我可以：

1. [具体行动1]
2. [具体行动2]
...

> **分组规范**：行动清单若按视角/主题分组（如员工视角/老板视角/通用），每组列表**各自从 1 开始编号**，不要跨组连续编号（粗体标题会割断列表，渲染易错乱）。

---

## 一句话总结

[全书最核心的一句话]
```

### Step 4: 质量检查

- 文档大小是否达标（**目标15KB+，不设上限**——宁可长不要漏）？
- **结构五件套是否齐全**：金句集锦 / 反模式清单 / 批判性审视 / 行动清单 / 一句话总结？
- **拆解/原文比例检查**：拆解文档 ≤ 原文 ~**80%**——正常结构化重构约 30-60%（实战 5 本：84-188KB 拆解 vs 173-463KB 原文 ≈ 30-55%）。超过 80% → 警惕**原文照搬**（AI 偷懒复制段落而非重构），应重新拆
- 是否覆盖了书中的所有主要章节？
- 每个概念是否独立成段？
- 是否包含金句、案例、行动清单？

🔴 **CHECKPOINT：最终输出确认**
- 展示文档结构和大小
- 展示提取的概念/框架数量
- 确认输出路径：`{配置路径}/02｜蒸馏拆解/{干净书名}-完整拆解.md`
- 覆盖与否已在分发前确认（见「覆盖检查」）；此处只确认输出质量和发布
- 等用户确认后再发布

### Step 5: 移动源文件（可选）

拆解完成后，把源文件（epub/pdf/md）移到「已拆解」目录，避免下次重复处理：
- 原文件所在目录已有 `已拆解/` → 直接移入
- 没有 → 在原文件同目录创建 `已拆解/` 并移入
- 用户说「不要移动」→ 跳过此步（源文件留在原地，用户自行管理）

---

## 特殊场景

### epub批量处理

1. 用pandoc批量转换（python脚本循环调用），每本先 clean_book_title 提取干净书名
2. 清理epub残留格式
3. 每本执行「书名关键词校验」（见 Step 1 CHECKPOINT），0 次出现时报告用户确认，不要闷头拆
4. 按文件大小从小到大排序，优先处理小文件
5. **覆盖检查（分发 subagent 之前，必须先做）**：列出所有目标文件 `02｜蒸馏拆解/{干净书名}-完整拆解.md`，标记其中已存在的 → 告知用户清单，询问「这些已存在，是否覆盖？」；用户确认后才进入下一步；未经确认不写入，**绝不自动创建副本**
6. **每本一个 subagent 并行拆解**（`delegate_task`，一次 3 个并行；每本 subagent 必须包含下述铁律 prompt）
7. 拆解完成后**移动 epub 到「已拆解」目录**，避免下次重复处理。分两种情况：
   - **待拆解/已拆解 结构**（用户整理的批量库）→ 移入与待拆解同级的「已拆解」目录
   - **单本/任意路径直接给文件** → 在原文件**同目录**创建 `已拆解/` 子目录并移入（没有就 `mkdir -p`）
   - 如果用户说「不要移动」，跳过此步
8. 汇总报告：成功/失败清单、输出路径、质量检查（大小 + 结构五件套）

**subagent prompt 模板**：见 `templates/subagent-prompt.md`（必须原文使用，铁律行不要删——它们是输出密度的关键，实战产出 84-188KB/本；删了会退回 17KB 的浓缩版）。

**为什么每本一个 subagent 而不是多维拆**：单本专注 100% 通读，输出密度最高（实战 84-188KB/本）；按维度拆（概念/案例/金句分开）协调成本高、易遗漏、命名难对齐。

### 文件名对齐（三个目录必须一致）

当 epub、书籍原文、蒸馏拆解三个目录的文件名不一致时，以**干净书名**为准（见 Step 1 命名规范化）：

```
01-书籍｜epub/已拆解/书名 - 作者.epub     ← 源头（保留原始名）
01｜书籍原文/干净书名.md                   ← 转换后（命名规范化）
02｜蒸馏拆解/干净书名-完整拆解.md          ← 拆解后（基准名 + 后缀）
```

**常见不一致原因：**
- epub 转 md 时用 metadata 提取书名 + sed 裁剪，丢失了作者/副标题（已修复为直接用文件名）
- 批量处理时 sed 把 `- `（空格短横线空格）替换成了 `-`（无空格）
- 中文冒号 `：` 被 sed 砍掉

**对齐脚本：**
```python
import os, difflib

epub_names = {os.path.splitext(f)[0] for f in os.listdir(epub_dir)}
md_names = {os.path.splitext(f)[0] for f in os.listdir(md_dir)}

# Find mismatches via fuzzy match
for ep in epub_names - md_names:
    close = difflib.get_close_matches(ep, md_names, n=1, cutoff=0.7)
    if close:
        # Rename md to match epub
        os.rename(os.path.join(md_dir, close[0]+'.md'), os.path.join(md_dir, ep+'.md'))
```

**验证：** 三个目录的去扩展名文件集必须完全相等（数量和名称）。

### 内容整合（从拆解到知识手册）

当用户要求将大量蒸馏拆解整合为知识手册时：

1. **分类** — 用关键词匹配将书籍分入 15-20 个主题（execute_code 脚本）
2. **并行整合** — 用 delegate_task 批量处理，每批 3 个子 agent，每个负责 2-3 个主题
3. **每个子 agent 的任务**：读取主题下所有书籍 → 按逻辑重组（不是逐书摘要）→ 标注来源 → 写入文件
4. **质量检查** — 统计文件大小、检查主题重叠、识别缺失主题
5. **迭代修复** — 拆分过大主题、补充缺失章节、加交叉引用
6. **建 MOC** — 总览表 + 学习路线（按场景推荐）+ 数据来源

**已知陷阱：**
- ❌ 用子 agent 更新 MOC 时，如果其他子 agent 还在创建新章节，MOC 会漏掉后来的章节 → 等所有章节完成后再建/更新 MOC
- ❌ 让子 agent「节省篇幅」→ 用户明确要求「不能节省篇幅，不能偷懒」
- ❌ 15 个以上主题用一个「其他」兜底 → 必须拆分为独立文件，否则读者跳跃感强

### 大文件处理（>10000行）

1. 用Read工具分段读取（offset递增，每次2000行）——若 read_file 报 Binary（中文为主大文件的误判，见 Step 2 警告），改用 python 分段 print 读取
2. 或启动 subagent 让它自己分段读取（用 `delegate_task`，prompt 里注明用 python 读取）
3. 提取时按主题分组，避免遗漏

### 跨语言书籍

- epub转md后检查语言
- 如果是繁体中文 → 用opencc转换为简体：`opencc -c t2s -i input.md -o output.md`
  - **opencc 未安装时**（环境检测已提示）：先尝试 `brew install opencc`（macOS）/ `winget install opencc` 或官网安装；无法安装时**询问用户**「是安装 opencc 还是接受繁体原文拆解？」，不静默失败、不假装已转简体
- 如果是英文 → 用agent翻译关键概念的名称

### 其他格式

**pandoc 直接支持的格式**（docx / html / fb2 / odt / rtf / txt 等）：与 epub 流程一致，直接转换，之后走相同的「clean 书名 → 清理 → 校验 → 拆解」：

```bash
pandoc "$file" -t markdown --wrap=none -o "${BOOK_TITLE}.md"
```

**mobi / azw3（Kindle 格式）**：pandoc 不支持，需先转 epub：
- 安装 calibre：macOS `brew install calibre` / Windows `winget install calibre`
- `ebook-convert 输入.mobi 输出.epub` → 转完后走 epub 流程
- 未装 calibre 时**提示用户**，不静默失败、不假装成功

**不支持的格式**：明确告知用户无法处理，建议转 epub 后重试。

### Windows 环境

本 skill 主流程面向 macOS（pandoc + python3）。在 Windows 上使用时：python 命令改为 `python`（无 3 后缀），安装用 `winget install pandoc / python`，批量转换和移动已拆解用 PowerShell 命令——全部见 `references/windows-adaptation.md`。

### 错误恢复

```
if pandoc转换失败:
  1. **先确认文件路径存在**：`ls -lh "$file"`——路径输错/文件不存在是最常见原因，先排除（不存在 → 让用户重给正确路径，不往下走）
  2. 检查pandoc是否安装: pandoc --version
  3. if 未安装 → 安装: brew install pandoc
  4. if 版本过旧 → 升级: brew upgrade pandoc
  5. if 文件损坏 → 检查文件完整性

if epub格式异常:
  1. 检查文件扩展名是否正确
  2. 尝试用calibre转换: calibre-debug -e input.epub
  3. 如果仍然失败 → 提示用户检查文件

if 大文件读取失败:
  1. 检查文件大小: ls -lh file.md
  2. if 超过100MB → 分段处理
  3. if 编码问题 → 检查文件编码: file file.md
  4. if 内存不足 → 分批处理

if 提取的框架太少:
  1. 检查是否通读全文
  2. 检查是否遗漏了某些章节
  3. 重新启动subagent，强调"不要合并、不要省略"

if 输出文档不达标:
  1. 检查文档大小: wc -c output.md
  2. if 小于15KB → 补充更多细节
  3. 检查是否包含所有必要部分（金句、案例、行动清单）

if 框架重复或冲突:
  1. 检查是否有相似的框架
  2. if 重复 → 合并或选择更完整的版本
  3. if 冲突 → 保留两个版本，标注内在张力

if subagent 卡住/无产出/超时:
  1. 不要无限等待——超过预期时间（如 10 分钟无进展）主动取消
  2. 取消后重新 spawn 该 subagent，prompt 强调「100% 通读 + 铁律」
  3. 单本失败不影响其他本；批量中失败的单独记录，最后统一重试

if 用户对输出不满意:
  1. 询问具体哪里不满意
  2. if 框架太多 → 精简，只保留核心
  3. if 框架太少 → 补充更多细节
  4. if 格式问题 → 调整输出格式
```

---

## 常见坑

维护本 skill 时的坑类型（占位符漏列/缺落位命令/检查项漂移等）见 `references/common-pitfalls.md`。

---

## 最后

**书籍蒸馏的核心承诺：每一本书的知识，都要100%提取出来，不浪费一页纸。**

一个好的拆解文档，让你不用重读整本书也能抓住它的核心——但如果你想深挖某个点，原书还在那里。

---

## 内容整合

当需要将大量已拆解书籍整合成主题化手册时，见：
- `references/content-integration-workflow.md` — 从蒸馏拆解到知识手册的完整工作流（主题分类→并行整合→质量检查→MOC）

---

## 参考文件

- `references/extraction-framework.md` — 概念识别方法论，帮你判断什么值得提取
- `references/content-integration-workflow.md` — 内容整合工作流（批量整合→主题手册）
- `references/windows-adaptation.md` — Windows 环境适配（python/PowerShell 命令、中文路径问题）
- `references/common-pitfalls.md` — 维护本 skill 时的常见坑类型（占位符漏列/缺落位命令/检查项漂移等）
- `templates/subagent-prompt.md` — subagent 拆书 prompt 模板（铁律完整版，批量/单本拆解必用）
- `scripts/quality_check.py` — 输出质量检查脚本，可快速验证拆解文档完整性
