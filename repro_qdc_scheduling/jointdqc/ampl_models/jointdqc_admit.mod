# JointDQC (admission form) — BSM-aware joint allocation + admission control.
# The base paper selects a batch by QUBIT capacity only and is blind to switch BSM
# (entanglement-swap) capacity. Here we make BSM capacity a first-class scheduling
# resource: maximise the number of admitted circuits subject to a HARD per-layer BSM
# budget (cross-pod ebit load <= aggregate core capacity), then minimise base cost as a
# tie-break. Extends Formulation 1 (Bahrani et al.); all latencies T pre-normalised by T_dec.

set M;                                  # candidate circuits (batch)
set J;                                  # available QPUs
set SW;                                 # edge + aggregation switches

param Kmax {M} integer >= 1;
param w {M} >= 0;
param N {J} >= 0;
param s {J} binary;
param T {J, J} >= 0;
param F {J, J} >= 0;
param nu {m in M, k in 1..Kmax[m]} >= 0;
param omega0 >= 0 default 1;
param omega1 >= 0 default 1;
param epsl >= 0 default 1e-3;            # 1st tie-break: minimise core (cross-pod) BSM load
param epsc >= 0 default 1e-6;            # 2nd tie-break: minimise base latency+infidelity cost

param Bcap {SW} >= 0;                    # BSM budget of each edge/agg switch
param inc {SW, j1 in J, j2 in J: j1 < j2} default 0;
param xpod {j1 in J, j2 in J: j1 < j2} binary default 0;
param Ncore >= 1;
param Bcore >= 0;                        # BSM budget per core switch

var r {M, J} binary;
var y {m in M, k in 1..Kmax[m]} binary;
var z {m in M, j1 in J, j2 in J: j1 < j2} >= 0, <= 1;
var x {m in M, k in 1..Kmax[m], j1 in J, j2 in J: j1 < j2} >= 0, <= 1;

# maximise admitted circuits; among equal-admission optima prefer the smallest core
# (cross-pod) BSM load, then the smallest base cost. The core-load tie-break makes the
# BSM-OBLIVIOUS baseline (Bcore -> inf) a *fair, deterministic strong baseline*: it not
# only admits the most circuits but also incurs the least congestion it can at that
# admission -- so any remaining gap to JointDQC is due solely to the hard BSM budget.
maximize Admitted:
    sum {m in M, k in 1..Kmax[m]} y[m,k]
  - epsl * sum {m in M, k in 1..Kmax[m], j1 in J, j2 in J: j1 < j2}
        xpod[j1,j2] * nu[m,k] * x[m,k,j1,j2]
  - epsc * sum {m in M, k in 1..Kmax[m], j1 in J, j2 in J: j1 < j2}
        nu[m,k] * x[m,k,j1,j2] * (omega0 * w[m] * T[j1,j2] + omega1 * (1 - F[j1,j2]));

s.t. AtMostOnce {m in M}:                 # a circuit is admitted at most once
    sum {k in 1..Kmax[m]} y[m,k] <= 1;
s.t. Capacity {m in M}:
    sum {j in J} r[m,j] * s[j] * N[j] >= w[m] * sum {k in 1..Kmax[m]} y[m,k];
s.t. PartitionCount {m in M}:
    sum {j in J} r[m,j] = sum {k in 1..Kmax[m]} k * y[m,k];
s.t. SinglePartitionPerQPU {j in J}:
    sum {m in M} r[m,j] <= 1;
s.t. ZLower {m in M, j1 in J, j2 in J: j1 < j2}:
    r[m,j1] + r[m,j2] - 1 <= z[m,j1,j2];
s.t. ZUpper1 {m in M, j1 in J, j2 in J: j1 < j2}:
    z[m,j1,j2] <= r[m,j1];
s.t. ZUpper2 {m in M, j1 in J, j2 in J: j1 < j2}:
    z[m,j1,j2] <= r[m,j2];
s.t. XLower {m in M, k in 1..Kmax[m], j1 in J, j2 in J: j1 < j2}:
    z[m,j1,j2] + y[m,k] - 1 <= x[m,k,j1,j2];
s.t. XUpper1 {m in M, k in 1..Kmax[m], j1 in J, j2 in J: j1 < j2}:
    x[m,k,j1,j2] <= z[m,j1,j2];
s.t. XUpper2 {m in M, k in 1..Kmax[m], j1 in J, j2 in J: j1 < j2}:
    x[m,k,j1,j2] <= y[m,k];

# ---- HARD BSM budgets (the new first-class resource) ----
s.t. SwitchCap {sw in SW}:
    sum {m in M, j1 in J, j2 in J: j1 < j2}
        inc[sw,j1,j2] * (sum {k in 1..Kmax[m]} nu[m,k] * x[m,k,j1,j2])
    <= Bcap[sw];
s.t. CoreCap:
    sum {m in M, j1 in J, j2 in J: j1 < j2}
        xpod[j1,j2] * (sum {k in 1..Kmax[m]} nu[m,k] * x[m,k,j1,j2])
    <= Ncore * Bcore;
