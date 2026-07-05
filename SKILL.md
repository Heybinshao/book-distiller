---
name: book-distiller-universal
description: 【书籍榨干器·通用版】从epub/pdf/md文件提取书籍完整知识的通用型Skill。环境自检、交互引导，支持单文件和批量处理，适配macOS和Windows。触发词：拆书、拆解、榨干、蒸馏。
author: 宝藏彬少
version: 2.0.0
created: 2026-07-06
tags:
  - 书籍
  - 拆解
  - 蒸馏
  - epub
  - pdf
---

# 【书籍榨干器·通用版】

> 每一本书的知识，100%提取出来，不浪费一页纸。

**书籍榨干器** 是一个通用型 AI 拆书 Skill。你提供 epub/pdf/md 文件，它自动提取出核心命题、关键概念、案例、金句、行动清单等结构化知识。

---

## 简介

| 项目 | 说明 |
|------|------|
| **用途** | 把一本书的核心知识提取成结构化拆解文档 |
| **输入** | epub / pdf / md 文件（单本）或含这些文件的文件夹（批量） |
| **输出** | 一份 Markdown 拆解文档，含核心命题、概念、案例、金句、反模式、行动清单 |
| **前置条件** | 需要安装 pandoc + Python 3（环境检测会自动检查） |
| **适用平台** | macOS / Windows |
| **适用 Agent** | Hermes、MiMo Code、Codex 等支持文件操作和代码执行的 AI 编程助手 |

---

## 快速开始

只需对 AI 说一句话：

> **「拆解这本书，文件在 /Users/xxx/Downloads/思考快与慢.epub」**

AI 会自动完成：
环境检测 → 格式转换 → 通读提取 → 输出文档 → 移动已拆解 → 质量检查

更多触发方式见下方「使用方式」表格。

---

## 使用方式

用户通过以下方式触发：

| 用户说 | 触发模式 |
|--------|---------|
| 「拆解这本书，文件在 xxx.epub」 | 单文件模式 |
| 「帮我拆解这个文件夹，路径在 xxx」 | 批量模式 |
| 「榨干这本书」/「蒸馏这本书」 | 单文件模式 |

收到指令后，自动判断模式并开始执行。

---

## 模式选择

本 Skill 支持两种模式：

| 模式 | 适用场景 | 用户提供 |
|------|---------|---------|
| **单文件模式** | 第一次使用、只想拆一本书 | 一个 epub/pdf/md 文件路径 |
| **批量模式** | 有多本书要拆、熟悉流程后 | 一个文件夹路径 |

---

## 📄 单文件模式

### 第一步：环境检测

用户提供文件路径后，先检查环境。

**检查方式：** 尝试执行以下命令。如果能跑通，说明工具已安装；如果报错，引导用户安装。

```bash
# 检查 pandoc（epub→md 转换）
pandoc --version

# 检查 python（格式清理）
# macOS: python3 --version
# Windows: python --version
```

**检测报告模板：**

```
📋 环境检测结果：
✅ pandoc — 已就绪
✅ Python — 已就绪
→ 可以开始拆书
```

如果缺少工具，给出安装指引，让用户装完再试。

### 第二步：格式转换

用 `pandoc` 把 epub/pdf 转成 Markdown 文本。

```bash
# macOS / Windows（命令相同，pandoc 跨平台）
pandoc "输入文件路径" -t markdown --wrap=none -o "临时文件路径.md"
```

转换后，用 Python 清理残留的格式垃圾。把以下代码中的 `文件路径` 替换为实际的 md 文件路径，然后执行：

```python
import re

input_file = "替换为实际的md文件路径"

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 删除图片引用
content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
# 删除HTML/SVG标签
content = re.sub(r'<[^>]+>', '', content)
# 删除CSS类标记
content = re.sub(r'\{\.?[a-zA-Z][^}]*\}', '', content)
# 合并连续空行（超过3行的缩成3行）
content = re.sub(r'\n{4,}', '\n\n\n', content)

with open(input_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ 格式清理完成：{input_file}")
```

**如何执行这段 Python 代码：**

| 方式 | 说明 |
|------|------|
| 有代码执行环境 | 直接运行上面的代码，把路径替换成实际 md 文件路径 |
| 只有终端/命令行 | 把代码保存为 `.py` 文件，用 `sys.argv[1]` 接收路径参数，然后执行 |
| 其他 | 只要能运行 Python 就行，不限方式 |

> 批量处理多文件时，建议用第二种方式（创建临时脚本 + 传参循环调用）。

### 第三步：通读全文

通读清理后的 md 文件，提取书中所有核心内容。

**大文件处理规则：**
- 文件不大 → 一次读完
- 文件很大 → 分多次读取，每次读一部分，直到全部读完

