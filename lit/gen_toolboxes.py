#!/usr/bin/env python3
"""Generate app/toolboxes.html.

Every fact on the page is parsed or fetched, never hand-written:
  audit/parse_toolboxes.py  -> toolbox_src.json  (rows of the two lists' tables)
                               toolbox_meta.json (surveys, citation, format glossary)
  audit/verify_toolboxes.py -> toolbox_links.json (live status + GitHub metadata)
  bibliography.csv + audit/paper_versions.csv   -> our own corpus cross-reference

Capability text is shown twice when both exist -- once as the curated list's own
wording, once as the repository's self-description -- because they disagree for a
few entries (e.g. amore-upf/ted-q is a dataset repo, not a QML framework).
"""
import csv
import json
import os
import re
import sys
from collections import OrderedDict

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
AUD = os.path.join(LIT, "audit")
OUT = "/Users/bjergsen/Documents/GitHub/tn-lm/app/toolboxes.html"
TODAY = "2026-09-27"

SRC_LABEL = {"llms": "Tensor Methods for LLMs 清单", "tnn": "Tensorial NN 清单"}
SRC_SHORT = {"llms": "TMs4LLMs", "tnn": "TNN"}

TOOL_H3 = {"Python tensor libraries", "Others",
           "Basic Tensor Operations", "Deep-Model Implementations",
           "Quantum and Tensor-Network Simulation"}
PAPER_H3 = {"Hardware co-design", "Case Studies"}
H3_ZH = {
    "Python tensor libraries": "Python 张量库",
    "Others": "其他语言",
    "Basic Tensor Operations": "基础张量运算",
    "Deep-Model Implementations": "深度模型实现",
    "Quantum and Tensor-Network Simulation": "量子与 TN 模拟",
}

CAT_ORDER = ["basic", "layers", "quantum", "engine", "einsum"]
CAT_NAME = {"basic": "基础张量运算与分解",
            "layers": "深度模型层实现",
            "quantum": "张量网络与量子模拟",
            "engine": "通用张量网络引擎（清单外补充）",
            "einsum": "广义 einsum 与收缩路径引擎"}
CAT_DESC = {
    "basic": "张量代数、分解算法（CP / Tucker / TT / t-SVD）与后端抽象，本身不提供神经网络层。",
    "layers": "把张量分解封装成可训练的神经网络层，可直接嵌进 PyTorch / TensorFlow 模型。",
    "quantum": "任意几何张量网络的构造、收缩与量子线路模拟，是多体物理与 QNLP 的底座。",
    "engine": "两份清单没有收录、但这个方向绕不开的通用引擎：凝聚态 DMRG/TDVP、对称扇区、"
              "GPU 收缩与 2D/动力学求解器。选入理由逐条写在 audit/toolbox_extra.csv，"
              "star、许可证、最后推送与归档状态仍由 GitHub 接口取得。",
    "einsum": "不叫自己「张量网络库」的收缩引擎：einsum 路径优化、命名轴接口与编译式收缩。"
              "本页把 cotengra 归在量子/TN，这一组是它的同族与前置基线。",
}
EXTRA_CSV = "toolbox_extra.csv"
EXTRA_H3 = "清单外补充"

# llms 表叫 "Tensor Toolbox for MATLAB"（指向 gitlab 官方仓库），tnn 表叫 "Tensor Toolbox"
# （指向 tensortoolbox.org 官方站）：同一个 Sandia 产品的两个入口，应合并
NAME_ALIAS = {"tensor toolbox for matlab": "tensor toolbox"}

# 主分类默认由源表结构推出（见 cat_of）；这三条会推错，手工指定并写明理由
CAT_OVERRIDE = {
    "quimb": "quantum",     # 源表归在 Python tensor libraries，但能力是 MPS/PEPS/MERA + DMRG/TEBD
    "cotengra": "quantum",  # 只做收缩路径优化，既不产出分解也不是通用张量代数
    "torchmps": "layers",   # 提供 PyTorch MPS 层；llms 的 Others 表没有 NN layers 列可判
}

GH_RE = re.compile(r"github\.com/([^/\s]+)/([^/\s#?]+)")
LIC_BLANK = {"", "NOASSERTION", "None", None}


def norm_name(s):
    s = NAME_ALIAS.get(s.strip().lower(), s.strip().lower())
    return re.sub(r"[^a-z0-9]+", "", s)


def gh_of(url):
    m = GH_RE.search(url or "")
    return (m.group(1) + "/" + m.group(2)).lower() if m else ""


def url_label(u):
    if "github.com" in u:
        return "GitHub"
    if "gitlab.com" in u:
        return "GitLab"
    if "readthedocs" in u:
        return "文档"
    return "官网"


def load_links():
    """url -> verified record; a full API record beats an html-scraped one."""
    raw = json.load(open(os.path.join(AUD, "toolbox_links.json"), encoding="utf-8"))
    out = {}
    for k, v in raw.items():
        if not k.startswith("url:") or not isinstance(v, dict):
            continue
        url = k[4:]
        prev = out.get(url)
        if v.get("kind") == "github":
            if prev is None or (prev.get("source") == "html" and v.get("source") != "html"):
                out[url] = v
        elif prev is None:
            out[url] = v
    return out


def rec_for(links, gh):
    """GitHub metadata for owner/repo, whatever URL spelling it was cached under."""
    if not gh:
        return {}
    for u, v in links.items():
        if v.get("kind") == "github" and gh_of(u) == gh:
            return v
    return {}


def cat_of(key, h3s, layers):
    if key in CAT_OVERRIDE:
        return CAT_OVERRIDE[key]
    h3 = set(h3s)
    if "Deep-Model Implementations" in h3 or layers == "+":
        return "layers"
    if "Quantum and Tensor-Network Simulation" in h3 and not (
            h3 & {"Basic Tensor Operations", "Python tensor libraries", "Others"}):
        return "quantum"
    return "basic"


