# notes_preamble.md — 2608.30505v1 前言改造记录（00_preamble / 01_frontmatter / 骨架编译）

日期：2026-09-25。工作目录：`/Users/bjergsen/mnt/u26/research/tn/zh/2608.30505v1/`。
英文源（只读）：`/Users/bjergsen/mnt/u26/research/tn/2608.30505v1/survey_arxiv_version.tex`（2605 行）。

## 1. 改造点清单（parts/00_preamble.tex，对应源文件第 1–90 行）

1. **ctex**：在 `geometry` 之后、`hyperref`（原第 14 行）之前插入 `\usepackage[fontset=macnew]{ctex}`。本机字体为 macnew 方案（宋体/黑体/仿宋/楷体齐全），无需额外 `\setCJKmainfont`。
2. **microtype**：保留（原第 8 行 `[expansion=false]` 与第 18 行重复加载均保留）。XeLaTeX 下 microtype 正常加载、无报错（仅 Info 级提示 generic protrusion settings），**未移除**。
3. **xcolor 双加载**：原文件第 11、12 行连续 `\usepackage{xcolor}` + `\usepackage[table]{xcolor}`。TeX Live 2026 的 xcolor v3.02 不再报 option clash（已单独验证），但为保险仍在两者之前加了 `\PassOptionsToPackage{table}{xcolor}`（无害，可删）。
4. **cleveref 中文化**：`\usepackage[capitalize,noabbrev]{cleveref}` 保持原位（hyperref 之后）；在其后用 `\crefname`/`\Crefname` 设置：section/subsection/subsubsection→节、figure→图、table→表、equation→式、algorithm→算法、theorem→定理、appendix→附录、listing→清单、definition→定义、lemma→引理、proposition→命题、corollary→推论、remark→注记、assumption→假设。实测 `\cref` 渲染为「图 1」「式 (1)」「表 1」「节 1」「定理 1」。
5. **biblatex**：`\usepackage[backend=bibtex,sorting=none,maxbibnames=99]{biblatex}` + `\addbibresource{references.bib}` 原样保留。中文 string 用
   `\DefineBibliographyStrings{english}{bibliography={参考文献}, references={参考文献}, andothers={等}, page={页}, pages={页}}`。
   实测参考文献标题为「参考文献」，页码范围显示「页 11071–11078」。
6. **固定名称中文化**：`\figurename=图`、`\tablename=表`、`\contentsname=目录`、`\abstractname=摘要`（另加 `\AtBeginDocument` 兜底）、`\refname=参考文献`、`\appendixname=附录`。
   **注意：article 类没有 `\bibname`，重定义会报 `LaTeX Error: Command \bibname undefined`（首编即踩到，已改为注释说明）。**
7. **自定义宏全部原样保留**：`\email`、`revisionmagenta`/`\rev`、`\R \C \X \Y \W \A \T \E \G \ten \mat \vecb \rank \TTD \cp \bt \mps \mha \ffn \kv \lora \peft \set \llama`；float 参数 `\topfraction` 等、`\hypersetup`、tikz 库与 layer 声明全部保留。
8. **标题中译**（在 00_preamble 内）：`\title{面向语言模型的张量方法：从词元表示到训练、\\ 适配、压缩、推理与可解释性}`，保留原 `\\` 断行风格（两行）。
9. **作者/单位/邮箱保留英文**（authblk 结构原样）。
10. **无 `\newtheorem`**：源文件第 1–90 行及全文均无定理类环境定义与使用，故 00_preamble 不定义；骨架验证用的 `\newtheorem{theorem}{定理}` 只写在 skeleton.tex 里。若正文 parts 将来需要定理环境，请在 00_preamble 补 `\newtheorem{...}{中文}`（cleveref 的 crefname 已预置）。

## 2. parts/01_frontmatter.tex（对应源文件第 91–102 行）

- `\begin{document}`、`\maketitle`、`\begin{abstract}…\end{abstract}`、被注释的 `%\tableofcontents` 原样保留。
- 摘要全文译成中文（学术书面语，按 GLOSSARY：大语言模型（LLM）、词元、适配、预训练、推理、可解释性、嵌入、注意力、前馈网络（FFN）、张量分解、张量网络、张量化；`$\rho_{\rm gap}$` 数学内容原样）。
- 源文件第 98 行被注释掉的旧版英文摘要段落**原样保留为注释**。
- GitHub 链接 `\href{https://github.com/ma-tt-a/awesome-tensor-methods-for-llms}{this https URL}` 原样保留。

## 3. 骨架编译（skeleton.tex / skeleton.pdf 保留备查）

