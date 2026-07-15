"""AMPL + CPLEX driver for the paper's MILP formulations (Formulation 1 & 2).

Uses the locally installed AMPL (/Applications/AMPL) with the CPLEX solver, driven
through amplpy. Model files live in ampl_models/. All latencies passed to AMPL are
pre-normalised by T_dec.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from itertools import combinations

from amplpy import AMPL, Environment

AMPL_DIR = os.environ.get("AMPL_DIR", "/Applications/AMPL")
_MODEL_DIR = os.path.join(os.path.dirname(__file__), "ampl_models")


@dataclass
class BatchResult:
    assignment: dict            # m -> sorted list of allocated QPU ids ([] if unassigned)
    k: dict                     # m -> partition count (0 if unassigned)
    objective: float
    zeta: int                   # zeta value that yielded feasibility
    solve_time: float           # wall-clock seconds spent inside solve()


@dataclass
class SingleResult:
    qpus: list
    objective: float
    solve_time: float
    feasible: bool = True


class MilpSolver:
    def __init__(self, solver: str | None = None):
        self._env = Environment(AMPL_DIR)
        self.solver = solver or os.path.join(AMPL_DIR, "cplex")
        self.total_solve_time = 0.0
        self.n_solves = 0

    def _fresh(self, model_file: str) -> AMPL:
        # The short-term AMPL lease renews over the internet; a transient
        # network drop raises "License not valid". Retry for up to ~1 h so
        # overnight experiment grids survive brief outages.
        for attempt in range(30):
            try:
                ampl = AMPL(self._env)
                break
            except SystemError as exc:
                if "License" not in str(exc) or attempt == 29:
                    raise
                time.sleep(120)
        ampl.set_option("solver", self.solver)
        # These instances (weak LP bound) are quick to solve but very slow to
        # PROVE optimal: the optimum incumbent shows up in <45s even when the
        # bound needs 10+ min (both CPLEX and Gurobi). We accept the incumbent
        # at the time limit; threads=3 leaves headroom for parallel workers.
        # The greedy warm start we set on r/y is used by CPLEX automatically
        # (an incumbent hint); without it the solution can leave a high-nu
        # circuit (QFT) on an expensive cross-pod pair, inflating its JET.
        # NOTE: CPLEX 22.2 (AMPL driver) removed the old "mipstartvalue" key
        # and errors out on it, so it is no longer passed here.
        # QDC_MILP_TIMELIMIT overrides the limit (pytket experiments only need
        # a good allocation, not proven-optimal, so run them at ~15 s).
        tl = os.environ.get("QDC_MILP_TIMELIMIT", "45")
        ampl.set_option("cplex_options",
                        f"mipgap=0.01 timelimit={tl} mipemphasis=1 threads=3")
        ampl.read(os.path.join(_MODEL_DIR, model_file))
        return ampl

    @staticmethod
    def _set_links(ampl: AMPL, network, qpus: list):
        t = {(j1, j2): (0.0 if j1 == j2 else network.latency(j1, j2))
             for j1 in qpus for j2 in qpus}
        f = {(j1, j2): (1.0 if j1 == j2 else network.fidelity(j1, j2))
             for j1 in qpus for j2 in qpus}
        ampl.get_parameter("T").set_values(t)
        ampl.get_parameter("F").set_values(f)

    # ------------------------------------------------------------------ batch
    def _greedy_batch_start(self, circuits: dict, network, available: list,
                            nu: dict) -> dict:
        """Greedy warm start: circuits in descending nu (connectivity) order
        each take their cheapest capacity-feasible QPU combo. -> {m: [qpus]}"""
        free = set(available)
        alloc = {}
        order = sorted(circuits, key=lambda m: -nu.get((m, 2), 0.0))
        for m in order:
            w, kmax = circuits[m]
            best = None
            for k in range(1, kmax + 1):
                for combo in combinations(sorted(free), k):
                    if sum(network.capacities[j] for j in combo) < w:
                        continue
                    cost = nu.get((m, k), 0.0) * sum(
                        w * network.latency(a, b) + (1 - network.fidelity(a, b))
                        for a, b in combinations(combo, 2))
                    key = (cost, sum(network.capacities[j] for j in combo))
                    if best is None or key < best[0]:
                        best = (key, list(combo))
                if best is not None and k == 1:
                    break  # a zero-cost single-QPU fit cannot be beaten
            if best is not None:
                alloc[m] = best[1]
                free -= set(best[1])
        return alloc

    def solve_batch(self, circuits: dict, network, available: list,
                    nu: dict, zeta: int | None = None) -> BatchResult:
        """Formulation 1. circuits: m -> (w_m, Kmax_m); nu: (m, k) -> nu_mk.

        Implements the adaptive-zeta fallback: start at len(circuits) and decrement
        until feasible (paper Sec. III-A).
        """
        ms = sorted(circuits)
        ampl = self._fresh("formulation1.mod")
        ampl.get_set("M").set_values(ms)
        ampl.get_set("J").set_values(available)
        ampl.get_parameter("Kmax").set_values({m: circuits[m][1] for m in ms})
        ampl.get_parameter("w").set_values({m: circuits[m][0] for m in ms})
        ampl.get_parameter("N").set_values(
            {j: network.capacities[j] for j in available})
        ampl.get_parameter("s").set_values({j: 1 for j in available})
        self._set_links(ampl, network, available)
        ampl.get_parameter("nu").set_values(
            {(m, k): nu[(m, k)] for m in ms for k in range(1, circuits[m][1] + 1)})

        # greedy warm start on r / y (CPLEX picks it up via mipstartvalue=1)
        alloc = self._greedy_batch_start(circuits, network, available, nu)
        ampl.get_variable("r").set_values(
            {(m, j): (1 if j in alloc.get(m, []) else 0)
             for m in ms for j in available})
        ampl.get_variable("y").set_values(
            {(m, k): (1 if len(alloc.get(m, [])) == k else 0)
             for m in ms for k in range(1, circuits[m][1] + 1)})

        zeta_val = len(ms) if zeta is None else zeta
        while zeta_val >= 0:
            ampl.get_parameter("zeta").set_values([zeta_val])
            t0 = time.perf_counter()
            ampl.solve(verbose=False)
            dt = time.perf_counter() - t0
            self.total_solve_time += dt
            self.n_solves += 1
            if ampl.solve_result in ("solved", "limit"):
                r = ampl.get_variable("r").get_values().to_dict()
                y = ampl.get_variable("y").get_values().to_dict()
                # a "limit" result without a true incumbent yields all-zero
                # variables; verify the assignment count before accepting
                if sum(1 for v in y.values() if v > 0.5) >= zeta_val:
                    assignment = {m: sorted(j for (mm, j), v in r.items()
                                            if mm == m and v > 0.5) for m in ms}
                    kcount = {m: next((int(k) for (mm, k), v in y.items()
                                       if mm == m and v > 0.5), 0) for m in ms}
                    return BatchResult(assignment, kcount,
                                       ampl.get_objective("C").value(),
                                       zeta_val, dt)
            zeta_val -= 1
        raise RuntimeError("Formulation 1 infeasible even with zeta = 0")

    # ----------------------------------------------------------------- single
    def solve_single(self, w_m: int, k_max: int, network,
                     available: list) -> SingleResult:
        """Formulation 2 (AssignQCirc in Algorithms 3-4)."""
        ampl = self._fresh("formulation2.mod")
        ampl.get_set("J").set_values(available)
        ampl.get_parameter("Kmax").set_values([k_max])
        ampl.get_parameter("wm").set_values([w_m])
        ampl.get_parameter("N").set_values(
            {j: network.capacities[j] for j in available})
        ampl.get_parameter("s").set_values({j: 1 for j in available})
        self._set_links(ampl, network, available)
        t0 = time.perf_counter()
        ampl.solve(verbose=False)
        dt = time.perf_counter() - t0
        self.total_solve_time += dt
        self.n_solves += 1
        if ampl.solve_result not in ("solved", "limit"):
            return SingleResult([], float("inf"), dt, feasible=False)
        r = ampl.get_variable("r").get_values().to_dict()
        qpus = sorted(int(j) for j, v in r.items() if v > 0.5)
        if not qpus:  # "limit" without incumbent
            return SingleResult([], float("inf"), dt, feasible=False)
        return SingleResult(qpus, ampl.get_objective("C").value(), dt)
