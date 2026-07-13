"""Fig. 7: avg ebits and circuit partitions per QCirc; (a)(b) Sc.1, (c)(d) Sc.2."""

import os

import matplotlib.pyplot as plt

from common import FIG_DIR, SCHEME_STYLE, grouped_bars, load_kl_results

SCHEMES = ["RB", "CAB", "Single", "Batch_a0.55", "Batch_a0.65", "Batch_a0.75"]


def main():
    acc = load_kl_results()
    fig, axes = plt.subplots(2, 2, figsize=(9, 6.5))
    panels = [("Sc1", "ebits_per_qcirc", "Ebits per QCirc", "(a)"),
              ("Sc1", "partitions_per_qcirc", "Partitions per QCirc", "(b)"),
              ("Sc2", "ebits_per_qcirc", "Ebits per QCirc", "(c)"),
              ("Sc2", "partitions_per_qcirc", "Partitions per QCirc", "(d)")]
    for ax, (scen, key, ylabel, tag) in zip(axes.flat, panels):
        grouped_bars(ax, acc, scen, SCHEMES, key)
        ax.set_ylabel(ylabel)
        ax.text(0.97, 0.95, tag, transform=ax.transAxes, ha="right", va="top")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=True,
               bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    os.makedirs(FIG_DIR, exist_ok=True)
    out = os.path.join(FIG_DIR, "fig7_ebits_partitions.pdf")
    fig.savefig(out, bbox_inches="tight")
    fig.savefig(out.replace(".pdf", ".png"), dpi=200, bbox_inches="tight")
    print("saved", out)


if __name__ == "__main__":
    main()
