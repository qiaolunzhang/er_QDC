"""Workload generation (paper Sec. IV-A3).

A QC set of size M contains all four circuit types, each contributing 25%. Qubit
counts are drawn uniformly from type-specific ranges:

  Sc.1: R_GHZ = R_WState = [18,26], R_DJ = [14,22], R_QFT = [10,18]
  Sc.2: ranges shifted up by 4:    [22,30],         [18,26],        [14,22]
  Sc.3: R_QFT = R_DJ = [22,30], R_GHZ = R_WState = [24,32]  (partition-intensive)

Arrival order is a seeded random interleaving of the types.
"""

from __future__ import annotations

import numpy as np

from .circuits import make_circuit

SCENARIOS = {
    "Sc1": {"GHZ": (18, 26), "WState": (18, 26), "DJ": (14, 22), "QFT": (10, 18)},
    "Sc2": {"GHZ": (22, 30), "WState": (22, 30), "DJ": (18, 26), "QFT": (14, 22)},
    "Sc3": {"GHZ": (24, 32), "WState": (24, 32), "DJ": (22, 30), "QFT": (22, 30)},
}


def generate_qc_set(scenario: str, m_total: int, seed: int) -> list:
    """Return M circuits in arrival order (list of QuantumCircuit)."""
    ranges = SCENARIOS[scenario]
    assert m_total % 4 == 0, "M must be divisible by 4 (25% per type)"
    rng = np.random.default_rng(seed)
    types = [t for t in ranges for _ in range(m_total // 4)]
    rng.shuffle(types)
    circuits = []
    for ctype in types:
        lo, hi = ranges[ctype]
        # exclusive upper bound (numpy convention). Validated against the paper:
        # with w=22 QFTs included, any forced balanced split costs >= 121 ebits
        # (JET >= 0.68), contradicting the paper's Sc.2 Batch makespan ~0.6 and
        # JET_QFT ~ 0.115; with w <= 21 (110 ebits, JET 0.62 on a 1-switch link)
        # every reported number becomes consistent.
        w = int(rng.integers(lo, hi))
        circuits.append(make_circuit(ctype, w))
    return circuits
