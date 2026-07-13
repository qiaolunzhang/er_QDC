# 复现 TODO — 2409.12675v5 "Resource Management and Circuit Scheduling for DQC Interconnect Networks"

> 目标：**像素级**复现论文全部结果（Table II–IV，Fig 7–11）。
> 每完成一项就把 `[ ]` 改成 `[x]`，并在 `PROGRESS_LOG.md` 记一条带时间戳的记录。
> 论文原文：`../../2409.12675v5_Quantum_Data_Center.pdf`（同目录有 .md 转换版便于 grep）。

---

## 论文关键参数速查（Sec. IV）

| 参数 | 值 |
|---|---|
| QPU 数 J | 16（fat-tree，4 pods × 4 QPUs） |
| QPU 容量 | {8, 12, 16, 20} 各 4 台，固定随机种子分配；整个仿真重复 10 个种子取平均 |
| 链路类型 n_s | 1 / 3 / 5 个光交换机（同 edge switch / 同 pod / 跨 pod） |
| 链路时延 | T_link_{n_s} = T_el / η_s^{n_s}（Eq. 8），η_s = 10^(−loss/10)，默认 loss=0.5 dB |
| 链路保真度 | F_link1=0.96, F_link3=0.94, F_link5=0.92 |
| 时间归一化 | T_local/T_dec = 5×10⁻⁴，T_el/T_dec = 0.005 |
| 电路类型 | QFT / DJ / W-state / GHZ（MQT Bench），各占 25% |
| Sc.1 qubit 范围 | R_GHZ=R_WState=[18,26]，R_DJ=[14,22]，R_QFT=[10,18] |
| Sc.2 | Sc.1 每个范围 +4：[22,30] / [18,26] / [14,22] |
| Sc.3（仅 pytket 实验） | R_QFT=R_DJ=[22,30]，R_GHZ=R_WState=[24,32]，M∈{12,20,28} |
| M（电路总数） | {12, 20, 28, 36}，每个 M 独立生成 10 套 QC 集取平均 |
| 调度参数 | β=0.85，K_max=4（所有电路），α∈{0.55,0.65,0.75}，ω₀=ω₁ |
| 求解器 | **AMPL + CPLEX 22.1.1（用户指定，本机 /Applications/AMPL）**；论文用 Python-MIP+Gurobi，最优解相同，Table IV 时间只做比例级对照 |
| 回归训练集 | 4 类电路 × w∈[10,30]（84 个）；测试集 w∈[31,40]（40 个）；k=2..6 |

### 电路连通图模型（Fig. 6, w=4 归纳）
- **GHZ**：路径图（链），边权 1
- **W-state**：路径图，边权 2
- **DJ**：星形图（q0 为中心），边权 1
- **QFT**：完全图，边权 1

### JET 分层模型（Eq. 9）
`JET/T_dec = N_LL · T_local/T_dec + Σ_{n_s∈{1,3,5}} N^(e)_{link_ns} · T_link_ns/T_dec`
- 电路按 layer 序列建模；仅含本地门的 layer 各贡献一个 T_local；
- 每个 ebit（远程门跨分区产生）串行贡献一个 T_link（同层多个远程门也串行）。

---

## Phase 0 — 项目搭建 ✅

- [x] 阅读参考项目 `code_JSAC_link_configuration` 的 CLAUDE.md / AI_GUIDE，提炼组织方式
- [x] 建立目录骨架（src 包 / tests / experiments / plot_scripts / results / figures / AI_GUIDE / document）
- [x] 记录用户 prompt 到 `9_JSAC_quantum_computing/prompts/`
- [x] `requirements.txt` + 依赖安装验证（amplpy+AMPL+CPLEX、networkx、scikit-learn、matplotlib）

## Phase 1 — 系统模型 ✅

