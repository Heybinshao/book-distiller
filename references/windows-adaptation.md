# Windows 适配（跨平台拆书）

> book-distiller 的 Windows 版本差异。macOS 主流程见 SKILL.md；本文件只列 Windows 特有命令。
> 来源：book-distiller-universal（2.0.0，已合并至此）。

## 环境检测（Windows）

```powershell
# 检查 pandoc（epub→md 转换）
pandoc --version
# 检查 python（格式清理）—— Windows 用 python 而非 python3
python --version
```

**缺失时安装**：
```powershell
winget install pandoc
winget install python
# 或官网下载：pandoc.org / python.org
```

## 单文件转换

```powershell
pandoc "输入文件路径" -t markdown --wrap=none -o "临时文件路径.md"
```

清理脚本与 macOS 相同，但执行用 `python`（不是 python3）。可保存为 `clean_md.py` 用 `sys.argv[1]` 接收路径：

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

## 批量转换（PowerShell）

```powershell
# 先保存 clean_md.py 到 C:\temp\clean_md.py
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

## 移动已拆解文件（PowerShell）

```powershell
New-Item -ItemType Directory -Force -Path "原文件所在目录\已拆解"
Move-Item "原文件路径" "原文件所在目录\已拆解\"
```

## 常见问题（Windows）

| 问题 | 处理 |
|------|------|
| 中文路径乱码 | PowerShell 对中文路径支持良好，直接用完整路径即可；若异常，把文件移到不含中文的目录（如 `C:\books\`） |
| pandoc 没安装 | `winget install pandoc` 或官网下载安装包 |
| python 命令找不到 | 用 `python`（Windows）而非 `python3`（macOS） |
| 批量拆到一半卡住 | 取消当前任务，检查已完成/未完成，从断点继续；并行数与主流程一致（每批 3 本并行），避免限速 |

## 输出示例（Windows）

```
C:\Users\用户名\Downloads\思考快与慢-完整拆解.md
├── 核心命题：人类思维的两个系统
├── 关键概念（12个）：系统1/系统2、锚定效应、可得性启发...
├── 金句集锦（8条）
├── 反模式清单（5条）
├── 行动清单（6条）
└── 一句话总结
```
