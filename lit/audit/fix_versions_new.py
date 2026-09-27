#!/usr/bin/env python3
"""Rebuild the version layer for the papers being added.

Two corrections over fetch_openalex_new.py:
  * "published" now comes only from arXiv's own <arxiv:doi>/<arxiv:journal_ref>
    metadata. OpenAlex keeps a preprint and its journal version as separate works, so
    looking a work up by 10.48550/arXiv.* returns the preprint, and its landing page is
    a doi.org URL that just redirects back to arxiv.org -- not a published version.
  * GitHub repositories are verified over https://github.com/<owner>/<repo> instead of
    api.github.com, whose 60-requests/hour anonymous quota is exhausted. A 403 from the
    API is not evidence that a repository does not exist.

arXiv comments are fetched too, because code links are more often stated there.
"""
import csv, json, os, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
OUT = LIT + "/audit"
sys.path.insert(0, OUT)
import build_versions as B  # noqa: E402  resolve_host / find_links

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) tn-lm-completion"}
GH = re.compile(r"github\.com/([A-Za-z0-9_.\-]+)/([A-Za-z0-9_.\-]+)", re.I)
CITE = re.compile(r"^\s*(?:code|software|implementation|source|repository|demo|data|"
                  r"source ?code|models?)\b[^.;]{0,60}(?:available|released|hosted|published|at|provided)",
                  re.I)


def arxiv_comments(ids):
    """arxiv:comment text per id, batched."""
    out = {}
    cf = OUT + "/cand_comment.csv"
    if os.path.exists(cf):
        for r in csv.DictReader(open(cf, newline="", encoding="utf-8")):
            out[r["arxiv_id"]] = r["comment"]
    todo = [i for i in ids if i not in out]
    if not todo:
        return out
    for k in range(0, len(todo), 40):
        chunk = todo[k:k + 40]
        url = ("http://export.arxiv.org/api/query?id_list="
               + urllib.parse.quote(",".join(chunk), safe=",") + f"&max_results={len(chunk) * 3}")
        for a in range(3):
            try:
                d = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
                break
            except Exception as e:
                sys.stderr.write(f"  arxiv retry {a + 1}: {e}\n")
                time.sleep(5)
                d = None
        if d is None:
            continue
        for e in ET.fromstring(d).findall(
                "{http://www.w3.org/2005/Atom}entry"):
            eid = (e.findtext("{http://www.w3.org/2005/Atom}id") or "").strip()
            m = re.search(r"abs/(.+?)(?:v\d+)?$", eid)
            if not m or m.group(1) not in set(chunk):
                continue
            c = e.find("{http://arxiv.org/schemas/atom}comment")
            out[m.group(1)] = re.sub(r"\s+", " ", c.text).strip() if c is not None and c.text else ""
        time.sleep(3)
    with open(cf, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["arxiv_id", "comment"])
        w.writerows(sorted(out.items()))
    return out


gh_verified = {}
_OPENER = urllib.request.build_opener(B._NoRedirect)


def gh_exists(owner_repo, depth=0):
    """Resolve the repo page without following redirects: 200/451 exists, 404 does not,
    30x means the repository was renamed or moved, so retry the target once."""
    repo = owner_repo.strip("/").rstrip(".")
    if repo in gh_verified:
        return gh_verified[repo]
    if depth > 2 or repo.count("/") != 1:
        return ""
    url = "https://github.com/" + repo
    verdict = ""
    try:
        r = _OPENER.open(urllib.request.Request(url, headers=UA, method="GET"), timeout=30)
        verdict = url if r.status in (200, 451) else ""
        r.close()
    except urllib.error.HTTPError as e:
        loc = e.headers.get("Location") or ""
        if e.code in (301, 302, 303, 307, 308):
            m = re.search(r"github\.com/([A-Za-z0-9_.\-]+)/([A-Za-z0-9_.\-]+)", loc)
            if m:
                verdict = gh_exists(f"{m.group(1)}/{m.group(2)}", depth + 1)
        elif e.code == 451:
            verdict = url
    except Exception as err:
        sys.stderr.write(f"  probe {repo}: {type(err).__name__}\n")
    gh_verified[repo] = verdict
    time.sleep(0.4)
    return verdict


sel = list(csv.DictReader(open(OUT + "/to_add.csv", newline="", encoding="utf-8")))
meta = {r["arxiv_id"]: r for r in csv.DictReader(open(OUT + "/cand_meta.csv", newline="", encoding="utf-8"))}
oa = json.load(open(OUT + "/openalex_new.json"))
ids = [r["arxiv_id"] for r in sel]
cmt = arxiv_comments(ids)
print(f"selected={len(sel)} | comments fetched={len(cmt)} | comments non-empty="
      f"{sum(1 for v in cmt.values() if v.strip())}", flush=True)

COLS = ["arxiv_id", "citations", "journal_doi", "jref", "venue", "published", "published_host",
        "oa_pdf", "github", "github_from", "homepage", "openalex_hit"]
out = []
for s in sel:
    i = s["arxiv_id"]
    m, o = meta[i], (oa.get(i) or {})
    doi = m["doi"].strip()
    pub, phost = "", ""
    if doi and not doi.lower().startswith("10.48550"):
        phost = B.resolve_host(doi)
        pub = "https://doi.org/" + doi
        if not phost:
            pub, phost = "", ""      # DOI 解析不到真实站点就宁缺毋滥
    text = m["abstract"] + " " + cmt.get(i, "")
    gh, gh_from = "", ""
    for src_name, txt in (("abstract", m["abstract"]), ("comment", cmt.get(i, ""))):
        for mm in GH.finditer(txt):
            good = gh_exists(f"{mm.group(1)}/{mm.group(2)}")
            if good:
                gh, gh_from = good, src_name
                break
        if gh:
            break
    hp = ""
    for mm in re.finditer(r"https?://([A-Za-z0-9.\-]+)/(?:[^\s()\"']*)?", text):
        host = mm.group(1).lower()
        if re.search(r"(readthedocs\.io|github\.io|gitlab\.io|gitee\.com)$", host):
            hp = mm.group(0).rstrip('.,;)\'"')
            break
    out.append({
        "arxiv_id": i,
        "citations": "" if o.get("cited") is None else str(o["cited"]),
        "journal_doi": doi, "jref": m["journal_ref"], "venue": o.get("venue", ""),
        "published": pub, "published_host": phost,
        "oa_pdf": f"https://arxiv.org/pdf/{i}",
        "github": gh, "github_from": gh_from, "homepage": hp,
        "openalex_hit": "" if not o or o.get("missing") else "1",
    })

with open(OUT + "/new_versions.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS)
    w.writeheader(); w.writerows(out)

f = lambda k: sum(1 for x in out if (x[k] or "").strip())
from collections import Counter
print(f"wrote new_versions.csv rows={len(out)}")
print(f"  arXiv journal DOI {f('journal_doi')} | published link {f('published')} | "
      f"journal_ref {f('jref')}")
print(f"  github {f('github')} (from abstract {sum(1 for x in out if x['github_from'] == 'abstract')}, "
      f"from comment {sum(1 for x in out if x['github_from'] == 'comment')}) | homepage {f('homepage')}")
print(f"  citations filled {f('citations')} of {len(out)}")
print("  published hosts:", Counter(x["published_host"] for x in out if x["published_host"]).most_common(10))
print("  github urls:", [x["github"] for x in out if x["github"]][:10])
