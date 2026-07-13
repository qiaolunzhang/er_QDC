"""Circuit -> QPU mapping, ebit accounting, and the layered JET model (Eq. 9).

Given the QPUs allocated to a circuit (the scheduling decision), this module:
1. picks partition sizes (near-equal, repaired to respect QPU capacities),
2. partitions the circuit graph with K-L,
3. maps parts to the specific QPUs (best of all k! permutations, k <= 4,
   minimising total ebit latency),
4. derives ebit counts per link type and JET/T_dec via the layered model:
   JET/T_dec = N_LL * T_local/T_dec + sum_ns N_ebits(ns) * T_link_ns/T_dec.
Layers containing at least one remote gate contribute only their (sequential)
entanglement generation times; layers with exclusively local gates contribute one
T_local each.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import permutations

from .network import T_LOCAL_OVER_TDEC
from .partitioner import kway_partition


@dataclass
class MappingResult:
    qpu_of_qubit: dict            # qubit -> QPU id
    parts: dict                   # QPU id -> list of qubits
    n_ebits: int
    ebits_by_ns: dict             # n_switches -> ebit count
    jet: float                    # JET / T_dec


def _balanced_sizes(w: int, caps: list) -> list:
    """Near-equal sizes summing to w, each capped by the matching capacity.

    caps must be sorted descending; returned sizes align with caps.
    """
    k = len(caps)
    base, rem = divmod(w, k)
    sizes = [base + (1 if i < rem else 0) for i in range(k)]
    sizes.sort(reverse=True)
    # repair: push overflow from over-capacity slots into slots with slack
    for i in range(k):
        if sizes[i] > caps[i]:
            excess = sizes[i] - caps[i]
            sizes[i] = caps[i]
            for jdx in range(k):
                if jdx != i and excess > 0:
                    room = caps[jdx] - sizes[jdx]
                    take = min(room, excess)
                    sizes[jdx] += take
                    excess -= take
            if excess > 0:
                raise ValueError("allocated QPUs cannot hold the circuit")
    return sizes


def _maxfill_sizes(w: int, caps: list) -> list:
    """Fill the largest QPUs first (each part >= 1 qubit).

    For dense circuit graphs (QFT complete graph, DJ star) this minimises the
    cut: e.g. a 22-qubit QFT on 20+20 splits (20, 2) -> 40 ebits instead of the
    balanced (11, 11) -> 121 ebits. The paper uses the balanced cut only as the
    nu_mk ESTIMATE; the actual mapping is capacity-constrained K-L.
    """
    k = len(caps)
    remaining = w - k  # reserve one qubit per part
    if remaining < 0:
        raise ValueError("more QPUs than qubits")
    sizes = []
    for c in caps:
        take = min(c - 1, remaining)
        sizes.append(1 + take)
        remaining -= take
    if remaining > 0:
        raise ValueError("allocated QPUs cannot hold the circuit")
    return sizes


def _feasible_size_sweep(w: int, caps: list):
    """Yield feasible k part-size tuples from balanced to max-fill.

    caps sorted descending. Sweeps how much the first (largest) part takes,
    distributing the rest greedily; each part gets >= 1 qubit.
    """
    k = len(caps)
    seen = set()
    base = _balanced_sizes(w, caps)
    seen.add(tuple(base))
    yield base
    try:
        mf = _maxfill_sizes(w, caps)
        if tuple(mf) not in seen:
            seen.add(tuple(mf))
            yield mf
    except ValueError:
        pass
    # sweep first-part size between balanced and its capacity
    lo = base[0]
    for first in range(lo + 1, caps[0] + 1):
        remaining = w - first
        if remaining < k - 1:
            break
        sizes = [first]
        for c in caps[1:]:
            take = min(c, max(1, remaining - (k - len(sizes) - 1)))
            sizes.append(take)
            remaining -= take
        if remaining == 0 and all(1 <= s <= c for s, c in zip(sizes, caps)):
            t = tuple(sizes)
            if t not in seen:
                seen.add(t)
                yield sizes


def _min_cut_partition(graph, k: int, caps: list, seed: int) -> list:
    from .partitioner import cut_size, kway_partition
    w = graph.number_of_nodes()
    best = None
    for sizes in _feasible_size_sweep(w, caps):
        parts = kway_partition(graph, k, seed=seed, sizes=sizes)
        c = cut_size(graph, parts)
        if best is None or c < best[0]:
            best = (c, parts)
    return best[1]


def map_circuit(circ, qpus: list, network, seed: int = 0) -> MappingResult:
    k = len(qpus)
    if k == 1:
        j = qpus[0]
        return MappingResult({q: j for q in range(circ.width)},
                             {j: list(range(circ.width))}, 0, {},
                             jet=len(circ.layers) * T_LOCAL_OVER_TDEC)

    qpus_desc = sorted(qpus, key=lambda j: -network.capacities[j])
    caps = [network.capacities[j] for j in qpus_desc]
    # Balanced (capacity-repaired) K-L, matching the paper's "iterative K-L
    # k-way partitioning" with "partitions of equal or nearly equal size".
    # This reproduces both Fig. 7 (ebits) and Fig. 8 (average JET). A min-cut
    # (unbalanced) variant undershoots the paper's ebit counts by ~40% and is
    # rejected; see PROGRESS_LOG 2026-07-13.
    sizes = _balanced_sizes(circ.width, caps)
    parts = kway_partition(circ.graph, k, seed=seed, sizes=sizes)

    # choose part -> QPU permutation minimising total ebit latency,
    # subject to part sizes fitting capacities
    wcut = {}  # (part_a, part_b) -> summed weight of crossing edges
    owner_part = {}
    for idx, part in enumerate(parts):
        for q in part:
            owner_part[q] = idx
    for u, v, d in circ.graph.edges(data=True):
        a, b = owner_part[u], owner_part[v]
        if a != b:
            key = (min(a, b), max(a, b))
            wcut[key] = wcut.get(key, 0) + d.get("weight", 1)

    best_perm, best_cost = None, None
    for perm in permutations(range(k)):  # parts[i] -> qpus_desc[perm[i]]
        if any(len(parts[i]) > caps[perm[i]] for i in range(k)):
            continue
        cost = sum(w * network.latency(qpus_desc[perm[a]], qpus_desc[perm[b]])
                   for (a, b), w in wcut.items())
        if best_cost is None or cost < best_cost:
            best_cost, best_perm = cost, perm

    qpu_of_part = {i: qpus_desc[best_perm[i]] for i in range(k)}
    qpu_of_qubit = {q: qpu_of_part[owner_part[q]] for q in range(circ.width)}

    jet, n_ebits, ebits_by_ns = jet_from_placement(circ, qpu_of_qubit, network)
    parts_by_qpu = {qpu_of_part[i]: sorted(parts[i]) for i in range(k)}
    return MappingResult(qpu_of_qubit, parts_by_qpu, n_ebits, ebits_by_ns, jet)


def jet_from_placement(circ, qpu_of_qubit: dict, network):
    """Layered JET model (Eq. 9) for an arbitrary qubit -> QPU placement.

    Returns (jet, n_ebits, ebits_by_ns). Layers with only local gates contribute
    one T_local each; every remote gate occurrence contributes its link latency
    (sequential entanglement generation).
    """
    n_ll = 0
    jet = 0.0
    n_ebits = 0
    ebits_by_ns = {}
    for layer in circ.layers:
        remote = [g for g in layer
                  if len(g) == 2 and qpu_of_qubit[g[0]] != qpu_of_qubit[g[1]]]
        if not remote:
            n_ll += 1
            continue
        for g in remote:
            ns = network.n_switches(qpu_of_qubit[g[0]], qpu_of_qubit[g[1]])
            jet += network.latency_by_ns[ns]
            ebits_by_ns[ns] = ebits_by_ns.get(ns, 0) + 1
            n_ebits += 1
    jet += n_ll * T_LOCAL_OVER_TDEC
    return jet, n_ebits, ebits_by_ns
