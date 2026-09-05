#!/usr/bin/env python3
"""原料包抽取器：从蒸馏拆解抽取五件套（命题/概念/金句/反模式/总结）。

用法:
    python3 extract_materials.py <蒸馏拆解目录> <MOC文件> <输出目录>

- 蒸馏拆解目录: 含 {书名}-完整拆解.md 的目录
- MOC文件: 蒸馏拆解MOC（## 分类名（N）+ - [[书名-完整拆解]] 格式）；
  无 MOC 时传 "none"，脚本改为处理目录下全部拆解文件
- 输出目录: 原料包落盘位置（{书名}.mat.md）

产出: 原料包 + 标准输出（统计+校验结果）。原料包大小中位应约为原拆解的 1/4。
"""
import os, re, sys, json


def trim(s, n):
    s = re.sub(r'\s+', ' ', s or '').strip()
    return s[:n] + ('…' if len(s) > n else '')


def extract_material(title, txt):
    lines = txt.splitlines()
    out = [f"# 《{title}》"]
    # 1) 命题：标题后第一个 > 引用
    for l in lines[:12]:
        if l.startswith('>'):
            t = trim(l.lstrip('> '), 160)
            if t:
                out.append(f"命题：{t}")
            break
    # 定位 ## 节
    sec_pos = {}
    for i, l in enumerate(lines):
        m = re.match(r'^##\s*(.+)', l)
        if m:
            sec_pos[m.group(1).strip()] = i
    # 2) 概念：### 节 + 定义/机制/案例/启示 粗体行
    concepts, cur = [], None
    for l in lines:
        if l.startswith('### '):
            if cur:
                concepts.append(cur)
            cur = {'name': l[4:].strip(), 'def': '', 'mech': '', 'case': '', 'ins': ''}
        elif cur is not None:
            if l.startswith('## '):
                concepts.append(cur)
                cur = None
                continue
            m = re.match(r'\*\*(定义|机制|案例|启示)\*\*[：:]\s*(.*)', l.strip())
            if m:
                k, v = m.group(1), trim(m.group(2), 110)
                cur[{'定义': 'def', '机制': 'mech', '案例': 'case', '启示': 'ins'}[k]] = v
            elif re.match(r'\*\*(定义|机制|案例|启示)\*\*', l.strip()) and not cur['def']:
                cur['def'] = trim(l.strip().strip('*：: '), 110)
    if cur:
        concepts.append(cur)
    if concepts:
        out.append("概念：")
        for c in concepts[:40]:
            parts = [c['name'][:60]]
            for kk in ('def', 'mech', 'case', 'ins'):
                if c[kk]:
                    parts.append(c[kk])
            out.append("- " + "｜".join(parts))
    # 3) 金句
    quotes = []
    for h, i in sec_pos.items():
        if '金句' in h:
            for l in lines[i + 1:]:
                if l.startswith('## '):
                    break
                if l.strip().startswith('>'):
                    q = trim(l.strip().lstrip('> '), 120)
                    if q:
                        quotes.append(q)
    if quotes:
        out.append("金句：")
        out += [f"> {q}" for q in quotes[:12]]
    # 4) 反模式
    for h, i in sec_pos.items():
        if '反模式' in h:
            rows = [trim(l, 100) for l in lines[i + 1:i + 30]
                    if l.strip().startswith('|') and '---' not in l and '反模式' not in l.split('|')[1]]
            if rows:
                out.append("反模式：")
                out += [f"- {r}" for r in rows[:10]]
            break
    # 5) 一句话总结
    for h, i in sec_pos.items():
        if '一句话总结' in h:
            for l in lines[i + 1:]:
                if l.strip() and not l.startswith('#'):
                    out.append("总结：" + trim(l, 160))
                    break
            break
    # 兜底：无概念时抽 ## 节标题+首段
    if not concepts:
        heads = []
        for i, l in enumerate(lines):
            if l.startswith('## ') and not any(k in l for k in ('金句', '反模式', '行动', '批判')):
                body = ""
                for l2 in lines[i + 1:]:
                    if l2.startswith('#'):
                        break
                    if l2.strip() and not l2.startswith('>'):
                        body = trim(l2, 140)
                        break
                heads.append(f"- {l[3:].strip()[:50]}：{body}")
        if heads:
            out.append("脉络：")
            out += heads[:25]
    return "\n".join(out)


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    dist_dir, moc_arg, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out_dir, exist_ok=True)

    if moc_arg.lower() == 'none':
        themes = {"全部": [f[:-len('-完整拆解.md')] for f in os.listdir(dist_dir)
                          if f.endswith('-完整拆解.md')]}
    else:
        moc = open(moc_arg, encoding='utf-8').read()
        themes, current = {}, None
        for line in moc.splitlines():
            m = re.match(r'^## (.+?)（(\d+)）', line.strip())
            if m:
                current = m.group(1).strip()
                themes[current] = []
                continue
            if current:
                m2 = re.match(r'^- \[\[(.+?)-完整拆解\]\]', line.strip())
                if m2:
                    themes[current].append(m2.group(1))

    disk = {f[:-len('-完整拆解.md')]: f for f in os.listdir(dist_dir)
            if f.endswith('-完整拆解.md')}
    moc_books = {b for bl in themes.values() for b in bl}
    ghost = sorted(moc_books - set(disk))
    orphan = sorted(set(disk) - moc_books)
    if ghost:
        print(f"⚠ MOC 有但磁盘没有 {len(ghost)} 本: {ghost[:5]}")
    if orphan:
        print(f"ℹ 磁盘有但 MOC 没有 {len(orphan)} 本: {orphan[:5]}")

    index = {}
    for theme, books in themes.items():
        for b in books:
            if b not in disk:
                continue
            txt = open(os.path.join(dist_dir, disk[b]), encoding='utf-8', errors='ignore').read()
            mat = extract_material(b, txt)
            safe = re.sub(r'[/\\:*?"<>|｜]', '·', b)[:80]
            p = os.path.join(out_dir, safe + ".mat.md")
            with open(p, 'w', encoding='utf-8') as f:
                f.write(mat)
            index[b] = {"theme": theme, "material": p, "size": len(mat)}

    sizes = sorted(v["size"] for v in index.values())
    print(f"原料包 {len(index)} 份 → {out_dir}")
    if sizes:
        print(f"大小: 中位 {sizes[len(sizes)//2]}B 最小 {sizes[0]}B 最大 {sizes[-1]}B 总 {sum(sizes)//1024}KB")
    json.dump(index, open(os.path.join(os.path.dirname(out_dir), 'materials_index.json'), 'w'),
              ensure_ascii=False, indent=1)
    print("materials_index.json 已写")


if __name__ == '__main__':
    main()
