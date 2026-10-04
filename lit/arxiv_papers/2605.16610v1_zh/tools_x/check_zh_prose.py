#!/usr/bin/env python3
r"""check_untranslated.py 的 TikZ 感知版（本篇 412 个 tikzpicture，通用版会大量误报）。

用法: check_zh_prose.py <file.tex>

做法：先把 \begin{tikzpicture}...\end{tikzpicture} 整块、以及 \tikzset/\draw/\node/
\path/\fill/\coordinate/\def 等图件命令行抹成空白，再套用与共用工具相同的散文判定
（无汉字 + 6 个连续英文词，或 60 个以上拉丁字母）。
"""
import re
import sys

CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
LATIN_WORD = re.compile(r"[A-Za-z]{2,}")
MATH_HINT = re.compile(r"[\\\^_=<>+\-*/]{2,}|\$")
TIKZ_CMD = re.compile(r"\\(?:tikzset|draw|node|path|fill|filldraw|coordinate|path|def|edef|renewcommand|newcommand|usepackage|input|bibliography|bibliographystyle|label|ref|eqref|cite[a-zA-Z]*|item|hspace|vspace|scalebox|centering)[\s\S]*?(?:;|$)", re.M)


def strip_comments(text):
    out = []
    for line in text.split("\n"):
        i = 0
        while i < len(line):
            if line[i] == "\\":
                i += 2
                continue
            if line[i] == "%":
                line = line[:i]
                break
            i += 1
        out.append(line)
    return "\n".join(out)


def main():
    src = strip_comments(open(sys.argv[1], encoding="utf-8").read())
    src = re.sub(r"\\begin\{tikzpicture\}[\s\S]*?\\end\{tikzpicture\}", lambda m: " " * len(m.group(0)), src)
    src = re.sub(r"\$\S[^$]*\$", lambda m: " " * len(m.group(0)), src)  # 行内数学整段抹掉（跨行不处理）
    lines = src.split("\n")
    hits = []
    for n, line in enumerate(lines, 1):
        if CJK.search(line):
            continue
        body = TIKZ_CMD.sub(" ", line)
        body = re.sub(r"\\[a-zA-Z@]+\*?", " ", body)
        body = re.sub(r"[{}\[\]\\~&]", " ", body)
        words = LATIN_WORD.findall(body)
        letters = sum(len(w) for w in words)
        run = re.findall(r"[A-Za-z]{2,}(?:\s+[A-Za-z']{1,}){5,}", body)
        if (run and letters >= 40) or (letters >= 60 and not MATH_HINT.search(body)):
            hits.append((n, line.strip()[:150]))
    if not hits:
        print("漏译检查(TikZ 感知): PASS — 无「不含汉字的英文散文行」")
        return 0
    print("漏译检查(TikZ 感知): 发现 %d 处待判定：" % len(hits))
    for n, s in hits:
        print(f"  L{n}: {s}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
