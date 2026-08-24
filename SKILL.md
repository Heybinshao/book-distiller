---
name: book-distiller
description: 【书籍榨干器】从epub/pdf/md文件提取书籍的完整知识：心智模型、关键概念、金句、案例、反模式、行动清单。
  用户提供文件并说「拆解」「蒸馏」「榨干」时触发。命名规范化提取干净书名作为基准名（去副标题/括号/作者冗余，保留系列号），
  转换后自动清理HTML标签、坏图片链接。输出路径读 config.json（默认知识库收集箱/书籍拆解，不存在自动创建）。
author: 彬少
version: 2.0.0
created: 2026-06-25
updated: 2026-08-23
metadata:
  hermes:
    tags: [书籍, 拆解, 蒸馏, 榨干, epub, pdf]
    category: binshao
---

# 书籍榨干器

> 每一本书的知识，100%提取出来，不浪费一页纸。

---

## 快速开始

```
用户：提供epub/pdf/md文件 + "拆解这本书"
→ Step 1：格式转换（epub→md），清理残留格式
→ Step 2：通读全文，提取所有概念、金句、案例、反模式
→ Step 3：写入完整拆解文档
→ Step 4：质量检查，确认输出
→ Step 5：源文件按结果分类归档（可选）
→ Step 6：执行结果报告（产物 + 源文件去向）
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
{config.json output_path}/          # 当前：知识库 01｜收集箱/书籍拆解
├── 01｜书籍原文/           # 转换后的md文件（用干净书名命名）
│   └── {干净书名}.md
└── 02｜蒸馏拆解/           # 拆解后的文档
    └── {干净书名}-完整拆解.md
```

> **子目录名以 config.json 为准**：`original_subdir`（默认 `01｜书籍原文`）和 `distilled_subdir`（默认 `02｜蒸馏拆解`）是可配置字段，正文流程中写死的目录名只是当前默认值。用户改了 config → 全流程跟着用新名字，不要硬编码覆盖。

> 输出到「收集箱/书籍拆解」是设计：拆解产物先进收集箱（处理中），确认质量后由用户决定是否归档到知识库正式位置（如 `Z｜归档文章/01｜书籍拆解/`）。给别人用时，对方改 config.json 的 output_path 指向自己的路径即可——目录不存在会自动创建。

### 配置文件

- 位置：本 skill 目录下的 `config.json`（与 SKILL.md 同级）
- 内容：记录用户指定的输出路径
- **首次使用（config.json 不存在）**：先展示将使用的默认路径（知识库收集箱/书籍拆解），随「使用默认路径吗？」一并询问用户——用户确认后才写入 config；用户指定了其他路径 → 把用户路径写进 config 再继续。**不要在用户确认前静默创建 config**
- 后续使用直接读取，不再重复询问（用户想换路径时说一声即可，改 config 生效）

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
- **超长书名兜底（clean_book_title 处理后仍过长时）**：无冒号分隔的长宣传语连排（如《职场实用写作课涵盖所有实用写作类别写的简洁高效有说服力职场人必备写作宝典套装4册》）是 clean_book_title 的盲区——它只砍 `：`后的内容，砍不了连排宣传语。处理：提取后若书名仍 >25 字，取**开头最短有区分度的书名核心**（上例 →「职场实用写作课」），系列号保留；**必须报告用户确认**简化名后再进入转换，禁止静默截断
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
转换完成后，用 Python 脚本清理非文字内容（可直接复用封装好的脚本 `python3 <skill目录>/scripts/clean_md.py <文件>`，功能与下方内联代码一致）：
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
- 用户确认装错且无正确源文件 → 源文件移入「异常-待确认/」（见批量处理第 10 条），从待拆清单剔除并记录原因

🟡 **CHECKPOINT：非文字书判定（单本必查，防照拆垃圾）**
- 单本拆解同样要先过漫画/绘本判定：书名含「漫画」「绘本」「画集」「摄影」，或抽查正文以对话气泡/图片说明为主 → **先报告用户**：「这本疑似漫画/摄影集，纯文字提取后没有可蒸馏的知识结构，确认要继续吗？」
- 用户确认不拆 → 终止流程，源文件移入「跳过-非文字书/」（见批量处理第 10 条）；用户坚持拆 → 继续，但产出预期按文学/图像类适配

