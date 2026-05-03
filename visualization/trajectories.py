"""
Phase 1 可視化: 2-agent軌道・‖ΔM(t)‖時系列・位相空間（Figure 1）
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
from ._font import setup_japanese_font
setup_japanese_font()


def plot_phase1(
    M1_hist: np.ndarray,
    M2_hist: np.ndarray,
    times: np.ndarray,
    out_path: Path,
    epsilon_band: tuple[float, float] = (0.05, 0.15),
) -> None:
    """
    Figure 1 (a-d) を生成して保存。

    Parameters
    ----------
    M1_hist, M2_hist : shape (T, d)
    times            : shape (T,)
    epsilon_band     : (ε_low, ε_high) — 非収束帯域の表示範囲
    """
    delta_M = M2_hist - M1_hist
    norm_dM = np.linalg.norm(delta_M, axis=1)
    dt = times[1] - times[0]
    d_norm = np.gradient(norm_dM, dt)

    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(2, 2, hspace=0.35, wspace=0.3)

    # (a) M空間でのΔM軌道
    ax_a = fig.add_subplot(gs[0, 0])
    sc = ax_a.scatter(
        delta_M[:, 0], delta_M[:, 1],
        c=times, cmap="viridis", s=8, alpha=0.7,
    )
    plt.colorbar(sc, ax=ax_a, label="t")
    ax_a.scatter(*delta_M[0], color="green", s=80, zorder=5, label="t=0")
    ax_a.scatter(*delta_M[-1], color="red", s=80, zorder=5, label="t=T")
    ax_a.set_xlabel(r"$\Delta M_1$")
    ax_a.set_ylabel(r"$\Delta M_2$")
    ax_a.set_title("(a) ΔM 軌道（M 空間）")
    ax_a.legend(fontsize=8)
    ax_a.grid(alpha=0.3)

    # (b) ‖ΔM(t)‖ 時系列
    ax_b = fig.add_subplot(gs[0, 1])
    ax_b.plot(times, norm_dM, color="steelblue", lw=1.5, label=r"$\|\Delta M(t)\|$")
    ax_b.axhspan(*epsilon_band, alpha=0.15, color="orange", label=r"$\varepsilon$ 帯域")
    ax_b.set_xlabel("時刻 t")
    ax_b.set_ylabel(r"$\|\Delta M\|$")
    ax_b.set_title(r"(b) $\|\Delta M(t)\|$ 時系列")
    ax_b.legend(fontsize=8)
    ax_b.grid(alpha=0.3)

    # (c) d/dt‖ΔM‖ 時系列
    ax_c = fig.add_subplot(gs[1, 0])
    ax_c.plot(times, d_norm, color="tomato", lw=1.2, label=r"$\frac{d}{dt}\|\Delta M\|$")
    ax_c.axhline(0, color="black", lw=0.8, linestyle="--")
    ax_c.set_xlabel("時刻 t")
    ax_c.set_ylabel(r"$\frac{d}{dt}\|\Delta M\|$")
    ax_c.set_title(r"(c) $\frac{d}{dt}\|\Delta M(t)\|$ 時系列")
    ax_c.legend(fontsize=8)
    ax_c.grid(alpha=0.3)

    # (d) 位相空間（‖ΔM‖ vs d/dt‖ΔM‖）
    ax_d = fig.add_subplot(gs[1, 1])
    sc_d = ax_d.scatter(
        norm_dM, d_norm,
        c=times, cmap="plasma", s=8, alpha=0.6,
    )
    plt.colorbar(sc_d, ax=ax_d, label="t")
    ax_d.axhline(0, color="black", lw=0.8, linestyle="--")
    ax_d.set_xlabel(r"$\|\Delta M\|$")
    ax_d.set_ylabel(r"$\frac{d}{dt}\|\Delta M\|$")
    ax_d.set_title(r"(d) 位相空間（$\|\Delta M\|$ vs $\dot{\|\Delta M\|}$）")
    ax_d.grid(alpha=0.3)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.suptitle("Figure 1: 2-agent System — ΔM ダイナミクス", fontsize=13, y=1.01)
    fig.savefig(out_path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"[Phase 1] 保存: {out_path}")
