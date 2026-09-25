#!/usr/bin/env python3
"""Download every reachable PDF from bibliography.csv into lit/papers/.
Resume-safe: skips files that already exist. Writes download log after each batch."""
import ast, os, re, subprocess, sys, time
import pandas as pd

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
PDF_DIR = os.path.join(LIT, "papers")
LOG = os.path.join(LIT, "download_log.csv")
os.makedirs(PDF_DIR, exist_ok=True)

BIB = pd.read_csv(os.path.join(LIT, "bibliography.csv"))
BIB["all_pdfs"] = BIB["all_pdfs"].apply(
    lambda s: ast.literal_eval(s) if isinstance(s, str) and s.startswith("[") else [])

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")

def safe_name(t):
    t = re.sub(r"[^A-Za-z0-9]+", "_", str(t))[:60].strip("_")
    return t or "paper"

def fname(row):
    yr = int(row["year"]) if pd.notna(row["year"]) else "nd"
    if isinstance(row.get("arxiv_id"), str) and row["arxiv_id"]:
        return f"{yr}_arxiv_{row['arxiv_id']}.pdf"
    return f"{yr}_{safe_name(row['title'])[:50]}.pdf"

log = []
if os.path.exists(LOG):
    done = pd.read_csv(LOG)
    done_files = set(done.loc[done.status == "ok", "file"])
else:
    done_files = set()

start, end = int(sys.argv[1]), int(sys.argv[2])
log = []
if os.path.exists(LOG):
    done = pd.read_csv(LOG)
    done_files = set(done.loc[done.status == "ok", "file"])
else:
    done_files = set()

n_ok = n_fail = n_skip = 0

for i in range(start, min(end, len(BIB))):
    row = BIB.iloc[i]
    f = fname(row)
    path = os.path.join(PDF_DIR, f)
    if f in done_files or os.path.exists(path):
        n_skip += 1
        continue
    ok = False
    for link in row["all_pdfs"]:
        for attempt in range(1):
            tmp = path + ".part"
            rc = subprocess.run(
                ["curl", "-4", "-sS", "-L", "-m", "30", "--connect-timeout", "10",
                 "-A", UA, "-o", tmp, link],
                capture_output=True, text=True).returncode
            if rc == 0 and os.path.exists(tmp) and os.path.getsize(tmp) > 10000:
                with open(tmp, "rb") as fh:
                    head = fh.read(4)
                if head == b"%PDF":
                    os.replace(tmp, path)
                    log.append({"idx": i, "file": f, "status": "ok",
                                "source": link, "bytes": os.path.getsize(path)})
                    ok = True
                    break
            if os.path.exists(tmp):
                os.remove(tmp)
            time.sleep(1.5 * (attempt + 1))
        if ok:
            break
        time.sleep(0.6)
    if not ok:
        log.append({"idx": i, "file": f, "status": "fail",
                    "source": ";".join(row["all_pdfs"])[:200], "bytes": 0})
    n_ok += ok
    n_fail += (not ok)
    time.sleep(0.4)

if log:
    pd.DataFrame(log).to_csv(LOG, mode="a", header=not os.path.exists(LOG), index=False)
print(f"batch [{start},{end}): ok={n_ok} fail={n_fail} skip={n_skip}")
