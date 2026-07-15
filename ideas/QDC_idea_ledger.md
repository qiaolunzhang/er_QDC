# QDC — Idea Ledger (permanent; never delete)

> **Purpose:** record EVERY generated idea across all cycles so no potentially-good idea is lost
> when it falls out of the rolling best-3. The best 3 live in `QDC_best3_ideas.md`; this ledger is
> the full memory. **Standing rule:** each cycle, APPEND its 3 new ideas here (and update statuses);
> never remove an entry. Full detail for the 16 cycle-1 candidates is in
> `qdc_literature/_candidates.json`; detail for the rolling best-3 is in `QDC_best3_ideas.md`.
>
> **Status legend:** ★current = in the current best-3 · runner-up = strong, just outside · displaced =
> was best-3, replaced · archived = scored but not selected (still potentially useful) · near-dup =
> excluded as a near-duplicate of a higher entry.
> **Last updated:** cycle 5 (2026-06-29).

## Current best 3 (cycle 11, 2026-06-29)
**I1 AnalyticBlockDQC (85.5)** · **J1 CrossLayerFidDQC (85.0)** · **K1 CongestFreeDQC (84.0)**.
*(Re-scored fresh under ChunmingQiao v8 + QDN-transport deep-dive. E1→top runner-up (crossover published by Cisco 2601.01353); new K1 ★current, K2/K3 runner-up. Each best-3 carries a prior-art positioning in `QDC_best3_ideas.md` cycle 11.)*

