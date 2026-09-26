# 全量 304 行摘要一致性扫描结论

执行方式：`python3 lit/audit/scan_abstracts.py`（用户本机，确定性 HTTP 请求，**零模型额度**，约 2 分钟）。
数据源：arXiv `id_list` 批量（138 个 id / 6 批，全部返回）+ OpenAlex 小写 DOI 批量 `filter`（112 个 DOI / 6 批，命中 91 个）。
逐行结果见 `full304_scan.csv`。

## 分类结果

| verdict | 行数 | 含义 |
|---|---|---|
| consistent | 103 | 存量整体是权威源摘要的子串 |
| truncated_snippet | 15 | 存量含 `…`，且每个片段都能在权威源命中——干净的截短 |
| partial | 8 | 仅部分片段命中 |
| zero_hit | 56 | 有权威源但**零片段命中** —— 内容不对 |
| no_identifier | 121 | 本行提不出 arXiv id 也提不出 DOI，脚本层面判不了 |
| empty | 1 | 存量为空（行 159，即试点里的 P17） |

`zero_hit` 的 56 行里，**48 行含 `…`、8 行不含**。不含 `…` 的这 8 行形状上"正常"（长度合规、无省略号），是最高危的一类，试点中 P06 就属于此类并被证实为串台。

## 关键判定：标识符是对的，错的是 abstract 字段

对 `zero_hit`/`partial` 中能提出 arXiv id 的 39 行，逐条比对权威源标题与存量标题的词重合度：**全部 ≥0.73，其中 36 条为 1.00**。也就是说这些行指向的论文真实存在、id 正确、标题正确。

结合试点对 P06/P07/P09/P10/P11/P12/P15/P16 的逐条取证（片段含 `[10]`、`[17]`、`DMRG9`、`Section 4.3` 等只有正文才有的标记），可以判定 `zero_hit` 的成因不是"论文是假的"，而是：

> 抓取管线把论文正文片段（或多报告合并 PDF 中他人报告的摘要）写进了 `abstract` 列。

因此这 56 行应整体视为**需要替换摘要**，而不是需要删除条目。

## 去重

按"同 arXiv id 多行"和"同 DOI 多行"直接比对：**0 组重复**（见 `duplicate_keys.json`）。

但试点确认了 P01(行 6) ↔ P20(行 10) 是同一篇（Eisert/Cramer/Plenio, area laws）。它逃过本轮简单去重的原因：P01 的 `arxiv_id=0808.3773`、P20 无 id 且 `url` 指向 APS 页面，而连接两者的 DOI `10.1103/RevModPhys.82.277` 藏在 **arXiv 元数据的 `arxiv:doi`/`journal_ref` 字段**里，不在 CSV 任何列中。

另按标题归一化相似度 >0.75 扫出约 20 对候选，其中高度疑似同一工作的有：`29↔55`(0.794)、`78↔189`(0.821)、`151↔215`(0.914)、`191↔224`(0.891)；`56↔144`（TIE vs ETTE）为误报。**要真正定论必须走 arXiv 元数据里的 DOI 字段做二跳去重**，脚本尚未实现这一步。

## 尚未覆盖的部分

`no_identifier` 的 121 行是最大盲区：提不出任何标识符，脚本无从校验。这类行只能靠标题反查（OpenAlex/S2/Crossref 逐条检索），需要判断力（同名不同人、预印本与刊发版标题差异、被截断的标题），是 LLM 取证该花额度的地方。

**建议的下一步预算分配**：186 行需进一步处理（zero_hit 56 + partial 8 + empty 1 + no_identifier 121）。其中 zero_hit 的 56 行成因已由试点确认、且权威源摘要已在 `full304_scan.csv` 里（`authority_tail40` 可作校验锚），**多数可直接机械替换摘要**，不必送云端；真正需要 LLM 的是 121 行 `no_identifier` + 8 行 `partial` 的定性。

## 复跑

```bash
cd tn-lm && python3 lit/audit/scan_abstracts.py
```
产物：`lit/audit/full304_scan.csv`、`lit/audit/duplicate_keys.json`。
脚本内已处理两处实测坑：arXiv 拒绝默认 `urllib` UA（需带 `Mozilla/5.0`）、OpenAlex 的 `filter=doi:` 区分大小写（必须小写）。
