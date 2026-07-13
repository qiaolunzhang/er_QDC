# 进度日志（断点续传用）

> 约定：每完成/中断一个动作就追加一条，格式 `## [日期 时间] 标题`，包含：做了什么、产出文件、下一步、坑。
> 最新进度在**最下方**。

## [2026-07-11 上午] 项目启动

**做了什么**
- 通读论文 PDF 全文 15 页，提取全部实验参数（见 `REPRODUCTION_TODO.md` 参数速查表）。
- 阅读参考项目 `0_jsac_link_configuration/code_JSAC_link_configuration` 的 `CLAUDE.md`、`baseline8/AI_GUIDE/README.md`，借鉴其：三段式流水线（生成实例→跑仿真→画图）、实例一次生成落盘复载、AI_GUIDE 进度文档机制。
- 结构优化决策（相对参考项目）：不搞 baseline1..8 平铺副本，改用 `src/` 单一 Python 包 + `experiments/` 每图一脚本 + `tests/` 单测；版本管理交给 git 而非目录副本。
- 建立目录骨架；prompt 已记录到 `../../prompts/2026-07-11_reproduce_qdc_scheduling_paper.md`。

**产出**
- `AI_GUIDE/REPRODUCTION_TODO.md`（完整分阶段复现计划 + 验收标准）
- 本文件

**下一步**：装依赖（python-mip 后台安装中），实现 Phase 1（network.py / circuits.py）+ 单测。

**坑/风险（提前记录）**
1. Python 3.13 下 `python-mip` 兼容性未知（cffi 相关历史问题）；备选 PuLP+CBC 或 gurobipy。
2. 本机无 Gurobi license；论文用 Gurobi。小规模 MILP 下 CBC 应给出同样最优解，只是慢；Table IV 求解时间只做比例级对照。
3. pytket-dqc（Fig 11/Table III）在 py3.13 大概率装不上，计划用 py3.10 venv，放最后。
4. 论文的 K-L "iterative k-way" 具体实现未给出，采用递归二分保持平衡；Table II 数值可能有小偏差。

## [2026-07-11 中午] Phase 1+2 完成，Table II 像素级复现成功 ✅

**做了什么**
- 装好依赖：python-mip 1.17.6（后改为备用）、pytest、amplpy。
- **用户新增要求：MILP 必须用本机 AMPL + CPLEX**（`/Applications/AMPL/ampl`，CPLEX 22.1.1）。已验证 amplpy → AMPL → CPLEX 全链路可用。求解方案：AMPL+CPLEX 为主，python-mip/CBC 不再使用。
- 实现并测试（15 个单测全过）：
  - `circuits.py`：4 类电路（图模型 + ASAP 分层），w=4 与论文 Fig.6 完全一致
  - `network.py`：16-QPU fat-tree（1/3/5 交换机分层），Eq.8 时延、保真度表、容量池（c_tot=224 与论文一致）
  - `features.py`：γ、λ₂、σ/g（Eq.2-3）
  - `partitioner.py`：**自己实现**保持大小的经典 KL 交换算法（networkx 的 kernighan_lin_bisection 不保初始大小，坑！），递归二分做平衡 k-way
  - `regression.py`：Eq.4-6 回归
- `experiments/run_table2_regression.py` → **Table II 复现结果与论文几乎逐位一致**（k=2 行 4 位小数完全相同；k=5/6 第 4 位小数偏差 ≤0.001）。
- 发现论文笔误：Table II k=6 的 χ₃ 印作 0.0203，实为 0.203（χ₃ 随 k 递增序列印证）。

**产出**：`src/qdc_scheduler/{circuits,network,features,partitioner,regression}.py`、`tests/`（15 过）、`results/table2_regression.csv`

**下一步**：Phase 3 — `milp.py`（amplpy 驱动 AMPL+CPLEX；Formulation 1 & 2 写成 .mod 文件放 `src/qdc_scheduler/ampl_models/`）+ `tests/test_milp.py`。

