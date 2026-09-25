#!/usr/bin/env python3
"""OpenAlex backfill for papers still lacking full abstracts / venue. Resumable."""
import time, urllib.parse, subprocess, json
import pandas as pd

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
BIB = f"{LIT}/bibliography.csv"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 Chrome/124.0 Safari/537.36")

def norm(t):
    return set(__import__("re").sub(r"[^a-z0-9]+", " ", str(t).lower()).split())

def full_enough(a):
    return len(str(a)) > 400

bib = pd.read_csv(BIB, dtype={"arxiv_id": str})
bib["journal_ref"] = bib["journal_ref"].fillna("").astype(str)
bib["abstract"] = bib["abstract"].fillna("")

todo = [i for i, r in bib.iterrows()
        if not (full_enough(r["abstract"]) and len(r["journal_ref"]) > 0)]
print("todo:", len(todo))

n_ok = 0
for k, idx in enumerate(todo):
    title = str(bib.loc[idx, "title"])
    q = urllib.parse.urlencode({"search": title, "per-page": 3,
                                "mailto": "research@example.org"})
    url = "https://api.openalex.org/works?" + q
    data = None
    for attempt in range(4):
        r = subprocess.run(["curl", "-sS", "-m", "30", "-A", UA, url],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip().startswith("{"):
            try:
                data = json.loads(r.stdout)
                break
            except Exception:
                pass
        wait = 15 * (attempt + 1)
        print(f"  retry idx {idx} in {wait}s (rc={r.returncode})")
        time.sleep(wait)
    if data is None:
        continue
    best, best_score = None, 0.0
    for w in data.get("results", []):
        t2 = w.get("display_name", "")
        A, B = norm(title), norm(t2)
        score = len(A & B) / max(len(A), len(B), 1)
        if score > best_score:
            best, best_score = w, score
    if best and best_score >= 0.55:
        inv = best.get("abstract_inverted_index")
        if inv:
            pos = {}
            for w, ps in inv.items():
                for p in ps:
                    pos[p] = w
            abs_full = " ".join(pos[i] for i in sorted(pos))
            if len(abs_full) > len(bib.loc[idx, "abstract"]):
                bib.loc[idx, "abstract"] = abs_full
        src = (best.get("primary_location") or {}).get("source") or {}
        venue = src.get("display_name", "") or ""
        if venue and not bib.loc[idx, "journal_ref"]:
            bib.loc[idx, "journal_ref"] = venue
        n_ok += 1
    time.sleep(0.5)
    if k % 10 == 0:
        bib.to_csv(BIB, index=False)
        print(f"progress {k+1}/{len(todo)}, matched {n_ok}")

bib.to_csv(BIB, index=False)
print("done. matched:", n_ok,
      "| full abstracts:", int(bib["abstract"].apply(full_enough).sum()),
      "| journal_ref:", int((bib["journal_ref"].str.len() > 0).sum()))
