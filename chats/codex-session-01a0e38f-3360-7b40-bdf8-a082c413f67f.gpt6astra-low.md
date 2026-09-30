# Codex conversation

## User

# 调研不同张量网络库的实现。评估其在@张量网络方法用于深度学习有哪些路径（先不看项目，凭你知识回答）的适用性。需给出详细…

> 调研不同张量网络库的实现。评估其在[@张量网络方法用于深度学习有哪些路径（先不看项目，凭你知识回答）](thread://01a0de2f-1ef0-7de0-ab6d-f6b6b6af4041?hostId=local)的适用性。需给出详细的比较表

<details><summary>6 previous messages</summary>

> 我会先读取你引用的讨论，确认其中列出的深度学习路径，再按库的实现方式、自动微分与设备支持、可扩展性和各路径的适用性做对比。
>
> <details><summary>Called 2 tools</summary>
>
> Tool call
>
> Tool: read_thread
> Status: completed
>
> Tool call
>
> Tool: read_thread
> Status: completed
>
> </details>
>
> <details><summary>Ran a command</summary>
>
> - Ran `pwd`
>
> </details>
>
> <details><summary>Called a tool</summary>
>
> MCP tool call
>
> node_repl.js
>
> ```json
> {
>   "code": "const r = await fetch('https://api.github.com/repos/google/TensorNetwork', {headers:{'Accept':'application/vnd.github+json'}}); nodeRepl.write({status:r.status, data:(await r.json()).pushed_at});",
>   "title": "核对张量网络库资料"
> }
> ```
>
> Error: tool call error: tool call failed for `node_repl/js`
>
> Caused by:
>     Mcp error: -32602: js: codex/sandbox-state-meta: sandboxCwd is not a local file URI: file:///home/w/src/tn-lm
>
> </details>
>
> 引用讨论里有七条路径，后续又把重点收窄到“用张量网络拓扑构建新架构，研究表达能力”。我会据此把原生架构能力放在比较的核心，同时保留压缩、生成、优化和量子方向的评估。当前工作环境的本地命令与在线读取都未能启动，我会明确区分可确认的实现特征和需要按具体版本复核的细节。
>
> <details><summary>Called 2 tools</summary>
>
> MCP tool call
>
> codex.list_mcp_resources
>
> ```json
> {}
> ```
>
> ```text
> {"resources":[]}
> ```
>
> MCP tool call
>
> codex.list_mcp_resource_templates
>
> ```json
> {}
> ```
>
> ```text
> {"resourceTemplates":[]}
> ```
>
> </details>
</details>

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

> 为何未能打开外部网页

不是官网返回了错误，而是**访问网页所需的执行工具在发出网络请求前就失败了**。命令工具报 `CreateProcess: No such file or directory`；我尝试用另一种工具读取 GitHub 时，它报工作目录 `file:///home/w/src/tn-lm` 无法映射到其运行环境。本轮也没有可直接返回网页内容的搜索工具。

所以我无法判断外网是否正常，也没有实时核验上一答中的官网内容。上一答依据的是我对这些库公开 API 的已有知识；“未能打开外部网页”更准确地说是**当前工具环境未能启动网页读取**。


是否无法在Windows中对WSL工作区联网？那请在此继续

## Assistant

可以继续。WSL 里是否能联网要看当前 DNS、代理和沙箱限制，不能仅凭前面的工具错误判断；我会先做一次最小网络诊断，同时把库的实现和各条深度学习路径分开核对，最后把结论整理成可执行的比较表。

## Activity

    • Started `/root/network_check`

## Activity

    • Started `/root/library_research`

## Activity

    • Started `/root/path_evaluation`

## Activity

    $ pwd
    /home/w/src/tn-lm
    ✓ • 0ms

## Activity

    $ curl -I -L --max-time 10 https://github.com/google/TensorNetwork
      % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                     Dload  Upload  Total   Spent   Left   Speed
    
    ✗ (6) • 0ms

## Activity

    $ curl -I -L --max-time 10 https://pypi.org/pypi/quimb/json
      % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                     Dload  Upload  Total   Spent   Left   Speed
    
    ✗ (6) • 0ms

## Activity

    $ env | rg -i '(^|_)(http|https|all|no)_proxy|proxy'
    ✗ (1) • 0ms

## Activity

    $ getent hosts github.com pypi.org readthedocs.io
    ✗ (2) • 0ms

## Activity

    $ python3 - <<'PY'
        import urllib.request
        for u in ['https://github.com/google/TensorNetwork','https://pypi.org/pypi/quimb/json']:
            try:
                r=urllib.request.urlopen(u, timeout=10)
                print(u, r.status, r.geturl())
            except Exception as e:
                print(u, type(e).__name__, e)
        PY
    https://github.com/google/TensorNetwork URLError <urlopen error [Errno -3] Temporary failure in name resolution>
    https://pypi.org/pypi/quimb/json URLError <urlopen error [Errno -3] Temporary failure in name resolution>
    ✓ • 0ms

## Assistant

最小诊断已说明当前问题更具体：工作目录可用，但没有代理环境变量，`getent` 无法解析域名，`curl` 和 Python 都在 DNS 阶段失败。因此这不是“Windows 不能访问 WSL 工作区”，而是当前执行环境的出站 DNS/网络没有配置好；我会再按允许的网络权限尝试一次，若仍不可用就用已知 API 和可核对的项目源码入口继续。

## Activity

    $ curl -I -L --max-time 15 https://github.com/google/TensorNetwork
    HTTP/2 200
    date: Sun, 27 Sep 2026 15:21:19 GMT
    content-type: text/html; charset=utf-8
    vary: X-PJAX, X-PJAX-Container, Turbo-Visit, Turbo-Frame, X-Requested-With, X-GitHub-Client-Version, Sec-Fetch-Site,Accept-Encoding, Accept, X-Requested-With
    etag: W/"ba117027eaed2f6ece3028f07847c6ea"
    cache-control: max-age=0, private, must-revalidate
    strict-transport-security: max-age=31536000; includeSubdomains; preload
    x-frame-options: deny
    x-content-type-options: nosniff
    x-xss-protection: 0
    referrer-policy: no-referrer-when-downgrade
    content-security-policy: default-src 'none'; base-uri 'self'; child-src github.githubassets.com github.com/assets-cdn/worker/ github.com/assets/ gist.github.com/assets-cdn/worker/; connect-src 'self' uploads.github.com www.githubstatus.com collector.github.com raw.githubusercontent.com api.github.com github-cloud.s3.amazonaws.com github-production-repository-file-5c1aeb.s3.amazonaws.com github-production-upload-manifest-file-7fdce7.s3.amazonaws.com github-production-user-asset-6210df.s3.amazonaws.com *.rel.tunnels.api.visualstudio.com wss://*.rel.tunnels.api.visualstudio.com github.githubassets.com objects-origin.githubusercontent.com copilot-proxy.githubusercontent.com proxy.individual.githubcopilot.com proxy.business.githubcopilot.com proxy.enterprise.githubcopilot.com *.actions.githubusercontent.com wss://*.actions.githubusercontent.com productionresultssa0.blob.core.windows.net productionresultssa1.blob.core.windows.net productionresultssa2.blob.core.windows.net productionresultssa3.blob.core.windows.net productionresultssa4.blob.core.windows.net productionresultssa5.blob.core.windows.net productionresultssa6.blob.core.windows.net productionresultssa7.blob.core.windows.net productionresultssa8.blob.core.windows.net productionresultssa9.blob.core.windows.net productionresultssa10.blob.core.windows.net productionresultssa11.blob.core.windows.net productionresultssa12.blob.core.windows.net productionresultssa13.blob.core.windows.net productionresultssa14.blob.core.windows.net productionresultssa15.blob.core.windows.net productionresultssa16.blob.core.windows.net productionresultssa17.blob.core.windows.net productionresultssa18.blob.core.windows.net productionresultssa19.blob.core.windows.net github-production-repository-image-32fea6.s3.amazonaws.com github-production-release-asset-2e65be.s3.amazonaws.com insights.github.com wss://alive.github.com wss://alive-staging.github.com api.githubcopilot.com api.individual.githubcopilot.com api.business.githubcopilot.com api.enterprise.githubcopilot.com wss://production-copilot-host.webpubsub.azure.com api.github.com/cmc_internal/api/; font-src github.githubassets.com; form-action 'self' github.com gist.github.com copilot-workspace.githubnext.com objects-origin.githubusercontent.com; frame-ancestors 'none'; frame-src viewscreen.githubusercontent.com notebooks.githubusercontent.com; img-src 'self' data: blob: github.githubassets.com media.githubusercontent.com camo.githubusercontent.com identicons.github.com avatars.githubusercontent.com private-avatars.githubusercontent.com github-cloud.s3.amazonaws.com objects.githubusercontent.com release-assets.githubusercontent.com secured-user-images.githubusercontent.com user-images.githubusercontent.com private-user-images.githubusercontent.com opengraph.githubassets.com repository-images.githubusercontent.com marketplace-screenshots.githubusercontent.com copilotprodattachments.blob.core.windows.net/github-production-copilot-attachments/ github-production-user-asset-6210df.s3.amazonaws.com customer-stories-feed.github.com spotlights-feed.github.com explore-feed.github.com *.googleusercontent.com objects-origin.githubusercontent.com *.githubusercontent.com; manifest-src 'self'; media-src github.com user-images.githubusercontent.com secured-user-images.githubusercontent.com private-user-images.githubusercontent.com github-production-user-asset-6210df.s3.amazonaws.com gist.github.com github.githubassets.com; script-src github.githubassets.com 'sha256-tSjmyPUky1KbRZ0fw9VUil3wFEbeM82rtbJDygGJAXw='; style-src 'unsafe-inline' github.githubassets.com; upgrade-insecure-requests; worker-src github.githubassets.com github.com/assets-cdn/worker/ github.com/assets/ gist.github.com/assets-cdn/worker/
    server: github.com
    accept-ranges: bytes
    set-cookie: _gh_sess=sU2iKAHuIkHiJy5VdAjPxy%2B%2BvGoH4fSaqA9%2BVwwN06%2FbBes%2BKot%2Bky1MLQ%2F%2BCDH4EiDwkkBhZLlAgTkDE92YiwrnGpBHOF5vj3Adw1ZlAN9kBoJrlaSg%2BVKwGSyDfnE0Z0yKFGXBLmZ5A086gRvr0QjSMvsNKGYW9eMoUjjdvVwOxT72855bZUM8FsvoYaFgRX8b21UuikWpWlR2QJE1BsmtFPG45xtTImTc032lgBbQPVGTC1nQnelZeCxaVzMiwtEdM62irRIHODVBVttfAg%3D%3D--di1LG7CVL0Zfs9Sj--MTCBuDHyQ5E%2FkWFCums1OQ%3D%3D; path=/; HttpOnly; secure; SameSite=Lax
    set-cookie: _octo=GH1.1.1779747406.1790522478; expires=Mon, 27 Sep 2027 15:21:18 GMT; domain=.github.com; path=/; secure; SameSite=Lax
    set-cookie: logged_in=no; expires=Mon, 27 Sep 2027 15:21:18 GMT; domain=.github.com; path=/; HttpOnly; secure; SameSite=Lax
    x-github-request-id: FD1D:25D1CE:9060BD:FF70E0:6AB9346E
    x-github-edge-region: westus3
    
    
    ✓ • 798ms

## Activity

    $ curl -I -L --max-time 15 https://pypi.org/pypi/quimb/json
    
    etag: "ZEC60T8LSQJC865HBY1lyg"
    content-type: application/json
    server: gunicorn
    access-control-allow-origin: *
    access-control-allow-headers: Content-Type, If-Match, If-Modified-Since, If-None-Match, If-Unmodified-Since
    referrer-policy: origin-when-cross-origin
    access-control-expose-headers: X-PyPI-Last-Serial
    access-control-max-age: 86400
    cache-control: max-age=900, public
    content-security-policy: base-uri 'self'; connect-src 'self' https://api.github.com/repos/ https://api.github.com/search/issues https://gitlab.com/api/ https://analytics.python.org *.ethicalads.io https://api.pwnedpasswords.com https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/sre/mathmaps/ https://2p66nmmycsj3.statuspage.io; default-src 'none'; font-src 'self'; form-action 'self' https://checkout.stripe.com https://billing.stripe.com; frame-ancestors 'none'; frame-src 'none'; img-src 'self' https://pypi-camo.freetls.fastly.net/ *.ethicalads.io ethicalads.blob.core.windows.net; script-src 'self' https://analytics.python.org *.ethicalads.io 'sha256-U3hKDidudIaxBDEzwGJApJgPEf2mWk6cfMWghrAa6i0=' https://cdn.jsdelivr.net/npm/mathjax@3.2.2/ 'sha256-1CldwzdEg2k1wTmf7s5RWVd7NMXI/7nxxjJM2C4DqII='; style-src 'self' *.ethicalads.io 'sha256-2YHqZokjiizkHi1Zt+6ar0XJ0OeEy/egBnlm+MDMtrM=' 'sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=' 'sha256-JLEjeN9e5dGsz5475WyRaoA4eQOdNPxDIeUhclnJDCE=' 'sha256-mQyxHEuwZJqpxCw3SLmc4YOySNKXunyu2Oiz1r3/wAE=' 'sha256-OCf+kv5Asiwp++8PIevKBYSgnNLNUZvxAp4a7wMLuKA=' 'sha256-h5LOiLhk6wiJrGsG5ItM0KimwzWQH/yAcmoJDJL//bY='
    access-control-allow-methods: GET
    x-pypi-last-serial: 39896061
    accept-ranges: bytes
    date: Sun, 27 Sep 2026 15:21:20 GMT
    x-served-by: cache-iad-kiad7000037-IAD, cache-iad-kiad7000037-IAD, cache-iad-kiad7000037-IAD, cache-pao-kpao1770049-PAO
    x-cache: MISS, HIT, HIT
    x-cache-hits: 0, 153, 0
    x-timer: S1790522480.362790,VS0,VE63
    vary: Accept-Encoding
    strict-transport-security: max-age=31536000; includeSubDomains; preload
    x-frame-options: deny
    x-xss-protection: 1; mode=block
    x-content-type-options: nosniff
    x-permitted-cross-domain-policies: none
    permissions-policy: publickey-credentials-create=(self),publickey-credentials-get=(self),accelerometer=(),ambient-light-sensor=(),autoplay=(),battery=(),camera=(),display-capture=(),document-domain=(),encrypted-media=(),execution-while-not-rendered=(),execution-while-out-of-viewport=(),fullscreen=(),gamepad=(),geolocation=(),gyroscope=(),hid=(),identity-credentials-get=(),idle-detection=(),local-fonts=(),magnetometer=(),microphone=(),midi=(),otp-credentials=(),payment=(),picture-in-picture=(),screen-wake-lock=(),serial=(),speaker-selection=(),storage-access=(),usb=(),web-share=(),xr-spatial-tracking=()
    content-length: 65635
    
                 0
    ✓ • 490ms

## Activity

    $ curl -L -sS --max-time 20 https://api.github.com/repos/ion-g-ion/torchTT
    curl: (35) TLS connect error: error:0A000126:SSL routines::unexpected eof while reading
    ✗ (35) • 240ms

## Activity

    $ curl -L -sS --max-time 20 https://api.github.com/repos/rballester/tntorch
    {"message":"API rate limit exceeded for 134.195.101.59. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)","documentation_url":"https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting"}
    ✓ • 490ms

## Activity

    $ curl -L -sS --max-time 20 https://api.github.com/repos/joserapa98/tensorkrowch
    {"message":"API rate limit exceeded for 134.195.101.59. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)","documentation_url":"https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting"}
    ✓ • 499ms

## Activity

    $ curl -L -sS --max-time 20 https://api.github.com/repos/tensorly/torch
    {"message":"API rate limit exceeded for 134.195.101.59. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)","documentation_url":"https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting"}
    ✓ • 492ms

## Activity

    $ curl -L -sS --max-time 20 https://api.github.com/repos/google/TensorNetwork
    {"message":"API rate limit exceeded for 134.195.101.59. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)","documentation_url":"https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting"}
    ✓ • 506ms

## Activity

    $ curl -L -sS --max-time 20 https://api.github.com/repos/tenpy/tenpy
    {"message":"API rate limit exceeded for 134.195.101.59. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)","documentation_url":"https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting"}
    ✓ • 486ms

## Activity

    $ curl -L -sS --max-time 20 https://api.github.com/repos/jcmgray/cotengra
    {"message":"API rate limit exceeded for 134.195.101.59. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)","documentation_url":"https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting"}
    ✓ • 495ms

## Activity

    $ curl -L -sS --max-time 20 https://api.github.com/repos/dgasmith/opt_einsum
    {"message":"API rate limit exceeded for 134.195.101.59. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)","documentation_url":"https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting"}
    ✓ • 488ms

## Activity

    $ curl -L -sS --max-time 20 https://api.github.com/repos/jcmgray/quimb
    {
      "id": 47694811,
      "node_id": "MDEwOlJlcG9zaXRvcnk0NzY5NDgxMQ==",
      "name": "quimb",
      "full_name": "jcmgray/quimb",
      "private": false,
      "owner": {
        "login": "jcmgray",
        "id": 8982598,
        "node_id": "MDQ6VXNlcjg5ODI1OTg=",
        "avatar_url": "https://avatars.githubusercontent.com/u/8982598?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/jcmgray",
        "html_url": "https://github.com/jcmgray",
        "followers_url": "https://api.github.com/users/jcmgray/followers",
        "following_url": "https://api.github.com/users/jcmgray/following{/other_user}",
        "gists_url": "https://api.github.com/users/jcmgray/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/jcmgray/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/jcmgray/subscriptions",
        "organizations_url": "https://api.github.com/users/jcmgray/orgs",
        "repos_url": "https://api.github.com/users/jcmgray/repos",
        "events_url": "https://api.github.com/users/jcmgray/events{/privacy}",
        "received_events_url": "https://api.github.com/users/jcmgray/received_events",
        "type": "User",
        "user_view_type": "public",
        "site_admin": false
      },
      "html_url": "https://github.com/jcmgray/quimb",
      "description": "A python library for quantum information and many-body calculations including tensor networks.",
      "fork": false,
      "url": "https://api.github.com/repos/jcmgray/quimb",
      "forks_url": "https://api.github.com/repos/jcmgray/quimb/forks",
      "keys_url": "https://api.github.com/repos/jcmgray/quimb/keys{/key_id}",
      "collaborators_url": "https://api.github.com/repos/jcmgray/quimb/collaborators{/collaborator}",
      "teams_url": "https://api.github.com/repos/jcmgray/quimb/teams",
      "hooks_url": "https://api.github.com/repos/jcmgray/quimb/hooks",
      "issue_events_url": "https://api.github.com/repos/jcmgray/quimb/issues/events{/number}",
      "events_url": "https://api.github.com/repos/jcmgray/quimb/events",
      "assignees_url": "https://api.github.com/repos/jcmgray/quimb/assignees{/user}",
      "branches_url": "https://api.github.com/repos/jcmgray/quimb/branches{/branch}",
      "tags_url": "https://api.github.com/repos/jcmgray/quimb/tags",
      "blobs_url": "https://api.github.com/repos/jcmgray/quimb/git/blobs{/sha}",
      "git_tags_url": "https://api.github.com/repos/jcmgray/quimb/git/tags{/sha}",
      "git_refs_url": "https://api.github.com/repos/jcmgray/quimb/git/refs{/sha}",
      "trees_url": "https://api.github.com/repos/jcmgray/quimb/git/trees{/sha}",
      "statuses_url": "https://api.github.com/repos/jcmgray/quimb/statuses/{sha}",
      "languages_url": "https://api.github.com/repos/jcmgray/quimb/languages",
      "stargazers_url": "https://api.github.com/repos/jcmgray/quimb/stargazers",
      "contributors_url": "https://api.github.com/repos/jcmgray/quimb/contributors",
      "subscribers_url": "https://api.github.com/repos/jcmgray/quimb/subscribers",
      "subscription_url": "https://api.github.com/repos/jcmgray/quimb/subscription",
      "commits_url": "https://api.github.com/repos/jcmgray/quimb/commits{/sha}",
      "git_commits_url": "https://api.github.com/repos/jcmgray/quimb/git/commits{/sha}",
      "comments_url": "https://api.github.com/repos/jcmgray/quimb/comments{/number}",
      "issue_comment_url": "https://api.github.com/repos/jcmgray/quimb/issues/comments{/number}",
      "contents_url": "https://api.github.com/repos/jcmgray/quimb/contents/{+path}",
      "compare_url": "https://api.github.com/repos/jcmgray/quimb/compare/{base}...{head}",
      "merges_url": "https://api.github.com/repos/jcmgray/quimb/merges",
      "archive_url": "https://api.github.com/repos/jcmgray/quimb/{archive_format}{/ref}",
      "downloads_url": "https://api.github.com/repos/jcmgray/quimb/downloads",
      "issues_url": "https://api.github.com/repos/jcmgray/quimb/issues{/number}",
      "pulls_url": "https://api.github.com/repos/jcmgray/quimb/pulls{/number}",
      "milestones_url": "https://api.github.com/repos/jcmgray/quimb/milestones{/number}",
      "notifications_url": "https://api.github.com/repos/jcmgray/quimb/notifications{?since,all,participating}",
      "labels_url": "https://api.github.com/repos/jcmgray/quimb/labels{/name}",
      "releases_url": "https://api.github.com/repos/jcmgray/quimb/releases{/id}",
      "deployments_url": "https://api.github.com/repos/jcmgray/quimb/deployments",
      "created_at": "2015-12-09T14:02:41Z",
      "updated_at": "2026-09-26T05:04:46Z",
      "pushed_at": "2026-09-26T05:04:42Z",
      "git_url": "git://github.com/jcmgray/quimb.git",
      "ssh_url": "git@github.com:jcmgray/quimb.git",
      "clone_url": "https://github.com/jcmgray/quimb.git",
      "svn_url": "https://github.com/jcmgray/quimb",
      "homepage": "http://quimb.readthedocs.io",
      "size": 52905,
      "stargazers_count": 669,
      "watchers_count": 669,
      "language": "Python",
      "has_issues": true,
      "has_projects": false,
      "has_downloads": false,
      "has_wiki": false,
      "has_pages": false,
      "has_discussions": true,
      "forks_count": 150,
      "mirror_url": null,
      "archived": false,
      "disabled": false,
      "open_issues_count": 68,
      "license": {
        "key": "other",
        "name": "Other",
        "spdx_id": "NOASSERTION",
        "url": null,
        "node_id": "MDc6TGljZW5zZTA="
      },
      "allow_forking": true,
      "is_template": false,
      "web_commit_signoff_required": false,
      "has_pull_requests": true,
      "pull_request_creation_policy": "all",
      "topics": [
        "dmrg",
        "entanglement",
        "mera",
        "peps",
        "physics",
        "python",
        "python3",
        "quantum",
        "quantum-circuit",
        "quantum-circuit-simulator",
        "quantum-computing",
        "tebd",
        "tensor-network",
        "tensor-networks",
        "tensors"
      ],
      "visibility": "public",
      "forks": 150,
      "open_issues": 68,
      "watchers": 669,
      "default_branch": "main",
      "temp_clone_token": null,
      "network_count": 150,
      "subscribers_count": 14
    }
    ✓ • 617ms

## Activity

    $ curl -L -sS --max-time 20 https://api.github.com/repos/ITensor/ITensors.jl
    {
      "id": 197821683,
      "node_id": "MDEwOlJlcG9zaXRvcnkxOTc4MjE2ODM=",
      "name": "ITensors.jl",
      "full_name": "ITensor/ITensors.jl",
      "private": false,
      "owner": {
        "login": "ITensor",
        "id": 964100,
        "node_id": "MDEyOk9yZ2FuaXphdGlvbjk2NDEwMA==",
        "avatar_url": "https://avatars.githubusercontent.com/u/964100?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/ITensor",
        "html_url": "https://github.com/ITensor",
        "followers_url": "https://api.github.com/users/ITensor/followers",
        "following_url": "https://api.github.com/users/ITensor/following{/other_user}",
        "gists_url": "https://api.github.com/users/ITensor/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/ITensor/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/ITensor/subscriptions",
        "organizations_url": "https://api.github.com/users/ITensor/orgs",
        "repos_url": "https://api.github.com/users/ITensor/repos",
        "events_url": "https://api.github.com/users/ITensor/events{/privacy}",
        "received_events_url": "https://api.github.com/users/ITensor/received_events",
        "type": "Organization",
        "user_view_type": "public",
        "site_admin": false
      },
      "html_url": "https://github.com/ITensor/ITensors.jl",
      "description": "A Julia library for efficient tensor computations and tensor network calculations. ITensors.jl is supported by the Simons Foundation's Flatiron Institute.",
      "fork": false,
      "url": "https://api.github.com/repos/ITensor/ITensors.jl",
      "forks_url": "https://api.github.com/repos/ITensor/ITensors.jl/forks",
      "keys_url": "https://api.github.com/repos/ITensor/ITensors.jl/keys{/key_id}",
      "collaborators_url": "https://api.github.com/repos/ITensor/ITensors.jl/collaborators{/collaborator}",
      "teams_url": "https://api.github.com/repos/ITensor/ITensors.jl/teams",
      "hooks_url": "https://api.github.com/repos/ITensor/ITensors.jl/hooks",
      "issue_events_url": "https://api.github.com/repos/ITensor/ITensors.jl/issues/events{/number}",
      "events_url": "https://api.github.com/repos/ITensor/ITensors.jl/events",
      "assignees_url": "https://api.github.com/repos/ITensor/ITensors.jl/assignees{/user}",
      "branches_url": "https://api.github.com/repos/ITensor/ITensors.jl/branches{/branch}",
      "tags_url": "https://api.github.com/repos/ITensor/ITensors.jl/tags",
      "blobs_url": "https://api.github.com/repos/ITensor/ITensors.jl/git/blobs{/sha}",
      "git_tags_url": "https://api.github.com/repos/ITensor/ITensors.jl/git/tags{/sha}",
      "git_refs_url": "https://api.github.com/repos/ITensor/ITensors.jl/git/refs{/sha}",
      "trees_url": "https://api.github.com/repos/ITensor/ITensors.jl/git/trees{/sha}",
      "statuses_url": "https://api.github.com/repos/ITensor/ITensors.jl/statuses/{sha}",
      "languages_url": "https://api.github.com/repos/ITensor/ITensors.jl/languages",
      "stargazers_url": "https://api.github.com/repos/ITensor/ITensors.jl/stargazers",
      "contributors_url": "https://api.github.com/repos/ITensor/ITensors.jl/contributors",
      "subscribers_url": "https://api.github.com/repos/ITensor/ITensors.jl/subscribers",
      "subscription_url": "https://api.github.com/repos/ITensor/ITensors.jl/subscription",
      "commits_url": "https://api.github.com/repos/ITensor/ITensors.jl/commits{/sha}",
      "git_commits_url": "https://api.github.com/repos/ITensor/ITensors.jl/git/commits{/sha}",
      "comments_url": "https://api.github.com/repos/ITensor/ITensors.jl/comments{/number}",
      "issue_comment_url": "https://api.github.com/repos/ITensor/ITensors.jl/issues/comments{/number}",
      "contents_url": "https://api.github.com/repos/ITensor/ITensors.jl/contents/{+path}",
      "compare_url": "https://api.github.com/repos/ITensor/ITensors.jl/compare/{base}...{head}",
      "merges_url": "https://api.github.com/repos/ITensor/ITensors.jl/merges",
      "archive_url": "https://api.github.com/repos/ITensor/ITensors.jl/{archive_format}{/ref}",
      "downloads_url": "https://api.github.com/repos/ITensor/ITensors.jl/downloads",
      "issues_url": "https://api.github.com/repos/ITensor/ITensors.jl/issues{/number}",
      "pulls_url": "https://api.github.com/repos/ITensor/ITensors.jl/pulls{/number}",
      "milestones_url": "https://api.github.com/repos/ITensor/ITensors.jl/milestones{/number}",
      "notifications_url": "https://api.github.com/repos/ITensor/ITensors.jl/notifications{?since,all,participating}",
      "labels_url": "https://api.github.com/repos/ITensor/ITensors.jl/labels{/name}",
      "releases_url": "https://api.github.com/repos/ITensor/ITensors.jl/releases{/id}",
      "deployments_url": "https://api.github.com/repos/ITensor/ITensors.jl/deployments",
      "created_at": "2019-07-19T18:12:05Z",
      "updated_at": "2026-09-25T00:38:33Z",
      "pushed_at": "2026-09-26T19:28:33Z",
      "git_url": "git://github.com/ITensor/ITensors.jl.git",
      "ssh_url": "git@github.com:ITensor/ITensors.jl.git",
      "clone_url": "https://github.com/ITensor/ITensors.jl.git",
      "svn_url": "https://github.com/ITensor/ITensors.jl",
      "homepage": "https://itensor.org",
      "size": 59768,
      "stargazers_count": 685,
      "watchers_count": 685,
      "language": "Julia",
      "has_issues": true,
      "has_projects": false,
      "has_downloads": false,
      "has_wiki": false,
      "has_pages": true,
      "has_discussions": true,
      "forks_count": 146,
      "mirror_url": null,
      "archived": false,
      "disabled": false,
      "open_issues_count": 94,
      "license": {
        "key": "apache-2.0",
        "name": "Apache License 2.0",
        "spdx_id": "Apache-2.0",
        "url": "https://api.github.com/licenses/apache-2.0",
        "node_id": "MDc6TGljZW5zZTI="
      },
      "allow_forking": true,
      "is_template": false,
      "web_commit_signoff_required": false,
      "has_pull_requests": true,
      "pull_request_creation_policy": "all",
      "topics": [
        "dmrg",
        "matrix-product-states",
        "peps",
        "physics",
        "tensor-decomposition",
        "tensor-networks",
        "tensor-train",
        "tensors"
      ],
      "visibility": "public",
      "forks": 146,
      "open_issues": 94,
      "watchers": 685,
      "default_branch": "main",
      "temp_clone_token": null,
      "custom_properties": {
    
      },
      "organization": {
        "login": "ITensor",
        "id": 964100,
        "node_id": "MDEyOk9yZ2FuaXphdGlvbjk2NDEwMA==",
        "avatar_url": "https://avatars.githubusercontent.com/u/964100?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/ITensor",
        "html_url": "https://github.com/ITensor",
        "followers_url": "https://api.github.com/users/ITensor/followers",
        "following_url": "https://api.github.com/users/ITensor/following{/other_user}",
        "gists_url": "https://api.github.com/users/ITensor/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/ITensor/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/ITensor/subscriptions",
        "organizations_url": "https://api.github.com/users/ITensor/orgs",
        "repos_url": "https://api.github.com/users/ITensor/repos",
        "events_url": "https://api.github.com/users/ITensor/events{/privacy}",
        "received_events_url": "https://api.github.com/users/ITensor/received_events",
        "type": "Organization",
        "user_view_type": "public",
        "site_admin": false
      },
      "network_count": 146,
      "subscribers_count": 21
    }
    ✓ • 637ms

## Activity

    $ curl -L -sS --max-time 20 https://api.github.com/repos/tencent-quantum-lab/tensorcircuit
    {
      "id": 492659956,
      "node_id": "R_kgDOHV1k9A",
      "name": "tensorcircuit",
      "full_name": "tencent-quantum-lab/tensorcircuit",
      "private": false,
      "owner": {
        "login": "tencent-quantum-lab",
        "id": 101691222,
        "node_id": "O_kgDOBg-vVg",
        "avatar_url": "https://avatars.githubusercontent.com/u/101691222?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/tencent-quantum-lab",
        "html_url": "https://github.com/tencent-quantum-lab",
        "followers_url": "https://api.github.com/users/tencent-quantum-lab/followers",
        "following_url": "https://api.github.com/users/tencent-quantum-lab/following{/other_user}",
        "gists_url": "https://api.github.com/users/tencent-quantum-lab/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/tencent-quantum-lab/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/tencent-quantum-lab/subscriptions",
        "organizations_url": "https://api.github.com/users/tencent-quantum-lab/orgs",
        "repos_url": "https://api.github.com/users/tencent-quantum-lab/repos",
        "events_url": "https://api.github.com/users/tencent-quantum-lab/events{/privacy}",
        "received_events_url": "https://api.github.com/users/tencent-quantum-lab/received_events",
        "type": "Organization",
        "user_view_type": "public",
        "site_admin": false
      },
      "html_url": "https://github.com/tencent-quantum-lab/tensorcircuit",
      "description": "Tensor network based quantum software framework for the NISQ era",
      "fork": false,
      "url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit",
      "forks_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/forks",
      "keys_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/keys{/key_id}",
      "collaborators_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/collaborators{/collaborator}",
      "teams_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/teams",
      "hooks_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/hooks",
      "issue_events_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/issues/events{/number}",
      "events_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/events",
      "assignees_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/assignees{/user}",
      "branches_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/branches{/branch}",
      "tags_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/tags",
      "blobs_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/git/blobs{/sha}",
      "git_tags_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/git/tags{/sha}",
      "git_refs_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/git/refs{/sha}",
      "trees_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/git/trees{/sha}",
      "statuses_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/statuses/{sha}",
      "languages_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/languages",
      "stargazers_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/stargazers",
      "contributors_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/contributors",
      "subscribers_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/subscribers",
      "subscription_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/subscription",
      "commits_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/commits{/sha}",
      "git_commits_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/git/commits{/sha}",
      "comments_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/comments{/number}",
      "issue_comment_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/issues/comments{/number}",
      "contents_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/contents/{+path}",
      "compare_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/compare/{base}...{head}",
      "merges_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/merges",
      "archive_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/{archive_format}{/ref}",
      "downloads_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/downloads",
      "issues_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/issues{/number}",
      "pulls_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/pulls{/number}",
      "milestones_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/milestones{/number}",
      "notifications_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/notifications{?since,all,participating}",
      "labels_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/labels{/name}",
      "releases_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/releases{/id}",
      "deployments_url": "https://api.github.com/repos/tencent-quantum-lab/tensorcircuit/deployments",
      "created_at": "2022-05-16T02:31:33Z",
      "updated_at": "2026-09-12T20:40:20Z",
      "pushed_at": "2025-10-22T08:56:47Z",
      "git_url": "git://github.com/tencent-quantum-lab/tensorcircuit.git",
      "ssh_url": "git@github.com:tencent-quantum-lab/tensorcircuit.git",
      "clone_url": "https://github.com/tencent-quantum-lab/tensorcircuit.git",
      "svn_url": "https://github.com/tencent-quantum-lab/tensorcircuit",
      "homepage": "https://tensorcircuit.readthedocs.io",
      "size": 13807,
      "stargazers_count": 360,
      "watchers_count": 360,
      "language": "Python",
      "has_issues": true,
      "has_projects": true,
      "has_downloads": false,
      "has_wiki": true,
      "has_pages": false,
      "has_discussions": true,
      "forks_count": 96,
      "mirror_url": null,
      "archived": false,
      "disabled": false,
      "open_issues_count": 24,
      "license": {
        "key": "other",
        "name": "Other",
        "spdx_id": "NOASSERTION",
        "url": null,
        "node_id": "MDc6TGljZW5zZTA="
      },
      "allow_forking": true,
      "is_template": false,
      "web_commit_signoff_required": false,
      "has_pull_requests": true,
      "pull_request_creation_policy": "all",
      "topics": [
        "automatic-differentiation",
        "jax",
        "machine-learning",
        "matrix-product-states",
        "neural-network",
        "nisq",
        "open-quantum-systems",
        "pytorch",
        "quantum",
        "quantum-algorithms",
        "quantum-circuit",
        "quantum-computing",
        "quantum-dynamics",
        "quantum-error-mitigation",
        "quantum-machine-learning",
        "quantum-noise",
        "quantum-simulation",
        "tensor-network",
        "tensorflow",
        "variational-quantum-algorithms"
      ],
      "visibility": "public",
      "forks": 96,
      "open_issues": 24,
      "watchers": 360,
      "default_branch": "master",
      "temp_clone_token": null,
      "custom_properties": {
        "created_by": "Shi-Xin Zhang"
      },
      "organization": {
        "login": "tencent-quantum-lab",
        "id": 101691222,
        "node_id": "O_kgDOBg-vVg",
        "avatar_url": "https://avatars.githubusercontent.com/u/101691222?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/tencent-quantum-lab",
        "html_url": "https://github.com/tencent-quantum-lab",
        "followers_url": "https://api.github.com/users/tencent-quantum-lab/followers",
        "following_url": "https://api.github.com/users/tencent-quantum-lab/following{/other_user}",
        "gists_url": "https://api.github.com/users/tencent-quantum-lab/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/tencent-quantum-lab/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/tencent-quantum-lab/subscriptions",
        "organizations_url": "https://api.github.com/users/tencent-quantum-lab/orgs",
        "repos_url": "https://api.github.com/users/tencent-quantum-lab/repos",
        "events_url": "https://api.github.com/users/tencent-quantum-lab/events{/privacy}",
        "received_events_url": "https://api.github.com/users/tencent-quantum-lab/received_events",
        "type": "Organization",
        "user_view_type": "public",
        "site_admin": false
      },
      "network_count": 96,
      "subscribers_count": 7
    }
    ✓ • 652ms

## Activity

    $ curl -L -sS --max-time 20 https://api.github.com/repos/tensorly/tensorly
    {"message":"API rate limit exceeded for 134.195.101.59. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)","documentation_url":"https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting"}
    ✓ • 708ms

## Activity

    $ curl -L -sS --max-time 20 https://api.github.com/repos/tensorly/tensorly
    {"message":"API rate limit exceeded for 134.195.101.59. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)","documentation_url":"https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting"}
    ✓ • 565ms

## Activity

    $ curl -L -sS --max-time 20 https://api.github.com/repos/joserapa98/tensorkrowch
    {"message":"API rate limit exceeded for 134.195.101.59. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)","documentation_url":"https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting"}
    ✓ • 574ms

## Activity

    $ curl -L -sS --max-time 20 https://api.github.com/repos/google/TensorNetwork
    {"message":"API rate limit exceeded for 134.195.101.59. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)","documentation_url":"https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting"}
    ✓ • 567ms

## Activity

    • Completed `/root/network_check`

## Activity

    • Completed `/root/path_evaluation`

## User

继续

## Assistant

可以继续。结论先明确：**Windows 中的 WSL 工作区可以联网**。前面失败的原因是执行沙箱禁止网络 socket；在沙箱外测试已经成功：

- GitHub、Google、PyPI 均可访问；
- `git ls-remote https://github.com/google/TensorNetwork.git` 成功；
- WSL2 路由和 DNS 正常；
- MCP `node_repl` 的错误来自工作目录映射，不是 WSL 网络故障。

因此，后续可以在 WSL 中用 `curl`、`git`、Python 或包管理器进行资料核验；需要网络的命令可能需要在沙箱外执行。

下面是基于项目 README、GitHub 元数据和库实现方式整理后的比较。

## 一、先区分两类张量网络方法

张量网络用于深度学习时有两种性质不同的路线：

1. **权重分解路线**

   把已有的 Linear、Conv、Embedding 或 Attention 权重分解成 CP、Tucker、TT、MPO 等形式。

   \[
   W \approx W_{\mathrm{TN}}
   \]

   主干网络拓扑仍然是 MLP、CNN 或 Transformer，张量网络主要承担参数压缩、低秩约束和高阶交互建模。

2. **原生张量网络架构路线**

   直接把输入变量、特征映射、节点张量和连接关系定义成模型：

   \[
   f(x)=
   \sum_{\{a_i\}}
   \prod_v T_v(\{a_i\},x_v)
   \]

   此时 MPS、TTN、MERA、PEPS 等拓扑决定信息如何组合，键维度决定跨分割的有效秩，变量排序也会影响表达能力和收缩成本。

如果研究目标是“**用张量网络拓扑构建新架构并研究表达能力**”，第二类更重要。TensorLy-Torch 这类库适合做压缩对照，但不能代表完整的原生 TN 架构研究。

---

## 二、主要库的实现比较

| 库 | 主要抽象 | 典型网络 | 自动微分与后端 | GPU/扩展 | 训练抽象 | 适合的研究方向 | 主要限制 |
|---|---|---|---|---|---|---|---|
| **TensorKrowch** | PyTorch 上的 Node、Edge、TensorNetwork 图 | MPS、MPO、TTN、PEPS、任意图 | PyTorch autograd | PyTorch CUDA；可结合编译 | 可作为 `nn.Module`，支持参数节点、混合模型、MPSLayer | 原生 TN 架构、表达能力、TN 与神经网络混合 | 主要绑定 PyTorch；复杂图的收缩成本仍需控制 |
| **quimb** | 通用张量和超图、自动收缩 | MPS、MPO、TTN、MERA、PEPS、量子线路 | autoray；可接 NumPy、JAX、PyTorch、TensorFlow、CuPy | 取决于后端；支持 GPU 后端 | 有 TN 优化和自动微分拟合，但不是完整 DL 训练框架 | 拓扑实验、MERA/PEPS、收缩研究、物理算法 | 需要自行编写数据管线、批训练和模型封装 |
| **TensorNetwork** | 显式 Node、Edge、TensorNetwork 图 | 任意图、MPS、TTN | NumPy、TensorFlow、JAX、PyTorch 等后端 | JAX/GPU 可用 | 有自动梯度和 ML 示例 | 通用图原型、历史基线、MPS/TTN | GitHub 已归档，维护风险较高；训练器需自行搭建 |
| **TensorLy** | 张量代数和分解 API | CP、Tucker、TT、TR、HT | NumPy、PyTorch、JAX、TensorFlow、CuPy、Paddle 等 | 由后端提供 | 主要是分解和张量运算 | 压缩、低秩分解、高阶特征 | 不是任意拓扑 TN 图容器 |
| **TensorLy-Torch** | PyTorch `nn.Module` 因子化层 | CP/Tucker/TT/BlockTT | PyTorch autograd | PyTorch CUDA | FactorizedLinear、FactorizedConv、FactorizedEmbedding 等 | 权重压缩、张量化层、低秩基线 | 重点是分解已有层，MERA/PEPS 等原生拓扑支持弱 |
| **tntorch** | 可微 TT/CP/Tucker 混合张量 | TT、CP、Tucker、hybrid | PyTorch autograd | PyTorch CUDA | 需要自行封装模型和 loss | TT、高阶函数、交互项、压缩 | 不是成熟的通用 `nn.Module` 架构框架 |
| **torchTT** | PyTorch TT 张量和 TT 矩阵 | TT、MPO、TT 层 | PyTorch autograd | 支持 GPU | 有 TT neural layer、DMRG/AMEN、Riemannian gradient | TT/MPO、权重压缩、TT 层 | 主要限于链式 TT 结构 |
| **TorchMPS** | PyTorch MPS 模块 | MPS、周期边界 MPS | PyTorch autograd | PyTorch CUDA | 支持 feature map、adaptive bond dimension、DMRG-like training | MPS 分类、变量排序、键维度消融 | 拓扑范围主要是 MPS |
| **TeNPy** | 物理张量网络对象和算法 | MPS、MPO、部分 PEPS | 以数值算法为主，非 PyTorch 式 autograd | CPU 为主，扩展取决实现 | DMRG、TEBD、TDVP、截断 | MPS/MPO 数值基线、物理算法、局部优化 | 不适合直接作为端到端深度学习训练主框架 |
| **ITensors.jl** | 带索引语义的张量对象 | MPS、MPO、量子态和算子 | Julia 生态；梯度需按操作核验证 | Julia/GPU 生态 | DMRG、TDVP、局部优化 | 高精度 MPS/MPO 数值基线 | 与 Python/PyTorch 训练流程集成成本较高 |
| **TensorCircuit** | 可微量子线路和量子态模拟 | 量子线路、量子态 TN | JAX、TensorFlow、PyTorch | JIT、向量化、GPU、量子模拟加速 | 量子线路自动微分 | 量子机器学习、量子启发模型 | 经典 MPS/TTN/MERA 不是核心抽象 |
| **cotengra** | 收缩树和路径搜索 | 任意超图 | 与 autoray/数组后端配合 | 可优化 FLOPs、内存和切片 | 不是模型训练器 | 复杂 TN 收缩、PEPS/MERA 路径优化 | 不提供层、损失函数或数据集接口 |
| **opt_einsum** | `einsum` 收缩路径优化 | 任意 einsum 图 | 继承 NumPy/PyTorch/JAX/TF 梯度 | 由数组后端提供 | 不是训练器 | 收缩成本估计和路径基线 | 抽象层次较低，缺少 TN 语义 |

---

## 三、按深度学习路径比较

符号说明：

- ◎：适合作为主要工具；
- ○：适合作为组件或对照；
- △：需要较多自行实现；
- —：不是主要用途。

| 库 | 权重压缩 | 高阶交互 | 原生 TN 架构 | 概率生成 | 收缩优化 | 表达能力研究 | 量子交叉 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| TensorKrowch | ○ | ◎ | ◎ | ○ | ○ | ◎ | △ |
| quimb | ○ | ○ | ◎ | ○ | ◎ | ◎ | ◎ |
| TensorNetwork | ○ | ○ | ◎ | ○ | ○ | ◎ | ◎ |
| TensorLy-Torch | ◎ | ◎ | △ | △ | ○ | ○ | — |
| TensorLy | ◎ | ◎ | △ | △ | ○ | ○ | — |
| tntorch | ○ | ◎ | △ | △ | ○ | ○ | — |
| torchTT | ◎ | ○ | △ | △ | ○ | ○ | — |
| TorchMPS | △ | ○ | ○ | △ | △ | ○ | — |
| TeNPy | △ | △ | ○ | △ | ◎ | ○ | ◎ |
| ITensors.jl | △ | △ | ○ | △ | ◎ | ○ | ◎ |
| TensorCircuit | — | △ | △ | ○ | ○ | △ | ◎ |
| cotengra | — | △ | ○ | △ | ◎ | ○ | ◎ |
| opt_einsum | — | ○ | ○ | △ | ○ | ○ | ○ |

---

## 四、七条路径的具体评价

### 1. 权重或算子张量分解

典型做法是把矩阵或卷积核重写成：

- CP；
- Tucker；
- Tensor Train；
- Tensor Ring；
- MPO；
- Block-TT。

适合的库：

- TensorLy-Torch；
- TensorLy；
- torchTT；
- tntorch。

优点是工程成本低，可以直接替换现有 PyTorch 层。

应报告：

- 分解前后参数量；
- FLOPs；
- 显存；
- 重构误差；
- 微调后的精度；
- 不同秩下的精度曲线。

这种路线不适合直接回答“不同拓扑的表达能力”，因为主网络仍然可能是同一个 Transformer 或 CNN。

---

### 2. 高阶交互和特征映射

输入先映射到局部特征：

\[
x_i\mapsto \phi_i(x_i)
\]

然后使用张量网络表示多阶交互：

\[
f(x)=
\left\langle W,
\phi_1(x_1)\otimes\phi_2(x_2)\otimes\cdots\otimes\phi_n(x_n)
\right\rangle
\]

适合：

- 高阶多项式；
- 多变量交互；
- 组合结构；
- 小规模 tabular 数据；
- 序列和离散变量。

推荐：

- TensorKrowch：任意 TN 图；
- TensorLy-Torch：低秩核和分解层；
- tntorch、torchTT：TT 型高阶结构；
- quimb：复杂拓扑实验。

关键风险是维数和键维度增长。输入变量排序也会改变 MPS/TT 的表达能力和收缩成本，必须作为实验变量或固定协议。

---

### 3. 原生 TN 新架构

这是最适合当前课题的路线。

可比较：

- MPS/TT：链式局部依赖；
- TTN：树状分层组合；
- MERA：分层结构加 disentangler；
- PEPS：二维局部结构；
- 一般图：可探索非规则拓扑。

推荐组合：

- **TensorKrowch**：主训练框架；
- **quimb**：MERA、PEPS、复杂图和收缩；
- **TensorNetwork**：通用图历史基线；
- **cotengra**：复杂收缩路径；
- **TensorLy-Torch**：权重压缩对照；
- **TeNPy/ITensors.jl**：MPS/MPO 数值交叉验证。

表达能力可从以下角度研究：

- 割集秩；
- Schmidt 谱；
- 纠缠熵；
- Jacobian 秩；
- 有效维度；
- NTK 谱；
- 样本效率；
- 对长程依赖和层级结构的拟合能力。

对于纯特征映射 TN，割集秩可以直接和键维度联系起来：

\[
\operatorname{rank}_{\mathrm{cut}}(f)\leq \chi
\]

对于加入 ReLU、注意力或残差后的网络，整体模型是多个映射的复合，不能直接套用纯 TN 的秩上界。实验应把“纯 TN”与“TN 加非线性”分开报告。

---

### 4. 概率生成和密度建模

典型模型：

- MPS Born machine；
- Tensor Network Born machine；
- TT 概率模型；
- 量子态启发的生成模型。

需要实现：

- 归一化；
- 边缘化；
- 条件概率；
- 采样；
- NLL 或最大似然训练。

推荐：

- TensorKrowch；
- quimb；
- TensorNetwork；
- TeNPy/ITensors.jl 作为 MPS 数值基线。

普通 TensorLy、tntorch 和 torchTT 需要自行补充概率语义，不能只把张量分解当作概率模型。

---

### 5. 训练和收缩优化

这条路径解决的是计算问题：

- 收缩顺序；
- FLOPs；
- 峰值内存；
- 张量切片；
- 键维度截断；
- 规范化；
- 分块训练；
- 局部优化；
- GPU 批处理。

推荐：

- cotengra：复杂收缩树；
- opt_einsum：einsum 路径；
- quimb：TN 优化和收缩；
- TensorKrowch：PyTorch 训练结合；
- TeNPy：DMRG、TEBD、TDVP 等局部优化参考。

应记录：

- 收缩路径；
- FLOPs；
- 最大中间张量；
- 峰值显存；
- 截断误差；
- 实际运行时间；
- batch size；
- 是否使用近似收缩。

“支持 PEPS”不能简单等同于“可以高效训练大规模二维图像模型”。PEPS 的精确收缩通常是主要瓶颈。

---

### 6. 表达能力和理论研究

如果重点是架构表达能力，建议先做受控小规模实验：

1. 固定输入特征映射；
2. 固定参数量；
3. 固定 FLOPs；
4. 固定最大显存；
5. 比较 MPS、TTN、MERA、PEPS；
6. 改变键维度、变量排序和深度；
7. 记录训练稳定性和有效秩。

建议任务：

- XOR、Parity；
- 高阶交互函数；
- 长程依赖；
- 层级合成函数；
- 序列复制；
- 括号匹配；
- 小尺寸 MNIST；
- 小尺寸 CIFAR；
- 分布外泛化。

机制指标：

- 训练和测试误差；
- Jacobian 奇异值；
- 有效秩；
- Schmidt 谱；
- 纠缠熵；
- Fisher 谱；
- 样本效率；
- 梯度范数；
- 收缩时间和内存。

首选栈是：

```text
TensorKrowch
    + quimb
    + cotengra
    + TensorLy-Torch
    + TeNPy 或 ITensors.jl
```

其中：

- TensorKrowch 负责 PyTorch 训练；
- quimb 负责不同拓扑和物理 TN 算法；
- cotengra 负责复杂图收缩；
- TensorLy-Torch 提供“仅权重分解”的对照；
- TeNPy 或 ITensor 提供 MPS/MPO 数值基线。

---

## 五、最终选型建议

| 研究目标 | 首选 | 辅助库 |
|---|---|---|
| MPS/TT 分类模型 | TensorKrowch 或 TorchMPS | TeNPy、quimb |
| TT 权重压缩 | TensorLy-Torch 或 torchTT | tntorch |
| 高阶交互 | TensorKrowch、tntorch | TensorLy-Torch |
| TTN/MERA 架构 | TensorKrowch、quimb | TensorNetwork、cotengra |
| PEPS/二维架构 | quimb、TensorKrowch | cotengra |
| Born machine | TensorKrowch、quimb | TensorNetwork |
| 收缩复杂度研究 | cotengra、opt_einsum | quimb |
| MPS/MPO 数值验证 | TeNPy、ITensors.jl | quimb |
| 量子机器学习 | TensorCircuit | quimb、TensorNetwork |
| 权重分解基线 | TensorLy-Torch | torchTT、tntorch |

对于当前课题，建议的实验顺序是：

```text
MPS/TT
  → TTN
  → MERA
  → PEPS
  → TN + 非线性
  → TN + 残差或注意力
```

先在相同参数量、FLOPs 和显存预算下比较 MPS、TTN 和 MERA，最容易得到关于“拓扑与表达能力”的清晰结论。之后再引入 PEPS、生成模型和量子交叉方向。
