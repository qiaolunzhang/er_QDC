"""Linear-regression estimation of the partitioning cost coefficient nu_mk
(paper Sec. III-A1 Eqs. 4-6 and Sec. IV-B, Table II).

Target (Eq. 4): normalised balanced k-way cut  nu~_mk = Cut_m^(k) / total edge weight.
Model  (Eq. 5): nu~ ~= chi0*gamma + chi1*lambda2 + chi2*(sigma/g) + chi3, fitted per k
by minimising MSE (Eq. 6). The estimated cost nu_mk rescales by total edge weight.

Training set: all 4 circuit types, w in [10, 30]  (84 circuits).
Test set:     all 4 circuit types, w in [31, 40]  (40 circuits).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import LinearRegression

from .circuits import CIRCUIT_TYPES, make_circuit
from .features import feature_vector
from .partitioner import cut_size, kway_partition


def dataset(w_values, k: int, seed: int = 0):
    """Feature matrix X=[gamma, lambda2, sigma/g] and target nu~ for all 4 types."""
    xs, ys = [], []
    for ctype in CIRCUIT_TYPES:
        for w in w_values:
            circ = make_circuit(ctype, w)
            parts = kway_partition(circ.graph, k, seed=seed)
            nu_tilde = cut_size(circ.graph, parts) / circ.total_edge_weight
            xs.append(feature_vector(circ.graph))
            ys.append(nu_tilde)
    return np.array(xs), np.array(ys)


@dataclass
class NuModel:
    k: int
    chi: np.ndarray       # [chi0, chi1, chi2] feature coefficients
    chi3: float           # intercept
    r2_test: float = np.nan
    rmse_test: float = np.nan

    def nu_tilde(self, g) -> float:
        return float(self.chi @ feature_vector(g) + self.chi3)

    def nu(self, g) -> float:
        """Estimated (rescaled) partitioning cost coefficient nu_mk (Eq. 5)."""
        total_edge_weight = sum(d["weight"] for _, _, d in g.edges(data=True))
        return max(0.0, self.nu_tilde(g)) * total_edge_weight


def fit_nu_model(k: int, train_w=range(10, 31), test_w=range(31, 41),
                 seed: int = 0) -> NuModel:
    x_tr, y_tr = dataset(train_w, k, seed)
    reg = LinearRegression().fit(x_tr, y_tr)
    model = NuModel(k=k, chi=reg.coef_.copy(), chi3=float(reg.intercept_))
    x_te, y_te = dataset(test_w, k, seed)
    pred = reg.predict(x_te)
    ss_res = float(((y_te - pred) ** 2).sum())
    ss_tot = float(((y_te - y_te.mean()) ** 2).sum())
    model.r2_test = 1.0 - ss_res / ss_tot
    model.rmse_test = float(np.sqrt(((y_te - pred) ** 2).mean()))
    return model


def fit_all(k_values=range(2, 7), **kw) -> dict:
    return {k: fit_nu_model(k, **kw) for k in k_values}