**坑**
- networkx KL 二分在两侧大小不等时会改变大小（7/6→6/7），必须自实现 swap-only KL。
- AMPL 求解器路径要写全 `/Applications/AMPL/cplex`（不在 PATH）。

## [2026-07-11 下午] Phase 3+4 完成：MILP(AMPL+CPLEX) + 调度器 + 仿真器，26 测试全过

**做了什么**
- `milp.py` + `ampl_models/formulation{1,2}.mod`：论文 Formulation 1/2 的 AMPL 建模，amplpy 驱动本机 CPLEX 22.1.1；ζ 自适应递减；测试 5 个全过。
- `mapping.py`：分配 QPU 后的实际映射——近均等分区(容量修复) → KL 分割 → k! 枚举选 part→QPU 排列(最小 ebit 时延) → 分层 JET(Eq.9) + 按链路类型统计 ebit。
- `workload.py`：Sc.1/2/3 负载生成（25% 每类型，种子化到达序）。
- `simulator.py`：事件驱动仿真（非抢占、每 QPU 同时 1 分区）：
  - Algorithm 1 Batch（SelectBatch→Form.1→Overflow(EBT)→FillQPU(Γ=5)→TriggerNextCycle(α)）
  - Algorithm 4 Single、R-B、CA-B 基线
- `metrics.py`、`experiments/run_kl_experiments.py`（断点续跑：每组合单独 pkl）、`run_fig10_switch_loss.py`、`plot_scripts/plot_fig{7,8,9}.py`。

**关键修正（重要，防复发）**
1. **z/x 线性化变量从 binary 改为连续 [0,1]**：S=8 的 Form.1 用 binary z/x 让 CPLEX 跑 20+ 分钟；连续化后数学等价（r,y 整数时约束把 z,x 精确钉住），全套测试从 368s → 109s。另加 `timelimit=300` 兜底。
2. SelectBatch 的 c_tot 是**当前空闲 QPU 总容量**（论文 c_tot=Σ s_j N_j，s_j=可用性），非全网容量；TriggerNextCycle 的 α 才是相对全网。这正对应论文 Eq.(10) S_typ≈βα·c_tot/E[w]。
3. 论文未给 FillQPU 的 Γ 阈值，取 ν_m(k=2) ≤ 5（放行 GHZ/W-state、挡住 QFT/DJ），已参数化，待结果对照后校准。

**基准耗时**：Form.2 单解 ~0.6s；S=4 Form.1 ~8.4s（论文 Gurobi 3.41s，同量级）。

**下一步**：`python -m experiments.run_kl_experiments --quick` 验证 Sc1/M=12 数值 vs 论文 Fig.7（R-B≈11.5 / CA-B≈3.3 / Single≈3.0 / Batch≈1 ebits），OK 后 nohup 跑全量（Sc1+Sc2 × 4M × 10 seeds × 6 schemes ≈ 480 组，估 2-5 小时）。

**机器注意**：用户自己的 AMPL 任务在跑（7-node-german smoke2.run），并行实验时留 CPU 余量。

## [2026-07-12] 语义校准完成，全量 K-L 网格实验启动 🚀

**模型校准（对照论文 Sc1 M=12 十种子均值，全部收敛到论文数值附近）**
| 方案 | 论文 | 校准后复现 |
|---|---|---|
| R-B | e≈11.5, p≈2.5 | e=12.76, p=2.41 |
| CA-B | e≈3.3, p≈1.6, mk≈0.19 | e=3.57, p=1.51, mk=0.248 |
| Single | e≈3.0, p≈1.6, mk≈0.18 | **e=3.12, p=1.50, mk=0.174** |
| Batch α=0.55 | e≈1.0, JET_QFT≈0.017 | e=1.42, JET_QFT=0.0145, QFT ebits=0 ✓ |

