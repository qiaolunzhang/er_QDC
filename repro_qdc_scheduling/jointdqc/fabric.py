"""Explicit fat-tree fabric with optical switches and BSM budgets (JointDQC).

The base paper (`qdc_scheduler.network.DQCNetwork`) characterises a QPU pair only by its
switch-hop count n_s in {1,3,5} and gives fixed latency/fidelity per pair. That hides *which*
switches a remote gate traverses and how many remote gates share a switch. JointDQC needs the
explicit fabric so per-switch BSM (entanglement-swap) contention becomes a constraint.

Topology (3-tier fat-tree, matching the paper's n_s in {1,3,5}):
  - 16 QPUs, pod(j) = j // 4, edge_switch(j) = j // 2  -> 8 edge switches E0..E7
  - 4 aggregation switches A0..A3, one per pod (pod p aggregates edge switches {2p, 2p+1})
  - Ncore core switches Cr0..Cr_{Ncore-1}, fully connected to every aggregation switch

Path (set of switches performing a BSM for a remote gate between QPUs j1, j2):
  - same edge switch  -> [E]                          (n_s = 1)
  - same pod, diff edge-> [E1, A, E2]                 (n_s = 3)
  - cross pod          -> [E1, A1, Cr, A2, E2]        (n_s = 5); the core Cr is a routing choice

BSM budget: edge/agg switches get a generous default; the *core* budget `Bcore` per core switch is
the sweepable bottleneck knob (cross-pod contention is exactly the resource the base model ignores).
"""

from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from itertools import combinations
from dataclasses import dataclass

from qdc_scheduler.network import DQCNetwork


@dataclass
class Fabric:
    ncore: int = 2                 # number of core switches (routing multiplicity)
    bcore: float = 4.0             # BSM budget per core switch (ebits/cycle)
    bedge: float = 1e9             # BSM budget per edge switch (default: unconstrained)
    bagg: float = 1e9              # BSM budget per aggregation switch
    capacity_seed: int = 0
    switch_loss_db: float = 0.5

    def __post_init__(self):
        self.net = DQCNetwork(switch_loss_db=self.switch_loss_db,
                              capacity_seed=self.capacity_seed)
        self.J = list(range(self.net.J))
        # switch id namespaces (strings keep them distinct in AMPL sets)
        self.edges = [f"E{e}" for e in range(self.net.J // 2)]       # 8
        self.aggs = [f"A{p}" for p in range(self.net.n_pods)]        # 4
        self.cores = [f"Cr{c}" for c in range(self.ncore)]
        self.switches = self.edges + self.aggs + self.cores

    # ---- topology helpers ----
    def pod(self, j):
        return self.net.pod(j)

    def edge_switch(self, j):
        return f"E{self.net.edge_switch(j)}"

    def agg_switch(self, j):
        return f"A{self.pod(j)}"

    def is_xpod(self, j1, j2):
        return self.pod(j1) != self.pod(j2)

    def path_fixed_switches(self, j1, j2):
        """Edge+agg switches on the (fixed) path; the core, if any, is a routing choice."""
        if j1 == j2:
            return []
        e1, e2 = self.edge_switch(j1), self.edge_switch(j2)
        if e1 == e2:                                    # n_s = 1
            return [e1]
        if not self.is_xpod(j1, j2):                    # n_s = 3, same pod
            return [e1, self.agg_switch(j1), e2]
        # n_s = 5, cross pod: E1 A1 [core] A2 E2  (core added separately)
        return [e1, self.agg_switch(j1), self.agg_switch(j2), e2]

    # ---- capacity map ----
    def bcap(self, sw):
        if sw.startswith("Cr"):
            return self.bcore
        if sw.startswith("E"):
            return self.bedge
        return self.bagg

    # ---- convenience pass-throughs ----
    @property
    def capacities(self):
        return self.net.capacities

    def latency(self, j1, j2):
        return self.net.latency(j1, j2)

    def fidelity(self, j1, j2):
        return self.net.fidelity(j1, j2)

    @property
    def total_capacity(self):
        return self.net.total_capacity

    # ---- incidence data for the AMPL model ----
    def incidence(self):
        """Return (inc, xpod) dicts over ordered pairs j1<j2.

        inc[(sw, j1, j2)] = 1 if edge/agg switch sw lies on the fixed path of the pair.
        xpod[(j1, j2)]    = 1 if the pair is cross-pod (traverses one core switch).
        """
        inc, xpod = {}, {}
        for j1, j2 in combinations(self.J, 2):
            for sw in self.path_fixed_switches(j1, j2):
                inc[(sw, j1, j2)] = 1
            xpod[(j1, j2)] = 1 if self.is_xpod(j1, j2) else 0
        return inc, xpod
