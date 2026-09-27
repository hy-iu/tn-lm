#!/usr/bin/env python3
"""Download full-text PDFs for the rows just merged into bibliography.csv.

Filenames follow download.py's convention (year_<first 50 chars of the sanitized
title>.pdf) because that is the name gen_library.py:fname() looks for first.
Writes lit/audit/pdf_add_log.csv and is safe to re-run: existing files over 20 KB
are skipped, so a second pass only retries the failures.
"""
import csv, os, re, subprocess, time

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
PAPERS = LIT + "/papers"
TODAY = "2026-09-26"
MIN_OK = 20 * 1024


def safe_name(t):
    return re.sub(r"[^A-Za-z0-9]+", "_", str(t))[:60].strip("_") or "paper"


rows = [r for r in csv.DictReader(open(LIT + "/bibliography.csv", newline="", encoding="utf-8"))
        if (r["search_time"] or "").startswith(TODAY) and (r["arxiv_id"] or "").strip()]
print("rows to fetch:", len(rows))

log_path = LIT + "/audit/pdf_add_log.csv"
prev = {}
if os.path.exists(log_path):
    prev = {r["arxiv_id"]: r for r in csv.DictReader(open(log_path, newline=""))}

recs = []
for n, r in enumerate(rows, 1):
    aid, yr = r["arxiv_id"].strip(), re.sub(r"\D", "", str(r["year"]))[:4] or "nd"
    dst = os.path.join(PAPERS, f"{yr}_{safe_name(r['title'])[:50]}.pdf")
    if os.path.exists(dst) and os.path.getsize(dst) > MIN_OK:
        recs.append({"arxiv_id": aid, "file": os.path.basename(dst), "http": "cached",
                     "bytes": str(os.path.getsize(dst)), "ok": "1"})
        continue
    tmp = dst + ".part"
    # -4 是必需的：本机到 arxiv.org 的 IPv6 通路被限速，实测同一个 PDF
    # 走 IPv4 4.1s 拿满 4.59MB，走默认（IPv6）25s 只到 502KB。download.py 也带 -4。
    p = subprocess.run(["curl", "-4", "-sSL", "--connect-timeout", "10", "--max-time", "90",
                        "-w", "%{http_code} %{size_download}",
                        "-o", tmp, "https://arxiv.org/pdf/" + aid], capture_output=True, text=True)
    code, size = (p.stdout.strip().split() + ["0"])[:2]
    size = int(float(size or 0))
    good = code == "200" and size > MIN_OK
    if good:
        os.replace(tmp, dst)
    elif os.path.exists(tmp):
        os.remove(tmp)
    recs.append({"arxiv_id": aid, "file": os.path.basename(dst), "http": code,
                 "bytes": str(size), "ok": "1" if good else "0"})
    if n % 20 == 0 or not good:
        print(f"  {n}/{len(rows)} {aid} http={code} bytes={size} ok={good}", flush=True)
    time.sleep(1.0)

merged = dict(prev)
for x in recs:
    merged[x["arxiv_id"]] = x
with open(log_path, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["arxiv_id", "file", "http", "bytes", "ok"])
    w.writeheader()
    w.writerows([merged[k] for k in sorted(merged)])
ok = sum(1 for x in merged.values() if x["ok"] == "1")
print(f"done: {ok}/{len(merged)} pdfs present; log -> {log_path}")
