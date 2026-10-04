# VERIFY — 2501.15674v2《TensorLLM: Tensorising Multi-Head Attention for Enhanced Reasoning and Compression in LLMs》中文译本

- 英文源：`/Users/bjergsen/mnt/u26/research/tn/2501.15674v2/conference_101719.tex`（378 行，IEEEtran conference）
- 中文源：`/Users/bjergsen/mnt/u26/research/tn/zh/2501.15674v2/conference_101719.tex`（由 `parts/*.tex` 拼接）
- 编译：`xelatex -interaction=nonstopmode -file-line-error conference_101719.tex` ×2（.bbl 已存在，直接复用，未重跑 bibtex）
- 中文方案：`\usepackage[fontset=macnew]{ctex}`，置于 `hyperref` 之前；`\figurename`→图、`\tablename`→表、`\abstractname`→摘要、`\IEEEkeywordsname`→索引词、`\refname`→参考文献；`\newtheorem{thm}{定理}`、`\newtheorem{rem}{\bf{注记}}`

## 页数对比

| | 页数 | 提取文字长度 |
|---|---|---|
| EN `2501.15674v2.pdf` | 8 | 43023 |
| ZH `zh/2501.15674v2.pdf` | 9 | 23857 |

差异 +1 页（+12.5%，<25% 阈值）。原因：中文双栏 IEEEtran 下公式与浮动体（2 个 figure*、4 个 table）占位与英文不同，图 1/图 2 各占整页宽浮动页；中文文字长度短属正常（汉字信息密度高于英文单词串）。

图表标题次数（pypdf 正则）：EN `Fig. N.`=3、`TABLE N`=4；ZH `图 N`=6、`表 N`=9（含正文交叉引用「图 1/图 2」「表 I–IV」；图注 2 条、表注 4 条与英文一一对应，已在渲染页目视确认前缀为「图 1.」「表 II」等）。`\includegraphics` 计数：EN=2，ZH=2（methodology.pdf、tensor_network.pdf）。

## 校验 ① parity.py

```
结构一致性: PASS（环境计数、label/cite/ref 集合、图件列表全部一致）
  环境数: IEEEkeywords=1, abstract=1, cases=1, document=1, enumerate=1, equation=13, figure*=2, itemize=4, multline=1, rem=3, split=4, table=3, table*=1, tabular=4
  \label=24 \cite=47 \ref=19 \includegraphics=0
PARITY_EXIT=0
```

## 校验 ② check_untranslated.py

```
漏译检查: FAIL — 发现 1 处疑似未翻译的英文段落：
  .../zh/2501.15674v2/conference_101719.tex:41  \textit{Department of Electrical and Electronic Engineering}\\
EXIT=1
```
该条为作者单位行，属任务书明示可忽略的误报（作者姓名/单位/邮箱按铁律保留英文）。除该行外无漏译。

## 校验 ③ 编译健康度

```
grep -cE 'Reference .* undefined|Citation .* undefined|Missing character|Undefined control sequence' conference_101719.log
0
```
`grep -c '^!' conference_101719.log` = 0；Overfull 仅 1 处（1.09856pt，表 II 段落，无内容溢出页外）。

## 校验 ④ 视觉校对（render_pages.sh + ReadMediaFile）

- 第 1 页（zhA-1）：中文标题/摘要/索引词，作者与单位英文保留，脚注中文，无豆腐块。
- 第 2 页（zhA-2）：正文中文，「表 I 数学符号」表注前缀正确，表内文字单元格已译，式 (1) 完整。
- 第 3 页（zhA-3）：图 1（methodology.pdf）整幅清晰，图注中文且前缀「图 1」；式 (3) 中 `U Σ V^T` 的 Σ 正常渲染。
- 第 4 页（zhA-4）：图 2（tensor_network.pdf）图注中文前缀「图 2」，行内公式 Σ 正常。
- 第 5 页（zhB-1）：式 (7)–(14) 完整，「注记 1」定理名中文，无豆腐块。
- 第 6 页（zhD-1）：表 II 表注前缀「表 II」，表头「数据集/模型名称/原始/本文」已译；「注记 2」中文。
- 第 8 页（zhE-1）：「参考文献」标题中文，条目英文原样；表 IV 表注前缀「表 IV」。
- 第 9 页（zhC-1）：参考文献续页，英文条目完整。

## 校验 ⑤ PDF 级对比（pypdf）

见上「页数对比」表；`\includegraphics` EN=2 / ZH=2；参考文献标题 ZH 含「参考文献」、不含「References」。

## 保留未译清单（按任务书要求保留英文）

1. 作者姓名、单位、邮箱（第 41–43 行）。
2. 参考文献区全部条目（.bbl 原样复用）。
3. 表内行标签 `Acc`/`Loss`/`CR` 缩写保留（表注中已用中文定义：准确率/损失/压缩率）；数据集名 HotPotQA、FEVER、Bios Profession、BigBench-WikidataQA 与模型名 RoBERTa、GPT-J、LLaMA2 为专名。
4. 数据集小节中的提示词字面串（如 ``$<$\texttt{question}$>$ The answer is"）为送入模型的英文 prompt 原文，保留英文。
5. 公式环境内部的英文词（`\text{where}`、`\text{if}`、`\text{for}`、`\text{Attention}`、`\text{MultiHead}` 等）按「数学内容逐字保留」铁律不动。
6. 代码标识符 `\texttt{mask}`、`\texttt{max\_len}`、URL（GitHub 链接）。

## 已知问题与残留风险

1. **公式健壮性修改（唯一偏离逐字保留处）**：英文源中 3 处 `\mathbf{\Sigma}`（式 (3)、SVD 段行内式、图 2 图注）在 XeLaTeX+ctex 下触发 `Missing character: U+0006`（OT1 字符槽 6 在 TU 粗体字中不存在），且 Σ 在 PDF 中**不渲染**（显示为缺字）。已改为 `\boldsymbol{\Sigma}`（parts/10_introduction.tex 1 处、parts/20_background.tex 2 处），渲染结果与英文 PDF 的粗体 Σ 一致，语义不变。修改后 Missing character 计数为 0。
2. 字体替换警告：`TU/ptm` 系列 undefined（IEEEtran 请求 Times，XeLaTeX 下回退默认拉丁字体），仅警告，不影响输出；另有 `STFangsong` 无 CJK script 的 fontspec Info，可忽略。
3. Overfull \hbox 1.09856pt 一处（表 II 所在段落），无可见溢出。
4. 式 (6) 中 `\text{where}` 保持英文（数学环境逐字保留），与英文 PDF 一致。