## Master table (best combined score seen, both rubrics)
| ID | Title | Decision-type | Best score | Status | Cycle | Source-of-detail |
|----|-------|---------------|-----------:|--------|------:|-------------------|
| I1 | AnalyticBlockDQC | analytical-performance-model/dimensioning | **85.5** | ★current #1 | 9 | QDC_best3_ideas.md |
| J1 | CrossLayerFidDQC | cross-layer placement co-design | 85.0 | ★current | 10 | QDC_best3_ideas.md |
| K1 | CongestFreeDQC | transport/distributed flow-control | **84.0** | ★current | 11 | QDC_best3_ideas.md |
| E1 | SwapVsBuy | provisioning/routing (server-centric) | 85.5 | top runner-up | 5 | QDC_best3_ideas.md |
| K3 | IterDQC | iterative-workload control-knob | **83.0** | runner-up | 11 | QDC_best3_ideas.md |
| G1 | FrontierDQC | admission/feasibility-frontier | 85.0 | runner-up | 7 | QDC_best3_ideas.md |
| J2 | SteinerEntDQC | multipartite/GHZ routing | **83.5** | runner-up | 10 | QDC_best3_ideas.md |
| H1 | DecoupleDQC | architecture/timescale-decoupling | 84.5 | runner-up | 8 | QDC_best3_ideas.md |
| H2 | StructFidDQC | compiler/property-by-construction | 84.0 | runner-up | 8 | QDC_best3_ideas.md |
| F1 | DeferredDQC | scheduling (deferred/recourse) | 84.5 | runner-up | 6 | QDC_best3_ideas.md |
| G3 | BypassWorthDQC | provisioning (memory lever) | 83.5 | runner-up | 7 | QDC_best3_ideas.md |
| I2 | TenantThreatDQC | multi-tenant isolation/threat-aware | **83.0** | runner-up | 9 | QDC_best3_ideas.md |
| H3 | ProtoMixDQC | protocol-selection/taxonomy | 82.5 | runner-up | 8 | QDC_best3_ideas.md |
| I3 | ExhaustEstDQC | online inference/self-tuning | **81.5** | runner-up | 9 | QDC_best3_ideas.md |
| J3 | VoidFillDQC | online memory-slot scheduling (geometry) | **81.0** | runner-up | 10 | QDC_best3_ideas.md |
| K2 | QSSReliableDQC | resilience/reliability coding | **82.0** | runner-up | 11 | QDC_best3_ideas.md |
| D2 | FidelitySLA-Dual | scheduling (fidelity SLA) | 83.5 | runner-up | 4 | QDC_best3_ideas.md |
| F2 | OneKnobDQC | provisioning (interpolating-knob) | 83.0 | runner-up | 6 | QDC_best3_ideas.md |
| E2 | TwoTimescaleSched | scheduling (scale/decomp) | 83.0 | runner-up | 5 | QDC_best3_ideas.md |
| G2 | SurrogateGapDQC | surrogate-robust scheduling | **82.5** | runner-up | 7 | QDC_best3_ideas.md |
| #7 | Decomposed-and-Bounded (CG + Lagrangian yardstick + GNN oracle) | scheduling (scale+bound) | 85.0 | runner-up | 1 | _candidates.json |
| #4 | JointDQC (Lagrangian/CG joint alloc+routing) | scheduling (joint) | 84.0 | runner-up | 1 | _candidates.json |
| N1 | CutoffFlip | provisioning (memory) | 82.0 | runner-up | 2 | QDC_best3_ideas.md |
| F3 | MinStateDQC | scheduling (min-state coherence) | 81.5 | runner-up | 6 | QDC_best3_ideas.md |
| D1 | FairCompletionFlip | multi-tenant fairness | 81.5 | runner-up | 4 | QDC_best3_ideas.md |
| E3 | MinMonitorState | scheduling (coherence) | 80.5 | archived (⊂ F3) | 5 | QDC_best3_ideas.md |
| C3 | RepeaterCarve | routing (server-centric) | 81.0 | runner-up | 3 | QDC_best3_ideas.md |
| N2 | ε-Local-DQC | admission (fidelity definition) | 81.0 | runner-up | 2 | QDC_best3_ideas.md(c2) |
| D3 | BufferThreshold | provisioning (inter-rack buffer) | 79.5 | near-dup (of N1) | 4 | QDC_best3_ideas.md |
| C1 | SwitchFlip | scheduling (switch reconfig) | 79.0 | displaced | 3 | QDC_best3_ideas.md |
| #14 | Success-Prob-Constrained + Tiered Purification | scheduling (success SLA) | 82.0 | runner-up | 1 | _candidates.json |
| C2 | TrafficShape | admission (partition floor) | 78.5 | archived | 3 | QDC_best3_ideas.md(c3) |
| N3 | BSM-Mechanism (truthful BSM/ebit allocation) | mechanism/allocation | 75.5 | archived | 2 | (below) |
| N4 | GeoQDC (geometry/tight-constant reconfig packing) | scheduling (switch) | 75.5 | archived (⊂ C1) | 2 | (below) |
| #1c | SC-Route (server-centric approx bounds) | routing (server-centric) | 75.0 | archived (⊂ C3) | 1 | _candidates.json |
| #11 | CostQDC (CAPEX/OpEx dimensioning + bypass memory) | design-time economics | 75.0 | displaced | 1 | _candidates.json |
| #13 | BSM-Contention-Aware Co-Scheduling | scheduling (BSM contention) | 74.5 | archived (⊂ #7/#4) | 1 | _candidates.json |
| #8 | Look-Ahead Switch Reconfiguration | scheduling (switch) | 72.5 | archived (⊂ C1) | 1 | _candidates.json |
| #6 | To-Buffer-or-Not (CAPEX perishable-inventory) | provisioning (buffer) | 72.5 | archived (⊂ N1/D3) | 1 | _candidates.json |
| #10 | SurviveDQC (correlated-drift shared backup) | resilience | 71.5 | archived | 1 | _candidates.json |
| #15 | Killing-the-Static-Alpha-Knob (online batch trigger) | scheduling (trigger) | 71.5 | archived | 1 | _candidates.json |
| N5 | RelocateThePartitioner (cut-surrogate is the bottleneck) | scheduling (surrogate) | 71.0 | archived | 2 | (below) |
| #2 | RedundEnt (submodular BSM redundancy) | provisioning (redundancy) | 70.5 | archived | 1 | _candidates.json |
| #5 | Chance-Constrained DQC (retry budget) | scheduling (stochastic) | 70.5 | archived (⊂ D2) | 1 | _candidates.json |
| #12 | LocateQDC (passive multi-fault localization) | monitoring/diagnosis | 68.0 | archived | 1 | _candidates.json |
| #9 | GroomQDC (coherence-bounded entanglement grooming) | scheduling (grooming) | 67.5 | archived | 1 | _candidates.json |
| #16 | Generate-or-Buffer (memory-aware pre-distribution) | provisioning (buffer) | 65.5 | archived (⊂ N1) | 1 | _candidates.json |
| #3 | FreshEbit (AoI buffer provisioning) | provisioning (buffer) | 65.0 | archived (⊂ N1) | 1 | _candidates.json |

