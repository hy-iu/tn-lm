#!/usr/bin/env python3
"""Measure recall gap: re-run the 12 retrieval families against the arXiv API with
paging, then diff returned arXiv ids against bibliography.csv.

The original corpus came from Semantic Scholar with limit=30 per query (every
lit/csv/qNN_*.csv has exactly 30 rows). This probe asks: what is still out there?
"""
import csv, json, os, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
OUT = os.path.join(LIT, "audit")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) recall-probe"}
NS = {"a": "http://www.w3.org/2005/Atom",
      "os": "http://a9.com/-/spec/opensearch/1.1/"}

FAMILIES = {
    "q01_mps_lm":       '(ti:"matrix product state" OR ti:"matrix-product state") AND (abs:"language model" OR ti:language)',
    "q02_tn_seq":       'abs:"tensor network" AND (abs:"sequence modeling" OR ti:sequence)',
    "q03_tt_nn":        '(ti:"tensor train" OR ti:"tensor-train" OR abs:"tensor train") AND (ti:"neural network" OR ti:compression OR abs:"deep neural")',
    "q04_tn_llm":       'abs:"tensor network" AND (abs:"large language model" OR ti:LLM)',
    "q05_born":         'abs:"Born machine"',
    "q06_mi":           'abs:"mutual information" AND (abs:"natural language" OR abs:"language model")',
    "q07_qiml_review":  'ti:"quantum-inspired tensor network"',
    "q08_ttn":          'abs:"tree tensor network" AND (abs:generative OR abs:"language model")',
    "q09_qllm":         'ti:quantum AND (ti:"language model" OR ti:LLM)',
    "q10_tt_tf":        '(abs:tensorized OR abs:"tensor train" OR abs:"matrix product state") AND ti:transformer',
    "q11_peps":         'abs:"projected entangled pair state" AND (abs:learning OR abs:"neural network")',
    "q12_ent_lang":     'abs:entanglement AND ti:language',
    # Families the original 12 never covered. x1 alone returns tn4ml (2502.13090).
    "x1_tn_ml":         'abs:"tensor network" AND ti:"machine learning"',
    "x2_tn_opt":        'abs:"tensor network" AND abs:"optimization pipeline"',
    "x3_tn_software":   'abs:"tensor network" AND (abs:library OR abs:software) '
                        'AND (abs:"machine learning" OR abs:"deep learning")',
}

# A missing record only counts as on-topic if its title carries a tensor-network term.
ON_TOPIC = re.compile(r"tensor[- ]?network|matrix[- ]product|tensor[- ]train|PEPS|MERA|"
                      r"tree tensor|born machine|entanglement (?:renormalization|squeezing)", re.I)


def fetch(query, start, per_page):
    url = ("http://export.arxiv.org/api/query?search_query=" + urllib.parse.quote(query)
           + f"&start={start}&max_results={per_page}&sortBy=relevance&sortOrder=descending")
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:
            sys.stderr.write(f"  retry {attempt+1}: {e}\n")
            time.sleep(4 * (attempt + 1))
    return None


def parse(data):
    root = ET.fromstring(data)
    tot = root.findtext("os:totalResults", default="0", namespaces=NS)
    ents = []
    for e in root.findall("a:entry", NS):
        eid = e.findtext("a:id", default="", namespaces=NS)
        m = re.search(r"arxiv\.org/abs/([^v]+)v?(\d*)", eid)
        title = re.sub(r"\s+", " ", e.findtext("a:title", default="", namespaces=NS)).strip()
        pub = e.findtext("a:published", default="", namespaces=NS)
        ents.append({"id": m.group(1) if m else "", "title": title, "year": pub[:4]})
    return int(tot), ents


corpus_ids, corpus_titles = set(), set()
with open(os.path.join(LIT, "bibliography.csv"), newline="") as fh:
    for row in csv.DictReader(fh):
        blob = " ".join(str(row.get(k) or "") for k in ("arxiv_id", "url", "all_pdfs", "pdf_links"))
        for m in re.finditer(r"([0-9]{4}\.[0-9]{4,5})", blob):
            corpus_ids.add(m.group(1))
        t = re.sub(r"[^a-z0-9]+", " ", (row.get("title") or "").lower()).strip()
        if t:
            corpus_titles.add(t)

print(f"corpus arxiv ids: {len(corpus_ids)} | corpus titles: {len(corpus_titles)}", flush=True)

RAW = os.path.join(OUT, "recall_probe_raw.json")
cache = json.load(open(RAW)) if os.path.exists(RAW) else {}


def norm_t(t):
    return re.sub(r"[^a-z0-9]+", " ", str(t).lower()).strip()


PER_PAGE = 200
all_missing, family_rows = {}, []
for fam, q in FAMILIES.items():
    if fam in cache:
        total, got = cache[fam]["total"], cache[fam]["entries"]
    else:
        got, start, total = [], 0, None
        while True:
            data = fetch(q, start, PER_PAGE)
            if data is None:
                break
            t, ents = parse(data)
            if total is None:
                total = t
            got.extend(ents)
            start += PER_PAGE
            if not ents or start >= total:
                break
            time.sleep(3)
        time.sleep(3)
        total = total or len(got)
        cache[fam] = {"total": total, "entries": got}
        json.dump(cache, open(RAW, "w"))
    hit_ids = {e["id"] for e in got if e["id"]}
    by_id = {e["id"]: e for e in got if e["id"]}
    new = {i: by_id[i] for i in hit_ids - corpus_ids
           if norm_t(by_id[i]["title"]) not in corpus_titles}
    for i, e in new.items():
        rec = all_missing.get(i)
        if rec is None:
            all_missing[i] = dict(e, families=fam)
        else:
            rec["families"] += "," + fam
    family_rows.append({"family": fam, "query": q, "total_results": total,
                        "fetched": len(got), "in_corpus": len(hit_ids & corpus_ids),
                        "missing": len(new),
                        "missing_on_topic": sum(1 for e in new.values() if ON_TOPIC.search(e["title"]))})
    print(f"{fam:16s} total={total:5d} fetched={len(got):5d} in_corpus={len(hit_ids & corpus_ids):4d} "
          f"new={len(new)} on_topic_new={family_rows[-1]['missing_on_topic']}", flush=True)

with open(os.path.join(OUT, "recall_probe_families.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(family_rows[0]))
    w.writeheader(); w.writerows(family_rows)

rows = sorted(all_missing.values(), key=lambda r: (r["year"], r["title"]))
with open(os.path.join(OUT, "recall_probe_missing.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["id", "year", "title", "families"])
    w.writeheader(); w.writerows(rows)

on_topic = [r for r in rows if ON_TOPIC.search(r["title"])]
with open(os.path.join(OUT, "missing_on_topic.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["id", "year", "title", "families"])
    w.writeheader(); w.writerows(on_topic)

by_year = {}
for r in on_topic:
    by_year[r["year"]] = by_year.get(r["year"], 0) + 1

print(f"\ncandidates returned by arXiv but absent from corpus: {len(all_missing)}")
print(f"  of those, title carries a tensor-network term (on-topic): {len(on_topic)}")
print("  on-topic by year:", dict(sorted(by_year.items())))
print(f"tn4ml 2502.13090 in on-topic missing set: {'2502.13090' in all_missing}")
json.dump({"n_candidates": len(all_missing), "n_on_topic": len(on_topic),
           "on_topic_by_year": by_year,
           "tn4ml_in_missing_set": "2502.13090" in all_missing,
           "tn4ml": all_missing.get("2502.13090")},
          open(os.path.join(OUT, "recall_probe_summary.json"), "w"), indent=1)

