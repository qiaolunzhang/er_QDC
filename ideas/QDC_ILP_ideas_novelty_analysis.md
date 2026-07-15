# Distributed Quantum Computing in a Data Center: Six Ideas with Clean ILP Formulations

Each idea below is stated as a solvable (mixed-)integer program, followed by the closest prior work,
the precise gap it leaves, and a residual-novelty verdict (**NOVEL / INCREMENTAL / AT-RISK**) with its
most-threatening reference. Citations `[n]` are resolved in **References**; a summary table and
recommendation close the note.

**Shared enabler.** End-to-end fidelity is multiplicative in the per-link Werner parameter
(`w_φ = Π_e w_e`), hence *additive in log-space* (`log w_φ = Σ_e log w_e`), so a fidelity floor becomes
one linear constraint `Σ_e log w_e ≥ log w^req`. With Chernoff linearization of the chance constraints,
this is what renders all six problems ILP-tractable.

---

## 1. #4 JointDQC — Joint Circuit Allocation and Entanglement Routing (MILP + decomposition)

### ILP formulation
- **Given:** a QDC fabric graph (Clos/fat-tree) with per-switch Bell-state-measurement (BSM) and
  port capacities and per-QPU communication-qubit budgets; a batch of partitioned circuits with
  remote-gate (ebit) demands.
- **Decide:** circuit-to-QPU-subset allocation `r_mj` and partition count `y_mk` (as in the base
  model), and a multi-commodity ebit flow `x` routing each remote-gate demand over the fabric.
- **Subject to:** flow conservation; per-switch BSM/port capacity; per-QPU comm-qubit budget; the
  coupling that a partition's cut induces its remote-gate demand — all linear.
- **Objective:** maximize served circuits per unit time (or minimize makespan) — linear.
- **Linearization / solve:** a standard capacitated multi-commodity-flow + assignment MILP whose
  block structure (one block per circuit, coupled only through shared switch capacity) admits
  **Dantzig-Wolfe column generation / Lagrangian decomposition**; the master LP relaxation yields a
  **certified optimality-gap** bound. Exact at J≤16; scalable to 10²–10³ QPUs via pricing.
  **ILP cleanliness: highest.**

### Related work and gap
A first line of work schedules *compute* for distributed quantum computing while abstracting the
network away: *Bahrani et al.* [1] formulate a batch MILP that allocates circuits to QPUs, but assume
the network reliably provides entanglement on demand and evaluate only at 16 QPUs. A complementary
line of work routes or schedules *entanglement* for a pre-partitioned circuit while ignoring
multi-tenant compute allocation: *the ESDI framework* [13] and *network-aware remote-gate scheduling*
[14] optimize entanglement distribution over a fixed demand. A third line applies learning to the
compilation, e.g. *the reinforcement-learning DQC compiler* [15], which produces a fast schedule but
no optimality guarantee. However, these studies mainly focus on either compute allocation with a free
network or entanglement routing for a fixed partition, which differs significantly from jointly
optimizing allocation and routing over a capacity-limited shared fabric with a provable optimality
gap. Note that the closest joint attempt, *network-operations scheduling* [5], decouples placement
from scheduling only as unbounded sequential steps.

### Contributions
To the best of our knowledge, this is the first work to jointly optimize compute allocation and
entanglement routing for a quantum data center with a certified optimality gap. We formulate the joint
problem as a single MILP that makes per-switch BSM and communication-qubit contention first-class; we
prove the block structure that admits a Dantzig-Wolfe / Lagrangian decomposition; and we provide a
scalable solver whose LP relaxation reports the gap to the joint optimum across 16–1024 QPUs. We
thereby close the two gaps the base model [1] states — scalability and the network-free abstraction.

### Verdict
**NOVEL claim / INCREMENTAL machinery.** The decomposition machinery is reused, so the load-bearing
novelty is the joint model with a certified gap, not the solver. Most-threatening: [5]. Sharpening:
lead with the certified gap and the network-contention coupling that [5] lacks.

---

## 2. D2 — Success-Probability-/Fidelity-Constrained Scheduling via Robust-Dual MILP

