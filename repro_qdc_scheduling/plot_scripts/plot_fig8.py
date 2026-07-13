"""Fig. 8: normalised JET per circuit type; (a)-(d) Sc.1, (e)-(h) Sc.2."""

import os

import matplotlib.pyplot as plt

from common import FIG_DIR, grouped_bars, load_kl_results

SCHEMES = ["CAB", "Single", "Batch_a0.55", "Batch_a0.65", "Batch_a0.75"]
TYPES = ["QFT", "DJ", "WState", "GHZ"]


def main():
    acc = load_kl_results()
    fig, axes = plt.subplots(4, 2, figsize=(9, 12))
    tags = iter("abcdefgh")
    for row, ctype in enumerate(TYPES):
        for col, scen in enumerate(["Sc1", "Sc2"]):
            ax = axes[row, col]
            grouped_bars(ax, acc, scen, SCHEMES, "jet_by_type", subkey=ctype)
            ax.set_ylabel(f"Normalised JET of {ctype}")
            ax.text(0.97, 0.95, f"({next(tags)})", transform=ax.transAxes,
                    ha="right", va="top")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=True,
               bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    os.makedirs(FIG_DIR, exist_ok=True)
    out = os.path.join(FIG_DIR, "fig8_jet_by_type.pdf")
    fig.savefig(out, bbox_inches="tight")
    fig.savefig(out.replace(".pdf", ".png"), dpi=200, bbox_inches="tight")
    print("saved", out)


if __name__ == "__main__":
    main()
