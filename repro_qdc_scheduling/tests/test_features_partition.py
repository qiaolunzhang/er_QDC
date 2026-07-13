import networkx as nx
import numpy as np
import pytest

from qdc_scheduler.circuits import make_ghz, make_qft, make_wstate
from qdc_scheduler.features import (algebraic_connectivity, coeff_of_variance,
                                    weighted_density)
from qdc_scheduler.partitioner import cut_size, kway_partition


def test_weighted_density_hand_computed():
    # W-state w=4: total edge weight 6, C(4,2)=6 -> gamma = 1
    assert weighted_density(make_wstate(4).graph) == pytest.approx(1.0)
    # QFT complete graph weight 1 -> gamma = 1
    assert weighted_density(make_qft(6).graph) == pytest.approx(1.0)
    # GHZ w=4: 3 / 6 = 0.5
    assert weighted_density(make_ghz(4).graph) == pytest.approx(0.5)


def test_algebraic_connectivity_complete_graph():
    # normalised Laplacian of K_n has eigenvalues {0, n/(n-1) x(n-1)}
    n = 8
    lam2 = algebraic_connectivity(make_qft(n).graph)
    assert lam2 == pytest.approx(n / (n - 1), rel=1e-9)


def test_coeff_of_variance_regular_graph_zero():
    assert coeff_of_variance(make_qft(5).graph) == pytest.approx(0.0, abs=1e-12)
    assert coeff_of_variance(make_ghz(6).graph) > 0  # endpoints have degree 1


def test_kway_partition_sizes_and_determinism():
    g = make_qft(13).graph
    parts = kway_partition(g, 4, seed=0)
    assert sorted(len(p) for p in parts) == [3, 3, 3, 4]
    assert sorted(sum(parts, [])) == list(range(13))
    assert parts == kway_partition(g, 4, seed=0)


def test_kl_beats_or_matches_naive_split_on_path():
    # path graph: optimal 2-way cut = 1 (cut the middle edge)
    g = make_ghz(20).graph
    parts = kway_partition(g, 2, seed=0)
    assert cut_size(g, parts) == 1


def test_cut_size_hand_computed():
    g = nx.Graph()
    g.add_edge(0, 1, weight=5)
    g.add_edge(1, 2, weight=2)
    assert cut_size(g, [[0, 1], [2]]) == 2
    assert cut_size(g, [[0], [1, 2]]) == 5