🟡 **CHECKPOINT：覆盖检查（必须在写入/分发 subagent 之前做）**
- 检查两个输出目录：`{配置路径}/01｜书籍原文/{干净书名}.md` 和 `{配置路径}/02｜蒸馏拆解/{干净书名}-完整拆解.md` 是否已存在
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

> ⚠️ **大书也不要按维度分拆多个 subagent**（概念/金句/案例分开各派一个）——实战已否决该路线：协调成本高、易遗漏、命名难对齐。无论单本多大，都是「每本一个 subagent 100% 通读」（批量规范见「epub/md 批量处理」第 8 条），大文件由该 subagent 自己分段读取。

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

- 文档大小检查（**软信号，不设硬指标**——实战 622 本中位 41KB、P5 24KB，执行到位产出天然充分。<10KB 不直接判失败：先确认原文是否本身是薄书，非薄书则抽查内容密度，警惕执行不到位）
- **结构五件套是否齐全**：金句集锦 / 反模式清单 / 批判性审视 / 行动清单 / 一句话总结？
- ⚠️ **快速拆解模式豁免**：用户选了「快速拆解/只要重点」→ 本步跳过五件套检查（该模式本就只出 P0），只验核心命题 + 关键概念是否完整，避免把正常产出误判为不合格
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

拆解完成后，把源文件（epub/pdf/md）**按结果分类归档**，与批量处理第 10 条同一套口径：
- ✅ 拆解成功 → `已拆解/`
- 🚫 漫画/摄影跳过（用户确认） → `跳过-非文字书/`
- ⚠️ 装错书（用户确认且无正确源文件） → `异常-待确认/`
- ❌ 拆解失败无产物 → `失败-待重试/`
- 目录位置：原文件同目录创建对应子目录；用户说「不要移动」→ 全部留在原地（源文件自行管理）

### Step 6: 执行结果报告（单本必做）

全部步骤完成后，向用户输出一份双维度结果报告：

```
## 拆解完成报告

【产物】
- 拆解文档：{配置路径}/02｜蒸馏拆解/{干净书名}-完整拆解.md（{大小}）
- 书籍原文：{配置路径}/01｜书籍原文/{干净书名}.md
- 质量检查：五件套齐全情况 / 概念数 / 金句数

【源文件】
- 处理结果：✅ 已拆解 / 🚫 跳过 / ⚠️ 异常待确认 / ❌ 待重试
- 去向：{归档目录完整路径} 或「原地保留（用户要求不移动）」
```

批量场景同一份报告结构，外加各归档类目的数量清单（见批量处理第 11 条）。

---

## 特殊场景

### epub/md 批量处理

> **md 文件同样适用本节全部流程**：目录里混有 .md 源文件时，md 跳过 pandoc 转换（源文件即文本，直接复制为干净名），但**筛选四查（关键词校验/同书去重/非文字书判定/覆盖检查）与五类归档一个不少**——md 同样可能是漫画、重复、装错书。

