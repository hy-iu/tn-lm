#!/usr/bin/env python3
"""Identify each awesome-list entry and mark whether the corpus already has it.

Resolution order per entry: arXiv id straight out of the URL, then DOI out of the URL
(OpenAlex then Crossref for the title), then a title search on OpenAlex and on arXiv.
Match against the corpus uses the same three tests the merge used: arXiv id, DOI, or an
identical normalized title (plus the >=60-char-prefix + same-year rule that caught the
arXiv-subtitle duplicate earlier). Results are cached, so re-runs only hit the network
for entries that are still unknown.
"""
import csv, json, os, re, sys, time, urllib.parse, urllib.request

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
OUT = LIT + "/audit"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) tn-lm-awesome",
      "Accept": "application/json"}
sys.path.insert(0, OUT)
from scan_abstracts import sq  # noqa: E402

ARX = re.compile(r"arxiv\.org/(?:abs|pdf)/([\w.\-]+?)(?:v\d+)?(?:$|[?#/])")
DOI = re.compile(r"doi\.org/(10\.\d{4,5}/[^\s\"')]+)", re.I)


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
    for wd, ix in inv.items():
        for k in ix:
            pos[k] = wd
    return re.sub(r"\s+", " ", " ".join(pos[k] for k in sorted(pos))).strip()


bib = list(csv.DictReader(open(LIT + "/bibliography.csv", newline="", encoding="utf-8")))
c_ax, c_doi, c_t = set(), set(), set()
for r in bib:
    blob = " ".join(str(r.get(k) or "") for k in ("arxiv_id", "url", "all_pdfs", "pdf_links", "journal_ref"))
    c_ax |= {m.group(1) for m in ARX.finditer(blob)}
    c_ax |= {(r.get("arxiv_id") or "").strip()} - {""}
    c_doi |= {m.group(1).lower().rstrip(".") for m in DOI.finditer(blob)}
    for d in re.findall(r"10\.\d{4,5}/[^\s;\"'|]+", str(r.get("journal_ref") or "")):
        c_doi.add(d.lower().rstrip("."))
    c_t.add(sq(r["title"]))
print(f"corpus: {len(c_ax)} arxiv ids, {len(c_doi)} dois, {len(c_t)} titles")

ent = [r for r in csv.DictReader(open(OUT + "/awesome_entries.csv", newline="", encoding="utf-8"))
       if r["host"] not in ("github.com", "gitlab.com", "tensorly.org", "tensortoolbox.org", "itensor.org")
       and r["section"] != "Python tensor libraries"]
# List B repeats the same paper in "Recent Highlights" with an abbreviated title
# ("TRAC") and in its topic section with the full one, both pointing at the same URL.
# Keep the longest title per URL so the lookup has something to match on.
byurl = {}
for e in ent:
    cur = byurl.get(e["url"])
    if cur is None or len(e["title"]) > len(cur["title"]):
        byurl[e["url"]] = e
ent = list(byurl.values())
print("paper-like entries:", len(ent))

CACHE = OUT + "/awesome_lookup.json"
lk = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
if "--reprobe" in sys.argv:
    # the first pass used an invalid OpenAlex filter (titles.search); anything that
    # came back empty has to be asked again.
    before = len(lk)
    lk = {k: v for k, v in lk.items() if v.get("how") != "NOT-FOUND"}
    print(f"re-probing {before - len(lk)} previously unresolved entries", flush=True)

