# VERIFY.md — 2003.01039v4《Tensor Networks for Probabilistic Sequence Modeling》中译校对记录

日期：2026-10-03。
英文源（只读）：`lit/arxiv_papers/2003.01039v4/`（AISTATS 2021 模板：`aistats.tex` 816 行 + `aistats2021.sty` + `aistats.bbl`（46 条）+ 2 张 PDF 图）；英文参考 PDF：`lit/arxiv_papers/2003.01039v4.pdf`（18 页）。
工作目录：`lit/arxiv_papers/2003.01039v4_zh/`。
交付：`lit/arxiv_papers/2003.01039v4_zh.pdf`（16 页）。

## 流水线（与前两篇一致：切分 → 并行译者 → check_chunk → 拼回 → xelatex）

1. 英文基线编译：`_baseline/` pdflatex 通过（18 页，引用齐全）。上游缺陷：3 处 `\verb` 用法触发 `\verb ended by end of line`（第 470、474、808 行），PDF 仍完整产出，exit 码非 0 属上游遗留，原样保留。
2. 正文按节边界切成 17 个字节级可复原片段（`en_parts/` 原件、`parts/` 译副本）：preamble+摘要 / 引言 / 背景 / Uniform MPS / Born 机器 / 正则表达式与 u-MPS / regex 采样与 regularization 头 / 采样 / regularization / 实验 / 合成实验 / 电子邮件实验 / 结论 / 附录 A / 附录 B 证明 / 附录 C 运行时 / 附录 D 细节。摘要由主线程补译，其余 16 片段派并行译者（每批 3 个，按用户要求），`tools_x/check_chunk.py` 全部 STRUCT OK。
3. 拼回后修复两处译稿引入的问题：① 反斜杠后接全角括号（`\（`）导致 Undefined control sequence；② 修复时误伤标题里合法的 `\\（`，已复原。
4. 中央显示词统一：`\eqnref` 宏定义 Equation→式；Theorem/Lemma/Algorithm 引用词→定理/引理/算法（仅散文处，宏名与键名不动）。

## 导言区改动

| 位置 | 改动 |
|---|---|
| `\documentclass` 后 | xeCJK + SimSun/KaiTi/SimHei；`\figurename{图}`、`\tablename{表}`、`\refname{参考文献}` |
| `\usepackage{amsthm}` 后 | `\proofname{证明}`（amsthm 加载前不可 renew） |
| 3 个 `\newtheorem` 显示名 | Lemma→引理、Theorem→定理、Theorem*→定理 |
| `\aistatstitle` | 中文主标题 + `\\` + 英文原题副行 |
| `\begin{document}` 后 | `\runningtitle{Tensor Networks for Probabilistic Sequence Modeling}`（英文；sty 以高度 >10pt 判定，中文页眉有风险） |
| `aistats2021.sty`（本地副本） | `\centerline{...\bfseries Abstract}`→摘要（sty 硬编码） |

## 编译与校验

- `xelatex` 两遍：16 页（英文 18 页，中文排版更紧凑），0 undefined citation、0 `??`、无新增 `!`；仅剩上游 `\verb` 报错（英文基线相同）。
- 漏译扫描：仅剩 xeCJK 字体配置与作者单位 2 处预期保留项。
- 逐页 PNG（`render/p-01..16.png`）人工目检通过：双栏无重叠溢出；图 1–2、表 1–6 正常；定理 1–4、引理、证明环境标题中文；算法 1 伪代码含「采样字符串字面量」等中文注释；页眉为英文 running title（模板判定限制，预期保留）；参考文献按惯例保留英文。
