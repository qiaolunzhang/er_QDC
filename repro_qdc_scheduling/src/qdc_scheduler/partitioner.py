"""Balanced k-way graph partitioning via iterative Kernighan-Lin bisection.

The paper (Sec. III-A1 and IV-B) computes the balanced k-way cut size "via iterative
applications of the Kernighan-Lin (K-L) algorithm". We implement recursive KL
bisection: to obtain k (nearly) equal parts, split the node set into two groups with
target sizes proportional to ceil(k/2)/k and floor(k/2)/k, refine the split with a
classic swap-only KL pass (preserves the exact part sizes, unlike networkx's
implementation), then recurse on each side. Capacity-constrained variants pass
explicit target sizes.
"""

from __future__ import annotations

import networkx as nx


def _kl_bisect(g: nx.Graph, nodes: list, size_a: int, seed: int) -> tuple:
    """Split `nodes` into parts of exactly (size_a, len-size_a) minimising cut.

    Classic Kernighan-Lin: repeated passes of tentative best-gain pair swaps with
    locking; commit the best prefix of each pass while its cumulative gain > 0.
    Deterministic (sorted initial split, ties broken by node order).
    """
    nodes = sorted(nodes)
    part_a, part_b = set(nodes[:size_a]), set(nodes[size_a:])
    wgt = {v: {} for v in nodes}
    sub = g.subgraph(nodes)
    for u, v, d in sub.edges(data=True):
        w = d.get("weight", 1)
        wgt[u][v] = w
        wgt[v][u] = w

    def dval(v, own, other):
        return (sum(w for u, w in wgt[v].items() if u in other)
                - sum(w for u, w in wgt[v].items() if u in own))

    while True:
        d = {}
        for v in part_a:
            d[v] = dval(v, part_a, part_b)
        for v in part_b:
            d[v] = dval(v, part_b, part_a)
        ua, ub = sorted(part_a), sorted(part_b)
        swaps, gains = [], []
        for _ in range(min(len(ua), len(ub))):
            best = None
            for x in ua:
                for y in ub:
                    gain = d[x] + d[y] - 2 * wgt[x].get(y, 0)
                    if best is None or gain > best[0]:
                        best = (gain, x, y)
            gain, x, y = best
            swaps.append((x, y))
            gains.append(gain)
            ua.remove(x)
            ub.remove(y)
            for v in ua:
                d[v] += 2 * wgt[v].get(x, 0) - 2 * wgt[v].get(y, 0)
            for v in ub:
                d[v] += 2 * wgt[v].get(y, 0) - 2 * wgt[v].get(x, 0)
        # best prefix of cumulative gains
        cum, best_cum, best_k = 0, 0, 0
        for i, gain in enumerate(gains):
            cum += gain
            if cum > best_cum:
                best_cum, best_k = cum, i + 1
        if best_cum <= 0:
            break
        for x, y in swaps[:best_k]:
            part_a.remove(x)
            part_a.add(y)
            part_b.remove(y)
            part_b.add(x)
    return sorted(part_a), sorted(part_b)


def _split_sizes(total: int, k: int) -> list:
    """k near-equal part sizes summing to `total` (larger parts first)."""
    base, rem = divmod(total, k)
    return [base + (1 if i < rem else 0) for i in range(k)]


def kway_partition(g: nx.Graph, k: int, seed: int = 0, sizes: list | None = None) -> list:
    """Partition g's nodes into k parts of the given (or near-equal) sizes.

    Returns a list of k node-lists.
    """
    nodes = list(g.nodes)
    if sizes is None:
        sizes = _split_sizes(len(nodes), k)
    assert len(sizes) == k and sum(sizes) == len(nodes)
    return _recurse(g, nodes, sizes, seed)


def _recurse(g: nx.Graph, nodes: list, sizes: list, seed: int) -> list:
    k = len(sizes)
    if k == 1:
        return [list(nodes)]
    ka = (k + 1) // 2
    size_a = sum(sizes[:ka])
    part_a, part_b = _kl_bisect(g, nodes, size_a, seed)
    return (_recurse(g, part_a, sizes[:ka], seed + 1)
            + _recurse(g, part_b, sizes[ka:], seed + 2))


def cut_size(g: nx.Graph, parts: list) -> float:
    """Sum of weights of edges crossing between different parts."""
    owner = {}
    for idx, part in enumerate(parts):
        for n in part:
            owner[n] = idx
    return sum(d.get("weight", 1) for u, v, d in g.edges(data=True)
               if owner[u] != owner[v])


def cut_edges(g: nx.Graph, parts: list) -> list:
    """List of (part_u, part_v, weight) for every cut edge occurrence group."""
    owner = {}
    for idx, part in enumerate(parts):
        for n in part:
            owner[n] = idx
    return [(owner[u], owner[v], d.get("weight", 1))
            for u, v, d in g.edges(data=True) if owner[u] != owner[v]]