1. 用pandoc批量转换（python脚本循环调用；.md 文件跳过转换直接用），每本先 clean_book_title 提取干净书名
2. 清理epub残留格式
3. 每本执行「书名关键词校验」（见 Step 1 CHECKPOINT），0 次出现时报告用户确认，不要闷头拆
4. **同书重复检测**：批量清单中可能出现同一本书的多个条目指向同一个 md 文件（如无后缀版和带后缀版）。用 MD5 对比源文件内容，相同则去重只拆一份，另一条记入 skipped 列表
5. **非文字书跳过（分发前必做）**：漫画、绘本、摄影集等以图为主的书**不拆**——纯文字提取后没有可蒸馏的知识结构，产出必是垃圾。判定方法：书名含「漫画」「绘本」「画集」「摄影」，或转换后抽查正文发现以对话气泡/图片说明为主 → 直接记入 skipped 列表（附 reason=漫画/摄影），不派 subagent。实战案例：622 本批次跳过《纳闷集》《真有意思》等数十本漫画
6. 按文件大小从小到大排序，优先处理小文件
7. **覆盖检查（分发前必做）**：列出所有目标文件——`{原文目录}/{干净书名}.md` 和 `{蒸馏目录}/{干净书名}-完整拆解.md` **两个输出目录都要查**（上次转换/拆解中断的残留会冲突），标记已存在的 → 告知用户清单，询问「这些已存在，是否覆盖？」；用户确认后才进入下一步；未经确认不写入，**绝不自动创建副本**
8. **每本一个 subagent 并行拆解**（`delegate_task`，一次 5 个并行——实战 622 本验证 5 并发最优，8 并发 524 率飙升；每本 subagent 必须包含下述铁律 prompt + 分段写入规范）。⚠️ 第 3-7 条全部是筛选/检查步骤，**必须全部完成后再执行本条分发**——检查类步骤排在分发之后等于没查
9. **进度落盘（断点续跑）**：用 `worklist.json`（待拆清单）+ `progress.json`（已完成/跳过/失败/剩余）记录进度，存放在工作目录。每批完成后更新。中断后可从断点继续，不重复已拆的书。状态口径：
   - `completed`：拆解成功（五件套齐全）
   - `skipped`：漫画/重复等主动跳过（附 reason）
   - `failed`：subagent 失败无产物——断点续跑时**视为待拆**自动重试，重试成功迁入 `completed`；连续 2 次失败的书暂停重试、汇总时单独列出，由用户决定是否换模型/时段再跑
10. 拆解完成后**按结果分类归档源文件**（避免下次重复处理 + 排除件可追溯）：
   - ✅ 已成功拆完 → `已拆解/`
   - 🚫 漫画/摄影等非文字书 → `跳过-非文字书/`
   - 🔁 MD5 重复未拆的副本 → `重复-未拆/`
   - ⚠️ 装错书/校验失败待确认 → `异常-待确认/`（需人工判断的件）
   - ❌ subagent 失败无产物（429 过载/524 反复失败/超时）→ `失败-待重试/`——内容没问题，重试即可成功，与「异常-待确认」分开，避免和需人工判断的件混淆；重试成功后移入 `已拆解/`
   - 目录位置：单本/任意路径场景在原文件同目录创建这些子目录；用户整理好的批量库（待拆解/已拆解 结构）与待拆目录同级创建；用户说「不要移动」→ 全部留在原地
11. 汇总报告：成功/失败清单、五类归档目录各自的数量与代表文件、输出路径、质量检查（大小 + 结构五件套）
12. **工作目录清理询问（全部完成后必做）**：批量拆解会在工作目录留下 `worklist.json` / `progress.json` / `skipped_comics.json` 等断点续跑账本和临时脚本。**触发时机**：仅当待拆清单清空（所有书均为 completed/skipped 终态）且用户没有「继续下一批」意图时——分批节奏下（如「弄完这批暂停」）账本仍要用于续跑，**不询问清理**。触发后主动询问用户：「工作目录里的进度账本（记录了本次批量任务的完成/跳过状态，用于断点续跑）已经没用了，是否删除整个工作目录？」——告知用途后再删，不静默保留、也不未经确认直接删

**subagent prompt 模板**：见 `templates/subagent-prompt.md`（必须原文使用，铁律行不要删——它们是输出密度的关键；同时必须附带「分段写入规范」和「半成品补尾机制」——622 本实战中缺了这两条会导致大量 524 超时和并行脚本污染）。

**为什么每本一个 subagent 而不是多维拆**：单本专注 100% 通读，输出密度最高（实战 84-188KB/本）；按维度拆（概念/案例/金句分开）协调成本高、易遗漏、命名难对齐。

