# Phase 6 设计笔记：pytket-dqc 系实验（Fig. 11 + Table III）

## 论文设置（Sec. IV-A2(b), IV-D）

6 种 scheduling–partitioning 配置：

| 配置 | QPU 分配 & 调度 | 电路分割 |
|---|---|---|
| Pytket-PA | pytket-dqc 原生 placement（逐电路顺序处理） | PartitioningAnnealing |
| Pytket-PH | 同上 | PartitioningHeterogeneous (KaHyPar) |
| Single+PA | 我方 Single-QCirc 调度器 | pytket-dqc PA（网络图限制在所分配 QPU 子集） |
| Single+PH | 同上 | PH |
| Batch+PA | 我方 Batch-QCirc 调度器 | PA（限制在所分配子集） |
| Batch+PH | 同上 | PH |

场景：Sc.1 / Sc.2 / Sc.3（Sc.3: R_QFT=R_DJ=[22,30]，R_GHZ=R_W=[24,32]，全部超过单 QPU 最大容量 20，强制分布式）；M ∈ {12, 20, 28}。指标：ebits/QCirc、partitions/QCirc、normalised makespan；Table III：M=28、PH 下按类型 ebits。

## 技术路线

- 环境：`conda env pytket_dqc`（python 3.10），`pip install git+https://github.com/CQCL/pytket-dqc`
- 电路：需要真实 pytket `Circuit`（不是图模型）。按 circuits.py 同样的门序构造：
  GHZ: H + CX 链；W-state: 受控 G + CX 阶梯（用 CRy+CX 近似标准 W-state 制备）；
  DJ: H 层 + CX 到 ancilla + H 层；QFT: H + CU1 阶梯。
  ⚠️ pytket-dqc 要求电路先 rebase 到其支持的门集（CU1/Rz/H 等，`DQCPass`）。
- 网络：`NISQNetwork(server_coupling, server_qubits)`——server=QPU，容量=server_qubits 数量；
  全连通 server_coupling（fat-tree 逻辑上全通）。注意 pytket-dqc 不支持异构链路成本 →
  ebit 计数按其 distribution.cost()（跨 server 门/ebit 数）。
- 映射回我们的指标：
  - ebits/QCirc = distribution cost（pytket-dqc 的 ebit 计数）
  - partitions/QCirc = 分配到的非空 server 数
  - makespan：将 pytket 分布结果映射回我们的 JET 模型（跨 server 门→对应 QPU 对的 T_link），
    在同一事件驱动仿真器里执行（Pytket-* 配置的调度顺序=逐电路 FIFO；Single+/Batch+ 用我方调度器的时序）。
- 进程边界：主实验仍在 py3.13 跑；pytket 部分经 `subprocess` 调 py3.10 解释器执行一个 worker 脚本
  （JSON in/out：门序列+server 配置 → 每 qubit 的 server 分配 + ebit 数），避免两个环境纠缠。

## 风险

1. pytket-dqc 安装失败（kahypar wheel 在 macOS arm64 可能没有）→ 备选：Docker（linux/amd64）或仅复现 PA（不依赖 kahypar）。
2. W-state 的标准制备电路与论文用的 MQT Bench 版本可能有差异 → 用图模型对齐验证（w=4 时边权 2 的路径图）。
3. pytket-dqc 的 cost 定义（含 detached gates / embedding）与论文 ebit 计数的对应关系需实验校准（Table III 有具体数值可对照：如 Sc.1 M=28 Pytket-PH QFT=1.375, Batch+PH QFT=0）。
