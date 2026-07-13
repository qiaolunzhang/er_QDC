"""Table IV: average MILP solver runtime per call, Single vs Batch (alpha=0.55).

Aggregates solver_time / n_solves from the results produced by
run_kl_experiments.py (Sc.1, Sc.2) and, when available, the Sc.3 pytket runs.
Paper values (Gurobi 11, Intel 2.4 GHz): Single ~0.006 s; Batch 3.41/2.93/4.14 s
for Sc.1/Sc.2/Sc.3 -> we compare ratios/trends only (different solver + hardware).

Run:  python -m experiments.run_table4_runtime
"""

import glob
import os
import pickle
import sys
from collections import defaultdict

import numpy as np

RESULTS_KL = os.path.join(os.path.dirname(__file__), "..", "results", "kl")


def main():
    acc = defaultdict(list)  # (scheme, scenario) -> per-call times
    for path in glob.glob(os.path.join(RESULTS_KL, "*.pkl")):
        with open(path, "rb") as f:
            s = pickle.load(f)
        cfg = s["config"]
        if cfg["scheme"] not in ("Single", "Batch_a0.55"):
            continue
        if s["n_solves"]:
            acc[(cfg["scheme"], cfg["scenario"])].append(
                s["solver_time"] / s["n_solves"])
    print(f"{'scheme':>12} {'scenario':>9} {'avg s/solve':>12} {'runs':>5}")
    for (scheme, scen), vals in sorted(acc.items()):
        print(f"{scheme:>12} {scen:>9} {np.mean(vals):12.4f} {len(vals):5d}")
    print("\npaper (Gurobi): Single ~0.006s; Batch(0.55) Sc1=3.41 Sc2=2.93 Sc3=4.14")


if __name__ == "__main__":
    main()
