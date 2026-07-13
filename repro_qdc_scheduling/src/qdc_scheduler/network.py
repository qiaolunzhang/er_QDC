"""DQC network model (paper Sec. II + Sec. IV-A1).

Fat-tree data-centre topology with 4 pods x 4 QPUs (J = 16). Each pod has two edge
switches with two QPUs each. The number of optical switches n_s on the path between
two QPUs is:
    same edge switch -> 1,  same pod (different edge switch) -> 3,  cross-pod -> 5.

Link latency (Eq. 8):  T_link_{n_s} = T_el / eta_s^{n_s}, with per-switch
transmission efficiency eta_s = 10^(-loss_dB/10). Link fidelities: F_link1 = 0.96,
F_link3 = 0.94, F_link5 = 0.92 (for the default 0.5 dB loss; higher losses keep the
same fidelity table unless stated otherwise).

All times are normalised by T_dec: T_el/T_dec = 0.005, T_local/T_dec = 5e-4.

QPU capacities: four QPUs each of 8, 12, 16, 20 qubits, randomly assigned with a
fixed seed (repeated over 10 seeds in the experiments).
"""

from __future__ import annotations

import numpy as np

T_EL_OVER_TDEC = 0.005
T_LOCAL_OVER_TDEC = 5e-4
FIDELITY = {1: 0.96, 3: 0.94, 5: 0.92}
CAPACITY_POOL = [8] * 4 + [12] * 4 + [16] * 4 + [20] * 4


class DQCNetwork:
    def __init__(self, n_pods: int = 4, qpus_per_pod: int = 4,
                 switch_loss_db: float = 0.5, capacity_seed: int = 0):
        self.J = n_pods * qpus_per_pod
        self.n_pods = n_pods
        self.qpus_per_pod = qpus_per_pod
        self.switch_loss_db = switch_loss_db
        self.capacity_seed = capacity_seed

        rng = np.random.default_rng(capacity_seed)
        pool = list(CAPACITY_POOL)
        if self.J != len(pool):  # non-default sizes: cycle the capacity values
            pool = ([8, 12, 16, 20] * ((self.J + 3) // 4))[: self.J]
        self.capacities = list(rng.permutation(pool))
        self.capacities = [int(c) for c in self.capacities]

        eta = 10 ** (-switch_loss_db / 10.0)
        # latency (normalised by T_dec) per switch count n_s (Eq. 8)
        self.latency_by_ns = {ns: T_EL_OVER_TDEC / eta ** ns for ns in (1, 3, 5)}
        self.fidelity_by_ns = dict(FIDELITY)

    # --- topology -----------------------------------------------------------
    def pod(self, j: int) -> int:
        return j // self.qpus_per_pod

    def edge_switch(self, j: int) -> int:
        """Global edge-switch id; 2 QPUs per edge switch."""
        return j // 2

    def n_switches(self, j1: int, j2: int) -> int:
        if j1 == j2:
            raise ValueError("same QPU has no link")
        if self.edge_switch(j1) == self.edge_switch(j2):
            return 1
        if self.pod(j1) == self.pod(j2):
            return 3
        return 5

    # --- link parameters (normalised by T_dec) ------------------------------
    def latency(self, j1: int, j2: int) -> float:
        """T_{j1 j2} / T_dec."""
        return self.latency_by_ns[self.n_switches(j1, j2)]

    def fidelity(self, j1: int, j2: int) -> float:
        return self.fidelity_by_ns[self.n_switches(j1, j2)]

    @property
    def total_capacity(self) -> int:
        return sum(self.capacities)
