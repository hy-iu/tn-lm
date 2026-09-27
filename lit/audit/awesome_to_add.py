#!/usr/bin/env python3
"""Turn the awesome-list gaps into merge-ready rows.

Second chance for entries resolve_awesome could not identify: an arXiv title query using
the FULL title (the first pass truncated at 110 chars), then a Crossref title query.

For everything the corpus lacks, append three aligned rows -- cand_meta.csv (metadata),
new_versions.csv (version links), to_add.csv (the work list, rule 'W') -- then re-run
merge_add.py unchanged. It skips rows already present and inserts only the new ones.
"""
import csv, json, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
OUT = LIT + "/audit"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) tn-lm-awesome-add",
      "Accept": "application/json"}
TAG = re.compile(r"<[^>]+>")
# The terminator class must include the quote that closes a JSON string: OpenAlex keeps
# the preprint URL as "http://arxiv.org/abs/1906.06196", and without " here the arXiv id
# was silently never extracted.
ARX = re.compile(r"arxiv\.org/(?:abs|pdf)/([\w.\-]+?)(?:v\d+)?(?:$|[?#/\"\\])")
NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
sys.path.insert(0, OUT)
import ghverify                      # noqa: E402
import build_versions as B            # noqa: E402
from scan_abstracts import sq         # noqa: E402


def get(url, tries=2):
    for a in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=50).read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(3)
        except Exception:
            time.sleep(3)
    return None


def arxiv_title(t):
    d = get("http://export.arxiv.org/api/query?search_query=ti:"
            + urllib.parse.quote('"%s"' % re.sub(r"\s+", " ", t).strip()) + "&max_results=6")
    if not d:
        return ""
    for e in ET.fromstring(d).findall("a:entry", NS):
        tt = re.sub(r"\s+", " ", e.findtext("a:title", default="", namespaces=NS)).strip()
        i = re.search(r"abs/(.+?)(?:v\d+)?$", e.findtext("a:id", default="", namespaces=NS))
        if i and sq(tt) == sq(t):
            return i.group(1)
    return ""


def crossref_title(t):
    d = get("https://api.crossref.org/works?query.title=" + urllib.parse.quote(t[:200]) + "&rows=4")
    if not d:
        return None
    try:
        items = json.loads(d).get("message", {}).get("items", [])
    except Exception:
        return None
    et = sq(t)
    for it in items:
        ct = sq((it.get("title") or [""])[0])
        if not ct or (ct != et and not (ct.startswith(et[:25]) or et.startswith(ct[:25]))):
            continue
        yr = ((it.get("published-print") or it.get("published-online") or {}).get("date-parts", [[None]])[0][0])
        return {"doi": (it.get("DOI") or "").lower(), "title": (it.get("title") or [""])[0],
                "venue": (it.get("container-title") or [""])[0], "year": str(yr or ""),
                "cited": it.get("is-referenced-by-count"),
                "abstract": re.sub(r"\s+", " ", TAG.sub(" ", it.get("abstract") or "")).strip()}
    return None


def openalex_work(doi):
    d = get("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi.lower(), safe="")
            + "?mailto=audit@example.org")
    if not d:
        return {}
    w = json.loads(d)
    am = ARX.search(json.dumps(w.get("locations") or []))
    inv = w.get("abstract_inverted_index") or {}
    pos = {k: wd for wd, ix in inv.items() for k in ix}
    return {"doi": (w.get("doi") or "").replace("https://doi.org/", "").lower(),
            "arxiv_id": am.group(1) if am else "", "title": w.get("title") or "",
            "abstract": re.sub(r"\s+", " ", " ".join(pos[k] for k in sorted(pos))).strip(),
            "year": (w.get("publication_date") or "")[:4], "cited": w.get("cited_by_count"),
            "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or "",
            "authors": ", ".join((a.get("author") or {}).get("display_name") or ""
                                 for a in (w.get("authorships") or [])[:8])}


def arxiv_meta(ids):
    out = {}
    for k in range(0, len(ids), 40):
        ch = ids[k:k + 40]
        d = get("http://export.arxiv.org/api/query?id_list="
                + urllib.parse.quote(",".join(ch), safe=",") + "&max_results=%d" % (len(ch) * 3))
        if not d:
            continue
        for e in ET.fromstring(d).findall("a:entry", NS):
            eid = (e.findtext("a:id", default="", namespaces=NS) or "").strip()
            m = re.search(r"abs/(.+?)(?:v\d+)?$", eid)
            if not m or m.group(1) not in ch:
                continue

            def tg(tag, ns="x"):
                x = e.find(f"{ns and 'x:' or ''}{tag}".replace("x:", "{http://arxiv.org/schemas/atom}"), NS)
                return re.sub(r"\s+", " ", x.text).strip() if x is not None and x.text else ""
            dd = e.find("{http://arxiv.org/schemas/atom}doi")
            pc = e.find("{http://arxiv.org/schemas/atom}primary_category")
            out[m.group(1)] = {
                "arxiv_id": m.group(1),
                "title": re.sub(r"\s+", " ", e.findtext("a:title", default="", namespaces=NS)).strip(),
                "authors": ", ".join(x.findtext("a:name", default="", namespaces=NS)
                                      for x in e.findall("a:author", NS)),
                "year": (e.findtext("a:published", default="", namespaces=NS) or "")[:4],
                "published": e.findtext("a:published", default="", namespaces=NS) or "",
                "updated": e.findtext("a:updated", default="", namespaces=NS) or "",
                "abstract": re.sub(r"\s+", " ", e.findtext("a:summary", default="", namespaces=NS)).strip(),
                "doi": (dd.text or "").strip() if dd is not None else "",
                "journal_ref": tg("journal_ref"), "primary": pc.get("term") if pc is not None else "",
                "categories": ",".join(c.get("term") for c in e.findall("a:category", NS)),
                "versions": (re.search(r"v(\d+)$", eid) or ["", "1"])[1] if re.search(r"v(\d+)$", eid) else "1",
                "comment": tg("comment")}
        time.sleep(3)
    return out
