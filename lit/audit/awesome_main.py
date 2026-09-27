#!/usr/bin/env python3
"""Main pass: append the awesome-list gaps to the three merge inputs.

Uses awesome_to_add.py only for its fetch helpers. merge_add.py is then re-run unchanged
-- it skips anything already in the corpus and inserts only the new rows.
"""
import csv, json, re, sys, time, urllib.parse

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
OUT = LIT + "/audit"
sys.path.insert(0, OUT)
from awesome_to_add import (get, arxiv_title, crossref_title, openalex_work, arxiv_meta,
                            ARX, UA)  # noqa: E402
import ghverify                      # noqa: E402
import build_versions as B           # noqa: E402
from scan_abstracts import sq        # noqa: E402

bib = list(csv.DictReader(open(LIT + "/bibliography.csv", newline="", encoding="utf-8")))
c_ax, c_doi, c_t = set(), set(), set()
for r in bib:
    blob = " ".join(str(r.get(k) or "") for k in ("arxiv_id", "url", "all_pdfs", "pdf_links", "journal_ref"))
    c_ax |= {m.group(1) for m in ARX.finditer(blob)}
    c_ax |= {(r.get("arxiv_id") or "").strip()} - {""}
    c_doi |= {m.group(1).lower().rstrip(".") for m in re.finditer(r"(10\.\d{4,5}/[^\s\"'|;]+)", blob)}
    c_t.add(sq(r["title"]))

def openalex_title(t):
    """OpenAlex is the only source here whose title search actually finds these papers:
    arXiv's ti:"phrase" lookup returns 0 rows for titles that demonstrably exist, and its
    doi: field search answers HTTP 400. OpenAlex also carries the arXiv location."""
    q = re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", t)).strip()
    d = get("https://api.openalex.org/works?filter=title.search:"
            + urllib.parse.quote(q[:180]) + "&per-page=8&mailto=audit@example.org")
    if not d:
        return {}
    try:
        res = json.loads(d).get("results", [])
    except Exception:
        return {}
    et = sq(t)
    for w in res:
        ft = sq(w.get("title") or "")
        if not ft or (ft != et and not (ft.startswith(et[:25]) or et.startswith(ft[:25]))):
            continue
        am = ARX.search(json.dumps(w.get("locations") or []))
        doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
        return {"arxiv_id": am.group(1) if am else "",
                "doi": "" if doi.startswith("10.48550") else doi}
    return {}


work = [r for r in csv.DictReader(open(OUT + "/awesome_status.csv", newline="", encoding="utf-8"))
        if r["status"] in ("NEW", "unresolved")]
print(f"corpus: {len(c_ax)} ids / {len(c_doi)} dois | awesome rows to work on: {len(work)}", flush=True)

picked, failed = {}, []
for i, e in enumerate(work, 1):
    aid, doi = (e["arxiv_id"] or "").strip(), (e["doi"] or "").strip()
    if not aid and not doi:
        aid = arxiv_title(e["title"])
    if not aid and not doi:
        o = openalex_title(e["title"])
        aid, doi = o.get("arxiv_id", ""), o.get("doi", "") or doi
    if not aid and not doi:
        cr = crossref_title(e["title"])
        doi = cr["doi"] if cr else ""
    if not aid and doi.lower().startswith("10.48550"):
        aid = doi.split("arxiv.")[-1]
    if not (aid or doi):
        failed.append(e["title"][:58])
        continue
    if (aid and aid in c_ax) or (doi and doi.lower() in c_doi) or sq(e["title"]) in c_t:
        continue
    key = aid or doi.lower()
    if key not in picked:
        picked[key] = dict(e, aid=aid, doi=doi)
    if i % 12 == 0:
        print(f"   {i}/{len(work)} kept={len(picked)}", flush=True)
    time.sleep(0.2)

print(f"\nnew works identified: {len(picked)} | still unidentified: {len(failed)}")
for f in failed:
    print("   未识别:", f)

axm = arxiv_meta([v["aid"] for v in picked.values() if v["aid"]])
CM = ["arxiv_id", "title", "authors", "year", "published", "updated", "abstract", "doi",
      "journal_ref", "primary", "categories", "versions", "families"]
