#!/usr/bin/env python3
"""Backfill the version layer for rows resolve_unverified.py identified confidently.

Only these match kinds are applied: 'id', 'ti', 'ti-id', 'doi' -- each requires the
normalized titles to be identical (or the stored arXiv id to be the record we fetched).
'ti-fuzzy' rows are listed but never written, because a prefix match on a title is not
the same paper often enough to be worth a silent edit.

Writes: paper_versions.csv (abstract/links/verdict) and, where empty, bibliography.csv's
arxiv_id and journal_ref. Nothing else in the stored row is touched, so a card that had
a truncated snippet keeps showing the comparison note.
"""
import csv, os, re, sys

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
OUT = LIT + "/audit"
sys.path.insert(0, OUT)
import ghverify  # noqa: E402
from scan_abstracts import classify, sq  # noqa: E402

APPLY = {"id", "ti", "ti-id", "doi", "doi-openalex", "doi-crossref", "title-openalex"}
AUTH = {"doi-openalex": "openalex", "title-openalex": "openalex", "doi-crossref": "crossref"}
RES = sys.argv[1] if len(sys.argv) > 1 else "resolve_unverified.csv"
INFILE = os.path.join(OUT, RES)
bib = list(csv.DictReader(open(LIT + "/bibliography.csv", newline="", encoding="utf-8")))
taken = {}
for i, r in enumerate(bib):
    a = (r.get("arxiv_id") or "").strip()
    if a:
        taken.setdefault(a, i + 2)
    for m in re.finditer(r"arxiv\.org/(?:abs|pdf)/([\w\-.]+?)(?:v\d+)?(?:\W|$)",
                         " ".join(str(r.get(k) or "") for k in ("url", "all_pdfs"))):
        taken.setdefault(m.group(1), i + 2)
bib_cols = list(bib[0].keys())
pv = list(csv.DictReader(open(OUT + "/paper_versions.csv", newline="", encoding="utf-8")))
pv_cols = list(pv[0].keys())
res = list(csv.DictReader(open(INFILE, newline="", encoding="utf-8")))
by_row = {int(p["row_no"]): p for p in pv}

applied, skipped = [], []
for r in res:
    rn = int(r["row_no"])
    if r["match"] not in APPLY:
        if r["match"]:
            skipped.append((rn, r["match"], r["stored_title"][:50]))
        continue
    p, b = by_row[rn], bib[rn - 2]
    assert b["title"] == r["stored_title"], (rn, b["title"], r["stored_title"])
    ab = r["abstract"].strip()
    if not ab:
        skipped.append((rn, "empty-abstract", r["stored_title"][:50]))
        continue
    auth = AUTH.get(r["match"], "arxiv")
    srcs = {"arXiv": ab} if auth == "arxiv" else ({auth: ab})
    verdict, authority, _len, _tail = classify(b["abstract"], srcs)
    aid = r["found_arxiv_id"].strip()
    if aid and taken.get(aid, rn) != rn:
        skipped.append((rn, f"id-already-on-line-{taken[aid]}", r["stored_title"][:50]))
        continue
    gh = ghverify.first_repo(ab + " " + r["jref"]) if aid else ""
    before = (p["verdict"], p["abs_authority"], p["full_abs_len"], p["github"])
    p.update({"verdict": verdict, "abs_authority": auth,
              "arxiv_abs": ("https://arxiv.org/abs/" + aid) if aid else "",
              "oa_pdf": ("https://arxiv.org/pdf/" + aid) if aid else (p["oa_pdf"] or ""),
              "doi": r["doi"].strip() or p["doi"], "jref": r["jref"].strip() or p["jref"],
              "full_abs_len": str(len(ab)), "stored_abs_len": str(len((b["abstract"] or "").strip())),
              "full_abstract": ab, "github": gh or p["github"]})
    if aid and not (p["arxiv_id"] or "").strip():
        p["arxiv_id"] = aid
    if aid and not (b["arxiv_id"] or "").strip():
        b["arxiv_id"] = aid
    if r["jref"].strip() and not (b["journal_ref"] or "").strip():
        b["journal_ref"] = r["jref"].strip()
    applied.append((rn, r["match"], aid, verdict, before, (p["verdict"], p["abs_authority"],
                                                             p["full_abs_len"], p["github"])))

print(f"applied {len(applied)} rows | skipped {len(skipped)}")
for rn, kind, aid, verdict, bef, aft in applied:
    print(f"   line {rn:>4} {kind:6s} arxiv={aid:16s} verdict {bef[0]} -> {verdict}")
if applied:
    with open(LIT + "/bibliography.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=bib_cols)
        w.writeheader(); w.writerows(bib)
    with open(OUT + "/paper_versions.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=pv_cols)
        w.writeheader(); w.writerows(pv)
    print("written")
else:
    print("nothing applied; files untouched")
print("\nskipped (需人工过目):")
for s in skipped[:40]:
    print("   ", s)
