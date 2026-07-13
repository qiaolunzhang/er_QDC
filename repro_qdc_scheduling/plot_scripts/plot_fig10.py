"""Fig. 10: average makespan vs optical switch loss (Sc.2, alpha=0.55).

Grouped bars: x = M, groups = scheme (CA-B, Single, Batch), hatch = loss level.
"""

import glob
import os
import pickle
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

from common import FIG_DIR

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results", "fig10")
SCHEMES = [("CAB", "CA-B+K-L", "#8c8c8c"), ("Single", "Single+K-L", "#2e9e6f"),
           ("Batch_a0.55", "Batch+K-L", "#a6cee3")]
LOSSES = [(0.5, ""), (1.0, "//"), (2.0, "xx")]
M_VALUES = [12, 20, 28, 36]


def main():
    acc = defaultdict(list)
    for path in glob.glob(os.path.join(RESULTS_DIR, "*.pkl")):
        with open(path, "rb") as f:
            s = pickle.load(f)
        c = s["config"]
        acc[(c["scheme"], c["loss"], c["M"])].append(s["makespan"])

    fig, ax = plt.subplots(figsize=(7, 4))
    n = len(SCHEMES) * len(LOSSES)
    width = 0.8 / n
    xs = np.arange(len(M_VALUES))
    i = 0
    for loss, hatch in LOSSES:
        for scheme, label, color in SCHEMES:
            vals = [np.mean(acc.get((scheme, loss, m), [np.nan]))
                    for m in M_VALUES]
            ax.bar(xs + (i - n / 2 + 0.5) * width, vals, width,
                   label=f"{label}" if loss == 0.5 else None,
                   color=color, hatch=hatch, edgecolor="black", linewidth=0.3)
            i += 1
    ax.set_xticks(xs)
    ax.set_xticklabels(M_VALUES)
    ax.set_xlabel("Total number of QCircs (M)")
    ax.set_ylabel("Normalised makespan")
    ax.legend(title=r"solid: 0.5 dB, //: 1 dB, xx: 2 dB ($\eta_s$)")
    os.makedirs(FIG_DIR, exist_ok=True)
    out = os.path.join(FIG_DIR, "fig10_switch_loss.pdf")
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    fig.savefig(out.replace(".pdf", ".png"), dpi=200, bbox_inches="tight")
    print("saved", out)


if __name__ == "__main__":
    main()
