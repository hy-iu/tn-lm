# VERIFY — 2512.24390v2《Les Houches Lecture Notes on Tensor Networks》中文译本

- 英文源：`/Users/bjergsen/mnt/u26/research/tn/2512.24390v2/`（只读，100% 保持未改动）
- 英文参考 PDF：`/Users/bjergsen/mnt/u26/research/tn/2512.24390v2.pdf`（81 页）
- 中文工作目录：`/Users/bjergsen/mnt/u26/research/tn/zh/2512.24390v2/`
- 中文交付 PDF：`/Users/bjergsen/mnt/u26/research/tn/zh/2512.24390v2.pdf`（77 页）
- 编译方案：`latexmk -xelatex -interaction=nonstopmode -file-line-error main.tex`
- 中文宏包：`\usepackage[fontset=macnew]{ctex}` 置于 `hyperref` 之前，兼容 `SciPost.cls`。

## 1. 页数与宏观对比

| 指标 | 英文原版 | 中文译版 | 差异 |
|---|---|---|---|
| 总页数 | 81 页 | 77 页 | -4 页（-4.9%，< 25% 阈值） |
| 章节数 | 8 个核心模块（导论、讲义 1~5、附录两篇） | 8 个核心模块 | 100% 对齐 |
| 参考文献条目数 | 225 篇 | 225 篇 | 100% 对齐 |

差异说明：中文信息密度高于英文单词串，排版更为紧凑，总页数略少 4 页属正常范围。

## 2. 校验 ① parity.py（结构一致性）

对全书 8 个模块运行结构一致性检查，结果全部通过（退出码均为 0）：

```
=== _Intro.tex ===
结构一致性: PASS（环境计数、label/cite/ref 集合、图件列表全部一致）
  环境数: 
  \label=0 \cite=1 \ref=0 \includegraphics=0

=== _Lecture_1.tex ===
结构一致性: PASS（环境计数、label/cite/ref 集合、图件列表全部一致）
  环境数: equation=42, pmatrix=3, vmatrix=1
  \label=13 \cite=21 \ref=0 \includegraphics=0

=== _Lecture_2.tex ===
结构一致性: PASS（环境计数、label/cite/ref 集合、图件列表全部一致）
  环境数: algorithm=2, align=3, cases=1, equation=29, figure=1, pmatrix=2, split=3
  \label=17 \cite=30 \ref=3 \includegraphics=0

=== _Lecture_3.tex ===
结构一致性: PASS（环境计数、label/cite/ref 集合、图件列表全部一致）
  环境数: equation=33, figure=1, pmatrix=8
  \label=14 \cite=18 \ref=1 \includegraphics=0

=== _Lecture_4.tex ===
结构一致性: PASS（环境计数、label/cite/ref 集合、图件列表全部一致）
  环境数: equation=35, pmatrix=2, split=1
  \label=18 \cite=36 \ref=4 \includegraphics=0

=== _Lecture_5.tex ===
结构一致性: PASS（环境计数、label/cite/ref 集合、图件列表全部一致）
  环境数: align=2, equation=36, gathered=1, pmatrix=1, split=1, table=1, tabular=1
  \label=28 \cite=62 \ref=3 \includegraphics=0

=== _App_Cohomology.tex ===
结构一致性: PASS（环境计数、label/cite/ref 集合、图件列表全部一致）
  环境数: align=1, array=2, equation=9, pmatrix=2, split=1
  \label=4 \cite=1 \ref=4 \includegraphics=0

=== _App_Cat.tex ===
结构一致性: PASS（环境计数、label/cite/ref 集合、图件列表全部一致）
  环境数: enumerate=2, equation=3
  \label=1 \cite=7 \ref=0 \includegraphics=0
```

## 3. 校验 ② check_untranslated.py（漏译检查）

对全书 8 个模块逐一执行漏译检查：

```
_Intro.tex: PASS（未发现无汉字的英文散文行）
_Lecture_1.tex: PASS（未发现无汉字的英文散文行）
_Lecture_2.tex: PASS（未发现无汉字的英文散文行）
_Lecture_3.tex: PASS（未发现无汉字的英文散文行）
_Lecture_4.tex: PASS（未发现无汉字的英文散文行）
_Lecture_5.tex: PASS（未发现无汉字的英文散文行）
_App_Cohomology.tex: PASS（未发现无汉字的英文散文行）
_App_Cat.tex: PASS（未发现无汉字的英文散文行）
```

主入口 `main.tex` 中仅作者单位和期刊页眉为英文（按规范属于免译白名单）。

## 4. 校验 ③ 编译健康度

```bash
$ grep -cE 'Reference .* undefined|Citation .* undefined|Missing character|Undefined control sequence' main.log
0
$ grep -c '^!' main.log
0
```

编译日志中未定义引用、缺失字符警告（无豆腐块）、致命错误计数全部为 **0**。

## 5. 校验 ④ 视觉校对

- `zh-front-1.png`（第 1 页）：文章主标题双语、摘要中文、目录全中文渲染排版规整，段落首行缩进自然。
- `zh-front-2.png`、`zh-front-3.png`（第 2~3 页）：目录续页及引言正文排版规整。
- `zh-l5-1.png`（第 50 页）：交换图表、对偶 MPO 的 TikZ 矢量图与对应中文论述渲染完美，无文字重叠。
- 参考文献区（第 65~77 页）：225 条引文排版正常，标题中文化为「参考文献」。

## 6. 保留未译清单（按规范要求）

1. **作者与单位信息**：作者姓名、单位地址及邮箱原样保留。
2. **参考文献条目**：225 篇文献全部保持英文原样，区域标题译为「参考文献」。
3. **英文概念保留**：`gauge` / `gauging`、`ansatz`（含 Bethe ansatz）、`pivot`、`parent Hamiltonian`、`normal form`、`adaptation`、`perplexity`、`string-net`。
4. **英文简称保留**：`MPS`、`MPO`、`PEPS`、`SPT`、`VUMPS`、`DMRG`、`SVD`、`TCI`、`QTT`。
5. **人名命名**：Anderson、Hubbard、Fourier、Bessel、Navier-Stokes、Yang-Baxter 等保留英文。
6. **正则与规范处理**：除系统系综领域的「正则系综/巨正则系综」使用中文外，机器学习与算法领域的 regularization、normalization、gauge、normal form 等均保留英文。

## 7. 术语与全局规则遵守

- `bond dimension` $\to$ 「键维」
- `interpolative construction` $\to$ 「插值构造」
- `exact diagonalization` $\to$ 「精确对角化」
- `Monte Carlo` $\to$ 「蒙卡」
- `Wick's theorem` $\to$ 「Wick 定理」
- 专业术语在各章节首次出现时均已按「中文译名（English）」格式注明英文原词。
- 公式与表格内严禁裸写原生 ASCII `|`，已统一转换为 `\mid`、`\vert`、`\Vert`。
