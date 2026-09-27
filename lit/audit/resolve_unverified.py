#!/usr/bin/env python3
"""Try to locate an authoritative record for the rows the audit could not verify.

121 of the 568 rows still have no full abstract: 96 carry neither an arXiv id nor a
DOI (the original Semantic Scholar scrape recorded only a snippet), and 25 do carry an
identifier whose fetch came back empty. This script only READS and reports -- applying
anything is a separate, reviewed step.

Match policy, deliberately strict:
  id      : the stored arXiv id resolves and its title normalizes to the stored title
  doi     : OpenAlex returns a work for the stored DOI and it carries an abstract
  ti      : arXiv title search, accepted only on an exact normalized-title match
  ti-fuzzy: arXiv title search where one normalized title is a >=25-char prefix of the
            other -- reported, never auto-applied.
"""
import csv, json, os, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
OUT = LIT + "/audit"
NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) tn-lm-resolve"}
sys.path.insert(0, OUT)
from scan_abstracts import sq  # noqa: E402


def get(url, tries=3):
    for a in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except Exception as e:
            sys.stderr.write(f"   retry {a + 1} {type(e).__name__} {e}\n")
            time.sleep(4 * (a + 1))
    return None


def arxiv_search(query):
    url = ("http://export.arxiv.org/api/query?search_query=" + urllib.parse.quote(query)
           + "&max_results=10&sortBy=relevance")
    d = get(url)
    if not d:
        return []
    out = []
    for e in ET.fromstring(d).findall("a:entry", NS):
        eid = (e.findtext("a:id", default="", namespaces=NS) or "").strip()
        m = re.search(r"abs/(.+?)(?:v\d+)?$", eid)
        jr = e.find("arxiv:journal_ref", NS)
        doi = e.find("arxiv:doi", NS)
        out.append({
            "arxiv_id": m.group(1) if m else "",
            "title": re.sub(r"\s+", " ", e.findtext("a:title", default="", namespaces=NS)).strip(),
            "abstract": re.sub(r"\s+", " ", e.findtext("a:summary", default="", namespaces=NS)).strip(),
            "jref": re.sub(r"\s+", " ", jr.text).strip() if jr is not None and jr.text else "",
            "doi": (doi.text or "").strip() if doi is not None else "",
            "year": (e.findtext("a:published", default="", namespaces=NS) or "")[:4],
        })
    return out


def openalex_doi(doi):
    d = get("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi.lower(), safe="")
            + "?mailto=audit@example.org")
    if not d:
        return None
    try:
        w = json.loads(d)
    except Exception:
        return None
    inv = w.get("abstract_inverted_index") or {}
    pos = {}
    for word, ix in inv.items():
        for k in ix:
            pos[k] = word
    return {"abstract": re.sub(r"\s+", " ", " ".join(pos[k] for k in sorted(pos))).strip(),
            "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or "",
            "cited": w.get("cited_by_count")}


bib = list(csv.DictReader(open(LIT + "/bibliography.csv", newline="", encoding="utf-8")))
pv = {int(p["row_no"]): p for p in csv.DictReader(open(OUT + "/paper_versions.csv", newline="", encoding="utf-8"))}
targets = [(i + 2, bib[i], pv[i + 2]) for i in range(len(bib))
           if not (pv[i + 2].get("full_abstract") or "").strip()]
print("rows without an authoritative abstract:", len(targets))

CACHE = OUT + "/resolve_cache.json"
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
COLS = ["row_no", "stored_title", "stored_year", "match", "found_arxiv_id", "found_title",
        "found_year", "full_abs_len", "jref", "doi", "abstract"]
