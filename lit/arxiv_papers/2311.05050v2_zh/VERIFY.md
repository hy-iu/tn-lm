# VERIFY.md — 2311.05050v2《Sequential learning on a Tensor Network Born machine with Trainable Token Embedding》中译校对记录

日期：2026-10-02。
英文源（只读）：`lit/arxiv_papers/2311.05050v2/`（`main.tex` 375 行 + `ref.bib` + 4 张 PDF 图）；英文参考 PDF：`lit/arxiv_papers/2311.05050v2.pdf`（6 页）。
工作目录：`lit/arxiv_papers/2311.05050v2_zh/`。
交付：`lit/arxiv_papers/2311.05050v2_zh.pdf`（5 页）。

## 流水线

1. 英文基线编译：`_baseline/` latexmk -pdf 通过（6 页，0 错误）。
2. 正文按节边界手工切分为 6 个字节级可复原片段（`en_parts/` 英文原件、`parts/` 待译副本）：preamble（不译）/ 摘要+引言 / 编码结构 / 边缘化与生成式采样 / 实验结果+总结+致谢 / 参考文献尾（不译）。
3. 4 个并行译者就地翻译，`tools_x/check_chunk.py` 逐片自检，全部 STRUCT OK（环境序列、label/ref/cite 键、$ 数、公式数与英文完全一致）。
4. `cat` 拼回 `main.tex`，漏译扫描仅剩 3 处预期保留项（xeCJK 字体配置、标题英文副题、作者单位）。

## 导言区改动

| 位置 | 改动 |
|---|---|
| `\documentclass` 后 | 新增 xeCJK；`\setCJKmainfont{SimSun}[ItalicFont=KaiTi, BoldFont=SimHei]` |
| 自定义引用宏 | `\eqnref/\figref/\tabref/\secref/\appref/\refcite` 显示名改为 式/图/表/第…节/附录/文献 |
| `\begin{document}` 后 | `\parindent 2em`；`\refname{参考文献}`、`\figurename{图}`、`\tablename{表}`、`\acknowledgmentsname{致谢}` |
| algorithmic | `\algorithmicrequire{输入:}`、`\algorithmicensure{输出:}`、`\floatname{algorithm}{算法}`（注意 revtex 下 `\algorithmname` 未定义，须用 `\floatname`） |
| `\title` | 中文主标题 + 英文原题副行 |

## 编译与校验

- `latexmk -xelatex`：exit 0，5 页（英文 6 页，尾部空附录页在中文版合并），0 `!` 错误、0 undefined citation/reference、0 Missing character。
- 逐页 PNG（`render/p-1..5.png`）人工目检通过：中文渲染无豆腐块；4 张图正常；算法 1/2 显示「输入:/输出:」；交叉引用无 `??`；参考文献按惯例保留英文。

## 上游遗留

- 式 (5) 下标中含句点 `δ_{b_{i-1}b'_{i-1}.}`（原文即如此），按原样保留。
