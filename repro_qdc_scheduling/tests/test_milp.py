import pytest

from qdc_scheduler.milp import MilpSolver
from qdc_scheduler.network import DQCNetwork


@pytest.fixture(scope="module")
def solver():
    return MilpSolver()


@pytest.fixture(scope="module")
def net():
    return DQCNetwork(capacity_seed=0)


def test_single_fits_one_qpu_zero_cost(solver, net):
    # circuit smaller than the largest QPU -> one QPU, objective 0
    biggest = max(range(16), key=lambda j: net.capacities[j])
    res = solver.solve_single(w_m=8, k_max=4, network=net, available=list(range(16)))
    assert res.feasible
    assert len(res.qpus) == 1
    assert res.objective < 1e-4  # only the epsilon best-fit tie-break term
    assert net.capacities[res.qpus[0]] >= 8


def test_single_forced_split_prefers_cheapest_pair(solver, net):
    # restrict to two QPUs on the same edge switch (1 switch) and two cross-pod;
    # a circuit needing both QPUs of a pair should pick the same-edge pair when
    # capacities allow, because T and 1-F are smallest for n_s = 1.
    # Build explicit choice: QPUs {0,1} same edge switch; {0, 15} cross pod.
    cap01 = net.capacities[0] + net.capacities[1]
    res = solver.solve_single(w_m=cap01, k_max=2, network=net, available=[0, 1, 15])
    assert res.feasible and len(res.qpus) == 2
    # cost of pair (0,1) is strictly less than any pair involving 15
    assert res.qpus == [0, 1]


def test_single_infeasible_when_capacity_insufficient(solver, net):
    res = solver.solve_single(w_m=100, k_max=2, network=net, available=[0, 1])
    assert not res.feasible


def test_batch_assigns_all_when_room(solver, net):
    circuits = {0: (8, 4), 1: (8, 4)}
    nu = {(m, k): float(k - 1) for m in circuits for k in range(1, 5)}
    res = solver.solve_batch(circuits, net, list(range(16)), nu)
    assert res.zeta == 2
    assert all(len(res.assignment[m]) >= 1 for m in circuits)
    assert all(res.k[m] == len(res.assignment[m]) for m in circuits)
    # constraint (4): no QPU hosts two circuits
    used = res.assignment[0] + res.assignment[1]
    assert len(used) == len(set(used))
    # both fit on single QPUs -> zero objective
    assert res.objective == pytest.approx(0.0)


def test_batch_zeta_fallback(solver, net):
    # two big circuits but only enough QPUs for one -> zeta drops to 1
    circuits = {0: (20, 1), 1: (20, 1)}  # Kmax=1: no splitting allowed
    big = [j for j in range(16) if net.capacities[j] == 20][:1]
    nu = {(m, 1): 0.0 for m in circuits}
    res = solver.solve_batch(circuits, net, big, nu)
    assert res.zeta == 1
    assigned = [m for m in circuits if res.assignment[m]]
    assert len(assigned) == 1
