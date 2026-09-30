我按引用聊天中的**七条路径**评估，同时把重点放在你后来明确的目标：**让张量网络拓扑成为新模型架构，并研究表达能力**。下表比较的是库对研究原型的适用性，不是模型精度或运行速度排名。

### 实现方式比较

| 库 | 核心实现与现成能力 | 反向传播与设备 | 对新架构研究的主要限制 |
|---|---|---|---|
| [TensorKrowch](https://github.com/joserapa98/tensorkrowch) | PyTorch 的节点、边和可训练网络抽象；适合搭 MPS、树形及二维类模型 | 使用 PyTorch 自动微分与设备 | 深层模型的非线性、残差和实验流程仍需设计；复杂图仍受收缩成本限制 |
| [TensorNetwork](https://github.com/google/TensorNetwork) | 显式 `Node`/`Edge` 图、收缩器、MPS 工具；拓扑自由度高 | NumPy、JAX、PyTorch、TensorFlow 等后端 | 是通用底座，神经网络层、批训练和生成概率计算需自建 |
| [quimb](https://quimb.readthedocs.io/en/latest/) | 通用张量网络、MPS、MERA、二维网络及收缩工具；可做树形图 | `TNOptimizer` 可接自动微分后端；GPU 取决于数组后端 | 适合拓扑实验，但深度学习数据流程、Born 损失和混合网络需自建 |
| [TensorLy](https://github.com/tensorly/tensorly) + [TensorLy-Torch](https://github.com/tensorly/torch) | CP、Tucker、TT 分解及可训练的因子化线性、卷积等层 | PyTorch 层可直接参与训练 | 强项是**权重分解**；MERA、PEPS 等网络拓扑不是其核心抽象 |
| [tntorch](https://github.com/rballester/tntorch) | PyTorch 上的 TT、Tucker 等高维张量表示、近似与运算 | PyTorch 自动微分 | 适合高阶函数和 TT 基线，缺少任意拓扑神经网络容器 |
| [torchTT](https://github.com/ion-g-ion/torchTT) | TT 张量、TT 矩阵及相关数值运算 | PyTorch 自动微分 | 适合 MPO/TT 算子实验；范围主要限于链式结构 |
| [TorchMPS](https://github.com/jemisjoky/torchmps) | 面向 PyTorch 的 MPS 模型 | PyTorch 自动微分 | 快速建立 MPS 对照方便，难承担跨拓扑统一框架 |
| [TeNPy](https://tenpy.readthedocs.io/en/latest/) | MPS/MPO、规范形式、截断、DMRG、TEBD、TDVP | 以物理数值计算流程为主 | 很适合研究键维和截断；PyTorch 式批训练及原生 MERA/PEPS 需大量改造 |
| [ITensors.jl / ITensorMPS.jl](https://github.com/ITensor/ITensorMPS.jl) | 带索引语义的张量运算、MPS/MPO、量子数与局部优化算法 | Julia 生态；梯度和 GPU 覆盖须按具体操作核对 | 数值基线强，与 Python 神经网络训练流程的集成成本较高 |
| [TensorCircuit](https://github.com/tencent-quantum-lab/tensorcircuit) | 可微量子线路及 MPS 线路模拟 | 支持自动微分后端 | 适合量子机器学习，经典 TTN/MERA/PEPS 架构并非主抽象 |
| [cotengra](https://github.com/jcmgray/cotengra) | 搜索收缩路径、复用计划、切片控制峰值内存 | 可配合多种数组后端；路径搜索本身是离散步骤 | 是复杂图的计算组件，不提供模型层或训练器 |
| [opt_einsum](https://github.com/dgasmith/opt_einsum) | `einsum` 收缩路径规划、FLOPs 与中间张量估算 | 梯度取决于所用数组后端 | 适合收缩成本基线；没有 TN 模型、规范化或采样语义 |

### 对七条路径的适用性

`◎` 适合作为核心工具；`○` 适合作为组件或基线；`△` 需要较多自行实现；`—` 并非主要用途。“优化”同时涵盖局部数值优化和收缩路径优化，具体区别见上表。

| 库 | 参数压缩 | 高阶交互 | 原生新架构 | 概率生成 | 训练/收缩优化 | 表达能力实验 | 量子交叉 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| TensorKrowch | ○ | ◎ | ◎ | ○ | ○ | ◎ | △ |
| TensorNetwork | △ | ○ | ◎ | ○ | ○ | ◎ | ◎ |
| quimb | △ | ○ | ◎ | ○ | ◎ | ◎ | ◎ |
| TensorLy + TensorLy-Torch | ◎ | ◎ | △ | △ | ○ | ○ | — |
| tntorch | ○ | ◎ | △ | △ | ○ | ○ | — |
| torchTT | ○ | ○ | △ | △ | ○ | ○ | — |
| TorchMPS | △ | ○ | ○ | △ | △ | ○ | — |
| TeNPy | △ | △ | ○ | △ | ◎ | ○ | ◎ |
| ITensors.jl | △ | △ | ○ | △ | ◎ | ○ | ◎ |
| TensorCircuit | — | △ | △ | ○ | ○ | △ | ◎ |
| cotengra | — | △ | ○ | △ | ◎ | ○ | ◎ |
| opt_einsum | — | ○ | ○ | △ | ○ | ○ | ○ |

### 针对课题的选型

| 要比较的架构 | 建议起点 | 需要控制或记录的变量 |
|---|---|---|
| **MPS/TT 与 TTN** | TensorKrowch 做可训练模型；quimb 或 TensorNetwork 做拓扑对照 | 特征映射、变量顺序、键维度、深度、参数量和 FLOPs |
| **MERA** | quimb 或 TensorNetwork | disentangler/isometry 约束、收缩方式；不能只换图形而忽略这些结构条件 |
| **PEPS/二维网络** | quimb，复杂收缩辅以 cotengra | 网格宽度、峰值内存、近似收缩及截断误差；“支持 PEPS”不代表能高效训练大图像 |
| **MPO-MLP、TN-RNN、TN-Transformer** | TensorKrowch 搭 TN 模块；TensorLy-Torch 做分解权重基线 | 区分“TN 决定信息组合方式”和“仅压缩原有权重” |
| **Born machine** | 从 MPS 和 quimb/TensorKrowch 起步 | 归一化、边缘化、条件采样是否真能按所选结构高效计算 |

**我会优先用 TensorKrowch + quimb 做主实验，TensorLy-Torch 做压缩对照，TeNPy 或 ITensors 做 MPS 数值对照。**先比较纯 MPS、TTN、MERA 在相同输入映射和计算预算下的表达，再加入非线性或残差。纯 TN 的割集秩上界，不能直接套到加入 ReLU、注意力后的整个网络。

本轮工具环境未能打开外部网页或运行库，因此表格依据这些项目已知的公开 API 设计；**最新版本、维护状态、具体模板类名和性能尚未实时核验**，这里不作这几项的确定性排名。

