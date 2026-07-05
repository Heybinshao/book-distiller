# 跨平台命令对照

> 供 Agent 参考：macOS 和 Windows 下的等价命令/路径。

---

## 工具检测

| 目的 | macOS (Bash/Zsh) | Windows (PowerShell) |
|------|------------------|---------------------|
| 检测 pandoc | `command -v pandoc` | `where pandoc` |
| 检测 python | `command -v python3` | `where python` |
| 检测 node | `command -v node` | `where node` |
| 检测 git | `command -v git` | `where git` |
| 判断操作系统 | `uname` 返回 `Darwin` | `$env:OS` 包含 `Windows` |

---

## 文件操作

| 目的 | macOS | Windows (PowerShell) |
|------|-------|---------------------|
| 列出 epub 文件 | `ls *.epub 2>/dev/null` | `Get-ChildItem -Filter *.epub` |
| 列出 pdf 文件 | `ls *.pdf 2>/dev/null` | `Get-ChildItem -Filter *.pdf` |
| 获取文件名（去扩展名） | `basename "$file" .epub` | `$_.BaseName` |
| 获取文件大小 | `ls -lh file.md` | `Get-Item file.md \| Select Length` |
| 获取行数 | `wc -l file.md` | `(Get-Content file.md).Count` |
| 检查文件存在 | `test -f file.md` | `Test-Path file.md` |
| 创建目录 | `mkdir -p path` | `New-Item -ItemType Directory -Force` |

---

## Python 命令

| | macOS | Windows |
|--|-------|---------|
| Python 命令 | `python3` | `python` |
| pip 命令 | `pip3` | `pip` |
| 临时脚本路径 | `/tmp/clean_md.py` | `C:\temp\clean_md.py` |
| 检查版本 | `python3 --version` | `python --version` |

---

## 安装命令

| 工具 | macOS | Windows |
|------|-------|---------|
| pandoc | `brew install pandoc` | `winget install pandoc` 或手动下载 |
| python | `brew install python` | `winget install python` 或手动下载 |
| poppler (pdftotext) | `brew install poppler` | `winget install poppler` 或手动下载 |

---

## 路径格式

| | macOS | Windows |
|--|-------|---------|
| 用户目录 | `/Users/用户名/` | `C:\Users\用户名\` |
| 下载目录 | `~/Downloads/` | `C:\Users\用户名\Downloads` |
| 桌面 | `~/Desktop/` | `C:\Users\用户名\Desktop` |
| 临时目录 | `/tmp/` | `C:\temp\` 或 `$env:TEMP` |
