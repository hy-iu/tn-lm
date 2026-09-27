#!/usr/bin/env python3
"""Parse the toolbox/software tables out of the two awesome-* READMEs.

Outputs lit/audit/toolbox_src.json: one record per (repo, section, table row).
Everything downstream (link verification, page generation) reads this file,
so a table edit in the source README is the only thing that needs re-running.
"""
import json
import os
import re

REPOS = {
    "llms": "/Users/bjergsen/mnt/u26/research/tnlm/repos/awesome-tensor-methods-for-llms/README.md",
    "tnn": "/Users/bjergsen/mnt/u26/research/tnlm/repos/awesome-tensorial-neural-networks/README.md",
}
# 本地克隆没有 .git，README 里也不都写自己的仓库地址，所以显式记下：
#   tnn  -> 另一份清单的 Related Projects 里点名了它，且本站论文库也收了该仓库
#   llms -> 用 GitHub 仓库名搜索唯一命中（total_count=1），与本站论文库记录一致
# 两个地址都实测 HTTP 200。绝不能把本地路径当成链接写进页面。
REPO_URL = {
    "llms": "https://github.com/ma-tt-a/awesome-tensor-methods-for-llms",
    "tnn": "https://github.com/tnbar/awesome-tensorial-neural-networks",
}
# only these H2/H3 sections are about software; the rest are paper bibliographies
WANT_H2 = {"Software", "Toolboxes"}
OUT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit/audit/toolbox_src.json"
META = "/Users/bjergsen/Documents/GitHub/tn-lm/lit/audit/toolbox_meta.json"

LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
ARXIV = re.compile(r"arxiv\.org/abs/(\d{4}\.\d{4,5})")
BIB = re.compile(r"@(?:misc|article)\s*\{(?P<body>.*?)\n\}", re.S)
GLOSS = re.compile(r"^-\s+\*\*(?P<term>[^*]+)\*\*\s*[—-]+\s*(?P<text>.+)$")


def split_row(line):
    """Markdown table row -> list of cell texts (handles escaped pipes poorly, but these tables have none)."""
    return [c.strip() for c in line.strip().strip("|").split("|")]


ACCENT = {"a": "á", "e": "é", "i": "í", "o": "ó", "u": "ú", "n": "ñ", "c": "ç"}


def clean(s):
    """Drop the $...$ math delimiters and BibTeX accent escapes the READMEs use."""
    s = re.sub(r"\$([^$]*)\$", r"\1", s)
    s = re.sub(r"\\['\"`^~=](\w)", lambda m: ACCENT.get(m.group(1), m.group(1)), s)
    return re.sub(r"[{}]", "", s).strip()


def survey_meta(text):
    """Pull the arXiv id / title / authors out of the README's citation block."""
    out = {"arxiv": "", "title": "", "authors": "", "key": ""}
    m = ARXIV.search(text)
    if m:
        out["arxiv"] = m.group(1)
    m = BIB.search(text)
    if m:
        body = m.group("body")
        for field in ("title", "author"):
            fm = re.search(field + r"\s*=\s*[{\"](.+?)[}\"]\s*,?\s*\n", body, re.S)
            if fm:
                out[field + ("s" if field == "author" else "")] = \
                    re.sub(r"\s+", " ", clean(fm.group(1))).replace("\\'", "'")
        km = re.search(r"@\w+\s*\{([^,]+),", text)
        if km:
            out["key"] = km.group(1).strip()
    return out


def main():
    rows = []
    meta = {}
    for tag, path in REPOS.items():
        with open(path, encoding="utf-8") as f:
            text = f.read()
        lines = text.split("\n")
        meta[tag] = dict(survey_meta(text), path=path, repo=REPO_URL[tag],
                         local=os.path.dirname(path))
        h2 = h3 = ""
        header = None
        for ln in lines:
            if ln.startswith("## ") and not ln.startswith("### "):
                h2, h3, header = ln[3:].strip(), "", None
                if h2 == "Tensor Formats":
                    meta[tag]["glossary"] = []
            elif ln.startswith("### "):
                h3, header = ln[4:].strip(), None
            elif h2 == "Tensor Formats":
                g = GLOSS.match(ln)
                if g:
                    meta[tag].setdefault("glossary", []).append(
                        {"term": clean(g.group("term")), "text": clean(g.group("text"))})
            elif ln.startswith("|") and h2 in WANT_H2:
                cells = split_row(ln)
                if set("".join(cells)) <= set("-: "):   # separator row
                    continue
                if header is None:
                    header = cells
                    continue
                rec = dict(zip(header, cells))
                links = LINK.findall(ln)
                rows.append({
                    "src": tag, "h2": h2, "h3": h3, "cols": header,
                    "cells": rec, "links": [{"text": t, "url": u} for t, u in links],
                    "raw": ln,
                })
            elif ln.startswith("- ") and h2 in WANT_H2 and h3 == "Case Studies":
                rows.append({"src": tag, "h2": h2, "h3": h3, "cols": [],
                             "cells": {"item": ln[2:].strip()},
                             "links": [{"text": t, "url": u} for t, u in LINK.findall(ln)],
                             "raw": ln})
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    with open(META, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print("rows:", len(rows))
    for tag in REPOS:
        sub = [r for r in rows if r["src"] == tag]
        for key in sorted({(r["h2"], r["h3"]) for r in sub}):
            n = sum(1 for r in sub if (r["h2"], r["h3"]) == key)
            print("  %-5s %-12s %-42s %d" % (tag, key[0], key[1], n))
        print("  %s survey: %s | %s | %s" % (
            tag, meta[tag]["arxiv"], meta[tag]["key"], meta[tag]["title"][:60]))
        print("  %s authors: %s" % (tag, meta[tag]["authors"][:100]))
        print("  %s glossary terms: %d" % (tag, len(meta[tag].get("glossary", []))))
    urls = sorted({l["url"] for r in rows for l in r["links"]})
    print("distinct urls:", len(urls))


if __name__ == "__main__":
    main()
