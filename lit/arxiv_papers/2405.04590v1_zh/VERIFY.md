# VERIFY.md — 2405.04590v1《Language Modeling Using Tensor Trains》中译校对记录

日期：2026-10-02。
英文源（只读）：`lit/arxiv_papers/2405.04590v1/`（ICML 2023 模板：`icml2023.tex` 973 行 + `sections/Preliminaries.tex` + `math_commands.tex` + 图件）；英文参考 PDF：`lit/arxiv_papers/2405.04590v1.pdf`（14 页）。
工作目录：`lit/arxiv_papers/2405.04590v1_zh/`。
交付：`lit/arxiv_papers/2405.04590v1_zh.pdf`（14 页）。

## 流水线

1. 英文基线编译：`_baseline/` latexmk -pdf -bibtex 通过（14 页，0 错误）。`sections/backgrounds.tex` 未被任何 `\input` 引用（废弃旧稿），不译。
2. 主文件按节边界切成 16 个字节级可复原片段，`sections/Preliminaries.tex` 整体 1 片段；共 15 个片段派并行译者（frontmatter 与附录引导页不译），`tools_x/check_chunk.py` 全部 STRUCT OK。
3. 摘要位于 frontmatter 片段，首轮漏译，后补译并复扫通过。
4. `cat` 拼回 `icml2023.tex` / `sections/Preliminaries.tex`，编译调通。

## 导言区改动

| 位置 | 改动 |
|---|---|
| `\documentclass` 后 | xeCJK + SimSun/KaiTi/SimHei；`\figurename/\tablename/\refname/\abstractname` 中文化 |
| `\usepackage{amsthm}` 后 | `\proofname{证明}`（amsthm 加载前 `\proofname` 未定义，不能放最前） |
| cleveref 之后 | `\crefname/\Crefname` figure/table/equation/section/appendix → 图/表/式/节/附录 |
| `\usepackage[accepted]{icml2023}` 后 | `\algorithmicrequire{输入:}`、`\algorithmicensure{输出:}`、`\floatname{algorithm}{算法}` |
| 8 个 `\newtheorem` 显示名 | Theorem→定理、Proposition→命题、Lemma→引理、Corollary→推论、Definition→定义、Assumption→假设、Remark→注、Claim→断言 |
| `\icmltitle` | 中文主标题 + 英文原题副行；`\icmltitlerunning{Language Modeling Using Tensor Trains}`（**必须用英文**：模板以 `\ht>6.25pt` 校验 running title，中文字形必超，会显示 "Title Suppressed Due to Excessive Size"） |
| `icml2023.sty`（本地副本） | `\fnum@figure/\fnum@table` Figure/Table→图/表；`\centerline{Abstract}`→摘要（sty 内硬编码，`\abstractname` 不起作用） |

## 编译与校验

- `latexmk -xelatex -bibtex`：exit 0，14 页（与英文一致），0 `!` 错误、0 Missing character；`TU/ptm` 字形替换警告为 xelatex+times 的正常替代，不影响输出。
- 漏译扫描：仅剩 xeCJK 字体配置 1 处预期项。
- 逐页 PNG（`render/p-01..14.png`）人工目检通过：双栏无重叠溢出；图 1–7、表 1–3 正常；证明/断言环境标题中文；页眉 "Published as a conference paper at ICML 2023" 与 running title 为原样保留英文；参考文献保留英文。
