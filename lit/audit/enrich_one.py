#!/usr/bin/env python3
"""Give bibliography line 78 its arXiv identity.

'Expressive power of tensor-network factorizations for probabilistic modeling' was
collected without an arxiv_id, so the audit layer could not locate an authority for it
and the page reports it as unverified. It is arXiv:1907.03741 -- the same paper, but the
corpus holds an earlier revision's abstract (1449 chars) while arXiv now serves a
revised one (1679 chars, with a longer title). Only the identifier and the version
layer are filled in here; the stored title and abstract are left untouched so the
mismatch stays visible as a note on the card.
"""
import csv, re, sys

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
OUT = LIT + "/audit"
AID = "1907.03741"
sys.path.insert(0, OUT)
from scan_abstracts import sq  # noqa: E402

bib = list(csv.DictReader(open(LIT + "/bibliography.csv", newline="", encoding="utf-8")))
cols = list(bib[0].keys())
pv = list(csv.DictReader(open(OUT + "/paper_versions.csv", newline="", encoding="utf-8")))
pv_cols = list(pv[0].keys())
meta = {r["arxiv_id"]: r for r in csv.DictReader(open(OUT + "/cand_meta.csv", newline="", encoding="utf-8"))}
nv = {r["arxiv_id"]: r for r in csv.DictReader(open(OUT + "/new_versions.csv", newline="", encoding="utf-8"))}

idx = [i for i, r in enumerate(bib) if r["title"].startswith("Expressive power of tensor-network")]
assert len(idx) == 1, idx
i = idx[0]
row, m, v = bib[i], meta[AID], nv[AID]
print(f"line {i + 2}: arxiv_id {row['arxiv_id']!r} -> {AID!r}")
assert not row["arxiv_id"].strip(), "already has an arxiv_id"
row["arxiv_id"] = AID

stored = row["abstract"].strip()
full = m["abstract"].strip()
verdict = "zero_hit" if sq(stored) != sq(full) else "consistent"
print(f"stored {len(stored)} chars vs arXiv {len(full)} chars -> verdict {verdict}")

p = next(x for x in pv if int(x["row_no"]) == i + 2)
before = dict(p)
p.update({"arxiv_id": AID, "doi": v["journal_doi"], "verdict": verdict,
          "abs_authority": "arxiv", "arxiv_abs": "https://arxiv.org/abs/" + AID,
          "published": v["published"], "published_host": v["published_host"],
          "oa_pdf": v["oa_pdf"], "github": v["github"], "homepage": v["homepage"],
          "jref": v["jref"], "venue": "" if v["venue"].lower().startswith("arxiv") else v["venue"],
          "full_abs_len": str(len(full)), "stored_abs_len": str(len(stored)),
          "full_abstract": full})
for k in before:
    if before[k] != p[k]:
        print(f"   {k}: {str(before[k])[:52]!r} -> {str(p[k])[:52]!r}")

with open(LIT + "/bibliography.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader(); w.writerows(bib)
with open(OUT + "/paper_versions.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=pv_cols)
    w.writeheader(); w.writerows(pv)
print("written")
