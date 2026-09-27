#!/usr/bin/env python3
"""OpenAlex + GitHub layer for the papers selected by select_missing.py.

Per-work lookup `api.openalex.org/works/doi:10.48550/arxiv.<id>` rather than a bulk
doi filter: OpenAlex merges a preprint into its version of record, and a merged work
reports the *journal* DOI, so bulk filtering keyed by canonical DOI would silently
miss most of them. Results cache to openalex_new.json, so re-runs only fetch gaps.

A GitHub URL is kept only when it appears in the paper's own arXiv abstract and the
repository answers on api.github.com. Anything not confirmed is left empty.
"""
import csv, json, os, re, sys, time, urllib.parse, urllib.request

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
OUT = LIT + "/audit"
sys.path.insert(0, OUT)
import build_versions as B  # noqa: E402  resolve_host / find_links

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) tn-lm-completion"}
GH_SHORT = re.compile(r"github\.com/([A-Za-z0-9_.\-]+)/([A-Za-z0-9_.\-]+)", re.I)
ARX = re.compile(r"arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5})")
GOODHOME = re.compile(r"(readthedocs\.io|github\.io|gitlab\.io|^\w[\w.\-]*\.(io|page)$)", re.I)

sel = list(csv.DictReader(open(OUT + "/to_add.csv", newline="", encoding="utf-8")))
meta = {r["arxiv_id"]: r for r in csv.DictReader(open(OUT + "/cand_meta.csv", newline="", encoding="utf-8"))}
print(f"selected: {len(sel)}", flush=True)

CACHE = OUT + "/openalex_new.json"
oa = json.load(open(CACHE)) if os.path.exists(CACHE) else {}


def work_by_doi(doi):
    url = "https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe="") + "?mailto=audit@example.org"
    for a in range(3):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45).read())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {}
            time.sleep(3 * (a + 1))
        except Exception:
            time.sleep(3 * (a + 1))
    return None


todo = [r["arxiv_id"] for r in sel if r["arxiv_id"] not in oa]
print(f"openalex to fetch: {len(todo)}", flush=True)
for k, i in enumerate(todo):
    w = work_by_doi("10.48550/arxiv." + i)
    if w is None:
        print(f"  !! {i} fetch failed (will retry next run)", flush=True)
        continue
    if not w:
        oa[i] = {"missing": True}
    else:
        canon = (w.get("doi") or "").replace("https://doi.org/", "").lower()
        locs = w.get("locations") or []
        pl = w.get("primary_location") or {}
        bo = w.get("best_oa_location") or {}
        non_arx = [l for l in locs if "arxiv.org" not in (l.get("landing_page_url") or "").lower()]
        vor = canon if not canon.startswith("10.48550") else ""
        if not vor:
            for l in locs:
                d = (l.get("landing_page_url") or "")
                m = re.search(r"doi\.org/(10\.\d{4,5}/.+)", d)
                if m and not m.group(1).lower().startswith("10.48550"):
                    vor = m.group(1).lower()
                    break
        venue = ((pl.get("source") or {}).get("display_name")) or ""
        srcs = [((l.get("source") or {}).get("display_name") or "") for l in non_arx]
        if venue.lower().startswith("arxiv") and srcs:
            venue = srcs[0]
        oa[i] = {"cited": w.get("cited_by_count"), "vor_doi": vor, "venue": venue,
                 "oa_pdf": bo.get("pdf_url") or (pl.get("pdf_url") or ""),
                 "pub_landing": (non_arx[0].get("landing_page_url") if non_arx else "")}
    if (k + 1) % 25 == 0:
        json.dump(oa, open(CACHE, "w"))
        print(f"  openalex {k + 1}/{len(todo)}", flush=True)
    time.sleep(0.18)
json.dump(oa, open(CACHE, "w"))
print(f"openalex cache: {len(oa)} entries", flush=True)

gh_cache = {}


def gh_probe(url):
    m = GH_SHORT.search(url or "")
    if not m:
        return "", ""
    repo = f"{m.group(1)}/{m.group(2)}".rstrip('.').removesuffix("/tree")
    if repo in gh_cache:
        return gh_cache[repo]
    good, home = "", ""
    try:
        req = urllib.request.Request("https://api.github.com/repos/" + repo,
                                     headers={**UA, "Accept": "application/vnd.github+json"})
        j = json.loads(urllib.request.urlopen(req, timeout=25).read())
        if j.get("full_name"):
            good, home = "https://github.com/" + j["full_name"], (j.get("homepage") or "").strip()
    except Exception:
        pass
    gh_cache[repo] = (good, home)
    time.sleep(0.15)
    return gh_cache[repo]


COLS = ["arxiv_id", "citations", "voR_doi", "venue", "published", "published_host",
        "oa_pdf", "github", "homepage", "openalex_hit"]
out = []
for r in sel:
    i = r["arxiv_id"]
    o = oa.get(i) or {}
    m = meta.get(i, {})
    gh_raw, hp_raw = B.find_links(m.get("abstract", ""))
    good, gh_home = gh_probe(gh_raw)
    hp = ""
    if gh_home and GOODHOME.search(urllib.parse.urlparse(gh_home).netloc or gh_home):
        hp = gh_home
    elif hp_raw and GOODHOME.search(urllib.parse.urlparse(hp_raw).netloc or hp_raw):
        hp = hp_raw
    pub, phost = "", ""
    if o.get("vor_doi"):
        phost = B.resolve_host(o["vor_doi"])
        if phost:
            pub = "https://doi.org/" + o["vor_doi"]
    elif o.get("pub_landing", "").startswith("http") and "arxiv.org" not in o.get("pub_landing", ""):
        pub = o["pub_landing"]
        phost = re.sub(r"^www\.", "", urllib.parse.urlparse(pub).netloc.lower())
    out.append({
        "arxiv_id": i,
        "citations": "" if o.get("cited") is None else str(o["cited"]),
        "voR_doi": o.get("vor_doi", ""), "venue": o.get("venue", ""),
        "published": pub, "published_host": phost,
        "oa_pdf": o.get("oa_pdf") or f"https://arxiv.org/pdf/{i}",
        "github": good, "homepage": hp,
        "openalex_hit": "" if o.get("missing") or not o else "1",
    })

with open(OUT + "/new_versions.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS)
    w.writeheader(); w.writerows(out)

f = lambda k: sum(1 for x in out if (x[k] or "").strip())
print(f"\nwrote new_versions.csv rows={len(out)}")
print(f"  openalex hit {f('openalex_hit')} | citations filled {f('citations')} | VoR DOI {f('voR_doi')}")
print(f"  published link {f('published')} | github {f('github')} | homepage {f('homepage')}")
from collections import Counter
print("  published hosts:", Counter(x["published_host"] for x in out if x["published_host"]).most_common(12))
