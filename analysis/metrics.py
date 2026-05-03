"""
シミュレーション指標の計算（Section 2-3）

- ΔM ノルム時系列
- VarE(t) — エッジ上の ‖ΔM‖ 分散
- μ_Δ(t) — 平均エッジノルム
- lim_sup 近似
- Consensus判定
"""
import numpy as np


def compute_metrics(norm_history: np.ndarray, dt: float) -> dict:
    """
    ‖ΔM(t)‖ 時系列から各種指標を計算。

    Parameters
    ----------
    norm_history : shape (T,) — ‖ΔM(t)‖ の時系列
    dt           : 時間刻み

    Returns
    -------
    dict with keys: lim_sup, mean_tail, d_norm (微分), non_convergent
    """
    T = len(norm_history)
    tail = norm_history[T // 2:]  # 後半を定常状態として扱う

    # 数値微分（中央差分）
    d_norm = np.gradient(norm_history, dt)

    return {
        "lim_sup": float(np.max(tail)),
        "lim_inf": float(np.min(tail)),
        "mean_tail": float(np.mean(tail)),
        "std_tail": float(np.std(tail)),
        "d_norm": d_norm,
        # lim_sup > ε → 非収束公理を支持
        "non_convergent": float(np.max(tail)) > 1e-3,
    }


def lim_sup_approx(series: np.ndarray, window: int = 50) -> np.ndarray:
    """
    移動窓での lim_sup 近似（Lemma 2.1 検証用）。
    各時刻 t で [t-window, t] の最大値を返す。
    """
    result = np.empty_like(series)
    for t in range(len(series)):
        start = max(0, t - window)
        result[t] = np.max(series[start : t + 1])
    return result


def edge_variance(edge_norms: np.ndarray) -> float:
    """VarE(ΔM) = Var(‖ΔM_{ij}‖) over edges"""
    return float(np.var(edge_norms))


def edge_mean(edge_norms: np.ndarray) -> float:
    """μ_Δ = mean(‖ΔM_{ij}‖) over edges"""
    return float(np.mean(edge_norms))


def consensus_check(
    var_e_series: np.ndarray,
    theta_M: float = 0.2,
    delta: float = 0.01,
    dt: float = 0.01,
    window: int = 100,
) -> dict:
    """
    Consensus 達成判定。

    定義: ∃T s.t. ∀t>T: VarE < θ_M かつ |d(VarE)/dt| < δ
    """
    d_var = np.abs(np.gradient(var_e_series, dt))
    stable = (var_e_series < theta_M) & (d_var < delta)

    # 連続 window ステップ安定なら Consensus
    consensus_t = None
    for t in range(window, len(stable)):
        if np.all(stable[t - window : t]):
            consensus_t = t
            break

    return {
        "achieved": consensus_t is not None,
        "first_t": consensus_t,
        "final_VarE": float(var_e_series[-1]),
        "final_dVarE": float(d_var[-1]),
    }
