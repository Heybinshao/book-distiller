#!/usr/bin/env python3
"""
书籍榨干器 — 输出质量检查

检查拆解文档是否完整、清晰、无遗漏。

用法:
    python3 quality_check.py <拆解文档路径>

示例:
    python3 quality_check.py ~/Downloads/书籍拆解/02-蒸馏拆解/原子习惯-完整拆解.md
"""

import sys
import re
from pathlib import Path


def check_core_proposition(content: str) -> tuple[bool, str]:
    """检查是否有一句话核心命题"""
    # 查找 > 开头的引言行（核心命题通常放在这里）
    blockquotes = re.findall(r'^>\s+(.+?)$', content, re.MULTILINE)
    if blockquotes:
        return True, f"核心命题: {blockquotes[0][:60]}..."
    return False, "❌ 未找到核心命题（> 开头的引言）"


def check_concepts(content: str) -> tuple[bool, str]:
    """检查是否有关键概念"""
    concepts = len(re.findall(r'^###\s+', content, re.MULTILINE))
    if concepts >= 3:
        return True, f"关键概念: {concepts}个 ✅"
    elif concepts >= 1:
        return True, f"关键概念: {concepts}个 ⚠️ (建议≥3个)"
    else:
        return False, "❌ 未找到关键概念（### 标题）"


def check_quotes(content: str) -> tuple[bool, str]:
    """检查是否包含金句"""
    quotes = len(re.findall(r'^>\s+"', content, re.MULTILINE))
    if quotes >= 3:
        return True, f"金句: {quotes}条 ✅"
    elif quotes >= 1:
        return True, f"金句: {quotes}条 ⚠️ (建议≥3条)"
    else:
        return False, "❌ 未找到金句（> \" 开头）"


def check_chapters(content: str) -> tuple[bool, str]:
    """检查章节覆盖（## 主题的数量）"""
    chapters = len(re.findall(r'^##\s+', content, re.MULTILINE))
    if chapters >= 5:
        return True, f"主题章节: {chapters}个 ✅"
    elif chapters >= 3:
        return True, f"主题章节: {chapters}个 ⚠️ (建议≥5个)"
    else:
        return False, f"❌ 主题章节太少: {chapters}个 (建议≥5个)"


def check_file_size(filepath: Path) -> tuple[bool, str]:
    """检查文件大小"""
    size = filepath.stat().st_size
    size_kb = size / 1024
    if size_kb >= 15:
        return True, f"文件大小: {size_kb:.0f}KB ✅ (目标≥15KB)"
    else:
        return False, f"❌ 文件太小: {size_kb:.0f}KB (目标≥15KB)"


def check_action_items(content: str) -> tuple[bool, str]:
    """检查是否有行动清单"""
    has_action = bool(re.search(r'行动清单|Action|可以做什么|下一步', content, re.IGNORECASE))
    return has_action, "行动清单 ✅" if has_action else "❌ 未找到行动清单"


def check_anti_patterns(content: str) -> tuple[bool, str]:
    """检查是否有反模式清单"""
    has_anti = bool(re.search(r'反模式清单', content))
    return has_anti, "反模式清单 ✅" if has_anti else "❌ 未找到反模式清单"


def check_critical_review(content: str) -> tuple[bool, str]:
    """检查是否有批判性审视"""
    has_review = bool(re.search(r'批判性审视', content))
    return has_review, "批判性审视 ✅" if has_review else "❌ 未找到批判性审视"


def check_summary(content: str) -> tuple[bool, str]:
    """检查是否有一句话总结"""
    has_summary = bool(re.search(r'一句话总结', content))
    return has_summary, "一句话总结 ✅" if has_summary else "❌ 未找到一句话总结"


def main():
    if len(sys.argv) < 2:
        print("用法: python3 quality_check.py <拆解文档路径>")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"❌ 文件不存在: {filepath}")
        sys.exit(1)

    content = filepath.read_text(encoding='utf-8')

    checks = [
        ("核心命题", check_core_proposition),
        ("概念数量", check_concepts),
        ("金句数量", check_quotes),
        ("章节覆盖", check_chapters),
        ("文件大小", lambda c: check_file_size(filepath)),
        ("行动清单", check_action_items),
        ("反模式清单", check_anti_patterns),
        ("批判性审视", check_critical_review),
        ("一句话总结", check_summary),
    ]

    print(f"质量检查: {filepath.name}")
    print("=" * 50)

    passed_count = 0
    total = len(checks)

    for name, check_fn in checks:
        passed, detail = check_fn(content)
        status = "✅" if passed else "❌"
        print(f"  {name:<10} {status}  {detail}")
        if passed:
            passed_count += 1

    print("=" * 50)
    print(f"结果: {passed_count}/{total} 通过")

    if passed_count == total:
        print("🎉 全部达标")
    elif passed_count >= total - 1:
        print("⚠️ 基本达标，建议补全不通过项")
    else:
        print("❌ 多项不达标，建议补充内容")

    sys.exit(0 if passed_count == total else 1)


if __name__ == '__main__':
    main()
