"""
Phase 2 可視化: ΔMネットワーク・VarE時系列・エージェント軌道PCA（Figure 2）
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
from ._font import setup_japanese_font
setup_japanese_font()


def plot_phase2(
    times: np.ndarray,
    var_e_scenarios: dict[str, np.ndarray],   # {"A": ..., "B": ..., "C": ...}
    delta_M_snapshots: list[np.ndarray],       # list of (n,n) matrices at key times
    snapshot_times: list[float],
    pca_projections: dict[str, np.ndarray],    # {"scenario": (T, n, 2)}
    consensus_times: dict[str, float | None],
    theta_M: float,
    out_path: Path,
) -> None:
    """Figure 2 (a-d) を生成して保存"""
    fig = plt.figure(figsize=(15, 11))
    gs = gridspec.GridSpec(2, 2, hspace=0.4, wspace=0.3)

    # (a) ΔMネットワーク ヒートマップ（スナップショット）
    ax_a = fig.add_subplot(gs[0, 0])
    n_snaps = min(len(delta_M_snapshots), 4)
    n_agents = delta_M_snapshots[0].shape[0]
    combined = np.zeros((n_agents, n_agents * n_snaps))
    for k, mat in enumerate(delta_M_snapshots[:n_snaps]):
        combined[:, k * n_agents : (k + 1) * n_agents] = mat
    im = ax_a.imshow(combined, aspect="auto", cmap="YlOrRd")
    plt.colorbar(im, ax=ax_a, label=r"$\|\Delta M_{ij}\|$")
    ax_a.set_xticks(
        [int((k + 0.5) * n_agents) for k in range(n_snaps)],
        labels=[f"t={snapshot_times[k]:.0f}" for k in range(n_snaps)],
    )
    ax_a.set_yticks(range(n_agents), labels=[f"A{i}" for i in range(n_agents)])
    ax_a.set_title("(a) ΔM ネットワーク ヒートマップ（時間発展）")

    # (b) VarE(t) 時系列（3シナリオ比較）
    ax_b = fig.add_subplot(gs[0, 1])
    colors = {"A": "tomato", "B": "steelblue", "C": "seagreen"}
    for name, ve in var_e_scenarios.items():
        ax_b.plot(times, ve, color=colors.get(name, "gray"), lw=1.5, label=f"Scenario {name}")
        ct = consensus_times.get(name)
        if ct is not None:
            ax_b.axvline(times[int(ct)], color=colors.get(name, "gray"),
                         linestyle=":", alpha=0.7)
    ax_b.axhline(theta_M, color="black", lw=1.0, linestyle="--", label=rf"$\theta_M={theta_M}$")
    ax_b.set_xlabel("時刻 t")
    ax_b.set_ylabel("VarE(t)")
    ax_b.set_title("(b) VarE(t) 時系列（3シナリオ比較）")
    ax_b.legend(fontsize=8)
    ax_b.grid(alpha=0.3)

    # (c) エージェント軌道の2D PCA投影（Scenario B）
    ax_c = fig.add_subplot(gs[1, 0])
    key = "B" if "B" in pca_projections else list(pca_projections.keys())[0]
    proj = pca_projections[key]  # (T, n, 2)
    n_ag = proj.shape[1]
    cmap = plt.cm.tab10
    for i in range(n_ag):
        traj = proj[:, i, :]
        ax_c.plot(traj[:, 0], traj[:, 1], color=cmap(i % 10), alpha=0.6, lw=1.0)
        ax_c.scatter(*traj[0], color=cmap(i % 10), s=40, marker="o")
        ax_c.scatter(*traj[-1], color=cmap(i % 10), s=40, marker="x")
    ax_c.set_xlabel("PC1")
    ax_c.set_ylabel("PC2")
    ax_c.set_title(f"(c) エージェント軌道 PCA投影（Scenario {key}）")
    ax_c.grid(alpha=0.3)

    # (d) Consensus達成時刻の分布（棒グラフ）
    ax_d = fig.add_subplot(gs[1, 1])
    names = list(consensus_times.keys())
    cts = [
        (consensus_times[n] / len(times) * times[-1]) if consensus_times[n] is not None else times[-1]
        for n in names
    ]
    bar_colors = [colors.get(n, "gray") for n in names]
    bars = ax_d.bar(names, cts, color=bar_colors, alpha=0.75, edgecolor="black")
    ax_d.set_ylabel("Consensus 達成時刻 t")
    ax_d.set_title("(d) Consensus 達成時刻（シナリオ比較）")
    for bar, ct in zip(bars, cts):
        if ct < times[-1]:
            ax_d.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                      f"{ct:.1f}", ha="center", va="bottom", fontsize=9)
        else:
            ax_d.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2,
                      "未達成", ha="center", va="center", fontsize=9, color="white")
    ax_d.grid(axis="y", alpha=0.3)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.suptitle("Figure 2: Multi-agent Consensus — ΔM ネットワークダイナミクス", fontsize=13, y=1.01)
    fig.savefig(out_path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"[Phase 2] 保存: {out_path}")
