# 2606.03465v1 中译工程 —— 前言/标题页/骨架 笔记

## 1. brainlab.sty 机制要点

- **hyperref 加载位置**：brainlab.sty 内部 `\RequirePackage[...]{hyperref}`（natbib 之后、cleveref 之前）。因此 `\usepackage[fontset=macnew]{ctex}` 必须放在 `\usepackage{brainlab}` **之前**（parts/00_preamble.tex 已如此）。
- **参考文献打印**：tex 主文件里没有显式 `\bibliography`。`\end{mainpart}` 时自动调用 `\brainprintbibliography`（sty 内定义：`\bibliographystyle{plainnat}` + `\bibliography{references}`，bibfile 选项实际未被该宏使用，硬编码为 references）。natbib + bibtex，latexmk 会自动跑 bibtex；参考文献区标题走 `\refname`，已在 AtBeginDocument 重定义为「参考文献」。
- **mainpart / appendixpart**：
  - `\begin{mainpart}` 展开为 `\maketitlebox`（标题框：标题+logo、作者、单位、`*Equal contribution`、摘要全文）；`\end{mainpart}` 打印参考文献（twocolumnmode 时再 `\onecolumn`）。
  - `\begin{appendixpart}` = `\clearpage` + `\appendix` + 一个 tcolorbox 横幅（原硬编码 "Appendix" + 英文论文标题，已改为「附录」+ `\papertitle`）。
- **图表前缀**：caption 包用 `\figurename`/`\tablename`；brainlab 加载 `babel[english]`，会在 `\begin{document}` 把名称重置为英文，故 00_preamble 用 `\AtBeginDocument{...}`（注册晚于 babel 的钩子、执行更晚）重断言中文名。
- **定理前缀**：`\DeclareBrainTcbTheorem{theorem}{Theorem}` 等把英文名作为 tcolorbox 标题的字面参数硬编码，**无法从 preamble 用 \renewcommand 覆盖**，只能改 sty 副本（已改，见 diff）。证明环境是 amsthm 的 proof，前缀走 `\proofname`（AtBeginDocument 已改「证明」）。
- **标题页 logo**：`\maketitlebox` 里 `\includegraphics{logos/brain_logo.pdf}` + `logos/brain.pdf`，相对路径，编译目录需保留 logos/。
- **段落版式**：brainlab 设 `\parindent=0pt`、`\parskip=0.5em`（无首行缩进、段间空行式）。与英文 PDF 一致，**保留不改**；BRIEF 里「首行缩进 2 字符」与原版版式冲突时以原版为准（本篇为 parskip 风格）。

## 2. 对 brainlab.sty 副本的全部改造（diff 见 brainlab.sty.diff，shortcuts.sty 未动）

1. `inputenc`/`fontenc[T1]` 用 `\ifpdftex … \fi` 包裹（XeLaTeX 下不加载；T1 在 xelatex 下会把 encodingdefault 从 TU 改回 T1，破坏 xeCJK 字体查找）。
2. 定理族名称中文化：Theorem→定理、Assumption→假设、Definition→定义、Proposition→命题、Corollary→推论、Lemma→引理、Remark→注记。
3. appendixpart 横幅：`Appendix` → `附录`；硬编码英文标题 → `\papertitle`（即中文标题）。
4. `*Equal contribution` → `*同等贡献`。
5. 未改：algorithm 环境标题仍为 "Algorithm~"（本篇正文未使用 algorithm 环境；若后续需要请同样中文化）。

## 3. parts/00_preamble.tex 的改造点

- `\documentclass[11pt]{article}` + brainlab 选项（shownumpages / citingstyle=numbers / bibliostyle=plainnat / bibfile=references）原样保留。
- `\usepackage[fontset=macnew]{ctex}` 置于 brainlab 之前（先于 hyperref）。
- **字体修复（关键坑，必须在 brainlab 之后执行）**：
  - 本机缺 macnew 预设的等宽中文字体 STFangsong → `\setCJKmonofont{Songti SC}`；
  - brainlab 加载的 newtxtext 会全局 `\defaultfontfeatures{Extension=.otf, Scale=...}`，污染其后一切 fontspec/xeCJK 字体声明（按文件名 "Songti SC.otf" 查找而报 "cannot be found"）→ 设 CJK 等宽字体前先 `\defaultfontfeatures{}` 清空。顺序：`\defaultfontfeatures{}` → `\setCJKmonofont{Songti SC}`，且必须放在 `\usepackage{brainlab}` 之后。
