"""Fig. 9: normalised makespan and throughput; (a)(b) Sc.1, (c)(d) Sc.2."""

import os

import matplotlib.pyplot as plt

from common import FIG_DIR, grouped_bars, load_kl_results

SCHEMES = ["CAB", "Single", "Batch_a0.55", "Batch_a0.65", "Batch_a0.75"]


def main():
    acc = load_kl_results()
    fig, axes = plt.subplots(2, 2, figsize=(9, 6.5))
    panels = [("Sc1", "makespan", "Normalised makespan", "(a)"),
              ("Sc1", "throughput", "Normalised throughput", "(b)"),
              ("Sc2", "makespan", "Normalised makespan", "(c)"),
              ("Sc2", "throughput", "Normalised throughput", "(d)")]
    for ax, (scen, key, ylabel, tag) in zip(axes.flat, panels):
        grouped_bars(ax, acc, scen, SCHEMES, key)
        ax.set_ylabel(ylabel)
        ax.text(0.97, 0.95, tag, transform=ax.transAxes, ha="right", va="top")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=True,
               bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    os.makedirs(FIG_DIR, exist_ok=True)
    out = os.path.join(FIG_DIR, "fig9_makespan_throughput.pdf")
    fig.savefig(out, bbox_inches="tight")
    fig.savefig(out.replace(".pdf", ".png"), dpi=200, bbox_inches="tight")
    print("saved", out)


if __name__ == "__main__":
    main()
