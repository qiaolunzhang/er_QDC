"""pytket-dqc based scheduling-partitioning experiments (paper Fig. 11, Table III).

Six configurations (paper Sec. IV-A2(b)):
  Pytket-PA / Pytket-PH : pytket-dqc native placement over the FULL network,
                          circuits processed sequentially (no contention logic)
  Single+PA / Single+PH : our Single-QCirc scheduler picks the QPU subset,
                          pytket-dqc partitions within it
  Batch+PA / Batch+PH   : same with Batch-QCirc (alpha = 0.55)

Grid: Sc1/Sc2/Sc3 x M in {12,20,28} x seeds 0..9. Results under results/pytket/.

Metrics:
  ebits      = pytket-dqc distribution cost (hypergraph ebit count, as in paper)
  partitions = number of servers actually used by the placement
  makespan   = replay of the schedule where each circuit occupies the servers of
               its pytket placement and lasts its layered JET (Eq. 9) computed
               from that placement (documented approximation: JET counts remote
               gates individually, while the ebits metric uses pytket's
               hyperedge cost which can merge them).

The pytket calls run in the py3.10 conda env via src/qdc_scheduler/pytket_worker.py
(one batched subprocess call per run).

Run:  python -m experiments.run_pytket_experiments [--scenario Sc3] [--configs ...]
"""

import argparse
import json
import os
import pickle
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from qdc_scheduler.mapping import jet_from_placement
from qdc_scheduler.milp import MilpSolver
from qdc_scheduler.network import DQCNetwork
from qdc_scheduler.regression import fit_all
from qdc_scheduler.simulator import Simulator
from qdc_scheduler.workload import generate_qc_set

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results", "pytket")
WORKER = os.path.join(os.path.dirname(__file__), "..", "src", "qdc_scheduler",
                      "pytket_worker.py")
PY310 = "/Users/qiaolun/miniconda3/envs/pytket_dqc/bin/python"
CONFIGS = ["Pytket-PA", "Pytket-PH", "Single+PA", "Single+PH",
           "Batch+PA", "Batch+PH"]


def scheduler_assignments(config, net, circuits, nu_models):
    """-> {m: [qpu, ...]} allocated subsets (full network for Pytket-*)."""
    if config.startswith("Pytket"):
        return {m: list(range(net.J)) for m in range(len(circuits))}
    sim = Simulator(net, circuits, nu_models, solver=MilpSolver())
    run = (sim.run_single() if config.startswith("Single")
           else sim.run_batch(alpha=0.55, beta=0.85))
    assign = {c.m: c.qpus for c in run.scheduled}
    # every circuit must have an allocation; fall back to the full network
    for m in range(len(circuits)):
        assign.setdefault(m, list(range(net.J)))
    return assign


def distribute_all(circuits, assignments, net, distributor, seed):
    jobs = [{"ctype": circuits[m].ctype, "width": circuits[m].width,
             "server_qubits": {str(j): net.capacities[j]
                               for j in assignments[m]},
             "distributor": distributor, "seed": seed}
            for m in range(len(circuits))]
    proc = subprocess.run([PY310, WORKER], input=json.dumps({"jobs": jobs}),
                          capture_output=True, text=True, timeout=7200)
    if proc.returncode != 0:
        raise RuntimeError(f"pytket worker failed: {proc.stderr[-2000:]}")
    return json.loads(proc.stdout.strip().splitlines()[-1])


def replay_makespan(circuits, placements, net):
    """FIFO replay: each circuit starts when all its servers are free."""
    free = {j: 0.0 for j in range(net.J)}
    finish_all = 0.0
    jets = []
    for m, circ in enumerate(circuits):
        qpu_of_qubit = {int(q): int(s) for q, s in placements[m].items()}
        jet, _, _ = jet_from_placement(circ, qpu_of_qubit, net)
        servers = sorted(set(qpu_of_qubit.values()))
        start = max(free[j] for j in servers)
        for j in servers:
            free[j] = start + jet
        finish_all = max(finish_all, start + jet)
        jets.append(jet)
    return finish_all, jets


def run_one(scenario, m_total, seed, config, nu_models):
    net = DQCNetwork(capacity_seed=seed)
    circuits = generate_qc_set(scenario, m_total, seed=seed)
    assignments = scheduler_assignments(config, net, circuits, nu_models)
    distributor = config.split("P")[-1]  # "A" or "H"
    results = distribute_all(circuits, assignments, net,
                             "PA" if distributor == "A" else "PH", seed)
    placements = [r["placement"] for r in results]
    makespan, jets = replay_makespan(circuits, placements, net)
    by_type_e, by_type_j = {}, {}
    for m, circ in enumerate(circuits):
        by_type_e.setdefault(circ.ctype, []).append(results[m]["ebits"])
        by_type_j.setdefault(circ.ctype, []).append(jets[m])
    return {
        "ebits_per_qcirc": float(np.mean([r["ebits"] for r in results])),
        "partitions_per_qcirc": float(np.mean([len(r["servers_used"])
                                               for r in results])),
        "makespan": makespan,
        "throughput": m_total / makespan,
        "ebits_by_type": {t: float(np.mean(v)) for t, v in by_type_e.items()},
        "jet_by_type": {t: float(np.mean(v)) for t, v in by_type_j.items()},
        "assignments": assignments,
        "placements": placements,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default=None, choices=["Sc1", "Sc2", "Sc3"])
    ap.add_argument("--m", default=None)
    ap.add_argument("--seeds", default=None)
    ap.add_argument("--configs", default=None,
                    help="comma list from: " + ",".join(CONFIGS))
    args = ap.parse_args()
    scenarios = [args.scenario] if args.scenario else ["Sc1", "Sc2", "Sc3"]
    m_values = ([int(v) for v in args.m.split(",")] if args.m
                else [12, 20, 28])
    if args.seeds:
        lo, hi = args.seeds.split("-")
        seeds = range(int(lo), int(hi) + 1)
    else:
        seeds = range(10)
    configs = args.configs.split(",") if args.configs else CONFIGS

    os.makedirs(RESULTS_DIR, exist_ok=True)
    nu_models = fit_all(k_values=range(2, 5))
    for scenario in scenarios:
        for m_total in m_values:
            for seed in seeds:
                for config in configs:
                    tag = f"{scenario}_M{m_total}_seed{seed}_{config}"
                    path = os.path.join(RESULTS_DIR, tag + ".pkl")
                    if os.path.exists(path):
                        continue
                    t0 = time.time()
                    s = run_one(scenario, m_total, seed, config, nu_models)
                    s["config"] = {"scenario": scenario, "M": m_total,
                                   "seed": seed, "scheme": config}
                    with open(path, "wb") as f:
                        pickle.dump(s, f)
                    print(f"{tag}: ebits={s['ebits_per_qcirc']:.2f} "
                          f"parts={s['partitions_per_qcirc']:.2f} "
                          f"mk={s['makespan']:.4f} ({time.time()-t0:.0f}s)",
                          flush=True)
    print("all done")


if __name__ == "__main__":
    main()
