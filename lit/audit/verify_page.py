#!/usr/bin/env python3
"""Regression check for app/library.html.

Compares the rendered PAPERS array against a snapshot taken before the merge, so any
change to a pre-existing record is reported instead of assumed harmless.
"""
import csv, json, os, re, sys

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
HTML = "/Users/bjergsen/Documents/GitHub/tn-lm/app/library.html"
SNAP = "/tmp/before_papers.json"

html = open(HTML, encoding="utf-8").read()
now = json.loads(re.search(r"const PAPERS=(\[.*?\]);\n", html, re.S).group(1))
before = json.load(open(SNAP, encoding="utf-8"))
bib = list(csv.DictReader(open(LIT + "/bibliography.csv", newline="", encoding="utf-8")))
pv = list(csv.DictReader(open(LIT + "/audit/paper_versions.csv", newline="", encoding="utf-8")))

fails = []
ck = lambda m: (print("FAIL:", m), fails.append(m))

print(f"records: before={len(before)} now={len(now)} bibliography={len(bib)} versions={len(pv)}")
if len(now) != len(bib):
    ck("PAPERS length != bibliography rows")
if sorted(int(p["row_no"]) for p in pv) != list(range(2, len(bib) + 2)):
    ck("paper_versions row_no is not exactly the bibliography line numbers")
for p in pv:
    if not bib[int(p["row_no"]) - 2]["title"].startswith(p["title"][:100]):
        ck(f"row_no {p['row_no']} points at the wrong paper")
        break

bt = {r["t"]: r for r in before}
if len(bt) != len(before):
    ck("snapshot had duplicate titles; per-record diff is unreliable")
# Backfilling is supposed to change a card's abstract/note/links/venue. A change to
# title, authors, year, url or pdf is not supposed to happen at all.
SAFE = {"abs", "absn", "vk", "lk", "v"}
now_by_t = {r["t"]: r for r in now}
changed, unsafe = [], []
for t, r in bt.items():
    n = now_by_t.get(t)
    if n is None or n == r:
        continue
    keys = {k for k in r if r[k] != n[k]}
    (changed if keys <= SAFE else unsafe).append((t, keys))
print(f"pre-existing records untouched: {len(bt) - len(changed) - len(unsafe)}/{len(bt)}")
print(f"pre-existing records changed only in backfill fields: {len(changed)}")
if unsafe:
    for t, k in unsafe[:5]:
        print("   UNSAFE:", t[:55], sorted(k))
    ck(f"{len(unsafe)} pre-existing records changed outside the backfill fields")

missing = [t for t in bt if t not in {x["t"] for x in now}]
if missing:
    ck(f"{len(missing)} records vanished, e.g. {missing[:3]}")

added = [r for r in now if r["t"] not in bt]
print(f"new records: {len(added)}")
noref = [r for r in added if not r["abs"].strip()]
if noref:
    ck(f"{len(noref)} new records have an empty abstract")
noid = [r for r in added if not r["lk"]]
if noid:
    ck(f"{len(noid)} new records have no version link at all")

publabel = [r for r in now for l in r["lk"] if l[0] == "发表版"]
if publabel:
    print(f"note: {len(publabel)} links still labelled 发表版")
    for r in publabel[:5]:
        print("   ", r["t"][:50], [l for l in r["lk"] if l[0] == "发表版"])

aid = [r["arxiv_id"].strip() for r in bib if (r["arxiv_id"] or "").strip()]
dup = {a for a in aid if aid.count(a) > 1}
if dup:
    ck(f"duplicate arxiv_id: {list(dup)[:5]}")

stat = dict(re.findall(r'<div class="num">([^<]*)</div><div class="lbl">([^<]*)</div>', html))
vk = sum(1 for r in now if r["vk"])
print("banner:", stat)
if str(vk) not in " ".join(f"{k}" for k in stat):
    ck(f"verified-abstract count {vk} not present in the banner numbers {list(stat)}")
npdf = sum(1 for r in now if r["pdf"])
badpdf = [r["pdf"] for r in now
          if r["pdf"] and not os.path.exists(os.path.join(LIT, "papers", os.path.basename(r["pdf"])))]
if badpdf:
    ck(f"{len(badpdf)} local pdf links point at missing files")
print(f"records with local pdf: {npdf}")
print("\n" + ("ALL CHECKS PASSED" if not fails else f"{len(fails)} CHECK(S) FAILED"))
sys.exit(1 if fails else 0)
