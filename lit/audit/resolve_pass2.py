#!/usr/bin/env python3
"""Second-pass resolver for rows that still lack an authoritative abstract.

Why a second pass is needed: scan_abstracts.extract() grabs the DOI with a greedy
pattern, so IOP/Frontiers URLs contribute DOIs like '10.1088/1367-2630/12/2/025007/meta'
-- the trailing '/meta' is not part of the DOI and every such lookup failed. 8 rows are
affected, 3 of them inside the unresolved set.

Order of attempts per row:
  1. cleaned DOI -> OpenAlex (abstract rebuilt from abstract_inverted_index)
  2. cleaned DOI -> Crossref (JATS abstract, tags stripped)
  3. no DOI / nothing found -> OpenAlex title search, accepted only when the normalized
     title is identical to the stored one
"""
import csv, json, re, sys, time, urllib.parse, urllib.request

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
OUT = LIT + "/audit"
sys.path.insert(0, OUT)
from scan_abstracts import extract, sq  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) tn-lm-resolve2",
      "Accept": "application/json"}
TAIL = re.compile(r"/(meta|abstract|full|pdf|pdfs?|referenceWork|citework)$", re.I)
TAG = re.compile(r"<[^>]+>")


def clean(doi):
    d = (doi or "").strip().rstrip(".")
    while TAIL.search(d):
        d = TAIL.sub("", d)
    return d


def get(url, tries=2):
    for a in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45).read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(3)
        except Exception:
            time.sleep(3)
    return None


def oa_abstract(w):
    inv = w.get("abstract_inverted_index") or {}
    pos = {}
    for word, ix in inv.items():
        for k in ix:
            pos[k] = word
    return re.sub(r"\s+", " ", " ".join(pos[k] for k in sorted(pos))).strip()


bib = list(csv.DictReader(open(LIT + "/bibliography.csv", newline="", encoding="utf-8")))
pv = list(csv.DictReader(open(OUT + "/paper_versions.csv", newline="", encoding="utf-8")))
by_row = {int(p["row_no"]): p for p in pv}
targets = [i + 2 for i in range(len(bib)) if not (by_row[i + 2].get("full_abstract") or "").strip()]
print("rows still without an authoritative abstract:", len(targets))

COLS = ["row_no", "stored_title", "stored_year", "match", "found_arxiv_id", "found_title", "found_year",
        "full_abs_len", "jref", "doi", "abstract"]
rows, fixed_doi = [], 0
for n, rn in enumerate(targets, 1):
    b, p = bib[rn - 2], by_row[rn]
    raw_doi = (p.get("doi") or "").strip()
    aid, doi = extract(b)
    cdoi = clean(raw_doi) or clean(doi)
    rec = {"row_no": rn, "stored_title": b["title"], "stored_year": str(b["year"])[:4],
           "match": "", "found_arxiv_id": aid or (b.get("arxiv_id") or "").strip(),
           "found_title": "", "found_year": "", "full_abs_len": "0", "jref": "",
           "doi": cdoi, "abstract": ""}
    if raw_doi and cdoi and raw_doi != cdoi:
        p["doi"] = cdoi
        fixed_doi += 1
        print(f"   DOI 去尾: 行 {rn} {raw_doi} -> {cdoi}")
    if cdoi:
        d = get("https://api.openalex.org/works/doi:" + urllib.parse.quote(cdoi.lower(), safe="")
                + "?mailto=audit@example.org")
        if d:
            w = json.loads(d)
            ab = oa_abstract(w)
            if ab:
                rec.update({"match": "doi-openalex", "abstract": ab,
                            "found_title": w.get("title") or b["title"],
                            "full_abs_len": str(len(ab)),
                            "jref": ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""})
        if not rec["abstract"]:
            d = get("https://api.crossref.org/works/" + urllib.parse.quote(cdoi, safe="/"))
            if d:
                try:
                    it = json.loads(d).get("message", {})
                except Exception:
                    it = {}
                ab = TAG.sub(" ", it.get("abstract") or "")
                ab = re.sub(r"\s+", " ", re.sub(r"^Abstract\s*", "", ab)).strip()
                if ab:
                    ttl = (it.get("title") or [""])[0]
                    rec.update({"match": "doi-crossref", "abstract": ab, "found_title": ttl,
                                "full_abs_len": str(len(ab)),
                                "jref": (it.get("container-title") or [""])[0]})
    if not rec["abstract"]:
        q = re.sub(r"[^\w\s]", " ", b["title"]).strip()
        q = re.sub(r"\s+", " ", q)
        d = get("https://api.openalex.org/works?filter=titles.search:"
                + urllib.parse.quote(q[:180]) + "&per-page=6&mailto=audit@example.org")
        if d:
            for w in json.loads(d).get("results", []):
                if sq(w.get("title") or "") != sq(b["title"]):
                    continue
                ab = oa_abstract(w)
                if not ab:
                    continue
                y = str((w.get("publication_date") or "")[:4])
                rec.update({"match": "title-openalex", "abstract": ab, "found_title": w["title"],
                            "found_year": y, "full_abs_len": str(len(ab)),
                            "jref": ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or "",
                            "doi": clean((w.get("doi") or "").replace("https://doi.org/", "")) or rec["doi"]})
                break
    rows.append(rec)
    if n % 10 == 0:
        print(f"   {n}/{len(targets)} 命中 {sum(1 for r in rows if r['match'])}", flush=True)
    time.sleep(0.25)

with open(OUT + "/resolve_pass2.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
with open(LIT + "/bibliography.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(bib[0].keys()))
    w.writeheader(); w.writerows(bib)
with open(OUT + "/paper_versions.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(pv[0].keys()))
    w.writeheader(); w.writerows(pv)

from collections import Counter
c = Counter(r["match"] for r in rows)
print(f"\nwrote resolve_pass2.csv: {dict(c.most_common())}")
print(f"DOI 去尾修正 {fixed_doi} 条 version 记录")
print("第二遍可回填:", sum(c[k] for k in ("doi-openalex", "doi-crossref", "title-openalex")))
