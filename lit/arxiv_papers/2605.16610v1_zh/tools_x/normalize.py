#!/usr/bin/env python3
"""Apply central term normalisation across translated chunks.

usage: normalize.py [--apply]      (default: dry run, prints hit counts)
Only whole-string replacements inside already-translated Chinese text are
listed here, so they cannot touch math, commands or TikZ coordinates.
"""
import sys
from pathlib import Path

PAIRS = [
    # 图形记法/图示记法：见 tools_x/TERM_DECISIONS.md
    ("图形记法", "图示记法"),
    ("图形符号", "图示符号"),
    ("图形语言", "图形语言"),
    # contraction 统一为「收缩」：见上，唯一候选是巧合子串，故不做全局替换
    # bond dimension
    ("键维度", "键维数"),
    ("键的维度", "键维数"),
    # rank / order
    ("张量的次序", "张量的阶"),
    # core tensor
    ("芯张量", "核心张量"),
    # marginal distribution
    ("边际分布", "边缘分布"),
    ("边际化", "边缘化"),
    # matricization
    ("矩阵化表示", "矩阵化"),
    ("扁平化", "展开"),
    # normalization
    ("规范化", "归一化"),
    ("归一化约束", "归一化约束"),
    # MPS per GLOSSARY tensor-network group
    ("矩阵积态", "矩阵乘积态"),
    ("矩阵积算符", "矩阵乘积算符"),
    # truncation
    ("截断处理", "截断"),
    # partial trace：统一用物理界既有的「偏迹」（g3 译偏迹，g4 译部分迹）
    ("部分迹", "偏迹"),
    # 撤下两条机械替换：
    #   ("缩并","收缩") —— 唯一命中是 ch4_011:1「张量收缩并合并为」，"缩并"是"收缩+并"的巧合子串
    #   ("迹掉","求迹") —— ch2_004:11 需整句改写，交给人工
    # 图示类
    ("图形证明", "图示证明"),
    ("图形记法", "图示记法"),
    ("自边", "自环边"),
    ("悬空边", "悬空腿"),
    ("悬腿", "悬空腿"),
    # leg 统一为「腿」（g5 在 ch3 开头用了「边」）
    ("归并边", "归并腿"),
    ("行边", "行腿"),
    ("列边", "列腿"),
    ("自由边", "自由腿"),
    # 零散统一
    ("NP-难", "NP 难"),
    ("NP 困难", "NP 难"),
    ("自成一体", "自成体系"),
    ("秩揭示", "秩揭示"),
    ("图形演算", "图示演算"),
    # 正文模式无希腊字形（T1 + Type1 Times），δ 必须回到数学模式
    ("克罗内克 δ", "克罗内克 $\\delta$"),
    # complexity
    ("计算代价", "计算代价"),
    # expectation
    ("数学期望", "期望"),
    # identity matrix
    ("单位矩阵", "单位矩阵"),
]

# drop no-op pairs
PAIRS = [p for p in PAIRS if p[0] != p[1]]


def main():
    apply = "--apply" in sys.argv
    root = Path(__file__).resolve().parent.parent
    total = {}
    for p in sorted((root / "parts").glob("*.tex")):
        s = original = p.read_text()
        hits = []
        for a, b in PAIRS:
            n = s.count(a)
            if n:
                hits.append((a, b, n))
                s = s.replace(a, b)
        # undo accidental double-substitution artifacts
        s = s.replace("核心张量张量", "核心张量")
        for a, b, n in hits:
            total[a] = total.get(a, 0) + n
        if s != original:
            print(f"{'APPLIED' if apply else 'dry'} {p.name}: " + ", ".join(f"{a}->{b}×{n}" for a, b, n in hits))
            if apply:
                p.write_text(s)
    print("---- totals ----")
    for a, n in sorted(total.items(), key=lambda kv: -kv[1]):
        print(f"{n:5d}  {a}")


if __name__ == "__main__":
    main()
