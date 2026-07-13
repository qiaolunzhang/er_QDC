"""Figures of merit (paper Sec. IV-A4)."""

from __future__ import annotations

import numpy as np


def ebits_per_qcirc(run) -> float:
    return sum(c.n_ebits for c in run.scheduled) / len(run.scheduled)


def partitions_per_qcirc(run) -> float:
    return sum(c.k for c in run.scheduled) / len(run.scheduled)


def jet_by_type(run) -> dict:
    """Average normalised JET per circuit type."""
    acc = {}
    for c in run.scheduled:
        acc.setdefault(c.ctype, []).append(c.jet)
    return {t: float(np.mean(v)) for t, v in acc.items()}


def ebits_by_type(run) -> dict:
    acc = {}
    for c in run.scheduled:
        acc.setdefault(c.ctype, []).append(c.n_ebits)
    return {t: float(np.mean(v)) for t, v in acc.items()}


def summarise(run) -> dict:
    return {
        "ebits_per_qcirc": ebits_per_qcirc(run),
        "partitions_per_qcirc": partitions_per_qcirc(run),
        "jet_by_type": jet_by_type(run),
        "ebits_by_type": ebits_by_type(run),
        "makespan": run.makespan,
        "throughput": run.throughput,
        "solver_time": run.solver_time,
        "n_solves": run.n_solves,
    }
