"""Plot JointDQC v2 results (results/final_*.csv) -> figures/*.pdf (+ overleaf copy).

Because cross-pod load is spread evenly over symmetric cores, only the AGGREGATE core BSM budget
B_tot matters (N_core is degenerate); we use it as the core-provisioning axis and restrict to the
canonical N_core=1 rows.

Honest story:
  jointdqc_regime    : effective throughput vs aggregate BSM budget, mixed vs dense workload
                       (at high budget OBL==JointDQC; at low budget JointDQC wins by dropping a few
                        circuits to stay congestion-free)
  jointdqc_ratio     : JointDQC/OBL effective-throughput ratio vs offered load M_b
                       (the gain concentrates where the candidate pool is tight)
  jointdqc_coreload  : OBL (BSM-oblivious) forced core load, by workload and load
  jointdqc_heuristic : CAG greedy vs JointDQC-MILP (heuristic quality)
"""

from __future__ import annotations

import glob
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(__file__)
FIG = os.path.join(HERE, "figures")
OVER = os.path.abspath(os.path.join(HERE, "..", "..", "..",
                                    "overleaf_quantum_computing", "figures", "jointdqc"))
os.makedirs(FIG, exist_ok=True)
os.makedirs(OVER, exist_ok=True)

STYLE = {
    "OBL":  ("BSM-Oblivious (strong base)", "#c0392b", "o"),
    "CAG":  ("JointDQC-Greedy", "#2980b9", "s"),
    "JDQC": ("JointDQC-MILP", "#27ae60", "^"),
}
WL = {"mixed": ("Mixed workload (Sc.2)", "#16a085"),
      "dense": ("Dense workload (QFT/DJ)", "#8e44ad")}
plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.alpha": 0.3,
                     "figure.dpi": 120, "savefig.bbox": "tight"})


def load():
    files = glob.glob(os.path.join(HERE, "results", "final_*.csv"))
    df = pd.concat([pd.read_csv(f, keep_default_na=False) for f in files], ignore_index=True)
    df["scheme"] = df["scheme"].astype(str)
    df["workload"] = df["workload"].astype(str)
    for c in ("Mb", "seed", "ncore", "budget_total", "admitted", "core_load",
              "bsm_rounds", "eff_throughput", "base_cost", "solve_time"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["eff_throughput", "budget_total"])
    return df[df.ncore == 1]      # N_core is degenerate; use the canonical rows


def _save(fig, name):
    for d in (FIG, OVER):
        fig.savefig(os.path.join(d, name + ".pdf"))
    fig.savefig(os.path.join(FIG, name + ".png"))
    plt.close(fig)
    print("wrote", name)


def fig_regime(df, Mb=8):
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.5), sharey=True)
    for ax, wl in zip(axes, ("mixed", "dense")):
        d = df[(df.workload == wl) & (df.Mb == Mb)]
        for sch in ("OBL", "CAG", "JDQC"):
            s = d[d.scheme == sch].groupby("budget_total").eff_throughput.agg(["mean", "std"])
            if s.empty:
                continue
            lbl, c, mk = STYLE[sch]
            ax.errorbar(s.index, s["mean"], yerr=s["std"], label=lbl, color=c,
                        marker=mk, capsize=3, lw=1.8)
        ax.set_xlabel("Aggregate core BSM budget $B_{tot}$")
        ax.set_title(WL[wl][0])
    axes[0].set_ylabel("Effective throughput")
    axes[1].legend(fontsize=8.5)
    fig.suptitle(f"Offered load $M_b={Mb}$", y=1.02, fontsize=11)
    _save(fig, "jointdqc_regime")


def fig_ratio(df, budget=8):
    fig, ax = plt.subplots(figsize=(5, 3.6))
    mbs = sorted(df.Mb.unique())
    for wl in ("mixed", "dense"):
        rs = []
        for mb in mbs:
            d = df[(df.workload == wl) & (df.Mb == mb) & (df.budget_total == budget)]
            o = d[d.scheme == "OBL"].eff_throughput.mean()
            j = d[d.scheme == "JDQC"].eff_throughput.mean()
            rs.append(j / o if o and o == o else np.nan)
        lbl, c = WL[wl]
        ax.plot(mbs, rs, marker="o", color=c, lw=1.8, label=lbl)
    ax.axhline(1.0, color="gray", ls="--", lw=1)
    ax.set_xlabel("Offered load $M_b$ (candidate circuits/cycle)")
    ax.set_ylabel("JointDQC / BSM-Oblivious\neffective-throughput ratio")
    ax.set_title(f"Value of BSM-aware admission ($B_{{tot}}={budget}$)")
    ax.set_xticks(mbs)
    ax.legend(fontsize=9)
    _save(fig, "jointdqc_ratio")


