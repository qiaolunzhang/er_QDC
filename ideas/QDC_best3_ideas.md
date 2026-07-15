# QDC — Best 3 Research Ideas (auto-maintained)

> **Per-round procedure (standing).** Each cycle: read latest BOTH KBs (ChunmingQiao SKILL.md+
> KNOWLEDGE.md ; QiaolunResearch SKILL.md+knowledge_base/*) + DQC background (`qdc_literature/`) →
> recommend **3 new ideas** + a cited DQC gap → **append to `QDC_idea_ledger.md`** → pool with current
> best 3 → **RE-SCORE ALL 6 POOLED FRESH (no carried scores)** → select best 3 (distinct types, no
> near-dups) → **for EACH best-3 a PRIOR-ART POSITIONING (cited SOTA → delta → NOVEL/INCREMENTAL/AT-RISK
> + most-threatening paper)** → rewrite this file + ledger + leaderboards.
>
> - **Cycle:** 11  ·  **Date:** 2026-06-29
> - **Skills/KBs:** QiaolunResearch `cbb4756e` + KB(4) · **ChunmingQiao v8 `d7f0c4ba`** (final build + QDN transport deep-dive) + KNOWLEDGE.md
> - **Prior best 3 (cycle 10):** I1 AnalyticBlockDQC, E1 SwapVsBuy, J1 CrossLayerFidDQC.

## Top 3 (this cycle, all freshly re-scored)
1. **I1 — AnalyticBlockDQC** (combined **85.5** · A85/B86, *stays #1*): first **analytical (non-sim) blocking model** for a QDC fabric — multiservice loss network with coherence/cutoff `T_dec` as holding time; reduced-load fixed point → inverted closed-form comm-qubit **dimensioning rule**.
2. **J1 — CrossLayerFidDQC** (combined **85.0** · A83/B87, *stays, #3→#2*): **cross-layer placement reversal** — binding fidelity loss is network-contention-induced schedule-time decoherence, not the cut; prove the (fidelity-weighted) min-cut placement is dominated by a contention-balanced one + closed-form crossover; rack topology = contention knob.
3. **K1 — CongestFreeDQC** (combined **84.0** · A83/B85, *NEW*): **distributed, compute-DAG-coupled congestion-free transport** for the QDC fabric — model "congestion" as quantum-memory contention at switches under cutoff `T_dec`; TCP-style SS→CA window with intermediate-node congestion-encounter halving; derive the **fabric-specific congestion-free invariant** + a **fairness window `W*=f(C,N,T_dec)`**, with the window coupled to the remote-gate DAG (admit only entanglement whose consuming gate is schedulable before cutoff). Gap to centralized ILP (<1%, his transport-paper template).

**Runners-up:** E1 SwapVsBuy (83.5, top runner-up — crossover now published by Cisco 2601.01353; revive as "the analytic threshold behind the benchmark") · K3 IterDQC (83.0 — re-partition frequency `f*` for iterative VQE/QAOA from a U-shaped convergence-vs-decoherence cost; genuinely uncontested workload class) · G1 (85.0, fidelity-near-dup of J1) · K2 QSSReliableDQC (82.0 — (k,n) secret-sharing reliability; primitive pre-owned). Full history: `QDC_idea_ledger.md` (48 ideas).

---

## Cycle-11 detail

### What changed in ChunmingQiao (final build + QDN transport deep-dive)
Folded in the QDN transport layer (Tele-DTP/TAG-DTP 2023 TON; AQTP 2024 JSAC): newly first-class, ledger-untouched moves — **"congestion"=quantum-memory contention, a QDN must be provably congestion-free** (window control + intermediate-node congestion-encounter halving; congestion-free only for α>1/2; fairness zig-zag, Jain 0.99, <1% from ILP); **reliability-by-construction via (k,n) quantum secret sharing** (no retransmission, forced by no-cloning); AQTP's **decouple-EL-creation-from-EC-assignment / lazy-bind-at-swap + immediate memory reuse** ("CBP wins when teleport p>0.94"). No prior ledger entry touches the transport/flow-control or reliability-by-construction layer → opens a new decision-type and lifts K1 into best-3, displacing E1.

### The 3 new ideas (Qiao move / Qiaolun anchor / DQC gap)
- **K1 CongestFreeDQC** — (a) **transplant his own QDN transport (Tele-DTP/AQTP) into the intra-QDC fabric + constraint-reframe** ("congestion-free" invariant); (b) deployable-on-existing-SDN (no centralized re-solve) + actionable W* + reuse-before-redundancy; (c) Bahrani/Cisco centralized "assume-reliable-entanglement" + 2504.20176 (centralized, no distributed control); Zhao&Qiao transport is wide-area QDN not the QDC fabric.
- **K3 IterDQC** *(runner-up, 83.0)* — (a) **let theory yield the control rule** (U-shaped cost → closed-form f*) + decouple-timescales; (b) networking-for-AI scheduling (SAPSA) + actionable knob + multi-scale eval; (c) no DQC work models *iterative/variational* workloads (Bahrani/Cisco one-shot). Re-partition frequency f* for VQE/QAOA from a convergence-vs-decoherence bound.
- **K2 QSSReliableDQC** *(runner-up, 82.0)* — (a) **achieve-property-by-construction** (reliability from (k,n) coding); (b) resilience + tiered residual-only escalation + conservative bound; (c) no-cloning/no-retransmission + assume-reliable base papers. AT-RISK: QSS-reliability owned by Qiao's TAG-DTP/AQTP + ax_1903.10685.

### Six-idea FRESH scoring table
| ID | Idea | Decision-type | Rubric A | Rubric B | Comb. |
|----|------|---------------|----------|----------|-------|
| **I1** | AnalyticBlockDQC — loss-network blocking + dimensioning | analytical-performance-model | 85 | 86 | **85.5** |
| **J1** | CrossLayerFidDQC — contention-driven placement reversal | cross-layer placement co-design | 83 | 87 | **85.0** |
| **K1** | CongestFreeDQC — compute-DAG-coupled congestion-free transport | transport/distributed flow-control | 83 | 85 | **84.0** |
| E1 | SwapVsBuy — cost-effectiveness puncture | provisioning/routing economics | 82 | 85 | 83.5 |
| K3 | IterDQC — re-partition frequency from convergence bound | iterative-workload control-knob | 82 | 84 | 83.0 |
| K2 | QSSReliableDQC — (k,n) secret-sharing reliability | resilience/reliability coding | 80 | 83 | 82.0 |

(E1 fell to A82 because Cisco 2601.01353 published its exact crossover; K1 edges it on gap-novelty.)

### Chosen BEST 3 (distinct: analytical-model / cross-layer-placement / transport-control; I1+K1 tractable HIGH, J1 MED-HIGH; no near-dups)
- **I1 (BEST-1)** A85/B86. Weakness: Erlang link-independence; ax_2405.18066 (single-switch Erlang) now IEEE-published. Fix: lead with coherence-as-holding-time perishability + network-wide fixed point + dimensioning curve, bounded gap to event-sim. Tractability HIGH.
- **J1 (BEST-2)** A83/B87. Weakness: "min-cut≠fidelity" now common (2506.06867); reversal must come from the contention layer; needs a stochastic sim. Fix: own the contention-induced reversal + crossover + topology-as-knob, couple to I1's loss-network. Tractability MED-HIGH.
- **K1 (BEST-3)** A83/B85. Weakness: crowded quantum-congestion-control lane + congestion-free machinery transplanted from his own AQTP (reused-proof demerit). Fix: never claim "first quantum congestion control"; own the **compute-DAG-coupled window + QDC-fabric-specific congestion-free condition + cross-circuit fairness**, tie W* to I1. Tractability HIGH (protocol + theorems + sim <1% of centralized ILP).

### Prior-art positioning & residual-novelty audit (most-threatening first)
- **I1** — **Most-threatening: ax_2405.18066** (single Entanglement-Generation Switch as Erlang loss + insensitivity, now IEEE-published); runner-up ax_2603.24874 (adaptive memory control for *stability*, not a closed-form blocking model). **Gap:** no network-of-rack-pairs reduced-load fixed point / coherence-as-holding-time / dimensioning inversion. **Delta:** network-wide perishable fixed point → dimensioning. **Verdict: NOVEL (network/perishable layer);** frame 2405.18066 as the degenerate single-EGS corner.
- **J1** — **Most-threatening: ax_2506.06867** (fidelity-driven hypergraph partitioning); runner-ups DisMap, Bahrani ν_mk min-cut — all *static* single-layer cut. **Gap:** none models network-layer dynamic contention/queueing-decoherence that *reverses* the ranking. **Delta:** cross-layer reversal + closed-form crossover + topology-as-contention-knob. **Verdict: NOVEL-narrow (borderline AT-RISK).**
- **K1** — **Most-threatening: Qiao's own AQTP (2024 JSAC)** + Tele-DTP (2023 TON) / Tele-QTP (ax_2105.08109), "Quantum ECN" survey (WashU 2025), ax_2603.24874 (memory control for stability); ax_2504.20176 (centralized QDC scheduling). **Gap:** all are wide-area QDN transport *decoupled from compilation*, or centralized QDC scheduling, or distribution-stability — none is a **distributed intra-QDC-fabric congestion-control whose window is coupled to the remote-gate DAG + cutoff** with a fabric-specific congestion-free condition. **Delta:** compute-DAG-coupled window + QDC-fabric congestion-free condition + cross-circuit fairness + dimensioning tie to I1. **Verdict: NOVEL-narrow, AT-RISK** → "compute-DAG-coupled, intra-QDC-fabric congestion-free window," not generic QDN transport.

> **Portfolio takeaways:** (1) I1 threat (2405.18066) IEEE-published → degenerate-corner framing mandatory. (2) J1 borderline AT-RISK (2506.06867) — survives on the contention layer. (3) K1 AT-RISK (own-AQTP transplant + crowded lane) — survives on the compute-DAG-coupled + fabric-specific angle. (4) E1 eroded by Cisco 2601.01353.

### CHANGELOG vs cycle 10 (I1/E1/J1)
- **I1 — STAYS #1** (85.5 flat).
- **J1 — STAYS, #3→#2** (85.0): highest Qiao sub-score (B87); survives on the contention-reversal regime.
- **E1 — DISPLACED → top runner-up** (85.0→83.5): Cisco 2601.01353 published the exact repeater-vs-bypass crossover, eroding the headline; revive as "the analytic threshold behind the benchmark" (not a near-dup of K1: provisioning-economics vs transport-control).
- **K1 — NEW, enters #3** (84.0): exploits the freshest edit (QDN transport layer), opens a new decision-type (distributed transport/flow-control); AT-RISK, defended by the compute-DAG-coupled + QDC-fabric angle.
- **K2 (82.0) / K3 (83.0) runners-up** — K2's QSS primitive pre-owned; K3 opens the uncontested iterative/variational workload class (strongest revival candidate).
- **Net:** {analytical perishable loss-model (I1) · cross-layer contention-reversal placement (J1) · compute-DAG-coupled congestion-free transport (K1)} — rotates toward the freshly-extracted transport/flow-control lane, keeping the analytical-model anchor and two HIGH-tractable members (I1, K1).
