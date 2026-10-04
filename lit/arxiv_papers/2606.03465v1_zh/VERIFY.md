# 2606.03465v1 中译校验记录（VERIFY）

- 英文源：`tn/2606.03465v1/brain_one_column.tex`（1740 行，只读）；英文 PDF：`tn/2606.03465v1.pdf`（23 页）
- 中文拼装：`cat parts/*.tex > brain_one_column.tex`（1730 行；parts/ 10 个片段）
- 编译：`latexmk -xelatex -interaction=nonstopmode -file-line-error brain_one_column.tex`，exit=0，bibtex 由 latexmk 自动运行
- 交付：`tn/zh/2606.03465v1.pdf`（27 页）

## 0. 页数对比

| | 页数 |
|---|---|
| 英文 PDF | 23 |
| 中文 PDF | 27 |
| 差异 | +4 页（+17.4%，< 25% 阈值） |

差异原因：CJK 字体行距高于英文正文、figure*/wrapfigure 浮动体在中文断行下的落页位置不同（如正文图 5/图 6 同页、附录图另起页），以及 longtable（表 4）在中文下仍跨 2 页但前后浮动体排布不同。中英均有附录目录页（EN "Contents" / ZH「目录」）与 longtable 跨页续表，结构对等。

## 1. 校验① parity.py（结构一致性）—— PASS

```
$ python3 tools/parity.py ../2606.03465v1/brain_one_column.tex 2606.03465v1/brain_one_column.tex
结构一致性: PASS（环境计数、label/cite/ref 集合、图件列表全部一致）
  环境数: appendixpart=1, cases=1, corollary=1, document=1, equation=8, figure=4, figure*=12, longtable=1, mainpart=1, minipage=4, proposition=1, subfigure=2, table=3, tabular=3, tcolorbox=2, wrapfigure=2
  \label=53 \cite=1 \ref=77 \includegraphics=0
```

（parity 的 includegraphics 计数对两边同为 0，属该脚本正则口径；实际非注释 `\includegraphics` 中英各 20 处、注释中各 2 处，见校验⑤。）

## 2. 校验② check_untranslated.py —— 6 处全部为误报

```
漏译检查: FAIL — 发现 6 处疑似未翻译的英文段落：
  brain_one_column.tex:48   authors={Artur Zagitov\equalcontrib, ...}      ← 作者名单，按 BRIEF 保留英文
  brain_one_column.tex:321  \includegraphics[...]{emnlp/figs/pareto_no_rtn_c4_...pdf}   ← 图件文件名（命令参数）
  brain_one_column.tex:560  \includegraphics[...]{emnlp/figs/llama2_layer01_...pdf}     ← 同上
  brain_one_column.tex:1100 \includegraphics[...]{emnlp/figs/llama2_layer17_...pdf}     ← 同上
  brain_one_column.tex:1127 \includegraphics[...]{emnlp/figs/pareto_no_rtn_wt2_...pdf}  ← 同上
  brain_one_column.tex:1134 \vspace{-4mm}\includegraphics[...]{emnlp/figs/pareto_no_rtn_lmeval_...pdf} ← 同上
```

逐条结论：1 处为作者/单位行（铁律保留英文），5 处为 `\includegraphics` 文件路径（非散文）。无真实漏译。

## 3. 校验③ 编译健康度 —— 四类计数全 0

```
$ for pat in 'Undefined control sequence' 'Reference .* undefined' 'Citation .* undefined' 'Missing character'; do grep -cE "$pat" brain_one_column.log; done
0
0
0
0
```

`! ` 致命错误 0；Overfull 0；仅 3 条 Underfull \hbox（lines 958–959，段落断行，无害）。
残留已知无害警告（与骨架阶段一致）：`TU/zi4/m/n undefined`（inconsolata 回退 Latin Modern tt）、`xeCJK Redefining CJKfamily \CJKttdefault`。

## 4. 校验④ 目检 —— PASS

渲染页（render/v-*.png，110 dpi）：p1、p3、p6、p8、p11、p15、p22、p23。

- p1：标题框内中文标题两行、BRAIn logo、英文作者行、`* 同等贡献`、中文摘要，无豆腐块。
- p8：定理族框「命题 1 (12)」「推论 1（谱范数与 Frobenius 范数的差距）」前缀正确，公式完整。
- p6：figure* 页，「图 5:」「图 6:」前缀正确；图 6 注含「内点（inlier）」。
- p3：正文页含「图 1:」中文图注与 Q1 灰框。
- p22/p23：longtable（表 4）跨页，首页注「表 4: …」+ 右下「续下页」，续页重复中文表头「表 4: …（续）。/ 压缩↑ 困惑度↓ LM-Eval 准确率(%)↑ 激活几何」，表格未溢出页宽。
- p15：附录横幅「附录」+ 中文论文标题 + 中文目录。
- p11：参考文献页（条目英文原样，符合学术惯例；区标题为「参考文献」，见 p10 末）。
- 全页无豆腐块、无乱码；方法名 Tucker MHA / TT FFN / Tucker+TT / TT all、\textsc 名保留英文。