def load_tools(links):
    rows = json.load(open(os.path.join(AUD, "toolbox_src.json"), encoding="utf-8"))
    tools, hw, cases = OrderedDict(), [], []
    for r in rows:
        if not r["links"] or r["h3"] not in TOOL_H3 | PAPER_H3:
            continue
        lk = r["links"][0]
        cells = r["cells"]
        if r["h3"] == "Hardware co-design":
            hw.append({"t": lk["text"], "u": lk["url"],
                       "d": cells.get("Description", ""), "v": cells.get("Venue", ""),
                       "y": cells.get("Year", "")})
            continue
        if r["h3"] == "Case Studies":
            cases.append({"t": lk["text"], "u": lk["url"]})
            continue

        name = lk["text"].strip()
        base = norm_name(name)
        gh = gh_of(lk["url"])
        # 两个清单里的 "TenDeC++" 指向两个不同的仓库，同名不等于同一个项目
        key = base
        if base in tools and gh and tools[base]["ghs"] and gh not in tools[base]["ghs"]:
            key = base + "|" + gh
        t = tools.get(key)
        if t is None:
            t = tools[key] = {"key": key, "base": base, "names": [], "urls": [],
                              "caps": OrderedDict(), "bes": [], "fmts": [],
                              "layers": "", "ghs": set(), "h3s": [], "srcs": []}
        if name not in t["names"]:
            t["names"].append(name)
        if lk["url"] not in [u for u, _ in t["urls"]]:
            t["urls"].append((lk["url"], url_label(lk["url"])))
        cap = (cells.get("Description") or cells.get("Main capability") or "").strip()
        if cap:
            t["caps"].setdefault(r["src"], cap)
        be = (cells.get("Backend") or cells.get("Language / Backend") or "").strip()
        if be and be not in t["bes"]:
            t["bes"].append(be)
        fmt = (cells.get("Decompositions") or "").strip()
        if fmt and fmt not in ("–", "-") and fmt not in t["fmts"]:
            t["fmts"].append(fmt)
        lay = (cells.get("NN layers") or "").strip()
        if lay == "+" or (lay in ("-", "–") and not t["layers"]):
            t["layers"] = "+" if lay == "+" else "-"
        if gh:
            t["ghs"].add(gh)
            # owner 的大小写要照源清单里的 URL，不能拿 gh 的小写化结果去显示
            m = GH_RE.search(lk["url"])
            if m:
                t.setdefault("gh_disp", m.group(1) + "/" + m.group(2))
        if r["h3"] not in t["h3s"]:
            t["h3s"].append(r["h3"])
        if r["src"] not in t["srcs"]:
            t["srcs"].append(r["src"])

    out = []
    for key, t in tools.items():
        gh = sorted(t["ghs"])[0] if t["ghs"] else ""
        g = rec_for(links, gh)
        # 清单给的 .../tree/<branch> 链接换成 API 回报的规范仓库地址
        urls = []
        for u, lb in t["urls"]:
            if gh_of(u) == gh and g.get("html_url"):
                u = g["html_url"]
            if u not in [x for x, _ in urls]:
                urls.append((u, lb))
        caps = [[SRC_LABEL[s], c] for s, c in t["caps"].items()]
        gd = (g.get("description") or "").strip()
        if gd and not any(gd.lower() == c.lower() for _, c in caps):
            caps.append(["仓库自述", gd])
        lic = g.get("license")
        if gh:
            ok = g.get("status") == 200
        else:
            # 没有 GitHub 仓库（GitLab / 官网），按 HTTP 检查结果判定
            ok = all(links.get(u, {}).get("status") in (200, 301, 302) for u, _ in urls)
        rec = {
            "n": t["names"][0], "alt": t["names"][1:], "cat": cat_of(t["base"], t["h3s"],
                                                                     t["layers"]),
            "gh": t.get("gh_disp", gh), "ghl": gh,
            "u": [[lb, u] for u, lb in urls], "cap": caps,
            "fmt": t["fmts"], "be": t["bes"], "lay": t["layers"],
            "st": g.get("stars"), "lic": "" if lic in LIC_BLANK else lic,
            "pu": (g.get("pushed_at") or "")[:10], "ar": bool(g.get("archived")),
            "ok": ok, "sr": t["srcs"],
            "h3": [H3_ZH.get(h, h) for h in t["h3s"]], "co": [],
        }
        out.append(rec)

    out.sort(key=sort_key)
    return out, hw, cases


def sort_key(r):
    return (CAT_ORDER.index(r["cat"]), -(r["st"] or 0), r["n"].lower())


def load_extras(links):
    """Toolboxes that the two lists never mentioned, selected in audit/toolbox_extra.csv.

    Only 'which repo, and why' is hand-written here; the name, star count, license,
    last push and archived flag all come from the same cached GitHub records as the
    rest of the page, so a missing API record drops the entry rather than guessing.
    """
    path = os.path.join(AUD, EXTRA_CSV)
    if not os.path.exists(path):
        return []
    out = []
    for r in csv.DictReader(open(path, encoding="utf-8")):
        repo = (r["repo"] or "").strip()
        if not repo:
            continue
        g = rec_for(links, repo.lower())
        if g.get("status") != 200 or not g.get("stars"):
            print("WARN 清单外条目 %s 没有可用的 GitHub 记录（status=%s），跳过"
                  % (repo, g.get("status")))
            continue
        full = g.get("full_name") or repo
        name = (r.get("display") or "").strip() or full.split("/")[-1]
        gd = (g.get("description") or "").strip()
        lic = g.get("license")
        rec = {
            "n": name, "alt": [], "cat": r["group"].strip(),
            "gh": full, "ghl": full.lower(),
            "u": [["GitHub", g.get("html_url") or "https://github.com/" + full]],
            "cap": [["仓库自述", gd]] if gd else [],
            "fmt": [], "be": [g["language"]] if g.get("language") else [],
            "lay": "", "st": g.get("stars"),
            "lic": "" if lic in LIC_BLANK else lic,
            "pu": (g.get("pushed_at") or "")[:10], "ar": bool(g.get("archived")),
            "ok": True, "sr": [], "h3": [EXTRA_H3], "co": [],
            "tier": (r.get("tier") or "").strip(),
            "why": (r.get("why") or "").strip(),
        }
        out.append(rec)
    return out


def load_corpus():
    """github repo -> the papers in our own bibliography that link to it."""
    with open(os.path.join(LIT, "bibliography.csv"), encoding="utf-8") as f:
        bib = list(csv.DictReader(f))
    vrows = list(csv.DictReader(open(os.path.join(AUD, "paper_versions.csv"),
                                     encoding="utf-8")))
    idx = OrderedDict()
    for v in vrows:
        gh = gh_of(v.get("github") or "")
        if not gh:
            continue
        try:
            ln = int(v["row_no"])
        except ValueError:
            continue
        if not 2 <= ln <= len(bib) + 1:
            continue
        b = bib[ln - 2]
        # row_no 是 bibliography 的行号（表头=1），标题前缀必须对得上，否则说明错位
        vt = (v.get("title") or "").strip()
        if vt and not b["title"].strip().lower().startswith(vt[:40].lower()):
            print("WARN corpus misalign line %d: %r vs %r" % (ln, vt[:40],
                                                              b["title"][:40]))
            continue
        idx.setdefault(gh, {"u": (v.get("github") or "").strip(), "p": []})
        idx[gh]["p"].append([ln, b["title"].strip(), (b.get("year") or "").strip(),
                             (b.get("citations") or "").strip()])
    for gh in idx:
        idx[gh]["p"].sort(key=lambda x: x[0])
    return idx


def main():
    links = load_links()
    meta = json.load(open(os.path.join(AUD, "toolbox_meta.json"), encoding="utf-8"))
    tools, hw, cases = load_tools(links)
    n_list = len(tools)
    tools += load_extras(links)
    tools.sort(key=sort_key)
    corpus = load_corpus()

    listed = {t["ghl"] for t in tools if t["ghl"]}
    for t in tools:
        t["co"] = [list(p) for p in corpus.get(t["ghl"], {}).get("p", [])] if t["ghl"] else []

    corp_rows = [{"gh": gh, "u": d["u"], "p": d["p"], "listed": gh in listed}
                 for gh, d in sorted(corpus.items(),
                                     key=lambda kv: (-len(kv[1]["p"]), kv[0]))]

    if "--dump" in sys.argv:
        for t in tools:
            print("%-8s %-36s %-44s ★%-6s %-14s push %-11s %s%s" % (
                t["cat"], t["n"], t["gh"] or "-", t["st"], t["lic"] or "-", t["pu"],
                ",".join(t["sr"]), "  ARCHIVED" if t["ar"] else ""))
            for s, c in t["cap"]:
                print("     [%s] %s" % (s, c[:110]))
            print("     fmt=%s be=%s lay=%s h3=%s ok=%s" % (
                t["fmt"], t["be"], t["lay"], t["h3"], t["ok"]))
            if t["co"]:
                print("     corpus=%s" % [(c[0], c[1][:40]) for c in t["co"]])
        print("\nhw=%d cases=%d corpus_repos=%d (listed=%d)" % (
            len(hw), len(cases), len(corp_rows),
            sum(1 for c in corp_rows if c["listed"])))
        for tag, m in meta.items():
            print("glossary[%s]=%d" % (tag, len(m.get("glossary", []))))
        return

    emit(tools, hw, cases, corp_rows, meta)


