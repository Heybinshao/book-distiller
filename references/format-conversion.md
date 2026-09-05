# 格式转换与命名规范化（完整命令手册）

> SKILL.md 主流程 Step 1 的详细命令。按场景取用；clean_book_title 单一来源是 `scripts/clean_title.py`（下文旧内联位置已改为脚本调用）。

### Step 1: 格式转换

**按输入格式处理：**
- `.epub` → 走下方「epub转md」
- `.pdf` → 走下方「pdf转md」
- `.md` → **跳过 pandoc 转换**：源 md 即书籍文本。直接跑「清理epub残留格式」（clean_md 清理 HTML 残留），并复制为 `01｜书籍原文/{干净书名}.md`——若源文件名不干净，**复制成干净名**（源文件保留原样，或按「源文件命名检查」询问结果处理）

**epub转md：**
```bash
# 第一步：提取干净书名（见下方 clean_book_title 函数），全流程基准名
# 原文件名可能带副标题/括号/作者，统一规范化后再转换
BOOK_TITLE="$(python3 scripts/clean_title.py "${file%.epub}")"
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
  BOOK_TITLE="$(python3 scripts/clean_title.py "${file%.epub}")"
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
BOOK_TITLE="$(python3 scripts/clean_title.py "${file%.pdf}")"
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
转换完成后运行封装脚本（单一来源，不要重写内联版本）：
```bash
python3 scripts/clean_md.py "${BOOK_TITLE}.md"
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



---

# 文件名对齐（三个目录必须一致）

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