## 5. 校验⑤ PDF 级对比 —— PASS

```
pages EN/ZH: 23 27  diff%: 17.4
text len EN/ZH: 76902 47469          ← 中文按字符计更紧凑，属正常
EN Figure N:  [1..19]（提取时 Figure 4 粘连为 "Figure4:"，实际存在）
ZH 图 N:      [1..19]
EN Table N:   [1,2,3,4]
ZH 表 N:      [1,2,3,4]
EN includegraphics active/commented: 20 2
ZH includegraphics active/commented: 20 2   ← 源中被注释的 2 张图两边一致未启用
```

## 6. 术语统一决定

- **inlier**：统一为「内点」，首次出现带英文「内点（inlier）」。改动：parts/30 图 6 注「非离群元素（inlier）」→「内点（inlier）」；parts/60「随机内点值」→「随机内点」（正文与图注各 1 处）；parts/70「内点矩阵」原已一致，未动。
- **Pareto frontier / compression-quality frontier**：英文本就是两个不同词，译为「Pareto 前沿」（parts/20、70 图注，GLOSSARY 一致）与「压缩-质量前沿」（parts/50 正文），保持区分，不改。
- 方法名 Tucker MHA / TT FFN / Tucker+TT / TT all、\textsc{preserve}/\textsc{compress}、HASSLE-free、LASER、SoLA、Dobi-SVD、RTN 等保留英文。

## 7. 翻译 agent 疑点核对结论

- **源 859 行孤立右括号**：英文 PDF 同样显示 "…tensorization in Fig. 2), residual-stream…"（孤立 `)` 为原文瑕疵）。译文 parts/40 保留「诸如图~\ref{fig:matrix_decomps}）中…」，与英文一致，不算错误。顺带修掉「诸如 图」之间多余空格。
- **tab:app_main_tensor_results_maxL**：该表在英文源 1315–1342 行整块注释，中文 parts/70 同样注释；全文（中英）均无 `\ref{tab:app_main_tensor_results_maxL}`——正文引用的是 `\ref{tab:app_main_tensor_results_full}`（longtable 表 4，已定义）。英文 PDF 无 "??"，中文 log Reference undefined = 0。无悬空引用。
- **corollary 可选参数**「[谱范数与 Frobenius 范数的差距]」保留，见 p8。
- **NBSP（U+00A0）**：parts/70 longtable 行首 NBSP 保留未改；xelatex 编译 Missing character = 0，p22/p23 排版正常，无需替换。

## 8. 修复清单（按 parts 片段）

- parts/30_moe_mismatch.tex：图 6 注 inlier 译法统一（非离群元素（inlier）→ 内点（inlier））。
- parts/40_why_fails.tex：删除「诸如 图」间多余空格（孤立「）」按原文保留）。
- parts/60_appx_notation.tex：「随机内点值」→「随机内点」×2。
- 其余片段（00/01/10/20/50/70/80）未改动。

## 9. 保留未译清单

- 作者姓名、单位（BRAIn Lab, Moscow, Russia）、邮箱/基金（本篇无显式基金行）。
- 参考文献全部条目（plainnat 英文原样）；区标题已中文化「参考文献」。
- 方法/模型专名：Tucker MHA、TT FFN、Tucker+TT、TT all、HASSLE-free、LASER、SoLA、Dobi-SVD、RTN、Flat-LLM、GPTQ、TD-MoE、MoBE、LoRA、LM-Eval、WikiText-2、C4、ARC-C、HellaSwag、OpenBookQA、PIQA、WinoGrande 等。
- 图内嵌文字（PDF 图件本身为英文，不重绘）。
- 表内方法名列与数值/单位保留；表头说明性文字已译中文。

## 10. 已知问题与残留风险

- 3 条 Underfull \hbox（958–959 行）：仅断行松散，无视觉缺陷。
- `TU/zi4/m/n` 回退使 `\texttt`/URL 用 Latin Modern tt 显示，外观与英文 PDF 的 inconsolata 略有差异，非错误。
- 中文 PDF 27 页 vs 英文 23 页（+17.4%），在 25% 阈值内，原因见第 0 节。
- 无其他未决问题。
