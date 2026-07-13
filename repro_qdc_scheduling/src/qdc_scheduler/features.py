"""Structural graph features of circuit graphs (paper Sec. III-A1, Eqs. 2-3).

(i)  weighted density gamma_m  = total edge weight / C(w, 2)          (Eq. 2)
(ii) algebraic connectivity lambda_{2,m}: second-smallest eigenvalue of the
     normalised Laplacian of the (weighted) circuit graph
(iii) coefficient of variance sigma_m / g_m of the weighted degrees   (Eq. 3)
"""

from __future__ import annotations

import networkx as nx
import numpy as np


def weighted_degrees(g: nx.Graph) -> np.ndarray:
    return np.array([d for _, d in g.degree(weight="weight")], dtype=float)


def weighted_density(g: nx.Graph) -> float:
    w = g.number_of_nodes()
    total_edge_weight = weighted_degrees(g).sum() / 2.0
    return total_edge_weight / (w * (w - 1) / 2.0)


def algebraic_connectivity(g: nx.Graph) -> float:
    lap = nx.normalized_laplacian_matrix(g, weight="weight").toarray()
    eig = np.linalg.eigvalsh(lap)
    return float(eig[1])


def coeff_of_variance(g: nx.Graph) -> float:
    deg = weighted_degrees(g)
    return float(deg.std() / deg.mean())  # population std (ddof=0), Eq. 3


def feature_vector(g: nx.Graph) -> np.ndarray:
    """[gamma_m, lambda_{2,m}, sigma_m/g_m] in the order of Eq. 5."""
    return np.array([weighted_density(g), algebraic_connectivity(g),
                     coeff_of_variance(g)])
