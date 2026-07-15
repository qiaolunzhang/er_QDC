# Pixel-Level Mimicry TODO — `jointdqc_jsac.tex` → arXiv:2409.12675 (Bahrani et al., JSAC)

Goal: bring the JointDQC companion paper to the **structure, logic flow, length, and
results density** of the reference paper, section by section. The contribution differs
(BSM contention), but the skeleton, rigor, figure/table count, and per-section length
should mirror the reference "pixel-for-pixel."

Reference anatomy (measured from `er_QDC/papers/2409.12675v5_Quantum_Data_Center.md`):
- ~15 double-column pages, **~11,500 words**, IEEEtran `[journal]`.
- **11 figures, 4 tables, 4 algorithms, 2 formulations, 33 references.**
- Sections: Abstract → I Intro (~1600w, Fig.1 + related work) → II Network Model
  (~1000w, Fig.3 fat-tree, Fig.4 workflow, notation Table I) → III Methods (~3500w,
  Alg.1–4, Formulation 1–2, ν regression) → IV Evaluation (~3500w, Fig.6–11, Table
  II–IV, 5 subsections) → V Conclusion (~450w) → Ack → Refs.

Current paper: ~280 lines, ~4 pages, 4 figures, 1 table, 2 refs. **Too short, too few
results.** Target after this pass: **~11–13 pages, ~9,000–10,000 words, 8–9 figures,
4 tables, 2 formulations, 1–2 algorithm blocks, ~18–22 references.**

Environment: Python `conda run -n rwa`, MILP `AMPL_DIR=/home/qiaolun/opt/ampl.linux-intel64`
+ CPLEX 22.2. All new experiments write to `jointdqc/results/`, all figures to
`jointdqc/figures/` and mirror to `overleaf_quantum_computing/figures/jointdqc/`.

Legend: [ ] todo · [~] in progress · [x] done.

---

## Part A — Section-by-section expansion plan (map ref → ours)

### A0. Abstract + keywords  [ ]
- Ref: ~200 words, dense. Ours already good; polish for parallelism with ref phrasing
  ("Simulation results demonstrate…"). Keep honest two-regime framing. Target ~230w.

### A1. Section I — Introduction  [ ]  (target ~1400w, +Fig.1)
Mirror the ref's 6-move intro:
1. QC/DQC motivation + remote-gate primitive (ref ¶1–2). **Add Fig.1**: remote-CNOT /
   BSM schematic (our `fig_remote_gate`), analogous to ref Fig.1–2.
2. Compute vs communication resources; scheduling vs partitioning (ref ¶3). State that
   the base model treats communication as free — our entry point.
3. Why switch BSM capacity matters: classical vs quantum contention (new ¶).
4. **Related work** (ref has a full column): network resource mgmt & entanglement
   scheduling [Vista, Zhang-SwitchQNet, Pouryousef, Cicconetti]; compilation/partitioning
   [Andres-Martinez, Ferrari, Cuomo]; multi-circuit scheduling [Parekh, Bahrani]. Position
   JointDQC as the first to make switch BSM budget a first-class scheduling constraint.
5. **Contributions** as an itemised list (keep the 3 honest bullets, expand each 1–2 lines).
6. **Paper organisation** paragraph ("The remainder … Sec. II …").

### A2. Section II — QDC Network Model with BSM Contention  [ ]  (target ~1200w, +Fig.2, +Table I)
Mirror ref Sec II:
- Optical-switch fabric, BSM-heralded entanglement, fat-tree. **Add Fig.2**: 4-pod
  fat-tree with edge/agg/core switches and the BSM budget annotated (`fig_fabric`).
- Graph model G(V,E); T_{j1j2}, F_{j1j2}; the on-demand / fixed-parameter assumptions —
  quote them, then state precisely which one we relax (finite BSM throughput).
- Formal path model: n_s ∈ {1,3,5}; T_link, F_link values; capacities {8,12,16,20}.
- **BSM-budget model** (our addition): per-switch budget B_σ, load L_σ, core load
  L_core, serialisation rounds R = ⌈L_core / B_tot⌉. Define effective throughput.
- **Add Table I**: notation table (mirror ref Table I) — reuse ref symbols + our new ones
  (B_σ, L_σ, R, B_tot, N_core, path incidence).

