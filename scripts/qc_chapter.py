#!/usr/bin/env python3
"""整合章节统一 QC：字符口径/书名覆盖/偷懒词/结构/收尾，五项一次跑完。

用法:
    python3 qc_chapter.py <章节文件> <书单json> [--floor N]

- 章节文件: 主题章节 .md
- 书单json: [书名, ...] 数组（从 chapter_plan.json 取该章 books 字段）
- --floor: 字符下限（缺省自动按书数定档：≤20 本 2 万 / 21-40 本 3.5 万 / ≥41 本 5 万）

退出码 0 = 全过；1 = 有问题（具体项见输出）。
"""
import os, re, sys, json


def book_hit(txt, b):
    """书名匹配：去作者后缀再 in 正文。'书名 - 作者' / '书名——作者' 均剥。"""
    core = re.split(r'\s*[-—]\s*[^《》]+$', b)[0].strip()
    return core in txt


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    floor = None
    if '--floor' in sys.argv:
        floor = int(sys.argv[sys.argv.index('--floor') + 1])
    path, books_json = args[0], args[1]
    txt = open(path, encoding='utf-8').read()
    books = json.load(open(books_json, encoding='utf-8'))
    n = len(books)
    if floor is None:
        floor = 20000 if n <= 20 else 35000 if n <= 40 else 50000

    missing = [b for b in books if not book_hit(txt, b)]
    lazy = [w for w in ["篇幅所限", "不一一列举", "此处略"] if w in txt]
    secs = re.findall(r'^## (.+)$', txt, re.M)
    dup = [h for h in secs if secs.count(h) > 1]
    has_end = '本章实践清单' in txt and '来源书目' in txt
    tail_ok = txt.rstrip().endswith(('》', ')', '）')) or '来源书目' in txt[-2000:]

    problems = []
    if len(txt) < floor:
        problems.append(f"字符 {len(txt)} < 下限 {floor}")
    if missing:
        problems.append(f"缺书 {len(missing)}: {missing[:5]}")
    if lazy:
        problems.append(f"偷懒词: {lazy}")
    if dup:
        problems.append(f"重复##标题: {dup}")
    if not has_end:
        problems.append("缺 实践清单/来源书目 结构")
    if not tail_ok:
        problems.append("尾部不是来源书目完结段")

    print(f"文件: {os.path.basename(path)}")
    print(f"字符 {len(txt)} (下限 {floor}) | 覆盖 {n - len(missing)}/{n} | ##节 {len(secs)}")
    print("判定:", "✓ 全过" if not problems else "✗ " + "；".join(problems))
    sys.exit(0 if not problems else 1)


if __name__ == '__main__':
    main()
