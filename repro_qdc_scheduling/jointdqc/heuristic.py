"""Scalable schemes for JointDQC: the network-oblivious baseline and a greedy heuristic.

- Network-Oblivious (NO): the base paper's Formulation 1 (via `qdc_scheduler.milp.MilpSolver`),
  which minimises latency+infidelity but is blind to switch BSM contention. This is the incumbent
  we must beat -- it is REUSED verbatim from the reproduction code.
- Congestion-Aware Greedy (CAG): places circuits one-by-one (densest first), each taking the
  capacity-feasible QPU combo that least raises the peak core BSM load given the residual budget.
  O(|M| * C(|J|,k)) -- scales far past the MILP, at a bounded optimality gap we report.
"""

from __future__ import annotations

from itertools import combinations

from qdc_scheduler.milp import MilpSolver

from evaluator import nu_of


# ------------------------------------------------------------------ NO baseline
def solve_no(circuits: dict, fabric, nu_models, zeta: int | None = None) -> dict:
    """Network-oblivious allocation = base Formulation 1. Returns {m: [qpus]}."""
    solver = MilpSolver()
    ms = sorted(circuits)
    kmax = min(4, len(fabric.J))
    circ_arg = {m: (circuits[m].width, kmax) for m in ms}
    nu = {(m, k): (nu_models[k].nu(circuits[m].graph) if k >= 2 else 0.0)
          for m in ms for k in range(1, kmax + 1)}
    res = solver.solve_batch(circ_arg, fabric.net, list(fabric.J), nu, zeta=zeta)
    return {m: list(res.assignment[m]) for m in ms}, res.solve_time


# ------------------------------------------------------------------ CAG heuristic
def _induced_core_load(circ, combo, fabric, nu_models):
    """Cross-pod ebit load a placement `combo` (k=len) would add to the core layer."""
    k = len(combo)
    nu = nu_of(circ, k, nu_models)
    if nu == 0.0:
        return 0.0
    return sum(nu for a, b in combinations(sorted(combo), 2) if fabric.is_xpod(a, b))


def solve_cag(circuits: dict, fabric, nu_models, zeta: int | None = None) -> dict:
    """Congestion-aware greedy. Densest circuits first; each minimises added peak core load."""
    ms = sorted(circuits)
    kmax = min(4, len(fabric.J))
    # order by connectivity nu_m(k=2), densest first
    order = sorted(ms, key=lambda m: -nu_of(circuits[m], 2, nu_models))
    free = set(fabric.J)
    alloc = {m: [] for m in ms}
    core_budget = fabric.ncore * fabric.bcore
    core_used = 0.0
    target = len(ms) if zeta is None else zeta
    placed = 0
    for m in order:
        if placed >= target:
            break
        w = circuits[m].width
        best = None  # (added_core_load, base_proxy, combo)
        for k in range(1, kmax + 1):
            for combo in combinations(sorted(free), k):
                if sum(fabric.capacities[j] for j in combo) < w:
                    continue
                add = _induced_core_load(circuits[m], combo, fabric, nu_models)
                if core_used + add > core_budget + 1e-9:
                    continue  # would blow the aggregate core budget
                nu = nu_of(circuits[m], k, nu_models)
                base = sum(nu * (w * fabric.latency(a, b) + (1 - fabric.fidelity(a, b)))
                           for a, b in combinations(sorted(combo), 2))
                key = (add, base, sum(fabric.capacities[j] for j in combo))
                if best is None or key < best[0]:
                    best = (key, list(combo), add)
            if best is not None and k == 1 and best[0][0] == 0:
                break  # a zero-core-load single-QPU fit cannot be beaten
        if best is not None:
            alloc[m] = best[1]
            core_used += best[2]
            free -= set(best[1])
            placed += 1
    return alloc
