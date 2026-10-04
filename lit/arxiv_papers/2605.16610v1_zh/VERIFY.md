# VERIFY.md — 2605.16610v1《Tensor Cookbook: Mastering Tensors through Diagrams》中译校对记录

日期：2026-09-27。
英文源（只读，未改动）：`/Users/bjergsen/mnt/u26/research/tn/2605.16610v1/`（`main.tex` + `macros.tex` + 8 个 `chapter*.tex`，共 9787 行）；英文参考 PDF：`/Users/bjergsen/mnt/u26/research/tn/2605.16610v1.pdf`（55 页）。
工作目录：`/Users/bjergsen/mnt/u26/research/tn/zh/2605.16610v1/`。
交付：本目录中文源码 + `../2605.16610v1.pdf`。

## 流水线（与 BRIEF 第 4 节一致）

1. `cp -R` 英文源到工作目录，另存一份纯净副本 `_baseline/` 用于**英文基线编译**（区分上游缺陷与译稿引入的问题）。
2. `tools_x/split_chunks.py` 把 8 个章文件切成 **45 个结构安全片段**（`en_parts/` 为英文原件，`parts/` 为待译副本）。切点只在「环境全闭合 + 花括号平衡 + `$`  parity 为偶 + 不在 tikzpicture/tabular/align/float 内」处；脚本 `assert` 拼回后与源文件逐字节相同（已 8/8 验证 `OK`）。
3. 18 个并行译者各自**就地 Edit** 自己那 2–4 个片段，用 `tools_x/check_chunk.py` 自检（环境序列 / label-ref-cite 键多重集 / `$` 计数 / equation 数 必须与英文片段完全一致，且无「不含汉字的英文散文行」）。
4. `tools_x/normalize.py` 做中央术语归一（分歧裁定见 `tools_x/TERM_DECISIONS.md`）。
5. `tools_x/assemble.sh` 拼回 8 个 `chapter*.tex`，生成 `tools_x/flat_en.tex` / `flat_zh.tex`，跑 parity 与漏译检查。
6. `latexmk -xelatex` 编译到干净，再跑五项校验。

## 0. 导言区改动（BRIEF 第 3 节授权，逐项记录）

| 位置 | 改动 | 原因 |
|---|---|---|
| `macros.tex` 首行前 | 新增 `\usepackage{xeCJK}` + `\setCJKmainfont{Songti SC}[ItalicFont={Kaiti SC}]` | 中文支持；置于 `hyperref` 之前。沿用本项目既有译稿的字体写法（不切 ctex：实测 ctex 的 macnew fontset 会整篇重排并引入已失效的 STFangsong 依赖） |
| `macros.tex` | `\usepackage{microtype}` 注释停用 | XeLaTeX 下 microtype 与 Type1 `TS1+ptm` 冲突，报 `Cannot use XeTeXglyph with ptmr8c; not a native platform font` + `Missing number, treated as zero`，**致命**（xelatex 返回 1，latexmk 中断，bibtex 不运行 → 58 条 citation 全 undefined）。英文基线未加载 xeCJK/fontspec，故不触发 |
| `macros.tex` | 补 `\ifx\BlackBox\undefined` 缺失的 `\fi` | 上游笔误：英文基线日志同样报 `\end occurred when \ifx on line 714 was incomplete`。该条件为真分支，补 `\fi` 后条件内的宏照常执行，PDF 内容不变（页数 55=55、首页文本一致核对通过） |
| `macros.tex` | 15 处 `\newtheorem{...}{英文名}` 的显示名改中文（定理/引理/命题/推论/定义/注/例/性质/步骤/猜想/公理/断言/假设） | 这些字符串会在 PDF 中显示 |
| `macros.tex` 末尾 | 新增 `\renewcommand{\proofname}{证明}`、`\contentsname{目录}`、`\figurename{图}`、`\tablename{表}`、`\refname{参考文献}`、`\appendixname{附录}` | amsthm 已定义 `proof`，其环境走 `\ifx` 假分支，须显式改名；其余为 article 类固定名 |
| `main.tex` | `\renewcommand{\bibname}{References}` → `{参考文献}` | 同上 |
| `main.tex` | `\title{}` 改「张量手册：通过图示精通张量」+ 第二行括注英文原题 | 题名要译；保留英文原题便于检索 |
| `main.tex` | `\input{macros.tex}` 后新增 `\setlength{\parindent}{2em}` | BRIEF 要求中文首行缩进 2 字符 |

