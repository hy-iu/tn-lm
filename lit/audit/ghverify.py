#!/usr/bin/env python3
"""Shared helper: confirm a github.com/<owner>/<repo> URL really resolves.

api.github.com is unusable here (60 requests/hour anonymous quota), and a 403 is not
evidence of absence, so this probes the human-facing URL instead and follows
renames/moves manually.
"""
import re
import time
import urllib.error
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) tn-lm-linkcheck"}
GH = re.compile(r"github\.com/([A-Za-z0-9_.\-]+)/([A-Za-z0-9_.\-]+)")
_cache = {}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def gh_exists(owner_repo, depth=0):
    repo = str(owner_repo).strip("/").rstrip(".")
    m = GH.search(repo)
    if m:
        repo = f"{m.group(1)}/{m.group(2)}"
    if repo in _cache:
        return _cache[repo]
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
            m2 = GH.search(loc)
            if m2:
                verdict = gh_exists(f"{m2.group(1)}/{m2.group(2)}", depth + 1) or url
        elif e.code == 451:
            verdict = url
    except Exception:
        verdict = ""
    _cache[repo] = verdict
    time.sleep(0.35)
    return verdict


def first_repo(text):
    """First github.com owner/repo in *text* that resolves; '' if none."""
    for m in GH.finditer(text or ""):
        good = gh_exists(f"{m.group(1)}/{m.group(2)}")
        if good:
            return good
    return ""
