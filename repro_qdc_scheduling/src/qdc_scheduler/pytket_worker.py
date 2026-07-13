"""pytket-dqc bridge worker — runs inside the py3.10 `pytket_dqc` conda env.

Reads a JSON job from stdin, distributes the circuit with pytket-dqc, writes a
JSON result to stdout. Kept dependency-free of the main (py3.13) package.

Input JSON — either a single job or {"jobs": [job, ...]} (batched to amortise
the ~10 s interpreter/import startup):
  job = {"ctype": "QFT"|"DJ"|"WState"|"GHZ", "width": int,
         "server_qubits": {"0": 8, "1": 12, ...},   # QPU id -> capacity
         "distributor": "PA"|"PH", "seed": int}

Output JSON: one result per job (list iff input was batched):
  {"ebits": int,                    # distribution cost (ebit count)
   "placement": {qubit: server},    # circuit qubit -> server id
   "servers_used": [int, ...]}
"""

import json
import sys

from pytket import Circuit
from pytket_dqc import DQCPass, NISQNetwork
from pytket_dqc.allocators import Ordered
from pytket_dqc.distributors import (PartitioningAnnealing,
                                     PartitioningHeterogeneous)


def build_circuit(ctype: str, w: int) -> Circuit:
    """Same gate sequences as qdc_scheduler.circuits (graph-model verified)."""
    c = Circuit(w)
    if ctype == "GHZ":
        c.H(0)
        for i in range(w - 1):
            c.CX(i, i + 1)
    elif ctype == "WState":
        c.Ry(0.3, 0)
        for i in range(w - 1):
            c.CRy(0.4, i, i + 1)
            c.CX(i + 1, i)
    elif ctype == "DJ":
        for q in range(w):
            c.H(q)
        for i in range(1, w):
            c.CX(i, 0)
        for q in range(1, w):
            c.H(q)
    elif ctype == "QFT":
        for i in range(w):
            c.H(i)
            for j in range(i + 1, w):
                c.CU1(1.0 / 2 ** (j - i), j, i)
    else:
        raise ValueError(ctype)
    return c


def run_job(job: dict) -> dict:
    # pytket-dqc's allocators require server IDs 0..k-1; our QPU ids may be
    # non-contiguous (e.g. {3,13,14}). Relabel to 0..k-1 and keep a reverse map.
    real_ids = sorted(int(k) for k in job["server_qubits"])
    to_real = {i: real_ids[i] for i in range(len(real_ids))}
    caps = {i: int(job["server_qubits"][str(real_ids[i])])
            for i in range(len(real_ids))}
    servers = sorted(caps)
    # A circuit allocated to a single server needs no distribution (0 ebits);
    # pytket-dqc's NISQNetwork requires >= 2 connected servers, so short-circuit.
    if len(servers) <= 1:
        s = to_real.get(0, 0)
        return {"ebits": 0, "placement": {q: s for q in range(job["width"])},
                "servers_used": [s]}

    circ = build_circuit(job["ctype"], job["width"])
    DQCPass().apply(circ)
    offsets, total = {}, 0
    for s in servers:
        offsets[s] = total
        total += caps[s]
    server_qubits = {s: list(range(offsets[s], offsets[s] + caps[s]))
                     for s in servers}
    coupling = [[a, b] for i, a in enumerate(servers) for b in servers[i + 1:]]
    network = NISQNetwork(coupling, server_qubits)

    # Calibrated settings (see AI_GUIDE/RESULTS_COMPARISON.md): default PA
    # (Random init) badly under-converges on 16 servers, and default PH
    # refinement leaves circuits spread over 4-5 servers -- both far worse
    # than the paper's reported baselines. Ordered init / stronger boundary
    # reallocation bring them to (slightly better than) the paper's level.
    if job["distributor"] == "PA":
        distribution = PartitioningAnnealing().distribute(
            circ, network, seed=job.get("seed", 0),
            initial_place_method=Ordered())
    else:
        distribution = PartitioningHeterogeneous().distribute(
            circ, network, seed=job.get("seed", 0),
            num_rounds=100, stop_parameter=0.0)

    placement = distribution.placement.placement  # hypergraph vertex -> server
    n_qubits = job["width"]
    # map internal server 0..k-1 back to the real QPU ids
    qubit_placement = {v: to_real[s] for v, s in placement.items()
                       if v < n_qubits}
    servers_used = sorted(set(qubit_placement.values()))
    return {
        "ebits": int(distribution.cost()),
        "placement": {int(k): int(v) for k, v in qubit_placement.items()},
        "servers_used": [int(s) for s in servers_used],
    }


def main():
    payload = json.load(sys.stdin)
    if "jobs" in payload:
        print(json.dumps([run_job(j) for j in payload["jobs"]]))
    else:
        print(json.dumps(run_job(payload)))


if __name__ == "__main__":
    main()
