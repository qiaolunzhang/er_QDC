"""Uniform congestion evaluator for JointDQC.

Given an allocation (circuit -> set of QPUs) produced by ANY scheme (network-oblivious base
MILP, congestion-aware JointDQC MILP, or the greedy heuristic), measure the fabric contention
it induces with a single, scheme-independent yard-stick. This is the fair referee: the MILP
that *optimises* these numbers should beat the base model that is blind to them.

Ebit-load model (identical to the MILP): a circuit m placed on QPU set S with k=|S| parts puts
an ebit load of nu_mk on every QPU pair (j1,j2) in S (nu_mk = expected remote-gate cut = ebits,
reused from the paper's regression). Each pair's load is charged to the BSM at every switch on its
path; cross-pod load is spread evenly over the Ncore symmetric core switches.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations


def nu_of(circ, k, nu_models):
    """nu_mk for a circuit at partition count k (0 for k<=1; regression value otherwise)."""
    if k <= 1:
        return 0.0
    return nu_models[k].nu(circ.graph)


def base_cost(circuits, alloc, fabric, nu_models, omega0=1.0, omega1=1.0):
    """The base-paper objective (latency + infidelity) of an allocation."""
    total = 0.0
    for m, qpus in alloc.items():
        k = len(qpus)
        nu = nu_of(circuits[m], k, nu_models)
        if nu == 0.0:
            continue
        for j1, j2 in combinations(sorted(qpus), 2):
            total += nu * (omega0 * circuits[m].width * fabric.latency(j1, j2)
                           + omega1 * (1 - fabric.fidelity(j1, j2)))
    return total


@dataclass
class Congestion:
    switch_load: dict          # switch id -> total ebit load
    core_load_total: float     # total cross-pod ebit load (all cores)
    peak_core_load: float      # per-core load after even spread = core_load_total / Ncore
    core_util: float           # peak_core_load / Bcore  (>1 => over budget => serialises)
    edge_agg_peak: float       # max load over edge/aggregation switches
    n_assigned: int
    base_cost: float
    cong_rounds: float         # serial BSM rounds at the busiest core = ceil-like util (>=1)


def evaluate(circuits, alloc, fabric, nu_models, omega0=1.0, omega1=1.0):
    """Measure congestion of `alloc` = {m: [qpus]} on `fabric`."""
    switch_load = {sw: 0.0 for sw in fabric.switches}
    core_total = 0.0
    n_assigned = 0
    for m, qpus in alloc.items():
        if qpus:
            n_assigned += 1
        k = len(qpus)
        nu = nu_of(circuits[m], k, nu_models)
        if nu == 0.0:
            continue
        for j1, j2 in combinations(sorted(qpus), 2):
            for sw in fabric.path_fixed_switches(j1, j2):
                switch_load[sw] += nu
            if fabric.is_xpod(j1, j2):
                core_total += nu
    # spread cross-pod load over the symmetric cores
    per_core = core_total / fabric.ncore
    for c in fabric.cores:
        switch_load[c] = per_core
    edge_agg_peak = max([switch_load[sw] for sw in fabric.edges + fabric.aggs], default=0.0)
    core_util = per_core / fabric.bcore if fabric.bcore > 0 else float("inf")
    cong_rounds = max(1.0, core_util)
    return Congestion(
        switch_load=switch_load,
        core_load_total=core_total,
        peak_core_load=per_core,
        core_util=core_util,
        edge_agg_peak=edge_agg_peak,
        n_assigned=n_assigned,
        base_cost=base_cost(circuits, alloc, fabric, nu_models, omega0, omega1),
        cong_rounds=cong_rounds,
    )
