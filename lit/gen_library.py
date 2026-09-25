#!/usr/bin/env python3
"""Generate app/library.html: embeds bibliography.csv as JSON with local-PDF mapping."""
import json, os, re
import pandas as pd

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"
OUT = "/Users/bjergsen/Documents/GitHub/tn-lm/app/library.html"

bib = pd.read_csv(os.path.join(LIT, "bibliography.csv"))

def safe_name(t):
    return (re.sub(r"[^A-Za-z0-9]+", "_", str(t))[:60].strip("_") or "paper")

def fname(row):
    yr = int(row["year"]) if pd.notna(row["year"]) else "nd"
    if isinstance(row.get("arxiv_id"), str) and row["arxiv_id"]:
        return f"{yr}_arxiv_{row['arxiv_id']}.pdf"
    return f"{yr}_{safe_name(row['title'])[:50]}.pdf"

records = []
for _, r in bib.iterrows():
    f = fname(r)
    local = os.path.join(LIT, "papers", f)
    pdf = f"../lit/papers/{f}" if os.path.exists(local) else None
    authors = str(r["authors"]) if pd.notna(r["authors"]) else ""
    if "·" in authors:
        authors = authors.split("·")[0].strip()
    jr = str(r["journal_ref"]).strip() if pd.notna(r.get("journal_ref")) else ""
    if jr:
        venue = jr
    else:
        pub = str(r["publication_info"]) if pd.notna(r["publication_info"]) else ""
        parts = [p.strip() for p in pub.split(" - ")]
        venue = parts[1] if len(parts) >= 2 else pub
    records.append({
        "t": str(r["title"]),
        "a": authors,
        "y": int(r["year"]) if pd.notna(r["year"]) else None,
        "c": int(r["citations"]) if pd.notna(r["citations"]) else 0,
        "v": venue,
        "abs": str(r["abstract"]) if pd.notna(r["abstract"]) else "",
        "u": str(r["url"]) if pd.notna(r["url"]) else "",
        "cl": str(r["clusters"]) if pd.notna(r["clusters"]) else "",
        "pdf": pdf,
    })