- `\AtBeginDocument` 重断言：figurename 图 / tablename 表 / refname、bibname 参考文献 / abstractname 摘要 / contentsname 目录 / appendixname 附录 / listfigurename、listtablename / proofname 证明。
- `\setbrainmeta`：title、abstract 译中文（abstract 按 GLOSSARY「LLM 张量方法」组）；authors、affiliations 保留英文。

## 4. 骨架编译命令与结果

```
cd /Users/bjergsen/mnt/u26/research/tn/zh/2606.03465v1
cat parts/00_preamble.tex parts/01_frontmatter.tex > skeleton.tex   # 再追加占位正文
latexmk -xelatex -interaction=nonstopmode -file-line-error skeleton.tex
```

结果（2026-09-25）：exit=0；`! ` 致命错误 0；Undefined control sequence 0；Missing character 0；Reference/Citation undefined 0；Overfull 0。bibtex 由 latexmk 自动运行，skeleton.bbl 正常。残留警告（均可接受）：
- `LaTeX Font Warning: Font shape TU/zi4/m/n undefined`（inconsolata 的 Type1 字体在 TU 编码下无对应，\texttt/\url 回退 Latin Modern tt；仅外观差异）；
- `Package xeCJK Warning: Redefining CJKfamily \CJKttdefault (STFangsong)`（ctex 的 AtBeginDocument 钩子仍会声明 STFangsong 族，但从未真正加载，无害）。

目检（render/zh-skel2-*.png）：中文标题两行+logo 正常、摘要中文无豆腐块、`* 同等贡献`、节标题「1 测试」、定理框「定理 1 (测试定理)」、证明前缀「证明」、图注「图 1:」、表注「表 1:」、参考文献区标题「参考文献」、附录横幅「附录」+中文标题。均正确。

## 5. 给拼装 agent 的注意事项

1. **拼接方式**：`cat parts/*.tex > brain_one_column.tex`（与英文源同名）。parts/01 已含 `\begin{document}\begin{mainpart}\allowdisplaybreaks\vspace{-8mm}`，**正文片段不要再重复这四行**（我曾因重复 `\vspace{-8mm}` 导致节标题压到标题框下边框上）。
2. **正文从 `\section{...}` 开始**；结尾结构为 `\end{mainpart}` + `\begin{appendixpart} … \end{appendixpart}` + `\end{document}`（参考文献由 \end{mainpart} 自动打印，勿手写 \bibliography）。
3. 编译命令：`latexmk -xelatex -interaction=nonstopmode -file-line-error brain_one_column.tex`；bibtex 自动。
4. 图表引用文字请写「图 N」「表 N」（编号与英文 PDF 一致）；定理类引用文字写「定理/命题/推论/引理/注记 N」。正文未用 \cref/\autoref，无需 cleveref 中文名。
5. `\captionof{figure}{...}`（源文件 268、1703、1720 行）依赖 caption 包，可用；wrapfigure 可用。
6. 数学宏全部来自 shortcuts.sty（未改动），如 \cX \R \norm \expect \trans \defeq 等可直接用。
7. 作者批注宏：本篇源码中可见批注宏仅标题页 `\equalcontrib`（已中文化为「同等贡献」）；正文若出现其他会显示的批注宏请翻译其文字。
8. 若正文出现 `\texttt{中文}` 或 tt 族中文，会触发 STFangsong 缺失报错——请避免在 \texttt/\verb 中放中文，或改用 \textsf。
9. 00_preamble 中 `\defaultfontfeatures{}` 之后**不要再加载 newtx 系包**；若需新增字体声明，放在 `\defaultfontfeatures{}` 之后。
10. 图件路径 `emnlp/figs/*.pdf`、logo 路径 `logos/*.pdf` 均为相对路径，编译目录即 zh/2606.03465v1/，勿移动。
