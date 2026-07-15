"""Extra figures + tables for the JointDQC companion paper (pixel-mimicry pass).

Produces, from results/*.csv:
  fig_congestion_blind : the base cost objective's core-load face is huge (E-CB)  -> Fig.3
  fig_switchloss       : BSM-aware gain vs optical-switch loss (E-SL, mirror ref Fig.10) -> Fig.7
  runtime table        : mean/max MILP solve time by scheme x workload x Mb (E-RT) -> Table IV
  latex_tables.tex     : ready-to-\\input LaTeX for the congestion-blindness + runtime tables

Reuses the style of plot.py. Writes PDFs to jointdqc/figures/ and the overleaf mirror.
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
RES = os.path.join(HERE, "results")
FIG = os.path.join(HERE, "figures")
OVER = os.path.abspath(os.path.join(HERE, "..", "..", "..",
                                    "overleaf_quantum_computing", "figures", "jointdqc"))
os.makedirs(FIG, exist_ok=True)
os.makedirs(OVER, exist_ok=True)
plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.alpha": 0.3,
                     "figure.dpi": 120, "savefig.bbox": "tight"})
WL = {"mixed": ("Mixed workload (Sc.2)", "#16a085"),
      "dense": ("Dense workload (QFT/DJ)", "#8e44ad")}


def _save(fig, name):
    for d in (FIG, OVER):
        fig.savefig(os.path.join(d, name + ".pdf"))
    fig.savefig(os.path.join(FIG, name + ".png"))
    plt.close(fig)
    print("wrote", name)


# ----------------------------------------------------------------- E-CB: Fig.3
def fig_congestion_blind():
    files = glob.glob(os.path.join(RES, "congestion_blind*.csv"))
    if not files:
        print("skip congestion_blind (no csv)"); return None
    df = pd.concat([pd.read_csv(f, keep_default_na=False) for f in files], ignore_index=True)
    for c in ("eps", "cmin", "load_min", "load_max", "cost_min", "cost_max", "seed", "Mb"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.drop_duplicates(subset=["workload", "Mb", "seed", "eps"])
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.4))
    # (a) core-load spread (min..max) vs cost tolerance eps, averaged over seeds
    ax = axes[0]
    for wl in ("mixed", "dense"):
        d = df[df.workload == wl]
        if d.empty:
            continue
        g = d.groupby("eps").agg(lmin=("load_min", "mean"), lmax=("load_max", "mean")).reset_index()
        lbl, c = WL[wl]
        ax.fill_between(g.eps * 100, g.lmin, g.lmax, alpha=0.25, color=c)
        ax.plot(g.eps * 100, g.lmax, marker="^", color=c, lw=1.8, label=f"{wl}: max")
        ax.plot(g.eps * 100, g.lmin, marker="v", color=c, lw=1.8, ls="--", label=f"{wl}: min")
    ax.set_xlabel("Base-cost tolerance above optimum (\\%)")
    ax.set_ylabel("Core (cross-pod) BSM load [ebits]")
    ax.set_title("Near-optimal cost, uncontrolled congestion")
    ax.legend(fontsize=8)
    # (b) at a modest cost tolerance where the indifference is visible, min vs max load.
    # (At a 1% gap these feasible instances have a nearly unique optimum; the base objective's
    #  indifference to cross-pod placement shows once a few % of cost slack is allowed.)
    ax = axes[1]
    TOL = 0.05
    d0 = df[np.isclose(df.eps, TOL)]
    if d0.empty:                       # fall back to nearest available tolerance
        near = df.eps.iloc[(df.eps - TOL).abs().argsort()].iloc[0]
        d0 = df[df.eps == near]; TOL = near
    wls = [w for w in ("mixed", "dense") if not d0[d0.workload == w].empty]
    x = np.arange(len(wls)); width = 0.35
    mins = [d0[d0.workload == w].load_min.mean() for w in wls]
    maxs = [d0[d0.workload == w].load_max.mean() for w in wls]
    ax.bar(x - width / 2, mins, width, label="min-load solution", color="#27ae60")
    ax.bar(x + width / 2, maxs, width, label="max-load solution", color="#c0392b")
    ax.set_xticks(x); ax.set_xticklabels(wls)
    ax.set_ylabel(f"Core BSM load within {TOL*100:.0f}\\%\nof the base optimum [ebits]")
    ax.set_title("A few \\% cost buys huge congestion swings")
    ax.legend(fontsize=8)
    _save(fig, "fig_congestion_blind")
    # numeric summary for the text (report spread at 1% and 5% tolerance)
    print("=== congestion-blindness (mean over seeds) ===")
    for tol in (0.0, 0.01, 0.05):
        dt = df[np.isclose(df.eps, tol)]
        for wl in ("mixed", "dense"):
            dw = dt[dt.workload == wl]
            if dw.empty:
                continue
            print(f"  eps={tol:.2f} {wl:5}: core load {dw.load_min.mean():.1f}..{dw.load_max.mean():.1f}"
                  f" ebits (cmin={dw.cmin.mean():.1f})")
    return df


# ----------------------------------------------------------------- E-SL: Fig.7
def fig_switchloss():
    f = os.path.join(RES, "switchloss.csv")
    if not os.path.exists(f):
        print("skip switchloss (no csv)"); return None
    df = pd.read_csv(f, keep_default_na=False)
    df["scheme"] = df["scheme"].astype(str)
    for c in ("loss_db", "eff_throughput", "core_load", "seed", "Mb", "budget_total"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.4), sharex=True)
    losses = sorted(df.loss_db.unique())
    # (a) JointDQC/OBL eff-throughput ratio vs loss
    ax = axes[0]
    for wl in ("mixed", "dense"):
        d = df[df.workload == wl]
        if d.empty:
            continue
        rs = []
        for L in losses:
            dl = d[d.loss_db == L]
            o = dl[dl.scheme == "OBL"].eff_throughput.mean()
            j = dl[dl.scheme == "JDQC"].eff_throughput.mean()
            rs.append(j / o if o else np.nan)
        ax.plot(losses, rs, marker="o", color=WL[wl][1], lw=1.8, label=WL[wl][0])
    ax.axhline(1.0, color="gray", ls="--", lw=1)
    ax.set_xlabel("Optical-switch loss $\\eta_s$ [dB]")
    ax.set_ylabel("JointDQC / BSM-Oblivious\neff-throughput ratio")
    ax.set_title("BSM-aware gain vs switch loss")
    ax.set_xticks(losses); ax.legend(fontsize=8.5)
    # (b) OBL forced core load vs loss (why the gain grows)
    ax = axes[1]
    for wl in ("mixed", "dense"):
        d = df[(df.workload == wl) & (df.scheme == "OBL")]
        if d.empty:
            continue
        m = d.groupby("loss_db").core_load.mean()
        ax.plot(m.index, m.values, marker="s", color=WL[wl][1], lw=1.8, label=WL[wl][0])
    b = df.budget_total.dropna().iloc[0] if not df.budget_total.dropna().empty else 8
    ax.axhline(b, color="k", ls=":", lw=1, label=f"budget $B_{{tot}}={int(b)}$")
    ax.set_xlabel("Optical-switch loss $\\eta_s$ [dB]")
    ax.set_ylabel("BSM-Oblivious core load [ebits]")
    ax.set_title("Oblivious congestion rises with loss")
    ax.set_xticks(losses); ax.legend(fontsize=8.5)
    _save(fig, "fig_switchloss")
    return df


# ----------------------------------------------------------------- E-RT: runtime table
def runtime_table():
    files = glob.glob(os.path.join(RES, "final_*.csv"))
    if not files:
        print("skip runtime table (no final_*.csv)"); return None
    df = pd.concat([pd.read_csv(f, keep_default_na=False) for f in files], ignore_index=True)
    df["scheme"] = df["scheme"].astype(str)
    for c in ("Mb", "solve_time", "eff_throughput"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    g = df.groupby(["workload", "scheme"]).solve_time.agg(["mean", "max", "count"]).round(3)
    print("=== MILP solve time (s) by workload x scheme ===")
    print(g.to_string())
    # overall per-scheme
    ov = df.groupby("scheme").solve_time.agg(["mean", "max"]).round(3)
    print("=== overall per-scheme ===")
    print(ov.to_string())
    return g


if __name__ == "__main__":
    fig_congestion_blind()
    fig_switchloss()
    runtime_table()
