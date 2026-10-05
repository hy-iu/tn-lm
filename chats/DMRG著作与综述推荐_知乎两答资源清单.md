# 知乎「关于DMRG有什么著作和综述推荐？」两答资源清单

> 保存日期：2026-10-04。资源取自以下两篇回答，凡本仓库已收录的条目单独标出，未重复保存。
>
> - 问题：<https://www.zhihu.com/question/426281684>
> - 答一（拉格朗日的忧郁，142 赞）：<https://www.zhihu.com/question/426281684/answer/3423870293>
> - 答二（一只冰牙喵，295 赞）：<https://www.zhihu.com/question/426281684/answer/3426403454>
>
> **转载声明**：本清单为上述两答的条目整理存档，转载自知乎，仅作个人学习与研究之用，无任何商业用途。原文版权归原作者（拉格朗日的忧郁、一只冰牙喵）所有，按知乎默认许可协议（CC BY-NC-SA 4.0）标注；如答主另有版权设置或对本次存档有异议，请联系我删除。

## 一、综述与讲义

| 资源 | 作者 | 出处 | 链接 |
| --- | --- | --- | --- |
| The density-matrix renormalization group in the age of matrix product states（两答共同首推；答二提醒：MPO 写法讲得少、含时演化没讲 TDVP） | U. Schollwöck | Ann. Phys. 326, 96 (2011) | [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0003491610001752) · [arXiv:1008.3477](https://arxiv.org/abs/1008.3477) |
| Time-evolution methods for matrix-product states（答一补充：含时演化讲得最充分） | S. Paeckel, T. Köhler, A. Swoboda, S. R. Manmana, U. Schollwöck, C. Hubig | Ann. Phys. 411, 167998 (2019) | [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0003491619302532) · [arXiv:1901.05824](https://arxiv.org/abs/1901.05824) |
| Matrix product states and projected entangled pair states: Concepts, symmetries, theorems（答一补充：观点更高，TDVP 解释受推崇） | J. I. Cirac, D. Perez-Garcia, N. Schuch, F. Verstraete | Rev. Mod. Phys. 93, 045003 (2021) | **已在论文库**（`lit/bibliography.csv`） |
| Tangent-space methods for uniform matrix product states（答二推荐：VUMPS，替代 iDMRG/iTEBD 求无穷长系统基态） | L. Vanderstraeten, J. Haegeman, F. Verstraete | SciPost Phys. Lect. Notes 7 (2019) | [SciPost](https://scipost.org/SciPostPhysLectNotes.7) · [arXiv:1810.07006](https://arxiv.org/abs/1810.07006) |
| Geometry of Matrix Product States: metric, parallel transport and curvature（两答都提；答二注：很数学，做物理基本不用看） | J. Haegeman, M. Mariën, T. J. Osborne, F. Verstraete | J. Math. Phys. 55, 021902 (2014) | [arXiv:1210.7710](https://arxiv.org/abs/1210.7710) |

## 二、奠基与算法论文

| 资源 | 作者 | 出处 | 链接 |
| --- | --- | --- | --- |
| Density matrix formulation for quantum renormalization groups（DMRG 开山作；答二建议最后再读，现代观点用 vMPS 理解） | S. R. White | PRL 69, 2863 (1992) | [APS](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.69.2863) |
| Efficient classical simulation of slightly entangled quantum computations（答二视作 MPS 的提出） | G. Vidal | PRL 91, 147902 (2003) | [APS](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.91.147902) · [arXiv:quant-ph/0301063](https://arxiv.org/abs/quant-ph/0301063) |
| Infinite size density matrix renormalization group, revisited（iDMRG，即 White 最早的加点式 DMRG） | I. P. McCulloch | arXiv (2008) | [arXiv:0804.2509](https://arxiv.org/abs/0804.2509) |
| Efficient simulation of one-dimensional quantum many-body systems（TEBD 最早论文） | G. Vidal | PRL 93, 040502 (2004) | [APS](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.93.040502) · [arXiv:quant-ph/0310089](https://arxiv.org/abs/quant-ph/0310089) |
| Classical simulation of infinite-size quantum lattice systems in one spatial dimension（iTEBD） | G. Vidal | PRL 98, 070201 (2007) | [APS](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.98.070201) · [arXiv:cond-mat/0605597](https://arxiv.org/abs/cond-mat/0605597) |
| Time-dependent variational principle for quantum lattices（TDVP，可处理长程相互作用） | J. Haegeman, et al. | PRL 107, 070601 (2011) | [APS](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.107.070601) · [arXiv:1103.0936](https://arxiv.org/abs/1103.0936) |
| Unifying time evolution and optimization with matrix product states（TDVP 的单点/两点更新版本） | J. Haegeman, C. Lubich, I. Oseledets, B. Vandereycken, F. Verstraete | PRB 94, 165116 (2016) | [APS](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.94.165116) · [arXiv:1408.5056](https://arxiv.org/abs/1408.5056) |

## 三、MPO 构造与压缩（手搓 DMRG 时的细节）

| 资源 | 作者 | 出处 | 链接 |
| --- | --- | --- | --- |
| Finite automata for caching in matrix product algorithms（有限状态机构造 MPS/MPO） | G. M. Crosswhite, D. Bacon | PRA 78, 012356 (2008) | [APS](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.78.012356) |
| Applying matrix product operators to model systems with long-range interactions（指数衰减势叠加近似 1/r^a 长程势） | G. M. Crosswhite, A. C. Doherty, G. Vidal | PRB 78, 035116 (2008) | [APS](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.78.035116) · [arXiv:0804.2504](https://arxiv.org/abs/0804.2504) |
| Generic construction of efficient matrix product operators（Rescaled SVD / Deparallelisation / Delinearisation，MPO 自动压缩） | C. Hubig, I. P. McCulloch, U. Schollwöck | PRB 95, 035129 (2017) | [APS](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.95.035129) · [arXiv:1611.02498](https://arxiv.org/abs/1611.02498) |

## 四、教程、网站与视频

| 资源 | 说明 | 链接 |
| --- | --- | --- |
| Tensors.net — T Tutorial 1: Tensor Contraction | 张量运算入门，附 MATLAB/Python/Julia 代码 | <https://www.tensors.net/p-tutorial-1> |
| Tensor Network Theory（tensornetwork.org） | tDMRG 各种时间演化方法（local/global Krylov、MPO 等）收集很全 | <https://tensornetwork.org/mps/algorithms/timeevo/> |
| TeNPy 文档 | Python 张量网络/DMRG 包 | <https://tenpy.readthedocs.io/en/latest/> |
| TeNPy lanczos.py toycode | Lanczos 参考实现 | <https://tenpy.readthedocs.io/en/latest/toycode_stubs/lanczos.html> |
| ITensors.jl 文档 | Julia 张量网络包（White 的学生 Matt Fishman 维护） | <https://itensor.github.io/ITensors.jl/dev/> |
| ITensor MPS Time Evolution 教程 | TEBD 图解 | <https://itensor.github.io/ITensors.jl/dev/tutorials/MPSTimeEvolution.html> |
| Wikipedia: Time-evolving block decimation | TEBD 概述 | <https://en.wikipedia.org/wiki/Time-evolving_block_decimation> |
| Wikipedia: Lanczos algorithm | DMRG 每步求基态用 Lanczos 足够 | <https://en.wikipedia.org/wiki/Lanczos_algorithm> |
| B 站 StringCNU（首师大冉老师） | 张量网络教学视频 | <https://space.bilibili.com/401005433/> |

## 五、知乎专栏与回答（中文入门向）

| 资源 | 链接 |
| --- | --- |
| 什么是张量网络（tensor network）？（高赞回答即一篇详细 review） | <https://www.zhihu.com/question/54786880> |
| 对于物理学家来说，一个数值解有多大意义？ | <https://www.zhihu.com/question/30053039/answer/46851931> |
| 为什么 vMPS 等价于 DMRG？ | <https://www.zhihu.com/question/516763300/answer/2352487921> |
| yangjh：物理中的数值方法之——DMRG 方法(1) | <https://zhuanlan.zhihu.com/p/102451474> |
| 零零：密度矩阵重整化群（DMRG）笔记 0.前言 | <https://zhuanlan.zhihu.com/p/110243829> |
| Richard Liu：从矩阵乘积态（MPS）到 DMRG（1） | <https://zhuanlan.zhihu.com/p/508258708> |
| Kyle Zhang：张量网络系列内容介绍：目录 | <https://zhuanlan.zhihu.com/p/411311029> |
| Kyle Zhang：有限状态自动机生成矩阵乘积算符（MPO） | <https://zhuanlan.zhihu.com/p/382361509> |
| Kyle Zhang：Lanczos 算法 & Arnoldi 算法简述 | <https://zhuanlan.zhihu.com/p/393679251> |

## 六、与仓库去重情况

- **已在工具库**（`lit/audit/toolbox_extra.csv`，见 `app/toolboxes.html` 引擎分类）：TeNPy、ITensors.jl / ITensor、tensors.net 相关生态——不再重复保存。
- **已在论文库**（`lit/bibliography.csv`）：Cirac et al., *Matrix product states and projected entangled pair states: Concepts, symmetries, theorems*, RMP 2021。
- 其余条目均为首次保存于本文件。论文的 arXiv 编号已逐条经 arXiv API 核对；Schollwöck 2011 综述两答均列为首推，`lit/` 中原本缺收，如需纳入论文库或下载 PDF 可再走 `lit/download.py` 流程。
- **2026-10-04 更新**：第二、三节全部 15 篇论文已下载至 `lit/dmrg_classics/`（14 篇有 arXiv 版：PDF 按 `年份_arxiv号.pdf` 命名，LaTeX 源码 e-print 在 `src/` 子目录；White 1992 无 arXiv，PDF 取自 TU Dortmund 公开镜像）。清单见 `lit/dmrg_classics/manifest.csv`，下载脚本为 `lit/audit/fetch_dmrg_classics.py`（断点续传）。
- **书籍补充**：清单中唯一的纸书是 Cardy *Scaling and Renormalization in Statistical Physics*（Cambridge 1996），无合法免费全文，仅从作者牛津主页取到样章第 11 章与习题提示（`books/`）。作为替代已下载两本免费讲义式专著：Orús 入门长文（arXiv:1306.2164，附源码）与 Ran 等《Tensor Network Contractions》的 arXiv 讲义版（arXiv:1708.09213，即 Springer LNP 964 开放获取书的前身）及出版版全文（开放获取，脚本下载被反爬拦截、由用户浏览器手动下载，存于 `books/2020_Tensor_Network_Contractions_Springer_LNP964_OA.pdf`）。Z-Library 为盗版书站，未使用。

## 七、两答中的经验性要点（摘录）

- 入门先和导师聊核心理念 + 看知乎中文材料，再读文献；White 1992 开山作反而建议最后读。
- 检验是否搞懂 DMRG 的最好方式是自己写一遍；写的时候注意：MPO 用有限状态机构造、Lanczos 代替精确对角化、避免 periodic DMRG（成环失去 canonical form 数值不稳）、费米子用 Jordan-Wigner 变换。
- fDMRG 即有限系统 DMRG；iDMRG 即 White 最早不断加点直至收敛的 DMRG；tDMRG（TEBD/TDVP 等）主要用于时间演化，虚时演化即可求基态。
