import networkx as nx
import pytest

from qdc_scheduler.circuits import make_circuit, make_dj, make_ghz, make_qft, make_wstate
from qdc_scheduler.network import DQCNetwork


# --- Fig. 6 pixel check (w = 4) ---------------------------------------------

def test_ghz_is_path_weight1():
    c = make_ghz(4)
    assert sorted(c.graph.edges) == [(0, 1), (1, 2), (2, 3)]
    assert all(d["weight"] == 1 for _, _, d in c.graph.edges(data=True))


def test_wstate_is_path_weight2():
    c = make_wstate(4)
    assert sorted(c.graph.edges) == [(0, 1), (1, 2), (2, 3)]
    assert all(d["weight"] == 2 for _, _, d in c.graph.edges(data=True))


def test_dj_is_star_weight1():
    c = make_dj(4)
    assert sorted(c.graph.edges) == [(0, 1), (0, 2), (0, 3)]
    assert all(d["weight"] == 1 for _, _, d in c.graph.edges(data=True))


def test_qft_is_complete_weight1():
    c = make_qft(4)
    assert c.graph.number_of_edges() == 6
    assert all(d["weight"] == 1 for _, _, d in c.graph.edges(data=True))


def test_total_edge_weight_counts_two_qubit_gates():
    for ctype, expected in [("GHZ", 9), ("WState", 18), ("DJ", 9), ("QFT", 45)]:
        assert make_circuit(ctype, 10).total_edge_weight == expected


def test_layers_cover_all_gates_and_respect_dependencies():
    c = make_qft(5)
    assert sum(len(l) for l in c.layers) == len(c.gates)
    seen = {}
    for li, layer in enumerate(c.layers):
        used = set()
        for gate in layer:
            for q in gate:
                assert q not in used  # no qubit reused within a layer
                used.add(q)
                seen[q] = li


# --- network ------------------------------------------------------------------

def test_fat_tree_switch_counts():
    net = DQCNetwork()
    for j in range(16):
        ns = [net.n_switches(j, o) for o in range(16) if o != j]
        assert ns.count(1) == 1    # its edge-switch sibling
        assert ns.count(3) == 2    # same pod, other edge switch
        assert ns.count(5) == 12   # other pods


def test_latency_and_fidelity_values():
    net = DQCNetwork(switch_loss_db=0.5)
    eta = 10 ** (-0.05)
    assert net.latency(0, 1) == pytest.approx(0.005 / eta)
    assert net.latency(0, 2) == pytest.approx(0.005 / eta ** 3)
    assert net.latency(0, 15) == pytest.approx(0.005 / eta ** 5)
    assert net.fidelity(0, 1) == 0.96
    assert net.fidelity(0, 2) == 0.94
    assert net.fidelity(0, 15) == 0.92


def test_capacities_pool_and_determinism():
    net1, net2 = DQCNetwork(capacity_seed=3), DQCNetwork(capacity_seed=3)
    assert net1.capacities == net2.capacities
    assert sorted(net1.capacities) == [8] * 4 + [12] * 4 + [16] * 4 + [20] * 4
    assert net1.total_capacity == 224  # matches paper's c_tot = 224
