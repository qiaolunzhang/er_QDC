# repro_qdc_scheduling 快速指引

复现论文 **arXiv:2409.12675v5**（Bahrani et al., IEEE JSAC）"Resource Management and Circuit Scheduling for Distributed Quantum Computing Interconnect Networks"。

必读文档（按顺序）：

1. `AI_GUIDE/METHODOLOGY_AND_DECISIONS.md` — **思想层全记录**：方法论、每个决策的依据、判断链、结果状态、工作流速查（接手必读）。
2. `AI_GUIDE/REPRODUCTION_TODO.md` — 分阶段复现计划、论文参数速查表、验收标准。
3. `AI_GUIDE/PROGRESS_LOG.md` — 带时间戳的进度日志，**断网重连后先看最后一条**。
4. `AI_GUIDE/RESULTS_COMPARISON.md` — 复现结果 vs 论文原图/表的逐项数值对照（Phase 5 起生成）。

## 目录结构

```
src/qdc_scheduler/   核心包：network / circuits / features / partitioner /
                     regression / milp / schedulers / simulator / metrics
experiments/         每个图/表一个实验脚本（run_table2_*.py, run_kl_*.py, ...），结果写 results/
plot_scripts/        每个图一个画图脚本（读 results/，出 pdf 到 figures/）
tests/               pytest 单测，实现一个模块配一个测试
results/             实验原始结果（pickle/csv，一次生成可复载，勿手改）
figures/             输出图；figures/comparison/ 放与论文并排对照
document/            设计笔记 / 论文公式推导记录
```

## 流水线（借鉴 code_JSAC_link_configuration 的三段式）

```
① experiments/ 生成实例并跑仿真（固定种子，结果落盘 results/）
② plot_scripts/ 读 results/ 画图
③ 对照论文原图，差异记入 AI_GUIDE/RESULTS_COMPARISON.md
```

## 要点速记

- 运行任何脚本前 `cd` 到本目录根：`python -m experiments.run_xxx`（包内相对导入 + 相对路径 `results/`）。
- 依赖：`pip install -r requirements.txt`；MILP 求解器优先 Gurobi、缺省 CBC（python-mip）。
- 测试：`python -m pytest tests/ -q`。
- 所有随机性走显式 seed（网络容量 seed、QC 集 seed），保证重跑比特级一致。
