#!/usr/bin/env python3
"""Verify every URL that parse_toolboxes.py pulled out of the two awesome-* READMEs.

GitHub repos go through api.github.com (stars / language / license / last push /
archived flag); everything else gets a plain HTTP GET. Results are cached in
toolbox_links.json so a re-run costs no API quota.
"""
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "toolbox_links.json")
UA = "tn-lm-toolbox-audit/1.0"
GH = re.compile(r"^https?://github\.com/([^/\s]+)/([^/\s#?]+)")

cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}


def curl_status(url):
    """-> (final_status, final_url). Follows redirects; 0 means unreachable."""
    p = subprocess.run(
        ["curl", "-4", "-sSL", "-o", "/dev/null", "--connect-timeout", "10",
         "--max-time", "30", "-w", "%{http_code}\t%{url_effective}",
         "-A", UA, url],
        capture_output=True, text=True)
    out = p.stdout.strip().split("\t")
    if len(out) != 2:
        return 0, url
    try:
        return int(out[0]), out[1]
    except ValueError:
        return 0, url


def gh_api(owner, repo):
    key = "gh:%s/%s" % (owner, repo)
    if key in cache:
        return cache[key]
    url = "https://api.github.com/repos/%s/%s" % (owner, repo)
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                              "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.load(r)
        rec = {"status": r.status, "full_name": d["full_name"],
               "stars": d.get("stargazers_count"), "forks": d.get("forks_count"),
               "language": d.get("language"), "archived": d.get("archived"),
               "pushed_at": d.get("pushed_at"), "created_at": d.get("created_at"),
               "license": (d.get("license") or {}).get("spdx_id"),
               "description": d.get("description"), "homepage": d.get("homepage"),
               "html_url": d.get("html_url"), "open_issues": d.get("open_issues_count"),
               "topics": d.get("topics") or []}
    except urllib.error.HTTPError as e:
        rec = {"status": e.code, "error": str(e)}
    except Exception as e:                                   # noqa: BLE001
        rec = {"status": 0, "error": repr(e)}
    cache[key] = rec
    json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    time.sleep(0.4)
    return rec


def gh_html(owner, repo, depth=0):
    """Scrape github.com/<owner>/<repo> HTML. Fallback for when the API quota is gone.

    Returns the same shape as gh_api() minus license/pushed_at, which the HTML
    page does not expose reliably. 'source' marks where the record came from.
    """
    key = "html:%s/%s" % (owner, repo)
    if key in cache:
        return cache[key]
    url = "https://github.com/%s/%s" % (owner, repo)
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) tn-lm-linkcheck"})
    rec = {"kind": "github", "source": "html", "full_name": "%s/%s" % (owner, repo),
           "html_url": url}
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read(3_000_000).decode("utf-8", "replace")
            rec["status"] = r.status
    except urllib.error.HTTPError as e:
        rec["status"] = e.code
        loc = e.headers.get("Location") or ""
        m = GH.match(loc)
        if e.code in (301, 302, 303, 307, 308) and m and depth < 2:
            return gh_html(m.group(1), m.group(2), depth + 1)
        body = ""
    except Exception as e:                                   # noqa: BLE001
        rec["status"], rec["error"], body = 0, repr(e), ""
    if body:
        m = re.search(r'id="repo-stars-counter-star"[^>]*?title="([\d,]+)"', body)
        if m:
            rec["stars"] = int(m.group(1).replace(",", ""))
        m = re.search(r'id="repo-network-counter"[^>]*?title="([\d,]+)"', body)
        if m:
            rec["forks"] = int(m.group(1).replace(",", ""))
        m = re.search(r'<meta property="og:description" content="([^"]*)"', body)
        if m:
            rec["description"] = (m.group(1).replace("&amp;", "&")
                                  .replace("&#39;", "'").replace("&quot;", '"'))
        langs = re.findall(r'aria-label="([A-Za-z0-9+#.\- ]+) [\d.]+"', body)
        if langs:
            rec["language"] = langs[0]
        m = re.search(r'<relative-time[^>]*datetime="(\d{4}-\d{2}-\d{2})', body)
        if m:
            rec["pushed_at"] = m.group(1)
        rec["archived"] = "This repository has been archived" in body
    cache[key] = rec
    json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    time.sleep(0.4)
    return rec


def check(url):
    key = "url:" + url
    if key in cache:
        return cache[key]
    m = GH.match(url)
    if m:
        rec = dict(gh_api(m.group(1), m.group(2)))
        rec["kind"] = "github"
        if rec.get("status") == 403:        # anonymous API quota exhausted
            rec = gh_html(m.group(1), m.group(2))
    else:
        st, final = curl_status(url)
        rec = {"kind": "web", "status": st, "final_url": final}
    cache[key] = rec
    json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    time.sleep(0.3)
    return rec


def api_available():
    try:
        req = urllib.request.Request("https://api.github.com/rate_limit",
                                     headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r)["resources"]["core"]["remaining"] > 25
    except Exception:                                        # noqa: BLE001
        return False


def purge_rate_limited():
    """Drop cached 403s so the HTML fallback actually runs on a re-run."""
    gone = [k for k, v in cache.items()
            if isinstance(v, dict) and v.get("status") == 403 and v.get("kind") == "github"]
    gone += [k for k, v in cache.items() if k.startswith("gh:") and v.get("status") == 403]
    # earlier runs treated .../tree/<branch> URLs as plain web; re-check them as repos
    gone += [k for k, v in cache.items()
             if k.startswith("url:https://github.com/") and v.get("kind") == "web"]
    if api_available():
        # HTML records lack license/pushed_at; upgrade them now that quota is back
        gone += [k for k, v in cache.items() if v.get("source") == "html"]
    for k in gone:
        cache.pop(k, None)
    if gone:
        json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return len(gone)


def main():
    print("purged %d rate-limited cache entries" % purge_rate_limited())
    rows = json.load(open(os.path.join(HERE, "toolbox_src.json"), encoding="utf-8"))
    urls = sorted({l["url"] for r in rows for l in r["links"]})
    print("checking %d urls" % len(urls))
    for u in urls:
        r = check(u)
        if r.get("kind") == "github":
            note = ""
            if r.get("full_name") and r["full_name"] not in u:
                note = "  RENAMED->" + r["full_name"]
            if r.get("source") == "html":
                note += "  [html]"
            print("  %-3s %-12s %-52s ★%-6s %-10s push %s%s" % (
                r.get("status"), r.get("license") or "-", r.get("full_name") or u,
                r.get("stars"), r.get("language") or "-", (r.get("pushed_at") or "")[:10], note))
        else:
            red = "" if r.get("final_url", u) == u else "  ->" + r["final_url"]
            print("  %-3s web   %-52s%s" % (r.get("status"), u, red))
    bad = [u for u in urls if check(u).get("status") not in (200, 301, 302, 451)]
    print("\nnot-200:", len(bad))
    for b in bad:
        print("   ", b, check(b).get("status"))


if __name__ == "__main__":
    main()
