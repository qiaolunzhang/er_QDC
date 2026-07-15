# QDC — Idea Leaderboards

Two views over all 30 ideas (full list + descriptions in `QDC_idea_ledger.md`):
- **§1 As-recorded** — each idea's score from the cycle it was judged in (ChunmingQiao v2→v5 evolved across cycles → cross-cycle comparison is approximate).
- **§2 Uniform-v5** — ALL 30 re-scored on one ruler (current ChunmingQiao v5 + QiaolunResearch), the fair comparison. **This supersedes §1 for ranking purposes.**

Generated 2026-06-29 (after cycle 5). **Cycle-11 update:** best 3 = **I1 AnalyticBlockDQC (85.5) · J1
CrossLayerFidDQC (85.0) · K1 CongestFreeDQC (84.0, NEW)**; E1→top runner-up (Cisco 2601.01353 published
its crossover), K3 (83.0)/K2 (82.0) runner-up. ChunmingQiao final build + QDN-transport deep-dive
elevated congestion-free-transport / reliability-by-construction moves (lifted K1). Ledger = 48 ideas.
See `QDC_best3_ideas.md` for fresh scores + prior-art. (Cycle 10 best-3 was I1/E1/J1.) _Earlier:_ **Cycle-10 update:** best 3 = **I1 AnalyticBlockDQC (85.5) · E1
SwapVsBuy (85.0) · J1 CrossLayerFidDQC (85.0, NEW)**; G1→top runner-up (fidelity-near-dup of J1), J2
(83.5)/J3 (81.0) runner-up. ChunmingQiao v8 final-build polish elevated the cross-layer-truth-telling /
topology-as-control-knob move (lifted J1). Ledger = 45 ideas. See `QDC_best3_ideas.md` for fresh scores +
prior-art. (Cycle 9 best-3 was I1/E1/G1.) _Earlier:_ **Cycle-9 update:** current best 3 = **I1 AnalyticBlockDQC (85.5, NEW) ·
E1 SwapVsBuy (85.0) · G1 FrontierDQC (85.0)**; H1→top runner-up, I2 (83.0) / I3 (81.5) runner-up.
ChunmingQiao v8 (81 papers) added the *recast-as-known-well-studied-theory* move (loss networks) → I1
(first analytical blocking model for a QDC fabric, threat ax_2405.18066 single-switch Erlang) tops the
list. Ledger now has 42 ideas; each best-3 carries a prior-art positioning. The §2 uniform table below is
the cycle-5 re-baseline snapshot (30 ideas); see `QDC_best3_ideas.md` for the latest fresh 6-idea scores +
prior-art audit. (Cycle 8 best-3 was E1/G1/H1.)

---

## §1 — AS-RECORDED leaderboards (cross-cycle, approximate)

### §1a Combined (Qiaolun + Qiao avg)
E1 84.5 · D2 84.0 · E2 82.5 · N1 82.0 · #7 81.5 · D1 81.5 · C3 81.0 · N2 81.0 · E3 80.5 · D3 79.5 · C1 79.0 · #14 77.5 · C2 77.5 · #4 77.0 · N3 75.5 · N4 75.5 · #1 SC-Route 75.0 · #11 75.0 · #13 74.5 · #8 72.5 · #6 72.5 · #10 71.5 · #15 71.5 · N5 71.0 · #2 70.5 · #5 70.5 · #12 68.0 · #9 67.5 · #16 65.5 · #3 65.0

### §1b ChunmingQiao-only (Rubric B)
D2 86 · E1 85 · N1 84 · C3 83 · #7 82 · N2 82 · D1 82 · E2 82 · D3 81 · E3 81 · C1 80 · #4 78 · N3 78 · C2 78 · N4 77 · #1 SC-Route 76 · #14 76 · #10 74 · #13 74 · #8 73 · #11 73 · #6 72 · N5 72 · #2 71 · #15 71 · #5 70 · #9 67 · #3 66 · #12 66 · #16 65

