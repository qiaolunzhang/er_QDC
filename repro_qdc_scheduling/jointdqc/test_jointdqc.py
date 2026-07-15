"""Fast sanity tests for the JointDQC sub-project.

Run from repo root:
  AMPL_DIR=/home/qiaolun/opt/ampl.linux-intel64 \
  conda run -n rwa python -m pytest jointdqc/test_jointdqc.py -q
The fabric/evaluator tests are pure-Python and instant; one tiny MILP test exercises the AMPL path.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

import pytest
from qdc_scheduler.workload import generate_qc_set
from qdc_scheduler.regression import fit_all
from fabric import Fabric
import evaluator
import heuristic


@pytest.fixture(scope="module")
def nu_models():
    return fit_all(range(2, 5))


def test_fabric_topology():
    fab = Fabric(ncore=2, capacity_seed=0)
    assert len(fab.J) == 16
    assert fab.edges == [f"E{i}" for i in range(8)]
    assert fab.aggs == [f"A{i}" for i in range(4)]
    assert fab.cores == ["Cr0", "Cr1"]
    # same edge switch -> one switch on path, n_s = 1
    assert fab.path_fixed_switches(0, 1) == ["E0"]
    assert not fab.is_xpod(0, 1)
    # same pod (0..3), different edge -> E,A,E (n_s = 3)
    assert fab.path_fixed_switches(0, 2) == ["E0", "A0", "E1"]
    assert not fab.is_xpod(0, 2)
    # cross pod -> edge,agg,agg,edge fixed (+core), and flagged cross-pod
    assert fab.is_xpod(0, 4)
    # QPU0 on E0 (pod0), QPU4 on E2 (pod1) -> E0,A0,A1,E2 fixed (core added separately)
    assert fab.path_fixed_switches(0, 4) == ["E0", "A0", "A1", "E2"]


def test_evaluator_load_accounting(nu_models):
    fab = Fabric(ncore=2, bcore=4.0, capacity_seed=0)
    circuits = {i: c for i, c in enumerate(generate_qc_set("Sc2", 4, seed=0))}
    # place one circuit intra-edge (QPUs 0,1) -> zero cross-pod load
    alloc = {0: [0, 1], 1: [], 2: [], 3: []}
    cong = evaluator.evaluate(circuits, alloc, fab, nu_models)
    assert cong.core_load_total == 0.0
    assert cong.n_assigned == 1
    # place a split circuit across pods -> positive core load
    alloc2 = {0: [0, 4], 1: [], 2: [], 3: []}
    cong2 = evaluator.evaluate(circuits, alloc2, fab, nu_models)
    if evaluator.nu_of(circuits[0], 2, nu_models) > 0:
        assert cong2.core_load_total > 0.0


def test_cag_respects_core_budget(nu_models):
    fab = Fabric(ncore=2, bcore=2.0, capacity_seed=1)   # tight budget
    circuits = {i: c for i, c in enumerate(generate_qc_set("Sc2", 12, seed=1))}
    alloc = heuristic.solve_cag(circuits, fab, nu_models)
    cong = evaluator.evaluate(circuits, alloc, fab, nu_models)
    assert cong.core_load_total <= fab.ncore * fab.bcore + 1e-6


@pytest.mark.slow
def test_admit_milp_tiny(nu_models):
    from solver import CongestSolver
    fab = Fabric(ncore=2, bcore=8.0, capacity_seed=0)
    circuits = {i: c for i, c in enumerate(generate_qc_set("Sc1", 4, seed=0))}
    res = CongestSolver(timelimit=10).solve_admit(circuits, fab, nu_models)
    assert 1 <= res.zeta <= 4     # admits between 1 and all 4
