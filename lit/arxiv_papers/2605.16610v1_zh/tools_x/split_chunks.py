#!/usr/bin/env python3
"""Split a .tex file into chunks at structurally safe boundaries.

Comments are stripped before analysis. A cut is allowed only where every
environment is closed, braces balance, and inline-math parity is even.
Concatenating the chunks must reproduce the input byte-for-byte (asserted).
"""
import re
import sys
from pathlib import Path

TARGET = 110
MAXL = 280
MINL = 45

# A cut inside one of these would split material that must stay together
# (diagram code, math, tables, floats).  Cuts between two \item lines of a
# list, or inside a theorem/proof body, are fine: reassembly is byte-exact.
HARD = {
    "tikzpicture", "tabular", "tabularx", "longtable", "tabu", "niceTabular",
    "align", "align*", "alignat", "alignat*", "eqnalign", "gather", "gather*",
    "equation", "equation*", "multline", "multline*", "flalign", "flalign*",
    "split", "cases", "array", "matrix", "pmatrix", "bmatrix", "Bmatrix",
    "vmatrix", "Vmatrix", "smallmatrix", "minipage", "figure", "figure*",
    "table", "table*", "tabular*", "algorithm", "algorithmic", "lstlisting",
    "verbatim", "filecontents", "document", "subfigure", "subfloat",
}

TOKEN = re.compile(r"\\(?:begin|end)\{([^{}]*)\}|\{|\}")


def strip_comments(line):
    out, i = [], 0
    while i < len(line):
        c = line[i]
        if c == "\\":
            out.append(line[i:i + 2])
            i += 2
            continue
        if c == "%":
            break
        out.append(c)
        i += 1
    return "".join(out)


def analyse(raw_lines):
    stack, balance, par = [], 0, 0
    states = []
    for raw in raw_lines:
        states.append((tuple(stack), balance, par))
        ln = strip_comments(raw).replace(r"\{", "\x01").replace(r"\}", "\x02").replace(r"\$", "\x03")
        for m in TOKEN.finditer(ln):
            tok = m.group(0)
            if tok.startswith("\\begin"):
                stack.append(m.group(1))
            elif tok.startswith("\\end"):
                if m.group(1) in stack:
                    while stack[-1] != m.group(1):
                        stack.pop()
                    stack.pop()
            elif tok == "{":
                balance += 1
            else:
                balance -= 1
        par = (par + len(re.findall(r"(?<!\\)\$", ln))) % 2
    return states


def safe_cut(states, raw_lines, idx):
    if idx >= len(raw_lines):
        return True
    stack, balance, par = states[idx]
    if balance or par:
        return False
    if any(e in HARD for e in stack):
        return False
    prev = strip_comments(raw_lines[idx - 1].rstrip()) if idx else ""
    if prev.endswith("\\"):
        return False
    if re.search(r"(\\item|\\and|\\\\)$", prev):
        return False
    return True


def split(path, outdir, prefix):
    content = Path(path).read_text()
    body = content if content.endswith("\n") else content + "\n"
    lines = body[:-1].split("\n")
    states = analyse(lines)
    safe = {i for i in range(len(lines)) if safe_cut(states, lines, i)}
    chunks, start = [], 0
    while start + TARGET < len(lines):
        cut = None
        for k in range(start + TARGET, len(lines)):
            if k not in safe:
                continue
            if not lines[k - 1].strip() or k - start >= MAXL:
                cut = k
                break
        if cut is None:
            break
        chunks.append((start, cut))
        start = cut
    chunks.append((start, len(lines)))
    if len(chunks) > 1 and chunks[-1][1] - chunks[-1][0] < MINL:
        a, _ = chunks[-2]
        chunks[-2] = (a, chunks[-1][1])
        chunks.pop()
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    man = []
    for n, (a, b) in enumerate(chunks):
        p = out / f"{prefix}_{n:03d}.tex"
        p.write_text("\n".join(lines[a:b]) + "\n")
        man.append((str(p), a + 1, b, b - a))
    joined = "".join((out / f"{prefix}_{n:03d}.tex").read_text() for n in range(len(chunks)))
    assert joined == body, f"reassembly mismatch for {path}"
    return man


if __name__ == "__main__":
    src, outdir, prefix = sys.argv[1:4]
    for p, a, b, ln in split(src, outdir, prefix):
        print(f"{p}\tlines {a}-{b}\t({ln})")