### A3. Section III — JointDQC: BSM-Aware Allocation and Admission  [ ]  (target ~3000w)
Mirror ref Sec III depth (methods is the ref's longest section):
- **III-A Recap of the base batch model** (~500w): variables r_{mj}, y_{mk}, McCormick
  z, x; cost function C (Eq.); ν_{mk} regression (cite our reproduction, reuse ref Table II
  values). Keep short but complete so the paper is self-contained.
- **III-B The base objective is congestion-blind** (~700w, promote to full subsection):
  formal argument (same-pod vs cross-pod cost gap tiny → equal-cost optima with wildly
  different core load); **reference the new empirical Fig.3** (load-spread histogram from
  E-CB experiment). This is the paper's conceptual core — give it room.
- **III-C JointDQC exact MILP** (~800w): full Formulation with objective (max admission,
  ε1 min-congestion, ε2 min-cost) + all constraints, **constraint-by-constraint prose**
  like ref's numbered list (1)–(6) + the two new BSM-budget constraints (7)–(8). Explain
  why max-admission is the operative objective in an over-subscribed cycle.
- **III-D Congestion-Aware Greedy (CAG)** (~500w): present as **Algorithm 1** in an
  `algorithmic` block (mirror ref Alg. style); complexity O(M·C(J,Kmax)).
- **III-E Complexity** (~500w): count JointDQC variables/constraints as fn of M,J,K (mirror
  ref Sec IV-E analysis), compare to base Formulation 1.

### A4. Section IV — Evaluation and Results  [ ]  (target ~3000w)
Mirror ref Sec IV's 5-subsection structure:
- **IV-A Setup** (~600w): 16-QPU 4-pod fat-tree, Kmax=4, capacities, switch loss 0.5 dB,
  T_link/F_link, workloads (mixed Sc.2 / dense QFT-DJ), 10 seeds, AMPL+CPLEX 22.2 10 s.
  Figures of merit: admitted, core load, **effective throughput** = admitted/R. Schemes
  OBL / JDQC / CAG. Define binding (Mb=8) vs slack (Mb=12) regime.
- **IV-B Congestion-blindness, empirically** (~500w, **NEW Fig.3**): the load-spread result
  (one instance, many solver tie-breaks → core load 4→~200 at equal base cost). Table-ise
  min/median/max load. This is the honest backbone.
- **IV-C Two regimes** (~700w, Fig.4 = current regime fig): eff-throughput vs B_tot at
  Mb=8, mixed & dense; OBL collapses, JointDQC sustains; ratios from Table (2.97/2.46 …).
  Honest note: mixed Mb=12 ratio ≈ 1.
- **IV-D Provisioning threshold** (~500w, Fig.5 ratio + Fig.6 coreload): ratio vs Mb;
  the actionable rule.
- **IV-E Switch-loss sensitivity** (~400w, **NEW Fig.7**): sweep η_s ∈ {0.5,1,2} dB (mirror
  ref Fig.10) → show the BSM-aware gain is robust / how congestion interacts with link cost.
- **IV-F Heuristic quality & runtime** (~400w, Fig.8 heuristic + **NEW Table IV** runtime):
  CAG within 5.4% of MILP; per-instance solve time from `solve_time` column; complexity.
- Tables: **Table II** (regression, reuse ref values), **Table III** (ratio summary vs
  B_tot — the current one, extend with admitted & load columns), **Table IV** (MILP runtime).

### A5. Section V — Conclusion  [ ]  (target ~400w)
Expand current: restate three findings + provisioning rule + future work (per-QPU comm-qubit
budgets, column generation for 10^2–10^3 QPUs, heterogeneous decoherence, dynamic links).

### A6. References  [ ]
Expand `thebibliography` from 2 → ~18–22: add [Vista entanglement scheduling], [Zhang
SwitchQNet ISCA'25], [Pouryousef network-aware], [Cicconetti], [Andres-Martinez pytket-dqc],
[Ferrari compiler], [Cuomo], [Parekh greedy], [MQT Bench], [Fiedler algebraic connectivity],
[Knapsack], [Beukers remote-entanglement], [Caleffi survey], etc. Pull from ref's bib.

---

## Part B — New experiments to run (fill the results gap)

### E-CB. Congestion-blindness load spread  [ ]  → `results/congestion_blind.csv`, Fig.3
- Fix one representative instance (dense, Mb=8, seed 0). Solve the **raw base model**
  (min-cost, no congestion tie-break) repeatedly under perturbed solver settings
  (mipgap, seed, emphasis, branching) to sample the equal-cost optimal face; record
  core_load each time. Expect a wide spread (≈4 → ≈200) at ~constant base_cost.
- New script `exp_congestion_blind.py` (reuse `solver.py` / `evaluator.py`). Plot histogram
  + cost-vs-load scatter → `fig_congestion_blind`. Report min/median/max in text + Table.

### E-SL. Switch-loss sensitivity  [ ]  → `results/switchloss.csv`, Fig.7
- Sweep per-switch loss η_s ∈ {0.5, 1, 2} dB → recompute T_link/F_link (η_s^{n_s}), rebuild
  Fabric, rerun OBL/JDQC/CAG at Mb=8, a tight budget (B_tot=8), 10 seeds, both workloads.
- Extend `fabric.py` to accept `switch_loss_db` (default 0.5) and recompute T/F. New
  `run_experiment.py --switchloss 0.5 1 2`. Plot eff-throughput ratio vs η_s → `fig_switchloss`.

### E-RT. Complexity + runtime table  [ ]  → Table IV (from existing `solve_time`)
- Aggregate `solve_time` from `final_*.csv` by scheme × workload × Mb → mean/max seconds.
- Derive JointDQC variable/constraint counts as fn of (M,J,K) analytically for the text.
- Small `summarize_runtime.py` (or extend `plot.py`) → prints/writes the table rows.

### E-BR. Breakdown figures from existing data  [ ]  (no new solves)
- admitted-vs-budget and core-load-vs-budget panels (already in CSV) → optionally fold
  into the regime/coreload figures or an appendix panel. Extend `plot.py`.

---

## Part C — Figures to produce (target 8–9)

| # | Name | Source | Status |
|---|------|--------|--------|
| 1 | `fig_remote_gate` remote-CNOT/BSM schematic | tikz/matplotlib | [ ] |
| 2 | `fig_fabric` 4-pod fat-tree + BSM budget | matplotlib | [ ] |
| 3 | `fig_congestion_blind` load-spread (E-CB) | new | [ ] |
| 4 | `jointdqc_regime` eff-thpt vs budget | exists | [x] |
| 5 | `jointdqc_ratio` ratio vs Mb | exists | [x] |
| 6 | `jointdqc_coreload` forced core load | exists | [x] |
| 7 | `fig_switchloss` sensitivity (E-SL) | new | [ ] |
| 8 | `jointdqc_heuristic` CAG vs MILP | exists | [x] |

Tables: I notation · II regression (reuse) · III ratio summary (extend) · IV runtime (new).

---

## Part D — Execution order (step by step)
1. [x] Analyse ref structure + current gap; write this TODO.
2. [ ] E-CB experiment + Fig.3 (backs the central claim) — highest priority.
3. [ ] E-SL experiment + Fig.7; extend `fabric.py` with switch-loss.
4. [ ] E-RT runtime aggregation → Table IV; complexity counts.
5. [ ] Generate Fig.1 (remote gate) + Fig.2 (fabric) schematics.
6. [ ] Rewrite `jointdqc_jsac.tex` section by section (A1→A6) to target lengths, wiring
   in all figures/tables. Keep IEEEtran, keep honest framing.
7. [ ] Compile-check locally if a LaTeX toolchain exists; else validate structure by hand.
8. [ ] Update this TODO with results/takeaways; update `TODO.md` log; git push both repos.

## Progress log
- 2026-07-15: Mapped reference anatomy (15p/11.5kw/11figs/4tables/33refs). Current paper
  4p/4figs/1table/2refs. Wrote this pixel-mimicry plan. Starting E-CB.
- 2026-07-15 (cont.): Built experiment machinery + rewrote paper:
  - `jointdqc_costface.mod` + `solver.solve_costface/costface_cmin`: rigorous cost-face probe for
    congestion-blindness (min/max core load at exact base optimum). `exp_congestion_blind.py`.
    Note: mixed workload's base optimum is often cross-pod-free (load 0) -> the order-of-magnitude
    spread comes from the DENSE instances (dense Mb=6). Running.
  - `exp_switchloss.py` (reuses Fabric.switch_loss_db): eta_s in {0.5,1,2} dB. DONE-ish. Clear
    effect on mixed: OBL core load 6.8->24.6->21.0 as loss rises (budget 8) -> eff-thpt 8->2->2.7,
    while JDQC/CAG hold at 8. Gain STRENGTHENS with loss (mirrors ref Fig.10). Dense at high loss:
    admission drops, load->0 (honest: effect concentrates on mixed here).
  - `plot_schematics.py` (subagent): Fig.1 remote-gate/BSM, Fig.2 4-pod fat-tree w/ BSM budget. DONE.
  - `plot_extra.py`: fig_congestion_blind (Fig.3), fig_switchloss (Fig.7), runtime aggregation.
  - Runtime (E-RT) from existing data: JDQC mean 6.5s/max 10.4s, OBL 5.2s, CAG 3.9s (Table IV). DONE.
  - Confirmed ratio table (10-seed): mixed Mb8 2.97/1.80/1.50/1.11; mixed Mb12 ~1.0; dense Mb8
    2.46/2.05/1.65/1.37; dense Mb12 2.74/2.00/1.50/1.00. Heuristic gap 5.4%.
  - Rewrote `jointdqc_jsac.tex`: ~2x longer, 8 figures (2 schematic + Fig.3 + 4 existing + Fig.7),
    5 tables (notation, regression, congestion-blind, runtime, ratio-summary), Formulation 1 with
    constraint-by-constraint prose, CAG Algorithm 1 (algpseudocode), full related-work + org, 20 refs.
    LaTeX structure linted (begin/end balanced, refs<->labels OK). No local LaTeX -> compile on Overleaf.
  - TODO: fill Table III (blind) numbers + regenerate Fig.3/Fig.7 once E-CB dense completes; push.
- 2026-07-15 (final): E-CB completed (mixed Mb8 seeds0-4, dense Mb6 seeds0-4). **Honest recalibration
  of the congestion-blindness claim** (important):
  - At a TIGHT tolerance (exact optimum / 1% MIP gap) these full-admission-FEASIBLE instances have a
    nearly unique optimum: dense Mb6 is 0..0 ebits (slack fabric packs same-pod), mixed Mb8 is 1.3..2.0.
  - The base objective's indifference to cross-pod placement shows once a few % cost slack is allowed:
    at 5% tolerance the DENSE core load swings 0 -> 35.4 ebits at ~equal cost; mixed 2.0 -> 3.2.
    => "objective trades 35 ebits of congestion for 5% cost" is the honest, data-backed statement.
  - Dropped the earlier over-claim ("order of magnitude at the EXACT optimum"). Rewrote abstract,
    intro bullet, Sec III-B, Sec IV-B, Fig.3 caption, Table III, conclusion to "within a few percent
    of optimal cost". Table III now reports @1% (near-unique) AND @5% (the swing) side by side.
    Fig.3(b) shows the 5% swing. This is a WEAKER but TRUTHFUL claim; the strong robust results remain
    two-regime (up to 2.97x) + switch-loss (1.8->3.65x) + heuristic 5.4%.
  - E-SL final: mixed ratio 1.80/2.65/3.65 at eta_s=0.5/1/2 dB (monotonic); dense ~2.0-2.3x. Gain
    strengthens with loss (mirrors ref Fig.10). Fig.7 done.
  - Made Formulation 1 a two-column figure* to avoid IEEEtran column overflow. All 8 figures present,
    begin/end balanced, refs<->labels OK. No local LaTeX -> Overleaf compile.
  - STATUS: pixel-mimic pass complete. Paper ~11-12 pages: 8 figures, 5 tables, Formulation 1 +
    Algorithm 1, related work + org, 20 refs. Pushing both repos.

## TAKEAWAYS (pixel-mimic pass)
1. Pixel-mimicry != verbatim copy: matched the reference's section skeleton, per-section length,
   figure/table density, and rigor, adapted to the BSM-contention contribution.
2. Rigor forced an honest downgrade: the cost-face MILP probe showed congestion-blindness is real but
   SUBTLER than the initial solver-tie-break anecdote implied (visible at ~5% cost slack, not at the
   exact optimum on feasible instances). Reported truthfully rather than cherry-picking.
3. Reuse paid off: every new experiment reused Fabric/solver/evaluator/regression; only ~1 new AMPL
   model (costface) + 2 thin experiment scripts + 2 plot modules were added.
4. Parallelism: ran E-CB (dense) + E-SL concurrently on 128 cores; delegated schematic figures to a
   subagent. Cut wall-clock roughly in half.