### ILP formulation
- **Given:** circuits with per-tenant output-fidelity SLAs `Pr[F_m ≥ F_m^req] ≥ 1−δ_m`; per-link
  Werner parameters and heralded-success statistics; QPU/partition resources.
- **Decide:** allocation `r_mj, y_mk` and per-link purification rounds `p_ml`.
- **Subject to:** the SLA chance constraint, linearized as a **per-circuit log-fidelity budget**
  `Σ_e log w_e(p) ≥ −log θ_m` (Werner log-linearity); a Chernoff/Bernstein upper-tail bound turns the
  probabilistic constraint into a linear inner approximation; the robust-over-uncertainty constraint
  is **collapsed via LP/Lagrangian duality into a single constraint**.
- **Objective:** minimize total ebits/time — linear.
- **Linearization / solve:** every constraint reduces to linear form; solves directly in a commercial
  MILP solver, with a scenario-based (sample-average) MILP as the small-instance optimality anchor.
  **ILP cleanliness: highest** — "plug-and-play" once the log/Chernoff transforms are applied.

### Related work and gap
A first line of work minimizes a *proxy* cost for distributed quantum computing: *Bahrani et al.* [1]
minimize a weighted sum of decoherence impact and entanglement infidelity, but never constrains the
executed circuit's end-to-end output fidelity. A complementary line of work guarantees fidelity at the
*entanglement-path* layer: *Jia and Chen* [3] route source–destination flows under a fidelity floor
with log-fidelity additivity and an NP-hardness-plus-`ε` result, and *Q-PATH/Q-LEAP* [4] provide
fidelity-guaranteed routing per flow. However, these studies mainly focus on a proxy objective or a
single-flow entanglement path, which differs significantly from a per-circuit output-fidelity *chance
constraint* embedded in the scheduling MILP with residual-only purification.

### Contributions
To the best of our knowledge, this is the first work to embed a per-circuit output-fidelity chance
constraint in a distributed-quantum-computing scheduler. We formulate output fidelity as a chance
constraint and linearize it into a log-fidelity budget, so a cost-optimal schedule can no longer
silently violate an application's fidelity requirement; we collapse the robust chance constraint into
a single MILP constraint by duality; and we budget purification only on the residual links that
breach the floor. We provide a divergence counterexample where the proxy-optimal schedule of [1]
violates the SLA while the SLA-optimal one costs marginally more.

### Verdict
**NOVEL claim / INCREMENTAL machinery.** The log-fidelity/hardness machinery is [3]'s; the delta is
the circuit-level SLA coupling and the robust-dual collapse in a scheduler. Most-threatening: [3].
Sharpening: foreground the output-fidelity SLA reframe (the base model never constrains output
fidelity); cite [3] only for the additivity trick.

---

## 3. H2 — StructFid: Output Fidelity by Construction via a Balanced-Cut ILP

### ILP formulation
- **Given:** a circuit interaction graph; per-rack-pair Werner parameters; a fidelity floor `F_req`.
- **Decide:** a partition of the circuit onto racks (binary node-to-rack assignment).
- **Subject to:** rack capacity; a `−log`-Werner-weight budget per remote-gate path — linear.
- **Objective:** minimize the **max** `−log w` cut-weight over rack-pairs (a min-max balanced cut),
  so the worst remote-gate path already meets `F_req` by the cut's structure; `(1+ε)` purification
  only on the irreducible residual.
- **Linearization / solve:** min-max is standard — introduce one bound variable `t` with linear
  constraints. This is a fidelity-weighted balanced graph-partitioning ILP (NP-hard); tree-DAG /
  single-partition instances have an exact polynomial special case. **ILP cleanliness: high.**

### Related work and gap
A first line of work partitions distributed-quantum-computing circuits to **minimize the cut count**
as a proxy for entanglement cost: *pytket-dqc* [8], *METIS-based partitioners* [6], and *Hungarian
Qubit Assignment* [7]. A complementary line adds *static* per-link or per-CNOT error into a weighted
cut: *fidelity-driven hypergraph partitioning* [9] and noise-aware cross-layer mappers. However, these
studies mainly focus on minimizing a (possibly error-weighted) cut and then bolting purification on
afterward, which differs significantly from partitioning so that the output-fidelity guarantee holds
by the cut's algebraic structure, with purification as a measured residual.

