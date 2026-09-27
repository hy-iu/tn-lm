#!/usr/bin/env python3
"""Add arXiv:2502.13090 (tn4ml) to the corpus.

All field values were fetched and verified this session:
  abstract/authors/date  <- arXiv Atom API (export.arxiv.org, id_list=2502.13090)
  citations/venue        <- OpenAlex W4407760034 (cited_by_count=0, no journal DOI)
  github/homepage        <- PyPI project_urls + GitHub API repos/bsc-quantic/tn4ml
No published journal version exists, so `journal_ref`, `published` and `doi` stay empty.
"""
import csv, os, re, shutil, sys

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
BIB = os.path.join(LIT, "bibliography.csv")
PV = os.path.join(LIT, "audit", "paper_versions.csv")
TMP_PDF = "/tmp/tn4ml_check.pdf"

ABS = ("Tensor Networks have emerged as a prominent alternative to neural networks for "
       "addressing Machine Learning challenges in foundational sciences, paving the way for "
       "their applications to real-life problems. This paper introduces tn4ml, a novel library "
       "designed to seamlessly integrate Tensor Networks into optimization pipelines for "
       "Machine Learning tasks. Inspired by existing Machine Learning frameworks, the library "
       "offers a user-friendly structure with modules for data embedding, objective function "
       "definition, and model training using diverse optimization strategies. We demonstrate "
       "its versatility through two examples: supervised learning on tabular data and "
       "unsupervised learning on an image dataset. Additionally, we analyze how customizing "
       "the parts of the Machine Learning pipeline for Tensor Networks influences performance "
       "metrics.")
assert len(ABS) == 843, len(ABS)

TITLE = "tn4ml: Tensor Network Training and Customization for Machine Learning"
AUTH = "E Puljak, S Sanchez-Ramirez, S Masot-Llima, J Vallès-Muns, A Garcia-Saez, M Pierini"
AID = "2502.13090"

with open(BIB, newline="", encoding="utf-8") as f:
    rdr = csv.DictReader(f)
    cols = rdr.fieldnames
    bib = list(rdr)
with open(PV, newline="", encoding="utf-8") as f:
    pv_cols = csv.DictReader(f).fieldnames
    pv = list(csv.DictReader(open(PV, newline="", encoding="utf-8")))

# --- guard: paper_versions row_no currently equals bibliography line number ---
assert len(bib) == len(pv) == 304, (len(bib), len(pv))
for p in pv:
    assert bib[int(p["row_no"]) - 2]["title"].startswith(p["title"][:100]), p["row_no"]
assert not any(AID in (r.get("arxiv_id") or "") for r in bib), "already present"
print("guards ok: 304 rows, all version rows aligned, tn4ml absent")


def key(r):
    y = int(float(r["year"])) if re.match(r"^\d", str(r["year"] or "")) else 0
    c = int(float(r["citations"] or 0)) if str(r["citations"]).strip()[:1].isdigit() else 0
    return (y, -c)


new = {c: "" for c in cols}
new.update({
    "title": TITLE, "authors": AUTH, "year": "2025.0", "citations": "0", "abstract": ABS,
    "result_id": "", "publication_info": AUTH + " - arXiv preprint arXiv:2502.13090, 2025 - arxiv.org",
    "pdf_links": "[]", "url": "https://arxiv.org/abs/2502.13090",
    "total_results": "manual", "search_time": "2026-09-26",
    "cluster": "MPS/序列建模", "arxiv_id": AID,
    "all_pdfs": "['https://arxiv.org/pdf/2502.13090']",
    "ntitle": re.sub(r"[^a-z0-9]+", " ", TITLE.lower()).strip(),
    "clusters": "MPS/序列建模", "n_hits": "1", "journal_ref": "",
})

nk = key(new)
pos = len(bib)
for i, r in enumerate(bib):
    if key(r) > nk:
        pos = i
        break
print(f"inserting at data-row index {pos} (bibliography line {pos + 2})")

# old row_no -> new row_no for every existing row at or after the insertion point
renum = {i + 2: (i + 3 if i >= pos else i + 2) for i in range(len(bib))}
for p in pv:
    p["row_no"] = str(renum[int(p["row_no"])])

bib.insert(pos, new)
assert len(bib) == 305
line_no = {id(r): i + 2 for i, r in enumerate(bib)}
for p in pv:
    src = bib[int(p["row_no"]) - 2]
    assert src["title"].startswith(p["title"][:100]), (p["row_no"], p["title"][:60])
assert len({r["arxiv_id"] for r in bib if r["arxiv_id"].strip()}) == \
       len([r for r in bib if r["arxiv_id"].strip()]), "duplicate arxiv_id"

pv.append({
    "row_no": str(line_no[id(new)]), "title": TITLE[:120], "arxiv_id": AID, "doi": "",
    "verdict": "consistent", "abs_authority": "arxiv",
    "arxiv_abs": "https://arxiv.org/abs/2502.13090", "published": "", "published_host": "",
    "oa_pdf": "https://arxiv.org/pdf/2502.13090",
    "github": "https://github.com/bsc-quantic/tn4ml",
    "homepage": "https://tn4ml.readthedocs.io",
    "jref": "", "venue": "", "full_abs_len": str(len(ABS)),
    "stored_abs_len": str(len(ABS)), "full_abstract": ABS,
})

with open(BIB, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader(); w.writerows(bib)
with open(PV, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=pv_cols)
    w.writeheader(); w.writerows(pv)
print(f"wrote {BIB} ({len(bib)} rows) and {PV} ({len(pv)} rows)")

if os.path.exists(TMP_PDF):
    def safe_name(t):
        return re.sub(r"[^A-Za-z0-9]+", "_", str(t))[:60].strip("_") or "paper"
    dst = os.path.join(LIT, "papers", f"2025_{safe_name(TITLE)[:50]}.pdf")
    shutil.copyfile(TMP_PDF, dst)
    print("PDF ->", os.path.basename(dst), os.path.getsize(dst), "bytes")
else:
    print("WARNING: no local PDF staged at", TMP_PDF)
