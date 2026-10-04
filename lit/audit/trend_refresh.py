#!/usr/bin/env python3
"""Rebuild lit/trend_data.csv and lit/发文趋势.png without pandas.

trend_chart.py hardcodes "12 组关键词检索 · 304 篇去重文献" in the figure title, which
is wrong once the corpus grows, so the figure has to be regenerated. This script
mirrors its grouping logic exactly; point --bib at the pre-merge CSV to A/B verify
that the regenerated numbers match the committed trend_data.csv before trusting it.

usage: /opt/homebrew/Caskroom/miniforge/base/bin/python3 lit/audit/trend_refresh.py
"""
import argparse, csv, os, re
from collections import Counter

LIT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "lit")
MAIN = {
    "MPS 语言模型": "MPS 作模型（序列/语言/生成）",
    "MPS/序列建模": "MPS 作模型（序列/语言/生成）",
    "MPS 生成/Born机": "MPS 作模型（序列/语言/生成）",
    "MPO/TT 压缩": "MPO/TT 压缩",
    "张量化Transformer": "MPO/TT 压缩",
    "量子/混合LLM": "量子/量子启发 LLM",
    "量子启发综述": "量子/量子启发 LLM",
    "互信息/标度": "高维结构与标度研究",
    "TTN/MERA/PEPS": "高维结构与标度研究",
}
COLORS = {"MPS 作模型（序列/语言/生成）": "#2E6FBA", "MPO/TT 压缩": "#E07B39",
          "量子/量子启发 LLM": "#3C9A78", "高维结构与标度研究": "#7B5EA7"}
ORDER = ["MPS 作模型（序列/语言/生成）", "MPO/TT 压缩", "量子/量子启发 LLM", "高维结构与标度研究"]

ap = argparse.ArgumentParser()
ap.add_argument("--bib", default=LIT + "/bibliography.csv")
ap.add_argument("--families", default="15", help="检索式族数，写进图题")
ap.add_argument("--out", default=LIT + "/trend_data.csv")
ap.add_argument("--png", default="")
ap.add_argument("--print-only", action="store_true")
a = ap.parse_args()

rows = [r for r in csv.DictReader(open(a.bib, newline="", encoding="utf-8"))]
yr = []
for r in rows:
    m = re.match(r"^\s*(\d{4})", str(r["year"]))
    if m:
        yr.append(int(m.group(1)))
    else:
        yr.append(None)
kept = [(y, r) for y, r in zip(yr, rows) if y]
years = list(range(min(y for y, _ in kept), max(y for y, _ in kept) + 1))
yidx = {y: i for i, y in enumerate(years)}

cnt = {m: [0] * len(years) for m in COLORS}
unclust = 0
for y, r in kept:
    cs = str(r.get("clusters") or "")
    mains = {MAIN[k] for k in MAIN if k in cs}
    if not mains:
        unclust += 1
    for m in mains:
        cnt[m][yidx[y]] += 1
uniq = Counter(y for y, _ in kept)
series = [uniq.get(y, 0) for y in years]
cum, tot = [], 0
for v in series:
    tot += v
    cum.append(tot)

header = ["year", "unique_papers", "cumulative"] + ORDER
if not a.print_only:
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for i, y in enumerate(years):
            w.writerow([y, series[i], cum[i]] + [cnt[m][i] for m in ORDER])
print(f"rows={len(kept)} years={years[0]}..{years[-1]} cumulative={cum[-1]} "
      f"unclustered={unclust} (missing-year rows dropped: {len(rows) - len(kept)})")
print("per-mainline totals:", {m: sum(cnt[m]) for m in ORDER})
if a.print_only:
    for i, y in enumerate(years):
        print("  ", y, series[i], cum[i], [cnt[m][i] for m in ORDER])
    raise SystemExit(0)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

avail = {f.name for f in font_manager.fontManager.ttflist}
# WSL/Linux 常无预装 CJK 字体；检测到 Windows 盘（/mnt/c）或 Noto 包时先注册再选
for fp in ("/mnt/c/Windows/Fonts/msyh.ttc", "/mnt/c/Windows/Fonts/simsun.ttc",
           "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"):
    if os.path.exists(fp):
        font_manager.fontManager.addfont(fp)
avail = {f.name for f in font_manager.fontManager.ttflist}
font = next((c for c in ["PingFang SC", "Songti SC", "Noto Sans CJK SC", "Heiti SC",
                         "Microsoft YaHei", "SimSun"] if c in avail), None)
if font:
    plt.rcParams["font.family"] = font
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(11, 6.2), dpi=150)
fig.patch.set_facecolor("#f4f0ea")
ax.set_facecolor("#f4f0ea")
bottom = [0] * len(years)
for m in ORDER:
    ax.bar(years, cnt[m], bottom=bottom, color=COLORS[m], width=0.72, label=m,
           edgecolor="#f4f0ea", linewidth=0.6)
    bottom = [b + c for b, c in zip(bottom, cnt[m])]
ax.plot(years, series, color="#4f483e", lw=1.6, marker="o", ms=3.5, label="当年论文数（去重）")
ax2 = ax.twinx()
ax2.plot(years, cum, color="#b82a00", lw=1.8, ls="--", label="累计论文数")
ax2.set_ylabel("累计（篇）", color="#b82a00", fontsize=10)
ax2.tick_params(axis="y", colors="#b82a00")
ax2.set_ylim(0, max(cum) * 1.15)
ax.set_xlim(years[0] - 0.6, years[-1] + 0.6)
ax.set_ylabel("当年论文数（篇）", fontsize=10, color="#4f483e")
ax.set_title("MPS 张量网络 × 深度学习/大模型 · 发文趋势\n"
             f"{a.families} 组检索式族 · {len(kept)} 篇去重文献 · 堆叠柱按主线归属（一篇可多归属）",
             fontsize=13, color="#4f483e", pad=14)
ax.tick_params(colors="#4f483e")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax2.spines["top"].set_visible(False)
ax.grid(axis="y", color="#d8cebe", lw=0.7, alpha=0.7)
ax.set_axisbelow(True)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, frameon=False, fontsize=9, loc="upper left")
fig.tight_layout()
out = a.png or (LIT + "/发文趋势.png")
fig.savefig(out)
print("png ->", out, os.path.getsize(out), "bytes")