**质量检查流程（每批完成后父 agent 执行）**：
1. 逐本检查五件套是否齐全（金句集锦/反模式清单/批判性审视/行动清单/一句话总结）
2. 检查有无重复章节标题（追加写入时可能产生重复段）
3. 归一化章节标题：去中文序号前缀（「一、」→删除）、降级错误的一级标题（`# 金句集锦`→`## 金句集锦`）
4. 半成品处理：概念写完但缺五件套 → 派轻量补尾任务（非整本重拆）；概念都没写完 → 整本重试
5. 每 10 本随机深读 1 本对照原文抽查内容深度

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
  2. if 明显偏小(<10KB) → 先确认原文是否本身是薄书；非薄书 → 抽查内容密度，重新启动subagent强调"不要合并、不要省略"
  3. 检查是否包含所有必要部分（金句、案例、行动清单）

if 框架重复或冲突:
  1. 检查是否有相似的框架
  2. if 重复 → 合并或选择更完整的版本
  3. if 冲突 → 保留两个版本，标注内在张力

if subagent 卡住/无产出/超时:
  1. 不要无限等待——超过预期时间（如 10 分钟无进展）主动取消
  2. 取消后重新 spawn 该 subagent，prompt 强调「100% 通读 + 铁律」
  3. 单本失败不影响其他本；批量中失败的单独记录，最后统一重试

if subagent 报 HTTP 524:
  1. 根因：单次 API 生成 >120s 被 Cloudflare 网关掐断（大文档一次性生成必踩）
  2. 解法：subagent prompt 里强制「分段写入」——write_file 写首段（≤5KB），后续段落写独占命名临时脚本再 python3 执行追加，禁止一次生成整份
  3. 已写入 templates/subagent-prompt.md 的「分段写入」规范，照抄即可

if subagent 报 HTTP 429 (model at capacity):
  1. 上游模型暂时过载，非本地问题
  2. 等几分钟后重新 spawn 该 subagent 即可
  3. 批量场景下连续多个 429 → 暂停几分钟再继续

if delegation 子代理超时:
  1. 默认无超时，但网关空闲超时会兜底杀掉长时间无活动的子代理
  2. 可通过 config.yaml 设置 `delegation.child_timeout_seconds: 1800` 给大书留够余量
  3. 超时的子代理可能已有半成品落盘 → 先检查磁盘产物再决定补尾还是重拆

if 并行 subagent 临时脚本互相覆盖:
  1. 根因：多个 subagent 用了相同的 /tmp/append_xxx.py 文件名
  2. 预防：subagent prompt 强制要求独占文件名 /tmp/append_{书名前3字}_{段号}.py
  3. 已污染的文件：读输出文件检查有无兄弟任务内容混入，有则定位删除重复段

if 同一本书出现多个文件名:
  1. 用 MD5 对比源文件内容，相同则为同书重复
  2. 去重只拆一份，另一条记入 skipped 列表（附原因）
  3. 实战案例：清单革命/清单革命（新版）、把时间当作朋友/把时间当作朋友（第3版）等

if 源文件装错书:
  1. 拆前校验：取干净书名核心词在正文中搜索，0 次 = 可能装错
  2. 报告用户确认，不自行判定
  3. 确认装错后：从待拆清单剔除并记录原因；若已有正确源文件则改名后重拆
  4. 实战案例：麦肯锡图表工作法→实为高频交易员、从零开始做运营入门篇→实为互联网思维独孤九剑、力量→实为同名小说

if 输出文档章节标题带序号或层级错误:
  1. 归一化脚本处理：去中文序号前缀（`## 一、xxx` → `## xxx`）
  2. 五件套标题统一为 ## 二级（`# 金句集锦` → `## 金句集锦`）
  3. 在质检阶段批量执行，不需要重拆

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

---

## 关于作者固定文案（发布时必用）

每次发布（README/公众号/GitHub 等）不重写、不省略公众号引流，使用固定文案：

> **彬少** —— 一个什么都折腾一下的人：装系统 · 玩AI · 搭知识库 · 做设计。这套 Skill 是我自己在用的，<该 skill 一句话定位>。微信公众号 **「宝藏彬少」**：折腾，是为了更好用。欢迎关注交流。

- GitHub 显示名已改「彬少」，署名用彬少、公众号名保留宝藏彬少
- 写前先读本 skill README 对原文，不凭记忆改写（曾只写品牌定位、漏掉公众号引流被纠正）
