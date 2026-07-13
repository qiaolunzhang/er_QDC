"""Fig. 10: makespan vs optical switch loss (0.5 / 1 / 2 dB), Sc.2, alpha=0.55.

Schemes: CA-B, Single-QCirc, Batch-QCirc(alpha=0.55). M in {12,20,28,36}, 10 seeds.
Results pickled per-combination under results/fig10/.

The loss = 0.5 dB case is identical in configuration to the Sc2 runs of
run_kl_experiments; use --reuse-kl to copy those results instead of re-running.

Run:  python -m experiments.run_fig10_switch_loss [--loss 1.0,2.0] [--reuse-kl]
"""

import argparse
import glob
import os
import pickle
import shutil
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from qdc_scheduler.metrics import summarise
from qdc_scheduler.milp import MilpSolver
from qdc_scheduler.network import DQCNetwork
from qdc_scheduler.regression import fit_all
from qdc_scheduler.simulator import Simulator
from qdc_scheduler.workload import generate_qc_set

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results", "fig10")
LOSSES = [0.5, 1.0, 2.0]
SCHEMES = ["CAB", "Single", "Batch_a0.55"]


def reuse_kl_for_half_db():
    """Copy Sc2 CAB/Single/Batch_a0.55 results from results/kl as loss=0.5."""
    kl_dir = os.path.join(os.path.dirname(__file__), "..", "results", "kl")
    n = 0
    for path in glob.glob(os.path.join(kl_dir, "Sc2_*.pkl")):
        with open(path, "rb") as f:
            s = pickle.load(f)
        c = s["config"]
        if c["scheme"] not in SCHEMES:
            continue
        s["config"] = {"loss": 0.5, "M": c["M"], "seed": c["seed"],
                       "scheme": c["scheme"]}
        tag = f"loss0.5_M{c['M']}_seed{c['seed']}_{c['scheme']}"
        with open(os.path.join(RESULTS_DIR, tag + ".pkl"), "wb") as f:
            pickle.dump(s, f)
        n += 1
    print(f"reused {n} kl results as loss=0.5")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--loss", default=None, help="comma list, e.g. 1.0,2.0")
    ap.add_argument("--schemes", default=None)
    ap.add_argument("--reuse-kl", action="store_true")
    args = ap.parse_args()
    global SCHEMES
    losses = [float(v) for v in args.loss.split(",")] if args.loss else LOSSES
    if args.schemes:
        SCHEMES = [s for s in SCHEMES if s in set(args.schemes.split(","))]
    os.makedirs(RESULTS_DIR, exist_ok=True)
    if args.reuse_kl:
        reuse_kl_for_half_db()
    nu_models = fit_all(k_values=range(2, 5))
    for loss in losses:
        for m_total in [12, 20, 28, 36]:
            for seed in range(10):
                for scheme in SCHEMES:
                    tag = f"loss{loss}_M{m_total}_seed{seed}_{scheme}"
                    path = os.path.join(RESULTS_DIR, tag + ".pkl")
                    if os.path.exists(path):
                        continue
                    net = DQCNetwork(capacity_seed=seed, switch_loss_db=loss)
                    circuits = generate_qc_set("Sc2", m_total, seed=seed)
                    sim = Simulator(net, circuits, nu_models, solver=MilpSolver())
                    t0 = time.time()
                    if scheme == "CAB":
                        run = sim.run_capacity()
                    elif scheme == "Single":
                        run = sim.run_single()
                    else:
                        run = sim.run_batch(alpha=0.55, beta=0.85)
                    s = summarise(run)
                    s["config"] = {"loss": loss, "M": m_total, "seed": seed,
                                   "scheme": scheme}
                    with open(path, "wb") as f:
                        pickle.dump(s, f)
                    print(f"{tag}: makespan={s['makespan']:.4f} "
                          f"({time.time()-t0:.1f}s)", flush=True)
    print("all done")


if __name__ == "__main__":
    main()
