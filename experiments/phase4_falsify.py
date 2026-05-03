"""
Phase 4: Falsifiability Protocol 実証（Appendix D 対応）

Protocol 1: 非収束性の反証テスト — 異ドメインで ΔM → 0 が起きるか
Protocol 3: CM, CU, CV 独立性テスト — ランダム状態での相関測定

出力: outputs/phase4/figure4.png + コンソール検証レポート
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import yaml
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from joblib import Parallel, delayed

# 日本語フォント設定
import matplotlib.font_manager as _fm
for _name in ["Hiragino Sans", "Yu Gothic", "Noto Sans CJK JP", "IPAexGothic"]:
    if _name in {f.name for f in _fm.fontManager.ttflist}:
        matplotlib.rc("font", family=_name)
        break

from core.agent import Agent
from core.dynamics import interaction_f
from core.resonance import check_CM, check_CU, check_CV


# ======== Protocol 1: 非収束性テスト ========

def _single_trial(domain_params: dict, T_max: float = 50, dt: float = 0.01, seed: int = 0) -> dict:
    """1試行: 2-agent シミュレーション → 最終 ‖ΔM‖ が収束したか"""
    rng = np.random.default_rng(seed)
    M1 = rng.uniform(-1, 1, 2)
    M2 = rng.uniform(-1, 1, 2)

    alpha_base = domain_params.get("alpha_base", 0.7)
    r_rep = domain_params.get("r_rep", 0.1)
    c_att = domain_params.get("c_att", 0.3)

    steps = int(T_max / dt)
    for step in range(steps):
        t = step * dt
        alpha = alpha_base + 0.1 * np.sin(0.1 * t)
        dM = M2 - M1
        f1 = interaction_f(alpha, dM, r_rep=r_rep, c_att=c_att)
        f2 = interaction_f(alpha, -dM, r_rep=r_rep, c_att=c_att)
        M1 = M1 + f1 * dt
        M2 = M2 + f2 * dt

    final_norm = float(np.linalg.norm(M2 - M1))
    return {"norm": final_norm, "converged": final_norm < 1e-3}


def run_protocol1(domain_params: dict, n_trials: int = 100) -> dict:
    """ドメイン別に n_trials 回試行し収束率を返す"""
    results = {}
    for domain, params in domain_params.items():
        trials = Parallel(n_jobs=-1)(
            delayed(_single_trial)(params, seed=i) for i in range(n_trials)
        )
        norms = [t["norm"] for t in trials]
        conv_rate = float(np.mean([t["converged"] for t in trials]))
        results[domain] = {
            "convergence_rate": conv_rate,
            "mean_norm": float(np.mean(norms)),
            "std_norm": float(np.std(norms)),
            # 90%以上収束 → 公理反証
            "axiom_falsified": conv_rate > 0.9,
        }
    return results


# ======== Protocol 3: CM, CU, CV 独立性テスト ========

def _random_state(n_agents: int = 5, d: int = 2, dv: int = 2, rng=None):
    """ランダムな状態生成"""
    if rng is None:
        rng = np.random.default_rng()
    Ms = rng.uniform(-2, 2, (n_agents, d))
    Us = rng.uniform(0, 1, n_agents)
    Vs = rng.uniform(0, 1, (n_agents, dv))
    Vs = Vs / (np.linalg.norm(Vs, axis=1, keepdims=True) + 1e-12)
    agents = [Agent(id=i, M=Ms[i], U=Us[i], V=Vs[i]) for i in range(n_agents)]
    edges = [(i, j) for i in range(n_agents) for j in range(i + 1, n_agents)]
    return agents, edges


def run_protocol3(n_samples: int = 500, seed: int = 42) -> dict:
    """n_samples 個のランダム状態で CM, CU, CV を計算し相関を測定"""
    rng = np.random.default_rng(seed)
    CM_vals, CU_vals, CV_vals = [], [], []

    for _ in range(n_samples):
        agents, edges = _random_state(rng=rng)
        _, var_e = check_CM(agents, edges)
        _, range_u = check_CU(agents)
        _, var_cv = check_CV(agents, edges)
        CM_vals.append(var_e)
        CU_vals.append(range_u)
        CV_vals.append(var_cv)

    CM_arr = np.array(CM_vals)
    CU_arr = np.array(CU_vals)
    CV_arr = np.array(CV_vals)

    corr_MU = float(np.corrcoef(CM_arr, CU_arr)[0, 1])
    corr_MV = float(np.corrcoef(CM_arr, CV_arr)[0, 1])
    corr_UV = float(np.corrcoef(CU_arr, CV_arr)[0, 1])
    corr_matrix = np.array([[1, corr_MU, corr_MV],
                             [corr_MU, 1, corr_UV],
                             [corr_MV, corr_UV, 1]])
    max_corr = max(abs(corr_MU), abs(corr_MV), abs(corr_UV))

    return {
        "CM": CM_arr, "CU": CU_arr, "CV": CV_arr,
        "corr_MU": corr_MU, "corr_MV": corr_MV, "corr_UV": corr_UV,
        "corr_matrix": corr_matrix,
        "max_corr": max_corr,
        # 全相関 < 0.3 → 独立性支持
        "independence_supported": max_corr < 0.3,
    }


# ======== 可視化 ========

def plot_phase4(proto1: dict, proto3: dict, out_path: Path) -> None:
    fig = plt.figure(figsize=(13, 9))
    gs = gridspec.GridSpec(2, 2, hspace=0.38, wspace=0.32)

    # (a) Protocol 1: ドメイン別収束率
    ax_a = fig.add_subplot(gs[0, 0])
    domains = list(proto1.keys())
    rates = [proto1[d]["convergence_rate"] * 100 for d in domains]
    colors = ["steelblue", "seagreen", "tomato"]
    bars = ax_a.bar(domains, rates, color=colors, alpha=0.75, edgecolor="black")
    ax_a.axhline(90, color="red", lw=1.2, linestyle="--", label="反証閾値 (90%)")
    ax_a.set_ylabel("収束率 (%)")
    ax_a.set_title("(a) Protocol 1: ドメイン別ΔM収束率")
    ax_a.set_ylim(0, 105)
    ax_a.legend(fontsize=8)
    for bar, r in zip(bars, rates):
        ax_a.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                  f"{r:.1f}%", ha="center", va="bottom", fontsize=9)
    ax_a.grid(axis="y", alpha=0.3)

    # (b) Protocol 1: 各ドメインの ‖ΔM‖ 分布（箱ひげ図代わりにバー）
    ax_b = fig.add_subplot(gs[0, 1])
    means = [proto1[d]["mean_norm"] for d in domains]
    stds = [proto1[d]["std_norm"] for d in domains]
    x = np.arange(len(domains))
    ax_b.bar(x, means, yerr=stds, color=colors, alpha=0.75, edgecolor="black",
             capsize=5)
    ax_b.set_xticks(x)
    ax_b.set_xticklabels(domains)
    ax_b.set_ylabel(r"最終 $\|\Delta M\|$ (mean ± std)")
    ax_b.set_title(r"(b) Protocol 1: 最終 $\|\Delta M\|$ 分布")
    ax_b.grid(axis="y", alpha=0.3)

    # (c) Protocol 3: 相関行列ヒートマップ
    ax_c = fig.add_subplot(gs[1, 0])
    import seaborn as sns
    labels = ["CM (VarE)", "CU (rangeU)", "CV (VarCV)"]
    sns.heatmap(
        proto3["corr_matrix"],
        annot=True, fmt=".3f", cmap="coolwarm", center=0,
        xticklabels=labels, yticklabels=labels,
        ax=ax_c, vmin=-1, vmax=1, linewidths=0.5,
    )
    ax_c.set_title("(c) Protocol 3: CM-CU-CV 相関行列")

    # (d) Protocol 3: 散布図（CM vs CU）
    ax_d = fig.add_subplot(gs[1, 1])
    ax_d.scatter(proto3["CM"], proto3["CU"], s=8, alpha=0.4, color="slategray")
    ax_d.set_xlabel("VarE (CM 指標)")
    ax_d.set_ylabel("rangeU (CU 指標)")
    ax_d.set_title(f"(d) CM vs CU 散布図 (r={proto3['corr_MU']:.3f})")
    ax_d.grid(alpha=0.3)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.suptitle("Figure 4: Falsifiability Protocol 実証", fontsize=13, y=1.01)
    fig.savefig(out_path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"[Phase 4] 保存: {out_path}")


def run(cfg: dict, out_dir: Path) -> dict:
    domain_params = cfg["domain_params"]
    n_trials = cfg["n_trials"]
    n_samples = cfg["n_samples"]

    print("  Protocol 1: 非収束性テスト 実行中...")
    proto1 = run_protocol1(domain_params, n_trials)

    print("  Protocol 3: 独立性テスト 実行中...")
    proto3 = run_protocol3(n_samples)

    out_dir.mkdir(parents=True, exist_ok=True)
    plot_phase4(proto1, proto3, out_dir / "figure4.png")

    return {"protocol1": proto1, "protocol3": proto3}


def report(result: dict) -> None:
    p1 = result["protocol1"]
    p3 = result["protocol3"]

    print("\n" + "=" * 55)
    print("  Phase 4: Falsifiability Protocol 検証レポート")
    print("=" * 55)
    print("\n  --- Protocol 1: 非収束性の反証テスト ---")
    for domain, r in p1.items():
        status = "✗ 反証" if r["axiom_falsified"] else "✓ 公理支持"
        print(f"  {domain:12s}: 収束率={r['convergence_rate']*100:.1f}%  {status}")

    print("\n  --- Protocol 3: CM・CU・CV 独立性テスト ---")
    print(f"  corr(CM, CU) = {p3['corr_MU']:.3f}")
    print(f"  corr(CM, CV) = {p3['corr_MV']:.3f}")
    print(f"  corr(CU, CV) = {p3['corr_UV']:.3f}")
    indep = p3["independence_supported"]
    print(f"  最大相関     = {p3['max_corr']:.3f}  {'✓ <0.3 (独立性支持)' if indep else '△ ≥0.3 (部分的依存)'}")
    print("=" * 55)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    with open(root / "config" / "scenarios.yaml") as f:
        all_cfg = yaml.safe_load(f)
    cfg = all_cfg["phase4"]

    result = run(cfg, root / "outputs" / "phase4")
    report(result)