def fig_coreload(df):
    b = df.budget_total.min()
    d = df[(df.scheme == "OBL") & (df.budget_total == b)]
    fig, ax = plt.subplots(figsize=(5, 3.6))
    mbs = sorted(df.Mb.unique())
    width = 0.35
    for i, wl in enumerate(("mixed", "dense")):
        means = [d[(d.workload == wl) & (d.Mb == mb)].core_load.mean() for mb in mbs]
        errs = [d[(d.workload == wl) & (d.Mb == mb)].core_load.std() for mb in mbs]
        ax.bar(np.arange(len(mbs)) + (i - 0.5) * width, means, width, yerr=errs,
               capsize=3, label=WL[wl][0], color=WL[wl][1])
    ax.set_xticks(np.arange(len(mbs)))
    ax.set_xticklabels(mbs)
    ax.set_xlabel("Offered load $M_b$")
    ax.set_ylabel("BSM-Oblivious core load (ebits)")
    ax.set_title("Congestion the base scheduler is forced to leave")
    ax.legend(fontsize=9)
    _save(fig, "jointdqc_coreload")


def fig_heuristic(df):
    d = df[df.scheme.isin(["JDQC", "CAG"])]
    keys = ["workload", "Mb", "seed", "budget_total"]
    jd = d[d.scheme == "JDQC"][keys + ["eff_throughput"]].rename(columns={"eff_throughput": "jd"})
    cg = d[d.scheme == "CAG"][keys + ["eff_throughput"]].rename(columns={"eff_throughput": "cg"})
    m = jd.merge(cg, on=keys)
    fig, ax = plt.subplots(figsize=(4.2, 4.0))
    ax.scatter(m.jd, m.cg, alpha=0.4, color="#2980b9", edgecolor="k", lw=0.3)
    lim = [0, max(m.jd.max(), m.cg.max()) + 1]
    ax.plot(lim, lim, "k--", lw=1, label="CAG = MILP")
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel("JointDQC-MILP effective throughput")
    ax.set_ylabel("JointDQC-Greedy effective throughput")
    gap = (1 - m.cg / m.jd.replace(0, np.nan)).mean() * 100
    ax.set_title(f"Heuristic quality (mean gap {gap:.1f}%)")
    ax.legend(fontsize=9)
    _save(fig, "jointdqc_heuristic")
    return gap


def summary(df):
    g = df.groupby(["workload", "Mb", "budget_total", "scheme"]).agg(
        adm=("admitted", "mean"), eff=("eff_throughput", "mean"),
        load=("core_load", "mean"), n=("seed", "nunique")).round(2).reset_index()
    g.to_csv(os.path.join(HERE, "results", "summary.csv"), index=False)
    print("=== JDQC/OBL effective-throughput ratio ===")
    for wl in ("mixed", "dense"):
        for mb in sorted(df.Mb.unique()):
            for b in sorted(df.budget_total.unique()):
                d = df[(df.workload == wl) & (df.Mb == mb) & (df.budget_total == b)]
                o = d[d.scheme == "OBL"].eff_throughput.mean()
                j = d[d.scheme == "JDQC"].eff_throughput.mean()
                if o == o and len(d[d.scheme == "OBL"]):
                    print(f"  {wl:5} Mb={mb} B={int(b):2}: OBL={o:.2f} JDQC={j:.2f} "
                          f"ratio={j/o:.2f} OBLload={d[d.scheme=='OBL'].core_load.mean():.1f} "
                          f"(n={d[d.scheme=='OBL'].seed.nunique()})")
    return g


if __name__ == "__main__":
    df = load()
    print(f"loaded {len(df)} N_core=1 rows; workloads={sorted(df.workload.unique())}; "
          f"Mb={sorted(df.Mb.unique())}; budgets={sorted(df.budget_total.unique())}")
    summary(df)
    fig_regime(df, Mb=8)
    fig_ratio(df, budget=8)
    fig_coreload(df)
    print("heuristic mean gap %.2f%%" % fig_heuristic(df))