for n, e in enumerate(ent, 1):
    k = e["url"]
    if k in lk:
        continue
    rec = {"arxiv_id": "", "doi": "", "found_title": "", "year": "", "oa_cited": "",
           "venue": "", "how": ""}
    m = ARX.search(e["url"])
    if m:
        rec["arxiv_id"] = m.group(1)
        rec["how"] = "url-arxiv"
    d = DOI.search(e["url"])
    if d and not rec["arxiv_id"]:
        rec["doi"] = d.group(1).lower().rstrip(".")
        rec["how"] = "url-doi"
    if not (rec["arxiv_id"] or rec["doi"]):
        q = re.sub(r"[^\w\s]", " ", e["title"])
        q = re.sub(r"\s+", " ", q).strip()
        raw = get("https://api.openalex.org/works?filter=title.search:"
                  + urllib.parse.quote(q[:180]) + "&per-page=8&mailto=audit@example.org")
        if raw:
            for w in json.loads(raw).get("results", []):
                ft = sq(w.get("title") or "")
                et = sq(e["title"])
                # accept an exact match or a >=25-char prefix (arXiv/OpenAlex often carry
                # a longer subtitled form of the same paper)
                if not ft or (ft != et and not (ft.startswith(et[:25]) or et.startswith(ft[:25]))):
                    continue
                dd = (w.get("doi") or "").replace("https://doi.org/", "").lower()
                am = ARX.search(json.dumps(w.get("locations") or []))
                rec["doi"] = dd if not dd.startswith("10.48550") else ""
                rec["arxiv_id"] = am.group(1) if am else ""
                rec["found_title"] = w.get("title") or ""
                rec["year"] = (w.get("publication_date") or "")[:4]
                rec["oa_cited"] = str(w.get("cited_by_count") or "")
                rec["venue"] = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
                rec["how"] = "title-openalex"
                break
        if not rec["how"]:
            raw = get("http://export.arxiv.org/api/query?search_query=ti:"
                      + urllib.parse.quote('"%s"' % q[:110]) + "&max_results=8")
            if raw:
                import xml.etree.ElementTree as ET
                NS = {"a": "http://www.w3.org/2005/Atom"}
                for x in ET.fromstring(raw).findall("a:entry", NS):
                    tt = re.sub(r"\s+", " ", x.findtext("a:title", default="", namespaces=NS)).strip()
                    if sq(tt) != sq(e["title"]):
                        continue
                    i = ARX.search(x.findtext("a:id", default="", namespaces=NS))
                    rec["arxiv_id"] = i.group(1) if i else ""
                    rec["found_title"], rec["year"] = tt, (x.findtext("a:published", default="", namespaces=NS) or "")[:4]
                    rec["how"] = "title-arxiv"
                    break
    lk[k] = rec
    if not rec["how"]:
        lk[k]["how"] = "NOT-FOUND"
    time.sleep(0.2)
    if n % 15 == 0:
        json.dump(lk, open(CACHE, "w"))
        print(f"   {n}/{len(ent)}", flush=True)
json.dump(lk, open(CACHE, "w"))

rows = []
for e in ent:
    r = lk[e["url"]]
    inax = bool(r["arxiv_id"]) and r["arxiv_id"] in c_ax
    indoi = bool(r["doi"]) and r["doi"] in c_doi
    intit = sq(e["title"]) in c_t or sq(r["found_title"]) in c_t
    status = "already" if (inax or indoi or intit) else ("unresolved" if r["how"] == "NOT-FOUND" else "NEW")
    hits = [nm for nm, ok in (("arxiv", inax), ("doi", indoi), ("title", intit)) if ok]
    rows.append(dict(e, arxiv_id=r["arxiv_id"], doi=r["doi"], year=r["year"] or e["year"],
                     cited=r["oa_cited"], venue=r["venue"], how=r["how"], status=status,
                     match_on=",".join(hits)))
with open(OUT + "/awesome_status.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

from collections import Counter
c = Counter(r["status"] for r in rows)
print(f"\n{len(rows)} entries:", dict(c.most_common()))
print("识别方式:", dict(Counter(r["how"] for r in rows).most_common()))
print("\n--- 库里没有的新条目 (%d) ---" % c["NEW"])
for r in sorted([x for x in rows if x["status"] == "NEW"], key=lambda x: x["year"]):
    print(f"   {r['year'] or '????'} [{r['list']}] {(r['arxiv_id'] or r['doi'] or '-')[:26]:28s} {r['title'][:60]}")
print("\n--- 认不出来的 (%d) ---" % c["unresolved"])
for r in rows:
    if r["status"] == "unresolved":
        print(f"   [{r['list']}] {r['host']:24s} {r['title'][:58]}")