### Contributions
We formulate circuit partitioning as a min-max balanced `−log`-Werner-weight cut, so end-to-end
fidelity `≥ F_req` is guaranteed by construction rather than recovered by an expensive purification
add-on. We prove NP-hardness of the balanced-cut objective and carve an exact polynomial tree-DAG
case, and we provide a `(1+ε)` residual-purification certificate on the over-budget edges only.

### Verdict
**NOVEL, but near-duplicate of the frontier idea (G1).** The novelty is constructing a feasible cut
inside the admissibility frontier rather than characterizing the frontier. Most-threatening: [9].
Sharpening: own the balanced fidelity-debt objective and the by-construction guarantee; concede
static error-weighting to [9].

---

## 4. #14 — Purification-Budgeted Scheduling (knapsack-style MILP)

### ILP formulation
- **Given:** circuits with per-circuit success SLAs `θ_m`; per-link base fidelity; distillation yield.
- **Decide:** allocation + **integer** purification rounds `p_ml` per link per circuit.
- **Subject to:** a per-circuit log-fidelity budget `Σ log-infidelity ≤ −log θ_m`; each round consumes
  extra ebits under an `n:1` distillation yield — a linear/knapsack coupling.
- **Objective:** minimize total ebits/makespan — linear.
- **Linearization / solve:** budgeted assignment with integer rounds ⇒ a knapsack-type MILP; small
  instances anchored by exact ILP, large by a marginal-fidelity-per-ebit greedy. **ILP cleanliness:
  high** — the lightest of the six to code.

### Related work and gap
A first line of work optimizes *link-level* distillable entanglement: *the optimal
distribution-and-purification algorithms over fusion trees* [12] choose purification to meet a
link-level fidelity target. A complementary line schedules distributed circuits with a proxy
infidelity term, *Bahrani et al.* [1], but distills nothing. However, these studies mainly focus on
link-level distillation or a soft infidelity proxy, which differs significantly from coupling
circuit-level allocation to a hard per-circuit success SLA with tiered, residual-only purification
budgeting.

### Contributions
We formulate a per-circuit success-probability SLA as a log-fidelity budget and co-budget integer
purification rounds inside the allocation MILP; we purify only the residual links that breach the
floor (reuse before redundancy); and we characterize when purification pays off versus simply
selecting higher-fidelity links.

### Verdict
**NOVEL claim, machinery INCREMENTAL.** Closest to link-level distillation work [12]; the delta is the
SLA-coupled tiered budgeting. Highest-leverage fix: prove the greedy is submodular ⇒ `(1−1/e)`,
turning "a heuristic" into a principled bound. Most-threatening: [12].

---

## 5. I2 — TenantThreat: Isolation-Aware Multi-Tenant Placement (interference MIP)

### ILP formulation
- **Given:** tenant circuits with per-tenant fidelity SLAs; a measured co-tenant crosstalk model.
- **Decide:** binary tenant-to-rack placement.
- **Subject to:** an effective per-rack quality `p_eff,r = p_e − Σ_{co-located t} γ_t` folded (via
  log) into a **per-tenant fidelity SLA linear constraint**; the "co-located" coupling is an
  **interference bin-packing** term, linearized with pairwise indicator variables and big-M.
- **Objective:** maximize admitted tenants — linear.
- **Linearization / solve:** an interference-aware bin-packing / assignment MIP; the crosstalk
  coupling is the only term needing big-M. **ILP cleanliness: high (with big-M caveat).**

### Related work and gap
A first line of work treats per-link entanglement success and fidelity as **fixed hardware
constants**: *Bahrani et al.* [1] and *the Cisco QDC blueprint* [2] assume a single class of link
quality. A complementary line studies multi-tenant quantum-network contention at the routing layer:
*network-aware remote-gate scheduling* [14] models BSM contention but only under an idealized
unlimited-resource profile. However, these studies mainly focus on single-class, tenant-independent
fidelity, which differs significantly from modeling entanglement quality as degraded by co-located
tenants and meeting a fidelity SLA by isolation-aware placement rather than by purification. Note that
only a few works consider quantum-data-center multi-tenancy at all, and none couples tenant crosstalk
to a fidelity SLA.

