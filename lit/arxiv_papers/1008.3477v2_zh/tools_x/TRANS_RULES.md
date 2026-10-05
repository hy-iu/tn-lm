# 1008.3477v2《The density-matrix renormalization group in the age of matrix product states》中译规则（每个译者必读）

英文原件（只读）：`en_parts/annals_NNN.tex`；你的译文**就地写入** `parts/annals_NNN.tex`（用 Edit/Write 替换英文段落，不要新建文件、不要编译）。
英文基线在 `_baseline/annals.tex`（76 页，已编译通过）。拼回时各片段首尾相接必须与原文逐字节等价（除译出的文字外）。

## 0. 本稿结构

- elsarticle 单栏模板，主文件一个 `annals.tex`，图全是外部 EPS（`\includegraphics{PyMPS_*.eps}`），**图代码一行不动**。
- 参考文献是文末手写 `\begin{thebibliography}`：**`\bibitem` 条目一律保持英文原样**（若你的片段含 bibitem，只译它前面的散文）。
- 有 `\tableofcontents`，标题译好即可。

## 1. 绝对不许改动

1. 一切数学：`$...$`、`\begin{equation}...\end{equation}`、`equation*`、`align`、`eqnarray`、`displaymath` 等环境内部，包括其中的 `\text{...}`、`\mbox{...}` 英文词（数学模式内不自动切中文字体，改了就丢字）。
2. 命令与环境：`\label` `\ref` `\cite` `\includegraphics` `\usepackage` `\newcommand`、宏名与宏参数、可选参数 `[...]`、`\begin{}`/`\end{}` 配对、`&`、`\\`、`\hat{}`、`\ket{}`/`\bra{}`（本稿自定义宏）。
3. 图：`\includegraphics` 整行，EPS 文件名。
4. `\bibitem{key}` 条目整体（作者、期刊、卷页、年份）。
5. 作者姓名与单位（Ulrich Schollwöck、LMU、IAS Berlin）、人名缩写（DMRG、MPS、MPO、NRG、TEBD、iTEBD、TDVP、SVD、AKLT、PBC、OBC、tDMRG、LL、FCS 等）。
6. **不得增删空行**：段落一行对一行，不得拆段/并段。行尾 `%` 注释保留。
7. 不得"顺手修正"原文拼写或语法。

## 2. 必须译为中文

正文所有段落；`\section/\subsection/\paragraph{}` 标题；`\caption{}`；脚注；`\item` 条目；`\emph{}`/`\textbf{}`/`{\em ...}` 里的英文（保留命令只换文字）。`\title{}` 改为：中文主标题 + `\\` + 英文原题副行：

```latex
\title{矩阵乘积态时代的密度矩阵重正化群\\ The density-matrix renormalization group in the age of matrix product states}
```

摘要 `\begin{abstract}` 内文译为中文。

## 3. 术语表（全篇统一，务必遵守）

| 英文 | 中文 |
|---|---|
| density-matrix renormalization group (DMRG) | 密度矩阵重正化群（DMRG） |
| matrix product state (MPS) | 矩阵乘积态（MPS） |
| matrix product operator (MPO) | 矩阵乘积算符（MPO） |
| numerical renormalization group (NRG) | 数值重正化群（NRG） |
| infinite-system / finite-system DMRG | 无限系统 / 有限系统 DMRG |
| block / superblock / site | 块 / 超块 / 格点 |
| left block, right block | 左块、右块 |
| Hilbert space | 希尔伯特空间 |
| local state space / local dimension | 局域态空间 / 局域维数 |
| bond dimension (D, m, χ) | 键维数 |
| decimation | 状态抽取 |
| truncation / discarded weight | 截断 / 丢弃权重 |
| canonical form; left/right-canonical | 规范形式；左规范/右规范 |
| mixed canonical form | 混合规范形式 |
| Schmidt decomposition | Schmidt 分解 |
| singular value decomposition (SVD) | 奇异值分解（SVD） |
| reduced density matrix | 约化密度矩阵 |
| entanglement entropy | 纠缠熵 |
| area law | 面积定律 |
| finitely correlated states | 有限关联态 |
| transfer operator / transfer matrix | 转移算符 / 转移矩阵 |
| thermodynamic limit | 热力学极限 |
| variational | 变分 |
| ground state / ground state energy | 基态 / 基态能量 |
| open / periodic boundary conditions | 开边界 / 周期边界条件 |
| sweep | 扫描 |
| effective Hamiltonian | 有效哈密顿量 |
| time evolution; real-time; imaginary-time | 时间演化；实时；虚时 |
| time-dependent DMRG (tDMRG) | 含时 DMRG（tDMRG） |
| dynamical structure function | 动力学结构函数 |
| spin chain / spin ladder | 自旋链 / 自旋梯子 |
| Heisenberg antiferromagnet | 海森堡反铁磁体 |
| strongly correlated | 强关联 |
| quantum many-body | 量子多体 |
| exact diagonalization | 精确对角化 |
| quantum Monte Carlo | 量子蒙特卡罗 |
| Bethe ansatz | Bethe 拟设 |
| matrix product state notation | 矩阵乘积态记法 |
| weight / norm / overlap | 权重 / 范数 / 重叠 |
| expectation value | 期望值 |
| correlation function | 关联函数 |

数字、单位、数学符号照抄；人名（White、Vidal、Cirac、Schollwöck、McCulloch、Verstraete 等）不译。

## 4. 自检（必做）

译完后运行：

```bash
python3 tools_x/check_chunk.py parts/annals_NNN.tex en_parts/annals_NNN.tex
```

必须通过（STRUCT OK）；如报结构漂移或残留英文，按提示修复后重跑，直到通过为止。
