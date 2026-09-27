#!/usr/bin/env python3
"""Merge the selected papers into bibliography.csv + paper_versions.csv.

Everything on disk is rewritten in one pass so the (year, citations-desc) ordering and
the row_no <-> line-number invariant that gen_library.py depends on both stay true.
The join key for remapping existing row numbers is the normalized title, which is
unique across the corpus (asserted below).
"""
import csv, os, re, sys
from collections import Counter

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
OUT = LIT + "/audit"
TODAY = "2026-09-26"

nt = lambda t: re.sub(r"[^a-z0-9]+", " ", str(t).lower()).strip()


def initials(full):
    """'Lieven De Wolf' -> 'L De Wolf'-ish: first letters of all but the last token."""
    names = [x.strip() for x in str(full).split(",") if x.strip()]
    out = []
    for nm in names:
        tk = nm.split()
        if len(tk) < 2:
            out.append(nm)
        else:
            out.append("".join(t[0] + " " for t in tk[:-1]) + " ".join(tk[-1:]))
    return ", ".join(out)


CLUSTERS = [
    ("MPS 语言模型", re.compile(r"language model|natural language|\bnlp\b|text generation|token|linguistic", re.I)),
    ("张量化Transformer", re.compile(r"transformer|self-attention|attention mechanism|\bbert\b|\bgpt\b", re.I)),
    ("MPO/TT 压缩", re.compile(r"compress|quantiz|\bprun|low-rank|rank allocation|efficientnet|inference cost", re.I)),
    ("MPS 生成/Born机", re.compile(r"born machine|generative|unsupervised|variational inferen|diffusion", re.I)),
    ("量子/混合LLM", re.compile(r"quantum .{0,30}(language|llm|nlp)|quantum neural network|quantum .{0,20}machine learning", re.I)),
    ("TTN/MERA/PEPS", re.compile(r"\bpeps\b|\bmera\b|tree tensor|multiscale entanglement|projected entangled|\bpepo\b|higher dim", re.I)),
    ("互信息/标度", re.compile(r"mutual information|area law|entanglement entropy|scaling law|\bcft\b|holograph", re.I)),
    ("MPS/序列建模", re.compile(r"sequence|recurrent|\brnn\b|autoregress|time series|forecast", re.I)),
    ("量子启发综述", re.compile(r"\breview\b|\bsurvey\b|lecture notes|state of the art|perspective", re.I)),
]


def clusters_of(title, abstract):
    blob = f"{title} {abstract}"
    return [name for name, rx in CLUSTERS if rx.search(blob)]


def skey(r):
    """Reproduce aggregate.py's pandas sort: year ascending with missing years LAST,
    then citations descending. Mapping a blank year to 0 would float those 6 rows to
    the top of the table and look like data churn."""
    y = int(re.sub(r"\D", "", str(r["year"]))[:4]) if re.match(r"^\s*\d{4}", str(r["year"])) else 9999
    c = str(r["citations"]).strip()
    c = int(float(c)) if re.match(r"^\d", c or "") else 0
    return (y, -c)


bib = list(csv.DictReader(open(LIT + "/bibliography.csv", newline="", encoding="utf-8")))
pv = list(csv.DictReader(open(OUT + "/paper_versions.csv", newline="", encoding="utf-8")))
cols, pv_cols = list(bib[0].keys()), list(pv[0].keys())
sel = list(csv.DictReader(open(OUT + "/to_add.csv", newline="", encoding="utf-8")))
meta = {r["arxiv_id"]: r for r in csv.DictReader(open(OUT + "/cand_meta.csv", newline="", encoding="utf-8"))}
nv = {r["arxiv_id"]: r for r in csv.DictReader(open(OUT + "/new_versions.csv", newline="", encoding="utf-8"))}

print(f"bib={len(bib)} pv={len(pv)} to_add={len(sel)} meta={len(meta)} versions_layer={len(nv)}")
assert len({nt(r["title"]) for r in bib}) == len(bib), "bibliography titles not unique"
for p in pv:
    assert bib[int(p["row_no"]) - 2]["title"].startswith(p["title"][:100]), p["row_no"]
