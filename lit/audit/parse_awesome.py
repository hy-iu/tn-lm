#!/usr/bin/env python3
"""Harvest paper entries from the two awesome-list READMEs.

Both files mix two layouts:
  | [Title](url) | Decomposition | note | Venue | Year |
  | Author et al., ["Title"](url) | role | Venue | Year |
plus bullet items. Fenced code blocks (the BibTeX entry contains an arXiv URL that is
not a paper row) are dropped first.

Output: awesome_entries.csv with title, url, host, venue, year, source list, section.
No network access here -- resolving identifiers is the next step.
"""
import csv, os, re

SRC = "/Users/bjergsen/mnt/u26/research/tnlm/repos"
LISTS = {"awesome-tensor-methods-for-llms": "A", "awesome-tensorial-neural-networks": "B"}
OUT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit/audit"

LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")

rows = []
for folder, tag in LISTS.items():
    path = os.path.join(SRC, folder, "README.md")
    lines = open(path, encoding="utf-8").read().splitlines()
    section, fence = "", False
    for ln in lines:
        if ln.startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        h = re.match(r"^(#{2,4})\s+(.*)", ln)
        if h:
            section = h.group(2).strip()
            continue
        m = LINK.search(ln)
        if not m:
            continue
        if not (ln.lstrip().startswith("|") or ln.lstrip()[:2] in ("- [", "* [")):
            continue
        title, url = m.group(1), m.group(2)
        # list B wraps titles as  Author et al., ["Title"](url) -- the author prefix is
        # outside the link, so the captured text only needs its quote marks removed.
        t = title.strip().strip("\"'“”‘’").strip()
        if not t or t.lower() in ("here", "pdf", "code", "link", "arxiv", "paper"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        venue = year = ""
        for c in reversed(cells):
            if re.fullmatch(r"(19|20)\d\d", c):
                year = c
                break
        rest = [c for c in cells if c and c != year]
        if len(rest) >= 2:
            venue = rest[-1]
        host = re.sub(r"^www\.", "", re.sub(r"^https?://", "", url).split("/")[0])
        rows.append({"list": tag, "section": section, "title": re.sub(r"\s+", " ", t).strip(),
                     "url": url, "host": host, "venue": venue, "year": year})

seen, uniq = set(), []
for r in rows:
    k = (re.sub(r"[^a-z0-9]", "", r["title"].lower()), r["url"])
    if k in seen:
        continue
    seen.add(k)
    uniq.append(r)

with open(OUT + "/awesome_entries.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["list", "section", "title", "url", "host", "venue", "year"])
    w.writeheader()
    w.writerows(uniq)

from collections import Counter
print("raw link rows:", len(rows), "| unique (title,url):", len(uniq))
print("by list:", Counter(r["list"] for r in uniq).most_common())
print("by host:", Counter(r["host"] for r in uniq).most_common(10))
print("distinct titles:", len({re.sub(r'[^a-z0-9]', '', r['title'].lower()) for r in uniq}))
print("\nsample:")
for r in uniq[:6] + uniq[-4:]:
    print(f"  [{r['list']}] {r['year'] or '????'} {r['host']:22s} {r['title'][:58]}")
