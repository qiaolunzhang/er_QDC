"""Fig. 11: pytket-dqc based scheduling-partitioning schemes.
Rows = Sc.1 / Sc.2 / Sc.3; columns = ebits/QCirc, partitions/QCirc, makespan.
Six schemes: Pytket-PA, Single+PA, Batch+PA, Pytket-PH, Single+PH, Batch+PH.
"""

import glob
import os
import pickle
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

from common import FIG_DIR

RESULTS = os.path.join(os.path.dirname(__file__), "..", "results", "pytket")
M_VALUES = [12, 20, 28]
# order + colours modelled on Fig. 11 (PA family greens, PH family oranges)
SCHEMES = [
    ("Pytket-PA", "Pytket-PA", "#b5d8a6"),
    ("Single+PA", "Single+PA", "#74a950"),
    ("Batch+PA", "Batch+PA", "#3b6b1f"),
    ("Pytket-PH", "Pytket-PH", "#ffe08a"),
    ("Single+PH", "Single+PH", "#e0952f"),
    ("Batch+PH", "Batch+PH", "#a5591a"),
]


def load():
    acc = defaultdict(list)
    for path in glob.glob(os.path.join(RESULTS, "*.pkl")):
        with open(path, "rb") as f:
            s = pickle.load(f)
        c = s["config"]
        acc[(c["scenario"], c["M"], c["scheme"])].append(s)
    return acc


def bars(ax, acc, scen, metric):
    n = len(SCHEMES)
    width = 0.8 / n
    xs = np.arange(len(M_VALUES))
    for i, (key, label, color) in enumerate(SCHEMES):
        vals = [np.mean([r[metric] for r in acc.get((scen, m, key), [])])
                if acc.get((scen, m, key)) else np.nan for m in M_VALUES]
        ax.bar(xs + (i - n / 2 + 0.5) * width, vals, width, label=label,
               color=color, edgecolor="black", linewidth=0.3)
    ax.set_xticks(xs)
    ax.set_xticklabels(M_VALUES)
    ax.set_xlabel("Total number of QCircs (M)")


def main():
    acc = load()
    fig, axes = plt.subplots(3, 3, figsize=(12, 10))
    cols = [("ebits_per_qcirc", "Ebits per QCirc"),
            ("partitions_per_qcirc", "Partitions per QCirc"),
            ("makespan", "Normalised makespan")]
    tags = iter("abcdefghi")
    for r, scen in enumerate(["Sc1", "Sc2", "Sc3"]):
        for c, (metric, ylabel) in enumerate(cols):
            ax = axes[r][c]
            bars(ax, acc, scen, metric)
            ax.set_ylabel(f"{ylabel}")
            ax.text(0.97, 0.95, f"({next(tags)})", transform=ax.transAxes,
                    ha="right", va="top")
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=6, frameon=True,
               bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    os.makedirs(FIG_DIR, exist_ok=True)
    out = os.path.join(FIG_DIR, "fig11_pytket.pdf")
    fig.savefig(out, bbox_inches="tight")
    fig.savefig(out.replace(".pdf", ".png"), dpi=150, bbox_inches="tight")
    print("saved", out)


if __name__ == "__main__":
    main()
