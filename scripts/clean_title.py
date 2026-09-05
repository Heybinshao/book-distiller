#!/usr/bin/env python3
"""干净书名提取器——全流程命名基准的单一来源。

用法:
    python3 clean_title.py "文件名（含扩展名也可）"

规则顺序（不可调换）：去括号 > 去=英文标题 > 去：副标题 > 去--作者 > 去[出版社] > 合并空格。
⚠ 必须先删括号再删作者——否则 `(Z-Library)` 里的连字符会被当作者分隔符误删（实测坑）。
保留系列号：重来2、好好说话2、财务自由之路Ⅲ 等数字/罗马数字不删。
"""
import re, sys


def clean_book_title(filename):
    name = filename
    name = re.sub(r'\.(epub|pdf|mobi|azw3|md|txt|docx)$', '', name, flags=re.IGNORECASE)  # 剥扩展名（调用侧 ${file%.ext} 漏剥时的防呆）
    name = re.sub(r'（[^）]*）', '', name)                  # 去 （副标题）全角括号
    name = re.sub(r'\([^)]*\)', '', name)                 # 去 (副标题/来源) 半角括号
    name = re.sub(r'\s*=\s*[^（(]*$', '', name)           # 去 =英文标题
    name = re.sub(r'[：:].*$', '', name)                  # 去 ：后描述（副标题）
    name = re.sub(r'\s*--?\s*\S+$', '', name)             # 去 --作者 / - 作者
    name = re.sub(r'\s*[\[\[].*$', '', name)              # 去 [出版社]
    name = re.sub(r'\s{2,}', ' ', name)                   # 合并多余空格
    return name.strip()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    print(clean_book_title(sys.argv[1]))
