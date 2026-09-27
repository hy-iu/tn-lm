#!/usr/bin/env python3
"""Fetch authoritative arXiv metadata for every recall-probe candidate.

Reads the per-family cache written by recall_probe.py, collects the arXiv ids that
are NOT already in bibliography.csv, then batch-fetches title/authors/date/abstract/
DOI/journal_ref/categories from the arXiv Atom API. Incremental: ids already present
in the output CSV are skipped on re-run.
"""
import csv, json, os, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
OUT = os.path.join(LIT, "audit")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) tn-lm-completion"}
NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
FIELDS = ["arxiv_id", "title", "authors", "year", "published", "updated", "abstract",
          "doi", "journal_ref", "primary", "categories", "versions", "families"]


def norm_t(t):
    return re.sub(r"[^a-z0-9]+", " ", str(t).lower()).strip()


bib = list(csv.DictReader(open(os.path.join(LIT, "bibliography.csv"), newline="")))
corpus_ids, corpus_titles = set(), set()
for r in bib:
    blob = " ".join(str(r.get(k) or "") for k in ("arxiv_id", "url", "all_pdfs", "pdf_links"))
    corpus_ids |= set(re.findall(r"[0-9]{4}\.[0-9]{4,5}", blob))
    corpus_titles.add(norm_t(r["title"]))

cand = {}
raw = json.load(open(os.path.join(OUT, "recall_probe_raw.json")))
for fam, blk in raw.items():
    for e in blk["entries"]:
        i = e["id"]
        if not i or i in corpus_ids or norm_t(e["title"]) in corpus_titles:
            continue
        cand.setdefault(i, {"families": []})
        if fam not in cand[i]["families"]:
            cand[i]["families"].append(fam)

CSVOUT = os.path.join(OUT, "cand_meta.csv")
done = set()
if os.path.exists(CSVOUT):
    for r in csv.DictReader(open(CSVOUT, newline="")):
        done.add(r["arxiv_id"])
print(f"candidates not in corpus: {len(cand)} | already fetched: {len(done)}", flush=True)

todo = [i for i in sorted(cand) if i not in done]
mode = "a" if done else "w"


def batch(ids):
    url = ("http://export.arxiv.org/api/query?id_list=" + urllib.parse.quote(",".join(ids), safe=",")
           + f"&max_results={len(ids) * 3}&start=0")
    for a in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
        except Exception as e:
            sys.stderr.write(f"  retry {a+1}: {e}\n")
            time.sleep(5 * (a + 1))
    return None


fh = open(CSVOUT, mode, newline="", encoding="utf-8")
w = csv.DictWriter(fh, fieldnames=FIELDS)
if not done:
    w.writeheader()
n = 0
for k in range(0, len(todo), 50):
    chunk = todo[k:k + 50]
    data = batch(chunk)
    if data is None:
        print(f"  !! batch {k} failed, will retry next run", flush=True)
        continue
    root = ET.fromstring(data)
    for e in root.findall("a:entry", NS):
        eid = e.findtext("a:id", default="", namespaces=NS)
        m = re.search(r"abs/(.+?)(?:v\d+)?$", eid.strip())
        if not m:
            continue
        i = m.group(1)
        if i not in cand:
            continue
        summ = re.sub(r"\s+", " ", e.findtext("a:summary", default="", namespaces=NS)).strip()
        jr = e.find("arxiv:journal_ref", NS)
        doi = e.find("arxiv:doi", NS)
        pc = e.find("arxiv:primary_category", NS)
        w.writerow({
            "arxiv_id": i,
            "title": re.sub(r"\s+", " ", e.findtext("a:title", default="", namespaces=NS)).strip(),
            "authors": ", ".join(a.findtext("a:name", default="", namespaces=NS)
                                 for a in e.findall("a:author", NS)),
            "year": e.findtext("a:published", default="", namespaces=NS)[:4],
            "published": e.findtext("a:published", default="", namespaces=NS),
            "updated": e.findtext("a:updated", default="", namespaces=NS),
            "abstract": summ,
            "doi": (doi.text or "").strip() if doi is not None else "",
            "journal_ref": re.sub(r"\s+", " ", jr.text).strip() if jr is not None else "",
            "primary": pc.get("term") if pc is not None else "",
            "categories": ",".join(c.get("term") for c in e.findall("a:category", NS)),
            "versions": (re.search(r"v(\d+)$", eid.strip()).group(1)
                         if re.search(r"v(\d+)$", eid.strip()) else "1"),
            "families": ",".join(cand[i]["families"]),
        })
        n += 1
    fh.flush()
    print(f"  batch {k//50 + 1}/{(len(todo) + 49) // 50}: wrote {n}", flush=True)
    time.sleep(3)
fh.close()
print(f"saved {CSVOUT} (total rows now {len(done) + n})")