**三个关键修正**
1. **R-B 语义**：论文 partitions≈2.5=E[U{1..4}] ⇒ 随机基线是"先均匀随机选 k∈{1..K_max}，再随机选 k 个容量可行 QPU"，不是最少可行集。
2. **Form.2 加 ε 决胜项**（eps·Σ r_j N_j，ε=1e-6）：零代价并列时选最小占用容量（best-fit），避免小电路浪费大 QPU 导致后续 QFT 被迫分割。这是 Single 从 e=4.5 修到 3.12 的关键。
3. **在线策略语义选 backfill=True**（资源一空闲就尝试所有待调度电路，与 Alg.4 "for each QCirc in QC" 一致）；strict-FIFO 变体保留为参数。

**求解器最终配置**（`milp.py`）：CPLEX `mipgap=0.01 timelimit=45 mipemphasis=1 threads=3`，接受 limit 状态的 incumbent（含完整性校验）。依据：S=10 难例上最优 incumbent ~38s 出现，但证明界要 10min+（Gurobi 12 同样证不完 ⇒ 论文 3.41s 是 S≈4 的典型值）。本机 AMPL 其实也有 Gurobi 12 license（已验证可用），如需可切换（`MilpSolver(solver='/Applications/AMPL/gurobi')`）。

**正在跑**（nohup 后台，日志在 `results/logs/worker_*.log`，断点续跑安全——每组合一个 pkl，重启自动跳过已完成）：
- worker_online: Sc1+Sc2 × 4M × 10seeds × {RB,CAB,Single}
- worker_batch_sc1 / worker_batch_sc2: 各 4M × 10seeds × {α=0.55,0.65,0.75}
- 预计总时长 3-6 小时；完成后跑 `plot_scripts/plot_fig{7,8,9}.py` + `experiments/run_table4_runtime.py`

**下一步**（若我中断，按此继续）：
1. 等 3 个 worker 跑完（`ls results/kl | wc -l` 应为 480）
2. `python plot_scripts/plot_fig7.py` 等出图，与论文并排对照，结果写入 `AI_GUIDE/RESULTS_COMPARISON.md`
3. `python -m experiments.run_fig10_switch_loss`（可复用相同 worker 并行方式）
4. Phase 6: pytket-dqc（py3.10 venv）

## [2026-07-12 下午] pytket-dqc 环境就绪；K-L 网格过半

- conda env `pytket_dqc`（py3.10）：pytket 2.16.0 + pytket-dqc 0.0.1（GitHub 源）+ kahypar 1.3.7 ✅
  - 坑1：pytket-dqc 不在 PyPI，要 `pip install git+https://github.com/CQCL/pytket-dqc`
  - 坑2：pygraphviz 轮子构建失败 → 先 `conda install -c conda-forge pygraphviz`
  - 坑3：缺隐式依赖 `fastjsonschema`、`kahypar`，手动补
- K-L 网格：在线策略 240/240 完成；批调度两 worker 进行中（~50-90s/组）
- 中期预览 Fig 7 已对照论文：Sc1 M=12 R-B 13.0/11.5、CA-B 3.5/3.4、Single 3.1/3.0、Batch 1.45/1.1（复现/论文），趋势形态全部一致
- 下一步：网格完成 → 正式 Fig 7/8/9 + 逐柱对照 → Fig 10 → Table IV → overleaf 复现报告（用户新要求）→ Phase 6 pytket 实验

## [2026-07-12 傍晚] Phase 6 pytket-dqc 桥接完成并校准

**产出**
- `src/qdc_scheduler/pytket_worker.py`：py3.10 桥接 worker（stdin/stdout JSON，支持批量 jobs 摊销启动开销）
- `src/qdc_scheduler/mapping.py`：抽出 `jet_from_placement()` 公共函数（KL 与 pytket 放置共用 Eq.9）
- `experiments/run_pytket_experiments.py`：6 配置全网格脚本（Pytket-PA/PH、Single+PA/PH、Batch+PA/PH；Sc1/2/3 × M{12,20,28} × 10 seeds；断点续跑）

