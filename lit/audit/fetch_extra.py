#!/usr/bin/env python3
"""Fetch GitHub metadata for the off-list toolboxes named in toolbox_extra.csv.

Reuses verify_toolboxes.check(), so every record lands in toolbox_links.json under the
same "url:https://github.com/<owner>/<repo>" key shape that gen_toolboxes.py already
reads -- the extras need no separate metadata file. The hand-written part stays in the
CSV (which repo, which group, why); stars / license / last push come from the API.
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verify_toolboxes as vt  # noqa: E402

GROUP = {"engine": "清单外引擎", "einsum": "einsum 引擎"}


def main():
    rows = list(csv.DictReader(open(os.path.join(HERE, "toolbox_extra.csv"),
                                    encoding="utf-8")))
    bad = []
    for r in rows:
        repo = r["repo"].strip()
        rec = vt.check("https://github.com/" + repo)
        g = GROUP[r["group"]]
        if rec.get("status") != 200 or not rec.get("stars"):
            bad.append(repo)
            print("%-42s %-14s STATUS %s %s" % (repo, g, rec.get("status"),
                                                rec.get("error", "")))
            continue
        lic = rec.get("license") or "-"
        print("%-42s %-14s %-6s ★%-6s %-14s %-9s pushed %s  %s" % (
            repo, g, (rec.get("language") or "-")[:12], rec.get("stars"),
            (rec.get("pushed_at") or "")[:10], lic[:9],
            (rec.get("pushed_at") or "")[:10],
            "archived" if rec.get("archived") else ""))
    print("\nrows=%d  取数失败=%d  %s" % (len(rows), len(bad), " ".join(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