命令：`latexmk -xelatex -interaction=nonstopmode -file-line-error skeleton.tex`（工作目录下执行；skeleton.tex 用 `\input{parts/00_preamble.tex}` + `\input{parts/01_frontmatter.tex}` + 占位正文：\section、中文段、`\cite{zheng2021fctn}`、tikz 占位 figure+\caption+\cref、equation、tblr 小表、theorem、`\printbibliography`）。

结果（最终 run，skeleton.log）：
- 致命错误 `! `：0；`Undefined control sequence`：0；`Missing character`：0；
  `Reference … undefined` / `Citation … undefined`（逐条）：0；overfull/underfull：0。
- latexmk 退出码 0，PDF 2 页；bibtex 由 latexmk 自动跑两轮，`skeleton.bbl/blg` 正常，引用渲染为数字 `[1]`。
- 已知无害告警（**非本次改造引入**，见下）：
  1. `LaTeX Warning: There were undefined references.` + `Package biblatex Warning: Please (re)run BibTeX…`：TeX Live 2026 biblatex 的 **bibtex fallback + `sorting=none`** 组合的固有 rerun 循环。已用最小文档复现：`backend=bibtex,sorting=none` 时 xelatex/pdflatex 均出现；去掉 `sorting=none` 即消失。输出内容完全正确（引用、文献表均正常），BRIEF ③ 的 grep 模式不匹配这两条，健康度计数仍为 0。**不要为此改 sorting 或 backend。**
  2. `xdvipdfmx:warning: Object @figure.1 / @table.1 already defined`：xetex 下 hyperref 锚点名冲突的已知无害警告。
  3. fontspec Info：`Script 'CJK' not explicitly supported within font 'STFangsong'`、`Could not resolve STFangsong/B|I|BI`：ctex macnew 仿宋无粗斜体的正常提示，可忽略。
- 目检（`tools/render_pages.sh skeleton.pdf 1 2 skel` → render/skel-1.png、skel-2.png）：
  第 1 页中文标题/作者行/「摘要」/中文摘要/节标题/正文/式 (1)/定理 1 全部正常，无豆腐块、无乱码；第 2 页「图 1:」「表 1:」中文前缀、tblr 表格中文表头、「参考文献」标题与 `[1]` 数字条目正常；正文 `\cref` 显示「图 1、式 (1)、表 1 与节 1」。

## 4. 给拼装 agent 的注意事项

1. 汇总文件用 `cat parts/*.tex > survey_arxiv_version.tex`（与英文源同名）；**不要在汇总文件上直接改**，改 parts 后重新 cat。
2. cleveref 中文配置在 00_preamble 内、`\usepackage{cleveref}` 之后；若正文引入新的 cref 类型（如 `lstlisting`、`subfigure`），在同一处补 `\crefname/\Crefname`。
3. biblatex 中文 string 已用 `\DefineBibliographyStrings{english}{...}` 设置；**不要**改用 `\renewcommand{\bibname}`（article 类无此命令）。
4. 编译命令：`latexmk -xelatex -interaction=nonstopmode -file-line-error survey_arxiv_version.tex`。bibtex 会自动跑；若 latexmk 提示 rerun，可手动 `bibtex <main> && xelatex ×2`。日志里若出现第 3 节列出的三类无害告警，忽略即可；验收 grep 模式为 `Reference .* undefined|Citation .* undefined|Missing character|Undefined control sequence`，须为 0。
5. **tikz 大图**：源文有 24 处 tblr 及多幅 tikz 图；tikz 首次编译较慢（每图数秒），全文预计数分钟级，属正常；不要因慢而改 `-interaction` 或删图。`\pgfdeclarelayer/\pgfsetlayers` 已在 preamble 声明，正文 tikz 可直接用 background/foreground 层。
6. **tabularray**：`\UseTblrLibrary{booktabs}` 已加载；tblr 的 `colspec/hlines/vlines` 等键照用。注意 tblr 单元格内中文无需特殊处理，但**单元格内不要出现未转义的 `&`/`\\` 以外的裸 `%`**；长表用 `longtblr`（源文若用 `threeparttable`+`tabular` 混排亦可，两包均已加载）。
7. 正文段落缩进由 ctex 默认（2 字符）提供，不要再加 `\setlength{\parindent}`。
8. 作者批注宏：本篇源文件只有 `\rev{}`（品红色修订标记），宏保留、**其内文字要译**（见 BRIEF 第 2 节）。
9. skeleton.tex / skeleton.pdf / build.log 保留在目录中备查，拼装时**不要**把 skeleton.tex 计入 `parts/*.tex`（它不在 parts/ 下，cat 不受影响）。
