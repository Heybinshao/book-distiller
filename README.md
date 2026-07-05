# 📖 书籍榨干器 · 通用版

> 把你的 epub/pdf 丢给 AI，自动拆出核心知识。**不需要任何技术背景。**

---

## 这是什么

一个通用的 AI 拆书 Skill。你提供文件，它自动完成：

```
epub/pdf/md 文件 → 格式转换 → 通读提取 → 结构化拆解文档
```

输出的拆解文档包含：核心命题、关键概念、案例、金句、反模式、行动清单。

---

## 前置条件

需要安装两个工具（环境检测会自动检查，缺哪个会提示你装）：

| 工具 | 用途 | macOS | Windows |
|------|------|-------|---------|
| pandoc | epub/pdf→md 转换 | `brew install pandoc` | `winget install pandoc` |
| Python 3 | 格式清理 | `brew install python` | `winget install python` |

---

## 快速开始

对你的 AI 编程助手说一句话：

> **「拆解这本书，文件在 /Users/xxx/Downloads/书名.epub」**

AI 会自动跑完整个流程。Windows 用户把路径换成 `C:\Users\xxx\Downloads\书名.epub` 就行。

---

## 适用平台

- macOS / Windows
- Hermes / MiMo Code / Codex 等支持文件操作和代码执行的 AI 助手

---

## 目录结构

```
book-distiller-universal/
├── SKILL.md                      # 主文件（加载这个就能用）
├── README.md                     # 本文件
├── LICENSE                       # MIT 开源协议
├── scripts/
│   └── clean_md.py               # 格式清理脚本
└── references/
    └── cross-platform-commands.md # 跨平台命令速查
```

---

## 许可证

MIT © 宝藏彬少