---

## §2 — UNIFORM-v5 leaderboards (one ruler; the fair ranking)

**Effect of uniform scoring:** the as-recorded numbers were biased — cycle-4/5 ideas judged under the newest version, cycle-1 candidates frozen at v2–v3. Under v5 applied to all 30: cycle-1 candidates carrying v5's rewarded machinery RISE (decouple-timescales / Lagrangian-yardstick / push-off-critical-path / complexity-placement / cost-effectiveness-proof); recent one-knob buffer/memory ideas FALL. Risers: **#7 (+3.5), JointDQC (+7.0), #14 (+4.5), #13 (+6.5), #8 (+7.5), #10 SurviveDQC (+8.0), #11 (+4.5), LocateQDC (+9.5)**. Fallers: **D3 (−5.0), N4 (−3.0), N1 (−2.5), E3 (−2.5)**.

### §2a Uniform-v5 COMBINED (all 30)
| # | ID | Title | A | B | Comb | Δ |
|--:|----|-------|--:|--:|--:|--:|
| 1 | E1 | SwapVsBuy (server-centric) | 84 | 86 | **85.0** | +0.5 |
| 2 | #7 | Decomposed-and-Bounded (CG+Lagrangian+GNN) | 83 | 87 | **85.0** | +3.5 |
| 3 | #4 | JointDQC (Lagrangian/CG joint alloc+routing) | 83 | 85 | **84.0** | +7.0 |
| 4 | D2 | FidelitySLA-Dual | 84 | 83 | **83.5** | −0.5 |
| 5 | E2 | TwoTimescaleSched | 83 | 83 | **83.0** | +0.5 |
| 6 | C3 | RepeaterCarve | 82 | 83 | **82.5** | +1.5 |
| 7 | #14 | Success-Prob-Constrained + Tiered Purification | 82 | 82 | **82.0** | +4.5 |
| 8 | D1 | FairCompletionFlip | 81 | 82 | **81.5** | 0.0 |
| 9 | #13 | BSM-Contention-Aware Co-Scheduling | 81 | 81 | **81.0** | +6.5 |
| 10 | C1 | SwitchFlip | 80 | 82 | **81.0** | +2.0 |
| 11 | N2 | ε-Local-DQC | 79 | 82 | **80.5** | −0.5 |
| 12 | #8 | Look-Ahead Switch Reconfiguration | 80 | 80 | **80.0** | +7.5 |
| 13 | N1 | CutoffFlip | 79 | 80 | **79.5** | −2.5 |
| 14 | #11 | CostQDC | 80 | 79 | **79.5** | +4.5 |
| 15 | #10 | SurviveDQC | 77 | 82 | **79.5** | +8.0 |
| 16 | C2 | TrafficShape | 78 | 79 | **78.5** | +1.0 |
| 17 | E3 | MinMonitorState | 77 | 79 | **78.0** | −2.5 |
| 18 | #1 | SC-Route | 76 | 79 | **77.5** | +2.5 |
| 19 | #12 | LocateQDC | 78 | 77 | **77.5** | +9.5 |
| 20 | #15 | Killing-the-Static-Alpha-Knob | 76 | 78 | **77.0** | +5.5 |
| 21 | N3 | BSM-Mechanism | 73 | 78 | **75.5** | 0.0 |
| 22 | D3 | BufferThreshold | 75 | 74 | **74.5** | −5.0 |
| 23 | #2 | RedundEnt | 73 | 76 | **74.5** | +4.0 |
| 24 | #5 | Chance-Constrained DQC | 74 | 74 | **74.0** | +3.5 |
| 25 | #6 | To-Buffer-or-Not | 73 | 73 | **73.0** | +0.5 |
| 26 | N4 | GeoQDC | 71 | 74 | **72.5** | −3.0 |
| 27 | N5 | RelocateThePartitioner | 70 | 72 | **71.0** | 0.0 |
| 28 | #9 | GroomQDC | 71 | 71 | **71.0** | +3.5 |
| 29 | #16 | Generate-or-Buffer | 69 | 69 | **69.0** | +3.5 |
| 30 | #3 | FreshEbit | 68 | 70 | **69.0** | +4.0 |

