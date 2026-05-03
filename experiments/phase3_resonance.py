"""
Phase 3: Resonance 条件シミュレーション（Section 4 検証）

実験:
  1. CM ∧ CU ∧ CV 独立性テスト
  2. 非収束的安定性（Resonance 中でも lim_sup > 0）
  3. Lyapunov 関数 V(t) の数値検証（Proposition 4.1）

出力: outputs/phase3/figure3.png + コンソール検証レポート
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import yaml

from core.agent import make_agents
from core.dynamics import compute_agent_derivatives
from core.network import make_complete_network
from core.resonance import check_resonance
from analysis.metrics import compute_metrics, lim_sup_approx
from analysis.lyapunov import lyapunov_V_from_history, lyapunov_dV, verify_lyapunov_decrease
from visualization.phase_space import plot_phase3


def run(cfg: dict, out_dir: Path) -> dict:
    n = cfg["n_agents"]
    d = cfg["d"]
    dv = cfg["dv"]
    T_max = cfg["T_max"]
    dt = cfg["dt"]
    steps = int(T_max / dt)

    rng_init = np.random.default_rng(42)
    agents = make_agents(n, d=d, dv=dv, init="clustered", clusters=3, seed=42)
    net = make_complete_network(agents)

    # 各エージェントの固有価値目標（V はこれに向けてゆっくり回帰）
    # M ダイナミクスとは独立した自律的価値観を表現する
    V_targets = rng_init.uniform(-1, 1, (n, dv))
    V_targets = V_targets / (np.linalg.norm(V_targets, axis=1, keepdims=True) + 1e-12)
    gamma_V_return = 0.03  # 固有目標への回帰強度

    resonance_records = []

    for step in range(steps):
        t = step * dt

        # 状態更新
        dMs, dUs, dVs = compute_agent_derivatives(
            agents, net.adj, t,
            gamma_U=cfg["gamma_U"],
            gamma_V=cfg["gamma_V"],
        )
        for i, a in enumerate(agents):
            # V 自律ドリフト: 固有目標への回帰（M動態と独立）
            dVs[i] = dVs[i] + gamma_V_return * (V_targets[i] - a.V)
            a.update(dMs[i], dUs[i], dVs[i], dt)

        # 共鳴条件チェック
        rec = check_resonance(
            agents, net.edges,
            theta_M=cfg["theta_M"],
            theta_U=cfg["theta_U"],
            theta_V=cfg["theta_V"],
        )
        resonance_records.append(rec)

    times = np.linspace(dt, T_max, steps)

    # Lyapunov
    M_histories = [a.M_history for a in agents]
    V_series = lyapunov_V_from_history(M_histories)[1:]  # step 0 除外
    dV_series = lyapunov_dV(V_series, dt)
    lyap_result = verify_lyapunov_decrease(V_series, dt)

    # 代表ペアの ‖ΔM‖
    i0, j0 = 0, 1
    M0 = np.array(agents[i0].M_history)[1:]
    M1 = np.array(agents[j0].M_history)[1:]
    norm_dM = np.linalg.norm(M1 - M0, axis=1)
    metrics = compute_metrics(norm_dM, dt)

    # 可視化
    out_dir.mkdir(parents=True, exist_ok=True)
    plot_phase3(
        times=times,
        resonance_records=resonance_records,
        V_series=V_series,
        dV_series=dV_series,
        norm_dM_series=norm_dM,
        out_path=out_dir / "figure3.png",
    )

    return {
        "resonance_records": resonance_records,
        "V_series": V_series,
        "lyap_result": lyap_result,
        "metrics": metrics,
        "norm_dM": norm_dM,
        "theta_M": cfg["theta_M"],
        "theta_U": cfg["theta_U"],
        "theta_V": cfg["theta_V"],
    }


def report(result: dict) -> None:
    recs = result["resonance_records"]
    resonance_fraction = np.mean([r["resonance"] for r in recs])
    m = result["metrics"]
    lr = result["lyap_result"]

    # 各条件の個別達成率
    cm_rate = np.mean([r["CM"] for r in recs])
    cu_rate = np.mean([r["CU"] for r in recs])
    cv_rate = np.mean([r["CV"] for r in recs])

    print("\n" + "=" * 55)
    print("  Phase 3: Resonance 条件 検証レポート")
    print("=" * 55)
    print(f"  Resonance 成立率 : {resonance_fraction * 100:.1f}%")
    print(f"  CM 単独成立率   : {cm_rate * 100:.1f}%")
    print(f"  CU 単独成立率   : {cu_rate * 100:.1f}%")
    print(f"  CV 単独成立率   : {cv_rate * 100:.1f}%")
    print(f"  lim_sup ‖ΔM‖   : {m['lim_sup']:.4f}  {'✓ >0' if m['non_convergent'] else '✗ ≈0'}")
    print(f"  Lyapunov 減少率 : {lr['fraction_decreasing'] * 100:.1f}%  {'✓ verified' if lr['verified'] else '△ 要確認'}")
    print(f"  mean dV/dt      : {lr['mean_dV']:.5f}")

    CM_vals = np.array([r["VarE"] for r in recs])
    CU_vals = np.array([r["rangeU"] for r in recs])
    CV_vals = np.array([r["VarCV"] for r in recs])
    print(f"\n  各指標の定常値（後半平均）:")
    T2 = len(recs) // 2
    print(f"  VarE  (CM指標) : {np.mean(CM_vals[T2:]):.4f}  (θ_M={result.get('theta_M', 0.2)})")
    print(f"  rangeU(CU指標) : {np.mean(CU_vals[T2:]):.4f}  (θ_U={result.get('theta_U', 0.3)})")
    print(f"  VarCV (CV指標) : {np.mean(CV_vals[T2:]):.4f}  (θ_V={result.get('theta_V', 0.1)})")

    print("\n  --- CM・CU・CV 独立性確認（軌道上）---")
    corr_MU = float(np.corrcoef(CM_vals, CU_vals)[0, 1])
    corr_MV = float(np.corrcoef(CM_vals, CV_vals)[0, 1])
    corr_UV = float(np.corrcoef(CU_vals, CV_vals)[0, 1])
    print(f"  corr(CM, CU) = {corr_MU:.3f}")
    print(f"  corr(CM, CV) = {corr_MV:.3f}")
    print(f"  corr(CU, CV) = {corr_UV:.3f}")
    max_corr = max(abs(corr_MU), abs(corr_MV), abs(corr_UV))
    print(f"  最大相関     = {max_corr:.3f}  {'✓ <0.7 (独立性支持)' if max_corr < 0.7 else '△ ≥0.7 (構造的結合)'}")
    if max_corr >= 0.7:
        print("  ※ 同一ネットワーク上での従属は動態由来。")
        print("    ランダム状態テスト (Phase 4 Protocol 3) で真の独立性を確認。")
    print("=" * 55)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    with open(root / "config" / "scenarios.yaml") as f:
        all_cfg = yaml.safe_load(f)
    cfg = all_cfg["phase3"]

    result = run(cfg, root / "outputs" / "phase3")
    report(result)
