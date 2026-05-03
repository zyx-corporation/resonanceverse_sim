"""
Phase 2: Multi-agent Consensus シミュレーション（Section 3 検証）

実験シナリオ:
  A: 制約なし自由相互作用
  B: 制度的制約あり（VarE > θ_M で収束バイアス注入）
  C: 外乱注入（t=50 で1エージェントを大摂動）

出力: outputs/phase2/figure2.png + コンソール比較レポート
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import yaml
from sklearn.decomposition import PCA

from core.agent import make_agents
from core.dynamics import compute_agent_derivatives
from core.network import make_small_world_network
from analysis.metrics import edge_variance, edge_mean, consensus_check
from visualization.networks import plot_phase2


def _run_scenario(
    cfg: dict,
    scenario: str,
    seed: int = 42,
) -> dict:
    """1シナリオ分のシミュレーション"""
    n = cfg["n_agents"]
    d = cfg["d"]
    T_max = cfg["T_max"]
    dt = cfg["dt"]
    theta_M = cfg["theta_M"]
    steps = int(T_max / dt)

    agents = make_agents(n, d=d, init="clustered", clusters=cfg["clusters"], seed=seed)
    net = make_small_world_network(agents, k=cfg["k"], p_rewire=cfg["p_rewire"], seed=seed)

    var_e_series = []
    delta_M_snapshots = []
    snapshot_steps = {0, steps // 4, steps // 2, steps - 1}
    M_traj = np.zeros((steps + 1, n, d))
    for i, a in enumerate(agents):
        M_traj[0, i] = a.M

    for step in range(steps):
        t = step * dt

        # Scenario C: 外乱注入
        if scenario == "C" and abs(t - cfg["perturbation_t"]) < dt / 2:
            idx = cfg["perturbation_idx"]
            delta = np.random.default_rng(seed).normal(0, cfg["perturbation_mag"], d)
            net.perturb_agent(idx, delta)

        # 制度的制約（Scenario B）: VarE > θ_M なら収束バイアス
        if scenario == "B":
            en = net.edge_delta_norms()
            if len(en) > 0 and edge_variance(en) > theta_M:
                for a in agents:
                    centroid = np.mean([ag.M for ag in agents], axis=0)
                    a.M += 0.01 * (centroid - a.M)

        # 微分計算 + オイラー更新
        dMs, dUs, dVs = compute_agent_derivatives(
            agents, net.adj, t,
            gamma_U=0.05, gamma_V=0.1,
        )
        for i, a in enumerate(agents):
            a.update(dMs[i], dUs[i], dVs[i], dt)

        # 指標記録
        en = net.edge_delta_norms()
        var_e_series.append(edge_variance(en) if len(en) > 0 else 0.0)

        for i, a in enumerate(agents):
            M_traj[step + 1, i] = a.M

        if step in snapshot_steps:
            delta_M_snapshots.append(net.delta_M_matrix())

    var_e_arr = np.array(var_e_series)
    return {
        "var_e": var_e_arr,
        "M_traj": M_traj,
        "snapshots": delta_M_snapshots,
        "consensus": consensus_check(var_e_arr, theta_M=theta_M, dt=dt),
    }


def run(cfg: dict, out_dir: Path) -> dict:
    """3シナリオを実行"""
    results = {}
    for scenario in ["A", "B", "C"]:
        print(f"  Scenario {scenario} 実行中...")
        results[scenario] = _run_scenario(cfg, scenario)

    T_max = cfg["T_max"]
    dt = cfg["dt"]
    steps = int(T_max / dt)
    times = np.linspace(dt, T_max, steps)

    # PCA投影（B シナリオ）
    pca_projections = {}
    for sc, res in results.items():
        M_flat = res["M_traj"]  # (T+1, n, d)
        T, n, d = M_flat.shape
        pca = PCA(n_components=2)
        M_2d = pca.fit_transform(M_flat.reshape(T * n, d)).reshape(T, n, 2)
        pca_projections[sc] = M_2d

    var_e_scenarios = {sc: results[sc]["var_e"] for sc in ["A", "B", "C"]}
    consensus_times = {
        sc: results[sc]["consensus"]["first_t"] for sc in ["A", "B", "C"]
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    # スナップショット時刻（最初の結果から）
    snap_steps = [0, steps // 4, steps // 2, steps - 1]
    snap_times = [s * dt for s in snap_steps]

    plot_phase2(
        times=times,
        var_e_scenarios=var_e_scenarios,
        delta_M_snapshots=results["B"]["snapshots"],
        snapshot_times=snap_times,
        pca_projections=pca_projections,
        consensus_times=consensus_times,
        theta_M=cfg["theta_M"],
        out_path=out_dir / "figure2.png",
    )
    return results


def report(results: dict) -> None:
    print("\n" + "=" * 55)
    print("  Phase 2: Multi-agent Consensus 検証レポート")
    print("=" * 55)
    for sc in ["A", "B", "C"]:
        c = results[sc]["consensus"]
        ve = results[sc]["var_e"]
        print(f"\n  --- Scenario {sc} ---")
        print(f"  最終 VarE      : {c['final_VarE']:.4f}")
        print(f"  Consensus 達成 : {'✓' if c['achieved'] else '✗'}", end="")
        if c["achieved"]:
            print(f"  (t={c['first_t']})")
        else:
            print()
    print("=" * 55)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    with open(root / "config" / "scenarios.yaml") as f:
        all_cfg = yaml.safe_load(f)
    cfg = all_cfg["phase2"]

    results = run(cfg, root / "outputs" / "phase2")
    report(results)