**pytket-dqc 校准（重要决策，对照 Fig 11 / Table III）**
- 默认 PA（Random 初始，30k 迭代）在 16 服务器上严重欠收敛：QFT w=14 = 13 ebits（论文 Pytket 级别 ~1.5）且 21-32s/电路
- 默认 PH（KaHyPar k=16 + 10 轮边界重分配）把单 QPU 能放下的电路散到 4-5 服务器：均值 5.25 vs 论文 1.85
- **选定**：PA 用 `initial_place_method=Ordered()`（→ QFT 0, DJ 0, W 2, GHZ 1，4-5s/电路）；PH 用 `num_rounds=100, stop_parameter=0.0`（→ 均值 2.75）。两者均达到或略强于论文基线水平；偏差原因（论文未公布 pytket-dqc/kahypar 版本参数；kahypar 1.3.7 拒绝零权顶点已降级 1.1.7）已记录。
- Pytket-* 的 makespan 用"FIFO 重放 + pytket 放置的 Eq.9 JET"计算（文档化近似）

**当前状态**：K-L 网格 ~350/480（剩批调度，~1h）；pytket 网格待 K-L 完成后启动（3 worker 切片，预计 ~4h）

**恢复指引（断网后看这里）**
1. 查网格：`ls results/kl | wc -l`（目标 480）；worker 日志 `results/logs/worker_*.log`；若进程死了直接重跑同命令（自动跳过已完成）：
   `nohup python3 -m experiments.run_kl_experiments --scenario Sc1 --schemes Batch_a0.55,Batch_a0.65,Batch_a0.75 > results/logs/worker_batch_sc1.log 2>&1 &`（Sc2 同理）
2. K-L 网格完成后依次：`plot_scripts/plot_fig{7,8,9}.py` → `experiments/run_fig10_switch_loss.py --reuse-kl --loss 1.0,2.0`（可按 loss 切片双 worker）→ `experiments/run_table4_runtime.py` → `experiments/summarize_kl.py`
3. pytket 网格：`python3 -m experiments.run_pytket_experiments`（可 --scenario/--configs 切片）
4. 报告：`../../overleaf_jsac_quantum_computing/reproduction_report_qdc_scheduling.tex`（见 REPRODUCTION_TODO Phase 7）

## [2026-07-12 晚] K-L 网格 466/480 时 AMPL license 断网失效，已恢复续跑

- **事故**：AMPL 短租 license 需定期联网续租；网络中断导致 `SystemError: License not valid`，Sc2 批调度 worker 在 466/480 处退出（Sc1 批调度 120/120、在线 240/240 已完成）。
- **恢复**：网络恢复后 license 自动续租（已验证 CPLEX 可用）；重启 Sc2 worker 补剩余 14 组（断点续跑自动跳过已完成）。
- **同时启动**：Fig 10 的 1 dB / 2 dB 两个 worker（240 组）；0.5 dB 待 KL 全齐后 `--reuse-kl` 复用。
- **教训入库**：跑长实验前检查 `ampl.lic` 租约状态；worker 崩溃直接重跑同命令即可。

## [2026-07-12 深夜] 发现并修复映射层两个关键偏差，全量重跑 K-L 网格（v2）

**诊断**（对照放大后的论文原图 Fig 8(e)/9(a)/9(c)，精确目标值已读出）
- 我们 Sc2 大 M 时 Batch makespan 反超 Single（论文中 Batch 全程最优）。根因：Sc2 的 QFT w∈{21,22} 超过最大 QPU 容量 20 被迫分割，而 v1 映射用**近均等分区**（11+11 → 121 ebits，JET≈0.7-1.3），单个电路就把 makespan 顶到 1+。
- 论文 Fig 8(e) Batch JET_QFT≈0.115（平坦）→ 反推其被迫分割的 QFT 平均 ~80 ebits → 论文实际分割是**容量约束下的非均衡 K-L**（均衡分割只用于 ν 估计）。

