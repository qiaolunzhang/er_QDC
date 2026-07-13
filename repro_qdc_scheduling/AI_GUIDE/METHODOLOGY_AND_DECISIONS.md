# 复现方法论与决策全记录（自包含，供任何 AI/人接手）

> 本文档是"思想层"的完整记录：为什么这么做、怎么判断、结论是什么。
> 时间线细节看 `PROGRESS_LOG.md`；逐项待办看 `REPRODUCTION_TODO.md`；数值对照看 `RESULTS_COMPARISON.md` 与 `results/comparison_table.md`。
> 复现对象：arXiv:2409.12675v5（DQC 数据中心电路调度，IEEE JSAC）。

---

## 1. 复现总方法论（可复用于任何论文）

1. **先像素级复现"确定性锚点"再做随机实验**。本项目的锚点是 Table II（回归系数）：
   它不含调度随机性，若能逐位复现则证明底层构件（电路图模型、K-L、特征、回归）全对。
   我们 Table II 达到 4 位小数一致 —— 之后一切偏差都能排除底层构件的嫌疑。
2. **论文没写清的实现细节，用"论文数值反推"来确定**（backward inference）。
   原则：多个图表的数值互相约束，正确的实现必须让所有数值同时自洽。
   本项目三次成功应用（见 §4 判断链 J2/J3/J4）。
3. **基线的退化并列解（tie-break）没有唯一答案**，复现到"趋势与量级一致"即可，
   把差异定位出来并记录，不要无限调参去拟合基线。
4. **每步实验前先做小规模 smoke（1-2 种子），对照锚定值，通过后再跑全量网格**。
   全量网格必须：每组合单独存盘（断点续跑）、显式种子（重跑比特级一致）、后台 + 监控。
5. **发现偏差的处理顺序**：先查自己的 bug → 再查语义理解（论文歧义处列出候选语义、
   分别实现小规模对照选型）→ 最后才归为"论文未指定的自由度"并记录。

## 2. 系统模型：每个非显然决策及依据

| 决策 | 内容 | 依据 |
|---|---|---|
| fat-tree n_s 映射 | 同 edge switch=1、同 pod=3、跨 pod=5；每 pod 4 QPU、2 edge switch | 论文 Fig.3(a) + "1/3/5 switches"；16 QPU 时每 QPU 恰有 1/2/12 个三类邻居 |
| 电路图模型 | GHZ=路径(权1)、W=路径(权2)、DJ=星(权1)、QFT=完全图(权1)，任意 w 归纳 | 论文 Fig.6 (w=4)；被 Table II 逐位一致**证实** |
| 电路 layer | 门序列 ASAP 分层（同层 qubit 不相交） | Eq.9 需要层结构；论文未给，此为标准做法 |
| **qubit 范围上界排他** | `integers(lo, hi)`，如 Sc2 QFT 实际 w∈[14,21] | 判断链 J4（关键！）：w=22 均衡分割 JET≥0.68 与论文 Batch makespan≈0.6 矛盾；排他后 w=21→110 ebits→link1 上 0.617≈0.6 ✓ 全部自洽 |
| 实际分割=均衡 K-L（容量修复） | 分区尽量等大，超容量时溢出到有余量的部分 | 判断链 J3：maxfill 变体使全体 ebits 低于论文 ~40%；均衡版 CA-B/Single ebits 与论文几乎重合（12.08 vs ~12） |
| part→QPU 排列 | k!≤24 全枚举，最小化 Σcut×T_link | 论文未指定；合理且计算可忽略 |
| JET (Eq.9) | 纯本地层各计 1×T_local；远程门每个 ebit 串行计 T_link；含远程门的层不计 T_local | 论文 Eq.9 原文 |

## 3. 算法与求解器：每个非显然决策及依据

