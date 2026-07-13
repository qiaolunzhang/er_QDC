"""K-L based scheduling-partitioning experiments (paper Fig. 7, 8, 9 + Table IV).

Grid: scenario {Sc1, Sc2} x M {12,20,28,36} x seed {0..9} x scheme
  schemes: RB, CAB, Single, Batch(alpha in {0.55, 0.65, 0.75})

Each (scenario, M, seed, scheme) result is pickled individually under
results/kl/, so interrupted runs resume where they left off (generate-once /
load-thereafter, like the reference project).

Run:  python -m experiments.run_kl_experiments [--quick]
"""

import argparse
import os
import pickle
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from qdc_scheduler.metrics import summarise
from qdc_scheduler.milp import MilpSolver
from qdc_scheduler.network import DQCNetwork
from qdc_scheduler.regression import fit_all
from qdc_scheduler.simulator import Simulator
from qdc_scheduler.workload import generate_qc_set

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results", "kl")

SCHEMES = [
    ("RB", {}),
    ("CAB", {}),
    ("Single", {}),
    ("Batch_a0.55", {"alpha": 0.55}),
    ("Batch_a0.65", {"alpha": 0.65}),
    ("Batch_a0.75", {"alpha": 0.75}),
]


def run_one(scenario, m_total, seed, scheme, params, nu_models):
    net = DQCNetwork(capacity_seed=seed)
    circuits = generate_qc_set(scenario, m_total, seed=seed)
    sim = Simulator(net, circuits, nu_models, solver=MilpSolver())
    if scheme == "RB":
        run = sim.run_random(seed=seed)
    elif scheme == "CAB":
        run = sim.run_capacity()
    elif scheme == "Single":
        run = sim.run_single()
    else:
        run = sim.run_batch(alpha=params["alpha"], beta=0.85)
    return summarise(run)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true",
                    help="small grid for smoke testing (M=12, 2 seeds)")
    ap.add_argument("--scenario", default=None, choices=["Sc1", "Sc2"])
    ap.add_argument("--m", default=None,
                    help="comma-separated M values, e.g. 12,20")
    ap.add_argument("--seeds", default=None, help="seed range, e.g. 0-9")
    ap.add_argument("--schemes", default=None,
                    help="comma-separated scheme names, e.g. RB,CAB,Single")
    args = ap.parse_args()

    global SCHEMES
    scenarios = [args.scenario] if args.scenario else ["Sc1", "Sc2"]
    m_values = [12] if args.quick else [12, 20, 28, 36]
    seeds = range(2) if args.quick else range(10)
    if args.m:
        m_values = [int(v) for v in args.m.split(",")]
    if args.seeds:
        lo, hi = args.seeds.split("-")
        seeds = range(int(lo), int(hi) + 1)
    if args.schemes:
        wanted = set(args.schemes.split(","))
        SCHEMES = [(n, p) for n, p in SCHEMES if n in wanted]

    os.makedirs(RESULTS_DIR, exist_ok=True)
    nu_models = fit_all(k_values=range(2, 5))

    total = len(scenarios) * len(m_values) * len(list(seeds)) * len(SCHEMES)
    done = 0
    for scenario in scenarios:
        for m_total in m_values:
            for seed in seeds:
                for scheme, params in SCHEMES:
                    done += 1
                    tag = f"{scenario}_M{m_total}_seed{seed}_{scheme}"
                    path = os.path.join(RESULTS_DIR, tag + ".pkl")
                    if os.path.exists(path):
                        continue
                    t0 = time.time()
                    summary = run_one(scenario, m_total, seed, scheme, params,
                                      nu_models)
                    summary["config"] = {"scenario": scenario, "M": m_total,
                                         "seed": seed, "scheme": scheme, **params}
                    with open(path, "wb") as f:
                        pickle.dump(summary, f)
                    print(f"[{done}/{total}] {tag}: makespan="
                          f"{summary['makespan']:.4f} ebits/qc="
                          f"{summary['ebits_per_qcirc']:.2f} "
                          f"({time.time()-t0:.1f}s)", flush=True)
    print("all done")


if __name__ == "__main__":
    main()
