"""Generate the bar-by-bar comparison table vs the paper's reference values.

Run:  python -m experiments.compare_with_paper
Writes results/comparison_table.md (also printed).
"""

import glob
import os
import pickle
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from paper_reference import EBITS, JET_QFT, MAKESPAN, PARTITIONS

RESULTS_KL = os.path.join(os.path.dirname(__file__), "..", "results", "kl")
OUT = os.path.join(os.path.dirname(__file__), "..", "results",
                   "comparison_table.md")


def load():
    acc = defaultdict(list)
    for path in glob.glob(os.path.join(RESULTS_KL, "*.pkl")):
        with open(path, "rb") as f:
            s = pickle.load(f)
        c = s["config"]
        acc[(c["scenario"], c["M"], c["scheme"])].append(s)
    return acc


def ours(acc, key, metric, subkey=None):
    runs = acc.get(key, [])
    if not runs:
        return np.nan
    if subkey:
        return float(np.mean([r[metric].get(subkey, np.nan) for r in runs]))
    return float(np.mean([r[metric] for r in runs]))


def main():
    acc = load()
    sections = [
        ("Fig 7(a)(c) ebits/QCirc", EBITS, "ebits_per_qcirc", None),
        ("Fig 7(b)(d) partitions/QCirc", PARTITIONS, "partitions_per_qcirc", None),
        ("Fig 9(a)(c) normalised makespan", MAKESPAN, "makespan", None),
        ("Fig 8(a)(e) JET QFT", JET_QFT, "jet_by_type", "QFT"),
    ]
    lines = ["# 复现 vs 论文逐柱对照表（自动生成）", ""]
    for title, ref, metric, subkey in sections:
        lines += [f"## {title}", "",
                  "| scenario | M | scheme | 论文 | 复现 | 相对偏差 |",
                  "|---|---|---|---|---|---|"]
        errs = []
        for (scen, m, scheme), pv in sorted(ref.items()):
            ov = ours(acc, (scen, m, scheme), metric, subkey)
            rel = (ov - pv) / pv if pv else np.nan
            errs.append(abs(rel))
            lines.append(f"| {scen} | {m} | {scheme} | {pv:.3g} | {ov:.3g} "
                         f"| {rel:+.0%} |")
        lines += ["", f"平均绝对相对偏差：{np.nanmean(errs):.1%}", ""]
    text = "\n".join(lines)
    with open(OUT, "w") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