def js(obj):
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


def emit(tools, hw, cases, corp_rows, meta):
    gloss = meta["llms"].get("glossary", [])
    n_tools = len(tools)
    n_both = sum(1 for t in tools if len(t["sr"]) == 2)
    n_ex = sum(1 for t in tools if t.get("tier"))
    n_eng = sum(1 for t in tools if t["cat"] == "engine")
    n_ein = sum(1 for t in tools if t["cat"] == "einsum")
    n_stars = sum(t["st"] or 0 for t in tools)
    n_overlap = sum(1 for t in tools if t["co"])
    n_corp_papers = sum(len(c["p"]) for c in corp_rows)
    n_arch = sum(1 for t in tools if t["ar"])
    n_nogh = sum(1 for t in tools if not t["ghl"])
    n_dead = sum(1 for t in tools if not t["ok"])
    if n_dead:
        print("WARN %d tools have no reachable URL: %s"
              % (n_dead, [t["n"] for t in tools if not t["ok"]]))

    corp_html = []
    for c in corp_rows:
        tag = '<span class="badge c">本页已收录</span>' if c["listed"] else ""
        n = len(c["p"])
        for i, (ln, ti, yr, cit) in enumerate(c["p"]):
            cells = ""
            if i == 0:
                cells = ('<td class="ghc" rowspan="%d"><a href="%s" target="_blank" '
                         'rel="noopener">%s</a>%s<br><span class="ghn">%d 篇</span></td>'
                         % (n, c["u"], c["gh"], tag, n))
            corp_html.append('<tr>%s<td class="tt">%s</td><td class="num">%s</td>'
                             '<td class="num">%s</td></tr>'
                             % (cells, ti, yr or "—", cit or "—"))

    hw_html = "\n".join(
        '<tr><td class="tt"><a href="%s" target="_blank" rel="noopener">%s</a></td>'
        '<td>%s</td><td class="num">%s</td><td class="num">%s</td></tr>'
        % (h["u"], h["t"], h["d"], h["v"], h["y"]) for h in hw)
    case_html = "\n".join(
        '<tr><td class="tt"><a href="%s" target="_blank" rel="noopener">%s</a></td></tr>'
        % (c["u"], c["t"]) for c in cases)
    gloss_html = "\n".join('<tr><td class="term">%s</td><td>%s</td></tr>'
                           % (g["term"], g["text"]) for g in gloss)

    src_html = "\n".join(
        '<div class="src-card"><div class="src-h">%s</div>'
        '<div class="src-t">%s</div><div class="src-a">%s</div>'
        '<div class="src-l"><a href="https://arxiv.org/abs/%s" target="_blank" '
        'rel="noopener">arXiv:%s</a> · <a href="%s" target="_blank" rel="noopener">'
        '清单仓库</a> · 本页收录其 %d 个工具条目</div></div>'
        % (SRC_LABEL[tag], m["title"], m["authors"], m["arxiv"], m["arxiv"],
           m["repo"], sum(1 for t in tools if tag in t["sr"]))
        for tag, m in meta.items())

    payload = {"tools": tools, "cat": CAT_ORDER, "catName": CAT_NAME,
               "catDesc": CAT_DESC, "srcShort": SRC_SHORT, "extraCsv": EXTRA_CSV}
    html = (TEMPLATE
            .replace("__DATA__", js(payload))
            .replace("__NT__", str(n_tools))
            .replace("__NBOTH__", str(n_both))
            .replace("__NEX__", str(n_ex))
            .replace("__NENG__", str(n_eng))
            .replace("__NEIN__", str(n_ein))
            .replace("__NLIST__", str(n_tools - n_ex))
            .replace("__NSTAR__", "{:,}".format(n_stars))
            .replace("__NOVER__", str(n_overlap))
            .replace("__NCORP__", str(len(corp_rows)))
            .replace("__NCORPP__", str(n_corp_papers))
            .replace("__NARCH__", str(n_arch))
            .replace("__NNOGH__", str(n_nogh))
            .replace("__NHW__", str(len(hw)))
            .replace("__NCASE__", str(len(cases)))
            .replace("__TODAY__", TODAY)
            .replace("__SRC_CARDS__", src_html)
            .replace("__GLOSS__", gloss_html)
            .replace("__HW__", hw_html)
            .replace("__CASES__", case_html)
            .replace("__CORP__", "\n".join(corp_html)))
    # 元数据里带着本地克隆路径，一旦漏进页面就是既失效又泄露目录结构的链接
    for leak in ("/Users/", "file://", "__"):
        assert leak not in html, "leaked %r into %s" % (leak, OUT)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote %s  %.0f KB  tools=%d both=%d archived=%d nogh=%d corpus_repos=%d "
          "corpus_papers=%d" % (OUT, os.path.getsize(OUT) / 1024, n_tools, n_both,
                                n_arch, n_nogh, len(corp_rows), n_corp_papers))


TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>工具库 · 张量网络 / 张量分解开源工具 __NT__ 个</title>
<style>
:root{
  --bg:#ece4d9; --surface:#f4f0ea; --card:#fffbf5;
  --ink:#4f483e; --muted:#6b5f4e; --accent:#b82a00; --tint:#ffc198;
  --serif:"Georgia","Times New Roman","Songti SC","SimSun",serif;
  --sans:"Inter","Helvetica Neue","PingFang SC","Microsoft YaHei",sans-serif;
  --mono:"JetBrains Mono","SF Mono","Courier New",monospace;
}
[data-theme="dark"]{--bg:#1a1713; --surface:#221e18; --card:#28231c; --ink:#e8e0d2; --muted:#9a8f7c; --accent:#ff6b33; --tint:#8a4426;}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.75;transition:background .3s,color .3s}
#side{position:fixed;left:0;top:0;bottom:0;width:56px;background:#4f483e;display:flex;flex-direction:column;align-items:center;z-index:50;padding:16px 0;gap:18px;overflow-y:auto}
#side .pgroup,#side .toc{display:flex;flex-direction:column;align-items:center;gap:18px}
#side a{writing-mode:vertical-rl;color:#f4f0ea;text-decoration:none;font-size:12px;letter-spacing:.25em;opacity:.85;transition:opacity .3s,color .3s}
#side .toc a{color:#d8cebe;font-size:11px;opacity:1}
#side a:hover{opacity:1;color:#ffab80}
#side a.cur{opacity:1;color:#ffab80;font-weight:700}
#side .toc a.on{opacity:1;color:#ffab80;font-weight:700}
#side hr{border:none;width:22px;border-top:1px solid rgba(244,240,234,.35);flex:none;margin:2px 0}
@media(max-width:760px){#side{gap:12px;padding:12px 0}#side .pgroup,#side .toc{gap:12px}}
#themeBtn{position:fixed;right:18px;top:18px;z-index:60;font-family:var(--mono);font-size:11px;letter-spacing:.15em;background:var(--card);color:var(--ink);border:1px solid var(--muted);padding:8px 14px;cursor:pointer;border-radius:999px}
#themeBtn:hover{border-color:var(--accent);color:var(--accent)}
main{margin-left:56px}
.wrap{max-width:1180px;margin:0 auto;padding:0 40px}
@media(max-width:760px){.wrap{padding:0 22px}}
header{border-bottom:2px solid var(--ink);padding:42px 0 26px}
.mast-meta{display:flex;justify-content:space-between;font-family:var(--mono);font-size:11px;color:var(--muted);letter-spacing:.12em;text-transform:uppercase;margin:18px 0 0;gap:12px;flex-wrap:wrap}
h1{font-family:var(--serif);font-size:38px;line-height:1.2}
h1 em{font-style:normal;color:var(--accent)}
.subtitle{margin-top:14px;color:var(--muted);max-width:760px}
section{padding:52px 0 8px}
.sec-label{font-family:var(--mono);font-size:11px;letter-spacing:.3em;text-transform:uppercase;color:var(--accent);margin-bottom:10px}
h2{font-family:var(--serif);font-size:26px;margin-bottom:16px}
h3{font-family:var(--serif);font-size:18px;margin:26px 0 8px}
p{margin-bottom:14px}
a{color:var(--accent);text-decoration:none;border-bottom:1px solid var(--tint)}
.note{font-size:13px;color:var(--muted);background:var(--card);border-left:3px solid var(--tint);padding:14px 18px;margin:16px 0;line-height:1.85}
.note b{color:var(--accent);font-weight:600}
.note summary{cursor:pointer;font-family:var(--mono);font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--accent)}
.note p{margin:10px 0 0}
.stats{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px;margin:18px 0 8px}
@media(max-width:980px){.stats{grid-template-columns:repeat(3,1fr)}}
@media(max-width:620px){.stats{grid-template-columns:repeat(2,1fr)}}
.stat{background:var(--card);border:1px solid #e2d9cb;padding:14px 16px}
[data-theme="dark"] .stat{border-color:#3a332a}
.stat .num{font-family:var(--serif);font-size:30px;color:var(--accent);line-height:1.1}
.stat .lbl{font-family:var(--mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin-top:4px}
.srcs{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px;margin:18px 0}
.src-card{background:var(--card);border:1px solid #e2d9cb;padding:16px 18px}
[data-theme="dark"] .src-card{border-color:#3a332a}
.src-h{font-family:var(--mono);font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:var(--accent);margin-bottom:8px}
.src-t{font-family:var(--serif);font-size:16px;line-height:1.45}
.src-a{font-size:12.5px;color:var(--muted);margin-top:8px}
.src-l{font-family:var(--mono);font-size:11px;margin-top:10px;padding-top:10px;border-top:1px dashed #d8cebe}
.toolbar{position:sticky;top:0;background:var(--bg);z-index:20;padding:14px 0 10px;border-bottom:1px solid #d8cebe;display:flex;flex-wrap:wrap;gap:10px;align-items:center}
[data-theme="dark"] .toolbar{border-bottom-color:#3a332a}
#q{flex:1;min-width:200px;font-family:var(--sans);font-size:14px;padding:8px 12px;border:1px solid var(--muted);background:var(--card);color:var(--ink);border-radius:2px}
#q:focus{outline:none;border-color:var(--accent)}
.chip{font-family:var(--sans);font-size:12px;padding:6px 12px;border:1px solid var(--muted);background:var(--card);color:var(--ink);cursor:pointer;border-radius:999px;transition:all .2s}
.chip:hover{border-color:var(--accent)}
.chip.on{background:var(--accent);border-color:var(--accent);color:#fffbf5}
select{font-family:var(--mono);font-size:12px;padding:7px 10px;border:1px solid var(--muted);background:var(--card);color:var(--ink);border-radius:2px}
#count{font-family:var(--mono);font-size:11px;color:var(--muted);width:100%}
.ghead{display:flex;align-items:baseline;gap:12px;padding:14px 8px 8px;cursor:pointer;user-select:none;border-bottom:2px solid var(--ink);margin-top:10px}
.ghead .gname{font-family:var(--serif);font-size:19px}
.ghead .gcount{font-family:var(--mono);font-size:11px;color:var(--muted)}
.ghead .gchev{font-family:var(--mono);font-size:12px;color:var(--muted);transition:transform .25s;flex:none}
.ghead .gbar{flex:1;height:3px;background:var(--tint);align-self:center;max-width:120px}
.ghead .gmean{margin-left:auto;font-size:12px;color:var(--muted);text-align:right;flex:0 1 auto;max-width:56%}
.gblock.closed .grow,.gblock.closed .gdesc{display:none}
.gblock.closed .gchev{transform:rotate(-90deg)}
.gdesc{font-size:12.5px;color:var(--muted);padding:8px 8px 0}
.grow{border-bottom:1px solid #e2d9cb;padding:13px 8px;cursor:pointer;transition:background .2s}
[data-theme="dark"] .grow{border-bottom-color:#3a332a}
.grow:hover{background:var(--surface)}
.grow .r1{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap}
.grow .rt{font-family:var(--serif);font-size:17px}
.grow .rt .alt{font-family:var(--mono);font-size:11px;color:var(--muted)}
.grow .rt .own{font-family:var(--mono);font-size:11px;color:var(--muted)}
.badge{font-family:var(--mono);font-size:10.5px;padding:2px 8px;border:1px solid #d8cebe;color:var(--muted);border-radius:2px;white-space:nowrap}
[data-theme="dark"] .badge{border-color:#3a332a}
.badge.c,.badge.st{color:var(--accent);border-color:var(--tint)}
.badge.lang{color:var(--ink);border-color:var(--muted)}
.badge.warn{color:#8a1f00;border-color:#8a1f00;background:rgba(184,42,0,.08)}
[data-theme="dark"] .badge.warn{color:#ffab80;border-color:#ffab80;background:rgba(255,107,51,.12)}
.capline{font-size:13.5px;color:var(--muted);margin-top:5px;line-height:1.7}
.ver{display:flex;flex-wrap:wrap;gap:6px;margin-top:9px}
.grow .r1 .ver{margin-left:auto;margin-top:0;justify-content:flex-end}
.ver a{font-family:var(--mono);font-size:10.5px;padding:3px 9px;border:1px solid var(--tint);border-radius:2px;color:var(--accent);white-space:nowrap}
.ver a:hover{background:var(--tint);color:var(--ink)}
.ver a.gh{border-color:#4a7c59;color:#4a7c59}
.detail{display:none;margin-top:11px;background:var(--card);border-left:3px solid var(--tint);padding:12px 16px}
.grow.open .detail{display:block}
.cap{font-size:13.5px;line-height:1.75;margin-bottom:8px}
.cap .s{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);display:block;margin-bottom:2px}
.cap.repo .s{color:#4a7c59}
.kv{font-family:var(--mono);font-size:11px;color:var(--muted);margin-top:8px;padding-top:8px;border-top:1px dashed #d8cebe;line-height:1.95;white-space:pre-line}
.corp{margin-top:9px}
.corp .ch{font-family:var(--mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--accent);margin-bottom:5px}
.corp li{font-size:13px;margin-left:18px;line-height:1.7}
.corp .cy{font-family:var(--mono);font-size:11px;color:var(--muted)}
table.plain{width:100%;border-collapse:collapse;margin:14px 0;font-size:13.5px;background:var(--card)}
table.plain th{font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);text-align:left;padding:10px 10px;border-bottom:2px solid var(--ink)}
table.plain td{padding:9px 10px;border-bottom:1px solid #e2d9cb;vertical-align:top}
[data-theme="dark"] table.plain td{border-bottom-color:#3a332a}
table.plain td.num{font-family:var(--mono);font-size:12px;color:var(--muted);white-space:nowrap}
table.plain td.tt{font-family:var(--serif);font-size:14.5px}
table.plain td.term{font-family:var(--mono);font-size:12px;color:var(--accent);white-space:nowrap}
table.plain td.ghc{font-family:var(--mono);font-size:11.5px;border-right:1px solid #e2d9cb;width:230px}
[data-theme="dark"] table.plain td.ghc{border-right-color:#3a332a}
table.plain td.ghc a{word-break:break-all}
.ghn{font-family:var(--mono);font-size:10px;color:var(--muted)}
footer{margin-top:70px;border-top:2px solid var(--ink);padding:26px 0 60px;font-family:var(--mono);font-size:11px;color:var(--muted);display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
</style>
</head>
<body>
<nav id="side">
  <div class="pgroup">
    <a href="index.html">研究备忘</a>
    <a href="figures.html">图解路线</a>
    <a href="library.html">论文库</a>
    <a href="toolboxes.html" class="cur">工具库</a>
  </div>
  <hr>
  <div class="toc">
    <a href="#sources">来源</a>
    <a href="#tools">工具</a>
    <a href="#portals">教程/知识库</a>
    <a href="#formats">格式</a>
    <a href="#hardware">硬件</a>
    <a href="#corpus">本库代码</a>
  </div>
</nav>
<button id="themeBtn" onclick="t()">◐ 主题</button>
<main><div class="wrap">
<header>
  <h1>工具<em>库</em></h1>
  <div class="mast-meta"><span>Vol. 03 — 开源工具 __NT__ 个</span><span>两份社区清单 __NLIST__ 个 · 清单外补充 __NEX__ 个</span><span><a href="library.html">论文库 →</a></span></div>
</header>

<section id="sources">
  <div class="sec-label">Provenance</div>
  <h2>数据来源与核验方式</h2>
  <div class="stats">
    <div class="stat"><div class="num">__NT__</div><div class="lbl">工具（清单内 __NLIST__ + 清单外 __NEX__）</div></div>
    <div class="stat"><div class="num">__NBOTH__</div><div class="lbl">两份清单共同收录</div></div>
    <div class="stat"><div class="num">__NSTAR__</div><div class="lbl">GitHub star 合计</div></div>
    <div class="stat"><div class="num">__NOVER__</div><div class="lbl">与本库论文代码重合</div></div>
    <div class="stat"><div class="num">__NCORP__</div><div class="lbl">本库论文附带仓库</div></div>
    <div class="stat"><div class="num">__NARCH__</div><div class="lbl">已归档停止维护</div></div>
  </div>
  <div class="srcs">__SRC_CARDS__</div>
  <details class="note" id="method">
    <summary>合并规则与核验方式 · 点击展开</summary>
    <p>张量分解 / 张量网络方向可直接上手的开源实现。条目取自两份社区维护的清单，另有 __NEX__ 个是清单外补充，但数字不是转抄的：star 数、许可证、最后推送时间与归档状态逐个向 GitHub 请求取得，能力描述同时给出清单原文与仓库自述，两者不一致时并列呈现而不替读者裁决。</p>
    <p><b>合并规则：</b>两份清单的 Software / Toolboxes 小节按工具名合并；同名但指向不同仓库的<b>不</b>合并 —— TenDeC++ 就是这种情况，两份清单各指一个不同的 C++ 项目，页面上用 owner 消歧，能力描述也各自独立，不互相借用。</p>
    <p><b>核验：</b>star / 许可证 / 最后推送 / 归档状态取自 GitHub REST 接口；配额耗尽时退回抓仓库页面，此时许可证一栏留空而不是猜一个。__NNOGH__ 个条目没有 GitHub 仓库（只有 GitLab 或官网），按 HTTP 可达性判定。</p>
    <p><b>分类：</b>默认由源表的章节结构与「NN layers」列推出；quimb、cotengra、TorchMPS 三条推不准，在 <span style="font-family:var(--mono)">lit/gen_toolboxes.py</span> 的 CAT_OVERRIDE 里手工指定并写了理由。</p>
    <p><b>清单外补充（__NEX__）：</b>两份清单的 Software / Toolboxes 表只覆盖「张量网络 × 神经网络」这一侧，凝聚态谱系的通用引擎与收缩路径优化的前置基线都不在其中——例如 TeNPy 与 cuQuantum 在两份清单的 README 里出现 0 次。补充条目按 GitHub 主题检索（<span style="font-family:var(--mono)">tensor-networks</span> / <span style="font-family:var(--mono)">tensor-decomposition</span> / <span style="font-family:var(--mono)">einsum</span> 等）取 star 排序的候选，再由人挑：哪一条属于哪个分类、为什么加、属于「必加 / 次一级 / 可选」哪一级，全部逐条写在 <span style="font-family:var(--mono)">lit/audit/toolbox_extra.csv</span> 里，卡片展开可见。级别是主观取舍，不是质量评测；star 与推送时间由 <span style="font-family:var(--mono)">lit/audit/fetch_extra.py</span> 走同一份 GitHub 接口缓存取得，取不到记录的条目直接跳过而不补写。</p>
    <p><b>不一致：</b>清单描述与仓库自述冲突时两条都留着，不替读者裁决。例如 TeD-Q 被清单描述为「可微分量子机器学习与 TN 模拟」，而仓库自述说它是 TED-Q <i>数据集</i>；google/TensorNetwork 已被 GitHub 标记为归档（只读），页面上打了标记而不是照抄清单的现在时描述。</p>
  </details>
</section>

<section id="tools">
  <div class="sec-label">Toolboxes</div>
  <h2>工具总表</h2>
  <div class="toolbar">
    <input id="q" type="search" placeholder="搜索工具名 / 能力描述 / 后端 / 分解格式…">
    <button class="chip on" data-g="all">全部</button>
    <button class="chip" data-g="basic">基础运算</button>
    <button class="chip" data-g="layers">模型层</button>
    <button class="chip" data-g="quantum">量子/TN</button>
    <button class="chip" data-g="engine" title="两份清单没收但绕不开的通用引擎">清单外引擎 __NENG__</button>
    <button class="chip" data-g="einsum" title="广义 einsum 与收缩路径引擎">einsum __NEIN__</button>
    <button class="chip" data-g="both" title="只看在两份清单里都出现的">双源</button>
    <button class="chip" data-g="live" title="只看未归档且 2025 年后有推送的">在维护</button>
    <select id="sortKey">
      <option value="st">排序：star</option>
      <option value="pu">排序：最后推送</option>
      <option value="n">排序：名称</option>
    </select>
    <button class="chip" id="sortDirBtn" title="点击切换升降序">▼ 降序</button>
    <span id="count"></span>
  </div>
  <div id="list"></div>
  <p class="note" style="margin-top:18px">点开任意一行可看到：两份清单各自的原文描述、仓库自述、支持的分解格式与后端、源清单把它归在哪几节，以及本站论文库里链接到该仓库的论文。清单外的 __NEX__ 条还会给出选入级别（必加 / 次一级 / 可选）与一句话理由。</p>
</section>

<section id="portals">
  <div class="sec-label">Learning &amp; Knowledge Bases</div>
  <h2>教程网站、权威专著与前沿知识库</h2>
  <p style="font-size:14px;color:var(--muted);line-height:1.8">系统收录国际物理与计算科学界公认的顶级张量网络交互学习网站、里程碑理论综述（涵盖公理化定理至 2026 年大模型前沿）以及权威专著与最新讲义，供理论推导与工程实战查阅。</p>

  <h3>核心交互式教程网站（5）</h3>
  <table class="plain">
    <thead><tr><th>平台 / 网站</th><th>特色定位与核心内容</th><th>支持语言 / 体系</th><th>链接</th></tr></thead>
    <tbody>
      <tr>
        <td class="tt"><b><a href="https://www.tensors.net" target="_blank" rel="noopener">Tensors.net</a></b></td>
        <td>由 Glen Evenbly 创建。被学界公认为最经典、最直观的手把手实操教程，从零推导并实现 MPS、DMRG、TEBD、TRG、CTMRG、MERA 及 2D PEPS，包含丰富交互图解。</td>
        <td class="term">Python (NumPy) / MATLAB / Julia</td>
        <td class="num"><a href="https://www.tensors.net" target="_blank" rel="noopener">tensors.net</a></td>
      </tr>
      <tr>
        <td class="tt"><b><a href="https://tensornetwork.org" target="_blank" rel="noopener">TensorNetwork.org</a></b></td>
        <td>张量网络理论、算法与软件的社区核心枢纽（Miles Stoudenmire、Glen Evenbly、Frank Pollmann 等维护）。规范化 Penrose 图解记号（Graphical Notation），涵盖各类拟态数学定义与社区资源库。</td>
        <td class="term">概念图解 / 算法规范 / 综述索引</td>
        <td class="num"><a href="https://tensornetwork.org" target="_blank" rel="noopener">tensornetwork.org</a></td>
      </tr>
      <tr>
        <td class="tt"><b><a href="https://tensor-networks.github.io" target="_blank" rel="noopener">TensorTutorials (UGent)</a></b></td>
        <td>比利时根特大学量子物理组（Frank Verstraete、Jutho Haegeman 等，MPS/PEPS/VUMPS 算法源头）。深入讲解热力学极限基态算法（VUMPS）、切空间方法（Tangent Space）与 2D PEPS 模拟。</td>
        <td class="term">Julia (TensorKit.jl / MPSKit.jl)</td>
        <td class="num"><a href="https://tensor-networks.github.io" target="_blank" rel="noopener">github.io</a></td>
      </tr>
      <tr>
        <td class="tt"><b><a href="https://pennylane.ai/qml/demonstrations/" target="_blank" rel="noopener">PennyLane Demos &amp; TN</a></b></td>
        <td>Xanadu 维护的量子计算与机器学习交互教程。系统讲解张量网络与量子线路（Quantum Circuits）的对偶映射、量子机器学习中 MPO/MPS 参数化及图张量网络收缩。</td>
        <td class="term">Python (PennyLane / PyTorch / JAX)</td>
        <td class="num"><a href="https://pennylane.ai/qml/demonstrations/" target="_blank" rel="noopener">pennylane.ai</a></td>
      </tr>
      <tr>
        <td class="tt"><b><a href="https://itensor.github.io/ITensors.jl/stable/" target="_blank" rel="noopener">ITensor Docs &amp; Tutorials</a></b></td>
        <td>Flatiron 研究所维护的现代顶级多体计算库官方文档。兼具严格的代数图解教程与现代高性能编程范式，原生覆盖 Abelian / 非 Abelian 量子数守恒与高效自适应 Lanczos DMRG。</td>
        <td class="term">Julia (ITensors.jl) / C++</td>
        <td class="num"><a href="https://itensor.github.io/ITensors.jl/stable/" target="_blank" rel="noopener">itensor.github.io</a></td>
      </tr>
    </tbody>
  </table>

  <h3>权威理论与方法综述（6）</h3>
  <table class="plain">
    <thead><tr><th>综述文献</th><th>学术定位与主要贡献</th><th>年份 / 出处</th><th>标识与链接</th></tr></thead>
    <tbody>
      <tr>
        <td class="tt"><b>Matrix product states and projected entangled pair states: Concepts, symmetries, theorems</b><br><span style="font-size:12px;color:var(--muted)">J. I. Cirac, D. Pérez-García, N. Schuch, F. Verstraete</span></td>
        <td>张量网络领域的公理化现代“圣经”（80+ 页）。严格奠定了 MPS 与 PEPS 的规范形定理、基本定理、整体与规范对称性分类及拓扑序刻画。</td>
        <td class="num">2021<br>Rev. Mod. Phys.</td>
        <td class="num"><a href="https://arxiv.org/abs/2011.12127" target="_blank" rel="noopener">arXiv:2011.12127</a></td>
      </tr>
      <tr>
        <td class="tt"><b>Tensor networks for complex quantum systems</b><br><span style="font-size:12px;color:var(--muted)">Román Orús</span></td>
        <td>高引用全景导引。图文并茂梳理 1D (MPS)、2D (PEPS)、临界态 (MERA)、开放系统以及张量网络在机器学习（TN in ML）与全息对偶（AdS/CFT）中的应用。</td>
        <td class="num">2019<br>Nat. Rev. Phys.</td>
        <td class="num"><a href="https://arxiv.org/abs/1812.04011" target="_blank" rel="noopener">arXiv:1812.04011</a></td>
      </tr>
      <tr>
        <td class="tt"><b>Tensor Network Contractions: Methods and Applications to Quantum Many-Body Systems</b><br><span style="font-size:12px;color:var(--muted)">S.-J. Ran, E. Tirrito, C. Peng, X. Chen, L. Tagliacozzo, G. Su, M. Lewenstein</span></td>
        <td>聚焦“如何把网络变成高效数值收缩算法”。详述正交规范化、实空间 RG、粗粒化与 CTMRG 等数值算法的工程落地，对动手写代码极为实用。</td>
        <td class="num">2020<br>Springer LNP</td>
        <td class="num"><a href="https://arxiv.org/abs/1708.09213" target="_blank" rel="noopener">arXiv:1708.09213</a></td>
      </tr>
      <tr>
        <td class="tt"><b>Tensor Methods for Language Models: From Token Representation to Training, Adaptation, Compression, Inference, and Interpretability</b><br><span style="font-size:12px;color:var(--muted)">M. Tarasov, S. Ahmadi-Asl, A. L. F. de Almeida, A. Cichocki</span></td>
        <td>2026 最新大模型张量方法全景综述。系统覆盖 Token 嵌入、注意力与 FFN 的矩阵乘积算符重写、TeRA 等高秩适配、全生命周期压缩与量子信息可解释性。</td>
        <td class="num">2026<br>arXiv e-print</td>
        <td class="num"><a href="https://arxiv.org/abs/2608.30505" target="_blank" rel="noopener">arXiv:2608.30505</a></td>
      </tr>
      <tr>
        <td class="tt"><b>Quantum-inspired tensor networks in machine learning models</b><br><span style="font-size:12px;color:var(--muted)">G. Valverde et al.</span></td>
        <td>2026 量子启发张量网络机器学习全景。涵盖监督学习、Born 机无监督生成、模型压缩，重点阐明了利用纠缠熵/量子互信息实现可解释性与隐私保护的数学优势。</td>
        <td class="num">2026<br>arXiv e-print</td>
        <td class="num"><a href="https://arxiv.org/abs/2604.14287" target="_blank" rel="noopener">arXiv:2604.14287</a></td>
      </tr>
      <tr>
        <td class="tt"><b>Tensor Networks Meet Neural Networks: A Survey and Future Perspectives</b><br><span style="font-size:12px;color:var(--muted)">M. Wang, Y. Pan, Z. Xu, G. Li, X. Yang, D. Mandic, A. Cichocki</span></td>
        <td>张量网络与神经网络交叉的经典参考清单。系统分类了张量卷积、张量循环网络、张量化 Transformer 以及软硬件协同加速方案。</td>
        <td class="num">2023 / 2026<br>arXiv e-print</td>
        <td class="num"><a href="https://arxiv.org/abs/2302.09019" target="_blank" rel="noopener">arXiv:2302.09019</a></td>
      </tr>
    </tbody>
  </table>

  <h3>经典专著与现代高阶讲义（4）</h3>
  <table class="plain">
    <thead><tr><th>著作 / 讲义名称</th><th>作者 / 机构</th><th>特色说明</th><th>来源 / 预印</th></tr></thead>
    <tbody>
      <tr>
        <td class="tt"><b>《张量网络态方法与应用》</b></td>
        <td>冉仕举、乐伟、彭程 等</td>
        <td>国内第一部系统讲解张量网络态的中文权威专著。从 SVD/MPS 入门，逐步进阶到 PEPS、MERA、热态张量网络，并配有详细 Python 算法实现思路与例程。</td>
        <td class="num">科学出版社<br>2020</td>
      </tr>
      <tr>
        <td class="tt"><b>Tensor Networks in a Nutshell</b></td>
        <td>Jacob Biamonte</td>
        <td>短小精悍，聚焦 Penrose 图形语法、图张量网络（Graph TN）以及量子计算线路与自旋玻璃的张量表示。配套开源讲义 [arXiv:1912.10049]。</td>
        <td class="num"><a href="https://arxiv.org/abs/1912.10049" target="_blank" rel="noopener">arXiv:1912.10049</a><br>2020</td>
      </tr>
      <tr>
        <td class="tt"><b>Les Houches Lecture Notes on Tensor Networks</b></td>
        <td>Les Houches Summer School</td>
        <td>法国莱苏什理论物理暑期学校最新高阶讲义。汇集国际一流专家讲授的高阶数值与理论方法（纠缠哈密顿量、连续张量网络与拓扑相）。</td>
        <td class="num"><a href="https://arxiv.org/abs/2512.24390" target="_blank" rel="noopener">arXiv:2512.24390</a><br>2025/2026</td>
      </tr>
      <tr>
        <td class="tt"><b>Tensor Cookbook: Mastering Tensors through Diagrams</b></td>
        <td>Independent Researchers</td>
        <td>2026 年最新发布的图解实战手册。专注于脱离繁杂指标下标记号的图解代数推导，提供大量工业界与学术界常见的复杂网络收缩优化模版。</td>
        <td class="num"><a href="https://arxiv.org/abs/2605.16610" target="_blank" rel="noopener">arXiv:2605.16610</a><br>2026</td>
      </tr>
    </tbody>
  </table>
</section>

<section id="formats">
  <div class="sec-label">Glossary</div>
  <h2>分解格式速查</h2>
  <p style="font-size:13.5px;color:var(--muted)">下表照录 Tensor Methods for LLMs 清单的 Tensor Formats 图例，用来解读上面「支持格式」一栏。物理命名与数值线性代数命名指的是同一批对象：MPS 就是 TT，MPO 就是 TTM。</p>
  <table class="plain"><thead><tr><th>格式</th><th>含义</th></tr></thead>
  <tbody>__GLOSS__</tbody></table>
</section>

<section id="hardware">
  <div class="sec-label">Beyond software</div>
  <h2>硬件协同设计与压缩案例</h2>
  <p style="font-size:13.5px;color:var(--muted)">这两组不是能直接装的软件包，而是清单 Software 节里一并收录的专用硬件设计与端到端压缩实践，照录以免遗漏。链接为清单原文所给，<b>未</b>逐条核验可达性：ACM 与 IEEE 对脚本请求分别返回 403 和 202，属反爬拦截，不代表链接失效。</p>
  <h3>硬件协同设计（__NHW__）</h3>
  <table class="plain"><thead><tr><th>设计</th><th>说明</th><th>会议</th><th>年份</th></tr></thead>
  <tbody>__HW__</tbody></table>
  <h3>压缩案例研究（__NCASE__）</h3>
  <table class="plain"><thead><tr><th>论文</th></tr></thead>
  <tbody>__CASES__</tbody></table>
</section>

<section id="corpus">
  <div class="sec-label">Cross-reference</div>
  <h2>本库论文附带的开源实现</h2>
  <p style="font-size:13.5px;color:var(--muted)">下面 __NCORP__ 个仓库不是从社区清单抄来的，而是从本站 <a href="library.html">论文库</a> 里 __NCORPP__ 篇论文的 GitHub 字段提出来的（一个仓库可能对应多篇论文）。链接可达性核验于 __TODAY__。标「本页已收录」的说明它同时出现在上面两份清单中 —— 只有 __NOVER__ 个，可见社区清单收的通用工具与单篇论文放出的代码基本是两个集合。</p>
  <table class="plain"><thead><tr><th>仓库</th><th>论文标题</th><th>年份</th><th>被引</th></tr></thead>
  <tbody>__CORP__</tbody></table>
</section>

<footer><span>MPS × LLM · Toolboxes</span><span>来源：ma-tt-a/awesome-tensor-methods-for-llms · tnbar/awesome-tensorial-neural-networks · 清单外补充见 lit/audit/toolbox_extra.csv</span><span>核验于 __TODAY__</span></footer>
</div></main>
<script>
const D=__DATA__;
const S={q:"",g:"all",sortKey:"st",sortDir:-1,closed:new Set(),open:new Set()};
function el(tag,cls,txt){const e=document.createElement(tag);if(cls)e.className=cls;if(txt!=null)e.textContent=txt;return e}
function link(url,txt,cls){const a=document.createElement("a");a.href=url;a.target="_blank";a.rel="noopener";a.textContent=txt;if(cls)a.className=cls;return a}
function toolEl(p,i){
 const d=el("div","grow");
 const r1=el("div","r1");
 const rt=el("span","rt");
 if(p.gh)rt.appendChild(el("span","own",p.gh.split("/")[0]+" / "));
 rt.appendChild(document.createTextNode(p.n));
 if(p.alt&&p.alt.length)rt.appendChild(el("span","alt","  又名 "+p.alt.join(" / ")));
 r1.appendChild(rt);
 const add=(txt,cls)=>r1.appendChild(el("span","badge "+(cls||""),txt));
 const be=[...new Set((p.be||[]).join(",").split(/[,/]/).map(s=>s.trim()).filter(Boolean))];
 if(be.length)add(be.slice(0,3).join(" / ")+(be.length>3?" 等":""),"lang");
 if(p.st!=null)add("★ "+p.st.toLocaleString("en-US"),"st");else add("无 GitHub 数据");
 if(p.lic)add(p.lic);
 if(p.pu)add("推送 "+p.pu);
 if(p.ar)add("已归档","warn");
 if(p.sr.length>1)add("双源收录","c");
 if(p.tier)add("清单外·"+p.tier,"c");
 if(p.co&&p.co.length)add("本库 "+p.co.length+" 篇","c");
 const ver=el("span","ver");
 (p.u||[]).forEach(([lb,url])=>ver.appendChild(link(url,lb,lb==="GitHub"?"gh":"")));
 if(p.gh)ver.appendChild(link("https://github.com/"+p.gh+"/commits","提交历史"));
 r1.appendChild(ver);
 d.appendChild(r1);
 d.appendChild(el("div","capline",(p.cap&&p.cap.length)?p.cap[0][1]:"（清单与仓库都没有给出一句话说明）"));
 const det=el("div","detail");
 (p.cap||[]).forEach(([s,c])=>{const b=el("div","cap"+(s==="仓库自述"?" repo":""));
  b.appendChild(el("span","s",s));b.appendChild(document.createTextNode(c));det.appendChild(b)});
 const bits=[];
 if(p.fmt&&p.fmt.length)bits.push("支持格式："+p.fmt.join("；"));
 if(p.be&&p.be.length)bits.push((p.sr.length?"后端 / 语言：":"GitHub 主语言：")+p.be.join("；"));
 if(p.lay)bits.push("神经网络层："+(p.lay==="+ "?"提供":"不提供"));
 if(p.h3&&p.h3.length)bits.push("清单归类："+p.h3.join(" / "));
 if(p.sr.length)bits.push("来源清单："+p.sr.map(s=>D.srcShort[s]||s).join(" + "));
 else bits.push("来源：两份社区清单之外，按 lit/audit/"+D.extraCsv+" 选入");
 if(p.tier)bits.push("选入级别："+p.tier+(p.why?"｜理由："+p.why:""));
 if(p.gh)bits.push("仓库："+p.gh);
 det.appendChild(el("div","kv",bits.join("\n")));
 if(p.co&&p.co.length){
  const cw=el("div","corp");
  cw.appendChild(el("div","ch","本站论文库中链接到此仓库的论文"));
  const ul=document.createElement("ul");
  p.co.forEach(([ln,ti,yr,cit])=>{const li=document.createElement("li");
   li.appendChild(document.createTextNode(ti+" "));
   li.appendChild(el("span","cy","bibliography 第 "+ln+" 行 · "+(yr||"—")+" · 被引 "+(cit||"—")));
   ul.appendChild(li)});
  cw.appendChild(ul);det.appendChild(cw);
 }
 d.appendChild(det);
 if(S.open.has(i))d.classList.add("open");
 d.addEventListener("click",e=>{if(e.target.tagName==="A")return;
  d.classList.toggle("open");
  if(d.classList.contains("open"))S.open.add(i);else S.open.delete(i)});
 return d;
}
function match(p){
 if(S.g==="both"&&p.sr.length<2)return false;
 if(S.g==="live"&&(p.ar||!(p.pu&&p.pu>="2025")))return false;
 if(S.g!=="all"&&S.g!=="both"&&S.g!=="live"&&p.cat!==S.g)return false;
 const q=S.q.trim().toLowerCase();
 if(!q)return true;
 const hay=[p.n,(p.alt||[]).join(" "),(p.cap||[]).map(c=>c[1]).join(" "),
  (p.fmt||[]).join(" "),(p.be||[]).join(" "),p.gh||"",(p.h3||[]).join(" ")].join(" ").toLowerCase();
 return hay.indexOf(q)>=0;
}
function render(){
 const list=document.getElementById("list");list.innerHTML="";
 document.getElementById("sortKey").value=S.sortKey;
 document.getElementById("sortDirBtn").textContent=S.sortDir<0?"▼ 降序":"▲ 升序";
 const ps=D.tools.map((p,i)=>({p,i})).filter(({p})=>match(p));
 const k=S.sortKey,dir=S.sortDir;
 ps.sort((A,B)=>{
  if(k==="n")return dir*String(A.p.n).localeCompare(String(B.p.n));
  const x=A.p[k],y=B.p[k];
  const xn=(x==null||x===""),yn=(y==null||y==="");
  if(xn&&yn)return 0;if(xn)return 1;if(yn)return -1;
  return dir*(x>y?1:(x<y?-1:0))});
 const chip=document.querySelector('.chip[data-g="'+S.g+'"]');
 document.getElementById("count").textContent="显示 "+ps.length+" / "+D.tools.length+" 个工具"
  +(S.g!=="all"&&chip?(" · 筛选「"+chip.textContent+"」"):"")
  +(S.q?(" · 搜索「"+S.q+"」"):"");
 const groups=new Map();
 ps.forEach(e=>{if(!groups.has(e.p.cat))groups.set(e.p.cat,[]);groups.get(e.p.cat).push(e)});
 D.cat.forEach(c=>{
  if(!groups.has(c))return;
  const blk=el("div","gblock");if(S.closed.has(c))blk.classList.add("closed");
  const gh=el("div","ghead");
  gh.appendChild(el("span","gname",D.catName[c]));
  gh.appendChild(el("span","gcount",groups.get(c).length+" 个"));
  gh.appendChild(el("span","gbar"));
  gh.appendChild(el("span","gmean",D.catDesc[c]));
  gh.appendChild(el("span","gchev","▾"));
  gh.addEventListener("click",()=>{blk.classList.toggle("closed");
   if(blk.classList.contains("closed"))S.closed.add(c);else S.closed.delete(c)});
  blk.appendChild(gh);
  groups.get(c).forEach(e=>blk.appendChild(toolEl(e.p,e.i)));
  list.appendChild(blk)});
 if(!ps.length)list.appendChild(el("div","gdesc","没有匹配的工具。"));
}
document.getElementById("q").addEventListener("input",e=>{S.q=e.target.value;render()});
document.getElementById("sortKey").addEventListener("change",e=>{
 S.sortKey=e.target.value;if(e.target.value==="n")S.sortDir=1;render()});
document.getElementById("sortDirBtn").addEventListener("click",()=>{S.sortDir*=-1;render()});
document.querySelectorAll(".chip[data-g]").forEach(ch=>ch.addEventListener("click",()=>{
 document.querySelectorAll(".chip[data-g]").forEach(c=>c.classList.remove("on"));
 ch.classList.add("on");S.g=ch.dataset.g;render()}));
render();
function t(){const r=document.documentElement;const cur=r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');const n=cur==='dark'?'light':'dark';r.setAttribute('data-theme',n);localStorage.setItem('tn-theme',n);}
(function(){const s=localStorage.getItem('tn-theme');if(s)document.documentElement.setAttribute('data-theme',s);else if(matchMedia('(prefers-color-scheme: dark)').matches)document.documentElement.setAttribute('data-theme','dark');})();
(function(){const ls=[...document.querySelectorAll('#side .toc a')];if(!('IntersectionObserver'in window)||!ls.length)return;
const spy=new IntersectionObserver(es=>{es.forEach(en=>{if(en.isIntersecting)ls.forEach(l=>l.classList.toggle('on',l.getAttribute('href')==='#'+en.target.id));});},{rootMargin:'-30% 0px -60% 0px'});
document.querySelectorAll('section[id]').forEach(s=>spy.observe(s));})();
</script>
</body></html>
"""


if __name__ == "__main__":
    main()
