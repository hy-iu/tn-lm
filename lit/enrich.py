#!/usr/bin/env python3
"""Enrich bibliography.csv: full abstracts + journal names.
1) arXiv batch API for known arXiv IDs. 2) OpenAlex title search for the rest.
Writes back: abstract (full when found, else original), new column journal_ref."""
import json, re, time, urllib.parse, urllib.request
import pandas as pd

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
BIB = f"{LIT}/bibliography.csv"
UA = {"User-Agent": "tn-lm-lit-enrich/1.0 (mailto:research@example.org)"}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode())

def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", str(t).lower()).strip()

bib = pd.read_csv(BIB)
bib["abstract"] = bib["abstract"].fillna("")
bib["journal_ref"] = ""

# ---- 1) arXiv batch (Atom XML) ----
import xml.etree.ElementTree as ET
ax = bib[bib["arxiv_id"].notna()]["arxiv_id"].tolist()
ax = [str(a) for a in ax]
ax = list(dict.fromkeys(ax))
ns = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
for i in range(0, len(ax), 50):
    chunk = ax[i:i+50]
    url = "https://export.arxiv.org/api/query?id_list=" + ",".join(chunk)
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            root = ET.fromstring(r.read())
        for e in root.findall("a:entry", ns):
            aid = e.find("a:id", ns).text.rsplit("/", 1)[-1].split("v")[0]
            summ = re.sub(r"\s+", " ", e.find("a:summary", ns).text).strip()
            jr = e.find("arxiv:journal_ref", ns)
            jr = jr.text.strip() if jr is not None and jr.text else ""
            m = bib["arxiv_id"] == aid
            if m.any():
                bib.loc[m, "abstract"] = summ
                if jr:
                    bib.loc[m, "journal_ref"] = jr
    except Exception as ex:
        print("arxiv batch fail", i, str(ex)[:100])
    time.sleep(3)

# ---- 2) OpenAlex title search for papers still lacking full abstract ----
def full_enough(a):
    return len(str(a)) > 400

need = bib[~bib["abstract"].apply(full_enough)].copy()
print("openalex candidates:", len(need))
n_found = 0
done_jr = bib["journal_ref"].str.len().fillna(0) > 0
for k, (idx, row) in enumerate(need.iterrows()):
    if full_enough(bib.loc[idx, "abstract"]) and done_jr.get(idx, False):
        continue
    title = str(row["title"])
    try:
        q = urllib.parse.urlencode({"search": title, "per-page": 3,
                                    "mailto": "research@example.org"})
        data = get("https://api.openalex.org/works?" + q)
        best, best_score = None, 0
        for w in data.get("results", []):
            t2 = w.get("display_name", "")
            a, b2 = norm(title), norm(t2)
            score = 0 if not a or not b2 else (1.0 if a == b2 else
                   len(set(a.split()) & set(b2.split())) / max(len(set(a.split())), len(set(b2.split()))))
            if score > best_score:
                best, best_score = w, score
        if best and best_score >= 0.6:
            inv = best.get("abstract_inverted_index")
            if inv:
                pos = {}
                for w, ps in inv.items():
                    for p in ps:
                        pos[p] = w
                abs_full = " ".join(pos[i] for i in sorted(pos))
                if len(abs_full) > len(str(bib.loc[idx, "abstract"])):
                    bib.loc[idx, "abstract"] = abs_full
            src = (best.get("primary_location") or {}).get("source") or {}
            venue = src.get("display_name", "")
            if venue and not str(bib.loc[idx, "journal_ref"]):
                bib.loc[idx, "journal_ref"] = venue
            n_found += 1
    except Exception as ex:
        print("openalex fail", idx, str(ex)[:80])
    if k % 15 == 0:
        bib.to_csv(BIB, index=False)
    time.sleep(0.15)

bib.to_csv(BIB, index=False)
n_full = bib["abstract"].apply(full_enough).sum()
n_jr = (bib["journal_ref"].str.len() > 0).sum()
print(f"done: full abstracts {n_full}/{len(bib)}, journal_ref {n_jr}, openalex matched {n_found}")
