"""AMPL + CPLEX driver for the JointDQC congestion-aware MILP (jointdqc_congest.mod).

Mirrors the base `qdc_scheduler.milp.MilpSolver` style (same AMPL/CPLEX setup, same result
dataclasses) so it is familiar and composable with the existing reproduction code. Adds the
fabric layer (per-switch BSM budgets + cross-pod core capacity) and an LP-relaxation solve that
yields a certified lower bound on the peak congestion -> the "certified optimality gap".
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from itertools import combinations

from amplpy import AMPL, Environment

AMPL_DIR = os.environ.get("AMPL_DIR", "/home/qiaolun/opt/ampl.linux-intel64")
_MODEL_DIR = os.path.join(os.path.dirname(__file__), "ampl_models")


@dataclass
class CongestResult:
    alloc: dict          # m -> sorted list of allocated QPU ids
    k: dict              # m -> partition count
    t: float             # peak normalised BSM utilisation (objective, minus tie-break)
    objective: float     # full objective value (t + eps*base_cost)
    zeta: int
    solve_time: float
    lp_bound: float = float("nan")   # LP-relaxation lower bound on t (filled by solve_lp)


class CongestSolver:
    def __init__(self, timelimit: int = 60):
        self._env = Environment(AMPL_DIR)
        self.solver = os.path.join(AMPL_DIR, "cplex")
        self.timelimit = int(os.environ.get("QDC_MILP_TIMELIMIT", timelimit))
        self.total_solve_time = 0.0
        self.n_solves = 0

    def _fresh(self, relax: bool = False) -> AMPL:
        ampl = AMPL(self._env)
        ampl.set_option("solver", self.solver)
        ampl.set_option("cplex_options",
                        f"mipgap=0.005 timelimit={self.timelimit} mipemphasis=0 threads=3")
        if relax:
            ampl.set_option("relax_integrality", 1)
        ampl.read(os.path.join(_MODEL_DIR, "jointdqc_congest.mod"))
        return ampl

    def _load(self, ampl: AMPL, circuits: dict, fabric, nu_models, zeta: int):
        ms = sorted(circuits)
        J = fabric.J
        kmax = {m: min(4, len(J)) for m in ms}
        ampl.get_set("M").set_values(ms)
        ampl.get_set("J").set_values(J)
        ampl.get_set("SW").set_values(fabric.edges + fabric.aggs)
        ampl.get_parameter("Kmax").set_values(kmax)
        ampl.get_parameter("w").set_values({m: circuits[m].width for m in ms})
        ampl.get_parameter("N").set_values({j: fabric.capacities[j] for j in J})
        ampl.get_parameter("s").set_values({j: 1 for j in J})
        t = {(a, b): (0.0 if a == b else fabric.latency(a, b)) for a in J for b in J}
        f = {(a, b): (1.0 if a == b else fabric.fidelity(a, b)) for a in J for b in J}
        ampl.get_parameter("T").set_values(t)
        ampl.get_parameter("F").set_values(f)
        nu = {(m, k): nu_models[k].nu(circuits[m].graph)
              for m in ms for k in range(2, kmax[m] + 1)}
        nu.update({(m, 1): 0.0 for m in ms})   # k=1 -> no cut
        ampl.get_parameter("nu").set_values(nu)
        # fabric
        ampl.get_parameter("Bcap").set_values({sw: fabric.bcap(sw)
                                               for sw in fabric.edges + fabric.aggs})
        inc, xpod = fabric.incidence()
        if inc:
            ampl.get_parameter("inc").set_values(inc)
        ampl.get_parameter("xpod").set_values(xpod)
        ampl.get_parameter("Ncore").set_values([fabric.ncore])
        ampl.get_parameter("Bcore").set_values([fabric.bcore])
        ampl.get_parameter("zeta").set_values([zeta])
        return ms

    def solve(self, circuits: dict, fabric, nu_models, zeta: int | None = None) -> CongestResult:
        """Solve the congestion MILP with adaptive-zeta fallback (like the base solver)."""
        ms = sorted(circuits)
        zeta_val = len(ms) if zeta is None else zeta
        while zeta_val >= 0:
            ampl = self._fresh(relax=False)
            self._load(ampl, circuits, fabric, nu_models, zeta_val)
            t0 = time.perf_counter()
            ampl.solve(verbose=False)
            dt = time.perf_counter() - t0
            self.total_solve_time += dt
            self.n_solves += 1
            if ampl.solve_result in ("solved", "limit"):
                y = ampl.get_variable("y").get_values().to_dict()
                if sum(1 for v in y.values() if v > 0.5) >= zeta_val or zeta_val == 0:
                    r = ampl.get_variable("r").get_values().to_dict()
                    alloc = {m: sorted(int(j) for (mm, j), v in r.items()
                                       if mm == m and v > 0.5) for m in ms}
                    kcount = {m: len(alloc[m]) for m in ms}
                    tval = ampl.get_variable("t").value()
                    return CongestResult(alloc, kcount, tval,
                                         ampl.get_objective("Peak").value(),
                                         zeta_val, dt)
            zeta_val -= 1
        raise RuntimeError("JointDQC congestion model infeasible even with zeta = 0")

    def _load_common(self, ampl, circuits, fabric, nu_models):
        """Set the sets/params shared by the congestion and admission models (no zeta)."""
        ms = sorted(circuits)
        J = fabric.J
        kmax = {m: min(4, len(J)) for m in ms}
        ampl.get_set("M").set_values(ms)
        ampl.get_set("J").set_values(J)
        ampl.get_set("SW").set_values(fabric.edges + fabric.aggs)
        ampl.get_parameter("Kmax").set_values(kmax)
        ampl.get_parameter("w").set_values({m: circuits[m].width for m in ms})
        ampl.get_parameter("N").set_values({j: fabric.capacities[j] for j in J})
        ampl.get_parameter("s").set_values({j: 1 for j in J})
        t = {(a, b): (0.0 if a == b else fabric.latency(a, b)) for a in J for b in J}
        f = {(a, b): (1.0 if a == b else fabric.fidelity(a, b)) for a in J for b in J}
        ampl.get_parameter("T").set_values(t)
        ampl.get_parameter("F").set_values(f)
        nu = {(m, k): nu_models[k].nu(circuits[m].graph)
              for m in ms for k in range(2, kmax[m] + 1)}
        nu.update({(m, 1): 0.0 for m in ms})
        ampl.get_parameter("nu").set_values(nu)
        ampl.get_parameter("Bcap").set_values({sw: fabric.bcap(sw)
                                               for sw in fabric.edges + fabric.aggs})
        inc, xpod = fabric.incidence()
        if inc:
            ampl.get_parameter("inc").set_values(inc)
        ampl.get_parameter("xpod").set_values(xpod)
        ampl.get_parameter("Ncore").set_values([fabric.ncore])
        ampl.get_parameter("Bcore").set_values([fabric.bcore])
        return ms

    def solve_admit(self, circuits: dict, fabric, nu_models) -> CongestResult:
        """Maximise admitted circuits subject to the hard BSM budget (jointdqc_admit.mod)."""
        ampl = AMPL(self._env)
        ampl.set_option("solver", self.solver)
        ampl.set_option("cplex_options",
                        f"mipgap=0.01 timelimit={self.timelimit} mipemphasis=1 threads=3")
        ampl.read(os.path.join(_MODEL_DIR, "jointdqc_admit.mod"))
        ms = self._load_common(ampl, circuits, fabric, nu_models)
        t0 = time.perf_counter()
        ampl.solve(verbose=False)
        dt = time.perf_counter() - t0
        self.total_solve_time += dt
        self.n_solves += 1
        if ampl.solve_result not in ("solved", "limit"):
            return CongestResult({m: [] for m in ms}, {m: 0 for m in ms}, 0.0, 0.0, 0, dt)
        r = ampl.get_variable("r").get_values().to_dict()
        alloc = {m: sorted(int(j) for (mm, j), v in r.items() if mm == m and v > 0.5)
                 for m in ms}
        kcount = {m: len(alloc[m]) for m in ms}
        admitted = sum(1 for m in ms if alloc[m])
        return CongestResult(alloc, kcount, float("nan"),
                             ampl.get_objective("Admitted").value(), admitted, dt)

    def _costface_ampl(self, circuits, fabric, nu_models):
        ampl = AMPL(self._env)
        ampl.set_option("solver", self.solver)
        ampl.set_option("cplex_options",
                        f"mipgap=0 timelimit={self.timelimit} mipemphasis=2 threads=3")
        ampl.read(os.path.join(_MODEL_DIR, "jointdqc_costface.mod"))
        self._load_common(ampl, circuits, fabric, nu_models)
        return ampl

    def costface_cmin(self, circuits, fabric, nu_models):
        """Base-cost optimum Cmin at FULL admission (objective CostObj). None if infeasible."""
        ampl = self._costface_ampl(circuits, fabric, nu_models)
        ampl.get_parameter("Cbudget").set_values([1e12])   # cost cap slack
        ampl.get_parameter("Dir").set_values([1])
        ampl.eval("objective CostObj;")
        t0 = time.perf_counter()
        ampl.solve(verbose=False)
        self.total_solve_time += time.perf_counter() - t0
        self.n_solves += 1
        if ampl.solve_result not in ("solved", "limit"):
            return None
        return ampl.get_variable("BaseCost").value()

    def solve_costface(self, circuits: dict, fabric, nu_models,
                       cbudget: float, direction: int = 1):
        """Probe the base-cost-optimal FACE (objective FaceObj of jointdqc_costface.mod).

        With full admission fixed, minimise (direction=+1) or maximise (direction=-1) the core
        (cross-pod) BSM load subject to base_cost <= cbudget. Returns (core_load, base_cost,
        feasible): the min/max core load achievable at essentially the base optimum is exactly
        the congestion the base objective fails to control. mipemphasis=2, mipgap=0 so the
        reported face extent is tight, not a solver artefact.
        """
        ampl = self._costface_ampl(circuits, fabric, nu_models)
        ampl.get_parameter("Cbudget").set_values([cbudget])
        ampl.get_parameter("Dir").set_values([direction])
        ampl.eval("objective FaceObj;")
        t0 = time.perf_counter()
        ampl.solve(verbose=False)
        self.total_solve_time += time.perf_counter() - t0
        self.n_solves += 1
        if ampl.solve_result not in ("solved", "limit"):
            return float("nan"), float("nan"), False
        return (ampl.get_variable("CoreLoad").value(),
                ampl.get_variable("BaseCost").value(), True)

    def solve_lp(self, circuits: dict, fabric, nu_models, zeta: int) -> float:
        """LP relaxation -> certified lower bound on the peak utilisation t."""
        ampl = self._fresh(relax=True)
        self._load(ampl, circuits, fabric, nu_models, zeta)
        t0 = time.perf_counter()
        ampl.solve(verbose=False)
        self.total_solve_time += time.perf_counter() - t0
        self.n_solves += 1
        if ampl.solve_result in ("solved", "limit"):
            return ampl.get_variable("t").value()
        return float("nan")