**提取清单：**

| 提取项 | 说明 |
|--------|------|
| **核心命题** | 这本书想论证什么？一句话概括 |
| **关键概念** | 作者定义了什么新概念、新术语？每个独立成段 |
| **心智模型/框架** | 作者用了什么分析框架？列出结构 |
| **案例** | 书中用什么案例支撑论点？保留细节 |
| **金句** | 原话保留，标注章节位置 |
| **反模式** | 作者反对什么做法？ |
| **行动清单** | 读完可以做什么？ |

### 第四步：输出拆解文档

按以下格式写入文件。输出路径默认为原文件同目录，文件名为 `{原文件名}-完整拆解.md`。

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

> "[原话]" — 第X章

---

## 反模式清单

| 反模式 | 危害 | 书中建议 |
|--------|------|---------|

---

## 行动清单

1. [具体行动1]
2. [具体行动2]

---

## 一句话总结

[全书最核心的一句话]
```

### 第五步：移动已拆解文件

拆解完成后，把原文件移到「已拆解」目录，避免下次重复处理。

**如果没有「已拆解」目录，在原文件同目录创建一个**，命名 `已拆解/`。

```bash
# macOS
mkdir -p "原文件所在目录/已拆解"
mv "原文件路径" "原文件所在目录/已拆解/"