未改动：`\usepackage[utf8]{inputenc}`（xelatex 下仅警告 "inputenc package ignored with utf8 based engines"）、`[T1]{fontenc}`、`lmodern`、`times`（保留 Times 正文外观，避免重排）。

## 1. 上游缺陷（英文原件即有，非译稿引入）

1. **52 处 `};;`**（TikZ 路径结束符多写一个 `;`）→ xelatex 报 `Missing character: There is no ; ("3B) in font nullfont`。英文基线 `_baseline/main.log` 同样报 145+ 条，逐条同因。按 BRIEF「不得顺手修正」原样保留，故本译稿的 `Missing character` 计数**不为 0**，这是 BRIEF 第 3 节合格标准第 4 条唯一未达项，性质为上游遗留、不影响输出（nullfont 下该字符本就被丢弃）。
2. `macros.tex` 缺 `\fi`（已在上表说明，为可编译性而补）。
3. 各片段译者报告的原文语病/笔误（标点和而不改）：见 `tools_x/TERM_DECISIONS.md` 末节。

## 2. 五项校验

### ① 结构一致性 parity.py —— PASS

```
$ python3 ../tools/parity.py tools_x/flat_en.tex tools_x/flat_zh.tex
结构一致性: PASS（环境计数、label/cite/ref 集合、图件列表全部一致）
  环境数: align=15, align*=87, array=2, bmatrix=5, cases=8, center=2, definition=8,
          enumerate=11, equation*=1, figure=1, itemize=8, pmatrix=2, proof=20,
          proposition=15, remark=8, table=2, tabular=3, theorem=6, tikzpicture=412
  \label=58 \cite=4 \ref=65 \includegraphics=0
```
`flat_en.tex` / `flat_zh.tex` 是把 `macros.tex` + 8 个章文件按 `\input` 顺序摊平成的整篇对照文件（脚本见 `tools_x/assemble.sh`）。
另：45 个片段逐一通过 `tools_x/check_chunk.py`（环境序列 / label-ref-cite 键多重集 / `$` 计数 / equation 数与英文片段完全一致），18 位译者的原始输出已逐条回收，全部 `STRUCT OK`。

### ② 漏译检查 —— 通用工具 408 命中，逐类判读后实质 PASS

```
$ python3 ../tools/check_untranslated.py tools_x/flat_zh.tex
漏译检查: FAIL — 发现 408 处疑似未翻译的英文段落：
  tools_x/flat_zh.tex:1116  \tikzset{tensor/.style = {minimum size = 0.5cm,shape = circle,...}}
  ...
```
408 条按类型统计（复用工具自身的 `is_prose()` 判定，逐行分类）：

```
总命中 408
   407  \tikzset 样式行（minimum size / shape = circle / thick, draw=black / line width=.4mm 等 TikZ 键值）
     1  TikZ 绘图命令行
     0  真英文散文
```
本篇有 **412 个 `tikzpicture`**，每个都以同一行 `\tikzset{tensor/.style={...}}` 开头；通用工具把 `style = {minimum size = 0.5cm, shape = circle, ...}` 的键值当成"6 个连续英文词"，故全部误报。这些行按 BRIEF 第 2 节第 2 条属于"命令与键名不得改动"。
为此另写 TikZ 感知版并复跑：

```
$ python3 tools_x/check_zh_prose.py tools_x/flat_zh.tex
漏译检查(TikZ 感知): PASS — 无「不含汉字的英文散文行」
```
（它先把 412 个 tikzpicture 整块、行内数学、TikZ 命令抹掉，再用与通用工具相同的"无汉字 + 6 连续英文词 / 60 拉丁字母"判据。）

### ③ 编译健康度 —— latexmk 正常结束，致命项全 0

```
$ latexmk -xelatex -interaction=nonstopmode -file-line-error main.tex
exit=0
$ grep -cE 'Reference .* undefined|Citation .* undefined|Undefined control sequence' main.log
0
$ grep -cE '^! ' main.log
0
$ grep -c 'Missing character' main.log
144
$ grep 'Missing character' main.log | grep -vc nullfont      # 非 nullfont 丢字
0
$ grep -c 'Overfull \hbox' main.log        # 中文稿
10
$ grep -c 'Overfull \hbox' _baseline/main.log   # 英文基线同引擎
7
```
- 无 `! ` 致命错误、无 `Undefined control sequence`、undefined ref/citation 计数 **0**（`bibtex` 正常，39 条 `bibitem` 全部解析）。
- `Missing character` 144 条**全部**是 `in font nullfont`，来自原文 52 处 `};;` 笔误（见第 1 节），英文基线同引擎同机器报同一批；**非 nullfont 的丢字为 0**，即没有任何汉字/标点缺字形（无豆腐块）。此项为 BRIEF 合格标准第 4 条唯一未达项，性质是上游遗留、不影响输出。
- overfull 仅比英文基线多 3 条，且目视未见图表跑出页外。