### §2b Uniform-v5 ChunmingQiao-ONLY (Rubric B, all 30)
| # | ID | Title | B | (comb rank) |
|--:|----|-------|--:|--:|
| 1 | #7 | Decomposed-and-Bounded | 87 | (2) |
| 2 | E1 | SwapVsBuy | 86 | (1) |
| 3 | #4 | JointDQC | 85 | (3) |
| 4 | D2 | FidelitySLA-Dual | 83 | (4) |
| 5 | E2 | TwoTimescaleSched | 83 | (5) |
| 6 | C3 | RepeaterCarve | 83 | (6) |
| 7 | #14 | Success-Prob + Tiered Purification | 82 | (7) |
| 8 | D1 | FairCompletionFlip | 82 | (8) |
| 9 | C1 | SwitchFlip | 82 | (10) |
| 10 | N2 | ε-Local-DQC | 82 | (11) |
| 11 | #10 | SurviveDQC | 82 | (15) |
| 12 | #13 | BSM-Contention-Aware | 81 | (9) |
| 13 | #8 | Look-Ahead Switch | 80 | (12) |
| 14 | N1 | CutoffFlip | 80 | (13) |
| 15 | #1 | SC-Route | 79 | (18) |
| 16 | C2 | TrafficShape | 79 | (16) |
| 17 | #11 | CostQDC | 79 | (14) |
| 18 | E3 | MinMonitorState | 79 | (17) |
| 19 | #15 | Killing-the-Static-Alpha | 78 | (20) |
| 20 | N3 | BSM-Mechanism | 78 | (21) |
| 21 | #12 | LocateQDC | 77 | (19) |
| 22 | #2 | RedundEnt | 76 | (23) |
| 23 | #5 | Chance-Constrained | 74 | (24) |
| 24 | D3 | BufferThreshold | 74 | (22) |
| 25 | N4 | GeoQDC | 74 | (26) |
| 26 | #6 | To-Buffer-or-Not | 73 | (25) |
| 27 | N5 | RelocateThePartitioner | 72 | (27) |
| 28 | #9 | GroomQDC | 71 | (28) |
| 29 | #3 | FreshEbit | 70 | (30) |
| 30 | #16 | Generate-or-Buffer | 69 | (29) |

### §2c New top 3 under the uniform ruler
- **By COMBINED:** **E1 SwapVsBuy (85.0)** · **#7 Decomposed-and-Bounded (85.0)** · **#4 JointDQC (84.0)**. → vs the as-recorded official best-3 (E1/D2/E2): only **E1 survives**; **D2→#4, E2→#5**, displaced by #7 & JointDQC (densest concentration of v5-rewarded moves: decouple-timescales + Lagrangian/CG yardstick + GNN-oracle-taught-by-exact-method + scale-vs-gap regime map, closing Bahrani's own open problems #1 & #8). E1 & #7 tie at 85.0; E1 takes #1 on cleaner standalone insight (Rubric A), #7 leads Rubric B.
- **By QIAO-ONLY:** **#7 (87)** · **E1 (86)** · **#4 JointDQC (85)**. D2 & E2 fall off the podium (tied 83). Notable Qiao-only riser: SurviveDQC (#10) to B-rank 11 (82) on pure complexity-placement (PP/#P/NP^PP + (1−1/e) carve), though Rubric A holds it to combined-15 on drift-model maturity.
- **Why the boards diverge:** combined rank tracks deployability/maturity (Rubric A pulls inference/complexity-heavy ideas down — LocateQDC, SurviveDQC); Qiao-only rewards paradigm fit + load-bearing theory (proof-and-bound ideas #7, SurviveDQC sit higher on B).
