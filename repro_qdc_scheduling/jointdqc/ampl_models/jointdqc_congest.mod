# JointDQC — congestion-aware joint allocation + routing (min-max peak BSM load).
# Extends Formulation 1 (Bahrani et al.): same allocation core (r,y,z,x) but the
# objective minimises the peak per-switch BSM (entanglement-swap) utilisation t,
# i.e. the fabric contention the base model is blind to. eps*C keeps the base cost
# (latency+infidelity) as a tie-break among equal-congestion optima.
# All latencies T are pre-normalised by T_dec.

set M;                                  # circuits in the batch
set J;                                  # available QPUs
set SW;                                 # edge + aggregation switches (per-switch cap)

param Kmax {M} integer >= 1;
param w {M} >= 0;
param N {J} >= 0;                        # QPU capacities
param s {J} binary;                     # QPU availability
param T {J, J} >= 0;
param F {J, J} >= 0;
param nu {m in M, k in 1..Kmax[m]} >= 0;
param zeta >= 0;
param omega0 >= 0 default 1;
param omega1 >= 0 default 1;
param epsc >= 0 default 1e-3;           # tie-break weight on base cost

# fabric data
param Bcap {SW} >= 0;                    # BSM budget of each edge/agg switch
param inc {SW, j1 in J, j2 in J: j1 < j2} default 0;   # switch on fixed path of pair
param xpod {j1 in J, j2 in J: j1 < j2} binary default 0; # pair is cross-pod (uses a core)
param Ncore >= 1;                        # number of symmetric core switches
param Bcore >= 0;                        # BSM budget per core switch

var r {M, J} binary;
var y {m in M, k in 1..Kmax[m]} binary;
var z {m in M, j1 in J, j2 in J: j1 < j2} >= 0, <= 1;
var x {m in M, k in 1..Kmax[m], j1 in J, j2 in J: j1 < j2} >= 0, <= 1;
var t >= 0;                              # peak normalised BSM utilisation

# ebit load carried by pair (j1,j2) for circuit m  =  sum_k nu_mk * x
# (nu_mk = expected remote-gate cut = # ebits, reused from the paper's regression)

minimize Peak:
    t
  + epsc * sum {m in M, k in 1..Kmax[m], j1 in J, j2 in J: j1 < j2}
        nu[m,k] * x[m,k,j1,j2] * (omega0 * w[m] * T[j1,j2] + omega1 * (1 - F[j1,j2]));

# ---- base allocation constraints (Formulation 1, (1)-(6)) ----
s.t. MinAssignment:
    sum {m in M, k in 1..Kmax[m]} y[m,k] = zeta;
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

# ---- fabric BSM contention (new) ----
# edge/aggregation switches: total ebit load on sw <= t * Bcap[sw]
s.t. SwitchCong {sw in SW}:
    sum {m in M, j1 in J, j2 in J: j1 < j2}
        inc[sw,j1,j2] * (sum {k in 1..Kmax[m]} nu[m,k] * x[m,k,j1,j2])
    <= t * Bcap[sw];

# core layer: cross-pod ebit load spread over Ncore symmetric cores <= t * Ncore * Bcore
s.t. CoreCong:
    sum {m in M, j1 in J, j2 in J: j1 < j2}
        xpod[j1,j2] * (sum {k in 1..Kmax[m]} nu[m,k] * x[m,k,j1,j2])
    <= t * Ncore * Bcore;
