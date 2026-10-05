# VERIFY.md — 1008.3477v2《矩阵乘积态时代的密度矩阵重正化群》中译校对记录

日期：2026-10-05。
英文源（只读）：`lit/arxiv_papers/1008.3477v2/`（`annals.tex` 3692 行，elsarticle 单栏；65 处 `\includegraphics` 引用 71 个 EPS 图；文末手写 `thebibliography`，约 150 条）。英文参考 PDF：`lit/dmrg_classics/2011_1008.3477.pdf`（122 页，arXiv v2，2011-01-03 提交，已经 arXiv 摘要页核实为最新版）。
工作目录：`lit/arxiv_papers/1008.3477v2_zh/`。
交付：`lit/arxiv_papers/1008.3477v2_zh.pdf`（110 页）。

## 流水线（与前几篇一致：切分 → 并行译者（每批 3 个）→ check_chunk → 拼回 → xelatex）

1. 英文基线编译：本机 TeX Live 缺 `elsarticle.cls`，从 CTAN zip 解包 `latex elsarticle.ins` 生成后放入源目录；pdflatex 两遍通过（76 页，0 未解析引用）。英文基线 exit 码非 0 但日志尾部正常收尾、PDF 完整，属上游遗留，原样保留。
2. `tools_x/split_chunks.py` 按安全边界切 31 片段（副本中把 `document` 从硬保护名单移除——它包住全文会导致无处可切；其余规则不变），拼回字节级复原已断言。`en_parts/` 原件、`parts/` 译副本。
3. 片段 000–027 派并行译者（每批 3 个，遵守 `tools_x/TRANS_RULES.md` 术语表：块/超块/格点/键维数/规范形式/状态抽取/转移算符等），全部 STRUCT OK；028–030 为纯 `\bibitem` 文献表，按惯例保留英文。
4. 拼回后全局清扫译稿残留的英文引导词：`Fig.~\ref`→`图~\ref`（15 处）、`Eq.~(`/`Eqs.~(`→`式~(`、`Ref.~\cite`→`文献~\cite`、`Sec.~\ref`→`第~\ref…~节`、`cf.\ …`→`参见…/见图…`，及一处「如图 图~\ref」叠词。宏 `\Eq` 显示词改「式~(\ref{#1})」。

## 导言区改动

| 位置 | 改动 |
|---|---|
| `\documentclass` 后 | xeCJK；字体用 `\IfFontExistsTF{SimSun}` 分支——有 SimSun 的机器沿用 SimSun/SimHei/KaiTi/FangSong（与前几篇一致），本机 fallback 到 Noto Serif/Sans CJK SC（按文件路径加载，见下）；`\figurename{图}`、`\tablename{表}`、`\refname{参考文献}`、`\contentsname{目 录}`（均用 `\renewcommand`） |
| `\abstracttitle` | elsarticle 类命令，置「摘要」 |
| `\title` | 中文主标题 + `\\` + 英文原题副行 |

## 本机编译环境修复（2026-10-05，Debian，此前 xelatex 工作流在另一台机器上）

- `xelatex` 二进制（`/usr/bin/xetex`）在但缺软链与格式：`~/.local/bin/xelatex → xetex`；`~/texmf/web2c/fmtutil.cnf` 补 `xelatex xetex language.dat -etex xelatex.ini` 条目（`xelatex.ini` 系统自带于 tex-ini-files），`fmtutil-user --byfmt xelatex` 生成格式。
- 缺 fontspec/xeCJK/ctexhook/ctexpatch：前两者由 CTAN tds/zip 源 `tex fontspec.ins`、自写 `xeCJK.ins` 生成装入 `~/texmf`；后两者从 `ctex-auxpkg.dtx` 按模块 `%<ctexhook>`、`%<ctexpatch>` 单独 docstrip 生成。注意 GitHub main 分支的 fontspec.dtx 只是元数据壳，生成物与 l3kernel 不匹配，必须用 CTAN 完整源。
- Noto CJK 为 TTC 多面共享 CFF：XeTeX 按家族名取面 0（jp）。用 fontTools 把 TTC index 2（SC 面）抽成独立 OTF 装入 `~/.fonts` 并 `fc-cache`；导言区 Noto 分支按文件路径加载。`pdffonts` 显示的 PS 名 `NotoSerifCJKjp-*` 是共享 CFF fontName 的残留，实际 cmap/GSUB 为 SC 面，字形正确。

## 编译与校验

- `xelatex` 三遍：110 页（英文基线 76 页；中文更宽 + 目录），rc=0，0 `!` 错误、0 undefined citation、0 `??`。
- 漏译扫描（正文剔除参考文献后找 ≥6 个英文词的纯英文行）：仅剩 5 处预期保留项——英文原题副行、两行作者单位、Email 行。
- 逐页 PNG（`render/p-001..110.png`）。目检页：p-001（中文主标题+英文副行、摘要、目录起始）、p-002（目录全）、p-005/p-020（正文+行内数学）、p-010/p-028/p-045/p-060/p-095（EPS 插图、图注中文、网络图清晰无变形）、p-085、p-098、p-100（后期正文/公式/列表）、p-100 修复后复查（「图 62」）、p-103 起参考文献为英文（预期）。中文渲染正常无缺字，公式完好，无重叠溢出。