bids = {r["arxiv_id"].strip() for r in bib if (r["arxiv_id"] or "").strip()}
bdoi = {d.lower().rstrip(".") for r in bib
        for d in re.findall(r"10\.\d{4,5}/[^\s\"'|;,]+",
                            " ".join(str(r.get(k) or "") for k in ("url", "journal_ref", "arxiv_id")))}
btitles = {nt(r["title"]) for r in bib}

newrows, newpv, skipped = [], [], Counter()
for s in sel:
    i = s["arxiv_id"]
    m, v = meta.get(i), nv.get(i)
    # Check membership first: staging rows whose version-layer payload has already been
    # consumed would otherwise be reported as "missing metadata", which would hide a row
    # that is genuinely absent from the corpus on a re-run.
    if (i in bids) or nt((m or {}).get("title") or s["title"]) in btitles:
        skipped["already_in_corpus"] += 1
        continue
    if not m or not v:
        skipped["missing_metadata"] += 1
        continue
    # staging rows are keyed by arXiv id; the few works with no arXiv record at all use
    # a "doi:<DOI>" key so they can flow through the same pipeline.
    is_doi = i.startswith("doi:")
    doi_val = i[4:] if is_doi else (v.get("journal_doi") or "")
    if is_doi and doi_val.lower() in bdoi:
        skipped["already_in_corpus"] += 1
        continue
    if not m["abstract"].strip():
        skipped["no_abstract"] += 1
        continue
    cit = (v.get("citations") or "").strip()
    if not re.match(r"^\d+$", cit):
        cit = ""            # OpenAlex 没收录就是没收录，不拿 0 冒充"零引用"
        skipped["citations_unknown"] += 1
    cl = clusters_of(m["title"], m["abstract"])
    pdf = "" if is_doi else f"https://arxiv.org/pdf/{i}"
    src_venue = (v.get("jref") or v.get("venue") or "").strip()
    if is_doi:
        pubinfo = initials(m["authors"]) + " - " + (src_venue or "arXiv") + ", " + m["year"]
    else:
        pubinfo = initials(m["authors"]) + " - arXiv preprint arXiv:" + i + ", " + m["year"] + " - arxiv.org"
        if v.get("jref"):
            pubinfo = initials(m["authors"]) + " - " + v["jref"]
    landing = v.get("published") or (("https://doi.org/" + doi_val) if doi_val else "")
    r = {c: "" for c in cols}
    r.update({"title": m["title"], "authors": initials(m["authors"]), "year": m["year"] + ".0",
              "citations": cit, "abstract": m["abstract"], "result_id": "",
              "publication_info": pubinfo, "pdf_links": "[]",
              "url": landing or (f"https://arxiv.org/abs/{i}" if not is_doi else ""),
              "total_results": "arxiv-completion",
              "search_time": TODAY + " (citations:OpenAlex)", "cluster": cl[0] if cl else "",
              "arxiv_id": "" if is_doi else i, "all_pdfs": ("['" + pdf + "']") if pdf else "[]",
              "ntitle": nt(m["title"]),
              "clusters": " / ".join(cl), "n_hits": str(len(s["families"].split(","))),
              "journal_ref": v.get("jref", "")})
    newrows.append(r)
    newpv.append({"_aid": i, "title": m["title"][:120], "arxiv_id": "" if is_doi else i,
                  "doi": doi_val, "verdict": "consistent",
                  "abs_authority": "openalex" if is_doi else "arxiv",
                  "arxiv_abs": "" if is_doi else "https://arxiv.org/abs/" + i,
                  "published": v.get("published", ""), "published_host": v.get("published_host", ""),
                  "oa_pdf": v.get("oa_pdf", ""), "github": v.get("github", ""),
                  "homepage": v.get("homepage", ""), "jref": v.get("jref", ""),
                  "venue": v.get("venue", ""), "full_abs_len": str(len(m["abstract"])),
                  "stored_abs_len": str(len(m["abstract"])), "full_abstract": m["abstract"]})