### ④ 视觉校对（`tools/render_pages.sh` 渲染 PNG 后逐页目视）

| 页 | 内容 | 结论 |
|---|---|---|
| 1 | 标题页 | 「张量手册：通过图示精通张量」+ 英文原题 + 作者/单位原样（Mila & DIRO、Université de Montréal、CIFAR AI Chair） |
| 2 | 目录 | 「目录」+ 6 个中文章题与 1.1–5.2 小节号、页码正常 |
| 3 | 记号表 | 表格左列数学符号、右列中文释义，`ll` 列未溢出 |
| 12 | 复制张量/偏迹 | 中文正文 + 图 + `命题 2.` + `\text{if } i=j=k` 保留英文（数学内） |
| 28 | 定义 4 / TT 分解 | `定义 4.`、`证明`、脚注中文、图内 `$\text{is left-orthogonal}$` 保留英文 |
| 33 | TT-SVD / 张量环 / PEPS | 中文正文、图内 `merge & apply rank-$R_2$ SVD` 等标签保留英文、`\citet` 蓝色引用正常 |
无豆腐块、无乱码、公式与图件完整，汉字为宋体（Songti SC），`\emph{中文}` 走楷体斜体。

### ⑤ PDF 级对比（英文 PDF vs 中文 PDF）

```
$ python3 ../tools/compare_pdf.py ../../2605.16610v1.pdf main.pdf
指标                     英文         中文
页数                     55         50  ok
可提取文字量             117743      61334
汉字数                     0      19015
汉字占比                0.000      0.310
拉丁字母数               82046      15874
嵌入图像数                   0          0
图标题(英式)                 2          0
图标题(中式)                 0          2
表标题(英式)                 2          0
表标题(中式)                 0          2
中文 PDF 汉字占比: 0.310
--- 中文 PDF 中疑似残留的英文散文 --- 共 17 行（全部为参考文献条目）
```
- 页数 55 → 50（**−9.1%**，在 ±25% 内；中文更紧凑，且未删任何内容）。
- 图题 2=2、表题 2=2；`\includegraphics` 两侧均为 0，图件全部是 `tikzpicture`，源码侧 412=412（见 ①）。
- 编号一一对应（从两份 PDF 正文抽取比对）：编号公式 15=15（最大 15）；`Theorem/定理` 出现号集 {3,9,14,17,19,20,27} 相同；`Proposition/命题` 15 个号集相同；`Remark/注` 8 个号集相同；`Definition/定义` 8=8（中文侧"定义 4"因 xdvipdfmx 逐字定位导致 pypdf 抽成"定 义 4"，已渲染第 28 页目视确认存在且无异常字距）；`Corollary/推论` 0=0。
- 残留 17 行英文全部是 `biblio.bib` 生成的参考文献条目，按 BRIEF 第 2 节第 4 条保留英文。

## 3. 保留未译项清单（逐项理由）

| 项 | 数量 | 依据 |
|---|---|---|
| 参考文献条目（作者/题名/期刊/年份） | 39 条 | BRIEF：参考文献保持英文是学术惯例；仅把区标题改成「参考文献」 |
| 作者姓名与单位、基金号（RGPIN-2019-05949、IVADO、CIFAR AI chair program、Discovery program） | — | BRIEF 第 2 节第 3 条 |
| 数学环境内的 `\text{}` 英文（`and`、`otherwise`、`for all`、`then`、`diag`、`const`、`times`、`mode-n matricization`、`reshape`、`merging`、`factorizing`、`is left-orthogonal`、`step:~1` 等） | 32 种 / 约 40 处 | BRIEF 第 2 节第 1 条：`$...$` 与数学环境内部一律不改 |
| 图内 `\node` 数学标签与 `\underrightarrow{\text{...}}` 步骤说明（`merge & apply rank-$R_2$ SVD`、`Keep $\Qb_1$, resume with $\Rb_1$`、`truncated SVD of`） | 若干 | 同上：位于数学模式内 |
| 人名专名（Kronecker、Hadamard、Khatri-Rao、Frobenius、Schmidt、Tucker、Candecomp、Parafac、Isserlis、Born、Wishart、Sylvester、Eckart–Young） | — | 与 GLOSSARY「Bethe 拟设 / Hartree-Fock / Fredholm 方程」同一处理方式 |
| 缩写与软件名（TT、CP、MPS、MPO、SVD、HOSVD、ALS、PEPS、TR、HT、TTN、QR、TN、NP、LaTeX、TikZ、Python、numpy、`ravel()`） | — | BRIEF 第 2 节第 5 条 |
| `\label`/`\ref`/`\cite` 键名、环境名、包名 | 全部 | BRIEF 第 2 节第 2 条 |

