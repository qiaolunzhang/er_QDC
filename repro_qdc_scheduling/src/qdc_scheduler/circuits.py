"""Benchmark quantum circuits modelled as weighted interaction graphs + gate layers.

Paper Sec. II / Fig. 6: each circuit is a weighted undirected graph whose nodes are
qubits and whose edge weights count two-qubit gate occurrences. For w = 4 (Fig. 6):
GHZ = path (weight 1), W-state = path (weight 2), DJ = star (weight 1),
QFT = complete graph (weight 1). These patterns generalise to arbitrary w.

For the layered JET model (Eq. 9) we also keep an explicit gate sequence and derive
layers by ASAP scheduling (gates acting on disjoint qubits share a layer).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import networkx as nx

CIRCUIT_TYPES = ("QFT", "DJ", "WState", "GHZ")


@dataclass
class QuantumCircuit:
    ctype: str
    width: int                        # w_m: number of qubits
    gates: list = field(repr=False)   # ordered list of tuples: (q,) local, (q1, q2) two-qubit
    graph: nx.Graph = field(repr=False, default=None)
    layers: list = field(repr=False, default=None)

    def __post_init__(self):
        if self.graph is None:
            self.graph = interaction_graph(self.gates, self.width)
        if self.layers is None:
            self.layers = asap_layers(self.gates)

    @property
    def total_edge_weight(self) -> int:
        """Total number of two-qubit gate occurrences = (1/2) sum_i g_i."""
        return sum(d["weight"] for _, _, d in self.graph.edges(data=True))


def interaction_graph(gates, width) -> nx.Graph:
    g = nx.Graph()
    g.add_nodes_from(range(width))
    for gate in gates:
        if len(gate) == 2:
            a, b = gate
            if g.has_edge(a, b):
                g[a][b]["weight"] += 1
            else:
                g.add_edge(a, b, weight=1)
    return g


def asap_layers(gates) -> list:
    """Greedy ASAP layering: a gate goes to the first layer where all its qubits are free."""
    free = {}  # qubit -> earliest available layer index
    layers = []
    for gate in gates:
        layer = max((free.get(q, 0) for q in gate), default=0)
        while len(layers) <= layer:
            layers.append([])
        layers[layer].append(gate)
        for q in gate:
            free[q] = layer + 1
    return layers


def make_ghz(w: int) -> QuantumCircuit:
    """H on q0 then CNOT chain q0->q1->...->q_{w-1}: path graph, edge weight 1."""
    gates = [(0,)] + [(i, i + 1) for i in range(w - 1)]
    return QuantumCircuit("GHZ", w, gates)


def make_wstate(w: int) -> QuantumCircuit:
    """Standard W-state ladder: per adjacent pair a controlled-G + CNOT (2 two-qubit
    gates per pair, sequential): path graph, edge weight 2."""
    gates = [(0,)]
    for i in range(w - 1):
        gates.append((i, i + 1))
        gates.append((i + 1, i))
    return QuantumCircuit("WState", w, gates)


def make_dj(w: int) -> QuantumCircuit:
    """Deutsch-Jozsa (balanced oracle): H layer, CNOTs from each input qubit to the
    shared ancilla q0, H layer: star graph centred at q0, edge weight 1."""
    gates = [(q,) for q in range(w)]
    gates += [(i, 0) for i in range(1, w)]
    gates += [(q,) for q in range(1, w)]
    return QuantumCircuit("DJ", w, gates)


def make_qft(w: int) -> QuantumCircuit:
    """QFT without final swaps: H(q_i) then CP(q_j, q_i) for j>i: complete graph,
    edge weight 1 (each pair interacts exactly once)."""
    gates = []
    for i in range(w):
        gates.append((i,))
        for j in range(i + 1, w):
            gates.append((j, i))
    return QuantumCircuit("QFT", w, gates)


_MAKERS = {"QFT": make_qft, "DJ": make_dj, "WState": make_wstate, "GHZ": make_ghz}


def make_circuit(ctype: str, w: int) -> QuantumCircuit:
    return _MAKERS[ctype](w)