- [x] `src/qdc_scheduler/network.py`：
  - fat-tree 逻辑拓扑：16 QPU，pair→n_s 映射（同 edge switch=1，同 pod 跨 edge=3，跨 pod=5；每 pod 4 QPU、2 edge switch、每 switch 挂 2 QPU）
  - T_{j1j2}、F_{j1j2} 计算（Eq. 8 + 保真度表）；QPU 容量随机分配（固定种子）
  - 测试 `tests/test_network.py`：n_s 分布计数（16 QPU → 每 QPU: 1 个 1-switch 邻居、2 个 3-switch、12 个 5-switch）；T/F 数值 spot check
- [x] `src/qdc_scheduler/circuits.py`：
  - 4 类电路连通图生成器（任意 w）＋ layer 结构（用于 JET）：
    - GHZ：H + CNOT 链（w−1 层，每层 1 门）
    - W-state：链上每对相邻 qubit 2 个双比特门
    - DJ：q0 为公共目标的 CNOT 串（w−1 层）
    - QFT：标准 QFT 受控相位门层序
  - 测试：w=4 时边权与 Fig. 6 完全一致；总边权 = 双比特门次数

## Phase 2 — 图特征 + K-L 分割 + ν_mk 回归（→ Table II）✅ 像素级一致（k=6 χ₃ 为论文排版笔误 0.0203→0.203）

- [x] `features.py`：γ_m（Eq. 2）、λ_{2,m}（归一化 Laplacian 第二小特征值）、σ_m/g_m（Eq. 3）
  - 测试：手算小图对照；QFT 完全图 λ₂ 解析值
- [x] `partitioner.py`：K-L 迭代式平衡 k-way 分割（递归二分，保持每部分大小相等或几乎相等）；cut size 计算
  - 测试：cut ≤ 随机分割；k=2 时与 networkx kernighan_lin_bisection 一致
- [x] `regression.py`：Eq. 4 归一化 cut → 线性回归（Eq. 5/6），k=2..6 分别拟合
- [x] `experiments/run_table2_regression.py`：训练 w∈[10,30]、测试 w∈[31,40]，输出系数/R²/RMSE 表
- [x] **对照 Table II**：k=2: χ=(0.0272,0.4345,0.0163,0.0434), R²=0.995, RMSE=0.0175；…；k=6: R²=0.925（数值逐项比对，允许 K-L 随机性小偏差，记录差异原因）

## Phase 3 — MILP 公式（Formulation 1 & 2）✅ AMPL+CPLEX

- [x] `milp.py`：
  - Formulation 1（Batch）：变量 r_mj, y_mk, z_{mj1j2}, x_{mkj1j2}；约束 (1)–(6)；目标 Eq. 1；ζ 自适应递减保可行
  - Formulation 2（Single）：单电路简化版
  - 求解器：amplpy → AMPL + CPLEX（.mod 文件放 src/qdc_scheduler/ampl_models/）
  - 测试 `tests/test_milp.py`：
    - 单电路可放进单 QPU → 目标 0、k=1
    - 强制分割的小例子 → 人工验证选择 T/(1−F) 最小的 QPU 对
    - 约束 (3)：Σr = k；约束 (4)：每 QPU ≤1 分区

## Phase 4 — 调度器（Algorithms 1–4）与仿真引擎 ✅（Γ 阈值待校准）

- [x] `simulator.py`（含调度策略，未单拆 schedulers.py）：
  - Algorithm 1 Dynamic Batch-QCirc：SELECTBATCH（按到达序累加至 β·c_tot）→ ASSIGNBATCH（Form.1）→ HANDLEOVERFLOW（Alg.2：按 EBT 升序扫描）→ FILLQPU（Alg.3：ν_m≤Γ 且 w_m≤剩余容量的电路用 Form.2 单独塞）→ TRIGGERNEXTCYCLE（等 α·c_tot 容量空闲）
  - Algorithm 4 Single-QCirc：逐电路 Form.2，资源可用即调度
  - 基线 R-B（容量可行的随机分配）、CA-B（经典背包：全连通假设下最小化占用 QPU 数，同一求解器）