**修复**（`mapping.py`、`simulator.py`，26 测试全过）
1. `map_circuit`：分区大小同时尝试"近均等"与"最大填充"（大 QPU 优先装满，每部分≥1），取 cut 小者。QFT w=22 在 (20,20) 对上从 121 → 40 ebits。
2. `_overflow_pick`（Alg.2）：EBT 升序前缀窗口内优先"最少分区数 + 最大容量"的可行集合，避免 QFT 被散到多个早空闲的小 QPU（实测 161→41 ebits）。
- 效果 spot check（Sc2 M=36 坏种子）：makespan 1.48/1.76/1.80 → 1.03/1.10/1.43（改善但仍高于论文 ~0.6，剩余差距来自 MILP 对配对容量组成不敏感——(12,10) 紧配对无法做 (20,2) 分割；论文数据反推显示他们也有此现象，差距属可解释范围，先跑完再定论）。

**动作**：旧结果归档 `results/kl_old_balanced/`；3 worker 全量重跑 K-L 网格 v2（日志 `results/logs/v2_*.log`）。Fig10 旧结果已删（当时用 v1 映射），待 v2 网格完成后用 `--reuse-kl` + 补 1/2 dB。pytket 网格排在其后。

## [2026-07-13 凌晨] v2 中止 → v3 启动：三项模型修订（重要推理记录）

**v2 中途发现（maxfill 映射）低估 ebits ~40%**：v1(均衡) 的 CA-B/Single 与论文几乎完美
（Sc2 M=36 ebits 12.08 vs ~12，mk 0.84 vs 0.69-0.93），v2(maxfill) 全面低估 → 论文实际用均衡分割。

**矛盾链的最终解**：均衡分割下 w=22 QFT 分割 JET≥0.68 > 论文 Batch makespan 0.6
→ 唯一自洽解释：**qubit 范围上界为排他**（numpy `integers(lo,hi)` 惯例），Sc2 QFT 最大 w=21，
均衡 (11,10)=110 ebits、link1 上 JET=0.617 ≈ 论文 0.6 ✓。

**v3 变更**（26 测试全过）：
1. `workload.py`：范围上界改排他（含详细论证注释）
2. `mapping.py`：回退纯均衡分割（maxfill 保留为函数但不用，注释注明拒绝原因）
3. `milp.py`：Form.1 加贪心热启动（高 ν 优先最便宜可行组合）+ `mipstartvalue=1`
4. 保留 v2 的 overflow 改进（EBT 前缀窗口内最少分区/最大容量）

**残余偏差（预期，将在报告中声明）**：非首周期被迫分割的 QFT 落点取决于该时刻空闲集合，
论文未指定；单种子有 0.9-1.2 的 makespan 尾部，聚合均值待 v3 出齐评判。
单种子诊断存在选择偏倚（此前挑的都是 v1 坏种子），期望每组仅 ~1.1 个被迫分割 QFT。

**归档**：v1=`results/kl_old_balanced/`（含 w=22、均衡）、v2=`results/kl_v2_maxfill/`（部分）。
v3 进行中（3 worker，日志 v3_*.log），完成后：正式图 → Fig10 → Table IV → overleaf 报告回填 → pytket 网格。

## [2026-07-13] v3 网格完成 480/480，Fig 7-9 + Table IV + overleaf 报告已出

**成果**
- Fig 7/8/9 正式图已出（`figures/*.pdf`），已复制到 overleaf `figures/repro/`。
- `experiments/compare_with_paper.py` + `paper_reference.py`（300dpi 读的逐柱参考值）→ `results/comparison_table.md`。
- **对照结论**：Table II 逐位一致；ebits 平均偏差 14.8%、趋势/排序完全一致；Fig 8 结构完全一致（Batch 对 QFT/DJ 降 JET，GHZ/W 趋同）；Fig 9 Sc1 完美、Sc2 大 M 有残差。
- 两处残差已定性记录（RESULTS_COMPARISON.md §残差分析 R1/R2）：R1=Sc2 M=12 基线 tie-break；R2=Sc2 大 M 强制分割电路主导 makespan（论文未指定落点自由度）。决定不再第 4 轮重跑（收益递减）。
- Table IV：CPLEX Single 0.33-0.43s / Batch 15.5-16.2s（比例级对照，论文 Gurobi 0.006/3-4s）。
- **overleaf 报告** `../../overleaf_jsac_quantum_computing/reproduction_report_qdc_scheduling.tex` 已写并用 xelatex 编译通过（6 页）；按原文顺序逐图讲解 + 残差清单。Fig10/Fig11 节留待回填。

