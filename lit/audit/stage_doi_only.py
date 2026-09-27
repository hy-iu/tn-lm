#!/usr/bin/env python3
"""Stage the identified-but-unstored awesome entries (no arXiv record exists for them).

merge_add.py accepts a 'doi:<DOI>' staging key and then leaves bibliography.arxiv_id
empty, so these land as DOI-identified rows. OpenAlex is queried for the abstract body;
an entry without one is reported and skipped rather than filled in from anywhere else.
"""
import csv, json, re, sys, time, urllib.parse

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
OUT = LIT + "/audit"
sys.path.insert(0, OUT)
from awesome_to_add import get, ARX            # noqa: E402
from scan_abstracts import sq                  # noqa: E402
import build_versions as B                     # noqa: E402

CM = ["arxiv_id", "title", "authors", "year", "published", "updated", "abstract", "doi",
      "journal_ref", "primary", "categories", "versions", "families"]
TA = ["arxiv_id", "year", "title", "primary", "rule", "families"]


def body(w):
    inv = w.get("abstract_inverted_index") or {}
    pos = {k: x for x, ix in inv.items() for k in ix}
    return re.sub(r"\s+", " ", " ".join(pos[k] for k in sorted(pos))).strip()


bib = list(csv.DictReader(open(LIT + "/bibliography.csv", newline="", encoding="utf-8")))
ids, dois, titles = set(), set(), set()
for r in bib:
    blob = " ".join(str(r.get(k) or "") for k in ("arxiv_id", "url", "all_pdfs", "pdf_links", "journal_ref"))
    ids |= {m.group(1) for m in ARX.finditer(blob)} - {""}
    dois |= {d.lower() for d in re.findall(r"10\.\d{4,5}/[^\s\"'|;]+", blob)}
    titles.add(sq(r["title"]))
allt = sorted(titles)
pref = lambda s: any(x == s or x.startswith(s[:25]) or s.startswith(x[:25]) for x in allt)

todo = []
for r in csv.DictReader(open(OUT + "/awesome_status.csv", newline="", encoding="utf-8")):
    aid, doi = (r["arxiv_id"] or "").strip(), (r["doi"] or "").strip()
    if (aid and aid in ids) or (doi and doi.lower() in dois) or pref(sq(r["title"])):
        continue
    if not doi:
        continue
    todo.append(r)
print("可经 DOI 入库且尚未在库的条目:", len(todo), flush=True)

cm = list(csv.DictReader(open(OUT + "/cand_meta.csv", newline="", encoding="utf-8")))
nv = list(csv.DictReader(open(OUT + "/new_versions.csv", newline="", encoding="utf-8")))
ta = list(csv.DictReader(open(OUT + "/to_add.csv", newline="", encoding="utf-8")))
seen = {r["arxiv_id"] for r in ta} - {""}
NVC = list(nv[0])
n = skipped = 0
for r in todo:
    doi = r["doi"].lower()
    key = "doi:" + doi
    if key in seen:
        continue
    d = get("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe="")
            + "?mailto=audit@example.org")
    if not d:
        print("   OpenAlex 查不到:", doi, "|", r["title"][:44])
        skipped += 1
        continue
    w = json.loads(d)
    ab = body(w)
    if not ab:
        print("   无摘要正文，不入库:", doi, "|", r["title"][:44])
        skipped += 1
        continue
    am = ARX.search(json.dumps(w.get("locations") or []))
    if am and am.group(1) in ids:
        skipped += 1
        continue
    src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
    host = B.resolve_host(doi)
    cm.append({c: "" for c in CM} | {"arxiv_id": key, "title": re.sub(r"\s+", " ", w.get("title") or r["title"]),
                                      "authors": ", ".join((a.get("author") or {}).get("display_name") or ""
                                                           for a in (w.get("authorships") or [])[:8]),
                                      "year": (w.get("publication_date") or "")[:4] or r["year"],
                                      "abstract": ab, "doi": doi, "journal_ref": src})
    nv.append({c: "" for c in NVC} | {"arxiv_id": key, "citations": str(w.get("cited_by_count") or ""),
                                      "journal_doi": doi, "jref": src, "venue": "" if src.lower().startswith("arxiv") else src,
                                      "published": "https://doi.org/" + doi if host else "",
                                      "published_host": host, "github": "", "homepage": "",
                                      "openalex_hit": "1"})
    ta.append({c: "" for c in TA} | {"arxiv_id": key, "year": (w.get("publication_date") or "")[:4] or r["year"],
                                     "title": re.sub(r"\s+", " ", w.get("title") or r["title"]),
                                     "rule": "W", "families": "awesome-" + r["list"]})
    seen.add(key)
    n += 1
    print(f"   +{key[:40]:42s} {(w.get('title') or '')[:40]}")
    time.sleep(0.2)

for path, cols, rows in ((OUT + "/cand_meta.csv", CM, cm), (OUT + "/to_add.csv", TA, ta),
                         (OUT + "/new_versions.csv", NVC, nv)):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
print(f"\nstaged={n} skipped={skipped} | to_add={len(ta)} cand_meta={len(cm)} new_versions={len(nv)}")
