# 直接张量语言模型：NLP 实测证据核查

核查日期：2026-10-01。重点是张量网络直接作为序列模型，而不是 TT 压缩 Transformer 权重。正文位置：`app/index.html#native-lm-benchmarks`；现代矩阵状态对照：`#matrix-state-benchmarks`。

## 核查结论

第一条路线已经有标准词级语言建模分数，至少包括 AAAI 2019 的 TSLM、2024 的 TTLM、ROCLING 2025 的增强 TTLM。但“直接参与建模”不等于“纯 Born-MPS”：后两类以 softmax 输出条件概率，2025 的最佳变体还加入了注意力。严格的 Born-uMPS 目前能核实的自然文本实验更窄。检索未找到纯 Born-MPS 在接近现代预训练预算下系统对标 Mamba／RWKV 的论文；这是本轮检索结果，不是不存在此类论文的证明。

## 概率定义决定哪些理论性质能迁移

- **Born-uMPS**：联合概率为矩阵链振幅的模平方，经全局配分函数归一化。能利用双层转移算子做精确边缘化、条件采样及正则约束采样。
- **TSLM／TTLM**：通过张量分解或双线性递归形成隐藏表示，softmax 定义 next-token 条件概率。概率的非线性归一化会改变整条序列的表示，不能直接沿用 Born-MPS 的联合分布 rank／互信息上界。
- **增强 TTLM**：进一步添加残差、偏置、可能的非线性和历史状态交互。注意力／EMA 引入的记忆必须计入模型总状态，不能只用核心 TT rank 描述其全部容量。
- **M²RNN**：非线性矩阵状态递归。属于现代序列架构的强对照，不能因隐藏态是矩阵就称为 MPS 概率模型。

上述分类依据原文公式，而不是标题中的 tensor、quantum 或 entanglement。

## 四组可复核实测

| 工作 | 数据／规模 | 实测 | 主要限制 |
|---|---|---|---|
| uMPS，AISTATS 2021 | 约 4,000 个邮箱地址，χ=50 | 字符 PPL 7.8→7.3（regex 正则化）；无约束生成语法合法率 35.4%→37.2% | 合成文法的长度泛化与邮箱结果必须分开；约束采样语法正确也不代表模型理解自然语言 |
| TSLM，AAAI 2019 | PTB／WT2，隐藏维 256／512，训练窗口 30／40 | TSLM 108.1／100.4；自实现 LSTM 110.3／101.4。MoS 后 83.6／81.0，对照 RNN+MoS 84.3／81.8 | 小模型、有限收益；并未优于表中所有历史 LSTM；非 Born 概率定义 |
| TTLM，2024 | PTB 4.2M／WT2 11.8M 参数，rank 20 | Large PPL 99.3／82.3；普通 RNN 115.3／96.6 | 原始 TTLM 559.8／546.4，改进来自变体。Transformer 对照 208.7／293.0，不能支持现代架构领先 |
| 增强 TTLM，ROCLING 2025 | rank 60；WT2 约 117M 参数 | 窗口 35：注意力变体 73.5、Transformer 73.7；窗口 128／256：66.42／65.38 | 后两种窗口没有同设置强架构对照；WT2 仍是约 2.09M 独立训练词元；大参数量不等于大语料预训练 |

PPL 均按论文表格抄录，不能跨分词、语料处理和训练协议直接比较。训练窗口是截断反向传播／输入序列长度；是否跨 batch 保留状态，需要复现代码另行检查，不能自动视为模型有效上下文上限。以上为文献核查，未运行作者模型复现分数。

### 2025 工作的独立审查点

原文表 6 的窗口 256 对照中，不含增强模块的 M-TTLM-L 为 66.49，注意力版为 65.38，Hadamard 版为 65.95。工程改善和附加模块贡献应分别消融。

注意力式 (5) 的复杂度为 O(NMR)，块数 M=⌈N/C⌉。**按该公式推导**，固定 C 时是 O(N²R/C)；只有固定摘要数量等额外假设才能将这一项写为关于 N 线性。Hadamard／EMA 式 (6) 为 O(NR)。表 6 将窗口 128→256 时块长也由 16→32，摘要数量近似保持不变；这同时改变两个变量，不能据此验证固定块长的线性复杂度。

论文只给固定随机种子，没有误差条；部分主文“所有变体胜过 Transformer”的措辞也强于表格结果，例如 PTB rank 60 的 83.7 仍略差于 Transformer 83.6。应以逐项表格为准。

## 公开代码与复现准备度

