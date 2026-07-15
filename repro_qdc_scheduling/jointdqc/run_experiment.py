"""Run the JointDQC BSM-aware-admission experiment grid -> results/jointdqc.csv.

Contribution under test (idea #4): the base DQC scheduler (Bahrani et al., Formulation 1) selects
and allocates a batch by QUBIT capacity only and is blind to optical-switch BSM (entanglement-swap)
capacity. In an over-subscribed data center this over-commits the shared switch fabric: remote gates
pile onto the core switches, whose finite BSM budget then serialises them. JointDQC makes BSM capacity
a first-class constraint and admits a fabric-feasible batch.

To compare fairly (removing the base cost-objective's congestion-indifference and solver-time
sensitivity), all schemes use the SAME admission-maximising objective; they differ ONLY in the BSM
budget constraint:
  OBL  : BSM-OBLIVIOUS strong baseline -- max admission, min-congestion tie-break, NO budget
         (solve_admit with an effectively infinite core budget). Budget-independent -> solved once.
  JDQC : JointDQC MILP -- max admission subject to a hard per-layer BSM budget (optimal). Per budget.
  CAG  : JointDQC BSM-aware greedy (scalable heuristic). Per budget.
All reuse the reproduction code (circuits, regression nu_mk, network) and AMPL+CPLEX.

Metric: effective throughput = admitted / BSM_rounds, BSM_rounds = ceil(core_load / B_tot) (>=1):
the serial entanglement-swap rounds the busiest core layer needs. OBL's allocation is budget-blind,
so its rounds grow as the budget tightens; JDQC/CAG cap the load at the budget.

Run from repo root:
  AMPL_DIR=... conda run -n rwa python jointdqc/run_experiment.py \
      --scenario Sc2 --mb 8 12 16 20 --seeds 0-9 --ncore 2 \
      --budgets 4 8 12 16 --timelimit 15
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import sys
import time

sys.path.insert(0, "src")
sys.path.insert(0, "jointdqc")

import numpy as np

from qdc_scheduler.workload import generate_qc_set
from qdc_scheduler.circuits import make_circuit
from qdc_scheduler.regression import fit_all
from fabric import Fabric
from solver import CongestSolver
import heuristic
import evaluator


def make_pool(workload, scenario, Mb, seed):
    """mixed -> the base paper's 25%-per-type workload; dense -> QFT/DJ only (high
    connectivity, wide enough to force splitting) -- the BSM-stressing regime."""
    if workload == "mixed":
        return {i: c for i, c in enumerate(generate_qc_set(scenario, Mb, seed=seed))}
    rng = np.random.default_rng(seed)
    types = (["QFT", "DJ"] * ((Mb + 1) // 2))[:Mb]
    rng.shuffle(types)
    return {i: make_circuit(t, int(rng.integers(22, 31))) for i, t in enumerate(types)}

FIELDS = ["workload", "scenario", "Mb", "seed", "ncore", "budget_total", "scheme",
          "admitted", "core_load", "bsm_rounds", "eff_throughput",
          "base_cost", "solve_time"]
BIG = 1e9


def parse_ints(spec):
    out = []
    for tok in str(spec).replace(",", " ").split():
        if "-" in tok:
            a, b = tok.split("-"); out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(tok))
    return out


def bsm_rounds(load, btot):
    return max(1, math.ceil(load / btot)) if btot < 1e8 else 1


def row(wl, scn, Mb, seed, ncore, btot, scheme, cong, st):
    r = bsm_rounds(cong.core_load_total, btot)
    return dict(workload=wl, scenario=scn, Mb=Mb, seed=seed, ncore=ncore, budget_total=btot,
                scheme=scheme, admitted=cong.n_assigned,
                core_load=round(cong.core_load_total, 3), bsm_rounds=r,
                eff_throughput=round(cong.n_assigned / r, 4),
                base_cost=round(cong.base_cost, 3), solve_time=round(st, 3))


def run(args):
    nu_models = fit_all(range(2, 5))
    budgets = [float(b) for b in args.budgets]
    exists = os.path.exists(args.out)
    fh = open(args.out, "a", newline="")
    writer = csv.DictWriter(fh, fieldnames=FIELDS)
    if not exists:
        writer.writeheader(); fh.flush()

    for ncore in args.ncore:
        for Mb in args.mb:
            for seed in parse_ints(args.seeds):
                circuits = make_pool(args.workload, args.scenario, Mb, seed)

                # OBL: BSM-oblivious strong baseline (infinite core budget) -> budget-independent.
                fab_inf = Fabric(ncore=ncore, bcore=BIG, bagg=BIG, capacity_seed=seed)
                res_obl = CongestSolver(timelimit=args.timelimit).solve_admit(circuits, fab_inf, nu_models)
                c_obl = evaluator.evaluate(circuits, res_obl.alloc, fab_inf, nu_models)

                for btot in budgets:
                    fab = Fabric(ncore=ncore, bcore=btot / ncore, bagg=BIG, capacity_seed=seed)
                    writer.writerow(row(args.workload, args.scenario, Mb, seed, ncore, btot,
                                        "OBL", c_obl, res_obl.solve_time))
                    res = CongestSolver(timelimit=args.timelimit).solve_admit(circuits, fab, nu_models)
                    c_jdqc = evaluator.evaluate(circuits, res.alloc, fab, nu_models)
                    writer.writerow(row(args.workload, args.scenario, Mb, seed, ncore, btot,
                                        "JDQC", c_jdqc, res.solve_time))
                    t0 = time.perf_counter()
                    alloc_cag = heuristic.solve_cag(circuits, fab, nu_models, zeta=None)
                    t_cag = time.perf_counter() - t0
                    c_cag = evaluator.evaluate(circuits, alloc_cag, fab, nu_models)
                    writer.writerow(row(args.workload, args.scenario, Mb, seed, ncore, btot,
                                        "CAG", c_cag, t_cag))
                    fh.flush()
                print(f"[ok] {args.workload} nc={ncore} Mb={Mb} seed={seed}: "
                      f"OBL adm={c_obl.n_assigned} L={c_obl.core_load_total:.1f}", flush=True)
    fh.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workload", default="mixed", choices=["mixed", "dense"])
    ap.add_argument("--scenario", default="Sc2")
    ap.add_argument("--mb", type=int, nargs="+", default=[8, 12, 16, 20])
    ap.add_argument("--seeds", default="0-9")
    ap.add_argument("--ncore", type=int, nargs="+", default=[2])
    ap.add_argument("--budgets", nargs="+", default=[4, 8, 12, 16])
    ap.add_argument("--timelimit", type=int, default=15)
    ap.add_argument("--out", default="jointdqc/results/jointdqc.csv")
    args = ap.parse_args()
    os.environ.setdefault("QDC_MILP_TIMELIMIT", str(args.timelimit))
    run(args)


if __name__ == "__main__":
    main()
