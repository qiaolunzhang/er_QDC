#!/usr/bin/env python3
"""Generate publication-quality schematic figures for the JointDQC IEEE paper.

Two figures are produced, each saved as .pdf and .png into two directories:
  * jointdqc/figures/
  * overleaf_quantum_computing/figures/jointdqc/

Only matplotlib (Agg backend) is used. Run under conda env `rwa`:
    conda run -n rwa python jointdqc/plot_schematics.py
"""

import os

import matplotlib

matplotlib.use("Agg")  # non-interactive backend, no display needed

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrow
from matplotlib.lines import Line2D

# ----------------------------------------------------------------------------
# Global style: IEEEtran double-column figures are ~3.5in wide; use small fonts.
# ----------------------------------------------------------------------------
plt.rcParams.update({
    "font.size": 8,
    "font.family": "serif",
    "axes.linewidth": 0.6,
    "lines.linewidth": 0.9,
    "savefig.dpi": 200,
    "pdf.fonttype": 42,  # editable text in the PDF
    "ps.fonttype": 42,
})

# Output directories.
OUT_DIRS = [
    "/home/qiaolun/research_project/1_quantum_computing/er_QDC/"
    "repro_qdc_scheduling/jointdqc/figures/",
    "/home/qiaolun/research_project/1_quantum_computing/"
    "overleaf_quantum_computing/figures/jointdqc/",
]

# Colour palette (grayscale-friendly: distinct in luminance as well as hue).
COL_COMPUTE = "#1f5fa8"   # blue  -> computing qubits
COL_COMM = "#c0631a"      # brown/orange -> communication qubits
COL_BOX = "#333333"       # box edges / text
COL_LIGHT = "#f2f2f2"     # light box fill
COL_HILITE = "#cc2222"    # red highlight for the cross-pod path
COL_LINE = "#555555"      # neutral connecting lines


# ----------------------------------------------------------------------------
# Small reusable helpers.
# ----------------------------------------------------------------------------
def draw_box(ax, x, y, w, h, label, *, fc="white", ec=COL_BOX, lw=0.9,
             fontsize=8, rounding=0.06, fontweight="normal", text_color=COL_BOX,
             zorder=2):
    """Draw a rounded rectangle centred at (x, y) with a centred label."""
    box = FancyBboxPatch(
        (x - w / 2.0, y - h / 2.0), w, h,
        boxstyle=f"round,pad=0.0,rounding_size={rounding}",
        linewidth=lw, edgecolor=ec, facecolor=fc, zorder=zorder,
    )
    ax.add_patch(box)
    if label:
        ax.text(x, y, label, ha="center", va="center",
                fontsize=fontsize, color=text_color, fontweight=fontweight,
                zorder=zorder + 1)
    return box


def draw_qubit(ax, x, y, color, label, *, r=0.11, label_dy=-0.28,
               fontsize=7, zorder=4):
    """Draw a filled circle (a qubit) with a label placed below it."""
    ax.add_patch(Circle((x, y), r, facecolor=color, edgecolor="black",
                         linewidth=0.5, zorder=zorder))
    ax.text(x, y + label_dy, label, ha="center", va="center",
            fontsize=fontsize, color=COL_BOX, zorder=zorder)


def draw_switch(ax, x, y, label, *, w=0.62, h=0.34, fc="white",
                ec=COL_BOX, fontsize=7, lw=0.8, zorder=3):
    """Draw a network switch as a small rounded box."""
    return draw_box(ax, x, y, w, h, label, fc=fc, ec=ec, lw=lw,
                    fontsize=fontsize, rounding=0.05, zorder=zorder)


def connect(ax, p0, p1, *, color=COL_LINE, lw=0.7, ls="-", zorder=1):
    """Draw a straight connecting line between two points."""
    ax.add_line(Line2D([p0[0], p1[0]], [p0[1], p1[1]],
                        color=color, lw=lw, linestyle=ls, zorder=zorder))


def save_figure(fig, basename):
    """Save the figure as .pdf and .png into every output directory."""
    saved = []
    for d in OUT_DIRS:
        os.makedirs(d, exist_ok=True)
        for ext in ("pdf", "png"):
            path = os.path.join(d, f"{basename}.{ext}")
            fig.savefig(path, bbox_inches="tight", dpi=200)
            saved.append(path)
    plt.close(fig)
    return saved


