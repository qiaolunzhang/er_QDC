# Formulation 1: MILP-based Batch-QCirc assignment problem (paper Sec. III-A1).
# Objective Eq. 1 (linearised via z, x); constraints (1)-(6).
# All latencies T are pre-normalised by T_dec.

set M;                                  # circuits in the selected batch
set J;                                  # available QPUs (integer ids)

param Kmax {M} integer >= 1;            # K_m^max
param w {M} >= 0;                       # qubit requirement w_m
param N {J} >= 0;                       # QPU capacities
param s {J} binary;                     # QPU availability
param T {J, J} >= 0;                    # entanglement latency / T_dec
param F {J, J} >= 0;                    # entanglement fidelity
param nu {m in M, k in 1..Kmax[m]} >= 0;  # partitioning cost coefficient nu_mk
param zeta >= 0;                        # number of circuits to assign this cycle
param omega0 >= 0 default 1;
param omega1 >= 0 default 1;

var r {M, J} binary;                                    # QPU_j allocated to circuit m
var y {m in M, k in 1..Kmax[m]} binary;                 # circuit m split into k parts
# z, x are products of binaries; constraints (5)-(6) pin them exactly once r, y are
# integral, so declaring them continuous in [0,1] is equivalent and far faster.
var z {m in M, j1 in J, j2 in J: j1 < j2} >= 0, <= 1;   # z = r[m,j1]*r[m,j2]
var x {m in M, k in 1..Kmax[m], j1 in J, j2 in J: j1 < j2} >= 0, <= 1;  # x = z*y

minimize C:
    sum {m in M, k in 1..Kmax[m], j1 in J, j2 in J: j1 < j2}
        nu[m,k] * x[m,k,j1,j2] * (omega0 * w[m] * T[j1,j2] + omega1 * (1 - F[j1,j2]));

s.t. MinAssignment:                       # (1)
    sum {m in M, k in 1..Kmax[m]} y[m,k] = zeta;

s.t. Capacity {m in M}:                   # (2)
    sum {j in J} r[m,j] * s[j] * N[j] >= w[m] * sum {k in 1..Kmax[m]} y[m,k];

s.t. PartitionCount {m in M}:             # (3)
    sum {j in J} r[m,j] = sum {k in 1..Kmax[m]} k * y[m,k];

s.t. SinglePartitionPerQPU {j in J}:      # (4)
    sum {m in M} r[m,j] <= 1;

s.t. ZLower {m in M, j1 in J, j2 in J: j1 < j2}:   # (5)
    r[m,j1] + r[m,j2] - 1 <= z[m,j1,j2];
s.t. ZUpper1 {m in M, j1 in J, j2 in J: j1 < j2}:
    z[m,j1,j2] <= r[m,j1];
s.t. ZUpper2 {m in M, j1 in J, j2 in J: j1 < j2}:
    z[m,j1,j2] <= r[m,j2];

s.t. XLower {m in M, k in 1..Kmax[m], j1 in J, j2 in J: j1 < j2}:   # (6)
    z[m,j1,j2] + y[m,k] - 1 <= x[m,k,j1,j2];
s.t. XUpper1 {m in M, k in 1..Kmax[m], j1 in J, j2 in J: j1 < j2}:
    x[m,k,j1,j2] <= z[m,j1,j2];
s.t. XUpper2 {m in M, k in 1..Kmax[m], j1 in J, j2 in J: j1 < j2}:
    x[m,k,j1,j2] <= y[m,k];