## Recoverable descriptions for ideas NOT in _candidates.json or current best-3
*(the cycle-2/3/4 new ideas; one-liners + core novelty so they can be revived)*
- **N2 ε-Local-DQC** — definitional novelty: replace the strict per-remote-gate fidelity floor with a weaker **circuit-level error budget** (Σ(1−F_eff) ≤ B_m); provably admits more circuits, collapses per-gate coupling into one knapsack constraint (Werner log-linearity); greedy (1−1/e). *Orthogonal to all winners; foldable into D2/#14.*
- **N3 BSM-Mechanism** — mechanism design: truthful multi-tenant BSM/ebit allocation where selfish circuit bids = makespan-optimal; impossibility-then-retreat (prove no strongly-dominant equilibrium, recover under stated assumptions). *Overlaps BSM-contention theme.*
- **N4 GeoQDC** — geometry/tight-constant: pack remote-gate ebit demands into k switch configs; crush the reconfiguration-count approximation constant via Clos/BCube topology geometry. *Subsumed by C1 SwitchFlip.*
- **N5 RelocateThePartitioner** — relocate-the-bottleneck: argue the binding constraint is the partition-cut surrogate error (not the solver); tight regret bound on schedule loss vs surrogate error. *Weakest reframe; overlaps #7.*
- **C1 SwitchFlip** — make optical-switch **reconfiguration count** the first-class objective; cover demand multigraph by fewest matchings under dwell ≤ cutoff (NP-hard, Vizing bracket Δ≤K*≤Δ+1); auxiliary config-transition graph; "add-a-config iff toggle+settling cost < hop-loss of reuse". *Displaced cycle 4; revive via closed-form K* for Clos.*
- **C2 TrafficShape** — provable inter-core ebit **lower bound from traffic-characterization metrics** (hotspotness → min-cut packing); coin (c,K)-locality-admissibility; bake as a conservative floor auditing Bahrani's learned ν_mk surrogate; (1−1/e) greedy. *Attacks 2310.01921's "metrics untied to optimization" gap.*
- **C3 RepeaterCarve** — complexity placement + tractable carve for **server-centric (repeater-chain)** QDC: NP-hard via multi-commodity flow with multiplicative Werner attenuation; exact-poly Dijkstra on `−ln` weights for linear/2D-grid bounded-degree fabrics; (1+ε)-purification otherwise. *Top runner-up; revive once validated on a server-centric simulator + maturity retired.*
- **D1 FairCompletionFlip** — reframe multi-tenant scheduling to **per-tenant slowdown** s_m=JCT/JET_solo; min max/p95 slowdown; dual-price admission weights, 2-competitive on identical QPUs; fairness is also a fidelity lever (starved qubit dephases). *Current best-3.*
- **D2 FidelitySLA-Dual** — chance-constrained **output-fidelity SLA** per tenant; Werner log-linearity + Chernoff tail → MILP; robust chance constraint collapsed via LP/Lagrangian duality; NP-hard pinned + exact-poly carve (single-partition/tree-DAG) + (1+ε)-purification; "purify iff density > ρ*". *Current best-3 #1; supersedes #14.*
- **D3 BufferThreshold** — perishable-queue (M/G/1 with TTL=cutoff) buy/don't-buy **buffer-depth** rule for the inter-rack port; closed-form B*=0 iff λ_demand·T_c<1; ranked against switch/EPS levers. *Excluded as near-dup of N1; distinct model (perishable queue vs DAG-slack) — keep for inter-rack-specific work.*