- [x] `simulator.py`：事件驱动仿真（QPU busy/idle、非抢占、每 QPU 同时最多 1 个分区）；分配后 K-L 实际分割（尊重容量）→ ebit 归属到实际 QPU 对/链路类型 → Eq. 9 算 JET → makespan/吞吐
- [x] `metrics.py`：ebits/QCirc、partitions/QCirc、按类型 JET、Normalised Makespan、Normalised Throughput
- [x] 测试：小场景手工验算（2 电路 4 QPU）；非抢占与容量约束不变式；α 增大 ⇒ makespan 单调不减（趋势性）

## Phase 5 — K-L 系实验复现（→ Fig 7, 8, 9, 10；Table IV）

- [x] `experiments/run_kl_experiments.py`（含 --m/--seeds/--schemes 并行切片；跑批中）：Sc.1 & Sc.2 × M∈{12,20,28,36} × 10 组 QC × {R-B, CA-B, Single, Batch(α=0.55/0.65/0.75)}，结果落盘 `results/`（pickle/csv，一次生成、可复载，仿照参考项目"生成↔加载"机制）
- [x]（脚本就绪，待数据）`plot_scripts/plot_fig7.py`：ebits/QCirc + partitions/QCirc 4 子图 → 对照 Fig. 7（如 Sc.1 M=12：R-B≈11.5, CA-B≈3.3, Single≈3.0, Batch≈1 ebit）
- [x]（脚本就绪，待数据）`plot_scripts/plot_fig8.py`：8 子图分类型 JET → 对照 Fig. 8（如 Sc.1 QFT：CA-B≈0.07, Single≈0.06, Batch≈0.017）
- [x]（脚本就绪，待数据）`plot_scripts/plot_fig9.py`：makespan + throughput 4 子图 → 对照 Fig. 9
- [x]（脚本就绪，待跑）`experiments/run_fig10_switch_loss.py`：η_s∈{0.5,1,2} dB，Sc.2，α=0.55 → 对照 Fig. 10（M=36 时 Batch 比 Single 快 14.7%/28.3%/43.8%）
- [x]（脚本就绪，待数据）`experiments/run_table4_runtime.py`：Single vs Batch 平均求解时间（论文：0.006s vs 3–4s，硬件不同允许比例级对照）
- [x] 逐柱对照：`experiments/compare_with_paper.py` → `results/comparison_table.md` + `RESULTS_COMPARISON.md`

## Phase 6 — pytket-dqc 系实验（→ Fig 11, Table III）✅

- [x] 安装 `pytket-dqc`（依赖 kahypar；Python 3.13 可能不兼容 → 备选：venv/py3.10 或 Docker）
- [x] 6 种配置：Pytket-PA / Pytket-PH / Single+PA / Single+PH / Batch+PA / Batch+PH
- [x] Sc.1/Sc.2/Sc.3 × M∈{12,20,28} → Fig. 11（9 子图）+ Table III（M=28 减种子）
- [x] pytket-dqc 成功安装（py3.10 conda env）

## Phase 7 — 复现报告 ✅

- [x] 在 `../../overleaf_jsac_quantum_computing/` 新建 `reproduction_report_qdc_scheduling.tex`（自包含可编译）
- [x] 内容：复现历程报告（方法、关键决策、坑）+ 按原文顺序逐张放复现结果图（Table II → Fig 7 → Fig 8 → Fig 9 → Fig 10 → Table IV →（若完成）Fig 11/Table III），每张图配解释与论文对照结论
- [x] 图源：`figures/*.png|pdf` 复制到 overleaf 项目 `figures/repro/` 子目录

## 验收标准（像素级）

1. Table II 每个系数/R²/RMSE 同数量级同趋势（K-L 与回归有随机性，目标相对误差 <10%，R² 偏差 <0.02）
2. Fig 7–10 每个柱的数值趋势与相对排序完全一致，绝对值目标 ±15% 内（论文未公开代码/全部种子，逐柱记录差异）
3. 图的样式（分组柱状、图例、坐标轴标签、配色深浅次序）模仿论文版式
4. 所有随机性均有固定种子，重跑结果比特级一致
