# JointDQC — Joint Circuit Allocation & Entanglement Routing (ILP experiment)

> Sub-project of `repro_qdc_scheduling`. Idea **#4 JointDQC** from
> `er_QDC/ideas/QDC_ILP_ideas_novelty_analysis.md` (rated ★★★★★ ILP cleanliness,
> NOVEL). This folder records **what we did, the results, and takeaways**.
>
> - **Started:** 2026-07-15
> - **Solver:** AMPL (`/home/qiaolun/opt/ampl.linux-intel64`) + CPLEX 22.2.0, driven by amplpy.
> - **Python:** conda env `rwa` (numpy/scipy/networkx/matplotlib/pandas/amplpy installed).
> - **Run from repo root** `repro_qdc_scheduling/` with `PYTHONPATH=src AMPL_DIR=/home/qiaolun/opt/ampl.linux-intel64`.

---

## 0. The gap we attack (why this is novel)

The base paper (Bahrani et al., arXiv:2409.12675, JSAC) schedules **compute** — it
allocates circuits to QPUs and picks a partition count — but **abstracts the network away**:
in `formulation1.mod` the entanglement latency `T[j1,j2]` and fidelity `F[j1,j2]` between two
QPUs are **fixed constants**, i.e. the fabric is assumed to deliver an ebit on demand with no
contention. Reality: every remote gate consumes a **Bell-state measurement (BSM) / entanglement
swap at each optical switch on its path**, and switches have **finite BSM budgets**. When a batch's
allocation piles many cross-pod remote gates onto the shared **core** switches, those switches
serialize → congestion the base objective never sees.

**JointDQC** makes per-switch BSM capacity a *first-class constraint* and **jointly** decides
circuit→QPU allocation **and** ebit routing over the fat-tree fabric, so the optimizer trades a
slightly more expensive placement for a congestion-free one. We report a **certified optimality
gap** (LP / Lagrangian bound) and a **scalable congestion-aware heuristic**.

---

## 1. ILP model to add (`ampl_models/jointdqc.mod`)

Extends Formulation 1. Keep base allocation core; add the fabric layer.

**Given (new):** explicit fat-tree fabric = QPUs J, edge switches `E`, aggregation switches `A`,
core switches `Cr`. Path incidence `inc[σ,j1,j2] ∈ {0,1}` (switch σ on the fixed edge/agg path of
pair j1<j2); `xpod[j1,j2] ∈ {0,1}` (cross-pod → must cross a core switch). Per-switch BSM budget
`Bcap[σ]`; per-core budget `Bcore`, `Ncore` symmetric cores.

**Decide:** base vars `r[m,j]`, `y[m,k]`, `z[m,j1,j2]`, `x[m,k,j1,j2]` (unchanged).

