"""
Phase 3 可視化: 共鳴条件位相空間・Lyapunov関数・非収束アトラクター（Figure 3）
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
from ._font import setup_japanese_font
setup_japanese_font()


def plot_phase3(
    times: np.ndarray,
    resonance_records: list[dict],   # check_resonance() の結果リスト（T個）
    V_series: np.ndarray,            # Lyapunov V(t)
    dV_series: np.ndarray,           # dV/dt
    norm_dM_series: np.ndarray,      # ‖ΔM‖ 時系列（代表ペア）
    out_path: Path,
) -> None:
    """Figure 3 (a-d) を生成して保存"""
    CM = np.array([r["VarE"] for r in resonance_records])
    CU = np.array([r["rangeU"] for r in resonance_records])
    CV = np.array([r["VarCV"] for r in resonance_records])
    res_flag = np.array([r["resonance"] for r in resonance_records], dtype=bool)

    fig = plt.figure(figsize=(14, 11))
    gs = gridspec.GridSpec(2, 2, hspace=0.38, wspace=0.32)

    # (a) (CM値, CU値, CV値) の3変数時系列 + 共鳴フラグ
    ax_a = fig.add_subplot(gs[0, 0])
    ax_a.plot(times, CM, label="VarE (CM指標)", color="steelblue", lw=1.4)
    ax_a.plot(times, CU, label="rangeU (CU指標)", color="tomato", lw=1.4)
    ax_a.plot(times, CV, label="VarCV (CV指標)", color="seagreen", lw=1.4)
    # 共鳴領域を背景塗りつぶし
    ax_a.fill_between(times, 0, ax_a.get_ylim()[1] if ax_a.get_ylim()[1] > 0 else 1.0,
                      where=res_flag, alpha=0.12, color="gold", label="Resonance")
    ax_a.set_xlabel("時刻 t")
    ax_a.set_title("(a) CM・CU・CV 指標の時系列")
    ax_a.legend(fontsize=7)
    ax_a.grid(alpha=0.3)

    # (b) CM-CU 散布図（共鳴/非共鳴を色分け）
    ax_b = fig.add_subplot(gs[0, 1])
    colors = np.where(res_flag, "gold", "slategray")
    ax_b.scatter(CM, CU, c=colors, s=6, alpha=0.6)
    ax_b.set_xlabel("VarE（CM 指標）")
    ax_b.set_ylabel("rangeU（CU 指標）")
    ax_b.set_title("(b) CM-CU 位相空間（金: Resonance）")
    ax_b.grid(alpha=0.3)
    # 閾値ライン
    ax_b.axvline(0.2, color="steelblue", lw=0.8, linestyle="--", alpha=0.7, label="θ_M")
    ax_b.axhline(0.3, color="tomato", lw=0.8, linestyle="--", alpha=0.7, label="θ_U")
    ax_b.legend(fontsize=8)

    # (c) Lyapunov V(t) と dV/dt
    ax_c = fig.add_subplot(gs[1, 0])
    ax_c2 = ax_c.twinx()
    l1, = ax_c.plot(times, V_series, color="navy", lw=1.5, label="V(t)")
    l2, = ax_c2.plot(times, dV_series, color="darkorange", lw=1.2, alpha=0.8, label="dV/dt")
    ax_c2.axhline(0, color="black", lw=0.7, linestyle="--")
    ax_c.set_xlabel("時刻 t")
    ax_c.set_ylabel("V(t)", color="navy")
    ax_c2.set_ylabel("dV/dt", color="darkorange")
    ax_c.set_title("(c) Lyapunov 関数 V(t) と dV/dt")
    lines = [l1, l2]
    ax_c.legend(lines, [l.get_label() for l in lines], fontsize=8)
    ax_c.grid(alpha=0.3)

    # (d) ‖ΔM‖ 非収束アトラクター可視化（ヒストグラム + 軌道）
    ax_d = fig.add_subplot(gs[1, 1])
    tail_start = len(times) // 2
    tail_norms = norm_dM_series[tail_start:]
    ax_d.plot(times, norm_dM_series, color="mediumslateblue", lw=1.0, alpha=0.7, label=r"$\|\Delta M(t)\|$")
    ax_d.axhspan(np.min(tail_norms), np.max(tail_norms), alpha=0.15, color="orange",
                 label=f"アトラクター域: [{np.min(tail_norms):.3f}, {np.max(tail_norms):.3f}]")
    ax_d.set_xlabel("時刻 t")
    ax_d.set_ylabel(r"$\|\Delta M\|$")
    ax_d.set_title(r"(d) 非収束的アトラクター領域 $B$")
    ax_d.legend(fontsize=8)
    ax_d.grid(alpha=0.3)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.suptitle("Figure 3: Resonance 条件の数値検証", fontsize=13, y=1.01)
    fig.savefig(out_path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"[Phase 3] 保存: {out_path}")
