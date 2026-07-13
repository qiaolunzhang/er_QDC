import pytest

from qdc_scheduler.circuits import make_ghz, make_qft
from qdc_scheduler.mapping import map_circuit
from qdc_scheduler.milp import MilpSolver
from qdc_scheduler.network import DQCNetwork, T_LOCAL_OVER_TDEC
from qdc_scheduler.regression import fit_all
from qdc_scheduler.simulator import Simulator
from qdc_scheduler.workload import generate_qc_set


@pytest.fixture(scope="module")
def net():
    return DQCNetwork(capacity_seed=0)


@pytest.fixture(scope="module")
def nu_models():
    return fit_all(k_values=range(2, 5))


def test_map_single_qpu_all_local(net):
    circ = make_ghz(8)
    j = max(range(16), key=lambda q: net.capacities[q])
    res = map_circuit(circ, [j], net)
    assert res.n_ebits == 0
    assert res.jet == pytest.approx(len(circ.layers) * T_LOCAL_OVER_TDEC)


def test_map_ghz_two_qpus_single_cut(net):
    # GHZ chain split across 2 QPUs -> exactly 1 cut edge -> 1 ebit
    circ = make_ghz(16)
    qpus = [j for j in range(16) if net.capacities[j] >= 8][:2]
    res = map_circuit(circ, qpus, net)
    assert res.n_ebits == 1
    ns = net.n_switches(*qpus)
    # JET = (num_layers - 1 remote layer) * T_local + 1 * T_link
    expected = (len(circ.layers) - 1) * T_LOCAL_OVER_TDEC + net.latency_by_ns[ns]
    assert res.jet == pytest.approx(expected)
    assert res.ebits_by_ns == {ns: 1}


def test_map_respects_capacities(net):
    circ = make_qft(24)
    qpus = sorted(range(16), key=lambda j: -net.capacities[j])[:2]  # 20 + 20
    res = map_circuit(circ, qpus, net)
    for j, qubits in res.parts.items():
        assert len(qubits) <= net.capacities[j]
    assert sum(len(v) for v in res.parts.values()) == 24


def test_simulator_single_invariants(net, nu_models):
    circuits = generate_qc_set("Sc1", 8, seed=1)
    sim = Simulator(net, circuits, nu_models, solver=MilpSolver())
    run = sim.run_single()
    assert len(run.scheduled) == 8              # every circuit scheduled once
    # non-preemption: a QPU never hosts two overlapping circuits
    for j in range(16):
        spans = sorted((c.start, c.finish) for c in run.scheduled if j in c.qpus)
        for (s1, f1), (s2, f2) in zip(spans, spans[1:]):
            assert s2 >= f1 - 1e-12
    assert run.makespan == max(c.finish for c in run.scheduled)


def test_simulator_batch_invariants(net, nu_models):
    circuits = generate_qc_set("Sc1", 8, seed=1)
    sim = Simulator(net, circuits, nu_models, solver=MilpSolver())
    run = sim.run_batch(alpha=0.55, beta=0.85)
    assert len(run.scheduled) == 8
    for j in range(16):
        spans = sorted((c.start, c.finish) for c in run.scheduled if j in c.qpus)
        for (s1, f1), (s2, f2) in zip(spans, spans[1:]):
            assert s2 >= f1 - 1e-12


def test_baselines_schedule_everything(net, nu_models):
    circuits = generate_qc_set("Sc1", 8, seed=2)
    for policy in ("run_random", "run_capacity"):
        sim = Simulator(net, circuits, nu_models, solver=MilpSolver())
        run = getattr(sim, policy)()
        assert len(run.scheduled) == 8
