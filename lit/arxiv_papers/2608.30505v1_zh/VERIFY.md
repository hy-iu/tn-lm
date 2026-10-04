# VERIFY.md — 2608.30505v1《Tensor Methods for Language Models》中译校对记录

日期：2026-09-25。工作目录：`/Users/bjergsen/mnt/u26/research/tn/zh/2608.30505v1/`。
英文源（只读）：`/Users/bjergsen/mnt/u26/research/tn/2608.30505v1/survey_arxiv_version.tex`（2605 行）；英文 PDF：`/Users/bjergsen/mnt/u26/research/tn/2608.30505v1.pdf`（58 页）。
拼装：`cat parts/*.tex > survey_arxiv_version.tex`（15 个片段，2588 行）；编译：`latexmk -xelatex -interaction=nonstopmode -file-line-error survey_arxiv_version.tex`（共 5 轮迭代，最终 exit 0）。
最终交付：`/Users/bjergsen/mnt/u26/research/tn/zh/2608.30505v1.pdf`（60 页）。

## 0. 页数对比

| 项 | 英文 PDF | 中文 PDF | 差异 |
|---|---|---|---|
| 页数 | 58 | 60 | +3.4%（<25%，无需额外解释；中文正文更紧凑但 tblr 长表与 tikz 图占版略增） |
| 提取文字长度 | 189240 | 107071 | 中文更紧凑（汉字信息密度高），属正常 |
| Figure/图 标题数 | 5 | 5 | 一致 |
| Figure/图 正文引用次数 | 16 | 16 | 一致 |
| Table/表 标题数 | 12 | 12 | 一致 |
| `\includegraphics` 计数 | 0 | 0 | 一致（全部图件为 tikz，`tikzpicture` 环境 5=5） |

## 1. 校验① parity.py（原始输出 + 复核）

工具原始输出（`python3 tools/parity.py 英文源 中文拼好文件`）：

```
\cite 不一致（en=395, zh=395）
    仅英文源有: frantar2023gptq,
dettmers2022llmint8, liu2023llmqat, frantar2023gptq, dettmers2022llmint8, liu2023llmqat, frantar2023sparsegpt,
ashkboos2024slicegpt, frantar2023sparsegpt, ashkboos2024slicegpt
    仅中文译有: frantar2023gptq, dettmers2022llmint8, liu2023llmqat x2, frantar2023sparsegpt, ashkboos2024slicegpt x2

结构一致性: FAIL
```

**结论：FAIL 为工具假象，非内容缺失。** parity.py 按行匹配 `\cite{...}`，而英文源第 2374–2375 行把同一多键 cite 折行书写（`\cite{frantar2023gptq,\n dettmers2022llmint8, liu2023llmqat}`），被切成两个"键串"；中文译文写在同一行。用跨行正则对两侧做规范化复核（注释行剔除后）：

```
cite 键多重集: en=457, zh=457, 仅 en={}, 仅 zh={}
label: en=72, zh=72, 无差异
ref/cref/Cref/eqref: en=114, zh=114, 无差异
equation/align/gather 环境: en=60, zh=60
figure 环境: en=5, zh=5
tblr/longtblr/tabular 环境: en=13, zh=13
```

结构一致性实质 **PASS**（环境/label/cite/ref/图/表/公式计数全部相等）。

## 2. 校验② check_untranslated.py（原始输出 + 逐条说明）

```
漏译检查: FAIL — 发现 6 处疑似未翻译的英文段落：
  .../survey_arxiv_version.tex:145  \affil[3]{Systems Research Institute of Polish Academy of Science and Warsaw University of Technology, Poland\\ \email{cichockiand@gmail.com}}
  .../survey_arxiv_version.tex:1033  TT-embeddings \cite{hrinchuk2020tensorized}, TensorGPT \cite{xu2023tensorgpt}, TN-gram \cite{zhou2026tensorizingengram},
  .../survey_arxiv_version.tex:1041  Hypoformer \cite{li2022hypoformer}, Shapeshifter \cite{pahani2021shapeshifter},  CoMERA \cite{yang2024comera}
  .../survey_arxiv_version.tex:1048  LoRTA \cite{hounie2024lorta}, LoTR \cite{bershatsky2024lotr}, TT-LoRA \cite{anjum2024ttlora}, MetaTT \cite{lopezpiqueres2025metatt}, QuanTA \cite{chen2024quanta
  .../survey_arxiv_version.tex:1063  TPA \cite{zhang2026tpa}, Tucker Attention \cite{klein2026tuckerattention}, DecoQuant \cite{liu2024decoquant}, EinSort \cite{koikeakino2026einsort}
  .../survey_arxiv_version.tex:1069  Bilinear MLPs \cite{pearce2025bilinearmlp}, PolySAE \cite{koromilas2026polysae}, TensorLens \cite{atad2026tensorlens}
```