# ----------------------------------------------------------------------------
# FIGURE 1 - remote CNOT gate via a BSM module between two QPUs.
# ----------------------------------------------------------------------------
def make_fig_remote_gate():
    fig, ax = plt.subplots(figsize=(4.6, 2.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.set_aspect("equal")
    ax.axis("off")

    # Two QPU enclosures.
    qpu_w, qpu_h = 2.4, 3.0
    qpu1_x, qpu2_x = 1.7, 8.3
    qpu_y = 2.6
    draw_box(ax, qpu1_x, qpu_y, qpu_w, qpu_h, "", fc=COL_LIGHT, lw=1.1,
             rounding=0.12)
    draw_box(ax, qpu2_x, qpu_y, qpu_w, qpu_h, "", fc=COL_LIGHT, lw=1.1,
             rounding=0.12)
    ax.text(qpu1_x, qpu_y + qpu_h / 2 + 0.28, r"QPU$_1$", ha="center",
            va="center", fontsize=9, fontweight="bold", color=COL_BOX)
    ax.text(qpu2_x, qpu_y + qpu_h / 2 + 0.28, r"QPU$_2$", ha="center",
            va="center", fontsize=9, fontweight="bold", color=COL_BOX)

    # Qubits inside QPU1 (computing on top, communication near the centre).
    q_cp1 = (qpu1_x, qpu_y + 0.85)
    q_cm1 = (qpu1_x + 0.85, qpu_y - 0.55)
    draw_qubit(ax, *q_cp1, COL_COMPUTE, r"$q_{cp1}$")
    draw_qubit(ax, *q_cm1, COL_COMM, r"$q_{cm1}$")

    # Qubits inside QPU2 (mirrored).
    q_cp2 = (qpu2_x, qpu_y + 0.85)
    q_cm2 = (qpu2_x - 0.85, qpu_y - 0.55)
    draw_qubit(ax, *q_cp2, COL_COMPUTE, r"$q_{cp2}$")
    draw_qubit(ax, *q_cm2, COL_COMM, r"$q_{cm2}$")

    # Local links between computing and communication qubits.
    connect(ax, q_cp1, q_cm1, color=COL_BOX, lw=0.8)
    connect(ax, q_cp2, q_cm2, color=COL_BOX, lw=0.8)

    # Central BSM module (diamond) between the communication qubits.
    bsm_x, bsm_y = 5.0, q_cm1[1]
    diamond = plt.Polygon(
        [(bsm_x, bsm_y + 0.5), (bsm_x + 0.7, bsm_y),
         (bsm_x, bsm_y - 0.5), (bsm_x - 0.7, bsm_y)],
        closed=True, facecolor="white", edgecolor=COL_BOX, linewidth=1.0,
        zorder=3)
    ax.add_patch(diamond)
    ax.text(bsm_x, bsm_y, "BSM", ha="center", va="center", fontsize=7.5,
            fontweight="bold", color=COL_BOX, zorder=4)

    # Lines from communication qubits into the BSM module.
    connect(ax, q_cm1, (bsm_x - 0.7, bsm_y), color=COL_COMM, lw=1.0)
    connect(ax, q_cm2, (bsm_x + 0.7, bsm_y), color=COL_COMM, lw=1.0)

    # Jagged / dashed "ebit" entanglement link drawn as a zigzag.
    zx = [q_cm1[0], 3.0, 3.4, 3.0, 3.4, bsm_x - 0.7]
    ebit_y = bsm_y
    zy = [ebit_y, ebit_y + 0.18, ebit_y - 0.18, ebit_y + 0.18,
          ebit_y - 0.18, ebit_y]
    ax.add_line(Line2D(zx, zy, color=COL_COMM, lw=0.9, linestyle="--",
                       zorder=2))
    ax.text(3.2, ebit_y + 0.55, "ebit", ha="center", va="center",
            fontsize=7, style="italic", color=COL_COMM)

    # Dashed classical-communication arrow between the QPUs (top).
    cc_y = qpu_y + qpu_h / 2 - 0.15
    ax.annotate("", xy=(qpu2_x - qpu_w / 2, cc_y),
                xytext=(qpu1_x + qpu_w / 2, cc_y),
                arrowprops=dict(arrowstyle="<->", linestyle="--",
                                color=COL_BOX, lw=0.9))
    ax.text(5.0, cc_y + 0.30, "classical comm.", ha="center", va="center",
            fontsize=7, color=COL_BOX)

    # Tiny legend for qubit colours.
    legend_handles = [
        Line2D([0], [0], marker="o", color="none",
               markerfacecolor=COL_COMPUTE, markeredgecolor="black",
               markersize=7, label="computing qubit"),
        Line2D([0], [0], marker="o", color="none",
               markerfacecolor=COL_COMM, markeredgecolor="black",
               markersize=7, label="communication qubit"),
    ]
    ax.legend(handles=legend_handles, loc="lower center", ncol=2,
              fontsize=6.5, frameon=False, handletextpad=0.3,
              columnspacing=1.0, bbox_to_anchor=(0.5, -0.02))

    return save_figure(fig, "fig_remote_gate")


# ----------------------------------------------------------------------------
# FIGURE 2 - 3-tier fat-tree (4 pods) annotated with the BSM budget.
# ----------------------------------------------------------------------------
def make_fig_fabric():
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 11)
    ax.axis("off")

    # Vertical tier positions.
    y_core = 10.0
    y_agg = 7.6
    y_edge = 5.0
    y_qpu = 2.2

    # --- Bottom tier: 16 QPUs in 4 pods (4 QPUs each) -----------------------
    # Capacity pattern {8, 12, 16, 20} cycled across the QPUs.
    cap_pattern = [8, 12, 16, 20]
    qpu_positions = []  # (x, y) per QPU, ordered pod0..pod3
    pod_span = 16.0 / 4.0
    qpu_w, qpu_h = 0.66, 0.5
    for pod in range(4):
        pod_left = pod * pod_span
        # four QPUs spread across the pod's horizontal band
        for k in range(4):
            x = pod_left + 0.9 + k * ((pod_span - 1.4) / 3.0)
            qpu_positions.append((x, y_qpu))

    # --- Lower-middle tier: 8 edge switches (2 per pod) ---------------------
    edge_positions = []
    for pod in range(4):
        pod_left = pod * pod_span
        for k in range(2):
            x = pod_left + 1.35 + k * (pod_span - 2.7)
            edge_positions.append((x, y_edge))

    # --- Middle tier: 4 aggregation switches (1 per pod) --------------------
    agg_positions = []
    for pod in range(4):
        x = pod * pod_span + pod_span / 2.0
        agg_positions.append((x, y_agg))

    # --- Top tier: 2 core switches ------------------------------------------
    core_positions = [(6.0, y_core), (10.0, y_core)]

    # Highlighted cross-pod path: pod0 QPU -> E -> A -> Cr -> A -> E -> pod3 QPU.
    hi_qpu_src = 0          # first QPU in pod 0
    hi_qpu_dst = 12         # first QPU in pod 3
    hi_edge_src = 0         # pod 0, edge 0
    hi_edge_dst = 6         # pod 3, edge 0
    hi_agg_src = 0
    hi_agg_dst = 3
    hi_core = 0

    def is_hi_line(kind, a, b):
        """Return True if a connecting segment lies on the highlighted path."""
        if kind == "qe":
            return (a == hi_qpu_src and b == hi_edge_src) or \
                   (a == hi_qpu_dst and b == hi_edge_dst)
        if kind == "ea":
            return (a == hi_edge_src and b == hi_agg_src) or \
                   (a == hi_edge_dst and b == hi_agg_dst)
        if kind == "ac":
            return (a == hi_agg_src and b == hi_core) or \
                   (a == hi_agg_dst and b == hi_core)
        return False

    # --- Pod background shading (behind everything) -------------------------
    for pod in range(4):
        pod_left = pod * pod_span
        rect = Rectangle((pod_left + 0.25, y_qpu - qpu_h / 2 - 0.45),
                         pod_span - 0.5,
                         (y_edge + 0.55) - (y_qpu - qpu_h / 2 - 0.45),
                         facecolor="#eef2f7", edgecolor="#c8d2de",
                         linewidth=0.6, zorder=0)
        ax.add_patch(rect)
        ax.text(pod_left + pod_span / 2.0, y_qpu - qpu_h / 2 - 0.75,
                f"Pod {pod}", ha="center", va="center", fontsize=7.5,
                fontweight="bold", color="#556",)

    # --- Draw connecting lines first (so boxes sit on top) ------------------
    # QPU -> edge switch (each QPU to the nearer of its pod's two edges).
    for qi, (qx, qy) in enumerate(qpu_positions):
        pod = qi // 4
        within = qi % 4
        edge_idx = pod * 2 + (0 if within < 2 else 1)
        ex, ey = edge_positions[edge_idx]
        hi = is_hi_line("qe", qi, edge_idx)
        connect(ax, (qx, qy + qpu_h / 2), (ex, ey - 0.17),
                color=COL_HILITE if hi else COL_LINE,
                lw=1.4 if hi else 0.6, zorder=2 if hi else 1)

    # edge -> aggregation switch.
    for ei, (ex, ey) in enumerate(edge_positions):
        pod = ei // 2
        ax_, ay = agg_positions[pod]
        hi = is_hi_line("ea", ei, pod)
        connect(ax, (ex, ey + 0.17), (ax_, ay - 0.17),
                color=COL_HILITE if hi else COL_LINE,
                lw=1.4 if hi else 0.6, zorder=2 if hi else 1)

    # aggregation -> BOTH core switches (fully connected).
    for ai, (ax_, ay) in enumerate(agg_positions):
        for ci, (cx, cy) in enumerate(core_positions):
            hi = is_hi_line("ac", ai, ci)
            connect(ax, (ax_, ay + 0.17), (cx, cy - 0.17),
                    color=COL_HILITE if hi else COL_LINE,
                    lw=1.4 if hi else 0.6, zorder=2 if hi else 1)

    # --- Draw the switches / QPUs on top ------------------------------------
    for ci, (cx, cy) in enumerate(core_positions):
        draw_switch(ax, cx, cy, f"Cr$_{ci}$", w=0.9, h=0.42, fontsize=7.5,
                    fc="#dfe8f3")
    for ai, (ax_, ay) in enumerate(agg_positions):
        draw_switch(ax, ax_, ay, f"A$_{ai}$", fc="#e8ecef")
    for ei, (ex, ey) in enumerate(edge_positions):
        draw_switch(ax, ex, ey, f"E$_{ei}$", w=0.56, h=0.32, fontsize=6.8,
                    fc="white")
    for qi, (qx, qy) in enumerate(qpu_positions):
        cap = cap_pattern[qi % 4]
        draw_box(ax, qx, qy, qpu_w, qpu_h, f"Q{qi}", fc="white",
                 ec=COL_BOX, lw=0.7, fontsize=6.2, rounding=0.03, zorder=3)
        ax.text(qx, qy - qpu_h / 2 - 0.18, f"c={cap}", ha="center",
                va="center", fontsize=5.8, color="#666")

    # --- Tier annotations (right/left labels) -------------------------------
    ax.text(15.9, y_core + 0.05, "core switches\n" r"budget $B_{tot}$",
            ha="right", va="center", fontsize=7, color="#334", style="italic")
    ax.text(0.05, y_agg + 0.75, "aggregation", ha="left", va="bottom",
            fontsize=7, color="#334", style="italic")
    ax.text(0.05, y_edge + 0.75, "edge", ha="left", va="bottom",
            fontsize=7, color="#334", style="italic")

    # --- Cross-pod BSM annotation -------------------------------------------
    ax.text(8.0, y_core + 0.75,
            r"$n_s{=}5$: 5 BSMs per cross-pod ebit",
            ha="center", va="center", fontsize=7.5, color=COL_HILITE,
            fontweight="bold")

    # Small legend for the highlighted path.
    legend_handles = [
        Line2D([0], [0], color=COL_HILITE, lw=1.6,
               label="cross-pod path (E-A-Cr-A-E)"),
        Line2D([0], [0], color=COL_LINE, lw=0.8, label="fabric link"),
    ]
    ax.legend(handles=legend_handles, loc="lower center", ncol=2,
              fontsize=6.2, frameon=False, handletextpad=0.5,
              columnspacing=1.2, bbox_to_anchor=(0.5, -0.06))

    return save_figure(fig, "fig_fabric")


def main():
    saved = []
    saved += make_fig_remote_gate()
    saved += make_fig_fabric()
    print(f"Saved {len(saved)} files:")
    for p in saved:
        print("  " + p)


if __name__ == "__main__":
    main()
