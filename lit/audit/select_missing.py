#!/usr/bin/env python3
"""Decide which arXiv candidates genuinely belong in the corpus.

Two inclusion rules, reported separately so the sample can be eyeballed:
  T  tensor-network term in the TITLE            (high precision, the known 182)
  A  TN term in the ABSTRACT + ML term in TITLE
     + arXiv primary category inside the ML/quantum-information set
Writes lit/audit/to_add.csv and prints samples plus the rule breakdown.
"""
import csv, re
from collections import Counter

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
OUT = LIT + "/audit"

TN = re.compile(r"tensor[- ]?network|tensor[- ]?train|matrix[- ]?product|projected entangled"
                r"|\bPEPS\b|\bMERA\b|\bTTN\b|tree tensor|born machine|entanglement renormalization"
                r"|entanglement squeezing|tensor ring|tensori[sz]ed|tensor decomposition"
                r"|\bMPS\b|\bDMRG\b|multiscale entanglement", re.I)
# Rule A only trusts an explicit tensor-network model name in the abstract; the looser
# terms above ("tensor decomposition", "MPS", ...) match too many passing mentions.
TN_STRONG = re.compile(r"tensor[- ]?networks?|tensor[- ]?train|matrix[- ]?product[- ]?states?"
                       r"|projected entangled pair|\bPEPS\b|\bMERA\b|\bTTN\b|tree tensor"
                       r"|born machine|entanglement renormalization|tensor ring", re.I)
# arXiv primaries clearly outside this review's scope (applied to rule A only).
OFFSCOPE = {"physics.geo-ph", "physics.chem-ph", "physics.flu-dyn", "physics.comp-ph",
            "physics.soc-ph", "physics.optics", "physics.app-ph", "physics.med-ph",
            "q-bio.QM", "q-bio.NC", "hep-th", "hep-ph", "nucl-th", "astro-ph.IM",
            "astro-ph.HE", "cond-mat.mtrl-sci", "cond-mat.mes-hall", "cond-mat.soft",
            "math.AG", "math.DG", "math.SP", "math.PR", "math-ph", "math.OC", "math.DS",
            "cs.NI", "cs.CR", "cs.RO", "cs.SY", "eess.SP", "eess.IV", "eess.SY"}
ML = re.compile(r"neural network|machine learning|language model|deep learning|transformer"
                r"|classifi|generative|autoencoder|reinforcement learning|sequence model"
                r"|natural language|\bLLM\b|\bNLP\b|regression|compression|embedd"
                r"|probabilistic|recommender|speech|token", re.I)
CATS = {"cs.LG", "cs.AI", "cs.CL", "cs.NE", "cs.CV", "cs.MS", "stat.ML", "quant-ph", "cs.GT"}

rows = list(csv.DictReader(open(OUT + "/cand_meta.csv", newline="", encoding="utf-8")))
print("candidates with arXiv metadata:", len(rows))

kept = []
for r in rows:
    t, ab, prim = r["title"], r["abstract"], r["primary"]
    if TN.search(t):
        rule = "T"
    elif prim in CATS and prim not in OFFSCOPE and TN_STRONG.search(ab) and ML.search(t):
        rule = "A"
    else:
        continue
    kept.append(dict(r, rule=rule))


c = Counter(r["rule"] for r in kept)
print("rule T:", c["T"], "| rule A:", c["A"], "| total:", len(kept))
print("\nprimary category distribution:", Counter(r["primary"] for r in kept).most_common())
print("year distribution:", sorted(Counter(r["year"] for r in kept).items()))

with open(OUT + "/to_add.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["arxiv_id", "year", "title", "primary", "rule", "families"])
    w.writeheader()
    for r in sorted(kept, key=lambda x: (x["rule"], x["year"], x["title"])):
        w.writerow({k: r[k] for k in w.fieldnames})

print("\n=== rule A sample (25 of %d) ===" % c["A"])
for r in [x for x in kept if x["rule"] == "A"][:25]:
    print(f"  {r['arxiv_id']} {r['primary']:8s} {r['year']}  {r['title'][:78]}")
print("\n=== rule T sample from 2026 (12) ===")
s = [x for x in kept if x["rule"] == "T" and x["year"] == "2026"]
for r in s[:12]:
    print(f"  {r['arxiv_id']} {r['primary']:8s}  {r['title'][:78]}")
