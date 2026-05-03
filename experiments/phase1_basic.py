"""
Phase 1: 2-agent 基礎検証（Section 2.4 Toy Example）

検証項目:
  - Lemma 2.1 (scale separation) の数値的実証
  - lim_sup ‖ΔM‖ > 0（非収束性公理）
  - ∃T, ∀t>T: ‖ΔM‖ < ε₀（有界性）
  - -δ < d/dt‖ΔM‖ < δ（緩やかな変化）

出力: outputs/phase1/figure1.png + コンソール検証レポート
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import yaml
from core.agent import Agent
from core.dynamics import interaction_f, alpha_periodic
from analysis.metrics import compute_metrics, lim_sup_approx
from visualization.trajectories import plot_phase1


def run(cfg: dict, out_dir: Path) -> dict:
    """Phase 1 シミュレーション本体"""
    T_max = cfg["T_max"]
    dt = cfg["dt"]
    steps = int(T_max / dt)

    # 初期状態
    M1 = np.array(cfg["M1_init"], dtype=float)
    M2 = np.array(cfg["M2_init"], dtype=float)

    M1_hist = [M1.copy()]
    M2_hist = [M2.copy()]

    r_rep = cfg["r_rep"]
    c_rep = cfg["c_rep"]
    c_att = cfg["c_att"]

    # 時間発展（オイラー法）
    for step in range(steps):
        t = step * dt
        alpha = alpha_periodic(t, cfg["alpha_base"], cfg["alpha_amp"], cfg["alpha_freq"])
        delta_M = M2 - M1

        dM1 = interaction_f(alpha, delta_M, r_rep, c_rep, c_att)
        dM2 = interaction_f(alpha, -delta_M, r_rep, c_rep, c_att)

        M1 = M1 + dM1 * dt
        M2 = M2 + dM2 * dt
        M1_hist.append(M1.copy())
        M2_hist.append(M2.copy())

    M1_arr = np.array(M1_hist)
    M2_arr = np.array(M2_hist)
    times = np.linspace(0, T_max, len(M1_arr))

    # 指標計算
    norm_dM = np.linalg.norm(M2_arr - M1_arr, axis=1)
    metrics = compute_metrics(norm_dM, dt)
    limsup = lim_sup_approx(norm_dM)

    # 可視化
    out_dir.mkdir(parents=True, exist_ok=True)
    plot_phase1(M1_arr, M2_arr, times, out_dir / "figure1.png",
                epsilon_band=cfg["epsilon_band"])

    return {"metrics": metrics, "times": times, "norm_dM": norm_dM, "limsup": limsup}


def report(result: dict) -> None:
    """検証結果をコンソールに出力"""
    m = result["metrics"]
    print("\n" + "=" * 55)
    print("  Phase 1: 2-agent System 検証レポート")
    print("=" * 55)
    print(f"  ‖ΔM(0)‖         : {result['norm_dM'][0]:.4f}")
    print(f"  lim_sup ‖ΔM‖    : {m['lim_sup']:.4f}  {'✓ >0 (非収束公理支持)' if m['non_convergent'] else '✗ ≈0 (収束)'}")
    print(f"  lim_inf ‖ΔM‖    : {m['lim_inf']:.4f}")
    print(f"  後半平均 ‖ΔM‖   : {m['mean_tail']:.4f}  (±{m['std_tail']:.4f})")
    print(f"  後半 d/dt 最大   : {max(abs(m['d_norm'][len(m['d_norm'])//2:])):.5f}")
    print("-" * 55)
    ok_limsup = m["non_convergent"]
    ok_bounded = m["lim_sup"] < 5.0  # 有界性の粗い判定
    ok_slow = max(abs(m["d_norm"][len(m["d_norm"]) // 2 :])) < 0.5
    print(f"  [{'PASS' if ok_limsup else 'FAIL'}] lim_sup > 0  （非収束性公理）")
    print(f"  [{'PASS' if ok_bounded else 'FAIL'}] ‖ΔM‖ < 5.0 （有界性）")
    print(f"  [{'PASS' if ok_slow else 'FAIL'}] |d/dt‖ΔM‖| < 0.5 （緩やかな変化）")
    print("=" * 55)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "config" / "scenarios.yaml"
    with open(cfg_path) as f:
        all_cfg = yaml.safe_load(f)
    cfg = all_cfg["phase1"]

    result = run(cfg, root / "outputs" / "phase1")
    report(result)