- **E1 SwapVsBuy** *(cycle 5, ★current #1)* — cost-effectiveness puncture for server-centric QDC: prove the inter-rack repeater swap-chain buys ≤ε over a cheap optical-bypass segment unless hop-count k>k*; closed-form "use repeater iff k>k*, else bypass; don't buy relay comm-qubits below k*". NP-hard placement, exact-poly Dijkstra carve on bounded-degree fabrics, (1+ε)-purification residual. Distinct from C3 (which *routes* the swap chain) and N1 (memory lever).
- **E2 TwoTimescaleSched** *(cycle 5, ★current)* — decouple slow offline rack-assignment (MILP/CG over demand heatmaps) from fast online EPR-batch scheduling (background-duality extended Dijkstra); regret bound online-loss ≤ ρ·surrogate-error; KS-test sets re-trigger period — kills Bahrani's static-α knob and Θ(S·K·J²) ceiling. Differs from #7 (GNN oracle) by a provable slow/fast separation with a bound.
- **E3 MinMonitorState** *(cycle 5, archived)* — prove a per-rack max-age envelope (O(racks) state, age=max-of-parents) suffices to upper-bound idle-qubit dephasing; reschedule iff envelope > A*; coin "coherence-budget admissibility" (Σ idle-exposure ≤ B_m) admitting more circuits via one knapsack; infer idle-age from the schedule, not hardware. Revive once envelope-sufficiency is robust to heterogeneous T_dec.

- **F1 DeferredDQC** *(cycle 6, ★current #1)* — two-stage recourse scheduler: offline provisions redundant candidate ebit paths (Chernoff-sized so ≥1 survives), online commits each remote gate only AFTER the per-slot herald is observed → residual collapses to an optimal bipartite matching under per-switch BSM capacity. SAA stochastic MILP yardstick (J≤12); closes Bahrani's static-link gap + Pouryousef's undesigned reactive regeneration via a defer-the-decision reframe.
- **F2 OneKnobDQC** *(cycle 6, ★current)* — expose the pre-distribution fraction φ∈[0,1] as one interpolating knob (φ=0 on-demand, φ=1 full pre-distribution); prove makespan+decay cost J(φ) quasi-convex and solve φ* in closed form (= f(T_mem, gen latency, CoV, ν_mk)); optimal memory budget falls out. Unifies the binary buffer ideas (N1/D3/#16) under a single-knob reframe with a derived threshold.
- **F3 MinStateDQC** *(cycle 6, runner-up; subsumes E3)* — prove a one-scalar-per-rack max-age envelope is a sufficient statistic to upper-bound idle-qubit dephasing, cutting reschedule state O(J·qubits)→O(racks), reschedule only on breach > A*; coin "coherence-budget admissibility" (one knapsack). Adds the sufficiency proof + empirical NP-hard-carve timing that archived E3 lacked. Closes Cisco's coherence-aware-scheduling open problem.

- **G1 FrontierDQC** *(cycle 7, ★current)* — prove the necessary+sufficient condition for ANY DQC schedule to meet output fidelity F_req: admissible iff remote-gate cut-weight (in −log Werner-w units) ≤ closed-form B(mem,comm-qubits,p_e,T_dec); characterize the whole admissible class and show pytket-dqc/METIS/HQA are degenerate corners; exact tree-DAG carve + (1+ε) purification certificate. Feasibility-frontier reframe closing Bahrani open #7 (no end-to-end fidelity constraint).
- **G2 SurrogateGapDQC** *(cycle 7, runner-up)* — distinguish eval-hardness from opt-hardness: the cut-cost is #P/NP-hard to EVALUATE but schedule-opt over a bounded-error surrogate ν̂ is poly with loss ≤ L·‖δ‖ (L from MILP duals); derive surrogate-RMSE threshold ε* below which the schedule is within ρ of OPT, plus a closed-form min-cut floor auditing the learned ν_mk. Closes Bahrani open #8 (surrogate estimation-error impact unquantified).
- **G3 BypassWorthDQC** *(cycle 7, top runner-up)* — cost-effectiveness puncture on the memory lever: model the memory-buffered inter-rack port as perishable-inventory M/G/1(TTL=T_mem) and prove buffered rate/fidelity gain ≤ε over cheap on-demand unless λ_demand·T_mem > closed-form (λ·T_mem)*=f(p_e,gen-latency,ν); default memoryless below it, ranked against switch/EPS levers. Excluded from best-3 as the SAME move as E1 (no-near-dup); revive if E1 dropped. Closes Cisco gap #3.

- **H1 DecoupleDQC** *(cycle 8, ★current)* — decouple the slow placement/partition control plane from the fast entanglement-routing/BSM data plane via a per-rack-pair demand-commitment interface PROVEN a sufficient statistic, so a herald failure is a data-plane table edit not a control-plane recompile; slow MILP/CG offline + fast background-duality Dijkstra online, with a measured regret bound vs monolithic joint MILP. Closes Bahrani #4 / Cisco #4. Threat: ax_2511.13687 (decouples but unbounded/sequential, no sufficiency proof).
- **H2 StructFidDQC** *(cycle 8, top runner-up)* — partition for a min-max balanced −log-Werner-w cut so end-to-end output fidelity ≥ F_req holds BY CONSTRUCTION, with (1+ε) purification only on irreducible residual edges (reuse-before-redundancy); NP-hard balanced-cut + tree-DAG exact-poly carve. Closes Bahrani #7 / 2310.03942. Excluded from best-3 as near-dup of G1's fidelity territory (G1 characterizes the frontier; H2 constructs a cut inside it) — revive if G1 dropped.
- **H3 ProtoMixDQC** *(cycle 8, runner-up)* — factor remote gates into {telegate,teledata,cat-entangler}×{on-demand,buffered}=6 schemes, one ebit-cost+decoherence MILP spanning all 6, prove the per-fragment optimum is a threshold partition of the (CZ-ratio, T_dec/gen-latency) plane (ρ*, (λT_dec)*); collapses 6^#fragments to independent per-fragment thresholds. Closes Bahrani 2405.07499's per-circuit protocol-mixing question.

- **I1 AnalyticBlockDQC** *(cycle 9, ★current #1)* — recast QDC remote-gate contention as a multiservice loss network with coherence/cutoff `T_dec` as holding time; solve the reduced-load (Erlang/Kelly) fixed point for per-rack-pair blocking `B(λ,T_dec,comm-qubits,p_e,switch)`, prove existence + coherence-corrected insensitivity bound, invert to a closed-form comm-qubit dimensioning rule. First analytical (non-sim) blocking model for a QDC fabric. Threat: ax_2405.18066 (single-switch Erlang loss) — survives on network-wide + perishable + dimensioning delta.
- **I2 TenantThreatDQC** *(cycle 9, runner-up)* — model entanglement success/fidelity as DEGRADED by co-located tenants (`p_eff = p_e − Σ tenant-crosstalk`, transplanting SAG-VMP `A′=A−Σ risk`); meet a per-tenant fidelity SLA by isolation-aware two-timescale placement (interference bin-packing NP-hard) rather than purification; yields a max-co-tenants-per-rack threshold. Closes Cisco open #8 (multi-tenant).
- **I3 ExhaustEstDQC** *(cycle 9, runner-up)* — estimate the per-rack-pair stochastic model `(p_e, Werner w, contention)` from heralding/BSM logs the QDC already emits (mine-the-data-exhaust / infer-don't-instrument), via an interpretable estimator fed as a conservative lower bound to a self-tuning (KS-test re-trigger) scheduler; no new metrology. Closes the static-known-link gap.

- **J1 CrossLayerFidDQC** *(cycle 10, ★current)* — reframe DQC placement around an end-to-end cross-layer metric (link-Werner-w × swap-depth × contention-queueing-decoherence `exp(−t_queue/T_dec)`, t_queue from a loss-network term) and PROVE the min-cut / fidelity-weighted-cut placement is dominated by a contention-balanced one when contention-decoherence dominates, with a closed-form crossover; rack-placement topology = the contention control knob. ILP yardstick + topology-as-knob heuristic; reversal validated on a stochastic net sim. Threat: ax_2506.06867 (static fidelity-weighted hypergraph partitioning) — survives on the contention layer + reversal regime.
- **J2 SteinerEntDQC** *(cycle 10, runner-up)* — recast GHZ distribution for multi-controlled/QEC remote gates as a degree-constrained node-weighted Steiner tree (terminals=racks, node-weight=BSM/comm-qubit, edge=−log Werner-w), O(log k) spider-greedy, fuse-vs-pairwise k* threshold. AT-RISK: GHZ-Steiner recast pre-exists (ax_2303.03334, ax_2503.14712); residual delta is the QDC rack-resource-constrained setting.
- **J3 VoidFillDQC** *(cycle 10, runner-up)* — map each perishable comm-qubit coherence-void (start, deadline=gen+T_dec) to a 2-D point so per-slot remote-gate ebit reservation = a geometric range query in O(log m), matching the offline interval-packing optimum's blocking; turns Bahrani's Θ(S·K·J²) per-slot scheduling into a cheap online hot-path. NOVEL but primarily a deployable speedup (low on the right-metric axis).

- **K1 CongestFreeDQC** *(cycle 11, ★current)* — distributed window/congestion control for the QDC fabric where "congestion"=quantum-memory contention at switches under cutoff `T_dec`; TCP-style SS→CA window with intermediate-node congestion-encounter halving; derive a fabric-specific congestion-free invariant + fairness window `W*=f(C,N,T_dec)`, window coupled to the remote-gate DAG. Transplants Qiao's own QDN transport (Tele-DTP/AQTP) into the intra-QDC Clos/BCube fabric; gap to centralized ILP <1%. AT-RISK: own-AQTP transplant + crowded quantum-congestion-control lane → survives on the compute-DAG-coupled + fabric-specific angle.
- **K2 QSSReliableDQC** *(cycle 11, runner-up)* — (k,n) quantum-secret-sharing/erasure coding over n parallel rack-pair paths so a remote gate succeeds if any k of n ebits survive decoherence (no regeneration, forced by no-cloning); tiered to code only residual high-risk gates; closed-form (n,k) for a per-gate success SLA. AT-RISK: QSS-reliability primitive owned by Qiao's TAG-DTP/AQTP + ax_1903.10685.
- **K3 IterDQC** *(cycle 11, runner-up)* — re-partitioning frequency `f*` for distributed iterative/variational DQC (VQE/QAOA, which re-execute a drifting parameterized circuit for hundreds of rounds) from a U-shaped convergence-vs-decoherence cost C(f); decouples slow re-partition from fast per-round scheduling. First DQC scheduler for iterative (not one-shot) workloads — genuinely uncontested class; strongest revival candidate.

## Notes
- "⊂ X" = thematically subsumed by idea X (kept here in case the subsumer is later dropped).
- A displaced/archived idea can re-enter any future cycle's pool if its highest-leverage fix is applied (e.g., #14 if its (1−1/e) submodularity proof lands; C3 once server-centric maturity is retired).