print(f"prepared {len(newrows)} rows | skipped {dict(skipped)}")
assert len({nt(r["title"]) for r in newrows}) == len(newrows), "duplicate titles among new rows"

# A journal version often carries a slightly different title than the preprint, so an
# exact-title test is not enough. Report 30-char prefix collisions for manual review
# rather than silently dropping them.
pref = {}
for r in bib:
    pref.setdefault(nt(r["title"])[:30], r["title"])
coll = [(nt(r["title"])[:30], pref[nt(r["title"])[:30]], r["title"])
        for r in newrows if nt(r["title"])[:30] in pref]
print(f"near-duplicate candidates (30-char title prefix collides with an existing row): {len(coll)}")
for p, old, new in coll[:12]:
    print(f"   existing: {old[:62]}\n   new     : {new[:62]}\n")

# A 30-char prefix is too loose to act on, but the same publication year plus an
# identical first 60 normalized characters is the same paper carrying a longer
# subtitle on arXiv (this caught arXiv:1907.03741 vs the corpus' 2019 entry).
same = {nt(r["title"])[:60]: r for r in bib}
dupes = []
keep = []
for r in newrows:
    k = nt(r["title"])[:60]
    if k in same and str(r["year"]) == str(same[k]["year"]):
        dupes.append((same[k]["title"], r["title"], r["arxiv_id"]))
        continue
    keep.append(r)
print(f"dropped as same-paper-as-existing (same year + 60-char title match): {len(dupes)}")
for old, new, aid in dupes:
    print(f"   {aid}\n     keep : {old[:70]}\n     drop : {new[:70]}")
with open(OUT + "/dup_resolution.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["arxiv_id", "kept_title", "dropped_title", "note"])
    for old, new, aid in dupes:
        w.writerow([aid, old, new, "same paper, arXiv title carries a longer subtitle"])
newrows = keep
newpv = [x for x in newpv if x["_aid"] not in {d[2] for d in dupes}]

combined = bib + newrows
combined.sort(key=skey)
line_of = {}
line_by_obj = {}
for idx, r in enumerate(combined):
    line_of.setdefault(nt(r["title"]), idx + 2)
    line_by_obj[id(r)] = idx + 2
assert len(line_of) == len(combined), "title collision after merge"

renumbered = []
for p in pv:
    src = bib[int(p["row_no"]) - 2]
    nl = line_of.get(nt(src["title"]))
    assert nl, "lost title during renumber: " + src["title"][:60]
    q = dict(p)
    q["row_no"] = str(nl)
    renumbered.append(q)
for nr, np_ in zip(newrows, newpv):
    q = {c: "" for c in pv_cols}
    q.update(np_)
    q["row_no"] = str(line_by_obj[id(nr)])
    renumbered.append(q)

assert len(combined) == len(renumbered), (len(combined), len(renumbered))
assert sorted(int(x["row_no"]) for x in renumbered) == list(range(2, len(combined) + 2))
for p in renumbered:
    assert combined[int(p["row_no"]) - 2]["title"].startswith(p["title"][:100]), p["row_no"]

with open(LIT + "/bibliography.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader(); w.writerows([{c: r.get(c, "") for c in cols} for r in combined])
with open(OUT + "/paper_versions.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=pv_cols)
    w.writeheader()
    w.writerows([{c: p.get(c, "") for c in pv_cols} for p in renumbered])

print(f"wrote bibliography.csv rows={len(combined)}  paper_versions.csv rows={len(renumbered)}")
print("cluster distribution:", Counter(r["cluster"] for r in combined).most_common())
print("unclustered:", sum(1 for r in combined if not r["cluster"]))
print("new rows with github:", sum(1 for x in newpv if x["github"]),
      "| homepage:", sum(1 for x in newpv if x["homepage"]),
      "| published link:", sum(1 for x in newpv if x["published"]))
with open(OUT + "/added_ids.txt", "w") as fh:
    fh.write("\n".join(x["_aid"] for x in newpv) + "\n")