| 决策 | 内容 | 依据 |
|---|---|---|
| MILP 求解 | AMPL + CPLEX 22.1.1（amplpy），.mod 文件在 `src/qdc_scheduler/ampl_models/` | 用户指定（论文原文是 Python-MIP+Gurobi；解相同） |
| z/x 连续化 | 线性化辅助变量声明为 [0,1] 连续 | r,y 整数时约束把 z,x 精确钉住 ⇒ 数学等价；binary 版 CPLEX 慢 5-20 倍 |
| CPLEX 选项 | `mipgap=0.01 timelimit=45 mipemphasis=1 threads=3 mipstartvalue=1`，接受 limit 态 incumbent | 该类实例 LP 界极弱：最优 incumbent <45s 出现但证明要 10min+（Gurobi 12 同样）；45s 处 incumbent=最优（实测多配置同值 1.04720） |
| 贪心热启动 | Form.1 求解前按 ν 降序给每电路最便宜可行组合，设 r/y 初值 | 保证 incumbent 起点即结构合理（QFT 优先便宜链路） |
| license 重试 | AMPL 创建失败含 "License" 时每 2min 重试至 1h | 短租 license 断网即失效，两次打断过夜实验 |
| Form.2 ε 决胜项 | `+1e-6·Σ r_j N_j`（best-fit） | 判断链 J1：零代价并列时任意选会浪费大 QPU，Single ebits 从 4.5 偏到论文的 3.0 附近的关键 |
| R-B 语义 | 均匀随机 k∈{1..4}，再随机选容量可行的 k 个 QPU | 论文 R-B partitions≈2.5=E[U{1..4}]，反推出该语义 |
| 在线策略 backfill | 资源一空闲尝试所有 pending（非严格 FIFO） | Algorithm 4 伪代码 "for each QCirc in QC"；实测 backfill=True 匹配（3.12 vs 论文 3.0） |
| SELECTBATCH 的 c_tot | 当前**空闲** QPU 总容量（非全网） | 论文 c_tot=Σs_j N_j（s_j=可用性）；亦是 Eq.10 S_typ≈βα·c_tot/E[w] 的来源 |
| TriggerNextCycle 的 α | 相对**全网**容量 | 论文原文 "fraction of the total qubit capacity across all QPUs" |
| FillQPU 阈值 Γ | ν_m(k=2) ≤ 5（放行 GHZ/W，挡 QFT/DJ） | 论文未给数值；按“防止高连通电路进 FillQPU”的原意设定 |
| Overflow 选择 | EBT 升序前缀窗口内选"最少分区数+最大容量"可行集 | Alg.2 原文允许（"taking into account circuit constraints"）；防 QFT 被散进小 QPU |

## 4. 关键判断链（现象 → 假设 → 验证 → 决策）

**J1（Single 偏高）**：v0 版 Single ebits=4.5 > CA-B=3.6，与论文（3.0 < 3.3）反序
→ 假设：Form.2 零代价并列解浪费大 QPU，迫使后续 QFT 分割
→ 验证：加 ε best-fit 项后 10 种子均值 3.12 ≈ 论文 3.0，反序消失 → 采纳。

**J2（R-B 语义）**：我们的随机基线 parts=1.73，论文≈2.5
→ 洞察：2.5 恰是 U{1,2,3,4} 的期望 → 论文 R-B 先随机选 k
→ 验证：改后 parts=2.41、ebits=12.76 ≈ 论文 2.5/11.5 → 采纳。

**J3（映射用均衡还是最大填充）**：v1（均衡）Sc2 Batch makespan 反超 Single（论文相反）；
v2（maxfill）修好 Batch 却让全体 ebits 掉到论文的 60%
→ 结论：论文用均衡（CA-B/Single 数值重合证实），Batch 的矛盾另有原因 → 回退均衡，继续查。

**J4（范围上界排他，本项目最深的一环）**：均衡分割下 w=22 QFT 的 JET 下限
=121×T_link1=0.68 > 论文 Batch makespan 0.6 —— 任何调度都救不了 ⇒ 矛盾必须出在
"w=22 是否存在"。numpy `integers(lo,hi)` 默认排他 ⇒ 若作者直接用 (lo,hi)，Sc2 QFT
最大 w=21：均衡 (11,10)=110 ebits，link1 JET=0.617≈0.6，同时 JET_QFT≈0.11、
ebits≈12 全对上 → 采纳排他上界。教训：**先算硬下界，若与论文矛盾则实现细节必错**。