- [uMPS 作者代码](https://github.com/jemisjoky/umps_code)：含 Born 模型与合成任务实验；MIT 许可证。README 明确注明不包含论文中的完整 regex sampler，不应把公开仓库视为完整正则采样实现。
- [TSLM 作者主页所列代码](https://github.com/shuishen112/AAAI19-TSLM)：链接由[作者主页](https://shuishen112.github.io/zhansu/)确认；本轮网页工具未成功读取仓库，不宣称已检查可运行性。
- [TTLM 作者代码](https://github.com/shuishen112/tensortrainlm)：README 提供 PyTorch／Lightning 实现、PTB／WT2 数据和训练入口。其默认 sequence length=30；README 列出了多类递归对照。未安装依赖或运行训练。
- 增强 TTLM：论文及 ACL 页面未给出作者代码链接，本轮定向检索也未定位；这是复现成本，不应写成确定没有公开代码。
- [M²RNN 训练框架](https://github.com/open-lm-engine/lm-engine)、[内核](https://github.com/open-lm-engine/accelerated-model-architectures)、[模型权重](https://huggingface.co/collections/open-lm-engine/m2rnn)：用于现代架构对照，不属于严格 Born-MPS 复现资产。

## 邻近结果及排除口径

Harvey 等（Scientific Reports 2025）的张量网络序列分类在 50,000 条 IMDb 评论上报告卷积模型准确率 88%，[代码公开](https://github.com/CQCL/classification-with-qttn)。这是实际 NLP 分类，生成式语言建模在文中是后续扩展。

2025／2026 的 POVM token 嵌入、unitary MPS、adaptive tensor tree 等工作改善 RNA、图像或结构化数据的建模，不能自动作为开放域 LM 对标证据。TPM 2026 的 “Robust classification and purification with a single tensor network Born machine” 仍评测 spirals／MNIST，未补足 NLP 证据。2025 PRA 的依存树模型用于解释文本互信息标度，不能当作现代 LM 任务分数。

“Tensor Train Recurrent Network Language Model Prediction”（Stat 2025）属于 LSTM 权重张量化／先验引导压缩；TensorGPT、Saten、MetaTT 等属于压缩或适配。题目包含 MPS／language model 并不足以归入第一条路线。搜索中的 Apple Metal MPS、NVIDIA Multi-Process Service 和面向 tensor-program 的 GPT-2 生成器也应排除。

找到 Ghent 2023 的 “Generative machine learning with tensor networks” 学位论文线索，但原始 PDF 在本轮网页工具中无法读取，未将二手摘要或搜索片段中的结果提升为已核实证据。

## 第一条路线下一步应回答什么

1. **能力还是优化问题？** 固定语料、分词和参数预算，对比 Born-uMPS、TTLM-Tiny／Large 与调优 LSTM／Transformer；至少三个随机种子，同时报告训练／验证 NLL，区分过拟合、数值失稳与容量不足。
2. **记忆来自哪里？** 对增强 TTLM 分开消融原生核心、残差／非线性、EMA、注意力；记录整个推理状态的字节数。截断训练窗口、评测窗口和持续状态重置协议分别说明。
3. **是否真的高效？** 记录实际 tokens/s、峰值显存和生成延迟；χ 的 O(χ³) 收缩开销、大词表 O(|V|χ²) 级参数压力与 GPU kernel 效率不能只用参数量代替。
4. **怎样走向现代 NLP？** 先在可复现的标准小语料上建立强对照，再增加独立训练语料与固定词元预算；只有固定同一 tokenizer、数据、预算的比较，才能讨论与 Mamba／RWKV 的差距。分类准确率、文法合法率和词级 PPL 应各自报告。

## 一手来源

- [uMPS：PMLR 论文及表 2–5](https://proceedings.mlr.press/v130/miller21a/miller21a.pdf)
- [TSLM：AAAI 发表页面](https://ojs.aaai.org/index.php/AAAI/article/view/4735)、[全文表 2／式 17–20](https://arxiv.org/html/1901.11167)
- [TTLM：全文表 1、§6.3–6.4](https://arxiv.org/html/2405.04590)
- [增强 TTLM：ROCLING 发表页面](https://aclanthology.org/2025.rocling-main.27/)、[原文式 5–6、表 3–6](https://aclanthology.org/2025.rocling-main.27.pdf)
- [量子启发序列分类：Scientific Reports](https://www.nature.com/articles/s41598-024-84295-2)
- [M²RNN：v2 表 1–2 与训练协议](https://arxiv.org/html/2603.14360v2)
- [TPM 2026：Born 模型工作任务范围](https://tractable-probabilistic-modeling.github.io/tpm2026/papers/)
- [文本互信息与依存树：PRA 111, 032409](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.111.032409)

代码链接逐篇核查结果另见 [开源链接审计](nlp_code_links_2026-10-01.json)。
