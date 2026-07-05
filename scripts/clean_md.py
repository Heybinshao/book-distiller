#!/usr/bin/env python3
"""
书籍榨干器 - Markdown 格式清理脚本

用法：
    python3 clean_md.py <输入文件.md>

功能：
    - 删除图片引用（![...](...)）
    - 删除 HTML/SVG 标签
    - 删除 CSS 类标记（{.xxx}）
    - 合并连续空行（超过3行缩成3行）
"""

import re
import sys


def clean_md(filepath: str) -> None:
    """清理 Markdown 文件中的格式垃圾。"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_size = len(content)

    # 删除图片引用
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
    # 删除 HTML/SVG 标签
    content = re.sub(r'<[^>]+>', '', content)
    # 删除 CSS 类标记
    content = re.sub(r'\{\.?[a-zA-Z][^}]*\}', '', content)
    # 合并连续空行（超过3行的缩成3行）
    content = re.sub(r'\n{4,}', '\n\n\n', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 清理完成：{filepath}")
    print(f"   原大小：{original_size} 字符 → 现大小：{len(content)} 字符")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python3 clean_md.py <输入文件.md>")
        sys.exit(1)

    clean_md(sys.argv[1])
