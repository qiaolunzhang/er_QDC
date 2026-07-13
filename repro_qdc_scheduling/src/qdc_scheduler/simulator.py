"""Event-driven scheduling simulator implementing the paper's Algorithms 1-4 and
the two baselines (R-B, CA-B).

Semantics (paper Sec. III):
- non-preemptive; a QPU hosts at most one circuit partition at a time;
- all M circuits are present at t = 0 in arrival order;
- a scheduled circuit occupies its allocated QPUs for its JET (Eq. 9), then frees
  them; makespan = completion time of the last circuit (all times / T_dec).

Policies:
  run_single   - Algorithm 4 (Formulation 2 per circuit, as resources free up)
  run_batch    - Algorithm 1 (SelectBatch -> Formulation 1 -> HandleOverflow ->
                 FillQPU -> TriggerNextCycle(alpha))
  run_random   - R-B baseline (random capacity-feasible allocation)
  run_capacity - CA-B baseline (knapsack: fewest QPUs, all-to-all assumption)
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field

import numpy as np

from .mapping import map_circuit
from .milp import MilpSolver

KMAX_DEFAULT = 4


@dataclass
class ScheduledCircuit:
    m: int
    ctype: str
    width: int
    qpus: list
    k: int
    start: float
    jet: float
    finish: float
    n_ebits: int
    ebits_by_ns: dict


@dataclass
class RunResult:
    scheduled: list               # list[ScheduledCircuit]
    makespan: float
    solver_time: float = 0.0
    n_solves: int = 0

    @property
    def throughput(self) -> float:
        return len(self.scheduled) / self.makespan


class Simulator:
    def __init__(self, network, circuits, nu_models, kmax: int = KMAX_DEFAULT,
                 solver: MilpSolver | None = None, fill_gamma: float = 5.0):
        self.net = network
        self.circuits = circuits          # arrival order
        self.nu_models = nu_models        # k -> NuModel (k = 2..)
        self.kmax = kmax
        self.solver = solver or MilpSolver()
        self.fill_gamma = fill_gamma      # threshold Gamma in Algorithm 3

    # ------------------------------------------------------------- helpers
    def _nu_table(self, ms: list) -> dict:
        nu = {}
        for m in ms:
            g = self.circuits[m].graph
            for k in range(1, self.kmax + 1):
                nu[(m, k)] = 0.0 if k == 1 else self.nu_models[k].nu(g)
        return nu

    def _nu2(self, m: int) -> float:
        """nu_m (k = 2) used as the connectivity score in Algorithm 3."""
        return self.nu_models[2].nu(self.circuits[m].graph)

    def _commit(self, m: int, qpus: list, t: float, out: list, free: dict):
        circ = self.circuits[m]
        mres = map_circuit(circ, qpus, self.net)
        finish = t + mres.jet
        out.append(ScheduledCircuit(m, circ.ctype, circ.width, sorted(qpus),
                                    len(qpus), t, mres.jet, finish,
                                    mres.n_ebits, mres.ebits_by_ns))
        for j in qpus:
            free[j] = finish

    @staticmethod
    def _idle(free: dict, t: float) -> list:
        return sorted(j for j, ft in free.items() if ft <= t + 1e-12)

    @staticmethod
    def _next_event(free: dict, t: float) -> float:
        future = [ft for ft in free.values() if ft > t + 1e-12]
        if not future:
            raise RuntimeError("deadlock: no future event")
        return min(future)

    def _result(self, out: list) -> RunResult:
        return RunResult(out, max(c.finish for c in out),
                         self.solver.total_solve_time, self.solver.n_solves)

    # --------------------------------------------- shared online-policy loop
    def _online_loop(self, alloc, backfill: bool = True) -> RunResult:
        """Common event loop for the online policies (Single / R-B / CA-B).

        alloc(m, idle) -> list of QPUs or None. With backfill=False the queue is
        strict FIFO: the head blocks until it can be assigned; with backfill=True
        any pending circuit may be scheduled whenever resources free up.
        """
        free = {j: 0.0 for j in range(self.net.J)}
        pending = list(range(len(self.circuits)))
        out, t = [], 0.0
        while pending:
            idle = self._idle(free, t)
            progressed = False
            for m in list(pending):
                sel = alloc(m, idle)
                if sel is not None:
                    self._commit(m, sel, t, out, free)
                    pending.remove(m)
                    idle = self._idle(free, t)
                    progressed = True
                elif not backfill:
                    break        # strict FIFO: head blocks the queue
            if pending and not progressed:
                t = self._next_event(free, t)
        return self._result(out)

    # ------------------------------------------------- Algorithm 4 (Single)
    def run_single(self, backfill: bool = True) -> RunResult:
        def alloc(m, idle):
            w = self.circuits[m].width
            if sum(self.net.capacities[j] for j in idle) < w:
                return None
            res = self.solver.solve_single(w, self.kmax, self.net, idle)
            return res.qpus if res.feasible else None
        return self._online_loop(alloc, backfill)

    # ------------------------------------------------- Algorithm 1 (Batch)
    def run_batch(self, alpha: float = 0.55, beta: float = 0.85) -> RunResult:
        free = {j: 0.0 for j in range(self.net.J)}
        pending = list(range(len(self.circuits)))   # arrival order
        out, t = [], 0.0
        c_tot = self.net.total_capacity
        while pending:
            # --- SelectBatch: accumulate by arrival until c_req exceeds
            # beta * (capacity of currently AVAILABLE QPUs); paper defines
            # c_tot = sum_j s_j N_j with s_j the availability flag, which is
            # what makes the expected batch size ~ beta*alpha*c_tot/E[w] (Eq. 10)
            idle = self._idle(free, t)
            c_avail = sum(self.net.capacities[j] for j in idle)
            batch, c_req = [], 0
            for m in pending:
                w = self.circuits[m].width
                if batch and c_req + w > beta * c_avail:
                    break
                batch.append(m)
                c_req += w
                if c_req > beta * c_avail:
                    break
            # --- AssignBatch (Formulation 1) on currently idle QPUs
            circs = {m: (self.circuits[m].width, self.kmax) for m in batch}
            bres = self.solver.solve_batch(circs, self.net, idle,
                                           self._nu_table(batch))
            assigned = [m for m in batch if bres.assignment[m]]
            for m in assigned:
                self._commit(m, bres.assignment[m], t, out, free)
                pending.remove(m)
            # --- HandleOverflow (Algorithm 2): EBT-sorted future reservation
            overflow = [m for m in batch if m not in assigned]
            for m in overflow:
                qpus, start = self._overflow_pick(m, free)
                self._commit(m, qpus, start, out, free)
                pending.remove(m)
            # --- FillQPU (Algorithm 3) on remaining idle QPUs
            idle = self._idle(free, t)
            avl = sum(self.net.capacities[j] for j in idle)
            if idle and pending:
                for m in list(pending):
                    w = self.circuits[m].width
                    if self._nu2(m) <= self.fill_gamma and w <= avl:
                        res = self.solver.solve_single(w, self.kmax, self.net, idle)
                        if res.feasible:
                            self._commit(m, res.qpus, t, out, free)
                            pending.remove(m)
                            idle = self._idle(free, t)
                            avl = sum(self.net.capacities[j] for j in idle)
            # --- TriggerNextCycle: wait until alpha * c_tot capacity is idle
            while pending:
                idle_cap = sum(self.net.capacities[j] for j in self._idle(free, t))
                if idle_cap >= alpha * c_tot:
                    break
                t = self._next_event(free, t)
        return self._result(out)

    def _overflow_pick(self, m: int, free: dict):
        """Algorithm 2: scan QPUs by ascending EBT for a capacity-feasible set.

        Within the earliest-EBT prefix that admits a feasible set, use the
        largest-capacity QPUs and the smallest partition count ("taking into
        account circuit constraints such as capacity and the maximum number of
        partitions") -- crucial for dense circuits (QFT), where scattering over
        many small QPUs explodes the ebit count.
        """
        w = self.circuits[m].width
        order = sorted(free, key=lambda j: (free[j], -self.net.capacities[j]))
        for prefix_len in range(1, len(order) + 1):
            prefix = order[:prefix_len]
            by_cap = sorted(prefix, key=lambda q: -self.net.capacities[q])
            for k in range(1, min(self.kmax, prefix_len) + 1):
                chosen = by_cap[:k]
                if sum(self.net.capacities[q] for q in chosen) >= w:
                    return chosen, max(free[q] for q in chosen)
        raise RuntimeError(f"overflow circuit {m} cannot fit anywhere")

    # ------------------------------------------------------- R-B baseline
    def run_random(self, seed: int = 0, backfill: bool = True) -> RunResult:
        rng = np.random.default_rng(seed)
        return self._online_loop(
            lambda m, idle: self._random_feasible(self.circuits[m].width, idle,
                                                  rng),
            backfill)

    def _random_feasible(self, w: int, idle: list, rng) -> list | None:
        """Random partition count k in {1..Kmax}, then k random QPUs, resampled
        until capacity-feasible (matches the paper's R-B whose average partition
        count is ~2.5 = E[uniform{1..4}])."""
        if sum(self.net.capacities[j] for j in idle) < w:
            return None
        for _ in range(200):
            k = int(rng.integers(1, self.kmax + 1))
            if k > len(idle):
                continue
            sel = [int(j) for j in rng.choice(idle, size=k, replace=False)]
            if sum(self.net.capacities[j] for j in sel) >= w:
                return sel
        return None

    # ------------------------------------------------------ CA-B baseline
    def run_capacity(self, backfill: bool = True) -> RunResult:
        return self._online_loop(
            lambda m, idle: self._min_count_alloc(self.circuits[m].width, idle),
            backfill)

    def _min_count_alloc(self, w: int, idle: list) -> list | None:
        """Knapsack baseline: fewest QPUs meeting capacity (link-agnostic).

        Enumerates subsets by increasing size (J <= 16, Kmax = 4); among equal
        sizes picks the lexicographically first feasible subset (arbitrary
        tie-break, as the baseline ignores link quality).
        """
        for k in range(1, self.kmax + 1):
            for combo in itertools.combinations(idle, k):
                if sum(self.net.capacities[j] for j in combo) >= w:
                    return list(combo)
        return None