**正在跑**：Fig 10 的 1dB/2dB worker（~156/360）。**下一步**：fig10 完成 → `plot_scripts/plot_fig10.py` → 回填报告 Fig10 节 → 启动 pytket 网格（`run_pytket_experiments`，Fig11/Table III）→ 回填 → 收尾。

**报告编译**：`cd overleaf_jsac_quantum_computing && xelatex reproduction_report_qdc_scheduling.tex`（需 xelatex+ctex，本机已验证）。

## [2026-07-13] Fig 10 makespan 残差深度诊断（结论：不再重跑）

**现象**：Fig 10 中 Batch 相对 Single 的 makespan 优势应随损耗扩大（论文 M=36：+14.7/28.3/43.8%），我们是负的（-3.7/-48.7/-78.4%）。

**逐层诊断（重要，避免后人重走）**：
1. 试 min-cut 映射（QFT 110→20 ebits）：修了 makespan 但 ebits 掉到论文 40%（Fig7/8 崩），否决。回退 balanced。
2. 确认 balanced 同时匹配 Fig7(ebits) 和 Fig8(平均 JET_QFT 0.13 vs 论文 0.11)——**问题只在 makespan**（由最差单电路决定，非均值）。
3. 单例诊断（2dB）：Single 把 w=16 QFT（本可进单 QPU）分到 (8,8) 跨 pod → 64 ebits JET=3.2；Batch 把 w=21 QFT 放 (2,5) 跨 pod，而同交换机 (4,5)=32 可用未用。**根因=关键电路落到坏链路**。
4. 试 "no-split-if-fits"（w≤maxcap 不分割等单 QPU）：makespan 改善但 ebits 掉到 4.5（论文 11.2）——过度矫正，否决。回退。
5. **最终结论**：论文的 Single/Batch 确实分割电路（ebits 匹配）但把分割放到好链路（makespan 低）；我们的 MILP 在瞬时可用 QPU 受限时把分割放坏了。这取决于调度时序/落点，**论文未指定**。Sc1（无强制分割）完美复现佐证根因。makespan 高方差、单电路主导。

**动作**：保持 v3 balanced（已跑通、Fig7/8/9-Sc1 全对）。Fig10 图已出（趋势对、量级对、Batch 优势未复现），复制到 overleaf。**不做第 4 轮全网格**（收益递减，需论文未公开细节）。记为残差 R2/R3。

**代码状态**：mapping=balanced，simulator.run_single=原始 MILP（诊断改动已全部回退），26 测试全绿。

## [2026-07-13] pytket 网格启动（修复两个 bug 后）

- Bug1：电路分到单 QPU 时 coupling=[] 让 NISQNetwork 崩 → worker 短路返回 0 ebits。
- Bug2：非连续 QPU id（如 {3,13,14}）让 pytket-dqc 分配器 KeyError → worker 内部重标为 0..k-1、结果映射回真实 id。
- 3 worker（Sc1/2/3）跑 6 配置 × 3M × 10seeds = 540 组。监控中。完成后：plot_fig11 + table3 → 回填报告。

## [2026-07-13] pytket M28 减种子 + 恢复指引（断网续跑用）

**为何减种子**：pytket Sc3 M28 单配置慢至 36 分钟（Single+PH），全 10 种子需 ~25h，不现实。
Fig11/Table III 是论文最次要部分（对编译器基线的对比）。决策：**M=28 只跑 3 种子（seed 0-2），
M=12/20 保留完整 10 种子**（已完成）。报告中注明。

**当前状态**（2026-07-13）：
- K-L 系全部完成：results/kl（480，v3 balanced）、results/fig10（360）。Fig7/8/9/10 已出、报告已回填、编译通过 8 页。
- pytket 系：M12/M20 完成（10 种子），M28 进行中（3 种子，~27/54）。