**Ebit load of pair (j1,j2) for circuit m:** `load[m,j1,j2] = Σ_k ν[m,k]·x[m,k,j1,j2]`
(ν_mk = expected cut = # remote gates = # ebits; from the paper's regression, reused verbatim).

**New constraints:**
- Edge/agg BSM capacity: `Σ_{m,j1<j2} inc[σ,j1,j2]·load[m,j1,j2] ≤ Bcap[σ]`  ∀σ∈E∪A.
- Core BSM capacity (symmetric cores, splittable flow): `Σ_{m,j1<j2} xpod[j1,j2]·load[m,j1,j2] ≤ Ncore·Bcore`.
- (optional min-max congestion form: introduce `t`, `Load_σ ≤ t·Bcap[σ]`, minimize `t`.)

**Objective:** same base cost `C = Σ ν_mk·x·(ω0·w·T + ω1·(1−F))` (so NO vs NA is a clean ablation:
only the capacity constraints differ). A congestion-penalized variant `C + ρ·t` is a secondary run.

**Certified gap:** solve MILP → incumbent `C*`; solve LP relaxation (`relax_integrality`) → bound `C_lp`;
`gap = (C* − C_lp)/C*`. (Stretch: Lagrangian dual on the coupling switch constraints → tighter bound +
decomposition proof, idea #4's headline.)

## 2. Heuristic to add (`heuristic.py`)

**Congestion-Aware Greedy (CAG):** process circuits in descending connectivity ν_m(k=2); each circuit
takes the cheapest capacity-feasible QPU combo whose induced ebit load still fits the **residual**
per-switch BSM budgets; update residuals. Scales to 10²–10³ QPUs. Report its gap vs the MILP optimum.
Baseline heuristic = **Network-Oblivious (NO)** = base Formulation 1 (no capacity), then post-hoc route
→ measure the congestion it incurs.

## 3. Experiments

| Exp | Sweep | Schemes | Metric | Output |
|-----|-------|---------|--------|--------|
| E1 Congestion value | batch size Mb ∈ {4,6,8,10,12}, 5 seeds | NO vs NA(MILP) | peak core BSM load, congestion-makespan, base cost | fig_congestion |
| E2 Budget threshold | Bcore ∈ {2,3,4,6,8,∞}, Mb fixed | NO vs NA | served / peak load / feasibility → threshold Bcore* | fig_threshold |
| E3 Topology (routing multiplicity) | Ncore ∈ {1,2,4} | NA | peak load vs Ncore | fig_topology |
| E4 Certified gap & runtime | Mb, J scaled | NA MILP vs LP bound vs CAG | opt-gap %, solve time | table_gap |
| E5 Heuristic quality | all instances | CAG vs MILP | CAG optimality gap | table_heuristic |

**Instance generator:** reuse `workload.generate_qc_set` (Sc2) + `regression.fit_all` for ν_mk +
`network.DQCNetwork` capacities; build a feasible batch that (nearly) fills the 16-QPU fabric, require
all assigned (zeta = Mb). Fixed seeds → bit-reproducible.

## 4. Deliverables
- Code + results + figures in this folder.
- **Overleaf:** `jointdqc_jsac.tex` — a JSAC-standard paper that **pixel-mimics** 2409.12675
  (IEEEtran, same section skeleton II Model / III MILP+heuristic / IV Evaluation), figures in
  `overleaf/figures/jointdqc/`.

---

## Progress log  (append-only; newest at bottom)

- **2026-07-15 setup** — env verified: AMPL 20260520 + CPLEX 22.2.0 + amplpy 0.17 work end-to-end in
  `rwa`. Base MILP solves once the incompatible `mipstartvalue=1` CPLEX option is dropped (CPLEX 22.2
  renamed it). Explored code (12 modules, formulation1/2.mod), overleaf (2 papers; repro report is a
  standalone article), and ideas. Picked idea #4 JointDQC. Created `jointdqc/` scaffolding.

## Results & takeaways  (filled as experiments complete)

### Pivot finding (2026-07-15) — the *right* metric is BSM-aware admission, not "congestion at equal admission"

I first tried to show JointDQC reduces peak core BSM load **at equal admission** (same circuits placed,
compare congestion). **This does NOT hold cleanly in the paper's fabric**, and understanding why is the
key insight:
- The base objective `Σ ν_mk·(w·T + (1−F))` already *penalises cross-pod pairs* (n_s=5 has the highest
  latency T and lowest fidelity F). So the base model **already avoids cross-pod entanglement** whenever
  it can. Probes at zeta=6,7 (Sc1/Sc2, Mb=8) → cross-pod load = 0 for NO, NA **and** CAG: whenever a
  feasible placement exists in this 4-pod × 4-QPU fabric, a congestion-free (intra-pod) one exists and
  every scheme finds it.
- Cross-pod is only *forced* when the QPU slots are near-exhausted — which coincides with
  **over-subscription** (the batch cannot be fully placed). There, the schemes admit *different numbers*
  of circuits, so "peak load at equal admission" is not a clean comparison.

**Conclusion:** the genuine gap the base model leaves is not "route better" but **"it has no notion of BSM
capacity, so its batch selection (by qubit capacity, β·c_tot) over-commits the shared switch fabric."**
The base cost is **separable per circuit**, so it never sees that many circuits' remote gates pile onto
the *same* core switches. → Reframed the contribution as **BSM-aware joint allocation + admission control**
(`jointdqc_admit.mod`: maximise admitted circuits s.t. a hard per-layer BSM budget), evaluated by
**effective throughput = admitted / BSM-serialisation-rounds**.

### E-pilot (Sc2, Mb=12 over-subscribed, N_core=2, B_core=4 ⇒ budget=8 ebits) — DOMINANT, clean
NO = base Formulation 1 (BSM-blind); NA = jointdqc_admit MILP; CAG = BSM-aware greedy.
```
seed0 | NO adm=8 L=12.2 rounds=2 eff=4.0 | NA adm=9 L=3.9 rounds=1 eff=9.0 (7s, optimal) | CAG adm=9 L=5.3 eff=9.0
```
JointDQC **admits more circuits AND floods the core far less** → ~2.25× effective throughput here.
No confound: NA/CAG dominate NO on *both* axes (admission and congestion). (more seeds confirming.)

**Takeaway (superseded by the validity audit below):** the first pilot looked like a huge win, but a
rigorous audit showed part of it was a solver artifact. See below for the honest, defensible result.

### Validity audit (2026-07-15) — why the naive comparison over-claims, and the honest result

I stress-tested the "NO floods the core" claim and found it is **not robust as stated**:
- **The base cost objective is congestion-indifferent.** Same-pod ($n_s{=}3$, $F{=}0.94$) and cross-pod
  ($n_s{=}5$, $F{=}0.92$) links cost almost the same, so Formulation 1 has many equal-cost optima with
  wildly different core \bsm{} load. On the *same* instance, CPLEX returned core load ranging
  **4.4 → 195.7** ebits depending only on the time limit / tie-break (probe: seed 1 gave 9.7/6.6/4.4 at
  10/60/120 s; seed 2 gave 195.7 at 10 s). So "NO floods" is really "the base objective does not
  *control* congestion" — an off-the-shelf solver floods *arbitrarily*.
- **Fair fix → the effect can vanish.** I added a congestion-minimising tie-break to the admission MILP
  and built the strongest *BSM-oblivious* baseline **OBL** (max admission, then min core load, no budget).
  In the paper's fabric (Sc.2, $N_{core}{=}2$), **OBL $=$ JDQC** (both admit 9 at core load $\approx$0):
  when the fat-tree has ample intra-pod capacity, congestion is *avoidable*, so a hard \bsm{} budget adds
  nothing over simply being congestion-aware.

**Where JointDQC genuinely wins — the stressed/constrained regime.** BSM contention only *binds* when
cross-pod placement is *forced*: a dense, high-connectivity workload (QFT/DJ, all must split) on a
core-constrained fabric ($N_{core}{=}1$). There the admission-vs-congestion trade-off is real and only a
BSM-aware scheduler navigates it. Pilot (QFT/DJ pool, $w\in[22,30]$, $N_{core}{=}1$, $B{=}4$):
```
OBL  admits 8 but is FORCED to core load 24.9 -> 7 serial BSM rounds -> eff = 1.14
JDQC admits 7 (drops 1) at core load 0.0      -> 1 round             -> eff = 7.00   (6x)
```
**Honest contribution:** JointDQC identifies and closes the base model's congestion-blindness; its hard
\bsm{} budget gives a *feasibility guarantee* the base model cannot, and this **matters in a
characterisable regime** — dense workloads on under-provisioned cores. The paper reports (i) the base
model's uncontrolled congestion, (ii) the well-provisioned regime where BSM does not bind (OBL$\approx$JDQC,
reported honestly), and (iii) the stressed regime + a threshold (core count / workload connectivity)
where BSM-aware admission is necessary. This is the "actionable threshold" the taste-review asked for.

### Final experiment design (v2)
Schemes: **OBL** (strong BSM-oblivious: max-admission + min-congestion, no budget), **JDQC** (BSM-aware
admission MILP), **CAG** (BSM-aware greedy). Sweeps: workload {mixed Sc.2, dense QFT/DJ}, budget $B_{tot}$,
load $M_b\in\{8,12\}$. Metric: effective throughput = admitted / BSM rounds = admitted / ceil(L/B_tot).
**Note:** $N_{core}$ turned out to be *degenerate* — with even spreading, effective throughput depends
only on the *aggregate* budget $B_{tot}=N_{core}B_{core}$, so we use $B_{tot}$ as the provisioning axis.

### FINAL RESULTS (10 seeds, N_core=1 canonical)  — honest, quantified
Effective-throughput ratio **JDQC / OBL** (OBL = strongest BSM-oblivious baseline; ratio $>1$ = JointDQC
wins). Core load = ebits the oblivious scheduler is forced to leave on the core.

| Workload | $M_b$ | $B{=}4$ | $B{=}8$ | $B{=}16$ | $B{=}32$ | OBL core load |
|----------|------|--------|--------|---------|---------|---------------|
| Mixed    | 8    | **2.97** | 1.80 | 1.50 | 1.11 | 18.2 |
| Dense    | 8    | **2.46** | 2.05 | 1.65 | 1.37 | 29.8 |
| Mixed    | 12   | 1.09 | 1.09 | 1.06 | 1.00 | 2.8 (slack: OBL cherry-picks clean) |
| Dense    | 12   | **2.74** | 1.95 | 1.48 | 1.00 | 18.8 |

> Caveat recorded: a single seed (dense $M_b{=}12$, seed 0) showed a $6\times$ outlier; the
> 10-seed **mean** is $2.74\times$. Headline is "**up to $\sim$3×**" (max $2.97\times$, mixed
> $M_b{=}8$, $B{=}4$), not 6× — averaging matters.

- **CAG heuristic within 5.4% of the MILP optimum** (mean effective-throughput gap, 10 seeds).
- **MILP solve time** a few seconds per 16-QPU instance (dense harder, ~10 s at the time limit).

**Final takeaways:**
1. The base cost objective is **congestion-blind**, not just suboptimal: equal-cost optima span core load
   ~4→200 ebits (probe evidence), so an off-the-shelf base solver congests the core *arbitrarily*.
2. On a **well-provisioned / lightly-loaded** fabric BSM contention **does not bind** — a congestion-aware
   tie-break suffices and JDQC$\approx$OBL (mixed $M_b{=}12$: ratio $\approx$1.0). *Reported honestly.*
3. JointDQC genuinely wins **only in the binding regime** — a (near-)fully-utilised fabric under a tight
   \bsm{} budget — where it trades 1–2 admitted circuits for a congestion-free batch: **up to ~3×**
   effective throughput at $B{=}4$, decaying to 1 as the budget grows (an actionable provisioning
   threshold). This nuance (WHEN it matters) is the paper's contribution, not a blanket "optimise jointly".
4. Deliverables: code in `jointdqc/` (fabric, 3 AMPL models, solver, heuristic, evaluator, runner, plot,
   tests); JSAC-style paper `overleaf/jointdqc_jsac.tex` (pixel-mimics arXiv:2409.12675); figures in
   `overleaf/figures/jointdqc/`.