data_js = json.dumps(records, ensure_ascii=False)
n_pdf = sum(1 for r in records if r["pdf"])
tot_cit = sum(r["c"] for r in records)
years = [r["y"] for r in records if r["y"]]
yspan = f"{min(years)}–{max(years)}"

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>论文库 · 全部文献 304 篇</title>
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
.wrap{max-width:1020px;margin:0 auto;padding:0 40px}
@media(max-width:760px){.wrap{padding:0 22px}}
header{border-bottom:2px solid var(--ink);padding:42px 0 26px}
.mast-meta{display:flex;justify-content:space-between;font-family:var(--mono);font-size:11px;color:var(--muted);letter-spacing:.12em;text-transform:uppercase;margin-bottom:18px}
h1{font-family:var(--serif);font-size:38px;line-height:1.2}
h1 em{font-style:normal;color:var(--accent)}
.subtitle{margin-top:14px;color:var(--muted);max-width:720px}
section{padding:52px 0 8px}
.sec-label{font-family:var(--mono);font-size:11px;letter-spacing:.3em;text-transform:uppercase;color:var(--accent);margin-bottom:10px}
h2{font-family:var(--serif);font-size:26px;margin-bottom:16px}
p{margin-bottom:14px}
a{color:var(--accent);text-decoration:none;border-bottom:1px solid var(--tint)}
/* stats */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:18px 0 8px}
.stat{background:var(--card);border:1px solid #e2d9cb;padding:14px 16px}
[data-theme="dark"] .stat{border-color:#3a332a}
.stat .num{font-family:var(--serif);font-size:30px;color:var(--accent);line-height:1.1}
.stat .lbl{font-family:var(--mono);font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);margin-top:4px}
/* toolbar */
.toolbar{position:sticky;top:0;background:var(--bg);z-index:20;padding:14px 0 10px;border-bottom:1px solid #d8cebe;display:flex;flex-wrap:wrap;gap:10px;align-items:center}
[data-theme="dark"] .toolbar{border-bottom-color:#3a332a}
#q{flex:1;min-width:200px;font-family:var(--sans);font-size:14px;padding:8px 12px;border:1px solid var(--muted);background:var(--card);color:var(--ink);border-radius:2px}
#q:focus{outline:none;border-color:var(--accent)}
.chip{font-family:var(--sans);font-size:12px;padding:6px 12px;border:1px solid var(--muted);background:var(--card);color:var(--ink);cursor:pointer;border-radius:999px;transition:all .2s}
.chip:hover{border-color:var(--accent)}
.chip.on{background:var(--accent);border-color:var(--accent);color:#fffbf5}
select,.yr{font-family:var(--mono);font-size:12px;padding:7px 10px;border:1px solid var(--muted);background:var(--card);color:var(--ink);border-radius:2px}
.yr{width:74px}
#count{font-family:var(--mono);font-size:11px;color:var(--muted);width:100%}
/* groups */
.ghead{display:flex;align-items:baseline;gap:12px;padding:14px 8px 8px;cursor:pointer;user-select:none;border-bottom:2px solid var(--ink);margin-top:10px}
.ghead .gname{font-family:var(--serif);font-size:19px}
.ghead .gcount{font-family:var(--mono);font-size:11px;color:var(--muted)}
.ghead .gchev{margin-left:auto;font-family:var(--mono);font-size:12px;color:var(--muted);transition:transform .25s}
.ghead .gbar{flex:1;height:3px;background:var(--tint);align-self:center;max-width:120px}
.gblock.closed .grow{display:none}
.gblock.closed .gchev{transform:rotate(-90deg)}
/* paper rows */
.grow{border-bottom:1px solid #e2d9cb;padding:12px 8px;cursor:pointer;transition:background .2s}
[data-theme="dark"] .grow{border-bottom-color:#3a332a}
.grow:hover{background:var(--surface)}
.grow .r1{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
.grow .rt{font-family:var(--serif);font-size:16px;flex:1;min-width:260px}
.grow .rt a{color:var(--ink);border-bottom:1px solid var(--tint)}
.grow .rt a:hover{color:var(--accent)}
.grow .rmeta{font-size:12.5px;color:var(--muted);margin-top:4px}
.badge{font-family:var(--mono);font-size:10.5px;padding:2px 8px;border:1px solid #d8cebe;color:var(--muted);border-radius:2px;white-space:nowrap}
[data-theme="dark"] .badge{border-color:#3a332a}
.badge.c{color:var(--accent);border-color:var(--tint)}
.badge.pdf{border-color:var(--accent)}
.badge.pdf a{color:var(--accent);border:none}
.grow .abs{display:none;margin-top:10px;font-size:13.5px;line-height:1.8;background:var(--card);border-left:3px solid var(--tint);padding:12px 16px;color:var(--ink)}
.grow.open .abs{display:block}
/* sortable flat table */
table.flat{width:100%;border-collapse:collapse;margin-top:8px;font-size:14px}
table.flat th{font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);text-align:left;padding:10px 8px;border-bottom:2px solid var(--ink);cursor:pointer;user-select:none;white-space:nowrap}
table.flat th:hover{color:var(--accent)}
table.flat td{padding:10px 8px;border-bottom:1px solid #e2d9cb;vertical-align:top}
[data-theme="dark"] table.flat td{border-bottom-color:#3a332a}
table.flat .tt{font-family:var(--serif);font-size:15px}
table.flat .tt a{color:var(--ink);border-bottom:1px solid var(--tint)}
table.flat .tt a:hover{color:var(--accent)}
footer{margin-top:70px;border-top:2px solid var(--ink);padding:26px 0 60px;font-family:var(--mono);font-size:11px;color:var(--muted);display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
</style>
</head>
<body>
<nav id="side">
  <div class="pgroup">
    <a href="index.html">研究备忘</a>
    <a href="figures.html">图解路线</a>
    <a href="library.html" class="cur">论文库</a>
  </div>
  <hr>
  <div class="toc">
    <a href="#overview">概览</a>
    <a href="#browse">论文列表</a>
  </div>
</nav>
<button id="themeBtn" onclick="t()">◐ 主题</button>
<main><div class="wrap">
<header>
  <div class="mast-meta"><span>Vol. 02 — 论文库 · __NPAPERS__ 篇 · 已下全文 __NPDF__</span><span>__YSPAN__</span><span><a href="index.html">← 研究备忘</a></span></div>
</header>

<section id="overview">
  <div class="stats">
    <div class="stat"><div class="num">__NPAPERS__</div><div class="lbl">去重论文</div></div>
    <div class="stat"><div class="num">__NPDF__</div><div class="lbl">已下载全文</div></div>
    <div class="stat"><div class="num">__TOTCIT__</div><div class="lbl">被引合计</div></div>
    <div class="stat"><div class="num" style="font-size:20px;padding-top:8px">__YSPAN__</div><div class="lbl">年份跨度</div></div>
    <div class="stat"><div class="num">4+1</div><div class="lbl">主线 + 未分组</div></div>
  </div>
  <p style="font-size:13px;color:var(--muted)">主线归属规则：MPS 语言模型 / 序列建模 / Born 机 → <b>MPS 作模型</b>；MPO·TT 压缩 / 张量化 Transformer → <b>MPO/TT 压缩</b>；量子·量子启发 LLM / 综述 → <b>量子/量子启发 LLM</b>；互信息·标度 / TTN·MERA·PEPS → <b>高维结构与标度研究</b>；其余命中 → <b>未分组</b>。一篇论文可同时属于多条主线（与图 6 计数口径一致）。题录经 arXiv / OpenAlex 补全（完整摘要与发表期刊，找不到的保留检索摘要）。被引数为检索索引返回值，仅作相对量级参考。</p>
</section>

<section id="browse">
  <div class="toolbar">
    <input id="q" type="search" placeholder="搜索标题 / 作者 / 摘要 / 出处关键词…">
    <button class="chip on" data-g="all">全部</button>
    <button class="chip" data-g="g0">MPS 作模型</button>
    <button class="chip" data-g="g1">MPO/TT 压缩</button>
    <button class="chip" data-g="g2">量子 LLM</button>
    <button class="chip" data-g="g3">高维与标度</button>
    <button class="chip" data-g="gx">未分组</button>
    <input class="yr" id="ymin" type="number" placeholder="起年" min="1980" max="2027">
    <input class="yr" id="ymax" type="number" placeholder="止年" min="1980" max="2027">
    <select id="sortKey">
      <option value="c">排序：被引</option>
      <option value="y">排序：年份</option>
      <option value="t">排序：标题</option>
    </select>
    <button class="chip" id="sortDirBtn" title="点击切换升降序">▼ 降序</button>
    <select id="groupBy">
      <option value="main">分组：主线</option>
      <option value="year">分组：年份</option>
      <option value="none">不分组（表格）</option>
    </select>
    <span id="count"></span>
  </div>
  <div id="list"></div>
</section>

<footer><span>MPS × LLM · Library</span><span>原始数据：<a href="../lit/bibliography.csv" download>bibliography.csv ↓</a> · <a href="../lit/trend_data.csv" download>trend_data.csv ↓</a></span><span>来源：学术检索索引 / arXiv / OpenAlex，仅供参考</span></footer>
</div></main>
<script>
const PAPERS=__DATA__;
const MAINMAP=[["MPS 语言模型","g0"],["MPS/序列建模","g0"],["MPS 生成/Born机","g0"],
 ["MPO/TT 压缩","g1"],["张量化Transformer","g1"],
 ["量子/混合LLM","g2"],["量子启发综述","g2"],
 ["互信息/标度","g3"],["TTN/MERA/PEPS","g3"]];
const GNAME={g0:"MPS 作模型（序列/语言/生成）",g1:"MPO/TT 压缩",g2:"量子/量子启发 LLM",g3:"高维结构与标度研究",gx:"未分组/其他"};
const GORDER=["g0","g1","g2","g3","gx"];
function mainOf(cl){const m=new Set();MAINMAP.forEach(([k,g])=>{if(cl.indexOf(k)>=0)m.add(g)});return m.size?m:new Set(["gx"])}
const S={q:"",g:"all",ymin:null,ymax:null,groupBy:"main",sortKey:"c",sortDir:-1,closed:new Set(),openAbs:new Set()};
function esc(s){return String(s==null?"":s)}
function rowEl(p,i){
 const d=document.createElement("div");d.className="grow";
 const r1=document.createElement("div");r1.className="r1";
 const rt=document.createElement("span");rt.className="rt";
 const a=document.createElement("a");a.href=p.u;a.target="_blank";a.rel="noopener";a.textContent=p.t;rt.appendChild(a);
 r1.appendChild(rt);
 const addBadge=(txt,cls)=>{const b=document.createElement("span");b.className="badge "+cls;b.textContent=txt;r1.appendChild(b)};
 addBadge(p.y||"—","");
 addBadge("被引 "+p.c,p.c>50?"c":"");
 if(p.pdf){const b=document.createElement("span");b.className="badge pdf";const l=document.createElement("a");l.href=p.pdf;l.target="_blank";l.rel="noopener";l.textContent="PDF";b.appendChild(l);r1.appendChild(b)}
 d.appendChild(r1);
 const meta=document.createElement("div");meta.className="rmeta";
 meta.textContent=(p.a?p.a+" · ":"")+(p.v||"")+(p.cl?" ｜ 命中："+p.cl:"");
 d.appendChild(meta);
 const abs=document.createElement("div");abs.className="abs";abs.textContent=p.abs||"（无摘要）";
 d.appendChild(abs);
 if(S.openAbs.has(i))d.classList.add("open");
 d.addEventListener("click",e=>{if(e.target.tagName==="A")return;d.classList.toggle("open");if(d.classList.contains("open"))S.openAbs.add(i);else S.openAbs.delete(i)});
 return d;
}
function flatTable(ps){
 const tb=document.createElement("table");tb.className="flat";
 const head=document.createElement("tr");
 [["标题","t"],["年份","y"],["被引","c"],["出处","v"]].forEach(([lb,k])=>{
  const th=document.createElement("th");th.textContent=lb+(S.sortKey===k?(S.sortDir<0?" ▼":" ▲"):"");
  th.addEventListener("click",()=>{if(S.sortKey===k)S.sortDir*=-1;else{S.sortKey=k;S.sortDir=k==="t"?1:-1}render()});
  head.appendChild(th)});
 tb.appendChild(head);
 ps.forEach(({p})=>{const tr=document.createElement("tr");
  const td=document.createElement("td");td.className="tt";
  const a=document.createElement("a");a.href=p.u;a.target="_blank";a.rel="noopener";a.textContent=p.t;
  if(p.pdf){const l=document.createElement("a");l.href=p.pdf;l.target="_blank";l.textContent=" · PDF";td.appendChild(l)}
  td.prepend(a);tr.appendChild(td);
  const y=document.createElement("td");y.textContent=p.y||"—";tr.appendChild(y);
  const c=document.createElement("td");c.textContent=p.c;tr.appendChild(c);
  const v=document.createElement("td");v.style.cssText="font-size:12px;color:var(--muted)";v.textContent=p.v;tr.appendChild(v);
  tb.appendChild(tr)});
 return tb;
}
function filtered(){
 const q=S.q.trim().toLowerCase();
 return PAPERS.map((p,i)=>({p,i})).filter(({p})=>{
  if(S.g!=="all"&&!mainOf(p.cl).has(S.g))return false;
  if(S.ymin&&!(p.y&&p.y>=S.ymin))return false;
  if(S.ymax&&!(p.y&&p.y<=S.ymax))return false;
  if(q){const hay=(p.t+" "+p.a+" "+p.abs+" "+p.v).toLowerCase();if(hay.indexOf(q)<0)return false}
  return true});
}
function sorted(ps){
 const k=S.sortKey,dir=S.sortDir;
 return ps.sort((A,B)=>{let x=A.p[k],y=B.p[k];
  const xn=(x==null),yn=(y==null);
  if(xn&&yn)return 0;if(xn)return 1;if(yn)return -1;
  if(typeof x==="string")return dir*x.localeCompare(y);
  return dir*(x-y)});
}
function render(){
 const list=document.getElementById("list");list.innerHTML="";
 document.getElementById("sortKey").value=S.sortKey;
 const db=document.getElementById("sortDirBtn");db.textContent=S.sortDir<0?"▼ 降序":"▲ 升序";
 const ps=sorted(filtered());
 document.getElementById("count").textContent="显示 "+ps.length+" / "+PAPERS.length+" 篇"+(S.g!=="all"?(" · "+GNAME[S.g]):"")+(S.q?(" · 搜索「"+S.q+"」"):"");
 if(S.groupBy==="none"){list.appendChild(flatTable(ps));return}
 const groups=new Map();
 ps.forEach(e=>{
  const keys=S.groupBy==="year"?[String(e.p.y||"无年份")]:[...mainOf(e.p.cl)];
  keys.forEach(k=>{if(!groups.has(k))groups.set(k,[]);groups.get(k).push(e)})});
 const order=[...groups.keys()].sort((a,b)=>{
  if(S.groupBy==="year")return b.localeCompare(a);
  return (GORDER.indexOf(a)-GORDER.indexOf(b))});
 order.forEach(k=>{
  const blk=document.createElement("div");blk.className="gblock";
  if(S.closed.has(k))blk.classList.add("closed");
  const gh=document.createElement("div");gh.className="ghead";
  const nm=document.createElement("span");nm.className="gname";
  nm.textContent=S.groupBy==="year"?(k+" 年"):GNAME[k];
  const cnt=document.createElement("span");cnt.className="gcount";cnt.textContent=groups.get(k).length+" 篇";
  const bar=document.createElement("span");bar.className="gbar";
  const ch=document.createElement("span");ch.className="gchev";ch.textContent="▾";
  gh.appendChild(nm);gh.appendChild(cnt);gh.appendChild(bar);gh.appendChild(ch);
  gh.addEventListener("click",()=>{blk.classList.toggle("closed");if(blk.classList.contains("closed"))S.closed.add(k);else S.closed.delete(k)});
  blk.appendChild(gh);
  groups.get(k).forEach(e=>blk.appendChild(rowEl(e.p,e.i)));
  list.appendChild(blk)});
}
document.getElementById("q").addEventListener("input",e=>{S.q=e.target.value;render()});
document.getElementById("ymin").addEventListener("input",e=>{S.ymin=+e.target.value||null;render()});
document.getElementById("ymax").addEventListener("input",e=>{S.ymax=+e.target.value||null;render()});
document.getElementById("groupBy").addEventListener("change",e=>{S.groupBy=e.target.value;render()});
document.getElementById("sortKey").addEventListener("change",e=>{S.sortKey=e.target.value;if(e.target.value==="t")S.sortDir=1;render()});
document.getElementById("sortDirBtn").addEventListener("click",()=>{S.sortDir*=-1;render()});
document.querySelectorAll(".chip[data-g]").forEach(ch=>ch.addEventListener("click",()=>{
 document.querySelectorAll(".chip").forEach(c=>c.classList.remove("on"));
 ch.classList.add("on");S.g=ch.dataset.g;render()}));
render();
/* theme */
function t(){const r=document.documentElement;const cur=r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');const n=cur==='dark'?'light':'dark';r.setAttribute('data-theme',n);localStorage.setItem('tn-theme',n);}
(function(){const s=localStorage.getItem('tn-theme');if(s)document.documentElement.setAttribute('data-theme',s);else if(matchMedia('(prefers-color-scheme: dark)').matches)document.documentElement.setAttribute('data-theme','dark');})();
/* TOC scrollspy */
(function(){const ls=[...document.querySelectorAll('#side .toc a')];if(!('IntersectionObserver'in window)||!ls.length)return;
const spy=new IntersectionObserver(es=>{es.forEach(en=>{if(en.isIntersecting)ls.forEach(l=>l.classList.toggle('on',l.getAttribute('href')==='#'+en.target.id));});},{rootMargin:'-30% 0px -60% 0px'});
document.querySelectorAll('section[id]').forEach(s=>spy.observe(s));})();
</script>
</body></html>
"""

html = (TEMPLATE
        .replace("__DATA__", data_js)
        .replace("__NPAPERS__", str(len(records)))
        .replace("__NPDF__", str(n_pdf))
        .replace("__TOTCIT__", str(tot_cit))
        .replace("__YSPAN__", yspan))
with open(OUT, "w") as f:
    f.write(html)
print("wrote", OUT, f"{os.path.getsize(OUT)/1024:.0f} KB,",
      len(records), "papers,", n_pdf, "with local pdf")
