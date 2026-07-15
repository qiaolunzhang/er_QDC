"""E-CB: the base cost objective is CONGESTION-BLIND -> results/congestion_blind.csv.

Claim (Section III-B / IV-B of the companion paper): the base paper's cost objective
(latency+infidelity, Bahrani et al. Formulation 1) has many equal-cost optima whose core
(cross-pod) BSM load differs by orders of magnitude, so an off-the-shelf base scheduler does
not CONTROL congestion. We prove this rigorously (not via solver-tie-break luck):

  1. Cmin = base optimum cost of a fixed instance (base Formulation 1, full admission).
  2. For a grid of cost tolerances eps, solve on the near-optimal face base_cost <= (1+eps)*Cmin:
       - minimise core load  (Dir=+1)  -> the best a congestion-aware tie-break could do
       - maximise core load  (Dir=-1)  -> the worst an oblivious solver could return
     The gap between max and min at small eps is the congestion the objective leaves free.

Run (from repo root):
  AMPL_DIR=/home/qiaolun/opt/ampl.linux-intel64 conda run -n rwa \
      python jointdqc/exp_congestion_blind.py --workload dense mixed --mb 8 --seeds 0-4
"""

from __future__ import annotations

import argparse
import csv
import os
import sys

sys.path.insert(0, "src")
sys.path.insert(0, "jointdqc")

from qdc_scheduler.regression import fit_all
from fabric import Fabric
from solver import CongestSolver
import evaluator
import heuristic
from run_experiment import make_pool, parse_ints

BIG = 1e9
EPS_GRID = [0.0, 0.001, 0.005, 0.01, 0.02, 0.05, 0.10]
FIELDS = ["workload", "Mb", "seed", "eps", "cmin", "cbudget",
          "load_min", "load_max", "cost_min", "cost_max"]


def run(args):
    nu_models = fit_all(range(2, 5))
    solver = CongestSolver(timelimit=args.timelimit)
    out = args.out
    exists = os.path.exists(out)
    fh = open(out, "a", newline="")
    writer = csv.DictWriter(fh, fieldnames=FIELDS)
    if not exists:
        writer.writeheader(); fh.flush()

    for wl in args.workload:
        for Mb in args.mb:
            for seed in parse_ints(args.seeds):
                circuits = make_pool(wl, args.scenario, Mb, seed)
                fab = Fabric(ncore=1, bcore=BIG, bagg=BIG, capacity_seed=seed)
                # Cmin = base-cost optimum at FULL admission (Formulation 1's objective). This is
                # exactly the cost the base scheduler targets; the costface model then reveals how
                # much core load is left UNCONTROLLED at that same cost.
                cmin = solver.costface_cmin(circuits, fab, nu_models)
                if cmin is None:
                    print(f"[skip] {wl} Mb={Mb} seed={seed}: full admission infeasible", flush=True)
                    continue
                for eps in EPS_GRID:
                    cb = cmin * (1.0 + eps) + 1e-9
                    lmin, cmn, ok1 = solver.solve_costface(circuits, fab, nu_models, cb, 1)
                    lmax, cmx, ok2 = solver.solve_costface(circuits, fab, nu_models, cb, -1)
                    if not (ok1 and ok2):
                        continue
                    writer.writerow(dict(workload=wl, Mb=Mb, seed=seed, eps=eps,
                                         cmin=round(cmin, 4), cbudget=round(cb, 4),
                                         load_min=round(lmin, 3), load_max=round(lmax, 3),
                                         cost_min=round(cmn, 4), cost_max=round(cmx, 4)))
                    fh.flush()
                    print(f"[ok] {wl} Mb={Mb} s={seed} eps={eps:.3f}: "
                          f"load {lmin:.1f}..{lmax:.1f} at cost<= {cb:.2f}", flush=True)
    fh.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workload", nargs="+", default=["dense", "mixed"])
    ap.add_argument("--scenario", default="Sc2")
    ap.add_argument("--mb", type=int, nargs="+", default=[8])
    ap.add_argument("--seeds", default="0-4")
    ap.add_argument("--timelimit", type=int, default=30)
    ap.add_argument("--out", default="jointdqc/results/congestion_blind.csv")
    args = ap.parse_args()
    os.environ.setdefault("QDC_MILP_TIMELIMIT", str(args.timelimit))
    run(args)


if __name__ == "__main__":
    main()
