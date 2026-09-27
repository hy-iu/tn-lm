#!/usr/bin/env python3
"""Restore the doi column in paper_versions.csv.

The last merge read the DOI via the key 'journal_doi', but new_versions.csv had been
rewritten with that column named 'voR_doi', so 55 freshly merged rows got an empty doi.
Rename the column back and copy the values across.
"""
import csv

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
OUT = LIT + "/audit"

nv = list(csv.DictReader(open(OUT + "/new_versions.csv", newline="", encoding="utf-8")))
NV = [c for c in nv[0]] + (["journal_doi"] if "journal_doi" not in nv[0] else [])
for r in nv:
    if "voR_doi" in r:
        r["journal_doi"] = r.pop("voR_doi")
    NV = list(dict.fromkeys(NV + list(r)))
NV = [c for c in ["arxiv_id", "citations", "journal_doi", "jref", "venue", "published",
                  "published_host", "oa_pdf", "github", "github_from", "homepage",
                  "openalex_hit"] if c in NV]

bib = list(csv.DictReader(open(LIT + "/bibliography.csv", newline="", encoding="utf-8")))
pv = list(csv.DictReader(open(OUT + "/paper_versions.csv", newline="", encoding="utf-8")))
by_aid = {r["arxiv_id"]: r for r in nv if (r.get("arxiv_id") or "").strip()}
fixed = 0
for p in pv:
    if (p.get("doi") or "").strip():
        continue
    b = bib[int(p["row_no"]) - 2]
    n = by_aid.get((b.get("arxiv_id") or "").strip())
    if n and (n.get("journal_doi") or "").strip():
        p["doi"] = n["journal_doi"]
        fixed += 1
print(f"paper_versions: restored {fixed} doi values (from new_versions.journal_doi)")

with open(OUT + "/new_versions.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=NV, extrasaction="ignore")
    w.writeheader(); w.writerows(nv)
with open(OUT + "/paper_versions.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(pv[0]))
    w.writeheader(); w.writerows(pv)
print("new_versions.csv header:", ",".join(NV))
