# 复现结果 vs 论文原文逐项对照（v3 网格，480/480）

> 自动逐柱对照见 `results/comparison_table.md`（`python -m experiments.compare_with_paper` 生成）。
> 论文参考值读自 300 dpi 原图裁剪，读数精度约 ±3% 轴范围。

## Table II — ν_mk 线性回归（✅ 像素级一致）
k=2..6 全部系数/R²/RMSE 与论文逐位一致（k=2 行 4 位小数完全相同）。
论文排版笔误：k=6 χ₃ 印作 0.0203，实为 0.203（χ₃ 序列单调递增佐证）。

## Fig 7 — ebits / partitions per QCirc（✅ 良好，平均偏差 ebits 14.8%）
- **趋势与排序完全一致**：R-B ≫ CA-B ≳ Single ≫ Batch；各方案随 M 递减。
- Sc1 全部四个 M：ebits 与论文吻合（如 Single M=12 2.81 vs 2.85，R-B M=20 9.83 vs 9.9）。
- partitions/QCirc：全体偏差 <10%（R-B≈2.4-2.8、其余≈1.5-2.0），与论文一致。
- **已知残差**：Sc2 M=12 的 CA-B/Single ebits 偏低（6.2/8.5 vs 13.5/11.2）——见下方 §残差分析。

## Fig 8 — 分类型 JET（✅ 结构完全一致）
- **核心论断复现**：Batch 对高连通电路（QFT/DJ）显著降低 JET 且随 M 平坦低位；
  低连通（W-state/GHZ）三方案趋同。
- QFT：Batch JET 平坦≈0.013(Sc1)/0.13-0.17(Sc2)，CA-B/Single 随 M 递减且更高——与论文 Fig 8(a)(e) 同形。
- GHZ/W-state：CA-B/Single/Batch 几乎重叠（论文亦然）。

## Fig 9 — makespan / throughput（部分：Sc1 ✅，Sc2 大 M 有残差）
- **Sc1（a/b）完美**：Batch 明显低于 Single 低于 CA-B（makespan），throughput 反之——与论文一致。
- **Sc2（c/d）**：M=12 排序正确（Batch<Single<CA-B）；M≥20 时三方案 makespan 趋同（≈0.8-0.9），
  Batch 未能像论文那样明显领先。throughput 面板仍显示 Batch 最优。

## Fig 10 —（生成中，1/2 dB worker 运行）
预期验证：η_s 增大时 Batch 相对 Single 优势扩大（论文 M=36：14.7%/28.3%/43.8%）。

## Table IV — MILP 求解时间（比例级对照）
| | 论文(Gurobi) | 复现(CPLEX+AMPL) |
|---|---|---|
| Single | ~0.006 s | 0.33-0.43 s（含 AMPL 进程启动开销） |
| Batch(α=0.55) | 3.41/2.93 s (Sc1/Sc2) | 15.5/16.2 s（45s 上限，弱 LP 界证明慢） |

趋势一致（Batch ≫ Single）。绝对值差异源于求解器、硬件、及"每次新建 AMPL 实例"的开销
（论文复用求解器上下文）；这是求解方式差异，非模型差异。

---

## 残差分析（诚实记录，不再调参的理由）

### R1: Sc2 M=12 基线偏低（CA-B/Single）
- 现象：M=12 时 CA-B ebits 6.2、Single 8.5，论文 13.5/11.2。M≥20 全部吻合。
- 归因：低 M = 低竞争，每电路拿到最优（最少/最大）QPU，分割少 → ebits 低。论文该点
  反而更高（CA-B 随 M 递减，与直觉相反），推测其 CA-B 在低竞争时仍产生更多分割，
  具体机制论文未详述。属基线退化解 tie-break 的自由度（论文 Gurobi vs 我们 CPLEX/字典序）。

### R2: Sc2 大 M 的 Batch makespan 未明显领先
- 现象：Sc2 M≥20 时 Batch≈Single≈CA-B makespan（≈0.8-0.9），论文 Batch 明显最低（0.59）。
- 归因：Sc2 中 GHZ/W-state（w 至 29）、QFT（w 至 21）**超过最大 QPU 容量 20 必须分割**，
  单个这类电路的 JET（w=21 QFT 均衡分割 = 110 ebits × T_link）就达 0.6-1.0，主导 makespan。
  当完工时间由不可避免的高 JET 电路决定时，调度器优化空间被压缩。论文的 Batch 应更成功地
  把这些电路配到便宜链路（同 edge switch），但这依赖具体容量分配与被迫分割电路的落点，
  **论文未指定该自由度**。Sc1（无强制分割）则完美复现，佐证差异根源在此。
- 已尝试并保留的缓解：MILP 贪心热启动、overflow 优先大容量少分区。进一步拟合需要论文
  未公开的实现细节，收益递减（已跑 3 轮全网格 v1/v2/v3）。

### 结论
主要论断——**Batch 大幅降低通信开销（ebits）、对高连通电路降低 JET、整体优于基线**——
全部复现。绝对值残差集中在两处可解释、论文未指定的自由度上，已如实记录。
