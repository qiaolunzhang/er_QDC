# Congestion-blindness probe: explore the base-cost-optimal FACE.
#
# The base paper's objective (Bahrani et al., Formulation 1) minimises
#   Cost = sum nu_mk * x_mkj1j2 * (omega0 w_m T_j1j2 + omega1 (1-F_j1j2)).
# We show this objective does NOT control core (cross-pod) BSM load: among schedules whose
# base cost is within a tolerance of the optimum, the core load spans a huge range. To measure
# that range RIGOROUSLY (not via solver-tie-break luck), we fix full admission and, subject to
# a base-cost budget Cbudget, either MINIMISE or MAXIMISE the core load (Dir = +1 / -1).
# The gap between the two at a tight Cbudget is the congestion-blindness of the base objective.

set M;
set J;
set SW;

param Kmax {M} integer >= 1;
param w {M} >= 0;
param N {J} >= 0;
param s {J} binary;
param T {J, J} >= 0;
param F {J, J} >= 0;
param nu {m in M, k in 1..Kmax[m]} >= 0;
param omega0 >= 0 default 1;
param omega1 >= 0 default 1;

param Bcap {SW} >= 0;                    # unused here (kept for load-compatibility)
param inc {SW, j1 in J, j2 in J: j1 < j2} default 0;
param xpod {j1 in J, j2 in J: j1 < j2} binary default 0;
param Ncore >= 1;
param Bcore >= 0;

param Cbudget >= 0;                       # base-cost budget = (1+eps) * Cmin
param Dir default 1;                      # +1 => minimise core load, -1 => maximise it

var r {M, J} binary;
var y {m in M, k in 1..Kmax[m]} binary;
var z {m in M, j1 in J, j2 in J: j1 < j2} >= 0, <= 1;
var x {m in M, k in 1..Kmax[m], j1 in J, j2 in J: j1 < j2} >= 0, <= 1;

# core (cross-pod) BSM load and base cost as linear expressions
var CoreLoad = sum {m in M, j1 in J, j2 in J: j1 < j2}
    xpod[j1,j2] * (sum {k in 1..Kmax[m]} nu[m,k] * x[m,k,j1,j2]);
var BaseCost = sum {m in M, k in 1..Kmax[m], j1 in J, j2 in J: j1 < j2}
    nu[m,k] * x[m,k,j1,j2] * (omega0 * w[m] * T[j1,j2] + omega1 * (1 - F[j1,j2]));

minimize CostObj: BaseCost;               # select this to get Cmin (the base optimum)
minimize FaceObj: Dir * CoreLoad;         # select this to probe the cost face

s.t. AdmitAll {m in M}:                    # full admission: every circuit is scheduled once
    sum {k in 1..Kmax[m]} y[m,k] = 1;
s.t. CostCap:                              # stay on the (near-)optimal cost face
    BaseCost <= Cbudget;
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
