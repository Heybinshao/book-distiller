#!/usr/bin/env python3
"""速览索引生成器：从原料包解析「命题+概念名」，为每章生成 index_NN.md。

用法:
    python3 gen_index.py <materials_index.json> <章名> <书单json> <输出index.md> [--part 半章说明]

- materials_index.json: extract_materials.py 产物
- 章名: 章节显示名（如 01｜个人品牌与自媒体）
- 书单json: [书名, ...]（A/B 拆半时传各半的名单）
- --part: 可选，A/B 半章的说明文字，写进索引头
"""
import os, re, sys, json


def parse_mat(path):
    txt = open(path, encoding='utf-8').read()
    lines = txt.splitlines()
    prop = ""
    for l in lines:
        if l.startswith("命题："):
            prop = l[3:].strip()
            break
    conc, in_conc = [], False
    for l in lines:
        if l.startswith("概念："):
            in_conc = True
            continue
        if in_conc:
            if l.startswith("- "):
                conc.append(l[2:].split("｜")[0].strip())
            elif l.strip():
                in_conc = False
    return prop, conc


def main():
    idx_json, ch_name, books_json, out_path = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    part = ""
    if '--part' in sys.argv:
        part = sys.argv[sys.argv.index('--part') + 1]
    index = json.load(open(idx_json, encoding='utf-8'))
    books = json.load(open(books_json, encoding='utf-8'))

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"# {ch_name} · 书单速览（{len(books)} 本）\n\n")
        if part:
            f.write(f"> {part}\n\n")
        f.write("> 每行：命题 + 概念名。写章节前先读本文件设计分篇结构；写作时逐本读 materials/ 下的原料包。\n\n")
        for b in books:
            if b not in index:
                print(f"⚠ 书单里的 {b} 不在原料包索引中，跳过")
                continue
            prop, conc = parse_mat(index[b]["material"])
            cnames = "；".join(conc[:8]) if conc else "（无概念节，读原料包）"
            f.write(f"- 《{b}》\n  命题：{prop}\n  概念：{cnames}\n")
    print(f"索引 → {out_path}（{os.path.getsize(out_path)//1024}KB）")


if __name__ == '__main__':
    main()
