#!/usr/bin/env python3
"""书籍榨干器：markdown 格式清理脚本
用法: python3 clean_md.py <input.md>
"""
import re, sys

def clean_md(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)                          # 图片引用
    content = re.sub(r'<svg[^>]*>.*?</svg>', '', content, flags=re.DOTALL)     # SVG
    content = re.sub(r'<[^>]+>', '', content)                                  # HTML 标签
    content = re.sub(r'\{\.?[a-zA-Z][^}]*\}', '', content)                     # CSS 类标记
    content = re.sub(r'\n{4,}', '\n\n\n', content)                             # 合并连续空行
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 清理完成：{filepath}")

if __name__ == '__main__':
    clean_md(sys.argv[1])
