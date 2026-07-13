"""Aggregate results/kl/*.pkl into a markdown table (results/kl_summary.md).

Run:  python -m experiments.summarize_kl
"""

import glob
import os
import pickle
from collections import defaultdict

import numpy as np

RESULTS_KL = os.path.join(os.path.dirname(__file__), "..", "results", "kl")
OUT = os.path.join(os.path.dirname(__file__), "..", "results", "kl_summary.md")
ORDER = ["RB", "CAB", "Single", "Batch_a0.55", "Batch_a0.65", "Batch_a0.75"]
TYPES = ["QFT", "DJ", "WState", "GHZ"]


def main():
    acc = defaultdict(list)
    for path in glob.glob(os.path.join(RESULTS_KL, "*.pkl")):
        with open(path, "rb") as f:
            s = pickle.load(f)
        c = s["config"]
        acc[(c["scenario"], c["M"], c["scheme"])].append(s)

    lines = ["# K-L 系实验汇总（种子均值）", ""]
    for scen in ("Sc1", "Sc2"):
        lines += [f"## {scen}", "",
                  "| M | scheme | n | ebits/QC | parts/QC | makespan | thrpt | "
                  + " | ".join(f"JET {t}" for t in TYPES) + " |",
                  "|---|---|---|---|---|---|---|" + "---|" * len(TYPES)]
        for m_total in (12, 20, 28, 36):
            for scheme in ORDER:
                runs = acc.get((scen, m_total, scheme), [])
                if not runs:
                    continue
                jet = [np.mean([r["jet_by_type"].get(t, np.nan) for r in runs])
                       for t in TYPES]
                lines.append(
                    f"| {m_total} | {scheme} | {len(runs)} "
                    f"| {np.mean([r['ebits_per_qcirc'] for r in runs]):.2f} "
                    f"| {np.mean([r['partitions_per_qcirc'] for r in runs]):.2f} "
                    f"| {np.mean([r['makespan'] for r in runs]):.4f} "
                    f"| {np.mean([r['throughput'] for r in runs]):.0f} | "
                    + " | ".join(f"{v:.4f}" for v in jet) + " |")
        lines.append("")
    with open(OUT, "w") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))
    print("saved", OUT)


if __name__ == "__main__":
    main()
