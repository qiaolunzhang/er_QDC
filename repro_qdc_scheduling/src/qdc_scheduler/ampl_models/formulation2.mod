# Formulation 2: MILP-based Single-QCirc assignment problem (paper Sec. III-B).
# Same objective/constraints as Formulation 1, simplified to one circuit.

set J;                                  # available QPUs

param Kmax integer >= 1;
param wm >= 0;                          # qubit requirement of the circuit
param N {J} >= 0;
param s {J} binary;
param T {J, J} >= 0;                    # latency / T_dec
param F {J, J} >= 0;
param omega0 >= 0 default 1;
param omega1 >= 0 default 1;
# epsilon tie-break: among zero/equal-cost optima prefer the smallest allocated
# capacity (best fit), so large QPUs stay free for circuits that need them
param eps >= 0 default 1e-6;

var r {J} binary;
# product of binaries, pinned by constraints (3) once r is integral -> continuous
var z {j1 in J, j2 in J: j1 < j2} >= 0, <= 1;

minimize C:
    sum {j1 in J, j2 in J: j1 < j2}
        z[j1,j2] * (omega0 * wm * T[j1,j2] + omega1 * (1 - F[j1,j2]))
    + eps * sum {j in J} r[j] * N[j];

s.t. Capacity:                            # (1)
    sum {j in J} r[j] * s[j] * N[j] >= wm;

s.t. PartitionCount:                      # (2)
    sum {j in J} r[j] <= Kmax;

s.t. ZLower {j1 in J, j2 in J: j1 < j2}:  # (3)
    r[j1] + r[j2] - 1 <= z[j1,j2];
s.t. ZUpper1 {j1 in J, j2 in J: j1 < j2}:
    z[j1,j2] <= r[j1];
s.t. ZUpper2 {j1 in J, j2 in J: j1 < j2}:
    z[j1,j2] <= r[j2];