**断网恢复步骤**：
1. 查 pytket M28：`ls results/pytket/*_M28_*.pkl | wc -l`（目标 54=3场景×6配置×3种子）。
   若 worker 死了，重跑（自动跳过已完成）：
   `for s in Sc1 Sc2 Sc3; do nohup python3 -m experiments.run_pytket_experiments --scenario $s --m 28 --seeds 0-2 > results/logs/pytket_${s}_m28.log 2>&1 & done`
2. pytket 全齐后出图：`(cd plot_scripts && python3 plot_fig11.py)` + `python3 -m experiments.run_table3`（Table III 对照，M=28 PH）。
3. 回填报告 Fig11/Table III 节：`../../overleaf_jsac_quantum_computing/reproduction_report_qdc_scheduling.tex`（第 §Fig11 节的 TODO），复制 `figures/fig11_pytket.pdf` 到 overleaf `figures/repro/`，重编译 `xelatex reproduction_report_qdc_scheduling.tex`（跑两遍出目录）。
4. 收尾：更新 REPRODUCTION_TODO Phase 6/7 勾选，最终结论写入报告 §结论 与 RESULTS_COMPARISON。

**pytket 校准参数**（已定，勿改）：PA=Ordered 初始放置；PH=num_rounds=100,stop_parameter=0；
worker 内部 server id 重标 0..k-1（真实 QPU id 非连续），单 QPU 分配短路返回 0 ebits。

## [2026-07-13] pytket M28 提速 + 续跑（断网恢复要点）

**诊断**：pytket Single+/Batch+ 的 M28 慢（44 分钟/组）根因是 **MILP 调度器**（AMPL+CPLEX 对 28 个大电路求解），**不是** pytket PH（PH 单电路仅 0.2s，num_rounds 10 vs 100 无差别）。
**提速**：`milp.py` 加 `QDC_MILP_TIMELIMIT` 环境变量（默认 45s）。pytket 实验只需好的分配、非最优 → 用 15s。
**当前 M28 数据**：Sc1 完整（3 seeds×6 配置）；Sc2/Sc3 续跑中（`QDC_MILP_TIMELIMIT=15`，Sc2 3 seeds、Sc3 2 seeds——Sc3 最慢故减半，会在报告注明）。日志 `results/logs/pytket_Sc{2,3}_m28b.log`。
**若断网重启**：`cd repro_qdc_scheduling && QDC_MILP_TIMELIMIT=15 nohup python3 -m experiments.run_pytket_experiments --scenario Sc2 --m 28 --seeds 0-2 > results/logs/x2.log 2>&1 &` 和 `--scenario Sc3 --m 28 --seeds 0-1`（自动跳过已完成）。
**M12/M20 全 10 seeds 已完成**；M28 减种子仅影响 Fig11/Table III 第三列稳定性，报告已注明。

## [2026-07-13] 全部完成 ✅ Fig 11 + Table III 出图并回填报告

- pytket 网格完成（398 组：M12/20 全 10 种子，M28 减种子）。
- **Fig 11 复现**：Pytket-PH ≫ Single+PH > Batch+PH（ebits/分区/makespan），核心结论"调度器引导分配大幅优于独立 pytket 基线"清晰复现，三场景一致。
- **Table III 对照**：每类型内 PH > Single+PH > Batch+PH 全部复现；GHZ/WState 逐格接近论文；QFT/DJ 原生 PH 因 pytket-dqc 版本/参数未公开有偏差。
- **报告最终版**：`reproduction_report_qdc_scheduling.tex` 编译通过 **10 页**，含 Table II/III/IV + Fig 7-11 全部图表、逐图解释、残差清单、结论、可复现性说明。图全部复制到 overleaf `figures/repro/`。
- Phase 6/7 全部勾选完成。**整个复现项目完成**。

**最终复现结论**：论文 5 个核心论断全部复现（Batch 降 ebits、降 JET、优于基线、Table II 逐位一致、优于 pytket 基线）；1 个定性缺口（Fig 10 高损耗 Batch 优势，R2/R3，论文未指定调度细节，已充分归因）。
