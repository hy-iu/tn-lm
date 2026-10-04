#!/usr/bin/env python3
"""Guardrail for translated chunks: compare a translated chunk with the
English original it came from.  Reports structural drift and residual English.

usage: check_chunk.py <zh_chunk.tex> <en_original.tex>
"""
import re
import sys
from pathlib import Path


def strip_comments(s):
    out = []
    for line in s.split("\n"):
        i, buf = 0, []
        while i < len(line):
            if line[i] == "\\":
                buf.append(line[i:i + 2])
                i += 2
                continue
            if line[i] == "%":
                break
            buf.append(line[i])
            i += 1
        out.append("".join(buf))
    return "\n".join(out)


def stats(s):
    body = strip_comments(s)
    envs = sorted(re.findall(r"\\(?:begin|end)\{([^{}]*)\}", body))
    labels = sorted(re.findall(r"\\(?:label|ref|eqref|cite|citet|citep|includegraphics)\s*(?:\[[^\]]*\])?\{([^{}]*)\}", body))
    return {
        "lines": len(s.split("\n")),
        "blank": len([l for l in s.split("\n") if not l.strip()]),
        "envs": envs,
        "keys": labels,
        "dollars": len(re.findall(r"(?<!\\)\$", body)),
        "braces": body.count("{") - body.count("}") - len(re.findall(r"\\\{", body)) + len(re.findall(r"\\\}", body)),
        "equations": len(re.findall(r"\\begin\{(?:equation|align|gather|multline)", body)),
        "chars": len(body),
    }


def residual_english(s):
    """Lines whose visible prose still contains 5+ consecutive English words."""
    out = []
    for n, line in enumerate(s.split("\n"), 1):
        body = strip_comments(line)
        # drop math, commands' arguments that are keys, and quoted keys
        txt = re.sub(r"\$[^$]*\$", " ", body)
        txt = re.sub(r"\\[a-zA-Z@]+\*?", " ", txt)
        txt = re.sub(r"[{}\\\[\]&~_^%$#]", " ", txt)
        for run in re.finditer(r"(?:[A-Za-z][A-Za-z'’\-]*\s+){5,}[A-Za-z][A-Za-z'’\-]*", txt):
            frag = run.group(0).strip()
            if len(frag.split()) >= 5:
                out.append((n, frag[:110]))
                break
    return out


if __name__ == "__main__":
    zh, en = (Path(a).read_text() for a in sys.argv[1:3])
    a, b = stats(zh), stats(en)
    bad = 0
    for k in ("envs", "keys", "dollars", "equations"):
        if a[k] != b[k]:
            bad = 1
            print(f"DIFF {k}: zh={len(a[k]) if isinstance(a[k], list) else a[k]} en={len(b[k]) if isinstance(b[k], list) else b[k]}")
            if k in ("envs", "keys"):
                from collections import Counter
                ca, cb = Counter(a[k]), Counter(b[k])
                only_en = {x: cb[x] - ca.get(x, 0) for x in cb if cb[x] > ca.get(x, 0)}
                only_zh = {x: ca[x] - cb.get(x, 0) for x in ca if ca[x] > cb.get(x, 0)}
                print("   仅英文:", dict(list(only_en.items())[:12]))
                print("   仅中文:", dict(list(only_zh.items())[:12]))
    if a["blank"] != b["blank"]:
        print(f"NOTE blank lines: zh={a['blank']} en={b['blank']} (段落结构变了)")
    if a["braces"] != b["braces"]:
        print(f"NOTE brace imbalance: zh={a['braces']} en={b['braces']}")
    res = residual_english(zh)
    if res:
        print(f"RESIDUAL ENGLISH ({len(res)} 行):")
        for n, frag in res:
            print(f"  L{n}: {frag}")
    print("STRUCT", "FAIL" if bad else "OK", "| zh/en chars:", a["chars"], b["chars"], "| lines:", a["lines"], b["lines"])