**J5（基线 tie-break 不追拟合）**：v3 后 Sc2 M=12 的 CA-B/Single 仍偏低（6.2/8.5 vs
13.5/11.2），但 M≥20 与 Sc1 全部吻合 → 定位为退化最优解 tie-break 的自由度（论文
Gurobi vs 我们 CPLEX/字典序），记录为已知偏差，不再调参。

**J6（pytket-dqc 校准）**：默认 PA 在 16 服务器欠收敛（QFT=13 ebits vs 论文~1.5）、
默认 PH 把单 QPU 电路散到 4-5 服务器
→ PA 用 Ordered 初始放置、PH 用 num_rounds=100 强化精化 → 达到/略强于论文基线
→ 采纳并声明（论文未公布 pytket-dqc/kahypar 版本参数；kahypar 需 1.1.7，1.3.7 拒绝零权顶点）。

## 5. 当前结果状态（v3 网格，2026-07-13）

- **Table II**：逐位一致（k=6 χ₃ 论文排版笔误 0.0203→0.203 已证）。
- **Sc1 全体 + Sc2 R-B/大 M**：ebits/partitions/makespan/JET 与论文逐柱吻合
  （例：Sc1 Single M=12 2.81 vs 2.85；Sc2 CA-B M=36 JET_QFT 0.242 vs 0.24、mk 0.885 vs 0.93）。
- **已知残余偏差**：Sc2 M=12 基线两格偏低（J5）；Batch 尾部个别种子 makespan 偏高
  （非首周期被迫分割 QFT 的链路落点取决于当时空闲集合，论文未指定）。
- Table IV：比例级对照（CPLEX 45s 上限 vs 论文 Gurobi 均值 3-4s；Single 0.33s 含
  AMPL 进程开销 vs 论文 6ms）。
- Fig 10 / pytket 网格（Fig 11、Table III）：待 v3 后运行。

## 6. 工作流速查（低阶 AI 直接照做）

```bash
cd code_er_QDC/repro_qdc_scheduling
python3 -m pytest tests/ -q                     # 26 个测试必须全绿
python3 -m experiments.run_table2_regression    # 锚点：Table II
# 全量网格（3 worker 并行、断点续跑，进度=ls results/kl | wc -l，目标 480）：
nohup python3 -m experiments.run_kl_experiments --schemes RB,CAB,Single > results/logs/o.log 2>&1 &
nohup python3 -m experiments.run_kl_experiments --scenario Sc1 --schemes Batch_a0.55,Batch_a0.65,Batch_a0.75 > results/logs/b1.log 2>&1 &
nohup python3 -m experiments.run_kl_experiments --scenario Sc2 --schemes Batch_a0.55,Batch_a0.65,Batch_a0.75 > results/logs/b2.log 2>&1 &
# 出图与对照：
(cd plot_scripts && python3 plot_fig7.py && python3 plot_fig8.py && python3 plot_fig9.py)
python3 -m experiments.compare_with_paper       # 自动逐柱对照表（论文参考值在 experiments/paper_reference.py）
python3 -m experiments.run_fig10_switch_loss --reuse-kl --loss 1.0,2.0
python3 -m experiments.run_table4_runtime
python3 -m experiments.run_pytket_experiments   # 需 conda env pytket_dqc（py3.10）
```

坑速查：AMPL license 断网失效（已自动重试）；networkx KL 不保分区大小（自实现）；
CPLEX 证明慢是常态（接受 incumbent）；pytket-dqc 装法见 PROGRESS_LOG 2026-07-12。

## 7. 结果归档

- `results/kl/` = **v3 当前有效**；`results/kl_old_balanced/` = v1（含 w=22、均衡映射）；
  `results/kl_v2_maxfill/` = v2 部分（maxfill，已否决）。对照历史勿删。