# Windows（PowerShell）
New-Item -ItemType Directory -Force -Path "原文件所在目录\已拆解"
Move-Item "原文件路径" "原文件所在目录\已拆解\"
```

> 如果用户说「不要移动」，则跳过此步。

### 第六步：质量检查

- 文档大小是否合理（目标 15KB+）？
- 是否覆盖了所有主要章节？
- 是否包含金句、案例、行动清单？
- 核心命题是否准确？

检查通过后，告知用户文件保存位置。

---

## 📚 批量模式

### 第一步：环境检测（同上）

### 第二步：扫描文件夹

列出指定文件夹中的所有 epub/pdf/md 文件。

```bash
# macOS
ls "文件夹路径"/*.epub 2>/dev/null
ls "文件夹路径"/*.pdf 2>/dev/null
ls "文件夹路径"/*.md 2>/dev/null

# Windows（PowerShell）
Get-ChildItem "文件夹路径" -Include *.epub, *.pdf, *.md
```

把文件清单展示给用户确认。例如：

```
📂 找到以下文件（共 8 本）：
1. 思考快与慢.epub
2. 穷查理宝典.epub
3. 影响力.epub
...
确认开始拆解？（Y/N）
```

### 第三步：批量格式转换

遍历所有文件，逐个执行格式转换 + Python 清理。

**支持的文件类型及处理方式：**

| 类型 | 处理方式 |
|------|---------|
| `.epub` | pandoc 转换 → Python 清理 |
| `.pdf` | pandoc 或 pdftotext 转换 → Python 清理 |
| `.md` | 直接使用，跳过转换步骤 |

**先创建一个临时 Python 清理脚本**，内容如下（用 `sys.argv[1]` 接收路径参数）：

```python
import re, sys
input_file = sys.argv[1]
with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()
content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
content = re.sub(r'<[^>]+>', '', content)
content = re.sub(r'\{\.?[a-zA-Z][^}]*\}', '', content)
content = re.sub(r'\n{4,}', '\n\n\n', content)
with open(input_file, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"✅ 清理完成：{input_file}")
```

**如果本 Skill 目录下有 `scripts/clean_md.py`，直接使用它**，路径为 `skill目录/scripts/clean_md.py`。也可以用 `/tmp/clean_md.py` 创建临时副本。

保存后执行批量转换：

```bash
# macOS 批量转换
for ext in epub pdf; do
  for file in "文件夹路径"/*.$ext; do
    [ -f "$file" ] || continue
    pandoc "$file" -t markdown --wrap=none -o "文件夹路径/$(basename "$file" .$ext).md"
    python3 /tmp/clean_md.py "文件夹路径/$(basename "$file" .$ext).md"
  done
done
# md 文件跳过转换，直接清理
for file in "文件夹路径"/*.md; do
  [ -f "$file" ] || continue
  python3 /tmp/clean_md.py "$file"
done
```

```powershell
# Windows 批量转换
Get-ChildItem "文件夹路径" -Include *.epub, *.pdf, *.md | ForEach-Object {
  if ($_.Extension -eq '.md') {
    python C:\temp\clean_md.py $_.FullName
  } else {
    $mdPath = Join-Path $_.DirectoryName "$($_.BaseName).md"
    pandoc $_.FullName -t markdown --wrap=none -o $mdPath
    python C:\temp\clean_md.py $mdPath
  }
}
```

> **输出目录说明：** 转换后的 md 文件与原 epub 放在同一目录。后续的拆解文档也默认输出到该目录。用户也可以指定单独的输出目录。

### 第四步：并行拆解

对每本已转换的 md 文件执行通读和提取（流程同单文件模式第三步）。

**并行策略：**

**方案一：多 Agent 并行（推荐，速度快）**
适用于 MiMo Code、Hermes 等支持多 Agent 的工具：
- 根据文件数量启动子任务（建议 ≤ 5 个）
- 每个子任务负责一本：通读 → 提取 → 写入拆解文档
- 所有子任务完成后，汇总结果

**方案二：逐本处理（兼容，速度慢）**
适用于不支持并行的 Agent：
- 按文件名排序，逐本处理
- 每本完成后更新进度：「已完成 3/8 本...」

每本的拆解文档独立输出，命名规则：`{原文件名}-完整拆解.md`

### 第五步：汇总报告

所有书拆解完成后，给用户一份汇总（输出目录默认为原文件所在目录）：

```
📊 拆解完成报告：
✅ 成功：8 本
❌ 失败：0 本

文件位置：{原文件目录}
├── 思考快与慢-完整拆解.md（28KB）
├── 穷查理宝典-完整拆解.md（35KB）
├── 影响力-完整拆解.md（22KB）
...
```

如果有失败的，列出失败的文件和原因。

---

## 核心原则

```
完整 > 原话 > 结构 > 篇幅
```

- 宁可长，不要漏
- 不合并概念，不省略案例，不精简金句
- 金句必须保留书中原话
- 每个概念独立成段

---

## 常见问题

### Q：pandoc 没安装怎么办？

**macOS：** 打开终端，运行 `brew install pandoc`
**Windows：** 打开 PowerShell（管理员），运行 `winget install pandoc`；或去 pandoc.org 下载安装包
安装后重新说「拆解这本书」就行。

### Q：Python 没安装怎么办？

**macOS：** 打开终端，运行 `brew install python`
**Windows：** 打开 PowerShell（管理员），运行 `winget install python`；或去 python.org 下载
> macOS 上用 `python3` 命令，Windows 上用 `python` 命令

### Q：批量拆到一半卡住了怎么办？

取消当前任务，检查哪些书已经拆完，哪些还没拆，从断点继续。建议每批不超过 **5 本**，不容易触发限速。

### Q：Windows 上路径里有中文会乱码吗？

PowerShell 对中文路径支持良好，直接用完整路径即可。如果遇到问题，尝试把文件移到路径不含中文的目录（如 `C:\books\`）。

### Q：拆解文档太短了？

有些书本身内容就少（如小册子、工具书）。如果确实有遗漏，告诉我哪本，我重新通读补充。

---

## 输出示例

**macOS 示例：**
```
~/Downloads/思考快与慢-完整拆解.md
├── 核心命题：人类思维的两个系统
├── 关键概念（12个）：系统1/系统2、锚定效应、可得性启发...
├── 金句集锦（8条）
├── 反模式清单（5条）
├── 行动清单（6条）
└── 一句话总结
```

**Windows 示例：**
```
C:\Users\用户名\Downloads\思考快与慢-完整拆解.md
├── 核心命题：人类思维的两个系统
├── 关键概念（12个）：系统1/系统2、锚定效应、可得性启发...
├── 金句集锦（8条）
├── 反模式清单（5条）
├── 行动清单（6条）
└── 一句话总结
```

---

## 各平台适配参考

不同 AI 编程助手执行这个 Skill 的方式略有不同，但核心流程一致：

| 步骤 | Hermes | Codex | MiMo Code |
|------|--------|-------|-----------|
| **环境检测** | `terminal` 运行检测命令 | 在代码环境运行检测命令 | 在终端运行检测命令 |
| **pandoc 转换** | `terminal` 执行 pandoc | 在代码环境用 subprocess 调用 pandoc | 在终端执行 pandoc |
| **Python 清理** | `execute_code` 直接运行，或用 `terminal` 执行脚本 | 在代码环境直接运行 | 在终端执行 Python 脚本 |
| **通读全文** | 用读取能力逐段读取，内容量大时分多次 | 逐段读取文件内容 | 读取文件内容 |
| **写入输出** | 用写入工具写文件 | 用文件操作写文件 | 写入文件 |
| **并行拆解** | `delegate_task` 多子任务 | 多会话或多线程 | 多 Agent 任务 |

> 所有 Agent 的共同前提：系统需安装 pandoc 和 Python 3。

---

## 许可证

本 Skill 由 **宝藏彬少** 制作，免费使用。
