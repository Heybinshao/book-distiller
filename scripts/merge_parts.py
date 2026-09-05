#!/usr/bin/env python3
"""A/B 半章合并器：把 parts/ 下的两个半章合并为全章。

用法:
    python3 merge_parts.py <A半章> <B半章> <输出全章> "<全章导语>"

- A 半章: 上半部分（含自己的 ## 来源书目，合并时剥掉）
- B 半章: 下半部分（含自己的 H1 标题行，合并时剥掉）
- 导语: 全章 > 引用，如 "本章融合 94 本书，回答：……"

合并后自动跑覆盖校验需要书单，本脚本只做结构与拼接；覆盖校验用 qc_chapter.py。
"""
import os, re, sys


def split_tail(txt):
    """剥掉末尾 ## 来源书目 段，返回正文。"""
    idx = txt.rindex('## 来源书目')
    return txt[:idx].rstrip() + "\n"


def main():
    if len(sys.argv) < 5:
        print(__doc__)
        sys.exit(1)
    path_a, path_b, out_path, intro = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    ta, tb = open(path_a, encoding='utf-8').read(), open(path_b, encoding='utf-8').read()

    body_a = split_tail(ta)
    lines_b = tb.splitlines()
    start_b = 1 if lines_b[0].startswith('# ') else 0  # 剥 B 的 H1

    h1 = os.path.basename(out_path).replace('.md', '')
    merged = f"# {h1}\n\n> {intro}\n\n---\n\n"
    merged += body_a + "\n\n---\n\n" + "\n".join(lines_b[start_b:])
    open(out_path, 'w', encoding='utf-8').write(merged)

    secs = re.findall(r'^## (.+)$', merged, re.M)
    dup = [h for h in secs if secs.count(h) > 1]
    print(f"合并 → {out_path}（{len(merged)} 字符）")
    print(f"来源书目段: {merged.count('## 来源书目')}（应为 1）| 实践清单: {merged.count('本章实践清单')}（应为 2，A/B 各一）")
    print("重复 ## 标题:", dup or "无")
    print("后续: 用 qc_chapter.py 对全章跑 A+B 并集书单覆盖校验")


if __name__ == '__main__':
    main()