逐条说明（均为误报，属 BRIEF 规定保留英文项）：
1. L145：作者单位/邮箱（authblk），规则要求保留英文原样。
2. L1033/1041/1048/1063/1069：生命周期总览 tikz 图（图 2）各阶段方框内的**方法专名列表**（TT-embeddings、TensorGPT、LoRTA、TPA、Bilinear MLPs 等），为模型/论文专名，按术语表与 BRIEF 保留英文；方框外的说明文字（§5.x、"暂无已发表工作"）已译中文，见渲染目检第 14 页。

## 3. 校验③ 编译健康度（最终 run 的 survey_arxiv_version.log）

```
grep -c '^! '                                        → 0
grep -c 'Undefined control sequence'                 → 0
grep -cE 'Reference .* undefined|Citation .* undefined' → 0
grep -c 'Missing character'                          → 0
```

overfull 共 16 处：10 处在参考文献条目（行 2586，英文条目逐字保留、含长 URL/作者串，最宽 61pt < 72pt 页边距，未出页）；6 处在记号表 tblr 公式单元格内（3.0pt，约 1mm，可忽略）。正文 overfull 已清零（见修复清单 40 片段）。underfull 0。

已知无害告警（notes_preamble.md 已预告，未改配置）：
- `LaTeX Warning: There were undefined references.` + `Package biblatex Warning: Please (re)run BibTeX`：biblatex backend=bibtex + sorting=none 的固有 rerun 循环（BRIEF ③ 的 grep 模式不匹配，计数 0）。
- `xdvipdfmx:warning: Object @figure.N/@table.N already defined`：hyperref 锚点名冲突，无害。
- fontspec Info：STFangsong 无粗斜体，正常提示。

## 4. 校验④ 渲染目检（render/ 下 PNG，gs 110dpi）

目检页：第 1 页（zhA-1）、第 13–17 页（zhB-1..5）、第 20 页（zhE-1）、第 30 页（zhC-1）、第 41 页（zhD-1）。结论：
- 中文标题/摘要/正文/节标题全部正常，无豆腐块、无乱码；公式完整（含 ΔW、Λ 等修复后的粗体希腊字母）。
- 第 14 页生命周期 tikz 大图：7 个阶段节点（词元化/嵌入/预训练/适配/压缩/推理/可解释性）中文标签**均未溢出** minimum width=3.0cm 节点框；方框内方法专名英文、§5.x 与"暂无已发表工作"为中文。
- 第 15、16、20 页 tikz 图（图 3、图 4 及式 (32)–(35) 段落）：节点标签、数学记号正常，无溢出。
- 第 15、30 页 tblr 长表（表 4、表 9）：中文表头/表注正常，版式完整未出页。
- 图/表前缀为「图」「表」（图 2:/图 3:/图 4:/表 4:/表 9:）；`\cref` 显示「图 3」「式 (55)」「表 4」「节 9.2」等中文形式。
- 第 41 页参考文献标题为「参考文献」，条目英文原样、编号 [1]… 正常。

## 5. 校验⑤ pypdf 中英 PDF 对比（原始输出）

```
pages EN 58 ZH 60 diff% 3.4
text len EN 189240 ZH 107071
EN Figure captions: 5 | EN Fig mentions: 16
ZH 图 captions: 5 | ZH 图 mentions: 16
EN Table captions: 12 | ZH 表 captions: 12
includegraphics EN 0 ZH 0
tikzpicture EN 5 ZH 5
```

页数差异 +3.4% < 25%，通过。

## 6. 修复清单（按 parts 片段）

| 片段 | 修复 | 原因 |
|---|---|---|
| parts/01_frontmatter.tex | 「压缩实现落差」→「压缩-实现鸿沟」（摘要内） | 术语统一（见 §7） |
| parts/10_introduction.tex | 「压缩-兑现差距」→「压缩-实现鸿沟」×2（贡献列表、组织结构段） | 同上 |
| parts/30_lifecycle_a.tex | 「理论压缩与实际收益之间的差距」→「压缩-实现鸿沟（理论压缩与实际收益之间的差距）」 | 同上，保留释义括号 |
| parts/32_lifecycle_c.tex | tikz 节点 `$\mat{\Delta W}$` → `$\bm{\Delta W}$` | `\mathbf` 包希腊字母 Δ 在 XeLaTeX 下映射为 U+0001 缺字（Missing character，节点内 Δ 不显示）；bm 已加载，渲染为粗体 Δ，与英文 PDF 观感一致 |
| parts/51_across_b.tex | `$\mat{\Lambda}$` ×2 → `$\bm{\Lambda}$` | 同上，Λ=U+0003 缺字；英文 PDF 该处 Λ 可见，修复后一致 |
| parts/40_tensorizing.tex | 长句语序微调：「投影 W∈R^{I×J} 被重排为 …，输入 x∈R^I 被重排为 …」→「投影 W∈R^{I×J} 与输入 x∈R^I 分别被重排为 … 与 …」 | 消除 25.4pt overfull（长不可断公式串）；语义与英文源逐句对应，数学内容未改 |

