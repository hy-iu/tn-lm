# 中央术语裁定（2605.16610v1 中译，拼装后统一执行）

各并行译者的分歧由中央统一。拼装后对 `parts/*.tex` 做一次全局归一，再重编译。

| 议题 | 裁定 | 依据 |
|---|---|---|
| contraction | 收缩 | GLOSSARY.md 张量网络节（LLM 节的「缩并」不适用于本篇） |
| diagrammatic notation / graphical language / graphical notation | 图示记法 / 图形语言 | 规则文件补充表；不用「图形记法」 |
| leg（tensor network 的腿） | 腿（首次括注 English） | g2 提议，与 dangling/free leg 搭配自然 |
| node / vertex | 节点 / 顶角→顶点（本篇用「顶点」） | |
| order（张量的阶） | 阶 | |
| mode | 模 | |
| copy tensor / hyperedge | 复制张量 / 超边 | |
| bond dimension | 键维数 | GLOSSARY.md |
| reshaping | 重排 | |
| matricization / flattening / unfolding | 矩阵化 / 展开 | |
| vectorization | 向量化 | |
| core tensor / factor matrix | 核心张量 / 因子矩阵 | |
| tensor train (TT) | 张量列（TT） | GLOSSARY.md |
| MPS / MPO | 矩阵乘积态 / 矩阵乘积算符 | GLOSSARY.md 张量网络节（不用「矩阵积态」） |
| Isserlis' theorem / Wick's theorem | Isserlis 定理 / 威克定理 | 人名专名保留拉丁；Wick 按 GLOSSARY 已有「威克定理」 |
| Born machine | Born 机器 | |
| Kronecker / Hadamard / Khatri-Rao / Frobenius / Schmidt / Tucker / Parafac | 人名保留拉丁，只译 product/norm/decomposition | 与 GLOSSARY「Bethe 拟设 / Hartree-Fock / Fredholm 方程」一致 |
| tracing out | 求迹（不用「迹掉」） | g4 提议「迹掉」偏口语；partial trace 已定为「部分迹」 |
| hyper-diagonal tensor | 超对角张量 | g4 |
| all-ones vector | 全 1 向量（写作 `全 1 向量`，不引入额外 `$`） | g4 为守住 `$` 计数刻意不加数学模式 |

## 检测器已知误报

`check_chunk.py` 的 `RESIDUAL ENGLISH` 会命中数学模式内的 `\text{times}`、`\text{otherwise}`、`\text{if}` 等（共 79 处 / 57 种，见下），这些按规则 1 必须保留英文，不视为漏译；最终报告用 `check_untranslated.py`（整篇级、豁免数学行）复核。


## 译者报告的原文问题（一律不改，仅记录）


- g2 / chapter2_basics_001.tex:19 —— 原文 "a tensor a matrix and a vector products" 有漏字，按语义译出。
- 全篇 52 处 `};;`（TikZ 里多写一个分号）：原样保留。它导致 xelatex 报 `Missing character ... in font nullfont`，英文原件用同一台机器同一引擎编译（`_baseline/main.log`）报同样的错，属上游笔误，非译稿引入。
- macros.tex 第 719 行 `\ifx\BlackBox\undefined` 缺 `\fi`（上游笔误，英文基线同样报 `\end occurred when \ifx ... was incomplete`）。为使 latexmk 正常退出，补了一个 `\fi`：该条件为真分支，补 `\fi` 后所有被条件包含的宏仍照常执行，PDF 内容不变（已用页数 55=55 与首页文本核对）。
- macros.tex 的 `microtype`：XeLaTeX 下与 Type1 `TS1+ptm` 冲突，报 `Cannot use XeTeXglyph with ptmr8c` + `Missing number, treated as zero` 致命错误，已在译稿中注释停用（英文基线未触发，因为未加载 xeCJK/fontspec）。

## 译者报告的原文疑点（按规则未改，供 VERIFY.md 引用）

- g3 / chapter2_basics_002.tex:77 —— `\draw[edge] (A) -- (B)` 引用的节点名在该 tikz 块里是 `a`、`b`，`A`/`B` 未定义；英文基线同样编译通过（节点由前文 picture 继承），未改。
- g3 / chapter2_basics_002.tex:133/140/153 —— `;;` 笔误。
- g2 / chapter2_basics_001.tex:19 —— "a tensor a matrix and a vector products" 漏字，按语义顺译。
- g4 / chapter2_basics_006.tex:191 —— "Since ... because ..." 双重因果病句，按语义顺译。
- g8 / chapter3_operations_008.tex:32 —— 映射写作 `\RR^d\to\RR^m`，但张量最后一模与结果维度均为 $p$，疑为原文笔误，未改。
- g14 / chapter5_gradients_000.tex:36 —— 公式后 `，。` 标点冗余；:183 `network. i.e.,` 句号后接 i.e.；:243 `\vectorize(\Gb_4)` 疑为 `\Gt_4`。均未改。
- g17 / chapter6_..._004.tex:116,142 —— 孤立的 `0.5);`；005:223 多余右括号 `$(\Ab^\ts\Ab)^{\outprod 2}))$`。均未改。

## 正文不引入裸希腊字母

g1 实测：导言区是 xeCJK + T1 编码 Type1 Times，正文模式没有希腊字形，写 `δ` 会触发 `Missing character`（静默丢字）。因此「Kronecker δ」一律写作「Kronecker delta 记号」，需要符号时用 `$\delta$`（会改变 `$` 计数，须同步放宽 check_chunk 的 dollars 比对）。已裁定：保持 g1 的写法。