### Contributions
To the best of our knowledge, this is the first work to model entanglement success/fidelity as
tenant-degraded (`p_eff = p_e − Σ tenant-crosstalk`) and to meet a per-tenant fidelity SLA by
isolation-aware placement. We formulate isolation-aware placement as an interference-bin-packing MIP,
prove NP-hardness, and provide the maximum co-tenants-per-rack that still holds the SLA.

### Verdict
**NOVEL.** No distributed-quantum-computing scheduler models tenant-degraded entanglement quality.
Most-threatening: the multi-tenant contention/routing line (of which [14] is the closest in corpus).
Sharpening: tie the crosstalk parameter `γ_t` to measured superconducting/ion values so the model is
not speculative.

---

## 6. J2 — SteinerEnt: GHZ Distribution as a Node-Weighted Steiner-Tree ILP

### ILP formulation
- **Given:** a rack graph; per-rack-pair Werner parameters; comm-qubit/BSM node costs; a set of racks
  needing a shared `k`-party GHZ state.
- **Decide:** a degree-constrained tree connecting the `k` terminal racks through fusion-repeater
  internal nodes.
- **Subject to:** classic Steiner-tree connectivity (cut-set or single-commodity-flow linearization);
  edge weight `−log w` (fidelity), node weight = BSM/comm-qubit cost; degree constraints.
- **Objective:** minimize total (edge + node) weight — linear.
- **Linearization / solve:** node-weighted Steiner-tree ILP is textbook (flow-based or cut-based
  formulation); an `O(log k)` spider/greedy gives a bounded heuristic. **ILP cleanliness: high.**

### Related work and gap
A first line of work models remote gates as **pairwise EPR + teleportation** and decomposes
multi-party gates into pairwise links: *Bahrani et al.* [1], *the Cisco blueprint* [2], and *the
remote-gate protocol-mixing study* [10]. A complementary line already casts *GHZ distribution* as a
Steiner-tree/fusion problem in a general quantum network: *multipath GHZ via Steiner trees* [11] and
*optimal distribution over fusion trees* [12]. However, the pairwise line differs significantly from
native multipartite distribution, while the Steiner line differs by being set in a generic network
without rack-level comm-qubit/BSM node weights, degree limits, or schedule-time decoherence.

### Contributions
We formulate GHZ distribution for multi-controlled / distributed-QEC remote gates as a
degree-constrained, node-weighted Steiner tree over the QDC rack fabric, with `−log`-Werner edge
weights and BSM/comm-qubit node weights, and we provide a fuse-versus-pairwise `k*` threshold.

### Verdict
**AT-RISK (INCREMENTAL-leaning).** The GHZ-Steiner recast itself is pre-owned by [11], [12]; the
residual is the rack-resource-constrained setting. Most-threatening: [12]. ILP-solvability is
excellent even though the idea's novelty is thin — good as a low-risk formulation exercise, weaker as
a headline contribution.

---

## Summary

| # | Idea | ILP type | ILP cleanliness | Novelty verdict | Most-threatening |
|---|------|----------|:---:|-----------------|------------------|
| 1 | **#4 JointDQC** | multi-commodity flow + assignment MILP (+ column generation) | ★★★★★ | NOVEL claim / reused machinery | [5] |
| 2 | **D2 FidelitySLA-Dual** | chance-constrained MILP (robust-dual) | ★★★★★ | NOVEL claim / reused machinery | [3] |
| 3 | **H2 StructFidDQC** | balanced-cut partitioning ILP | ★★★★ | NOVEL, near-dup of G1 | [9] |
| 4 | **#14 Purification-SLA** | knapsack-style budgeted MILP | ★★★★ | NOVEL / needs (1−1/e) proof | [12] |
| 5 | **I2 TenantThreatDQC** | interference bin-packing MIP | ★★★★ | NOVEL | [14] |
| 6 | **J2 SteinerEntDQC** | node-weighted Steiner-tree ILP | ★★★★ | AT-RISK / INCREMENTAL | [11], [12] |

