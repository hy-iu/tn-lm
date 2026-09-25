#!/usr/bin/env python3
"""Publication-trend chart + data from bibliography.csv."""
import ast
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

LIT = "/Users/bjergsen/Documents/GitHub/tn-lm/lit"

# CJK font
cands = ["PingFang SC", "Songti SC", "Noto Sans CJK SC", "Heiti SC", "STHeiti"]
avail = {f.name for f in font_manager.fontManager.ttflist}
font = next((c for c in cands if c in avail), None)
if font:
    plt.rcParams["font.family"] = font
plt.rcParams["axes.unicode_minus"] = False

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
COLORS = {
    "MPS 作模型（序列/语言/生成）": "#2E6FBA",
    "MPO/TT 压缩": "#E07B39",
    "量子/量子启发 LLM": "#3C9A78",
    "高维结构与标度研究": "#7B5EA7",
}

bib = pd.read_csv(f"{LIT}/bibliography.csv")
bib = bib[bib["year"].notna()].copy()
bib["year"] = bib["year"].astype(int)

years = list(range(bib["year"].min(), bib["year"].max() + 1))

# per-mainline counts (a paper can contribute to multiple mainlines)
cnt = {m: [0] * len(years) for m in COLORS}
for _, r in bib.iterrows():
    cs = str(r["clusters"])
    mains = {MAIN[k] for k in MAIN if k in cs}
    yi = years.index(r["year"])
    for m in mains:
        cnt[m][yi] += 1

uniq = bib.groupby("year").size().reindex(years, fill_value=0)
cum = uniq.cumsum()

# save trend data
df = pd.DataFrame({"year": years, "unique_papers": uniq.values,
                   "cumulative": cum.values, **{m: v for m, v in cnt.items()}})
df.to_csv(f"{LIT}/trend_data.csv", index=False)

# chart
fig, ax = plt.subplots(figsize=(11, 6.2), dpi=150)
fig.patch.set_facecolor("#f4f0ea")
ax.set_facecolor("#f4f0ea")

bottom = [0] * len(years)
for m in ["MPS 作模型（序列/语言/生成）", "MPO/TT 压缩",
          "量子/量子启发 LLM", "高维结构与标度研究"]:
    ax.bar(years, cnt[m], bottom=bottom, color=COLORS[m], width=0.72,
           label=m, edgecolor="#f4f0ea", linewidth=0.6)
    bottom = [b + c for b, c in zip(bottom, cnt[m])]

ax.plot(years, uniq.values, color="#4f483e", lw=1.6, marker="o", ms=3.5,
        label="当年论文数（去重）")
ax2 = ax.twinx()
ax2.plot(years, cum.values, color="#b82a00", lw=1.8, ls="--", marker="",
         label="累计论文数")
ax2.set_ylabel("累计（篇）", color="#b82a00", fontsize=10)
ax2.tick_params(axis="y", colors="#b82a00")
ax2.set_ylim(0, cum.max() * 1.15)

ax.set_xlim(min(years) - 0.6, max(years) + 0.6)
ax.set_ylabel("当年论文数（篇）", fontsize=10, color="#4f483e")
ax.set_title("MPS 张量网络 × 深度学习/大模型 · 发文趋势（1989-2026）\n"
             "12 组关键词检索 · 304 篇去重文献 · 堆叠柱按主线归属（一篇可多归属）",
             fontsize=13, color="#4f483e", pad=14)
ax.tick_params(colors="#4f483e")
for s in ["top"]:
    ax.spines[s].set_visible(False)
ax.spines["right"].set_visible(False)
ax2.spines["top"].set_visible(False)
ax.grid(axis="y", color="#d8cebe", lw=0.7, alpha=0.7)
ax.set_axisbelow(True)

h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=9, frameon=False)

# annotate key inflection points
for yr, txt in [(2016, "Stoudenmire\nMPS 分类器"), (2018, "Han\nBorn machine"),
                (2021, "Miller\nuMPS"), (2024, "CompactifAI\nLLaMA-2 7B")]:
    if yr in years:
        v = uniq[yr]
        ax.annotate(txt, xy=(yr, v), xytext=(yr, v + 12),
                    fontsize=8, color="#6b5f4e", ha="center",
                    arrowprops=dict(arrowstyle="-", color="#8a7d6b", lw=0.8))

plt.tight_layout()
plt.savefig(f"{LIT}/发文趋势.png", facecolor="#f4f0ea")
print("saved", f"{LIT}/发文趋势.png")
print(df.tail(14).to_string(index=False))
