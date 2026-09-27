#!/usr/bin/env python3
"""Repair two mechanical defects in the version layer.

1. Six rows carry a complete Springer DOI ('10.1007/JHEP12(2014)045') but a truncated
   'published' URL ('https://doi.org/10.1007/jhep12(2014') -- build_versions.py built
   that URL with a pattern that stops at the first parenthesis, so the link was dead.
   Rebuild the URL from the DOI column, which was always correct.
2. apply_resolve.py wrote the found arXiv id into bibliography.csv but left the matching
   paper_versions.csv row's arxiv_id empty. Sync them.
"""
import csv, re, sys, urllib.parse

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
OUT = LIT + "/audit"
sys.path.insert(0, OUT)
import build_versions as B  # noqa: E402

bib = list(csv.DictReader(open(LIT + "/bibliography.csv", newline="", encoding="utf-8")))
pv = list(csv.DictReader(open(OUT + "/paper_versions.csv", newline="", encoding="utf-8")))

n_url = n_id = 0
for p in pv:
    doi = (p.get("doi") or "").strip()
    pub = (p.get("published") or "").strip()
    if doi and "(" in doi and ")" in doi:
        want = "https://doi.org/" + urllib.parse.quote(doi, safe="()/:")
        if pub and pub != want:
            if "(" in pub and ")" not in pub:
                host = B.resolve_host(doi)
                print(f"   行 {p['row_no']:>4} 修复发表版链接\n      旧 {pub}\n      新 {want}")
                p["published"], p["published_host"] = want, (host or p.get("published_host") or "")
                n_url += 1
    b = bib[int(p["row_no"]) - 2]
    bid = (b.get("arxiv_id") or "").strip()
    if bid and not (p.get("arxiv_id") or "").strip():
        p["arxiv_id"] = bid
        n_id += 1

with open(OUT + "/paper_versions.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(pv[0].keys()))
    w.writeheader(); w.writerows(pv)
print(f"rebuilt {n_url} published URLs, synced {n_id} arxiv_id values")
still = [p for p in pv if "(" in (p["published"] or "") and ")" not in (p["published"] or "")]
print("仍被截断的链接:", len(still))