**Reading of the table.** The two cleanest *and* most novel ILP ideas are **#4 (JointDQC)** and
**D2 (FidelitySLA-Dual)**: both are load-bearing MILPs, both close a gap the base papers [1], [2]
state, and both linearize cleanly (multi-commodity flow; log-fidelity + Chernoff). **H2** and **#14**
are strong, lighter formulations on the fidelity axis but sit close to prior partitioning [9] and
distillation [12] work. **I2** is the freshest decision-type (tenant-degraded quality) with a clean
MIP but a big-M coupling. **J2** is the easiest ILP to write yet the weakest on novelty, because the
Steiner recast is already owned by [11], [12]. This is because ILP-solvability and novelty are largely
independent axes: the transform that makes an idea ILP-tractable (Werner log-linearity) is shared, so
it confers no novelty by itself — the novelty must come from the *reframe* (joint model,
output-fidelity SLA, tenant degradation), not the formulation.

*Recommendation.* Pursue **#4** and **D2** as the flagship ILP contributions (use #4's column
generation to report a certified gap; use D2's divergence counterexample to motivate the SLA). Keep
**H2**/**#14** as fidelity-axis companions and **I2** as the multi-tenant extension; treat **J2** as a
low-risk formulation exercise, not a headline.

---

## References

Provenance tag: `[corpus]` = present locally in `qdc_literature/`; `[web]` = external, verified online.

- **[1]** S. Bahrani, R. D. Oliveira, J. M. Parra-Ullauri, R. Wang, D. Simeonidou, "Resource Management and Circuit Scheduling for Distributed Quantum Computing Interconnect Networks," *IEEE J. Sel. Areas Commun.*, 2025. arXiv:2409.12675. `[corpus — the JSAC base paper]`
- **[2]** H. Shapourian, E. Kaur, T. Sewell, J. Zhao, M. Kilzer, R. Kompella, R. Nejabati (Cisco Quantum Labs), "Quantum Data Center Infrastructures: A Scalable Architectural Design Perspective," 2025. arXiv:2501.05598. `[corpus]`
- **[3]** H. Jia, J. Chen, "From Entanglement Purification Scheduling to Fidelity-constrained Multi-Flow Routing," *IEEE ICNP*, 2024. arXiv:2408.08243. `[corpus — the single most dangerous prior work for the fidelity ideas]`
- **[4]** Q-PATH / Q-LEAP: "Fidelity-Guaranteed Entanglement Routing in Quantum Networks." arXiv:2111.07764. `[corpus]`
- **[5]** "Network Operations Scheduling for Distributed Quantum Computing," 2025. arXiv:2511.13687. `[corpus]`
- **[6]** METIS-based distributed-quantum-circuit partitioning (gate partitioning + SeQUeNCe evaluation). arXiv:2310.03942. `[corpus]`
- **[7]** "Hungarian Qubit Assignment (HQA) for distributed quantum computing." arXiv:2403.17205. `[corpus]`
- **[8]** pytket-dqc: distributed-circuit compilation, Quantinuum, *IOP Quantum Sci. Technol.*, 2024. `[web]`
- **[9]** "A fidelity-driven approach to quantum circuit partitioning via weighted hypergraphs." arXiv:2506.06867. `[web]`
- **[10]** DQC-QR / remote-gate protocol mixing (telegate vs teledata vs cat-entangler). arXiv:2405.07499. `[corpus]`
- **[11]** "Multipartite (GHZ) entanglement distribution via Steiner trees in quantum networks." arXiv:2303.03334. `[corpus]`
- **[12]** "Optimal entanglement distribution and purification over fusion trees." arXiv:2503.14712. `[corpus]`
- **[13]** ESDI: "Entanglement Scheduling and Distribution in the Quantum Internet." arXiv:2303.17540. `[corpus]`
- **[14]** "Network-Aware Scheduling for Remote Gate Execution in Quantum Data Centers." arXiv:2504.20176. `[corpus]`
- **[15]** Reinforcement-learning compiler for distributed quantum computing. arXiv:2404.17077. `[corpus]`
- **[16]** Traffic characterization for distributed quantum computing (CCR / hotspotness / burstiness). arXiv:2310.01921. `[corpus]`

> Note: titles/authors for a few corpus entries ([4], [6], [7], [12]–[16]) are given descriptively;
> verify exact author lists against the arXiv IDs before use in a submission. [8], [9] are external to
> the local corpus (found via web search) — download and confirm before citing.