rows = []
for n, (rn, r, p) in enumerate(targets, 1):
    key = str(rn)
    if key in cache:
        rows.append(cache[key])
        continue
    stored_t, want_id = r["title"], (p.get("arxiv_id") or "").strip()
    rec = {"row_no": rn, "stored_title": stored_t, "stored_year": str(r["year"])[:4],
           "match": "", "found_arxiv_id": "", "found_title": "", "found_year": "",
           "full_abs_len": "0", "jref": "", "doi": "", "abstract": ""}
    hits = []
    if want_id:
        d = get("http://export.arxiv.org/api/query?id_list="
                + urllib.parse.quote(want_id, safe="/") + "&max_results=3")
        if d:
            for e in ET.fromstring(d).findall("a:entry", NS):
                eid = (e.findtext("a:id", default="", namespaces=NS) or "").strip()
                m = re.search(r"abs/(.+?)(?:v\d+)?$", eid)
                ab = re.sub(r"\s+", " ", e.findtext("a:summary", default="", namespaces=NS)).strip()
                tt = re.sub(r"\s+", " ", e.findtext("a:title", default="", namespaces=NS)).strip()
                jr = e.find("arxiv:journal_ref", NS)
                hits.append({"arxiv_id": m.group(1) if m else want_id, "title": tt, "abstract": ab,
                             "jref": re.sub(r"\s+", " ", jr.text).strip() if jr is not None and jr.text else "",
                             "doi": "", "year": (e.findtext("a:published", default="", namespaces=NS) or "")[:4]})
    if not hits:
        q = re.sub(r"[^\w\s]", "", stored_t).strip()
        hits = arxiv_search(f'ti:"{q[:110]}"')
        if not hits and len(q.split()) > 6:
            hits = arxiv_search('ti:"%s"' % " ".join(q.split()[:9]))
    best, kind = None, ""
    st = sq(stored_t)
    for h in hits:
        ft = sq(h["title"])
        if not ft:
            continue
        if want_id and h["arxiv_id"] == want_id and (st == ft or ft.startswith(st[:40]) or st.startswith(ft[:40])):
            best, kind = h, "id"
            break
        if st == ft:
            best, kind = h, ("ti" if not want_id else "ti-id")
            break
        if (ft.startswith(st[:25]) or st.startswith(ft[:25])) and not best:
            best, kind = h, "ti-fuzzy"
    if not best and (p.get("doi") or "").strip():
        o = openalex_doi(p["doi"].strip())
        if o and o["abstract"]:
            rec.update({"match": "doi", "doi": p["doi"].strip(), "full_abs_len": str(len(o["abstract"])),
                        "abstract": o["abstract"], "found_title": stored_t, "jref": o["venue"]})
    if best and rec["match"] != "doi":
        if kind == "ti-fuzzy":
            rec.update({"match": "ti-fuzzy", "found_arxiv_id": best["arxiv_id"],
                        "found_title": best["title"], "found_year": best["year"],
                        "jref": best["jref"], "doi": best["doi"],
                        "full_abs_len": str(len(best["abstract"])), "abstract": best["abstract"]})
        else:
            rec.update({"match": kind, "found_arxiv_id": best["arxiv_id"], "found_title": best["title"],
                        "found_year": best["year"], "jref": best["jref"], "doi": best["doi"],
                        "full_abs_len": str(len(best["abstract"])), "abstract": best["abstract"]})
    cache[key] = rec
    rows.append(rec)
    if n % 10 == 0:
        json.dump(cache, open(CACHE, "w"))
        print(f"  {n}/{len(targets)} matched-so-far "
              f"{sum(1 for v in cache.values() if v['match'] in ('id', 'ti', 'ti-id', 'doi'))}", flush=True)
    time.sleep(1.2)
json.dump(cache, open(CACHE, "w"))

with open(OUT + "/resolve_unverified.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS)
    w.writeheader(); w.writerows(rows)

from collections import Counter
c = Counter(r["match"] for r in rows)
print(f"\n{len(rows)} rows probed:", dict(c.most_common()))
print("可自动应用 (id/ti/ti-id/doi):", sum(c[k] for k in ("id", "ti", "ti-id", "doi")))
print("仅模糊匹配、需人工过目 (ti-fuzzy):", c["ti-fuzzy"])
for r in rows:
    if r["match"] == "ti-fuzzy":
        print(f"   {r['row_no']:>4} 存:{r['stored_title'][:46]!r}\n        到:{r['found_title'][:46]!r} {r['found_arxiv_id']}")
print("查不到:", c[""])