NV = ["arxiv_id", "citations", "voR_doi", "jref", "venue", "published", "published_host",
      "oa_pdf", "github", "github_from", "homepage", "openalex_hit"]
TA = ["arxiv_id", "year", "title", "primary", "rule", "families"]
allcm = list(csv.DictReader(open(OUT + "/cand_meta.csv", newline="", encoding="utf-8")))
allnv = list(csv.DictReader(open(OUT + "/new_versions.csv", newline="", encoding="utf-8")))
allta = list(csv.DictReader(open(OUT + "/to_add.csv", newline="", encoding="utf-8")))
hcm = {r["arxiv_id"] for r in allcm} - {""}
hnv = {r["arxiv_id"] for r in allnv} - {""}
hta = {r["arxiv_id"] for r in allta} - {""}

added = skipped = 0
for key, p in picked.items():
    m = axm.get(p["aid"])
    if not m:
        w = openalex_work(p["doi"]) if p["doi"] else {}
        cr = crossref_title(p["title"]) if not w.get("abstract") else None
        m = {"arxiv_id": w.get("arxiv_id") or p["aid"], "title": p["title"],
             "authors": w.get("authors", ""), "published": "", "updated": "",
             "year": w.get("year") or (cr or {}).get("year") or p["year"],
             "abstract": w.get("abstract") or (cr or {}).get("abstract") or "",
             "doi": "" if str(w.get("doi", "")).startswith("10.48550") else w.get("doi", ""),
             "journal_ref": w.get("venue") or (cr or {}).get("venue") or p["venue"],
             "primary": "", "categories": "", "versions": "1", "comment": ""}
    aid = m["arxiv_id"]
    if aid and aid in c_ax:
        skipped += 1
        print(f"   跳过（找回的预印本其实已在库中）: {aid} {p['title'][:46]}")
        continue
    if not aid or not m["abstract"].strip():
        skipped += 1
        print(f"   跳过（{'无 arXiv id' if not aid else '无权威摘要'}）: {key} {p['title'][:50]}")
        continue
    fam = "awesome-" + p["list"]
    if aid not in hcm:
        row = {c: m.get(c, "") for c in CM}
        row["families"] = fam
        allcm.append(row)
        hcm.add(aid)
    if aid not in hta:
        allta.append({c: "" for c in TA} | {"arxiv_id": aid, "year": m["year"], "title": m["title"],
                                            "primary": m["primary"], "rule": "W", "families": fam})
        hta.add(aid)
        added += 1
    if aid not in hnv:
        doi = m["doi"]
        pub, phost = "", ""
        if doi and not doi.lower().startswith("10.48550"):
            phost = B.resolve_host(doi)
            pub = "https://doi.org/" + doi if phost else ""
        gh = ""
        for txt in (m["abstract"], m.get("comment", "")):
            if "github" in (txt or "").lower():
                gh = ghverify.first_repo(txt)
                if gh:
                    break
        hp = ""
        mm = re.search(r"https?://[A-Za-z0-9.\-]+\.(?:readthedocs\.io|github\.io|gitlab\.io)[^\s\"')]*",
                       m["abstract"] + " " + m.get("comment", ""))
        if mm:
            hp = mm.group(0).rstrip('.,;)')
        cit = ""
        if doi:
            dd = get("https://api.openalex.org/works/doi:"
                     + urllib.parse.quote(doi.lower(), safe="") + "?mailto=audit@example.org")
            if dd:
                cit = str(json.loads(dd).get("cited_by_count", ""))
        allnv.append({c: "" for c in NV} | {
            "arxiv_id": aid, "citations": cit, "voR_doi": doi, "jref": m["journal_ref"],
            "venue": "", "published": pub, "published_host": phost,
            "oa_pdf": "https://arxiv.org/pdf/" + aid, "github": gh,
            "github_from": "text" if gh else "", "homepage": hp, "openalex_hit": "1"})
        hnv.add(aid)

for path, cols, rows in ((OUT + "/cand_meta.csv", CM, allcm),
                         (OUT + "/new_versions.csv", NV, allnv),
                         (OUT + "/to_add.csv", TA, allta)):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader(); w.writerows(rows)
print(f"\ncand_meta={len(allcm)} new_versions={len(allnv)} to_add={len(allta)}  (+{added} 待并入, {skipped} 跳过)")
