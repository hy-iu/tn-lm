#!/usr/bin/env python3
"""Aggregate scholar CSVs: dedupe, normalize years, extract arXiv IDs / PDF links."""
import ast, glob, os, re
import pandas as pd

CSV_DIR = "/Users/bjergsen/Documents/GitHub/tn-lm/lit/csv"
OUT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"

CLUSTER = {
    "q01_mps_lm": "MPS 语言模型", "q02_tn_seq": "MPS/序列建模",
    "q03_tt_nn": "MPO/TT 压缩", "q04_tn_llm": "MPO/TT 压缩",
    "q05_born": "MPS 生成/Born机", "q06_mi": "互信息/标度",
    "q07_qiml_review": "量子启发综述", "q08_ttn": "TTN/MERA/PEPS",
    "q09_qllm": "量子/混合LLM", "q10_tt_tf": "张量化Transformer",
    "q11_peps": "TTN/MERA/PEPS", "q12_ent_lang": "互信息/标度",
}

def norm_title(t):
    t = re.sub(r"[^a-z0-9]+", " ", str(t).lower()).strip()
    return t

def parse_links(s):
    if not isinstance(s, str) or not s.strip():
        return []
    try:
        v = ast.literal_eval(s)
        return v if isinstance(v, list) else [str(v)]
    except Exception:
        return [x.strip() for x in re.findall(r"https?://[^\s'\]\",]+", s)]

rows = []
for f in sorted(glob.glob(os.path.join(CSV_DIR, "q*.csv"))):
    key = os.path.basename(f).split("_")[0]
    cluster = CLUSTER.get(os.path.basename(f).replace(".csv", ""), "其他")
    try:
        df = pd.read_csv(f)
    except Exception as e:
        print("skip", f, e)
        continue
    df["cluster"] = cluster
    df["query"] = key
    rows.append(df)

all_df = pd.concat(rows, ignore_index=True)
print("raw rows:", len(all_df))

# normalize year
def get_year(v):
    m = re.search(r"(19|20)\d{2}", str(v))
    return int(m.group(0)) if m else None

all_df["year"] = all_df["year"].apply(get_year)

def arxiv_id(url):
    if not isinstance(url, str):
        return None
    m = re.search(r"arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5})", url)
    return m.group(1) if m else None

all_df["arxiv_id"] = all_df["url"].apply(arxiv_id)

# collect pdf links (any source) per row
all_df["pdf_links_parsed"] = all_df["pdf_links"].apply(parse_links)
all_df["all_pdfs"] = all_df.apply(
    lambda r: list(dict.fromkeys(r["pdf_links_parsed"])), axis=1)

# dedupe by normalized title; keep first occurrence but merge clusters
all_df["ntitle"] = all_df["title"].apply(norm_title)
all_df = all_df[all_df["ntitle"].str.len() > 5]

merged = []
for nt, g in all_df.groupby("ntitle"):
    best = g.sort_values("citations", ascending=False, na_position="last").iloc[0].copy()
    best["clusters"] = " / ".join(sorted(set(g["cluster"])))
    best["n_hits"] = len(g)
    # merge pdfs across duplicates
    pdfs = []
    for _, r in g.iterrows():
        pdfs.extend(r["all_pdfs"])
    best["all_pdfs"] = list(dict.fromkeys(pdfs))
    merged.append(best)

m = pd.DataFrame(merged).drop(columns=["pdf_links_parsed", "query"])
m = m.sort_values(["year", "citations"], ascending=[True, False], na_position="last")
print("unique papers:", len(m))
print(m["year"].value_counts().sort_index().to_string())

m.to_csv(os.path.join(OUT, "bibliography.csv"), index=False)
print("saved", os.path.join(OUT, "bibliography.csv"))