## 4. 术语统一与中央裁定

`tools_x/normalize.py` 在拼装前做了一次全局归一（先 dry-run 复核命中上下文，再 `--apply`），实际生效 12 项：
`部分迹→偏迹 ×5`、`图形记法→图示记法 ×4`、`克罗内克 δ→克罗内克 $\delta$ ×3`、`自成一体→自成体系 ×2`、`图形演算→图示演算`、`图形证明→图示证明`、`自边→自环边`、`归并边→归并腿`、`悬腿/悬空边→悬空腿`、`NP-难/NP 困难→NP 难`。
其中 `克罗内克 δ` 必须回到数学模式：正文是 T1 编码 Type1 Times，无希腊字形，裸 `δ` 会静默丢字（这 3 处也是唯一因此使 `$` 计数 +6 的改动，已在此说明，不影响其他结构校验）。
另有两项**故意不做**全局替换（`缩并→收缩`、`迹掉→求迹`）：前者唯一命中是「张量收缩并合并为」中"收缩+并"的巧合子串，替换会产生「收缩收缩」；后者需要整句改写，已手工改为「即对 $d_1$ 这一维``求迹''而得到」。
完整裁定表与分歧来源见 `tools_x/TERM_DECISIONS.md`。

## 5. 已知问题与残留风险

1. **`Missing character ... nullfont` 144 条未清**：上游 `};;` 笔误所致，英文基线同样报，按"不得顺手修正"保留。若要清零，只需把 8 个章文件里 52 处 `};;` 改成 `};`，不影响任何可见输出。
2. **术语轻微不一致**：`leg` 多数译「腿」，个别句子（ch3 开头一处、ch6 一处）按上下文写成「边」；`edge` 亦作「边」。已对高频形式做归一，剩余属语义可辨范围。
3. **GLOSSARY.md 自身冲突**：`contraction` 在张量网络节作「收缩」、在 LLM 节作「缩并」；`MPS` 在第 12 行作「矩阵乘积态」、第 242 行作「矩阵积态」。本篇按张量网络节取「收缩 / 矩阵乘积态」。
4. **图内英文标签**（如 `merge & apply rank-R2 SVD`）在 PDF 中可见但处于数学模式内，未译。若需中文化，须逐处把 `\text{}` 内容改为汉字并实测 xeCJK 在 `\text` 内的行为，属可做的后续增强。
5. **原文 5 处疑误未改**（见 `tools_x/TERM_DECISIONS.md` 末节），译文按上下文顺译，未添加"原文有误"式脚注——那属于超出翻译范围的改动。
6. `tn/` 整棵树在 `.gitignore` 内，本目录源码与产物**无 git 兜底**；`main.bbl` 为 bibtex 生成物（39 条），重编译若被 latexmk 截断需重跑 `bibtex main`。

## 6. 交付物

- `tn/zh/2605.16610v1/`：中文源码（`main.tex`、`macros.tex`、8 个 `chapter*.tex`、`parts/` 45 个片段、`en_parts/` 英文对照、`tools_x/` 脚本与本记录、`biblio.bib`、`TN_figures/`、`_baseline/` 英文基线构建）。
- `tn/zh/2605.16610v1.pdf`：中文成稿，50 页，707 KB。
- 完成度：**8/8 章、45/45 片段全文翻译**，非节译；五项校验中 ①③(致命项)④⑤ 通过，② 在通用工具下为误报、经分类判读与 TikZ 感知版复核为无漏译，唯一未达标的硬性项是 ③ 中"无 Missing character"（上游 `;;` 遗留，已量化并给出清零办法）。

