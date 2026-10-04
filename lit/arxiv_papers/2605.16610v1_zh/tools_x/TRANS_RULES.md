# 2605.16610v1《Tensor Cookbook》中译规则（每个译者必读）

工作目录：`/Users/bjergsen/mnt/u26/research/tn/zh/2605.16610v1/`
你只翻译分配给你的 `parts/*.tex` 片段，**就地修改**（用 Edit 替换英文段落，不要新建文件、不要编译）。

## 0. 这篇稿子的结构特点（决定你的操作方式）

- 全文图件都是**行内 TikZ**（`\begin{tikzpicture}...\end{tikzpicture}`），篇幅极大，但其中**只有坐标、样式、`$数学$` 标签**，一律不动。
- 章文件由 `main.tex` 用 `\input{chapterN_...}` 串起来；你的片段拼回原文时**必须逐字节等价**（除了你译出的文字）。
- 大量 `\begin{definition}/\proposition/\theorem/\proof/\remark` 定理环境：**环境名、`\label`、计数器一律不动**，环境内的英文正文要译。
- 作者批注宏（`\guillaume` 等）在正文中未被使用，不存在要译的批注。
- 参考文献由 `biblio.bib` + natbib 生成，**你不需要也不许碰 `biblio.bib`**。

## 1. 绝对不许改动

1. 一切数学：`$...$`、`$$...$$`、`\begin{equation}/\align/...` 环境内部，**包括其中的 `\text{otherwise}`、`\text{reshape}`、`\text{diag}` 等英文词**（数学模式内不自动切中文字体，改了就丢字）。
2. 命令与环境：`\label` `\ref` `\eqref` `\cite/\citet/\citep` `\includegraphics` `\input` `\usepackage`、宏名、宏参数、可选参数 `[...]`、`\begin{}`/`\end{}` 配对、`&` `\\` 分隔符。
3.  TikZ 代码整体：`\node` `\draw` `\draw[edge]` `\tikzset` `\def\x` `\scalebox` 参数、坐标、颜色名。
4. 表格结构：`\begin{tabular}{ll}` 列格式、`&`、`\\`。
5. 作者姓名、单位（Mila、DIRO、Université de Montréal、CIFAR AI Chair）、专名缩写（TT、CP、MPS、MPO、SVD、HOSVD、ALS、PEPS、QR、CNN、RNN、GPU、TikZ、LaTeX、arXiv、SciPost、ITensor、DMRG）。
6. **不得增删空行**，不得将一段拆成两段、不得把两段并成一段（段号与行结构要可核对）。
7. 不得"顺手修正"原文的拼写/语法/`;;` 之类的笔误。

## 2. 必须译为中文

正文所有段落、`\section/\subsection/\subsubsection/\paragraph{}` 标题、`\caption{}`、表格中的文字单元格、脚注、`\item` 条目、`\textbf{}`/`\emph{}`/`\textit{}` 里的英文（保留命令，只换文字，如 `\emph{vectorization}` → `\emph{向量化}`）、`\textblock`/`\subref` 之外的说明文字。

- 图注里的 "Fig. 1: ..." 只译文字，编号不改。
- `\node[...] (...){some english words};` 若为**非数学**的纯英文说明词，可译（例：`\node{reshape}` → `\node{重排}`）；含 `$...$` 的节点只动其中英文单词部分，没有英文单词就不动。
- 数学式后的英文连接词若出现在正文行（如 "where ... is ..."）要译。

## 3. 术语（`../GLOSSARY.md` 优先；下表是它没有的、本篇高频词）

| 英文 | 中文 |
|---|---|
| copy tensor | 复制张量 |
| hyperedge | 超边 |
| (tensor) order | 阶（张量的阶） |
| mode | 模 |
| fiber / slice | 纤维 / 切片 |
| matricization / flattening / unfolding | 矩阵化 / 展开 |
| vectorization | 向量化 |
| mode-$n$ product | 模 $n$ 乘积（保留数学模式内的 `$n$`） |
| core tensor | 核心张量 |
| factor matrix | 因子矩阵 |
| rank-one tensor | 秩一张量 |
| cut set / cut | 割集 / 割 |
| diagrammatic notation / graphical language | 图示记法 / 图形语言 |
| index notation | 指标记法 |
| Kronecker delta | 克罗内克 δ |
| Khatri-Rao / Hadamard / Kronecker product | Khatri-Rao 积 / Hadamard 积 / Kronecker 积（人名保留拉丁） |
| Frobenius norm | Frobenius 范数 |
| Eckart–Young | Eckart–Young |
| Isserlis' theorem | Isserlis 定理 |
| Born machine | Born 机器 |
| marginal / conditional distribution | 边缘分布 / 条件分布 |
| normalisation / normalise | 归一化 |
| expectation | 期望 |
| standard normal distribution | 标准正态分布 |
| multivariate | 多元 |
| orthonormal | 标准正交 |
| column/row space | 列空间 / 行空间 |
| pseudo-inverse | 伪逆 |
| computational complexity | 计算复杂度 |

规则：**人名构成的专名保留拉丁**（Kronecker、Hadamard、Frobenius、Schmidt、Isserlis、Betti…），只把 product/theorem/norm 等普通名词语译成中文；这与 `GLOSSARY.md` 里 "Bethe 拟设 / Hartree-Fock / Fredholm 方程" 的处理一致。
首次出现的关键术语写成「中文（English, 缩写）」，其后用中文或缩写。例：「张量网络（tensor network, TN）」。

## 4. 文风

- 学术书面中文，短句、少"的"字堆叠，不要机翻腔（避免"这是被做成的""对于……来说它"）。
- 中英混排用中文标点；**数学环境内部的标点（逗号、句号）不动**；正文中原文紧跟公式的 `,` `.` 用中文「，」「。」。
- 引用写法：图 3、式 (5)、表 I、第 2.1 节、文献 [12]；编号一律不改。
- 段落首行缩进由导言区统一处理，**不要**在正文里加 `\par`、`\noindent`（原文已有的保持原样）。
- `\RR`、`\Tt`、`\Ab` 等宏是数学符号，原样保留。

## 5. 每个片段完成后自检（必做，把输出贴进你的最终回复）

```bash
cd /Users/bjergsen/mnt/u26/research/tn/zh/2605.16610v1
python3 tools_x/check_chunk.py parts/<你的片段>.tex en_parts/<同名>.tex
```
要求最后一行是 `STRUCT OK`，且 `RESIDUAL ENGLISH` 为空（或仅剩你判定应保留英文的专名，需在回复中逐条说明理由）。
`NOTE blank lines` 若出现，说明你动了段落结构，必须改回去。

## 6. 回复格式（不要贴大段正文）

1. 处理的文件名列表 + 每个文件 `STRUCT OK/FAIL` 与残留英文行数。
2. 你新造或拿不准的术语（英文 → 你的译法），逐条列出，供中央统一。
3. 任何你认为原文有问题、但你按规则未改的地方（一句话即可）。