编译迭代：run1 发现 3 处 Missing character（Δ/Λ）→ 修复后 run2 清零；run3/4 处理 overfull（`\allowbreak` 置于上下标内无效，run5 改用语序调整）→ 正文 overfull 清零。

## 7. 术语统一决定

- **compression-realization gap**：以 70 片段（定义处 `\rho_{\rm gap}`、\subsection 标题）的「压缩-实现鸿沟」为全文统一译法；01/10/30 片段的三种旧译（压缩实现落差、压缩-兑现差距、理论压缩与实际收益之间的差距）已统一，30 片段保留释义性括注。
- **healing**：全文统一「修复」（51 片段首次出现注英文「修复（healing）」；51/60 片段其余出现及表 9 表头均为「修复」），无「治愈/疗愈」等变体。
- **张量列（TT）**：21 片段定义「张量列（tensor train, TT）」，其后「TT 分解」「张量列分解」混用与英文源 TT decomposition / tensor train decomposition 的混用对应；无「张量训练」误译（0 处）。
- **缩并**（48 处，无「收缩」变体）、**模**（模-n 积、第 n 模切片、沿模对）、**词元**（64 处，无「令牌」变体）、**困惑度**（7 处，无「困惑」裸用）均与 GLOSSARY 一致。
- **块项分解（BT/BTD）**：按指示保留源文件写法，未强改。

## 8. 保留未译清单（有意保留）

- 作者姓名、单位、邮箱（authblk 全保留英文）。
- 参考文献全部条目英文原样；参考文献区标题译「参考文献」。
- 模型/方法/软件专名：LLaMA、GPT-2、TT-embeddings、TensorGPT、LoRTA、TPA、Bilinear MLPs、PolySAE、TensorLens、Triton/CUDA、NumPy/PyTorch/JAX 等。
- 生命周期总览图（图 2）节点内方法专名列表（英文），节点外说明文字已译。
- URL、DOI、`\texttt{}` 代码标识符、数学内容全部原样。

## 9. 已知问题与残留风险

1. 参考文献条目 10 处 overfull（最宽 61pt）：英文条目逐字保留所致，未出页边（页边距 72pt）；不改 .bbl/条目内容。
2. 记号表（20 片段 tblr）公式单元格 6 处 ~3pt overfull，视觉不可察。
3. biblatex bibtex-backend rerun 循环告警、xdvipdfmx 锚点告警、fontspec 仿宋 Info：notes_preamble.md 已记录的固有告警，未改 backend/sorting。
4. parity.py 对折行 `\cite` 的按行切分导致其报 FAIL；规范化复核证明 cite 键多重集 457=457 完全一致（见 §1）。
5. 中文 PDF 提取文字长度（107k）低于英文（189k）为汉字编码/提取特性，非内容缺失；图/表/公式/引用计数均对齐。

## 10. 二次修订（2026-09-25，为小册子拼版修复参考文献 overfull）

小册子拼版时发现全稿墨迹并集右界 586pt（正常版心 524pt），源自参考文献区 10 处 overfull 的 URL/DOI 长串；左右半幅列宽不一。经最小复现定位：`ctex`（先于 hyperref 加载）+ `biblatex` 组合下 `\url` 断行机制失效（实验：xeCJK 单独加载断行正常，ctex+hyperref 正文 `\url` 不断行，与加载顺序/后端无关；`xurl` 无效果已移除）。修复（均为排版级，不改条目文字）：
- `parts/00_preamble.tex`：biblatex 加载后加 `\DeclareFieldFormat{url}{{\small\url{#1}}}`（URL 以 \small 字号排版）；
- `parts/70_discussion_end.tex`：`\printbibliography` 包 `{\sloppy ...}`。
修复后重新拼装编译：致命/undefined/Missing character 仍为 0；overfull 由 16 降为 6（仅剩记号表 tblr 单元格 3–8pt）；页数不变 60；全稿墨迹并集变为 (71,41,526,770)。交付 PDF `tn/zh/2608.30505v1.pdf` 已更新为重编版本。
