"""E-SL: switch-loss sensitivity -> results/switchloss.csv (mirror ref Fig.10).

The reference paper (Bahrani et al., Fig.10) sweeps optical-switch loss eta_s in {0.5,1,2} dB and
shows the batch scheduler's advantage grows with loss. We ask the analogous question for BSM
contention: does the BSM-aware admission gain of JointDQC persist (or strengthen) as switches get
lossier? Higher loss raises per-hop latency (T_link ~ 1/eta_s^{n_s}) and lowers fidelity, changing
the base cost -- but the CROSS-POD BSM load, and hence the serialisation the base model ignores, is
governed by the budget. We rerun OBL / JDQC / CAG at a tight budget across the three loss levels.

Run (from repo root):
  AMPL_DIR=/home/qiaolun/opt/ampl.linux-intel64 conda run -n rwa \
      python jointdqc/exp_switchloss.py --workload mixed dense --mb 8 \
      --loss 0.5 1 2 --budget 8 --seeds 0-9
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import sys

sys.path.insert(0, "src")
sys.path.insert(0, "jointdqc")

from qdc_scheduler.regression import fit_all
from fabric import Fabric
from solver import CongestSolver
import heuristic
import evaluator
from run_experiment import make_pool, parse_ints

BIG = 1e9
FIELDS = ["workload", "Mb", "seed", "loss_db", "budget_total", "scheme",
          "admitted", "core_load", "bsm_rounds", "eff_throughput", "base_cost", "solve_time"]


def bsm_rounds(load, btot):
    return max(1, math.ceil(load / btot)) if btot < 1e8 else 1


def row(wl, Mb, seed, loss, btot, scheme, cong, st):
    r = bsm_rounds(cong.core_load_total, btot)
    return dict(workload=wl, Mb=Mb, seed=seed, loss_db=loss, budget_total=btot, scheme=scheme,
                admitted=cong.n_assigned, core_load=round(cong.core_load_total, 3), bsm_rounds=r,
                eff_throughput=round(cong.n_assigned / r, 4), base_cost=round(cong.base_cost, 3),
                solve_time=round(st, 3))


def run(args):
    nu_models = fit_all(range(2, 5))
    exists = os.path.exists(args.out)
    fh = open(args.out, "a", newline="")
    writer = csv.DictWriter(fh, fieldnames=FIELDS)
    if not exists:
        writer.writeheader(); fh.flush()
    btot = float(args.budget)
    for wl in args.workload:
        for Mb in args.mb:
            for seed in parse_ints(args.seeds):
                circuits = make_pool(wl, args.scenario, Mb, seed)
                for loss in args.loss:
                    loss = float(loss)
                    # OBL: BSM-oblivious strong baseline (infinite core budget) at this loss level
                    fab_inf = Fabric(ncore=1, bcore=BIG, bagg=BIG,
                                     capacity_seed=seed, switch_loss_db=loss)
                    res_obl = CongestSolver(timelimit=args.timelimit).solve_admit(
                        circuits, fab_inf, nu_models)
                    c_obl = evaluator.evaluate(circuits, res_obl.alloc, fab_inf, nu_models)
                    writer.writerow(row(wl, Mb, seed, loss, btot, "OBL", c_obl, res_obl.solve_time))
                    # JDQC: hard BSM budget
                    fab = Fabric(ncore=1, bcore=btot, bagg=BIG,
                                 capacity_seed=seed, switch_loss_db=loss)
                    res = CongestSolver(timelimit=args.timelimit).solve_admit(
                        circuits, fab, nu_models)
                    c_jdqc = evaluator.evaluate(circuits, res.alloc, fab, nu_models)
                    writer.writerow(row(wl, Mb, seed, loss, btot, "JDQC", c_jdqc, res.solve_time))
                    # CAG greedy
                    import time as _t
                    t0 = _t.perf_counter()
                    alloc_cag = heuristic.solve_cag(circuits, fab, nu_models)
                    t_cag = _t.perf_counter() - t0
                    c_cag = evaluator.evaluate(circuits, alloc_cag, fab, nu_models)
                    writer.writerow(row(wl, Mb, seed, loss, btot, "CAG", c_cag, t_cag))
                    fh.flush()
                print(f"[ok] {wl} Mb={Mb} seed={seed}: loss sweep done", flush=True)
    fh.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workload", nargs="+", default=["mixed", "dense"])
    ap.add_argument("--scenario", default="Sc2")
    ap.add_argument("--mb", type=int, nargs="+", default=[8])
    ap.add_argument("--loss", nargs="+", default=[0.5, 1.0, 2.0])
    ap.add_argument("--budget", default=8)
    ap.add_argument("--seeds", default="0-9")
    ap.add_argument("--timelimit", type=int, default=12)
    ap.add_argument("--out", default="jointdqc/results/switchloss.csv")
    args = ap.parse_args()
    os.environ.setdefault("QDC_MILP_TIMELIMIT", str(args.timelimit))
    run(args)


if __name__ == "__main__":
    main()
