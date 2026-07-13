"""Shared helpers for reproducing the paper's bar-chart figures."""

import glob
import os
import pickle
from collections import defaultdict

import numpy as np

RESULTS_KL = os.path.join(os.path.dirname(__file__), "..", "results", "kl")
FIG_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")

# display order / labels / colours modelled on Fig. 7-9
SCHEME_STYLE = {
    "RB":          ("R-B+K-L", "#4d4d4d"),
    "CAB":         ("CA-B+K-L", "#8c8c8c"),
    "Single":      ("Single+K-L", "#2e9e6f"),
    "Batch_a0.55": (r"Batch+K-L, $\alpha=0.55$", "#a6cee3"),
    "Batch_a0.65": (r"Batch+K-L, $\alpha=0.65$", "#4f9bc7"),
    "Batch_a0.75": (r"Batch+K-L, $\alpha=0.75$", "#1f5fa8"),
}
M_VALUES = [12, 20, 28, 36]


def load_kl_results():
    """-> {(scenario, M, scheme): [summary, ...]} across seeds."""
    acc = defaultdict(list)
    for path in glob.glob(os.path.join(RESULTS_KL, "*.pkl")):
        with open(path, "rb") as f:
            s = pickle.load(f)
        cfg = s["config"]
        acc[(cfg["scenario"], cfg["M"], cfg["scheme"])].append(s)
    return acc


def mean_metric(acc, scenario, m_total, scheme, key, subkey=None):
    runs = acc.get((scenario, m_total, scheme), [])
    if not runs:
        return np.nan
    if subkey is None:
        return float(np.mean([r[key] for r in runs]))
    vals = [r[key][subkey] for r in runs if subkey in r[key]]
    return float(np.mean(vals)) if vals else np.nan


def grouped_bars(ax, acc, scenario, schemes, key, subkey=None):
    n = len(schemes)
    width = 0.8 / n
    xs = np.arange(len(M_VALUES))
    for i, scheme in enumerate(schemes):
        vals = [mean_metric(acc, scenario, m, scheme, key, subkey)
                for m in M_VALUES]
        label, color = SCHEME_STYLE[scheme]
        ax.bar(xs + (i - n / 2 + 0.5) * width, vals, width, label=label,
               color=color, edgecolor="black", linewidth=0.3)
    ax.set_xticks(xs)
    ax.set_xticklabels(M_VALUES)
    ax.set_xlabel("Total number of QCircs (M)")
